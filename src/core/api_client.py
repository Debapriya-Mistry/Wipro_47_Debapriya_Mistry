from __future__ import annotations
import json
import time
from typing import Any,Dict,Optional
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.core.auth import build_auth
from src.core.logger import get_logger

log=get_logger("api-client")

try:
    import allure
except ImportError:
    allure=None

class APIClient:
    def __init__(self,config):
        self.config = config
        self.base_url = config["base_url"].rstrip("/") + "/"
        self.timeout = config.get("timeout", 30)
        self.verify_ssl = config.get("verify_ssl", True)

        self.session = requests.Session()
        self.session.auth=build_auth(config.get("auth",{}))
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "behave-api-framework/1.0",
        })
        self._mount_retries(config.get("retries", 2),
                            config.get("backoff_factor", 0.5))

        self.last_response: Optional[requests.Response] = None

    def _mount_retries(self, total: int, backoff: float) -> None:
        retry = Retry(
            total=total,
            backoff_factor=backoff,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "PUT", "DELETE", "HEAD", "OPTIONS"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def build_url(self, endpoint: str) -> str:
        return urljoin(self.base_url, endpoint.lstrip("/"))

    def set_header(self, name: str, value: str) -> None:
        self.session.headers[name] = value

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = self.build_url(endpoint)
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("verify", self.verify_ssl)

        self._log_request(method, url, kwargs)
        started = time.perf_counter()
        try:
            response = self.session.request(method.upper(), url, **kwargs)
        except requests.exceptions.RequestException as exc:
            log.error("%s %s failed: %s", method.upper(), url, exc)
            raise
        elapsed_ms = (time.perf_counter() - started) * 1000

        self._log_response(response, elapsed_ms)
        self._attach_to_allure(method, url, kwargs, response, elapsed_ms)

        response.elapsed_ms = elapsed_ms  # convenience attribute
        self.last_response = response
        return response

    def get(self, endpoint: str, **kw) -> requests.Response:
        return self.request("GET", endpoint, **kw)

    def post(self, endpoint: str, **kw) -> requests.Response:
        return self.request("POST", endpoint, **kw)

    def put(self, endpoint: str, **kw) -> requests.Response:
        return self.request("PUT", endpoint, **kw)

    def patch(self, endpoint: str, **kw) -> requests.Response:
        return self.request("PATCH", endpoint, **kw)

    def delete(self, endpoint: str, **kw) -> requests.Response:
        return self.request("DELETE", endpoint, **kw)

    def close(self) -> None:
        self.session.close()

    @staticmethod
    def _pretty(payload: Any) -> str:
        try:
            return json.dumps(payload, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(payload)

    def _log_request(self, method: str, url: str, kwargs: Dict[str, Any]) -> None:
        log.info("--> %s %s", method.upper(), url)
        if kwargs.get("params"):
            log.debug("    params : %s", kwargs["params"])
        body = kwargs.get("json", kwargs.get("data"))
        if body is not None:
            log.debug("    body   : %s", self._pretty(body))

    def _log_response(self, response: requests.Response, elapsed_ms: float) -> None:
        log.info("<-- %s %s (%.0f ms)",
                 response.status_code, response.reason, elapsed_ms)
        preview = response.text[:1000] if response.text else "<empty>"
        log.debug("    body   : %s", preview)


    def _attach_to_allure(self, method, url, kwargs, response, elapsed_ms) -> None:
        if allure is None:
            return
        try:
            request_dump = {
                "method": method.upper(),
                "url": url,
                "headers": {k: ("***" if k.lower() == "authorization" else v)
                            for k, v in dict(self.session.headers).items()},
                "params": kwargs.get("params"),
                "body": kwargs.get("json", kwargs.get("data")),
            }
            allure.attach(self._pretty(request_dump), "HTTP Request",
                          allure.attachment_type.JSON)
            try:
                body = self._pretty(response.json())
                allure.attach(body, f"HTTP Response ({response.status_code})",
                              allure.attachment_type.JSON)
            except ValueError:
                allure.attach(response.text or "<empty>",
                              f"HTTP Response ({response.status_code})",
                              allure.attachment_type.TEXT)
            allure.attach(f"{elapsed_ms:.0f} ms", "Response Time",
                          allure.attachment_type.TEXT)
        except Exception as exc:                  # never fail a test on reporting
            log.debug("Allure attachment skipped: %s", exc)






