import pytest
from pytest_bdd import when, then, parsers
from sales.scr.Companies.feature_code.companiespage import CompaniesPage
from sales.runners.env_setup import EnvSetup

@pytest.fixture(autouse=True)
def reset_company_state():
    """Clear company state before each scenario to prevent cross-test leakage."""
    EnvSetup.clear_current_company_details()
    yield
    EnvSetup.clear_current_company_details()


@then("User navigates to CRM Companies page and Companies list should be visible")
def user_navigates_to_crm_companies_and_list_visible(page):
    CompaniesPage(page).navigateToCRMCompanies()
    CompaniesPage(page).verifyCompaniesListVisible()


@when(parsers.parse('User adds a company with details {company_details}'))
def user_adds_company(page, company_details):
    details = {}
    for pair in company_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    CompaniesPage(page).clickAddCompany()
    CompaniesPage(page).fillCompanyDetails(details)
    CompaniesPage(page).submitAddCompanyForm()



@then("Search current company fields and verify")
def search_current_company_fields_and_verify(page):
    name = EnvSetup.get_current_company_details().get("Name", "")
    website = EnvSetup.get_current_company_details().get("Website", "")
    cp = CompaniesPage(page)
    cp.navigateToCRMCompanies()
    cp.verifyCompaniesListVisible()
    search_fields = {
        "Name": name,
        "Website": website,
    }
    for field_name, search_term in search_fields.items():
        assert search_term, f"Search term for '{field_name}' is empty"
        cp.searchAndVerifyCompany(search_term, field_name)


@when("User opens edit form for current company")
def user_opens_edit_form_for_current_company(page):
    CompaniesPage(page).openEditFormForCurrentCompany()


@when(parsers.parse('User updates company with details {update_details}'))
def user_updates_company(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    CompaniesPage(page).fillCompanyDetails(details)
    CompaniesPage(page).submitUpdateCompanyForm()


@when("User opens details page for current company")
def user_opens_details_page_for_current_company(page):
    CompaniesPage(page).openDetailsPageForCurrentCompany()


@when(parsers.parse('User updates company on details page with {update_details}'))
def user_updates_company_on_details_page(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    CompaniesPage(page).updateCompanyOnDetailsPage(details)


@when("User deletes current company")
def user_deletes_current_company(page):
    CompaniesPage(page).deleteCurrentCompany()


@then("Current company should not appear in search results")
def current_company_should_not_appear_in_search_results(page):
    CompaniesPage(page).verifyCompanyDeleted()
