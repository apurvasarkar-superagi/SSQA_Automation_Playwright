import os
import random
import string
from sales.runners.env_setup import EnvSetup


class CompaniesPage:
    def __init__(self, page):
        self.page = page

    def navigateToCRMCompanies(self):
        self.page.get_by_role("img", name="crm_icon").click()
        self.page.get_by_role("link", name="Companies more_options").click()

    def verifyCompaniesListVisible(self):
        self.page.get_by_role("button", name="Add Company").wait_for()

    def clickAddCompany(self):
        self.page.get_by_role("button", name="Add Company").click()

    def fillCompanyDetails(self, details: dict):
        scenario_id = os.environ.get("SCENARIO_ID") or ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        os.environ["SCENARIO_ID"] = scenario_id

        for field, value in details.items():
            if not value:
                continue
            match field:
                case "Name":
                    value = f"{value}_{scenario_id}"
                    details["Name"] = value
                    self.page.get_by_role("textbox", name="Name").fill(value)
                case "Industry":
                    industry_box = self.page.get_by_role("combobox", name="Industry")
                    industry_box.click(force=True)
                    industry_box.fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Country":
                    country_box = self.page.get_by_role("combobox", name="Country")
                    country_box.click(force=True)
                    country_box.fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Website":
                    value = f"{value}/{scenario_id}"
                    details["Website"] = value
                    self.page.get_by_role("textbox", name="Website").fill(value)
                case "LinkedIn URL":
                    self.page.get_by_role("textbox", name="LinkedIn URL").fill(value)
                case "Description":
                    self.page.get_by_role("textbox", name="Description").fill(value)
                case "Company Size":
                    size_box = self.page.get_by_role("combobox", name="Company Size")
                    size_box.click(force=True)
                    size_box.fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Annual Revenue":
                    self.page.get_by_role("spinbutton", name="Annual Revenue").fill(value)
                case "City":
                    self.page.get_by_role("textbox", name="City").fill(value)
                case "State":
                    self.page.get_by_role("textbox", name="State").fill(value)
                case "Zipcode":
                    self.page.get_by_role("textbox", name="Zipcode").fill(value)
                case "Tags":
                    tags_box = self.page.get_by_role("combobox", name="Tags")
                    tags_box.click(force=True)
                    tags_box.fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
        EnvSetup.get_current_company_details().update(details)

    def submitAddCompanyForm(self):
        self.page.get_by_role("button", name="Add Company").nth(1).click()

    def verifySuccessMessage(self, message):
        self.page.get_by_text(message).wait_for()

    def openEditFormForCurrentCompany(self):
        name = EnvSetup.get_current_company_details().get("Name", "")
        self.searchAndVerifyCompany(name, "Name")
        self.page.get_by_role("button", name="more_icon").first.click()
        self.page.get_by_role("menuitem").filter(has_text="Edit").click()

    def openDetailsPageForCurrentCompany(self):
        name = EnvSetup.get_current_company_details().get("Name", "")
        self.searchAndVerifyCompany(name, "Name")
        self.page.get_by_text(name).first.click()
        self.page.get_by_text("Property Group").wait_for()

    def updateCompanyOnDetailsPage(self, details: dict):
        scenario_id = os.environ.get("SCENARIO_ID") or ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        os.environ["SCENARIO_ID"] = scenario_id
        for field, value in details.items():
            self.page.wait_for_timeout(2000)
            if not value:
                continue
            match field:
                case "Name":
                    value = f"{value}_{scenario_id}"
                    details["Name"] = value
                    self.page.locator("//span[text()='Name']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Name updated").first.wait_for()
                case "Industry":
                    self.page.locator("//span[text()='Industry']//following-sibling::div").first.click()
                    self.page.get_by_role("combobox").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Industry updated").first.wait_for()
                case "Country":
                    self.page.locator("//span[text()='Country']//following-sibling::div").first.click()
                    self.page.get_by_role("combobox").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Country updated").first.wait_for()
                case "Website":
                    value = f"{value}/{scenario_id}"
                    details["Website"] = value
                    self.page.locator("//span[text()='Website']").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Website updated").first.wait_for()
                case "LinkedIn URL":
                    self.page.locator("//span[text()='LinkedIn URL']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("LinkedIn URL updated").first.wait_for()
                case "Description":
                    self.page.locator("//span[text()='Description']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Description updated").first.wait_for()
                case "Company Size":
                    self.page.locator("//span[text()='Company Size']//following-sibling::div").first.click()
                    self.page.get_by_role("combobox").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Company Size updated").first.wait_for()
                case "Annual Revenue":
                    self.page.locator("//span[text()='Annual Revenue']//following-sibling::div").first.click()
                    self.page.locator(".ant-input-number-input").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Annual Revenue updated").first.wait_for()
                case "City":
                    self.page.locator("//span[text()='City']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("City updated").first.wait_for()
                case "State":
                    self.page.locator("//span[text()='State']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("State updated").first.wait_for()
                case "Zipcode":
                    self.page.locator("//span[text()='Zipcode']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Postal Code updated").first.wait_for()
                case "Tags":
                    self.page.locator("//span[text()='Tags']//following-sibling::div").first.click()
                    self.page.get_by_role("combobox").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Company updated successfully").wait_for()
                    self.page.get_by_text("Tags updated").first.wait_for()
        EnvSetup.get_current_company_details().update(details)

    def submitUpdateCompanyForm(self):
        self.page.get_by_role("button", name="Update Company").click()

    def deleteCurrentCompany(self):
        name = EnvSetup.get_current_company_details().get("Name", "")
        self.searchAndVerifyCompany(name, "Name")
        self.page.get_by_role("button", name="more_icon").first.click()
        self.page.get_by_role("menuitem").filter(has_text="Delete").click()
        self.page.get_by_role("button", name="Delete").click()

    def verifyCompanyDeleted(self):
        name = EnvSetup.get_current_company_details().get("Name", "")
        self.navigateToCRMCompanies()
        self.verifyCompaniesListVisible()
        search_input = self.page.locator('.action_bar_buttons  input[placeholder*="Search"]').first
        self.page.wait_for_timeout(5000)
        search_input.fill("")
        self.page.wait_for_timeout(5000)
        search_input.fill(name)
        search_input.press("Enter")
        self.page.wait_for_timeout(2000)
        try:
            self.page.get_by_text("No results found").wait_for(timeout=15000)
        except Exception:
            raise AssertionError(f"Company with name '{name}' still appears in search results after deletion")

    def searchAndVerifyCompany(self, search_term, field_name="value", retries=5, retry_interval=3000):
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
            f"Company not found in search results after {retries} attempts "
            f"when searching by {field_name}: '{search_term}'"
        )
