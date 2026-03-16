import os
import random
import string
from sales.runners.env_setup import EnvSetup


class LeadsPage:
    def __init__(self, page):
        self.page = page

    def navigateToCRMLeads(self):
        self.page.get_by_role("img", name="crm_icon").click()
        self.page.get_by_role("link", name="Leads more_options").click()

    def verifyLeadsListVisible(self):
        self.page.get_by_role("button", name="Add Lead").wait_for()

    def clickAddLead(self):
        self.page.get_by_role("button", name="Add Lead").click()

    def fillLeadDetails(self, details: dict):
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
                    local, domain = value.split("@", 1)
                    value = f"{local}+{scenario_id}@{domain}"
                    details["Email"] = value
                    self.page.get_by_role("textbox", name="Email").fill(value)
                case "Phone Number":
                    phone_field = self.page.get_by_placeholder("Enter a phone number")
                    phone_field.click()
                    phone_field.press("Control+a")
                    phone_field.fill(value)
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
                case "Current Role":
                    self.page.get_by_role("textbox", name="Current Role").fill(value)
                case "Description":
                    self.page.get_by_role("textbox", name="Description").fill(value)
                case "Tags":
                    self.page.get_by_role("combobox", name="Tags").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
        EnvSetup.get_current_lead_details().update(details)

    def submitAddLeadForm(self):
        self.page.get_by_role("button", name="Add Lead").nth(1).click()

    def verifySuccessMessage(self, message):
        self.page.get_by_text(message).wait_for()

    def openEditFormForCurrentLead(self):
        email = EnvSetup.get_current_lead_details().get("Email", "")
        self.searchAndVerifyLead(email, "Email")
        self.page.get_by_role("button", name="more_icon").first.click()
        self.page.get_by_role("menuitem").filter(has_text="Edit").click()

    def openDetailsPageForCurrentLead(self):
        email = EnvSetup.get_current_lead_details().get("Email", "")
        self.searchAndVerifyLead(email, "Email")
        first_name = EnvSetup.get_current_lead_details().get("First Name", "")
        self.page.get_by_text(first_name).first.click()
        self.page.get_by_text("Property Group").wait_for()

    def updateLeadOnDetailsPage(self, details: dict):
        scenario_id = os.environ.get("SCENARIO_ID") or ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        os.environ["SCENARIO_ID"] = scenario_id
        for field, value in details.items():
            self.page.wait_for_timeout(2000)
            if not value:
                continue
            match field:
                case "First Name":
                    value = f"{value}_{scenario_id}"
                    details["First Name"] = value
                    self.page.locator("//span[text()='First Name']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("First Name updated").first.wait_for()
                case "Last Name":
                    value = f"{value}_{scenario_id}"
                    details["Last Name"] = value
                    self.page.locator("//span[text()='Last Name']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Last Name updated").first.wait_for()
                case "Email":
                    local, domain = value.split("@", 1)
                    value = f"{local}+{scenario_id}@{domain}"
                    details["Email"] = value
                    self.page.locator("//span[text()='Email']//following-sibling::div").first.click()
                    self.page.locator(".input_medium").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Email updated").first.wait_for()
                case "Phone Number":
                    self.page.locator("//span[text()='Phone Number']//following-sibling::div").first.click()
                    phone_field = self.page.get_by_placeholder("Enter a phone number")
                    phone_field.click()
                    phone_field.press("Control+a")
                    phone_field.fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Phone Number updated").first.wait_for()
                case "LinkedIn URL":
                    self.page.locator("//span[text()='LinkedIn URL']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("LinkedIn URL updated").first.wait_for()
                case "Address":
                    self.page.locator("//span[text()='Address']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Address updated").first.wait_for()
                case "City":
                    self.page.locator("//span[text()='City']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("City updated").first.wait_for()
                case "State":
                    self.page.locator("//span[text()='State']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("State updated").first.wait_for()
                case "Country":
                    self.page.locator("//span[text()='Country']//following-sibling::div").first.click()
                    self.page.get_by_role("combobox").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Country updated").first.wait_for()
                case "Zipcode":
                    self.page.locator("//span[text()='Zipcode']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Postal Code updated").first.wait_for()
                case "Current Role":
                    self.page.locator("//span[text()='Current Role']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Current Role updated").first.wait_for()
                case "Description":
                    self.page.locator("//span[text()='Description']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Description updated").first.wait_for()
                case "Tags":
                    self.page.locator("//span[text()='Tags']//following-sibling::div").first.click()
                    self.page.get_by_role("combobox").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Lead updated successfully").wait_for()
                    self.page.get_by_text("Tags updated").first.wait_for()
        EnvSetup.get_current_lead_details().update(details)

    def submitUpdateLeadForm(self):
        self.page.get_by_role("button", name="Update Lead").click()

    def searchAndVerifyLead(self, search_term, field_name="value", retries=5, retry_interval=3000):
        search_input = self.page.locator('.action_bar_buttons  input[placeholder*="Search"]').first
        self.page.wait_for_timeout(5000)
        search_input.fill(search_term)
        search_input.press("Enter")
        locator = self.page.get_by_text(search_term).first
        for attempt in range(1, retries + 1):
            self.page.wait_for_timeout(2000)
            if locator.is_visible():
                return
            if attempt < retries:
                self.page.wait_for_timeout(retry_interval)
                search_input.fill("")
                search_input.fill(search_term)
                search_input.press("Enter")
        raise AssertionError(
            f"Lead not found in search results after {retries} attempts "
            f"when searching by {field_name}: '{search_term}'"
        )
