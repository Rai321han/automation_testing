import re
import random
from automation.playwright.utils.helper import format_airbnb_date


class LandingPage:

    def __init__(self, page):
        self.page = page
        self.locationDiv = (
            self.page.locator("div").filter(has_text=re.compile(r"^Where$")).nth(1)
        )
        self.guest_btn = self.page.get_by_role("button", name="Who Add guests")

        self.locationInput = self.page.get_by_test_id(
            "structured-search-input-field-query"
        )

        self.options = self.page.get_by_role("option")

        # All months container
        self.calendar = page.locator('[aria-label="Calendar"]')

        # Left month buttons
        self.left_month = (
            self.calendar.locator("div[data-state--date-string]")
            .locator("xpath=ancestor::div[contains(@class,'mjfhmhj')]")
            .nth(0)
        )

        # Right month buttons
        self.right_month = (
            self.calendar.locator("div[data-state--date-string]")
            .locator("xpath=ancestor::div[contains(@class,'mjfhmhj')]")
            .nth(1)
        )

    def goto(self, url):
        """
        Navigate to the URL and wait for DOM to load.
        Returns True if page loads successfully, False otherwise.
        """
        try:
            self.page.goto(url, wait_until="domcontentloaded")
            return True
        except Exception:
            return False

    def handle_popups(self, timeout=5000):
        try:
            btn = self.page.get_by_role("button", name="Got it")
            btn.wait_for(state="visible", timeout=timeout)
            btn.click()
            return True
        except:
            return False

    def click_location_input(self):
        self.locationDiv.click()

    def type_location(self, text, delay=100):
        # Wait for the input to be visible
        self.locationInput.wait_for(state="visible", timeout=5000)
        # Click to focus
        self.locationInput.click()
        # Type text
        self.locationInput.type(text, delay=delay)

    def select_random_suggestion(self):

        random_index = random.randint(0, self.options.count() - 1)
        self.options.nth(random_index).click()
        # return the text of the selected option for later verification
        selectedLocation = self.options.nth(random_index).inner_text()
        print(f"Selected location: {selectedLocation}")
        return selectedLocation

    def verify_suggestion_item_has_icon(self, index):

        option = self.options.nth(index)
        # Check if the option has an SVG icon
        svg_count = option.locator("svg").count()
        if svg_count > 0:
            print(f"PASS: Suggestion item at index {index} has an icon.")
            return True
        else:
            print(f"FAIL: Suggestion item at index {index} does NOT have an icon.")
            return False

    def random_click_next_month(self):
        forward_buttons = self.page.get_by_role(
            "button", name="Move forward to switch to the"
        )
        num_clicks = random.randint(3, 8)
        for _ in range(num_clicks):
            forward_buttons.click()
            self.page.wait_for_timeout(1000)

    def get_days_from_month(self, month_index):
        """
        month_index = 0 → left month
        month_index = 1 → right month
        """
        month = self.calendar.locator("div.mjfhmhj").nth(month_index)

        buttons = month.locator("button[data-state--date-string]")

        days = []

        count = buttons.count()

        for i in range(count):

            btn = buttons.nth(i)

            # skip disabled dates
            if btn.is_disabled():
                continue

            date_string = btn.get_attribute("data-state--date-string")

            days.append({"button": btn, "date": date_string})

        return days

    def select_random_dates(self):

        # wait for calendar visible
        self.calendar.wait_for()

        # get left month dates
        left_days = self.get_days_from_month(0)

        # get right month dates
        right_days = self.get_days_from_month(1)

        if not left_days:
            raise Exception("No check-in dates found")

        if not right_days:
            raise Exception("No check-out dates found")

        # pick random
        checkin = random.choice(left_days)
        checkout = random.choice(right_days)

        # click
        checkin["button"].click()
        checkout["button"].click()

        return checkin["date"], checkout["date"]

    def verify_selected_dates(self, check_in, check_out):
        expected = f"{format_airbnb_date(check_in)} - {format_airbnb_date(check_out)}"

        date_button = self.page.get_by_role("button", name=re.compile(r"^When "))

        actual = date_button.inner_text()

        print("Expected:", expected)
        print("Actual:", actual)

        if expected in actual:
            print("PASS: Dates correctly displayed")
            return True
        else:
            print("FAIL: Dates not matching")
            return False

    def click_guest_input(self):
        self.page.get_by_role("button", name="Who Add guests").click()

    def set_guests(self):
        adults = random.randint(3, 10)
        children = random.randint(2, 5)
        infants = random.randint(1, 3)
        pets = random.randint(0, 2)

        adultsBtn = self.page.get_by_test_id("stepper-adults-increase-button")
        childrenBtn = self.page.get_by_test_id("stepper-children-increase-button")
        infantsBtn = self.page.get_by_test_id("stepper-infants-increase-button")
        petsBtn = self.page.get_by_test_id("stepper-pets-increase-button")

        adultsBtn.wait_for(state="visible", timeout=5000)
        childrenBtn.wait_for(state="visible", timeout=5000)
        infantsBtn.wait_for(state="visible", timeout=5000)
        petsBtn.wait_for(state="visible", timeout=5000)

        # random click all buttons
        for _ in range(adults):
            adultsBtn.click()
            self.page.wait_for_timeout(500)

        for _ in range(children):
            childrenBtn.click()
            self.page.wait_for_timeout(500)

        for _ in range(infants):
            infantsBtn.click()
            self.page.wait_for_timeout(500)

        for _ in range(pets):
            petsBtn.click()
            self.page.wait_for_timeout(500)

        return adults, children, infants, pets

    def verify_guest_display(self, adults, children):
        guest_btn_text = self.guest_btn.inner_text()

        # Normalize: replace &nbsp; with regular space, remove extra whitespace
        normalized_text = " ".join(guest_btn_text.split())

        total_guests = adults + children

        # Check for "X guest" or "X guests" (flexible)
        guest_pattern = f"{total_guests}\\s+guest"

        if not re.search(guest_pattern, normalized_text, re.IGNORECASE):
            raise Exception(
                f"Guest count not displayed correctly. Expected {total_guests} guests, got: {normalized_text}"
            )

        return True

    def makeSearch(self):
        searchBtn = self.page.get_by_test_id("structured-search-input-search-button")
        searchBtn.click()
        self.page.wait_for_url("**/s/**", timeout=30000)
