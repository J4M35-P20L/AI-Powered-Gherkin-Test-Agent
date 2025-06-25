Feature: Multi-step User Authentication

  Scenario: Valid login
    Given I am on the website "https://myhubstaging.smdservers.net/"
    And I am under the SiteLink Web Edition header
    When I enter "CorpCode" as "SLQA"
    When I enter "LocationCode" as "TEST7"
    When I enter "Username" as "AUTO"
    When I enter "Password" as "AUTO"
    Then I should "first click login to reveal the password field, then enter the password, and finally click login again to complete sign-in"