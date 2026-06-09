import ollama
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


def remember(memory, user_input):
    text = user_input.strip()

    if "내 이름은" in text:
        name = text.replace("내 이름은", "").replace("이야", "").replace("야", "").strip()
        memory["profile"]["name"] = name
        return f"이름을 기억했습니다. ({name})"

    if "내가 좋아하는 음식은" in text:
        food = text.replace("내가 좋아하는 음식은", "").replace("이야", "").replace("야", "").strip()
        memory["likes"]["food"] = food
        return f"좋아하는 음식을 기억했습니다. ({food})"

    if "내가 좋아하는 색은" in text:
        color = text.replace("내가 좋아하는 색은", "").replace("이야", "").replace("야", "").strip()
        memory["likes"]["color"] = color
        return f"좋아하는 색을 기억했습니다. ({color})"

    if "내 프로젝트는" in text:
        project = text.replace("내 프로젝트는", "").replace("이야", "").replace("야", "").strip()
        memory["projects"]["main"] = project
        return f"프로젝트를 기억했습니다. ({project})"

    if text.startswith("기억해"):
        fact = text.replace("기억해", "").strip()
        memory["facts"].append({
            "content": fact,
            "time": datetime.now().isoformat()
        })
        return f"기억했습니다. ({fact})"

    return None


def recall(memory, user_input):
    text = user_input.strip()

    if "내 이름이 뭐야" in text:
        return memory["profile"].get("name", "아직 모릅니다.")

    if "내가 좋아하는 음식이 뭐야" in text:
        return memory["likes"].get("food", "아직 모릅니다.")

    if "내가 좋아하는 색이 뭐야" in text:
        return memory["likes"].get("color", "아직 모릅니다.")

    if "내 프로젝트가 뭐야" in text:
        return memory["projects"].get("main", "아직 모릅니다.")

    if "뭘 기억" in text or "기억한 것" in text:
        facts = memory.get("facts", [])
        if not facts:
            return "아직 기억한 내용이 없습니다."
        return "\n".join([f"- {item['content']}" for item in facts])

    return None


def ask_coco(memory, user_input):
    prompt = f"""
너는 사용자의 개인 AI 비서 코코 AI다.

저장된 사용자 기억:
{json.dumps(memory, ensure_ascii=False, indent=2)}

사용자 질문:
{user_input}

위 기억을 참고해서 자연스럽게 한국어로 대답해.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


def main():
    memory = load_memory()

    print("코코 AI 5호 시작!")
    print("종료하려면 exit 입력")

    while True:
        user_input = input("\n나: ")

        if user_input.lower() == "exit":
            save_memory(memory)
            print("코코: 기억을 저장하고 종료합니다.")
            break

        remembered = remember(memory, user_input)
        if remembered:
            save_memory(memory)
            print("코코:", remembered)
            continue

        recalled = recall(memory, user_input)
        if recalled:
            print("코코:", recalled)
            continue

        memory["history"].append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().isoformat()
        })

        answer = ask_coco(memory, user_input)

        memory["history"].append({
            "role": "coco",
            "content": answer,
            "time": datetime.now().isoformat()
        })

        save_memory(memory)
        print("코코:", answer)


if __name__ == "__main__":
    main()