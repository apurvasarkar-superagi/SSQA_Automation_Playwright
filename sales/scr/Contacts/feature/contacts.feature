@contact @CRM
Feature: Verify Contacts functionality in CRM

  @contact_1
  Scenario Outline: Verify user can add a new contact
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Contacts page and Contacts list should be visible
    When User adds a contact with details <contact_details>
    Then User should see "Contact added successfully" message
    And User should see contact email in profile details
    And Search current contact fields and verify

    Examples:
      | contact_details                              |
      | First Name=CTQATest,Last Name=Contlo,Email=qaautomation@contlo.com,Phone Number=+918888888888,LinkedIn URL=www.linkedin.in,Address=456 Oak Avenue,City=San Francisco,State=California,Country=United States,Zipcode=94102,Current Company=Contlo,Current Role=QA Automation Engineer,Description=Quality Assurance professional specializing in automation testing,Tags=automation |