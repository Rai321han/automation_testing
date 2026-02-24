class PropertyDetailsPage:

    def __init__(self, page):
        self.page = page
        self.title_locator = page.locator('[data-section-id="TITLE_DEFAULT"] h1')
        self.subtitle_locator = self.page.locator(
            '[data-section-id="OVERVIEW_DEFAULT_V2"] h2'
        )
        self.hero_images = page.locator('[data-section-id="HERO_DEFAULT"] picture img')

    def handle_popups(self, timeout=5000):
        try:
            btn = self.page.get_by_role("button", name="Close")
            btn.wait_for(state="visible", timeout=timeout)
            btn.click()
            return True
        except:
            return False

    def get_property_data(self):

        # wait first
        self.title_locator.wait_for(state="visible", timeout=10000)
        self.subtitle_locator.wait_for(state="visible", timeout=10000)

        # then read
        title = self.title_locator.inner_text()
        subtitle = self.subtitle_locator.inner_text()

        images = self.hero_images.evaluate_all("imgs => imgs.map(img => img.src)")

        return {"title": title, "subtitle": subtitle, "images": images}
