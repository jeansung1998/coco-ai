import os
import json
from datetime import datetime

BACKUP_DIR = "memory_backup"


def backup_memory(memory):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    now = datetime.now().strftime("%Y-%m-%d_%H%M")
    backup_file = os.path.join(BACKUP_DIR, f"memory_{now}.json")

    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

    return backup_file