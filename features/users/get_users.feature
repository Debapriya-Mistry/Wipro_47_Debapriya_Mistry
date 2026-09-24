@users @regression
Feature: Retrieve users from the User Management API
  As an API consumer
  I want to read user records
  So that I can display and verify user information

  Background:
    Given the API is available

  @smoke @get
  Scenario: Fetch the complete list of users
    When I request the list of all users
    Then the response status code should be 200
    And the response content type should be JSON
    And the response should match the "users_list_schema.json" schema
    And the response should contain 10 users
    And the response time should be within the configured SLA

  @smoke @get
  Scenario: Fetch a single user by a valid id
    When I request the user with id 1
    Then the response status code should be 200
    And the response should match the "user_schema.json" schema
    And the response field "id" should equal "1"
    And the response field "username" should equal "Bret"
    And the response field "address.geo.lat" should not be empty

  @get @negative
  Scenario: Fetch a user that does not exist
    When I request the user with id 9999
    Then the response status code should be 404
    And the response body should be empty

  @get @negative
  Scenario Outline: Invalid user identifiers are rejected
    When I request the user with id <user_id>
    Then the response status code should be <status>

    Examples: Invalid identifiers
      | user_id | status |
      | 0       | 404    |
      | -1      | 404    |
      | abc     | 404    |

  @get @filtering
  Scenario Outline: Filter users by a query parameter
    When I search for users with "<field>" equal to "<value>"
    Then the response status code should be 200
    And the response should contain 1 users
    And the response field "0.<field>" should equal "<value>"

    Examples: Filters
      | field    | value             |
      | username | Bret              |
      | email    | Sincere@april.biz |
      | id       | 3                 |
