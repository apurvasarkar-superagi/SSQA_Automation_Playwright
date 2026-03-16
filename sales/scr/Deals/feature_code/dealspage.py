import os
import random
import string
from sales.runners.env_setup import EnvSetup


class DealsPage:
    def __init__(self, page):
        self.page = page

    def navigateToCRMDeals(self):
        self.page.get_by_role("img", name="crm_icon").click()
        self.page.get_by_role("link", name="Deals more_options").click()

    def verifyDealsListVisible(self):
        self.page.get_by_role("button", name="Add Deal").wait_for()

    def clickAddDeal(self):
        self.page.get_by_role("button", name="Add Deal").click()

    def fillDealDetails(self, details: dict):
        scenario_id = os.environ.get("SCENARIO_ID") or ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        os.environ["SCENARIO_ID"] = scenario_id

        for field, value in details.items():
            if not value:
                continue
            match field:
                case "Title":
                    value = f"{value}_{scenario_id}"
                    details["Title"] = value
                    self.page.get_by_role("textbox", name="Title").fill(value)
                case "Amount":
                    self.page.get_by_placeholder("0.00").fill(value)
                case "Priority":
                    self.page.get_by_role("combobox", name="Priority").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Deal Type":
                    self.page.get_by_role("combobox", name="Deal Type").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Description":
                    self.page.get_by_role("textbox", name="Description").fill(value)
                case "Pipeline Stage":
                    self.page.get_by_role("combobox", name="Pipeline Stage*").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                case "Tags":
                    self.page.get_by_role("combobox", name="Tags").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
        EnvSetup.get_current_deal_details().update(details)

    def submitAddDealForm(self):
        self.page.get_by_role("button", name="Add Deal").nth(1).click()

    def verifySuccessMessage(self, message):
        self.page.get_by_text(message).wait_for()

    def openEditFormForCurrentDeal(self):
        title = EnvSetup.get_current_deal_details().get("Title", "")
        self.searchAndVerifyDeal(title, "Title")
        self.page.get_by_role("button", name="more_icon").first.click()
        self.page.get_by_role("menuitem").filter(has_text="Edit").click()
        self.page.wait_for_timeout(2000)

    def openDetailsPageForCurrentDeal(self):
        title = EnvSetup.get_current_deal_details().get("Title", "")
        self.searchAndVerifyDeal(title, "Title")
        self.page.get_by_text(title).first.click()
        self.page.get_by_text("Property Group").wait_for()

    def updateDealOnDetailsPage(self, details: dict):
        scenario_id = os.environ.get("SCENARIO_ID") or ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        os.environ["SCENARIO_ID"] = scenario_id
        for field, value in details.items():
            self.page.wait_for_timeout(2000)
            if not value:
                continue
            match field:
                case "Title":
                    value = f"{value}_{scenario_id}"
                    details["Title"] = value
                    self.page.locator("//span[text()='Title']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Deal updated successfully").wait_for()
                    self.page.get_by_text("Title updated").first.wait_for()
                case "Amount":
                    self.page.locator("//span[text()='Amount']//following-sibling::div").first.click()
                    self.page.locator(".amount-input").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Deal updated successfully").wait_for()
                    self.page.get_by_text("Amount updated").first.wait_for()
                case "Priority":
                    self.page.locator("//span[text()='Priority']//following-sibling::div").first.click()
                    self.page.locator("#priority input.ant-select-selection-search-input").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Deal updated successfully").wait_for()
                    self.page.get_by_text("Priority updated").first.wait_for()
                case "Deal Type":
                    self.page.locator("//span[text()='Deal Type']//following-sibling::div").first.click()
                    self.page.locator("#deal_type input.ant-select-selection-search-input").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_text("Deal updated successfully").wait_for()
                    self.page.get_by_text("Deal Type updated").first.wait_for()
                case "Description":
                    self.page.locator("//span[text()='Description']//following-sibling::div").first.click()
                    self.page.locator(".edit_inputs").fill(value)
                    self.page.keyboard.press("Enter")
                    self.page.get_by_text("Deal updated successfully").wait_for()
                    self.page.get_by_text("Description updated").first.wait_for()
                case "Tags":
                    self.page.locator("//span[text()='Tags']//following-sibling::div").first.click()
                    self.page.locator("#tags .ant-select-selection-search-input").fill(value)
                    self.page.locator(".ant-select-item-option-content", has_text=value).first.click()
                    self.page.get_by_placeholder("Enter description").fill("Update Deal")
                    self.page.locator("button.primary_medium").first.click()
                    self.page.get_by_text("Deal updated successfully").wait_for()
                    self.page.get_by_text("Tags updated").first.wait_for()
        EnvSetup.get_current_deal_details().update(details)

    def submitUpdateDealForm(self):
        self.page.get_by_role("button", name="Update Deal").click()
        self.page.wait_for_timeout(2000)

    def deleteCurrentDeal(self):
        title = EnvSetup.get_current_deal_details().get("Title", "")
        self.searchAndVerifyDeal(title, "Title")
        self.page.get_by_role("button", name="more_icon").first.click()
        self.page.get_by_role("menuitem").filter(has_text="Delete").click()
        self.page.get_by_role("button", name="Delete").click()

    def verifyDealDeleted(self):
        title = EnvSetup.get_current_deal_details().get("Title", "")
        self.navigateToCRMDeals()
        self.verifyDealsListVisible()
        search_input = self.page.locator('.action_bar_buttons  input[placeholder*="Search"]').first
        self.page.wait_for_timeout(5000)
        search_input.fill("")
        self.page.wait_for_timeout(5000)
        search_input.fill(title)
        search_input.press("Enter")
        self.page.wait_for_timeout(2000)
        try:
            self.page.get_by_text("No results found").wait_for(timeout=15000)
        except Exception:
            raise AssertionError(f"Deal with title '{title}' still appears in search results after deletion")

    def searchAndVerifyDeal(self, search_term, field_name="value", retries=5, retry_interval=3000):
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
            f"Deal not found in search results after {retries} attempts "
            f"when searching by {field_name}: '{search_term}'"
        )
