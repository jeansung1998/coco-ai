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


def get_importance(content):
    important_words = [
        "프로젝트",
        "목표",
        "꿈",
        "중요",
        "AI",
        "코코",
        "개발",
        "GitHub",
        "Ollama"
    ]

    score = 3

    for word in important_words:
        if word in content:
            score += 1

    if score > 10:
        score = 10

    return score


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
        "importance": get_importance(content),
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
            item["importance"] = get_importance(new_content)
            item["updated_time"] = datetime.now().isoformat()
            return old_content

    return None


def search_facts(memory, keyword):
    results = []

    keyword = keyword.strip()

    for item in memory.get("facts", []):
        content = item.get("content", "")

        if keyword in content:
            results.append(content)

    return results


def get_important_facts(memory, min_score=6):
    results = []

    for item in memory.get("facts", []):
        importance = item.get("importance", 3)

        if importance >= min_score:
            results.append(item)

    results.sort(key=lambda x: x.get("importance", 3), reverse=True)

    return results