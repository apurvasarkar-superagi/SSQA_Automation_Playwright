import os
from pytest_bdd import when, then, parsers
from sales.scr.Leads.feature_code.leadspage import LeadsPage
from playwright.sync_api import expect


@then("User navigates to CRM Leads page and Leads list should be visible")
def user_navigates_to_crm_leads_and_list_visible(page):
    LeadsPage(page).navigateToCRMLeads()
    LeadsPage(page).verifyLeadsListVisible()


@when(parsers.parse('User adds a lead with details {lead_details}'))
def user_adds_lead(page, lead_details):
    first_name, last_name, email = lead_details.split("___")
    scenario_id = os.environ.get("SCENARIO_ID", "")
    if "@" in email and scenario_id:
        local, domain = email.split("@", 1)
        email = f"{local}+{scenario_id}@{domain}"
    LeadsPage(page).clickAddLead()
    LeadsPage(page).fillLeadDetails(first_name, last_name, email)
    LeadsPage(page).submitAddLeadForm()


@then(parsers.parse('User should see lead email from {lead_details} in profile details'))
def user_should_see_lead_email_in_profile_details(page, lead_details):
    _, _, email = lead_details.split("___")
    scenario_id = os.environ.get("SCENARIO_ID", "")
    if "@" in email and scenario_id:
        local, domain = email.split("@", 1)
        email = f"{local}+{scenario_id}@{domain}"
    expect(page.locator("#profile_details_section").get_by_text(email)).to_be_visible()
