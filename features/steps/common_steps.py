import allure
from behave import given,when,then

from src.core.logger import get_logger
from src.utils import assertions as verify
from src.utils.json_schema_validator import validate_schema

log=get_logger("common_steps")

@given('the API is available')
def step_api_available(context):
    with allure.step(f"Base URL: {context.settings['base_url']}"):
        assert context.client is not None,"API Client was not initialised"
        allure.dynamic.parameter("environment",context.settings["env_name"])
        allure.dynamic.parameter("base_url",context.settings["base_url"])

@when('I send a {method} request to "{endpoint}"')
def step_send_generic_request(context, method, endpoint):
    payload = getattr(context, "request_payload", None)
    context.response = context.client.request(method, endpoint, json=payload)
    _cache_body(context)

@when('I store the response field "{path}" as "{alias}"')
@then('I store the response field "{path}" as "{alias}"')
def step_store_field(context, path, alias):
    value = verify.get_by_path(context.response_body, path)
    context.stash[alias] = value
    log.info("Stored %s = %s", alias, value)

@then('the response status code should be {expected:d}')
def step_status_code(context, expected):
    with allure.step(f"Status code is {expected}"):
        verify.assert_status_code(context.response, expected)

@then('the response status code should be one of "{codes}"')
def step_status_code_in(context, codes):
    expected = [int(code.strip()) for code in codes.split(",")]
    verify.assert_status_in(context.response, expected)

@then('the response content type should be JSON')
def step_content_type_json(context):
    verify.assert_content_type_json(context.response)

@then('the response should match the "{schema_name}" schema')
def step_validate_schema(context, schema_name):
    with allure.step(f"Validate against {schema_name}"):
        validate_schema(context.response_body, schema_name)


@then('the response time should be within the configured SLA')
def step_response_time_sla(context):
    max_ms = context.settings.get("max_response_time_ms", 3000)
    verify.assert_response_time(context.response, max_ms)


@then('the response time should be less than {max_ms:d} ms')
def step_response_time_explicit(context, max_ms):
    verify.assert_response_time(context.response, max_ms)


@then('the response should contain the field "{path}"')
def step_field_present(context, path):
    verify.assert_field_not_empty(context.response_body, path)

@then('the response field "{path}" should equal "{expected}"')
def step_field_equals(context, path, expected):
    verify.assert_json_field_equals(context.response_body, path, expected)


@then('the response field "{path}" should not be empty')
def step_field_not_empty(context, path):
    verify.assert_field_not_empty(context.response_body, path)


@then('the response body should be empty')
def step_body_empty(context):
    body = context.response_body
    assert body in (None, {}, [], ""), f"Expected an empty body, got: {body}"

@then('the response should contain {count:d} users')
@then('the response should contain {count:d} items')
def step_item_count(context, count):
    body = context.response_body
    assert isinstance(body, list), f"Expected a list, got {type(body).__name__}"
    assert len(body) == count, f"Expected {count} items, got {len(body)}"


@then('every item in the response should have "{field}" equal to the stored "{alias}"')
def step_every_item_matches_stored(context, field, alias):
    expected = str(context.stash[alias])
    mismatches = [item for item in context.response_body
                  if str(item.get(field)) != expected]
    assert not mismatches, (
        f"{len(mismatches)} item(s) had '{field}' != {expected}"
    )

#helper
def _cache_body(context):
    try:
        context.response_body = context.response.json()
    except ValueError:
        context.response_body = context.response.text or None
