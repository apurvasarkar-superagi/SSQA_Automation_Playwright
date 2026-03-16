@lead @CRM
Feature: Verify Leads functionality in CRM

  @lead_1
  Scenario Outline: Verify user can add a new lead
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Leads page and Leads list should be visible
    When User adds a lead with details <lead_details>
    Then User should see "Lead added successfully" message
    And Search current lead fields and verify

    Examples:
      | lead_details |
      | First Name=CTQATestLead,Last Name=Contlo,Email=qaautomation@contlo.com,Phone Number=+918888888888,LinkedIn URL=www.linkedin.in,Address=456 Oak Avenue,City=San Francisco,State=California,Country=United States,Zipcode=94102,Current Role=QA Automation Engineer,Description=Quality Assurance lead for automation testing,Tags=automation |

  @lead_2
  Scenario Outline: Verify user can update a lead via three dots menu
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Leads page and Leads list should be visible
    When User adds a lead with details <lead_details>
    Then User should see "Lead added successfully" message
    Then User navigates to CRM Leads page and Leads list should be visible
    When User opens edit form for current lead
    When User updates lead with details <update_details>
    Then User should see "Lead updated successfully" message
    And Search current lead fields and verify

    Examples:
      | lead_details | update_details |
      | First Name=CTQATestLead,Last Name=Contlo,Email=qaautomation@contlo.com,Phone Number=+918888888888,LinkedIn URL=www.linkedin.in,Address=456 Oak Avenue,City=San Francisco,State=California,Country=United States,Zipcode=94102,Current Role=QA Automation Engineer,Description=Quality Assurance lead for automation testing,Tags=automation | First Name=CTQATestLeadUpd,Last Name=ContloUpd,Email=qaautomation+upd@contlo.com,Phone Number=+917777777777,LinkedIn URL=www.linkedin.com/updated,Address=789 Pine Street,City=Los Angeles,State=New York,Country=United Kingdom,Zipcode=10001,Current Role=Senior QA Engineer,Description=Updated QA Automation lead,Tags=automation |

  @lead_3
  Scenario Outline: Verify user is able to edit via Details Page
    Given User navigates to the login page
    When User signs in with qaautomation_main_cred credentials
    Then User navigates to CRM Leads page and Leads list should be visible
    When User adds a lead with details <lead_details>
    Then User should see "Lead added successfully" message
    And Search current lead fields and verify
    When User opens details page for current lead
    When User updates lead on details page with <update_details>
    Then Search current lead fields and verify

    Examples:
      | lead_details | update_details |
      | First Name=CTQATestLeadDP,Last Name=ContloDP,Email=qaautomation@contlo.com,Phone Number=+918888888888,LinkedIn URL=www.linkedin.in,Address=456 Oak Avenue,City=San Francisco,State=California,Country=United States,Zipcode=94102,Current Role=QA Automation Engineer,Description=Details page test lead,Tags=automation | First Name=CTQATestLeadDPUpd,Last Name=ContloDPUpd,Email=qaautomationUpdate@contlo.com,Phone Number=+917777777777,LinkedIn URL=www.linkedin.com/dp-updated,Address=789 Pine Street,City=Los Angeles,State=New York,Country=United Kingdom,Zipcode=10001,Current Role=Senior QA Engineer,Description=Updated lead via details page,Tags=automation |