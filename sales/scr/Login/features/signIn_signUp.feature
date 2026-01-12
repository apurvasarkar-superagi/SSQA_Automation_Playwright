@signIn
Feature: Verify user sign in and settings verification

  @signIn_1
  Scenario: Verify user can sign in and access settings
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    And User navigates to Settings page
    Then User should verify all settings options are present
    And User should verify Profile option is available in settings sidebar

  @signIn_2
  Scenario: Verify user can sign in and access settings 2
    Given User navigates to the login page
    When User signs in with inbound_call_campaign_cred credentials
    And User navigates to Settings page
    Then User should verify all settings options are present
    And User should verify Profile option is available in settings sidebar