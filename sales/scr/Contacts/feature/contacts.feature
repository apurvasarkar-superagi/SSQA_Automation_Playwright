@contacts @CRM
Feature: Verify Contacts functionality in CRM

  @contacts_1
  Scenario Outline: Verify user can add a new contact
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Contacts page and Contacts list should be visible
    When User adds a contact with details <contact_details>
    Then User should see "Contact added successfully" message
    And User should see contact email from <contact_details> in profile details

    Examples:
      | contact_details                              |
      | Apurva___Sarkar___apurva.sarkar@superagi.com |
