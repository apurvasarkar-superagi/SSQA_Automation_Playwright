@leads @CRM
Feature: Verify Leads functionality in CRM

  @leads_1
  Scenario: Verify user can add a new lead
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Leads page and Leads list should be visible
    When User clicks Add Lead button
    And User fills lead details with first name "Apurva" last name "Sarkar" and email "apurvasarkar@gmail.com"
    And User submits the add lead form
    Then User should see "Lead added successfully" message