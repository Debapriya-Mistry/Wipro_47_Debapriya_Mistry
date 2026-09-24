@users @regression @delete
Feature: Delete users
  As an API consumer
  I want to remove user records
  So that obsolete accounts no longer exist

  Background:
    Given the API is available


  @smoke @delete
  Scenario: Delete an existing user
    When I send a request to delete the user with id 1
    Then the response status code should be 200
    And the response time should be within the configured SLA



  @delete @negative
  Scenario: Deleting a non-existent user
    When I send a request to delete the user with id 9999
    Then the response status code should be one of "200, 204, 404"
