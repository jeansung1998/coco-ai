from datetime import datetime
import os

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def log_message(role, message):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"{today}.txt")

    timestamp = datetime.now().strftime("%H:%M:%S")

    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {message}\n")