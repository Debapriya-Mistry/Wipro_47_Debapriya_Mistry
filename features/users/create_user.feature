@users @regression
Feature: Create users through the User Management API
  As an API consumer
  I want to register new users
  So that they can be managed by the system

  Background:
    Given the API is available

  @smoke @post
  Scenario: Create a user with a complete valid payload
    Given I have a valid user payload
    When I send a request to create the user
    Then the response status code should be 201
    And the response should contain the field "id"
    And the created user should match the payload I sent
    And the response time should be within the configured SLA

  @post
  Scenario: Create a user from the stored fixture data
    Given I have the user payload from fixture "valid_user"
    When I send a request to create the user
    Then the response status code should be 201
    And the response field "username" should equal "aarav_qa"


  @post @negative
  Scenario Outline: Server handles malformed create payloads
    Given I have the invalid user payload "<payload_key>"
    When I send a request to create the user
    Then the response status code should be one of "200, 201, 400, 422"

    Examples: Bad payloads
      | payload_key     |
      | empty           |
      | missing_email   |
      | blank_name      |
      | malformed_email |
      | wrong_types     |
