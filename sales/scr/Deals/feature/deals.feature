@deal @CRM
Feature: Verify Deals functionality in CRM

  @deal_1
  Scenario Outline: Verify user can add a new deal
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Deals page and Deals list should be visible
    When User adds a deal with details <deal_details>
    Then User should see "Deal added successfully" message
    And Search current deal fields and verify

    Examples:
      | deal_details                                                                                                                         |
      | Title=CTQATestDeal,Amount=50000,Priority=High,Deal Type=New,Description=QA Automation test deal for testing purposes,Tags=automation |

  @deal_2
  Scenario Outline: Verify user can update a deal via three dots menu
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Deals page and Deals list should be visible
    When User adds a deal with details <deal_details>
    Then User should see "Deal added successfully" message
    Then User navigates to CRM Deals page and Deals list should be visible
    When User opens edit form for current deal
    When User updates deal with details <update_details>
    Then User should see "Deal updated successfully" message
    And Search current deal fields and verify

    Examples:
      | deal_details | update_details |
      | Title=CTQATestDeal,Amount=50000,Priority=High,Deal Type=New,Description=QA Automation test deal for testing purposes,Tags=automation | Title=CTQATestDealUpd,Amount=75000,Priority=Medium,Deal Type=Existing,Description=Updated QA Automation deal,Tags=automation |

  @deal_3
  Scenario Outline: Verify user is able to edit via Details Page
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Deals page and Deals list should be visible
    When User adds a deal with details <deal_details>
    Then User should see "Deal added successfully" message
    And Search current deal fields and verify
    When User opens details page for current deal
    When User updates deal on details page with <update_details>
    Then Search current deal fields and verify

    Examples:
      | deal_details | update_details |
      | Title=CTQATestDealDP,Amount=50000,Priority=High,Deal Type=New,Description=Details page test deal,Tags=automation | Title=CTQATestDealDPUpd,Amount=75000,Priority=Medium,Deal Type=Existing,Description=Updated deal via details page,Tags=automation-updated |
