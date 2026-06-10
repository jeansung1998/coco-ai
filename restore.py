import os
import shutil

BACKUP_DIR = "memory_backup"
MEMORY_FILE = "memory.json"


def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return []

    files = []

    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith(".json"):
            files.append(filename)

    files.sort()
    return files


def restore_backup(index):
    backups = list_backups()

    if not backups:
        return None

    if index < 1 or index > len(backups):
        return None

    selected = backups[index - 1]
    source = os.path.join(BACKUP_DIR, selected)

    shutil.copy(source, MEMORY_FILE)

    return selected