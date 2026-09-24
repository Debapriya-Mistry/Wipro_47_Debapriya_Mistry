from __future__ import annotations

from typing import Dict, Any

import requests
from requests.auth import AuthBase
from src.core.logger import get_logger

log=get_logger("auth")

class NoAuth(AuthBase):
    def __call__(self, request):
        return request


def build_auth(auth_config:Dict[str,Any])->AuthBase:
    auth_type=(auth_config.get("type") or "none").lower()
    log.debug("Building auth strategy: %s",auth_type)

    if auth_type=="none":
        return NoAuth()
    raise ValueError(f"Unsupported auth type: {auth_type}")
