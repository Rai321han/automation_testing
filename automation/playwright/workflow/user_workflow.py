from datetime import datetime
from automation.playwright.pages.landing_page import LandingPage
from automation.playwright.core.base_workflow import BaseWorkflow
import random
import re

from automation.playwright.pages.propertyDetails import PropertyDetailsPage
from automation.playwright.pages.result_page import ResultPage


class UserWorkflow(BaseWorkflow):

    def run(self):
        try:
            landing = LandingPage(self.page)
            resultPage = ResultPage(self.page)

            # ── 1. Navigate to Airbnb ──────────────────────────────────────────
            self.run_step(
                "Open Airbnb landing page",
                landing.goto,
                "https://airbnb.com",
                comment_fn=lambda loaded: (
                    "Page loaded correctly" if loaded else "Page doesn't load correctly"
                ),
            )

            # ── 2. Clear cookies and storage after landing page load ──────────
            self._clear_browser_data()

            # ── 3. Close any pop-up, banner, or modal if it appears ──────────
            self.run_step(
                "Handle landing page popups",
                landing.handle_popups,
                reraise=False,
            )

            # ── 4. Click the location input ────────────────────────────────────
            self.run_step(
                "Click location input field",
                landing.click_location_input,
                locator=landing.locationDiv,
            )

            # ── 5. Type a random country ──────────────────────────────────────
            countries = [
                "Japan",
                "Brazil",
                "Canada",
                "Kenya",
                "Germany",
                "Argentina",
                "Thailand",
                "Egypt",
                "Norway",
                "India",
                "South Africa",
                "Mexico",
                "France",
                "Australia",
                "Nigeria",
                "Italy",
                "Russia",
                "Vietnam",
                "Chile",
                "Turkey",
            ]
            country = random.choice(countries)

            self.run_step(
                f"Type location '{country}' in search field",
                landing.type_location,
                text=country,
                delay=200,
                locator=landing.locationInput,
                comment_fn=lambda _: f"country typed successfully: {country}",
            )
            self.page.wait_for_timeout(2000)

            # ── 6. Assert search suggestions listbox is visible ───────────────
            suggestions_listbox = self.page.get_by_role(
                "listbox", name="Search suggestions"
            )

            def assert_suggestions_visible():
                if not suggestions_listbox.is_visible():
                    raise Exception("Auto-suggestion list did not appear")
                return True

            self.run_step(
                "Auto-suggestion list appears after typing location",
                assert_suggestions_visible,
                locator=suggestions_listbox,
                comment_fn=lambda result: "auto-suggestion list appears correctly",
            )

            # ── 6.1 Verify each suggestion item has an icon ────────────────────
            self.run_step(
                "Auto-suggestion list items has icon",
                lambda: landing.verify_suggestion_item_has_icon(0),
                locator=suggestions_listbox,
                comment_fn=lambda result: (
                    "first suggestion item has an icon"
                    if result
                    else "first suggestion item does NOT have an icon"
                ),
            )

            # ── 7. Extract all suggestion options ───────────────────────────────
            def get_all_suggestions():
                items = self.page.get_by_role("option").all_text_contents()
                if not items:
                    raise Exception("No suggestion options found in listbox")
                return items

            self.run_step(
                "Extract all suggestion items from the list",
                get_all_suggestions,
                locator=suggestions_listbox,
                comment_fn=lambda items: f"found {len(items)} suggestions: {items}",
            )

            # ── 8. Select a random suggestion ─────────────────────────────────
            location = self.run_step(
                "Randomly select one suggestion from the list",
                landing.select_random_suggestion,
                locator=suggestions_listbox,
                comment_fn=lambda loc: f"selected location: {loc}",
            )
            self.page.wait_for_timeout(2000)

            # ── 9. Assert date picker (calendar) opens ────────────────────────
            def assert_calendar_visible():
                if not landing.calendar.is_visible():
                    raise Exception("Date picker modal did not open")
                return True

            self.run_step(
                "Date picker modal opens after selecting location",
                assert_calendar_visible,
                locator=landing.calendar,
                comment_fn=lambda result: "date picker modal opened successfully",
            )

            # ── 10. Advance month forward (3–8 random clicks) ──────────────────
            self.run_step(
                "Advance calendar month forward randomly",
                landing.random_click_next_month,
                locator=self.page.get_by_role(
                    "button", name="Move forward to switch to the"
                ),
            )

            # ── 11. Pick random check-in / check-out dates ────────────────────
            checkin, checkout = self.run_step(
                "Select random check-in and check-out dates from calendar",
                landing.select_random_dates,
                locator=landing.calendar,
                comment_fn=lambda dates: f"selected check-in: {dates[0]}, check-out: {dates[1]}",
            )
            check_in = datetime.strptime(checkin, "%Y-%m-%d")
            check_out = datetime.strptime(checkout, "%Y-%m-%d")

            # ── 12. Verify the dates are correctly reflected in the UI ─────────
            date_button = self.page.get_by_role("button", name=re.compile(r"^When "))

            def verify_dates():
                # Try both formats: "May 03" and "May 3"
                expected_padded = (
                    f"{check_in.strftime('%b %d')} - {check_out.strftime('%b %d')}"
                )
                expected_unpadded = (
                    f"{check_in.strftime('%b %-d')} - {check_out.strftime('%b %-d')}"
                )
                actual = date_button.inner_text()

                if expected_padded not in actual and expected_unpadded not in actual:
                    raise Exception(
                        f"Date mismatch: expected '{expected_padded}' or '{expected_unpadded}' in '{actual}'"
                    )
                return True

            self.run_step(
                "Verify selected dates appear in the date input field",
                verify_dates,
                locator=date_button,
                comment_fn=lambda result: f"dates verified: {check_in.date()} - {check_out.date()}",
            )

            # ── 13. Validate dates are logical and valid ───────────────────────
            def validate_dates():
                if check_in >= check_out:
                    raise Exception(
                        f"Invalid dates: check-in ({check_in.date()}) >= check-out ({check_out.date()})"
                    )
                days_diff = (check_out - check_in).days
                if days_diff < 1:
                    raise Exception(f"Invalid date range: only {days_diff} days")
                return days_diff

            nights = self.run_step(
                "Validate selected dates are logical and valid",
                validate_dates,
                comment_fn=lambda nights: f"date range valid: {nights} nights",
            )
            self.page.wait_for_timeout(1000)

            # ── 14. Check if guest input field is clickable ────────────────────
            guest_btn = self.page.get_by_role("button", name="Who Add guests")

            def is_guest_btn_clickable():
                if not guest_btn.is_enabled():
                    raise Exception("Guest input field is not clickable")
                return True

            self.run_step(
                "Guest input field is clickable",
                is_guest_btn_clickable,
                locator=guest_btn,
                comment_fn=lambda result: "guest input field is clickable",
            )

            # ── 15. Open guest picker ─────────────────────────────────────────
            def open_guest_picker():
                guest_btn.click()
                guest_popup = self.page.locator(
                    '[data-testid="stepper-adults-increase-button"]'
                )
                guest_popup.wait_for(state="visible", timeout=5000)
                return True

            self.run_step(
                "Guest selection pop-up opens",
                open_guest_picker,
                locator=guest_btn,
                comment_fn=lambda result: "guest selection pop-up opened successfully",
            )

            # ── 16. Set guest counts ──────────────────────────────────────────
            adults, children, infants, pets = self.run_step(
                "Set guest counts (adults, children, infants, pets)",
                landing.set_guests,
                comment_fn=lambda counts: f"guests: adults={counts[0]}, children={counts[1]}, infants={counts[2]}, pets={counts[3]}",
            )

            self.log_step(
                f"Summary — Location: {location}, Check-in: {check_in.date()}, Check-out: {check_out.date()}, Guests: {adults + children}"
            )

            # ── 18. Submit the search ─────────────────────────────────────────
            search_btn = self.page.get_by_test_id(
                "structured-search-input-search-button"
            )
            self.run_step(
                "Submit search",
                landing.makeSearch,
                locator=search_btn,
            )

            # ── 19. Handle results page popups ────────────────────────────────
            self.run_step(
                "Handle results page popups",
                resultPage.handle_popups,
                reraise=False,
            )

            # ── 20. Verify search results page loads successfully ──────────────
            def verify_results_page_load():
                url = self.page.url
                if "search" not in url:
                    raise Exception(f"Not on results page: {url}")
                self.page.wait_for_selector(
                    '[data-testid="card-container"]', timeout=10000
                )
                return True

            self.run_step(
                "Search results page loads successfully",
                verify_results_page_load,
                comment_fn=lambda result: "results page loaded correctly",
            )

            # ── 21. Verify results page reflects search criteria ──────────────
            results_location = self.page.get_by_test_id("little-search-location")
            self.run_step(
                "Verify selected dates and guest count appear in the page UI correctly",
                resultPage.verify_results_page,
                location=location,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                children=children,
                infants=infants,
                locator=results_location,
                comment_fn=lambda result: f"search criteria verified: location={location}, check-in={check_in.date()}, check-out={check_out.date()}, guests={adults + children}",
            )

            # ── 22. Verify dates and guests in URL ──────────────────────────────
            def verify_url_params():
                url = self.page.url
                params_valid = True
                missing = []

                if f"checkin={check_in.strftime('%Y-%m-%d')}" not in url:
                    missing.append(f"checkin={check_in.strftime('%Y-%m-%d')}")
                if f"checkout={check_out.strftime('%Y-%m-%d')}" not in url:
                    missing.append(f"checkout={check_out.strftime('%Y-%m-%d')}")
                if f"adults={adults}" not in url:
                    missing.append(f"adults={adults}")
                if children > 0 and f"children={children}" not in url:
                    missing.append(f"children={children}")

                if missing:
                    raise Exception(f"Missing URL parameters: {missing}")
                return True

            self.run_step(
                "Verify selected dates and guest count are present in the page URL",
                verify_url_params,
                comment_fn=lambda result: f"URL params verified: checkin, checkout, adults, children",
            )

            # ── 23. Extract all listed properties ─────────────────────────────
            cards_container = self.page.locator(
                '[data-xray-jira-component="Guest: Listing Cards"]'
            )
            properties = self.run_step(
                "Extract property listings from results page",
                resultPage.extract_properties,
                locator=cards_container,
                comment_fn=lambda props: f"properties extracted: {[{'title': p['title'], 'price': p['price'], 'images': p['images']} for p in props]}",
            )
            self.log_step(f"Found {len(properties)} properties")
            for i, prop in enumerate(properties):
                self.log_step(f"  [{i + 1}] {prop['title']} — {prop['price']}")

            # ── 24. Click a random property card ──────────────────────────────
            first_card = cards_container.locator('[data-testid="card-container"]').first
            property_no, new_page = self.run_step(
                "Click random property card to open detail page",
                resultPage.click_random_property,
                locator=first_card,
                comment_fn=lambda result: f"property listing opened: index={result[0]}, title={properties[result[0]]['title']}",
            )

            # ── 25. Verify property details page opens successfully ────────────
            def verify_property_page_load():
                new_page.wait_for_load_state("domcontentloaded")
                return True

            self.run_step(
                "Listing/property details page opens successfully",
                verify_property_page_load,
                comment_fn=lambda result: "property details page loaded successfully",
            )

            # ── 26. Handle detail page popups ─────────────────────────────────
            propertyDetailPage = PropertyDetailsPage(new_page)
            close_btn = new_page.get_by_role("button", name="Close")
            self.run_step(
                "Handle property detail page popups",
                propertyDetailPage.handle_popups,
                locator=close_btn,
                reraise=False,
            )

            # ── 27. Extract property detail data ──────────────────────────────
            property_data = self.run_step(
                "Extract property detail data (title, subtitle, images)",
                propertyDetailPage.get_property_data,
                locator=propertyDetailPage.title_locator,
                comment_fn=lambda data: f"property data: title='{data['title']}', subtitle='{data['subtitle']}', images={data['images']}, image_urls={data['images']}",
            )

            return {"status": "PASS", "error": None}

        except Exception as e:
            self.log_error(e)
            return {"status": "FAIL", "error": str(e)}
