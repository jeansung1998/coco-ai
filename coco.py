import ollama
import os
import json
from datetime import datetime
from logger import log_message

MEMORY_FILE = "memory.json"
MODEL = "llama3.2"


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

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_memory()


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def fact_exists(memory, content):
    for item in memory.get("facts", []):
        if item.get("content") == content:
            return True
    return False


def add_fact(memory, content):
    content = content.strip()

    if not content:
        return False

    if fact_exists(memory, content):
        return False

    memory["facts"].append({
        "content": content,
        "time": datetime.now().isoformat()
    })

    save_memory(memory)
    return True


def delete_fact(memory, keyword):
    keyword = keyword.strip()

    before = len(memory.get("facts", []))

    memory["facts"] = [
        item for item in memory.get("facts", [])
        if keyword not in item.get("content", "")
    ]

    after = len(memory.get("facts", []))
    save_memory(memory)

    return before - after


def build_memory_text(memory):
    lines = []

    for item in memory.get("facts", []):
        lines.append("- " + item.get("content", ""))

    if not lines:
        return "아직 저장된 중요한 기억이 없습니다."

    return "\n".join(lines)


def show_memory(memory):
    print("\n[중요 기억]")
    facts = memory.get("facts", [])

    if not facts:
        print("아직 저장된 중요한 기억이 없습니다.")
        return

    for i, item in enumerate(facts, start=1):
        print(f"{i}. {item.get('content', '')}")


def should_remember(user_input):
    keywords = [
        "기억해",
        "기억해줘",
        "저장해",
        "저장해줘",
        "잊지마",
        "중요해",
        "내 이름은",
        "나는",
        "내가 좋아하는",
        "내 프로젝트",
        "코코 AI",
        "앞으로"
    ]

    for keyword in keywords:
        if keyword in user_input:
            return True

    return False


def ask_coco(memory, user_input):
    memory_text = build_memory_text(memory)

    system_prompt = f"""
너는 사용자의 개인 AI 비서 코코 AI다.
항상 한국어로 친절하고 쉽게 대답한다.
사용자는 초보자일 수 있으니 천천히 설명한다.

아래는 사용자의 중요한 기억이다.
{memory_text}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response["message"]["content"]


def main():
    memory = load_memory()

    print("코코 AI 8.4 시작!")
    print(f"모델: {MODEL}")
    print(f"기억: {len(memory.get('facts', []))}개 로드 완료")
    print("명령어: 종료 / 중요 기억 보여줘 / 기억 삭제:키워드")
    print()

    while True:
        user_input = input("나: ").strip()

        if not user_input:
            continue

        log_message("USER", user_input)

        if user_input in ["종료", "끝", "exit", "quit"]:
            print("코코: 종료할게.")
            log_message("COCO", "종료")
            break

        if user_input == "중요 기억 보여줘":
            show_memory(memory)
            continue

        if user_input.startswith("기억 삭제:"):
            keyword = user_input.replace("기억 삭제:", "").strip()
            count = delete_fact(memory, keyword)
            print(f"코코: {count}개의 기억을 삭제했어.")
            continue

        if should_remember(user_input):
            saved = add_fact(memory, user_input)

            if saved:
                print("코코: 중요한 내용으로 기억했어.")
            else:
                print("코코: 이미 기억하고 있는 내용이야.")

        try:
            answer = ask_coco(memory, user_input)
            print("코코:", answer)
            log_message("COCO", answer)

        except Exception as e:
            print("코코: 오류가 발생했어.")
            print("오류 내용:", e)
            log_message("ERROR", str(e))


if __name__ == "__main__":
    main()