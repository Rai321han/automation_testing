from automation.logging.logger import get_logger
import traceback
from automation.playwright.utils.screenshot_manager import ScreenshotManager


class BaseWorkflow:
    def __init__(self, page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

    def log_step(self, message):
        self.logger.info(message)

    def log_error(self, error):
        self.logger.error(str(error))
        self.logger.error(traceback.format_exc())

    def take_screenshot(self):
        path = ScreenshotManager.take(self.page)
        self.logger.info(f"Screenshot saved: {path}")
        return path
