@users @regression @update
Feature: Update existing users
  As an API consumer
  I want to modify user records
  So that user information stays accurate

  Background:
    Given the API is available


  @smoke @put
  Scenario: Fully replace a user with PUT
    Given I have the user payload from fixture "update_user"
    When I send a request to replace the user with id 1
    Then the response status code should be 200
    And the response field "id" should equal "1"
    And the response field "name" should equal "Aarav Sharma Updated"
    And the response field "email" should equal "aarav.updated@example.com"

  @patch
  Scenario Outline: Partially update a single field with PATCH
    When I patch the user with id 1 setting "<field>" to "<value>"
    Then the response status code should be 200
    And the response field "<field>" should equal "<value>"

    Examples: Fields
      | field    | value                |
      | name     | Patched Name         |
      | email    | patched@example.com  |
      | phone    | 1-999-888-7777       |
      | website  | patched.example.org  |

  @put @negative
  Scenario: Updating a non-existent user is rejected
    Given I have the user payload from fixture "minimal_user"
    When I send a request to replace the user with id 9999
    Then the response status code should be one of "404, 500"
