class commonScript:
    def __init__(self, page):
        self.page = page

    def goToSettings(self):
        self.page.locator("#navbar_right_section").click()
        self.page.locator(".text_color").filter(has_text="Settings").click()
        self.page.locator("#settings_sidebar").wait_for()
