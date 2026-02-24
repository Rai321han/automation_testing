import traceback
import asyncio
import concurrent.futures
import hashlib
import re

from automation.logging.logger import get_logger
from automation.playwright.utils.screenshot_manager import ScreenshotManager


class BaseWorkflow:
    """
    Base class for all Playwright-based automation workflows.

    Every step is tracked individually via run_step():
      - Result is saved to DB after EVERY step (pass or fail).
      - Screenshot is taken for EVERY step with a unique name based on test_case_name.
      - Full-page screenshot with red border around locator (if provided).
      - test_case_name is the human-readable step message stored as the DB key.
    """

    def __init__(self, page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def log_step(self, message: str):
        self.logger.info(message)

    def log_error(self, error):
        self.logger.error(str(error))
        self.logger.error(traceback.format_exc())

    # ------------------------------------------------------------------
    # Browser data management
    # ------------------------------------------------------------------

    def _clear_browser_data(self):
        """
        Clear cookies, local storage, and session storage.
        Must be called AFTER page navigation to avoid SecurityError.
        """
        try:
            self.page.context.clear_cookies()
            self.page.evaluate(
                """
                () => {
                    localStorage.clear();
                    sessionStorage.clear();
                }
                """
            )
            self.logger.info(
                "Browser data cleared (cookies, localStorage, sessionStorage)"
            )
        except Exception as e:
            self.logger.warning(f"Failed to clear browser data: {e}")

    # ------------------------------------------------------------------
    # Screenshot helpers
    # ------------------------------------------------------------------

    def _take_full_page_screenshot(self, locator=None) -> str:
        """
        Take a full-page screenshot.
        If locator is provided, apply a red border around it first.
        Returns the relative path (without 'media/' prefix).
        """
        try:
            if locator is not None:
                # Apply red border to element
                try:
                    locator.evaluate(
                        "el => {"
                        "  el.dataset._origOutline = el.style.outline;"
                        "  el.dataset._origBoxShadow = el.style.boxShadow;"
                        "  el.style.outline = '3px solid red';"
                        "  el.style.boxShadow = '0 0 0 3px rgba(255,0,0,0.5)';"
                        "}"
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to highlight locator: {e}")

            # Take full-page screenshot
            raw_path = ScreenshotManager.take_full_page(self.page)
            return raw_path.replace("media/", "", 1)

        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {e}")
            raise

        finally:
            # Always restore original styles
            if locator is not None:
                try:
                    locator.evaluate(
                        "el => {"
                        "  el.style.outline = el.dataset._origOutline || '';"
                        "  el.style.boxShadow = el.dataset._origBoxShadow || '';"
                        "  delete el.dataset._origOutline;"
                        "  delete el.dataset._origBoxShadow;"
                        "}"
                    )
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # DB persistence
    # ------------------------------------------------------------------

    def _save_result(
        self,
        test_case_name: str,
        passed: bool,
        comment: str = "",
        screenshot_path: str = "",
    ):
        """
        Upsert a Result row keyed on test_case_name.

        Django's ORM is synchronous. If this method is called from inside a
        running asyncio event loop (async view, Django Channels, ASGI server),
        the ORM will raise SynchronousOnlyOperation. We detect this and push
        the write into a ThreadPoolExecutor so it runs in a plain sync thread
        with its own database connection, which is always safe.
        """
        from automation.models import Result  # lazy — safe outside Django

        def _db_write():
            # Capture current page URL
            current_url = self.page.url if self.page else ""

            result, created = Result.objects.update_or_create(
                test_case=test_case_name,
                defaults={
                    "passed": passed,
                    "comment": comment,
                    "url": current_url,
                },
            )
            status = "PASS" if passed else "FAIL"
            action = "Created" if created else "Updated"
            self.logger.info(
                f"{action} DB result → [{status}] {test_case_name} | Screenshot: {screenshot_path}"
            )
            return result

        # Detect whether we're inside a running event loop.
        # asyncio.get_running_loop() raises RuntimeError if there is none.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Async context (ASGI view, Channels consumer, etc.)
            # Run the synchronous DB write in a worker thread so Django's
            # async guard doesn't fire and we don't block the event loop.
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(_db_write)
                return future.result()  # blocks this thread until DB write done
        else:
            # Plain sync context — call directly, no overhead
            return _db_write()

    # ------------------------------------------------------------------
    # Core step runner
    # ------------------------------------------------------------------

    def run_step(
        self,
        test_case_name: str,
        fn,
        *args,
        locator=None,
        reraise: bool = True,
        comment_fn=None,
        **kwargs,
    ):
        """
        Execute fn(*args, **kwargs) as a named, tracked test step.

        PASS path:
          • Calls fn, takes full-page screenshot with red border on locator (if provided).
          • Saves a PASS result to DB with screenshot path and custom comment.

        FAIL path:
          • Logs the error + full traceback.
          • Takes full-page screenshot with red border on locator (if provided).
          • Saves a FAIL result to DB with screenshot path and error message.
          • Re-raises by default so the workflow's outer try/except can halt it;
            pass reraise=False for non-critical steps (e.g. popup dismissal).

        comment_fn: Optional callable that takes the return value and returns a comment string.
                   Example: lambda props: f"found property: {props}"

        Returns fn's return value on success, None on swallowed failure.
        """
        self.logger.info(f"▶ Step: {test_case_name}")
        screenshot_path = ""

        try:
            return_value = fn(*args, **kwargs)

            # ── PASS ──────────────────────────────────────────────────────────
            # Take screenshot (full-page with locator highlight if provided)
            try:
                screenshot_filename = test_case_name + ".png"
                screenshot_path = ScreenshotManager.take(self.page, screenshot_filename)
                screenshot_path = screenshot_path.replace("media/", "", 1)
                self.logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as ss_exc:
                self.logger.error(f"Screenshot capture failed: {ss_exc}")
                screenshot_path = ""

            # Generate custom comment
            comment = comment_fn(return_value) if comment_fn else ""

            # Save to DB
            self._save_result(
                test_case_name,
                passed=True,
                comment=comment,
            )
            self.logger.info(f"✔ {test_case_name}")
            return return_value

        except Exception as exc:
            tb = traceback.format_exc()
            self.logger.error(f"✘ {test_case_name}: {exc}")
            self.logger.error(tb)

            # ── FAIL ──────────────────────────────────────────────────────────
            # Take screenshot (full-page with locator highlight if provided)
            try:
                screenshot_filename = self._generate_screenshot_filename(test_case_name)
                screenshot_path = ScreenshotManager.take(self.page, screenshot_filename)
                screenshot_path = screenshot_path.replace("media/", "", 1)
                self.logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as ss_exc:
                self.logger.error(f"Screenshot capture failed: {ss_exc}")
                screenshot_path = ""

            # Save to DB with error message as comment
            self._save_result(
                test_case_name,
                passed=False,
                comment=str(exc),
            )

            if reraise:
                raise
            return None
