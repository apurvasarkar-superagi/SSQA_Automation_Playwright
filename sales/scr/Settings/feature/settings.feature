@settings
Feature: Verify user sign in and settings verification

  @settings_1
  Scenario: Verify user can settings
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    And User navigates to Settings page
    Then User should verify all settings options are present
    And User should verify Profile option is available in settings sidebar