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
            # can be "Homes in X" or "Homes near X"
            parsed_locationType1 = normalized.replace("Location Homes in ", "").strip()
            parsed_locationType2 = normalized.replace(
                "Location Homes near ", ""
            ).strip()

            parsed_location = (
                parsed_locationType1 if parsed_locationType1 else parsed_locationType2
            )

            if parsed_location not in location:
                raise Exception(
                    f"Location not correctly displayed in search summary: {raw_text}"
                )
            else:
                print("PASS: Location is correctly displayed in the search summary")

        if check_in and check_out:
            # Get the actual displayed text
            littleDate = self.page.get_by_test_id("little-search-date")
            normalizedDate = " ".join(littleDate.inner_text().split())

            # Try multiple date formats
            # Format 1: "Feb 28 - Mar 8" (with hyphen)
            # Format 2: "Feb 28 – Mar 8" (with en-dash)
            # Format 3: from format_airbnb_date()
            check_in_month = check_in.strftime("%b").strip()
            check_in_day = check_in.day
            check_out_month = check_out.strftime("%b").strip()
            check_out_day = check_out.day

            # Try different dash characters
            possible_formats = [
                f"{check_in_month} {check_in_day} - {check_out_month} {check_out_day}",  # hyphen
                f"{check_in_month} {check_in_day} – {check_out_month} {check_out_day}",  # en-dash
                f"{check_in_month} {check_in_day} — {check_out_month} {check_out_day}",  # em-dash
            ]

            date_found = any(fmt in normalizedDate for fmt in possible_formats)

            if not date_found:
                raise Exception(
                    f"Check-in and check-out dates not correctly displayed in search summary. "
                    f"Expected one of {possible_formats}, got: {normalizedDate}"
                )
            else:
                print(
                    "PASS: Check-in and check-out dates are correctly displayed in the search summary"
                )

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

        properties = container.locator('[data-testid="card-container"]').evaluate_all(
            """
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
        """
        )

        return properties

    def click_random_property(self, timeout=10000):

        container = self.page.locator(
            '[data-xray-jira-component="Guest: Listing Cards"]'
        )

        first_card = container.locator('[data-testid="card-container"]').first
        first_card.wait_for(state="visible", timeout=timeout)

        cards = container.locator('[data-testid="card-container"]')
        count = cards.count()

        print(f"Total properties found: {count}")

        if count == 0:
            raise Exception("No property cards found.")

        random_index = random.randint(0, count - 1)
        selected_card = cards.nth(random_index)

        # ⭐ capture new tab
        with self.page.context.expect_page() as new_page_info:
            selected_card.click()

        new_page = new_page_info.value

        new_page.wait_for_load_state("domcontentloaded")

        return random_index, new_page
