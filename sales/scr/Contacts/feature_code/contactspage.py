class ContactsPage:
    def __init__(self, page):
        self.page = page

    def navigateToCRMContacts(self):
        self.page.locator(".w-1\\/6").first.click()
        self.page.locator(".card_container").click()
        self.page.get_by_role("img", name="crm_icon").click()
        self.page.get_by_role("link", name="Contacts more_options").click()

    def verifyContactsListVisible(self):
        self.page.get_by_role("button", name="Add Contact").wait_for()

    def clickAddContact(self):
        self.page.get_by_role("button", name="Add Contact").click()

    def fillContactDetails(self, first_name, last_name, email):
        self.page.get_by_role("textbox", name="First Name").fill(first_name)
        self.page.get_by_role("textbox", name="Last Name").click()
        self.page.get_by_role("textbox", name="Last Name").fill(last_name)
        self.page.get_by_role("textbox", name="Email").click()
        self.page.get_by_role("textbox", name="Email").fill(email)

    def submitAddContactForm(self):
        self.page.get_by_role("button", name="Add Contact").nth(1).click()

    def verifySuccessMessage(self, message):
        self.page.get_by_text(message).wait_for()
