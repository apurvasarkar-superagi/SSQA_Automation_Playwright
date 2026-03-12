import os
from pytest_bdd import when, then, parsers
from sales.scr.Leads.feature_code.leadspage import LeadsPage


@then("User navigates to CRM Leads page and Leads list should be visible")
def user_navigates_to_crm_leads_and_list_visible(page):
    LeadsPage(page).navigateToCRMLeads()
    LeadsPage(page).verifyLeadsListVisible()


@when("User clicks Add Lead button")
def user_clicks_add_lead_button(page):
    LeadsPage(page).clickAddLead()


@when(parsers.parse('User fills lead details with first name "{first_name}" last name "{last_name}" and email "{email}"'))
def user_fills_lead_details(page, first_name, last_name, email):
    scenario_id = os.environ.get("SCENARIO_ID", "")
    if "@" in email and scenario_id:
        local, domain = email.split("@", 1)
        email = f"{local}+{scenario_id}@{domain}"
    LeadsPage(page).fillLeadDetails(first_name, last_name, email)


@when("User submits the add lead form")
def user_submits_add_lead_form(page):
    LeadsPage(page).submitAddLeadForm()
