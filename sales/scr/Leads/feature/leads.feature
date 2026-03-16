@leads @CRM
Feature: Verify Leads functionality in CRM

  @leads_1
  Scenario Outline: Verify user can add a new lead
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Leads page and Leads list should be visible
    When User adds d with details <lead_details>
    Then User should see "Lead added successfully" message
    And User should see lead email from <lead_details> in profile details

    Examples:
      | lead_details                                      |
      | Apurva___Sarkar___apurvasarkar@gmail.com |
