import pytest
from pytest_bdd import when, then, parsers
from sales.scr.Deals.feature_code.dealspage import DealsPage
from sales.runners.env_setup import EnvSetup


@pytest.fixture(autouse=True)
def reset_deal_state():
    """Clear deal state before each scenario to prevent cross-test leakage."""
    EnvSetup.clear_current_deal_details()
    yield
    EnvSetup.clear_current_deal_details()


@then("User navigates to CRM Deals page and Deals list should be visible")
def user_navigates_to_crm_deals_and_list_visible(page):
    DealsPage(page).navigateToCRMDeals()
    DealsPage(page).verifyDealsListVisible()


@when(parsers.parse('User adds a deal with details {deal_details}'))
def user_adds_deal(page, deal_details):
    details = {}
    for pair in deal_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    DealsPage(page).clickAddDeal()
    DealsPage(page).fillDealDetails(details)
    DealsPage(page).submitAddDealForm()


@then("Search current deal fields and verify")
def search_current_deal_fields_and_verify(page):
    title = EnvSetup.get_current_deal_details().get("Title", "")
    dp = DealsPage(page)
    dp.navigateToCRMDeals()
    dp.verifyDealsListVisible()
    assert title, "Search term for 'Title' is empty"
    dp.searchAndVerifyDeal(title, "Title")


@when("User opens edit form for current deal")
def user_opens_edit_form_for_current_deal(page):
    DealsPage(page).openEditFormForCurrentDeal()


@when(parsers.parse('User updates deal with details {update_details}'))
def user_updates_deal(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    DealsPage(page).fillDealDetails(details)
    DealsPage(page).submitUpdateDealForm()


@when("User opens details page for current deal")
def user_opens_details_page_for_current_deal(page):
    DealsPage(page).openDetailsPageForCurrentDeal()


@when(parsers.parse('User updates deal on details page with {update_details}'))
def user_updates_deal_on_details_page(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    DealsPage(page).updateDealOnDetailsPage(details)


@when("User deletes current deal")
def user_deletes_current_deal(page):
    DealsPage(page).deleteCurrentDeal()


@then("Current deal should not appear in search results")
def current_deal_should_not_appear_in_search_results(page):
    DealsPage(page).verifyDealDeleted()
