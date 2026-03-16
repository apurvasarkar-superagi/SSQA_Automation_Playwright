import pytest
from pytest_bdd import when, then, parsers
from sales.scr.Leads.feature_code.leadspage import LeadsPage
from sales.runners.env_setup import EnvSetup


@pytest.fixture(autouse=True)
def reset_lead_state():
    """Clear lead state before each scenario to prevent cross-test leakage."""
    EnvSetup.clear_current_lead_details()
    yield
    EnvSetup.clear_current_lead_details()


@then("User navigates to CRM Leads page and Leads list should be visible")
def user_navigates_to_crm_leads_and_list_visible(page):
    LeadsPage(page).navigateToCRMLeads()
    LeadsPage(page).verifyLeadsListVisible()


@when(parsers.parse('User adds a lead with details {lead_details}'))
def user_adds_lead(page, lead_details):
    details = {}
    for pair in lead_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    LeadsPage(page).clickAddLead()
    LeadsPage(page).fillLeadDetails(details)
    LeadsPage(page).submitAddLeadForm()



@then("Search current lead fields and verify")
def search_current_lead_fields_and_verify(page):
    email = EnvSetup.get_current_lead_details().get("Email", "")
    last_name = EnvSetup.get_current_lead_details().get("Last Name", "")
    first_name = EnvSetup.get_current_lead_details().get("First Name", "")
    lp = LeadsPage(page)
    lp.navigateToCRMLeads()
    lp.verifyLeadsListVisible()
    search_fields = {
        "First Name": first_name,
        "Last Name": last_name,
        "Email": email,
    }
    for field_name, search_term in search_fields.items():
        assert search_term, f"Search term for '{field_name}' is empty"
        lp.searchAndVerifyLead(search_term, field_name)


@when("User opens edit form for current lead")
def user_opens_edit_form_for_current_lead(page):
    LeadsPage(page).openEditFormForCurrentLead()


@when(parsers.parse('User updates lead with details {update_details}'))
def user_updates_lead(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    LeadsPage(page).fillLeadDetails(details)
    LeadsPage(page).submitUpdateLeadForm()


@when("User opens details page for current lead")
def user_opens_details_page_for_current_lead(page):
    LeadsPage(page).openDetailsPageForCurrentLead()


@when(parsers.parse('User updates lead on details page with {update_details}'))
def user_updates_lead_on_details_page(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    LeadsPage(page).updateLeadOnDetailsPage(details)
