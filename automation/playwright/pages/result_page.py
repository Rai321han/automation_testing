from automation.playwright.utils.helper import format_airbnb_date
import random

class ResultPage:

    def __init__(self, page):
        self.page = page

    def handle_popups(self, timeout=5000):
        try:
            btn = self.page.get_by_role("button", name="Got it")
            btn.wait_for(state="visible", timeout=timeout)
            btn.click()
            return True
        except:
            return False

    def verify_results_page(
        self,
        location=None,
        check_in=None,
        check_out=None,
        adults=None,
        children=None,
        infants=None,
    ):

        url = self.page.url
        if "search" not in url:
            raise Exception(f"Not on results page, current URL: {url}")

        print("PASS: Navigated to results page")

        # Additional checks can be added here to verify that the URL contains the correct query parameters based on the search criteria
        # For example, you can check if the check-in and check-out dates are present in
        # the URL, or if the number of guests is correctly reflected in the query parameters.

        # url check
        if check_in and check_out:
            if (
                f"checkin={check_in.strftime('%Y-%m-%d')}" not in url
                or f"checkout={check_out.strftime('%Y-%m-%d')}" not in url
            ):
                raise Exception(f"Check-in or check-out dates not found in URL: {url}")
            else:
                print("PASS: Check-in and check-out dates are present in the URL")

        if adults is not None:
            if f"adults={adults}" not in url:
                raise Exception(f"Number of adults not found in URL: {url}")
            else:
                print("PASS: Number of adults is present in the URL")

        if children is not None:
            if f"children={children}" not in url:
                raise Exception(f"Number of children not found in URL: {url}")
            else:
                print("PASS: Number of children is present in the URL")

        if infants is not None:
            if f"infants={infants}" not in url:
                raise Exception(f"Number of infants not found in URL: {url}")
            else:
                print("PASS: Number of infants is present in the URL")

        # ui check
        littleLocation = self.page.get_by_test_id("little-search-location")
        littleDate = self.page.get_by_test_id("little-search-date")
        littleGuests = self.page.get_by_test_id("little-search-guests")

        # location innertext is like "Homes in Melbourne"
        # location is like "MelbourneCityCity, Australia"
        # we can check if parsed inntertext location is in the location string
        if location:
            raw_text = littleLocation.inner_text()

            # Normalize whitespace (remove newlines, extra spaces)
            normalized = " ".join(raw_text.split())

            # Remove prefix safely
            parsed_location = normalized.replace("Location Homes in ", "").strip()

            if parsed_location not in location:
                raise Exception(
                    f"Location not correctly displayed in search summary: {raw_text}"
                )
            else:
                print("PASS: Location is correctly displayed in the search summary")

        # if check_in and check_out:
        #     expected_date = (
        #         f"{format_airbnb_date(check_in)} - {format_airbnb_date(check_out)}"
        #     )
        #     normalizedDate = " ".join(littleDate.inner_text().split())
        #     if expected_date not in normalizedDate:
        #         raise Exception(
        #             f"Check-in and check-out dates not correctly displayed in search summary: {littleDate.inner_text()}"
        #         )
        #     else:
        #         print(
        #             "PASS: Check-in and check-out dates are correctly displayed in the search summary"
        #         )

        guest_count = 0
        if adults is not None:
            guest_count += adults

        if children is not None:
            guest_count += children

        # littleGuestsText is like '1 guest' or '3 guests'
        littleGuestsText = " ".join(littleGuests.inner_text().split())
        print("Guest summary text:", littleGuestsText)
        if f"{guest_count} guest" not in littleGuestsText:
            raise Exception(
                f"Guest count '{guest_count}' not found in search summary: {littleGuestsText}"
            )
        else:
            print("PASS: Guest count is correctly displayed in the search summary")

        return True

    def get_properties(self):
        from playwright.sync_api import Page

    def extract_properties(self):
        self.page.wait_for_selector('[data-testid="card-container"]')

        container = self.page.locator(
            '[data-xray-jira-component="Guest: Listing Cards"]'
        )

        properties = container.locator(
            '[data-testid="card-container"]'
        ).evaluate_all("""
        (cards) => {
            return cards.map(card => {

                // ---- TITLE ----
                const titleEl = card.querySelector('[data-testid="listing-card-title"]');
                const title = titleEl ? titleEl.innerText.trim() : "";

                // ---- PRICE (clean extraction) ----
                let price = "";

                const priceRow = card.querySelector('[data-testid="price-availability-row"]');

                if (priceRow) {
                    // Get all text nodes inside price row
                    const text = priceRow.innerText;

                    // Extract first currency value like $12,345
                    const match = text.match(/\\$[\\d,]+/);

                    if (match) {
                        price = match[0];
                    }
                }

                // ---- IMAGES ----
                const images = Array.from(card.querySelectorAll("picture img"))
                    .map(img => img.src)
                    .filter(Boolean);

                const uniqueImages = [...new Set(images)];

                return {
                    title,
                    price,
                    images: uniqueImages
                };
            });
        }
        """)

        return properties
    

    def click_random_property(self):
        # Wait until cards are visible
        self.page.wait_for_selector('[data-testid="card-container"]')

        # Scope to listing container (safer)
        container = self.page.locator(
            '[data-xray-jira-component="Guest: Listing Cards"]'
        )

        cards = container.locator('[data-testid="card-container"]')

        count = cards.count()

        if count == 0:
            raise Exception("No property cards found.")

        # Pick random index
        random_index = random.randint(0, count - 1)

        self.log_step(f"Clicking random property index: {random_index + 1} of {count}")

        selected_card = cards.nth(random_index)

        # Optional: scroll into view (prevents click interception issues)
        selected_card.scroll_into_view_if_needed()

        # Click the first link inside the card
        selected_card.locator("a").first.click()

        # Wait for navigation to complete
        self.page.wait_for_load_state("networkidle")