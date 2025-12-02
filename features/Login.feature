Feature: Myhub slwe login

  @smoke @regression @auctionLogin
  Scenario: login to the myhub slwe site
    Given I am on SiteLink myHub page
    And I am under the "SiteLink Web Edition" section
    When I enter "SLQA" into field with selector "#Client_CorpCode"
    When I enter Locationcode as "TEST1"
    When I enter Username as "AUTO"
    And I click on "Login" button
    Then I wait for "Password"
    When I enter Password as "AUTO"
    And I click on "Login" button
    Then I should be logged in successfully and see the "Dashboard" page