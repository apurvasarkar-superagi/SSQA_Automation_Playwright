from time import sleep


class SettingsPage:
    def __init__(self, page):
        self.page = page

    def verifyEverythingInSettings(self):
        sidebarOptions = self.page.locator("xpath=//div[contains(@class,'sidebar_option')]")
        #verify Profile is present in SideBar
        profileTextInSettings = sidebarOptions.filter(has=self.page.get_by_text("Profile"))
        profileIconInSettings = sidebarOptions.filter(has=self.page.get_by_alt_text("profile_icon"))
        profileTextInSettings.click()
        sleep(5)

