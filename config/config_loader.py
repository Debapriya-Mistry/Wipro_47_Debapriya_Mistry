import os
import re
from email.policy import default
from pathlib import Path
from typing import Any,Dict
import yaml

CONFIG_FILE=Path(__file__).parent/"config.yaml"
_VAR_PATTERN=re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")

class Config(dict):
    def __getattr__(self, item) -> Any:
        try:
            value=self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc
        return Config(value) if isinstance(value,dict) else value

def _interpolate(node:Any)->Any:
    if isinstance(node,dict):
        return {k: _interpolate(v) for k,v in node.items()}
    if isinstance(node,list):
        return [_interpolate(v) for v in node]
    if isinstance(node,str):
        def repl(match:"re.Match")->str:
            name,default=match.group(1),match.group(2)
            return os.getenv(name,default if default is not None else "")
        return _VAR_PATTERN.sub(repl,node)
    return node

def load_config(env:str | None=None)->Config:
    env=env or os.getenv("TEST_ENV","qa")
    with CONFIG_FILE.open(encoding="utf-8") as handle:
        raw=yaml.safe_load(handle)
    environments=raw.get("environments",{})
    if env not in environments:
        raise ValueError(
            f"Unknown environment '{env}' . Available: {list(environments)}"
        )
    merged:Dict[str,Any]={**raw.get("default",{}),**environments[env]}
    merged["env_name"]=env

    if os.getenv("BASE_URL"):
        merged["base_url"]=os.environ["BASE_URL"]
    return Config(_interpolate(merged))
