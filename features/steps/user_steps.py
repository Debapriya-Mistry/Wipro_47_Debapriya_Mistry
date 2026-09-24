import allure
from behave import given, then, when

from src.core.logger import get_logger
from src.utils import assertions as verify
from src.utils.data_generator import generate_user_payload, invalid_payloads
from src.utils.file_utils import get_user_fixture

log = get_logger("user_steps")


def _capture(context, response):
    context.response = response
    try:
        context.response_body = response.json()
    except ValueError:
        context.response_body = response.text or None

@given('I have a valid user payload')
def step_valid_payload(context):
    context.request_payload = generate_user_payload()
    allure.attach(str(context.request_payload), "Generated payload",
                  allure.attachment_type.TEXT)


@given('I have a valid user payload with name "{name}" and email "{email}"')
def step_valid_payload_with(context, name, email):
    context.request_payload = generate_user_payload(name=name, email=email)


@given('I have the user payload from fixture "{key}"')
def step_payload_from_fixture(context, key):
    context.request_payload = get_user_fixture(key)


@given('I have the invalid user payload "{key}"')
def step_invalid_payload(context, key):
    payloads = invalid_payloads()
    assert key in payloads, f"Unknown invalid payload '{key}'"
    context.request_payload = payloads[key]


@when('I request the list of all users')
def step_get_all_users(context):
    _capture(context, context.users_api.get_all())


@when('I request the user with id {user_id}')
def step_get_user_by_id(context, user_id):
    _capture(context, context.users_api.get_by_id(user_id.strip()))


@when('I search for users with "{field}" equal to "{value}"')
def step_search_users(context, field, value):
    _capture(context, context.users_api.search(**{field: value}))

@when('I send a request to create the user')
def step_create_user(context):
    response = context.users_api.create(context.request_payload)
    _capture(context, response)
    if response.status_code in (200, 201) and isinstance(context.response_body, dict):
        new_id = context.response_body.get("id")
        if new_id:
            context.stash["lastCreatedId"] = new_id


@when('I send a request to replace the user with id {user_id:d}')
def step_replace_user(context, user_id):
    _capture(context, context.users_api.update(user_id, context.request_payload))


@when('I patch the user with id {user_id:d} setting "{field}" to "{value}"')
def step_patch_user(context, user_id, field, value):
    context.request_payload = {field: value}
    _capture(context, context.users_api.partial_update(user_id, {field: value}))

@when('I send a request to delete the user with id {user_id:d}')
def step_delete_user(context, user_id):
    _capture(context, context.users_api.delete(user_id))

@then('the created user should match the payload I sent')
def step_created_matches_payload(context):
    soft = verify.SoftAssert()
    sent, received = context.request_payload, context.response_body
    for field in ("name", "username", "email", "phone", "website"):
        if field in sent:
            soft.equals(received.get(field), sent[field], field)
    with allure.step("Echoed fields match the request"):
        soft.assert_all()