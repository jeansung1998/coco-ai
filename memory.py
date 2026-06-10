import os
import json
from datetime import datetime

MEMORY_FILE = "memory.json"


def default_memory():
    return {
        "profile": {},
        "likes": {},
        "projects": {},
        "facts": [],
        "history": []
    }


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return default_memory()

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def fact_exists(memory, content):
    for item in memory.get("facts", []):
        if item.get("content") == content:
            return True
    return False


def add_fact(memory, content):
    if fact_exists(memory, content):
        return False

    memory["facts"].append({
        "content": content,
        "time": datetime.now().isoformat()
    })
    return True


def delete_fact(memory, keyword):
    facts = memory.get("facts", [])

    for item in facts:
        if keyword in item.get("content", ""):
            facts.remove(item)
            return True

    return False


def update_fact(memory, keyword, new_content):
    facts = memory.get("facts", [])

    for item in facts:
        if keyword in item.get("content", ""):
            old_content = item.get("content", "")
            item["content"] = new_content
            item["updated_time"] = datetime.now().isoformat()
            return old_content

    return None