from datetime import datetime
from automation.playwright.pages.landing_page import LandingPage
from automation.playwright.core.base_workflow import BaseWorkflow
import random

from automation.playwright.pages.result_page import ResultPage


class UserWorkflow(BaseWorkflow):

    def run(self):
        try:
            self.log_step("Starting user workflow")

            landing = LandingPage(self.page)
            resultPage = ResultPage(self.page)

            self.log_step("Opening landing page")

            # land on home page
            landing.goto("https://airbnb.com")

            landing.handle_popups()

            # click on location input field
            landing.click_location_input()

            # randomly type one country name from a list of 20 countries
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
            # type country in the input field
            landing.type_location(text=country, delay=200)
            landing.page.wait_for_timeout(2000)

            if not landing.page.get_by_role("listbox", name="Search suggestions"):
                raise Exception("Search suggestions not visible")

            # log serch suggestions visibility
            self.log_step("Search suggestions are visible")

            # take suggestion list in array
            suggestions = landing.page.get_by_role("option").all_text_contents()
            if len(suggestions) == 0:
                raise Exception("No search suggestions found")

            # log the list
            self.log_step(f"Search suggestions: {suggestions}")

            # select random suggestion from the list
            location = landing.select_random_suggestion()
            landing.page.wait_for_timeout(2000)

            if not landing.page.get_by_role("application", name="Calendar"):
                raise Exception("date picker is not visible")

            # log calendar visibility
            self.log_step("date picker is visible")

            # click month forward button randomly between 3 to 8 times
            landing.random_click_next_month()

            checkin, checkout = landing.select_random_dates()

            check_in = datetime.strptime(checkin, "%Y-%m-%d")
            check_out = datetime.strptime(checkout, "%Y-%m-%d")
            landing.verify_selected_dates(check_in, check_out)
            landing.page.wait_for_timeout(1000)
            landing.click_guest_input()
            adults, children, infants, pets = landing.set_guests()
            self.log_step(
                f"Selected check-in date: {check_in}, check-out date: {check_out}, guests: adults={adults}, children={children}, infants={infants}, pets={pets}"
            )
            landing.makeSearch()
            resultPage.handle_popups()
            resultPage.verify_results_page(
                location=location,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                children=children,
                infants=infants,
                pets=pets,
            )

            self.log_step("Workflow completed successfully")
            return {"status": "PASS", "screenshot": "not taken", "error": None}

        except Exception as e:
            self.log_error(e)
            # screenshot = self.take_screenshot()
            return {"status": "FAIL", "screenshot": "not taken", "error": str(e)}
