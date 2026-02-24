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

        verification_results = []

        # ── URL CHECK: Location ────────────────────────────────────────────
        if location:
            raw_text = self.page.get_by_test_id("little-search-location").inner_text()
            normalized = " ".join(raw_text.split())
            parsed_locationType1 = normalized.replace("Location Homes in ", "").strip()
            parsed_locationType2 = normalized.replace("Location Homes near ", "").strip()
            parsed_location = (
                parsed_locationType1 if parsed_locationType1 else parsed_locationType2
            )

            if parsed_location not in location:
                raise Exception(
                    f"Location not correctly displayed in search summary: {raw_text}"
                )
            verification_results.append(
                f"location: expected '{location}', found '{parsed_location}'"
            )

        # ── URL CHECK: Check-in and Check-out Dates ────────────────────────
        if check_in and check_out:
            expected_checkin = check_in.strftime("%Y-%m-%d")
            expected_checkout = check_out.strftime("%Y-%m-%d")

            if f"checkin={expected_checkin}" not in url:
                raise Exception(f"Check-in date not found in URL: {url}")
            if f"checkout={expected_checkout}" not in url:
                raise Exception(f"Check-out date not found in URL: {url}")

            verification_results.append(
                f"check-in date: expected 'checkin={expected_checkin}', found in URL"
            )
            verification_results.append(
                f"check-out date: expected 'checkout={expected_checkout}', found in URL"
            )

        # ── URL CHECK: Adults ──────────────────────────────────────────────
        if adults is not None:
            if f"adults={adults}" not in url:
                raise Exception(f"Number of adults not found in URL: {url}")
            verification_results.append(
                f"adults: expected 'adults={adults}', found in URL"
            )

        # ── URL CHECK: Children ────────────────────────────────────────────
        if children is not None and children > 0:
            if f"children={children}" not in url:
                raise Exception(f"Number of children not found in URL: {url}")
            verification_results.append(
                f"children: expected 'children={children}', found in URL"
            )

        # ── URL CHECK: Infants ─────────────────────────────────────────────
        if infants is not None and infants > 0:
            if f"infants={infants}" not in url:
                raise Exception(f"Number of infants not found in URL: {url}")
            verification_results.append(
                f"infants: expected 'infants={infants}', found in URL"
            )

        # ── UI CHECK: Location Display ─────────────────────────────────────
        if location:
            littleLocation = self.page.get_by_test_id("little-search-location")
            raw_text = littleLocation.inner_text()
            normalized = " ".join(raw_text.split())
            parsed_locationType1 = normalized.replace("Location Homes in ", "").strip()
            parsed_locationType2 = normalized.replace("Location Homes near ", "").strip()
            parsed_location = (
                parsed_locationType1 if parsed_locationType1 else parsed_locationType2
            )

            verification_results.append(
                f"UI location: expected '{location}', found '{parsed_location}'"
            )

        # ── UI CHECK: Date Display ─────────────────────────────────────────
        if check_in and check_out:
            littleDate = self.page.get_by_test_id("little-search-date")
            normalizedDate = " ".join(littleDate.inner_text().split())

            check_in_month = check_in.strftime("%b").strip()
            check_in_day = check_in.day
            check_out_month = check_out.strftime("%b").strip()
            check_out_day = check_out.day

            possible_formats = [
                f"{check_in_month} {check_in_day} - {check_out_month} {check_out_day}",
                f"{check_in_month} {check_in_day} – {check_out_month} {check_out_day}",
                f"{check_in_month} {check_in_day} — {check_out_month} {check_out_day}",
            ]

            date_found = any(fmt in normalizedDate for fmt in possible_formats)

            if not date_found:
                raise Exception(
                    f"Check-in and check-out dates not correctly displayed in search summary. "
                    f"Expected one of {possible_formats}, got: {normalizedDate}"
                )

            verification_results.append(
                f"UI dates: expected one of {possible_formats}, found '{normalizedDate}'"
            )

        # ── UI CHECK: Guest Count Display ──────────────────────────────────
        guest_count = 0
        if adults is not None:
            guest_count += adults
        if children is not None:
            guest_count += children

        littleGuests = self.page.get_by_test_id("little-search-guests")
        littleGuestsText = " ".join(littleGuests.inner_text().split())

        if f"{guest_count} guest" not in littleGuestsText:
            raise Exception(
                f"Guest count '{guest_count}' not found in search summary: {littleGuestsText}"
            )

        verification_results.append(
            f"UI guest count: expected '{guest_count} guest(s)', found '{littleGuestsText}'"
        )

        return verification_results

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
