Feature: Basic User Workflow on Amazon

  @smoke @login
  Scenario Outline: Successful user login with valid credentials
    Given the user is on the Amazon homepage
    When the user navigates to the Sign In page
    And the user enters "<email>" in the email field
    And the user enters "<password>" in the password field
    And the user clicks the "Continue" button
    And the user clicks the "Sign In" button
    Then the user should see the "Hello, <username>" message on the navigation bar

    Examples:
      | email              | password       | username |
      | testuser@mail.com  | secure_pass123 | TestUser |
      | another_user@mail.com | mypass_2025 | Jane     |

  @search
  Scenario: Search for a specific product
    Given the user is logged in
    When the user enters "Mechanical Keyboard" in the search bar
    And the user clicks the "Search" button
    Then the user should see search results for "Mechanical Keyboard"
    And the product listing page title should contain "Mechanical Keyboard"

  @logout
  Scenario: User logout
    Given the user is logged in
    When the user navigates to the Account & Lists menu
    And the user clicks the "Sign Out" link
    Then the user should be redirected to the Amazon homepage
    And the user should see the "Sign in" button in the navigation bar