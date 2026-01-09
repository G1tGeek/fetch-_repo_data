import os
from datetime import datetime

LOG_FILE = None


def init_logger(log_dir="logs", prefix="bitbucket_inventory"):
    global LOG_FILE
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE = os.path.join(log_dir, f"{prefix}_{ts}.log")


def log(msg: str, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] [{level}] {msg}"

    print(formatted)

    if LOG_FILE:
        with open(LOG_FILE, "a") as f:
            f.write(formatted + "\n")
