import os
import json
from datetime import datetime
import urllib.parse
import urllib.request

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


def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_memory():
    memory = load_json(MEMORY_FILE, default_memory())

    for key, value in default_memory().items():
        if key not in memory:
            memory[key] = value

    memory["history"] = [
        h for h in memory.get("history", [])
        if h.get("user") and h.get("coco")
    ][-20:]

    memory["facts"] = [
        f for f in memory.get("facts", [])
        if f.get("content")
    ]

    save_json(MEMORY_FILE, memory)
    return memory


def save_memory(memory):
    save_json(MEMORY_FILE, memory)


def add_history(memory, user_text, coco_text):
    memory["history"].append({
        "user": user_text,
        "coco": coco_text,
        "time": datetime.now().isoformat()
    })
    memory["history"] = memory["history"][-20:]
    save_memory(memory)


def memory_text(memory):
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
        lines.append(f"- {item.get('content')}")

    lines.append("[최근 대화]")
    if not memory.get("history"):
        lines.append("- 최근 대화 없음")
    else:
        for item in memory.get("history", [])[-5:]:
            lines.append(f"사용자: {item.get('user')}")
            lines.append(f"코코: {item.get('coco')}")

    return "\n".join(lines)


def remember(memory, content):
    content = content.strip()
    if not content:
        return "기억할 내용이 없습니다."

    for item in memory["facts"]:
        if item.get("content") == content:
            return "이미 기억하고 있습니다."

    memory["facts"].append({
        "content": content,
        "time": datetime.now().isoformat()
    })
    save_memory(memory)
    return "기억 완료."


def delete_memory(memory, keyword):
    before = len(memory["facts"])
    memory["facts"] = [
        item for item in memory["facts"]
        if keyword not in item.get("content", "")
    ]
    save_memory(memory)

    deleted = before - len(memory["facts"])
    if deleted == 0:
        return "삭제할 기억을 찾지 못했습니다."
    return f"기억 {deleted}개 삭제 완료."


def search_memory(memory, keyword):
    result = [f"기억 검색 결과: {keyword}"]
    found = False

    for group_name, group in [
        ("프로필", memory.get("profile", {})),
        ("취향", memory.get("likes", {})),
        ("프로젝트", memory.get("projects", {}))
    ]:
        for k, v in group.items():
            if keyword in str(k) or keyword in str(v):
                result.append(f"- {group_name} / {k}: {v}")
                found = True

    for item in memory.get("facts", []):
        content = item.get("content", "")
        if keyword in content:
            result.append(f"- 기억 / {content}")
            found = True

    if not found:
        return "검색 결과가 없습니다."

    return "\n".join(result)


def memory_status(memory):
    return f"""기억 상태:
- 프로필: {len(memory.get('profile', {}))}개
- 취향: {len(memory.get('likes', {}))}개
- 프로젝트: {len(memory.get('projects', {}))}개
- 기억: {len(memory.get('facts', []))}개
- 최근 대화: {len(memory.get('history', []))}개"""


def auto_memory(memory, text):
    if "내 이름은" in text:
        name = text.split("내 이름은", 1)[1].strip()
        memory["profile"]["name"] = name
        save_memory(memory)
        return "이름을 기억했습니다."

    if "내가 좋아하는" in text and "은" in text:
        left, right = text.split("은", 1)
        key = left.replace("내가 좋아하는", "").strip()
        value = right.strip()
        if key and value:
            memory["likes"][key] = value
            save_memory(memory)
            return f"좋아하는 {key}을 기억했습니다."

    return None


def load_notes():
    return load_json(NOTES_FILE, [])


def save_notes(notes):
    save_json(NOTES_FILE, notes)


def add_note(content):
    notes = load_notes()
    notes.append({
        "content": content,
        "time": datetime.now().isoformat()
    })
    save_notes(notes)
    return "메모 저장 완료."


def show_notes():
    notes = load_notes()
    if not notes:
        return "저장된 메모가 없습니다."

    lines = ["저장된 메모 목록:"]
    for i, note in enumerate(notes, start=1):
        lines.append(f"{i}. {note.get('content')}")
    return "\n".join(lines)


def delete_note(number):
    notes = load_notes()
    if number < 1 or number > len(notes):
        return "없는 메모 번호입니다."

    removed = notes.pop(number - 1)
    save_notes(notes)
    return f"메모 삭제 완료: {removed.get('content')}"


def current_files():
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    if not files:
        return "현재 폴더에 파일이 없습니다."
    return "현재 폴더 파일:\n" + "\n".join(f"- {f}" for f in files)


def current_folders():
    folders = [f for f in os.listdir(".") if os.path.isdir(f)]
    if not folders:
        return "현재 폴더에 폴더가 없습니다."
    return "현재 폴더 안의 폴더 목록:\n" + "\n".join(f"- {f}" for f in folders)


def project_files():
    targets = [
        "coco.py",
        "memory.py",
        "logger.py",
        "pc_control.py",
        "memory.json",
        "notes.json"
    ]

    lines = ["프로젝트 파일 상태:"]
    for filename in targets:
        state = "있음" if os.path.exists(filename) else "없음"
        lines.append(f"- {filename}: {state}")
    return "\n".join(lines)


def read_file(filename):
    filename = filename.strip()
    if not os.path.exists(filename):
        return f"{filename} 파일이 없습니다."
    if not os.path.isfile(filename):
        return f"{filename} 은 파일이 아닙니다."

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f"[{filename} 내용]\n\n" + f.read()
    except Exception as e:
        return f"파일 읽기 오류: {e}"


def wiki_search(query):
    try:
        encoded = urllib.parse.quote(query)
        url = (
            "https://ko.wikipedia.org/w/api.php"
            "?action=opensearch"
            f"&search={encoded}"
            "&limit=5"
            "&namespace=0"
            "&format=json"
        )

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8", errors="ignore"))

        titles = data[1]
        links = data[3]

        if not titles:
            return "웹 검색 결과를 찾지 못했습니다."

        lines = [f"웹 검색 결과: {query}"]
        for i, title in enumerate(titles, start=1):
            link = links[i - 1] if i - 1 < len(links) else ""
            lines.append(f"{i}. {title}")
            lines.append(f"   링크: {link}")

        return "\n".join(lines)

    except Exception as e:
        return f"웹 검색 오류: {e}"


def ask_ai(user_input, memory):
    prompt = f"""
너는 사용자의 개인 AI 비서 코코 AI야.
한국어로 쉽고 짧게 대답해.
저장된 기억을 참고해.

{memory_text(memory)}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response["message"]["content"]


def main():
    memory = load_memory()

    memory["projects"]["코코 AI"] = (
        "코코 AI 9.4 Recovery 진행 중. "
        "9.3.1 기억 시스템 복구, pc_control.py 연결, "
        "PC 제어 1단계 준비 완료."
    )
    save_memory(memory)

    print("코코 AI 9.4 Recovery 시작!")
    print(f"모델: {MODEL_NAME}")
    print("coco.py 복구 완료")
    print("PC 제어 연결 완료")
    print()
    print("명령어:")
    print("기억 보여줘 / 기억 상태 / 기억 검색:키워드 / 기억 삭제:키워드 / 기억해:내용")
    print("메모 저장:내용 / 메모 보여줘 / 메모 삭제:번호")
    print("현재 폴더 파일 보여줘 / 폴더 목록 보여줘 / 프로젝트 파일 상태 / 파일 읽기:파일명")
    print("웹 검색:검색어 / 검색:검색어")
    print("메모장 열어줘 / 계산기 열어줘 / 크롬 열어줘 / 탐색기 열어줘")
    print("사이트 열어줘:주소")
    print("종료")
    print()

    while True:
        user_input = input("나: ").strip()

        if not user_input:
            continue

        if user_input in ["종료", "끝", "exit", "quit"]:
            print("코코: 종료합니다.")
            break

        pc_result = handle_pc_command(user_input)
        if pc_result:
            print("코코:", pc_result)
            continue

        if user_input == "기억 보여줘":
            print("코코:", memory_text(memory))
            continue

        if user_input == "기억 상태":
            print("코코:", memory_status(memory))
            continue

        if user_input.startswith("기억 검색:"):
            keyword = user_input.replace("기억 검색:", "", 1).strip()
            print("코코:", search_memory(memory, keyword))
            continue

        if user_input.startswith("기억 삭제:"):
            keyword = user_input.replace("기억 삭제:", "", 1).strip()
            print("코코:", delete_memory(memory, keyword))
            continue

        if user_input.startswith("기억해:"):
            content = user_input.replace("기억해:", "", 1).strip()
            print("코코:", remember(memory, content))
            continue

        if user_input.startswith("메모 저장:"):
            content = user_input.replace("메모 저장:", "", 1).strip()
            print("코코:", add_note(content))
            continue

        if user_input == "메모 보여줘":
            print("코코:", show_notes())
            continue

        if user_input.startswith("메모 삭제:"):
            number_text = user_input.replace("메모 삭제:", "", 1).strip()
            try:
                print("코코:", delete_note(int(number_text)))
            except:
                print("코코: 메모 번호를 숫자로 입력해 주세요.")
            continue

        if user_input == "현재 폴더 파일 보여줘":
            print("코코:", current_files())
            continue

        if user_input == "폴더 목록 보여줘":
            print("코코:", current_folders())
            continue

        if user_input == "프로젝트 파일 상태":
            print("코코:", project_files())
            continue

        if user_input.startswith("파일 읽기:"):
            filename = user_input.replace("파일 읽기:", "", 1).strip()
            print("코코:", read_file(filename))
            continue

        if user_input.startswith("웹 검색:"):
            query = user_input.replace("웹 검색:", "", 1).strip()
            print("코코:", wiki_search(query))
            continue

        if user_input.startswith("검색:"):
            query = user_input.replace("검색:", "", 1).strip()
            print("코코:", wiki_search(query))
            continue

        memory_message = auto_memory(memory, user_input)

        try:
            answer = ask_ai(user_input, memory)
            if memory_message:
                answer = memory_message + "\n" + answer

            print("코코:", answer)
            add_history(memory, user_input, answer)
            log(f"USER: {user_input}")
            log(f"COCO: {answer}")

        except Exception as e:
            print("코코: 오류가 발생했습니다.")
            print(e)


if __name__ == "__main__":
    main()