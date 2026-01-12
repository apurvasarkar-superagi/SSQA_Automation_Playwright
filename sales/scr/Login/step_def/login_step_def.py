from pytest_bdd import given, when, then, parsers
from sales.scr.Login.feature_code.LoginPage import LoginPage
from sales.scr.Common.feature_code.common import commonScript
from sales.scr.Settings.feature_code.settingspage import SettingsPage


@given("User navigates to the login page")
def user_navigates_to_login_page(page):
    """Step definition for navigating to the login page"""
    login_page = LoginPage(page)
    login_page.navigate()


@when(parsers.parse("User signs in with {cred_key} credentials"))
def user_signs_in_with_credentials(page, cred_key):
    """Step definition for signing in with specific credentials"""
    login_page = LoginPage(page, cred_key=cred_key)
    login_page.login()


@when("User navigates to Settings page")
def user_navigates_to_settings_page(page):
    """Step definition for navigating to Settings page"""
    commonScript(page).goToSettings()


@then("User should verify all settings options are present")
def user_verifies_all_settings_options(page):
    """Step definition for verifying all settings options"""
    settings_page = SettingsPage(page)
    settings_page.verifyEverythingInSettings()


@then("User should verify Profile option is available in settings sidebar")
def user_verifies_profile_option_in_sidebar(page):
    """Step definition for verifying Profile option in settings sidebar"""
    settings_page = SettingsPage(page)
    # The verifyEverythingInSettings method already checks for Profile
    # If you need a separate verification, you can add a method to SettingsPage
    settings_page.verifyEverythingInSettings()