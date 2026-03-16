@company @CRM
Feature: Verify Companies functionality in CRM

  @company_1
  Scenario Outline: Verify user can add a new company
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Companies page and Companies list should be visible
    When User adds a company with details <company_details>
    Then User should see "Company added successfully" message
    And Search current company fields and verify

    Examples:
      | company_details                                                                                                                                                                                                                                    |
      | Name=CTQATestCo,Industry=Technology,Country=United States,Website=www.contlo.com,LinkedIn URL=www.linkedin.in,Description=QA Automation test company for testing purposes,Company Size=1-10,Annual Revenue=1000000,City=San Francisco,State=California,Zipcode=94102,Tags=automation |

  @company_3
  Scenario Outline: Verify user is able to edit via Details Page
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Companies page and Companies list should be visible
    When User adds a company with details <company_details>
    Then User should see "Company added successfully" message
    And Search current company fields and verify
    When User opens details page for current company
    When User updates company on details page with <update_details>
    Then Search current company fields and verify

    Examples:
      | company_details | update_details |
      | Name=CTQATestCoDP,Industry=Technology,Country=United States,Website=www.contlo.com,LinkedIn URL=www.linkedin.in,Description=Details page test company,Company Size=1-10,Annual Revenue=1000000,City=San Francisco,State=California,Zipcode=94102,Tags=automation | Name=CTQATestCoDPUpd,Industry=Financial Services,Country=United Kingdom,Website=www.contlo-dp-updated.com,LinkedIn URL=www.linkedin.com/company/dp-updated,Description=Updated company via details page,Company Size=11-50,Annual Revenue=2000000,City=London,State=England,Zipcode=EC1A 1BB,Tags=automation-updated |

  @company_2
  Scenario Outline: Verify user can update a company via three dots menu
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Companies page and Companies list should be visible
    When User adds a company with details <company_details>
    Then User should see "Company added successfully" message
    Then User navigates to CRM Companies page and Companies list should be visible
    When User opens edit form for current company
    When User updates company with details <update_details>
    Then User should see "Company updated successfully" message
    And Search current company fields and verify

    Examples:
      | company_details | update_details |
      | Name=CTQATestCo,Industry=Technology,Country=United States,Website=www.contlo.com,LinkedIn URL=www.linkedin.in,Description=QA Automation test company for testing purposes,Company Size=1-10,Annual Revenue=1000000,City=San Francisco,State=California,Zipcode=94102,Tags=automation | Name=CTQATestCoUpd,Industry=Financial Services,Country=United Kingdom,Website=www.contlo-updated.com,LinkedIn URL=www.linkedin.com/company/updated,Description=Updated QA Automation company,Company Size=11-50,Annual Revenue=2000000,City=London,State=England,Zipcode=EC1A 1BB,Tags=automation |
