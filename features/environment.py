import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import allure

from config.config_loader import load_config
from src.core.api_client import APIClient
from src.core.logger import configure_logging,get_logger
from src.endpoints.users_api import UsersAPI

log=get_logger("environment")

def before_all(context):
    env_name=context.config.userdata.get("env",os.getenv("TEST_ENV","qa"))
    context.settings=load_config(env_name)

    log_file=configure_logging(context.settings.get("log_level","INFO"))
    log.info("="*78)
    log.info("Starting test run | env=%s | base_url=%s",env_name,context.settings["base_url"])
    log.info("Log file: %s",log_file)
    log.info("="*78)

    context.client=APIClient(context.settings)
    context.users_api=UsersAPI(context.client)

    context.created_user_ids=[]

def after_all(context):
    _cleanup_created_users(context)
    if getattr(context,"client",None):
        context.client.close()
    log.info("Test run finished")

def before_feature(context,feature):
    log.info("FEATURE: %s",feature.name)

def before_scenario(context,scenario):
    log.info("-"*78)
    log.info("SCENARIO: %s %s",scenario.name,scenario.tags)

    context.response=None
    context.request_payload=None
    context.response_body=None
    context.stash={}

    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")

def after_scenario(context,scenario):
    if scenario.status.name=="failed":
        _attach_failure_context(context,scenario)
    log.info("RESULT: %s -> %s",scenario.name,scenario.status.name.upper())

def after_step(context,step):
    if step.status.name=="failed":
        log.error("STEP FAILED: %s %s",step.keyword,step.name)
        if step.error_message:
            allure.attach(step.error_message,f"Failure: {step.name}",allure.attachment_type.TEXT)


#helpers
def _attach_failure_context(context, scenario):
    try:
        if getattr(context, "response", None) is not None:
            allure.attach(
                f"URL: {context.response.url}\n"
                f"Status: {context.response.status_code}\n"
                f"Body: {context.response.text[:2000]}",
                "Last response at failure",
                allure.attachment_type.TEXT,
            )
    except Exception as exc:                        # pragma: no cover
        log.debug("Could not attach failure context: %s", exc)


def _cleanup_created_users(context):
    for user_id in getattr(context, "created_user_ids", []):
        try:
            context.users_api.delete(user_id)
            log.info("Cleaned up user id=%s", user_id)
        except Exception as exc:
            log.warning("Cleanup failed for user id=%s: %s", user_id, exc)
