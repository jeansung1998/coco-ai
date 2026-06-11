import os
import json
import urllib.parse
import urllib.request
from datetime import datetime

import ollama

from pc_control import handle_pc_command

try:
    from logger import log
except:
    def log(message):
        pass


MODEL_NAME = "llama3.2"

MEMORY_FILE = "memory.json"
NOTES_FILE = "notes.json"


def default_memory():
    return {
        "profile": {},
        "likes": {},
        "projects": {},
        "facts": [],
        "history": []
    }


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def clean_memory(memory):
    clean_history = []

    for item in memory.get("history", []):
        user_text = item.get("user")
        coco_text = item.get("coco")

        if user_text is None or coco_text is None:
            continue

        if not str(user_text).strip() or not str(coco_text).strip():
            continue

        clean_history.append(item)

    memory["history"] = clean_history[-20:]

    clean_facts = []
    used = set()

    for item in memory.get("facts", []):
        content = item.get("content")

        if content is None:
            continue

        content = str(content).strip()

        if not content:
            continue

        if content in used:
            continue

        used.add(content)

        clean_facts.append({
            "content": content,
            "time": item.get("time", datetime.now().isoformat())
        })

    memory["facts"] = clean_facts

    return memory


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return default_memory()

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)
    except:
        memory = default_memory()

    for key, value in default_memory().items():
        if key not in memory:
            memory[key] = value

    memory = clean_memory(memory)
    save_memory(memory)

    return memory


def add_history(memory, user_text, coco_text):
    if not user_text or not coco_text:
        return

    memory["history"].append({
        "user": user_text,
        "coco": coco_text,
        "time": datetime.now().isoformat()
    })

    memory["history"] = memory["history"][-20:]
    save_memory(memory)


def build_memory_text(memory):
    lines = []

    lines.append("[프로필]")
    for k, v in memory.get("profile", {}).items():
        lines.append(f"- {k}: {v}")

    lines.append("[취향]")
    for k, v in memory.get("likes", {}).items():
        lines.append(f"- {k}: {v}")

    lines.append("[프로젝트]")
    for k, v in memory.get("projects", {}).items():
        lines.append(f"- {k}: {v}")

    lines.append("[기억]")
    for item in memory.get("facts", []):
        content = item.get("content")
        if content:
            lines.append(f"- {content}")

    lines.append("[최근 대화]")
    recent_history = memory.get("history", [])[-5:]

    if not recent_history:
        lines.append("- 최근 대화 없음")
    else:
        for item in recent_history:
            user_text = item.get("user")
            coco_text = item.get("coco")

            if user_text and coco_text:
                lines.append(f"사용자: {user_text}")
                lines.append(f"코코: {coco_text}")

    return "\n".join(lines)


def remember_fact(memory, content):
    content = content.strip()

    if not content:
        return "기억할 내용이 없습니다."

    for item in memory.get("facts", []):
        if item.get("content") == content:
            return "이미 기억하고 있는 내용입니다."

    memory["facts"].append({
        "content": content,
        "time": datetime.now().isoformat()
    })

    save_memory(memory)

    return "기억 완료."


def delete_memory(memory, keyword):
    keyword = keyword.strip()

    if not keyword:
        return "삭제할 기억 키워드가 없습니다."

    before = len(memory["facts"])

    memory["facts"] = [
        item for item in memory["facts"]
        if keyword not in item.get("content", "")
    ]

    after = len(memory["facts"])

    save_memory(memory)

    if before == after:
        return "삭제할 기억을 찾지 못했습니다."

    return f"기억 {before - after}개 삭제 완료."


def search_memory(memory, keyword):
    keyword = keyword.strip()

    if not keyword:
        return "검색할 키워드가 없습니다."

    lines = [f"기억 검색 결과: {keyword}"]
    found = False

    for k, v in memory.get("profile", {}).items():
        if keyword in str(k) or keyword in str(v):
            lines.append(f"- 프로필 / {k}: {v}")
            found = True

    for k, v in memory.get("likes", {}).items():
        if keyword in str(k) or keyword in str(v):
            lines.append(f"- 취향 / {k}: {v}")
            found = True

    for k, v in memory.get("projects", {}).items():
        if keyword in str(k) or keyword in str(v):
            lines.append(f"- 프로젝트 / {k}: {v}")
            found = True

    for item in memory.get("facts", []):
        content = item.get("content", "")
        if keyword in content:
            lines.append(f"- 기억 / {content}")
            found = True

    for item in memory.get("history", []):
        user_text = item.get("user", "")
        coco_text = item.get("coco", "")

        if keyword in user_text or keyword in coco_text:
            lines.append(f"- 최근 대화 / 사용자: {user_text}")
            found = True

    if not found:
        return "검색 결과가 없습니다."

    return "\n".join(lines)


def memory_status(memory