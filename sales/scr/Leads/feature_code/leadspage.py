class LeadsPage:
    def __init__(self, page):
        self.page = page

    def navigateToCRMLeads(self):
        self.page.goto("https://sales.superagi.com/i-assistant")
        self.page.get_by_role("textbox", name="Search SuperAGI").wait_for()
        self.page.locator(".card_container").click()
        self.page.get_by_role("img", name="crm_icon").click()
        self.page.get_by_role("link", name="Leads more_options").click()

    def verifyLeadsListVisible(self):
        self.page.get_by_role("button", name="Add Lead").wait_for()

    def clickAddLead(self):
        self.page.get_by_role("button", name="Add Lead").click()

    def fillLeadDetails(self, first_name, last_name, email):
        self.page.get_by_role("textbox", name="First Name").fill(first_name)
        self.page.get_by_role("textbox", name="Last Name").fill(last_name)
        self.page.get_by_role("textbox", name="Email").fill(email)

    def submitAddLeadForm(self):
        self.page.get_by_role("button", name="Add Lead").nth(1).click()

    def verifySuccessMessage(self, message):
        self.page.get_by_text(message).wait_for()
