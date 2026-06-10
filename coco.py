import ollama
import os
import json
import re
import platform
import sys
from datetime import datetime
from logger import log_message

MEMORY_FILE = "memory.json"
MODEL = "llama3.2"
COCO_VERSION = "8.8"


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
            memory = json.load(f)

        base = default_memory()
        for key in base:
            if key not in memory:
                memory[key] = base[key]

        return memory

    except:
        return default_memory()


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def clean_memory_sentence(text):
    remove_words = [
        "기억해줘",
        "기억해",
        "저장해줘",
        "저장해",
        "잊지마",
        "잊지 말아줘"
    ]

    result = text.strip()

    for word in remove_words:
        result = result.replace(word, "")

    result = result.replace("..", ".")
    result = result.strip(" .")

    return result


def clean_name(name):
    name = name.strip()
    endings = ["이야", "야", "입니다", "이에요", "예요", "라고 해", "라고 합니다"]

    for ending in endings:
        if name.endswith(ending):
            name = name[:-len(ending)]

    return name.strip()


def fact_exists(memory, content):
    for item in memory.get("facts", []):
        if item.get("content") == content:
            return True
    return False


def add_fact(memory, content):
    content = clean_memory_sentence(content)

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


def should_remember(user_input):
    save_keywords = [
        "기억해",
        "기억해줘",
        "저장해",
        "저장해줘",
        "잊지마",
        "잊지 말아줘"
    ]

    for keyword in save_keywords:
        if keyword in user_input:
            return True

    return False


def update_structured_memory(memory, user_input):
    text = clean_memory_sentence(user_input)
    updated = False

    name_match = re.search(r"내 이름은\s*([가-힣a-zA-Z0-9]+)", text)
    if name_match:
        memory["profile"]["name"] = clean_name(name_match.group(1))
        updated = True

    color_match = re.search(r"좋아하는 색(?:은|깔은)?\s*([가-힣a-zA-Z0-9]+)", text)
    if color_match:
        color = color_match.group(1).strip()
        color = color.replace("이야", "").replace("야", "").replace("입니다", "")
        memory["likes"]["favorite_color"] = color
        updated = True

    if "코코 AI" in text or "코코AI" in text:
        memory["projects"]["main_project"] = "코코 AI"
        updated = True

    if updated:
        save_memory(memory)

    return updated


def build_memory_text(memory):
    lines = []

    profile = memory.get("profile", {})
    likes = memory.get("likes", {})
    projects = memory.get("projects", {})

    if profile.get("name"):
        lines.append(f"- 사용자 이름: {profile.get('name')}")

    if likes.get("favorite_color"):
        lines.append(f"- 좋아하는 색: {likes.get('favorite_color')}")

    if projects.get("main_project"):
        lines.append(f"- 주요 프로젝트: {projects.get('main_project')}")

    for item in memory.get("facts", []):
        lines.append("- " + item.get("content", ""))

    if not lines:
        return "아직 저장된 중요한 기억이 없습니다."

    return "\n".join(lines)


def show_memory(memory):
    print("\n[중요 기억]")
    facts = memory.get("facts", [])

    if not facts:
        print("아직 저장된 일반 기억이 없습니다.")
        return

    for i, item in enumerate(facts, start=1):
        print(f"{i}. {item.get('content', '')}")


def show_profile(memory):
    profile = memory.get("profile", {})
    likes = memory.get("likes", {})
    projects = memory.get("projects", {})

    print("\n[프로필]")

    print("이름:", profile.get("name", "아직 모름"))
    print("좋아하는 색:", likes.get("favorite_color", "아직 모름"))
    print("프로젝트:", projects.get("main_project", "아직 모름"))


def search_memory(memory, keyword):
    keyword = keyword.strip()
    print("\n[검색 결과]")

    if not keyword:
        print("검색어를 입력해줘.")
        return

    found = False

    for item in memory.get("facts", []):
        content = item.get("content", "")

        if keyword.lower() in content.lower():
            print("- " + content)
            found = True

    structured_text = build_memory_text(memory)

    for line in structured_text.splitlines():
        if keyword.lower() in line.lower():
            print(line)
            found = True

    if not found:
        print("검색 결과 없음")


def find_direct_answer(memory, user_input):
    question = user_input.strip()

    profile = memory.get("profile", {})
    likes = memory.get("likes", {})
    projects = memory.get("projects", {})

    if "이름" in question and ("내" in question or "나" in question):
        if profile.get("name"):
            return f"{profile.get('name')}이야."

    if "좋아하는 색" in question or "좋아하는 색깔" in question:
        if likes.get("favorite_color"):
            return f"{likes.get('favorite_color')}이야."

    if "프로젝트" in question or "뭐 만들" in question or "무엇을 만들" in question:
        if projects.get("main_project"):
            return f"{projects.get('main_project')}를 만들고 있어."

    return None


def add_history(memory, role, content):
    if "history" not in memory:
        memory["history"] = []

    memory["history"].append({
        "role": role,
        "content": content,
        "time": datetime.now().isoformat()
    })

    memory["history"] = memory["history"][-10:]
    save_memory(memory)


def build_history_text(memory):
    history = memory.get("history", [])[-6:]

    if not history:
        return "최근 대화 없음"

    lines = []

    for item in history:
        role = item.get("role", "")
        content = item.get("content", "")

        if role == "user":
            lines.append("사용자: " + content)
        elif role == "assistant":
            lines.append("코코: " + content)

    return "\n".join(lines)


def remove_english_noise(text):
    text = re.sub(r"[A-Za-z]{3,}", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def show_today():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"코코: 오늘 날짜는 {today}야.")


def show_now_time():
    now = datetime.now().strftime("%H:%M:%S")
    print(f"코코: 지금 시간은 {now}야.")


def show_system_info():
    print("\n[시스템 정보]")
    print("운영체제:", platform.system())
    print("운영체제 버전:", platform.version())
    print("파이썬 버전:", sys.version.split()[0])
    print("현재 폴더:", os.getcwd())


def show_project_status(memory):
    print("\n[프로젝트 상태]")
    print("코코 AI 버전:", COCO_VERSION)
    print("모델:", MODEL)
    print("일반 기억:", len(memory.get("facts", [])), "개")
    print("최근 대화:", len(memory.get("history", [])), "개")
    print("프로필 이름:", memory.get("profile", {}).get("name", "아직 모름"))
    print("좋아하는 색:", memory.get("likes", {}).get("favorite_color", "아직 모름"))
    print("프로젝트:", memory.get("projects", {}).get("main_project", "아직 모름"))


def ask_coco(memory, user_input):
    memory_text = build_memory_text(memory)
    history_text = build_history_text(memory)

    system_prompt = f"""
너는 사용자의 개인 AI 비서 코코 AI다.
반드시 한국어로만 대답한다.
영어 단어, 영어 문장, 로마자 발음을 섞지 않는다.
사용자는 초보자일 수 있으니 쉽고 짧게 답한다.

규칙:
- 기억에 있는 내용은 기억을 기준으로 답한다.
- 기억에 없는 내용은 모른다고 말한다.
- 답변은 3문장 이내로 한다.
- 이상한 외국어를 절대 섞지 않는다.

중요 기억:
{memory_text}

최근 대화:
{history_text}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        options={
            "temperature": 0.2
        }
    )

    answer = response["message"]["content"]
    answer = remove_english_noise(answer)

    if not answer:
        answer = "미안해. 다시 한국어로 답해볼게."

    return answer


def main():
    memory = load_memory()

    print(f"코코 AI {COCO_VERSION} 시작!")
    print(f"모델: {MODEL}")
    print(f"기억: {len(memory.get('facts', []))}개 로드 완료")
    print("명령어: 종료 / 내 프로필 보여줘 / 중요 기억 보여줘 / 중요 기억 개수 / 중요 기억 검색:키워드 / 기억 삭제:키워드")
    print("추가 명령어: 오늘 날짜 / 지금 시간 / 시스템 정보 / 프로젝트 상태")
    print()

    while True:
        user_input = input("나: ").strip()

        if not user_input:
            continue

        log_message("USER", user_input)
        add_history(memory, "user", user_input)

        if user_input in ["종료", "끝", "exit", "quit"]:
            print("코코: 종료할게.")
            log_message("COCO", "종료")
            break

        if user_input in ["오늘 날짜", "날짜", "오늘"]:
            show_today()
            continue

        if user_input in ["지금 시간", "시간", "몇 시야", "몇시야"]:
            show_now_time()
            continue

        if user_input == "시스템 정보":
            show_system_info()
            continue

        if user_input == "프로젝트 상태":
            show_project_status(memory)
            continue

        if user_input == "내 프로필 보여줘":
            show_profile(memory)
            continue

        if user_input == "중요 기억 보여줘":
            show_memory(memory)
            continue

        if user_input == "중요 기억 개수":
            count = len(memory.get("facts", []))
            print(f"코코: 현재 {count}개의 일반 기억이 있어.")
            continue

        if user_input.startswith("중요 기억 검색:"):
            keyword = user_input.replace("중요 기억 검색:", "").strip()
            search_memory(memory, keyword)
            continue

        if user_input.startswith("기억 삭제:"):
            keyword = user_input.replace("기억 삭제:", "").strip()
            count = delete_fact(memory, keyword)
            print(f"코코: {count}개의 기억을 삭제했어.")
            continue

        if should_remember(user_input):
            structured_saved = update_structured_memory(memory, user_input)
            fact_saved = add_fact(memory, user_input)

            if structured_saved or fact_saved:
                print("코코: 중요한 내용으로 기억했어.")
            else:
                print("코코: 이미 기억하고 있는 내용이야.")

        direct_answer = find_direct_answer(memory, user_input)

        if direct_answer:
            print("코코:", direct_answer)
            log_message("COCO", direct_answer)
            add_history(memory, "assistant", direct_answer)
            continue

        try:
            answer = ask_coco(memory, user_input)
            print("코코:", answer)
            log_message("COCO", answer)
            add_history(memory, "assistant", answer)

        except Exception as e:
            print("코코: 오류가 발생했어.")
            print("오류 내용:", e)
            log_message("ERROR", str(e))


if __name__ == "__main__":
    main()