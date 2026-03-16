@contact @CRM
Feature: Verify Contacts functionality in CRM

  @contact_1
  Scenario Outline: Verify user can add a new contact
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Contacts page and Contacts list should be visible
    When User adds a contact with details <contact_details>
    Then User should see "Contact added successfully" message
    And Search current contact fields and verify

    Examples:
      | contact_details                              |
      | First Name=CTQATest,Last Name=Contlo,Email=qaautomation@contlo.com,Phone Number=+918888888888,LinkedIn URL=www.linkedin.in,Address=456 Oak Avenue,City=San Francisco,State=California,Country=United States,Zipcode=94102,Current Company=Contlo,Current Role=QA Automation Engineer,Description=Quality Assurance professional specializing in automation testing,Tags=automation |

  @contact_2
  Scenario Outline: Verify user can update a contact via three dots menu
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Contacts page and Contacts list should be visible
    When User adds a contact with details <contact_details>
    Then User should see "Contact added successfully" message
    Then User navigates to CRM Contacts page and Contacts list should be visible
    When User opens edit form for current contact
    When User updates contact with details <update_details>
    Then User should see "Contact updated successfully" message
    And Search current contact fields and verify

    Examples:
      | contact_details | update_details |
      | First Name=CTQATest,Last Name=Contlo,Email=qaautomation@contlo.com,Phone Number=+918888888888,LinkedIn URL=www.linkedin.in,Address=456 Oak Avenue,City=San Francisco,State=California,Country=United States,Zipcode=94102,Current Company=Contlo,Current Role=QA Automation Engineer,Description=Quality Assurance professional specializing in automation testing,Tags=automation | First Name=CTQATestUpd,Last Name=ContloUpd,Email=qaautomation+upd@contlo.com,Phone Number=+917777777777,LinkedIn URL=www.linkedin.com/updated,Address=789 Pine Street,City=Los Angeles,State=New York,Country=United States,Zipcode=10001,Current Company=Contlo,Current Role=Senior QA Engineer,Description=Updated QA Automation contact,Tags=automation |

  @contact_3 @apurva
  Scenario Outline: Verify user is able to edit via Details Page
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Contacts page and Contacts list should be visible
    When User adds a contact with details <contact_details>
    Then User should see "Contact added successfully" message
    And Search current contact fields and verify
    When User opens details page for current contact
    When User updates contact on details page with <update_details>
    Then Search current contact fields and verify
    When User deletes current contact
    Then User should see "Contact deleted successfully" message
    Then Current contact should not appear in search results

    Examples:
      | contact_details | update_details |
      | First Name=CTQATestDP,Last Name=ContloDP,Email=qaautomation+dp@contlo.com,Phone Number=+918888888888,LinkedIn URL=www.linkedin.in,Address=456 Oak Avenue,City=San Francisco,State=California,Country=United States,Zipcode=94102,Current Company=Contlo,Current Role=QA Automation Engineer,Description=Details page test contact,Tags=automation | First Name=CTQATestDPUpd,Last Name=ContloDPUpd,Email=qaautomation+dpupd@contlo.com,Phone Number=+917777777777,LinkedIn URL=www.linkedin.com/dp-updated,Address=789 Pine Street,City=Los Angeles,State=New York,Country=United Kingdom,Zipcode=10001,Current Company=SuperAGI,Current Role=Senior QA Engineer,Description=Updated via details page,Tags=automation-updated |
