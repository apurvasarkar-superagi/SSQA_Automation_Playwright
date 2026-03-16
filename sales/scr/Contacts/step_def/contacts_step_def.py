import pytest
from pytest_bdd import when, then, parsers
from sales.scr.Contacts.feature_code.contactspage import ContactsPage
from sales.runners.env_setup import EnvSetup

@pytest.fixture(autouse=True)
def reset_contact_state():
    """Clear contact state before each scenario to prevent cross-test leakage."""
    EnvSetup.clear_current_contact_details()
    EnvSetup.set_current_identifier("")
    yield
    EnvSetup.clear_current_contact_details()


@then("User navigates to CRM Contacts page and Contacts list should be visible")
def user_navigates_to_crm_contacts_and_list_visible(page):
    ContactsPage(page).navigateToCRMContacts()
    ContactsPage(page).verifyContactsListVisible()


@when(parsers.parse('User adds a contact with details {contact_details}'))
def user_adds_contact(page, contact_details):
    details = {}
    for pair in contact_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    ContactsPage(page).clickAddContact()
    ContactsPage(page).fillContactDetails(details)
    ContactsPage(page).submitAddContactForm()



@then("Search current contact fields and verify")
def search_current_contact_fields_and_verify(page):
    email = EnvSetup.get_current_contact_details().get("Email", "")
    last_name = EnvSetup.get_current_contact_details().get("Last Name", "")
    first_name = EnvSetup.get_current_contact_details().get("First Name", "")
    cp = ContactsPage(page)
    cp.navigateToCRMContacts()
    cp.verifyContactsListVisible()
    search_fields = {
        "First Name": first_name,
        "Last Name": last_name,
        "Email": email,
    }
    for field_name, search_term in search_fields.items():
        assert search_term, f"Search term for '{field_name}' is empty"
        cp.searchAndVerifyContact(search_term, field_name)


@when("User opens edit form for current contact")
def user_opens_edit_form_for_current_contact(page):
    ContactsPage(page).openEditFormForCurrentContact()


@when(parsers.parse('User updates contact with details {update_details}'))
def user_updates_contact(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    ContactsPage(page).fillContactDetails(details)
    ContactsPage(page).submitUpdateContactForm()


@when("User opens details page for current contact")
def user_opens_details_page_for_current_contact(page):
    ContactsPage(page).openDetailsPageForCurrentContact()


@when(parsers.parse('User updates contact on details page with {update_details}'))
def user_updates_contact_on_details_page(page, update_details):
    details = {}
    for pair in update_details.split(","):
        key, _, value = pair.partition("=")
        details[key.strip()] = value.strip()
    ContactsPage(page).updateContactOnDetailsPage(details)


@when("User deletes current contact")
def user_deletes_current_contact(page):
    ContactsPage(page).deleteCurrentContact()


@then("Current contact should not appear in search results")
def current_contact_should_not_appear_in_search_results(page):
    ContactsPage(page).verifyContactDeleted()