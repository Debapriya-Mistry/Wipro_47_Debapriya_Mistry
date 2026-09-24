import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR=Path(__file__).resolve().parents[2]/"logs"
LOG_DIR.mkdir(exist_ok=True)

_CONFIGURED=False
_FORMAT="%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s"

def configure_logging(level="INFO")->Path:
    global _CONFIGURED
    log_file=LOG_DIR/f"run_{datetime.now():%Y%m%d_%H%M%S}.log"
    if _CONFIGURED:
        return log_file

    root=logging.getLogger("api_framework")
    root.setLevel(level.upper())
    root.propagate=False

    formatter=logging.Formatter(_FORMAT,datefmt="%H:%M:%S")

    console=logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler=logging.FileHandler(log_file,encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    root.addHandler(file_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    _CONFIGURED=True
    return log_file

def get_logger(name)->logging.Logger:
    return logging.getLogger(f"api_framework.{name}")



