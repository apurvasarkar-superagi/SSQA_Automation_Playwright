import os
import random
import string
from sales.runners.env_setup import EnvSetup


class ContactsPage:
    def __init__(self, page):
        self.page = page

    def navigateToCRMContacts(self):
        self.page.get_by_role("img", name="crm_icon").click()
        self.page.get_by_role("link", name="Contacts more_options").click()

    def verifyContactsListVisible(self):
        self.page.get_by_role("button", name="Add Contact").wait_for()

    def clickAddContact(self):
        self.page.get_by_role("button", name="Add Contact").click()

    def fillContactDetails(self, details: dict):
        scenario_id = os.environ.get("SCENARIO_ID") or ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        os.environ["SCENARIO_ID"] = scenario_id

        for field, value in details.items():
            if not value:
                continue
            match field:
                case "First Name":
                    value = f"{value}_{scenario_id}"
                    details["First Name"] = value
                    self.page.get_by_role("textbox", name="First Name").fill(value)
                case "Last Name":
                    value = f"{value}_{scenario_id}"
                    details["Last Name"] = value
                    self.page.get_by_role("textbox", name="Last Name").fill(value)
                case "Email":
                    local, domain = value.split("@", 1 )
                    value = f"{local}+{scenario_id}@{domain}"
                    details["Email"] = value
                    self.page.get_by_role("textbox", name="Email").fill(value)
                case "Phone Number":
                    self.page.get_by_placeholder("Enter a phone number").fill(value)
                case "LinkedIn URL":
                    self.page.get_by_role("textbox", name="LinkedIn URL").fill(value)
                case "Address":
                    self.page.get_by_role("textbox", name="Address").fill(value)
                case "City":
                    self.page.get_by_role("textbox", name="City").fill(value)
                case "State":
                    self.page.get_by_role("textbox", name="State").fill(value)
                case "Country":
                    self.page.get_by_role("combobox", name="Country").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Zipcode":
                    self.page.get_by_role("textbox", name="Zipcode").fill(value)
                case "Current Company":
                    self.page.get_by_role("combobox", name="Current Company").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Current Role":
                    self.page.get_by_role("textbox", name="Current Role").fill(value)
                case "Description":
                    self.page.get_by_role("textbox", name="Description").fill(value)
                case "Tags":
                    self.page.get_by_role("combobox", name="Tags").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
        EnvSetup.get_current_contact_details().update(details)

    def submitAddContactForm(self):
        self.page.get_by_role("button", name="Add Contact").nth(1).click()

    def verifySuccessMessage(self, message):
        self.page.get_by_text(message).wait_for()

    def searchContact(self, search_term):
        search_input = self.page.locator('.action_bar_buttons  input[placeholder*="Search"]').first
        search_input.fill(search_term)
        search_input.press("Enter")

    def searchAndVerifyContact(self, search_term, field_name="value", retries=5, retry_interval=3000):
        search_input = self.page.locator('.action_bar_buttons  input[placeholder*="Search"]').first
        self.page.wait_for_timeout(2000)
        search_input.fill(search_term)
        search_input.press("Enter")
        locator = self.page.get_by_text(search_term).first
        for attempt in range(1, retries + 1):
            if locator.is_visible():
                return
            if attempt < retries:
                self.page.wait_for_timeout(retry_interval)
                search_input.press("Enter")
        raise AssertionError(
            f"Contact not found in search results after {retries} attempts "
            f"when searching by {field_name}: '{search_term}'"
        )

    def verifyContactInSearchResults(self, value, field_name="value", retries=5, retry_interval=3000):
        """Retries the search until the contact appears in the table.
        Needed because backend indexing can lag behind the creation toast.
        """
        search_input = self.page.locator('.action_bar_buttons  input[placeholder*="Search"]').first
        locator = self.page.get_by_text(value).first

        for attempt in range(1, retries + 1):
            if locator.is_visible():
                return
            if attempt < retries:
                self.page.wait_for_timeout(retry_interval)
                search_input.press("Enter")  # re-trigger search

        raise AssertionError(
            f"Contact not found in search results after {retries} attempts "
            f"when searching by {field_name}: '{value}'"
        )
