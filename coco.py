import os
import json
from datetime import datetime

PROJECT_HISTORY_FILE = "project_history.json"
PROJECT_GOAL_FILE = "project_goals.json"

import urllib.parse
import urllib.request

import ollama
from pc_control import handle_pc_command
from voice import listen, speak, is_exit_command

from assistant_engine import personal_assistant_reply
from goal_engine import handle_goal_command
from schedule_engine import handle_schedule_command
from coach_engine import handle_coach_command
from memory_summary_engine import handle_memory_summary_command
from dashboard_engine import handle_dashboard_command
from startup_assistant import build_startup_message
from morning_briefing import build_morning_briefing
from conversation_engine import natural_conversation
from emotion_engine import handle_emotion
from relationship_engine import handle_relationship_command
from project_manager import handle_project_command
from voice_filter import clean_for_voice
from voice_message_engine import (
    startup_voice_message,
    briefing_voice_message
)

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
        "habits": {},
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

def integrated_memory_search(keyword):
    memory = load_memory()
    results = []

    for group_name, group in [
        ("프로필", memory.get("profile", {})),
        ("취향", memory.get("likes", {})),
        ("프로젝트", memory.get("projects", {}))
    ]:
        for k, v in group.items():
            if keyword in str(k) or keyword in str(v):
                results.append(
                    f"[{group_name}] {k}: {v}"
                )

    for item in memory.get("facts", []):
        content = item.get("content", "")
        if keyword in content:
            results.append(
                f"[기억] {content}"
            )

    for item in memory.get("history", []):
        user_text = item.get("user", "")
        coco_text = item.get("coco", "")

        if (
            keyword in user_text
            or keyword in coco_text
        ):
            results.append(
                f"[대화] 나:{user_text}"
            )

    return results

def search_chat_history_file(keyword):
    try:
        if not os.path.exists("chat_history.json"):
            return []

        with open(
            "chat_history.json",
            "r",
            encoding="utf-8"
        ) as f:
            history = json.load(f)

        results = []

        for item in history:
            message = str(
                item.get(
                    "message",
                    ""
                )
            )

            if keyword in message:
                results.append(message)

        return results[-10:]

    except Exception:
        return []

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

    lines.append("[습관]")
    for k, v in memory.get("habits", {}).items():
        lines.append(f"- {k}: {v}")    

    lines.append("[기억]")
    for item in memory.get("facts", [])[-5:]:
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

        split_words = [
            " 그리고 ",
            " 그리고",
            " 주말",
            " 퇴근",
            " 하지만",
            " 근데"
            " 이야"
        ]

        for word in split_words:
            if word in value:
                value = value.split(word, 1)[0].strip()

        if value.endswith("?"):
            return None

        if value.endswith("이야"):
            value = value[:-2].strip()

        if value.endswith("야"):
            value = value[:-1].strip()        

        if key and value:
            memory["likes"][key] = value
            save_memory(memory)
            return f"좋아하는 {key}을 기억했습니다."

    if "주말" in text:
        activity = text.replace("주말에는", "").replace("주말에", "").replace("주말은", "").strip()

        if activity:
            memory["habits"]["주말"] = activity
            save_memory(memory)
            return "주말 습관을 기억했습니다."

    if "퇴근 후" in text or "퇴근후" in text:
        activity = text.replace("퇴근 후에는", "").replace("퇴근 후", "").replace("퇴근후에는", "").replace("퇴근후", "").strip()

        if activity:
            memory["habits"]["퇴근후"] = activity
            save_memory(memory)
            return "퇴근 후 습관을 기억했습니다."
    if "자주" in text:
        activity = text.strip()

        if activity:
            count = 1

            while f"자주하는것_{count}" in memory["habits"]:
                count += 1

            memory["habits"][f"자주하는것_{count}"] = activity

            save_memory(memory)
            return "자주 하는 행동을 기억했습니다."

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
        "voice.py",
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


def process_command(user_input, memory, voice_mode=False):
    user_input = user_input.strip()
    compact_input = user_input.replace(" ", "")

    # 10.46 빠른 응답: 간단한 말은 AI 모델 호출 없이 바로 처리
    if compact_input in ["안녕", "안녕하세요", "하이", "ㅎㅇ"]:
        return "안녕! 나는 코코 AI야. 바로 대답할게."

    if "좋아하는음식" in compact_input and "뭐" in compact_input:
        food = memory.get("likes", {}).get("음식")
        if food:
            return f"네가 좋아하는 음식은 {food}야."
        return "아직 좋아하는 음식을 기억하지 못했어."

    if user_input.startswith("통합 검색:"):
        try:
            keyword = user_input.replace("통합 검색:", "").strip()

            if not keyword:
                return "검색어를 입력해줘."

            memory_results = integrated_memory_search(keyword)
            chat_results = search_chat_history_file(keyword)

            return (
                "[통합 검색 결과]\n\n"
                + "=== 기억 검색 결과 ===\n"
                + ("\n".join(memory_results[-10:]) if memory_results else "기억 검색 결과가 없습니다.")
                + "\n\n=== 대화 검색 결과 ===\n"
                + (
                    "\n".join(chat_results)
                    if chat_results
                    else "대화 검색 결과가 없습니다."
                )
            )    
            
        except Exception as e:
            return f"통합 검색 오류: {e}"

    pc_aliases = {

        # 유튜브
        "유튜브열어줘": "유튜브 열어줘",
        "유튜브켜줘": "유튜브 열어줘",
        "유튜브실행해줘": "유튜브 열어줘",
        "유튜브실행": "유튜브 열어줘",
        "유튜브틀어줘": "유튜브 열어줘",
        "유튜브열기": "유튜브 열어줘",

        # 네이버
        "네이버열어줘": "네이버 열어줘",
        "네이버켜줘": "네이버 열어줘",
        "네이버실행": "네이버 열어줘",
        "네이버실행해줘": "네이버 열어줘",

        # 구글
        "구글열어줘": "구글 열어줘",
        "구글켜줘": "구글 열어줘",
        "구글실행": "구글 열어줘",

        # 계산기
        "계산기열어줘": "계산기 열어줘",
        "계산기켜줘": "계산기 열어줘",
        "계산기실행": "계산기 열어줘",

        # 크롬
        "크롬열어줘": "크롬 열어줘",
        "크롬켜줘": "크롬 열어줘",
        "크롬실행": "크롬 열어줘",
    }

    if compact_input in pc_aliases:
        user_input = pc_aliases[compact_input]
    # 자연어 명령 처리

    # 자연어 명령 처리

    text = compact_input

    # 유튜브
    if "유튜브" in text:
        youtube_words = [
            "열",
            "켜",
            "실행",
            "틀",
            "보고싶",
            "보고싶어",
            "보여줘"
        ]

        if any(word in text for word in youtube_words):
            user_input = "유튜브 열어줘"

    # 네이버
    if "네이버" in text:
        naver_words = [
            "열",
            "켜",
            "실행",
            "검색"
        ]

        if any(word in text for word in naver_words):
            user_input = "네이버 열어줘"

    # 계산기
    if "계산기" in text or "계산" in text:
        calc_words = [
            "열",
            "켜",
            "실행",
            "쓰",
            "사용",
            "하고싶",
            "싶어",
            "싶다",
            "해보고싶"
        ]

        if any(word in text for word in calc_words) or text in ["계산기", "계산"]:
            return handle_pc_command("계산기 열어줘")

    pc_result = handle_pc_command(user_input)
    if pc_result:
        return pc_result

    if user_input == "기억 보여줘":
        return memory_text(memory)

    if user_input == "기억 상태":
        return memory_status(memory)

    if user_input.startswith("기억 검색:"):
        keyword = user_input.replace("기억 검색:", "", 1).strip()
        return search_memory(memory, keyword)

    if user_input.startswith("기억 삭제:"):
        keyword = user_input.replace("기억 삭제:", "", 1).strip()
        return delete_memory(memory, keyword)

    if user_input.startswith("기억해:"):
        content = user_input.replace("기억해:", "", 1).strip()
        return remember(memory, content)

    if user_input.startswith("메모 저장:"):
        content = user_input.replace("메모 저장:", "", 1).strip()
        return add_note(content)

    if user_input == "메모 보여줘":
        return show_notes()

    if user_input.startswith("메모 삭제:"):
        number_text = user_input.replace("메모 삭제:", "", 1).strip()
        try:
            return delete_note(int(number_text))
        except:
            return "메모 번호를 숫자로 입력해 주세요."

    if user_input == "현재 폴더 파일 보여줘":
        return current_files()

    if user_input == "폴더 목록 보여줘":
        return current_folders()

    if user_input == "프로젝트 파일 상태":
        return project_files()

    if user_input.startswith("파일 읽기:"):
        filename = user_input.replace("파일 읽기:", "", 1).strip()
        return read_file(filename)

    if user_input.startswith("웹 검색:"):
        query = user_input.replace("웹 검색:", "", 1).strip()
        return wiki_search(query)

    if user_input.startswith("검색:"):
        query = user_input.replace("검색:", "", 1).strip()
        return wiki_search(query)

    memory_message = auto_memory(memory, user_input)

    try:

        if "오늘 뭐 할까" in user_input:
            habits = memory.get("habits", {})

            if "주말" in habits:
                return f"주말에는 {habits['주말']}.\n오늘도 해볼래?"

            if "퇴근후" in habits:
                return f"퇴근 후에는 {habits['퇴근후']}.\n오늘도 해볼래?"
            
        if "내 습관이 뭐야" in user_input:
            habits = memory.get("habits", {})

            if not habits:
                return "아직 기억된 습관이 없어."

            result = "내가 기억하는 습관은:\n"

            for key, value in habits.items():
                result += f"- {key}: {value}\n"

            return result 

        if "내가 뭘 좋아하지" in user_input:
            likes = memory.get("likes", {})

            if not likes:
                return "아직 기억된 취향이 없어."

            result = "내가 기억하는 취향은:\n"

            for key, value in likes.items():
                result += f"- {key}: {value}\n"

            return result   
        
        if "나는 어떤 사람이야" in user_input:
            result = "내가 기억하기로는:\n\n"

            likes = memory.get("likes", {})
            habits = memory.get("habits", {})

            if likes:
                result += "[취향]\n"
                for key, value in likes.items():
                    result += f"- {key}: {value}\n"

            if habits:
                result += "\n[습관]\n"
                for key, value in habits.items():
                    result += f"- {key}: {value}\n"

            return result
        
        if "오늘 뭐 먹을까" in user_input:
            likes = memory.get("likes", {})

            if "음식" in likes:
                return f"{likes['음식']}을 좋아하니까 {likes['음식']} 어때?"

            return "아직 좋아하는 음식을 기억하지 못했어."
        
        if "심심해" in user_input or "뭐 하지" in user_input or "할 거 추천" in user_input:
            habits = memory.get("habits", {})

            if "주말" in habits:
                return f"주말에는 {habits['주말']}.\n지금도 그거 해보는 건 어때?"

            if "퇴근후" in habits:
                return f"퇴근 후에는 {habits['퇴근후']}.\n지금도 해볼래?"

            return "아직 추천할 만한 습관 기억이 없어."
        
        answer = ask_ai(user_input, memory)

        if memory_message:
            answer = memory_message + "\n" + answer

        add_history(memory, user_input, answer)
        log(f"USER: {user_input}")
        log(f"COCO: {answer}")

        return answer

    except Exception as e:
        return f"오류가 발생했습니다: {e}"


def voice_once(memory):
    speak("말해 주세요.")
    user_input = listen()

    if not user_input:
        answer = "말을 인식하지 못했습니다."
        print("코코:", answer)
        speak(clean_for_voice(answer))
        return

    print("나:", user_input)

    if user_input in ["종료", "끝", "그만", "멈춰"]:
        answer = "음성 모드를 종료합니다."
        print("코코:", answer)
        speak(clean_for_voice(answer))
        return

    answer = process_command(user_input, memory, voice_mode=True)
    print("코코:", answer)
    speak(clean_for_voice(answer))


def voice_loop(memory):
    speak("음성 대화 모드를 시작합니다. 종료하려면 그만이라고 말하세요.")

    fail_count = 0

    while True:
        user_input = listen()

        if not user_input:
            fail_count += 1

            print(f"코코: 잘 못 들었습니다. ({fail_count}/3)")

            if fail_count >= 3:
                answer = "음성 대화를 종료합니다."
                print("코코:", answer)
                speak(clean_for_voice(answer))
                break

            continue

        fail_count = 0

        print("나:", user_input)
        
        if user_input in ["코코야", "코코", "야코코", "야 코코"]:
            answer = "네, 부르셨나요?"
            print("코코:", answer)
            speak(clean_for_voice(answer))

            user_input = listen()

            if not user_input:
                continue

            print("나:", user_input)

        if is_exit_command(user_input):
            answer = "음성 대화 모드를 종료합니다."
            print("코코:", answer)
            speak(clean_for_voice(answer))
            break

        answer = process_command(
            user_input,
            memory,
            voice_mode=True
        )

        print("코코:", answer)
        speak(clean_for_voice(answer))

def load_project_history():
    if not os.path.exists(PROJECT_HISTORY_FILE):
        return {
            "project_name": "코코 AI",
            "current_version": "10.26",
            "history": []
        }

    with open(PROJECT_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project_history(history):
    with open(PROJECT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_project_history(version, title, content):
    history = load_project_history()

    item = {
        "version": version,
        "title": title,
        "content": content,
        "time": datetime.now().isoformat()
    }

    history["current_version"] = version
    history["history"].append(item)

    save_project_history(history)

    return f"{version} 프로젝트 기록 저장 완료"


def show_project_history():
    history = load_project_history()

    if not history["history"]:
        return "프로젝트 기록이 없습니다."

    lines = ["[코코 AI 프로젝트 히스토리]"]

    for item in history["history"][-10:]:
        lines.append(
            f"- {item['version']} | {item['title']} | {item['content']}"
        )

    return "\n".join(lines)


def search_project_history(keyword):
    history = load_project_history()

    results = []

    for item in history["history"]:
        text = (
            item.get("version", "")
            + item.get("title", "")
            + item.get("content", "")
        )

        if keyword in text:
            results.append(item)

    if not results:
        return f"'{keyword}' 관련 기록이 없습니다."

    lines = [f"[{keyword} 검색 결과]"]

    for item in results:
        lines.append(
            f"- {item['version']} | {item['title']} | {item['content']}"
        )

    return "\n".join(lines)

def build_project_review():
    history = load_project_history()

    items = history.get("history", [])

    if not items:
        return "아직 프로젝트 기록이 없어."

    lines = []

    lines.append("[오늘 개발 회고]")
    lines.append("")

    lines.append("최근 작업:")

    for item in items[-5:]:
        lines.append(
            f"- {item.get('title')} | {item.get('content')}"
        )

    lines.append("")
    lines.append(f"총 기록 수: {len(items)}개")
    lines.append(
        f"현재 버전: {history.get('current_version', '알 수 없음')}"
    )

    lines.append("")
    lines.append("다음 추천:")
    lines.append("- 앱 출시 준비")

    return "\n".join(lines)

def build_project_stats(memory):
    history = load_project_history()
    project_items = history.get("history", [])

    facts_count = len(memory.get("facts", []))
    likes_count = len(memory.get("likes", {}))
    habits_count = len(memory.get("habits", {}))
    projects_count = len(memory.get("projects", {}))
    relations_count = len(memory.get("relations", {}))

    latest_title = "없음"
    if project_items:
        latest_title = project_items[-1].get("title", "없음")

    lines = []
    lines.append("[코코 AI 개발 현황]")
    lines.append("")
    lines.append("프로젝트명: 코코 AI")
    lines.append(f"현재 버전: {history.get('current_version', '알 수 없음')}")
    lines.append(f"프로젝트 기록 수: {len(project_items)}개")
    lines.append("")
    lines.append("[기억 데이터]")
    lines.append(f"- 기억 수: {facts_count}개")
    lines.append(f"- 취향 수: {likes_count}개")
    lines.append(f"- 습관 수: {habits_count}개")
    lines.append(f"- 프로젝트 수: {projects_count}개")
    lines.append(f"- 관계 수: {relations_count}개")
    lines.append("")
    lines.append(f"최근 업데이트: {latest_title}")

    return "\n".join(lines)

def load_project_goals():
    if not os.path.exists(PROJECT_GOAL_FILE):
        return {
            "current_goal": "",
            "completed": []
        }

    with open(PROJECT_GOAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project_goals(data):
    with open(PROJECT_GOAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def set_project_goal(goal):
    data = load_project_goals()

    data["current_goal"] = goal

    save_project_goals(data)

    return f"프로젝트 목표 저장 완료: {goal}"


def get_project_goal():
    data = load_project_goals()

    goal = data.get("current_goal", "")

    if not goal:
        return "현재 설정된 목표가 없어."

    return f"현재 목표는 {goal} 이야."


def complete_project_goal():
    data = load_project_goals()

    goal = data.get("current_goal", "")

    if not goal:
        return "완료할 목표가 없어."

    data["completed"].append(goal)
    data["current_goal"] = ""

    save_project_goals(data)

    return f"목표 완료 처리: {goal}"


def show_completed_goals():
    data = load_project_goals()

    completed = data.get("completed", [])

    if not completed:
        return "완료된 목표가 없어."

    lines = ["[완료된 목표]"]

    for item in completed:
        lines.append(f"- {item}")

    return "\n".join(lines)

def build_growth_report(memory):
    history = load_project_history()
    goals = load_project_goals()

    project_items = history.get("history", [])
    current_goal = goals.get("current_goal", "")
    completed_goals = goals.get("completed", [])

    facts_count = len(memory.get("facts", []))
    likes_count = len(memory.get("likes", {}))
    habits_count = len(memory.get("habits", {}))
    projects_count = len(memory.get("projects", {}))
    relations_count = len(memory.get("relations", {}))

    latest_update = "없음"
    if project_items:
        latest_update = project_items[-1].get("title", "없음")

    lines = []
    lines.append("[코코 성장 보고서]")
    lines.append("")
    lines.append("[기억 성장]")
    lines.append(f"- 기억: {facts_count}개")
    lines.append(f"- 취향: {likes_count}개")
    lines.append(f"- 습관: {habits_count}개")
    lines.append(f"- 프로젝트: {projects_count}개")
    lines.append(f"- 관계: {relations_count}개")
    lines.append("")
    lines.append("[프로젝트 성장]")
    lines.append(f"- 프로젝트 기록: {len(project_items)}개")
    lines.append(f"- 최근 발전: {latest_update}")
    lines.append("")
    lines.append("[목표 상태]")

    if current_goal:
        lines.append(f"- 현재 목표: {current_goal}")
    else:
        lines.append("- 현재 목표: 없음")

    lines.append(f"- 완료한 목표: {len(completed_goals)}개")
    lines.append("")
    lines.append("[다음 추천]")
    lines.append("- 모바일 앱 UI 제작")
    lines.append("- 앱 출시 준비 단계 정리")

    return "\n".join(lines)

def build_growth_level_report(memory):
    history = load_project_history()
    goals = load_project_goals()

    facts_count = len(memory.get("facts", []))
    likes_count = len(memory.get("likes", {}))
    habits_count = len(memory.get("habits", {}))
    relations_count = len(memory.get("relations", {}))

    project_count = len(history.get("history", []))
    completed_count = len(goals.get("completed", []))

    score = (
        facts_count
        + likes_count
        + habits_count
        + relations_count
        + project_count
        + completed_count
    )

    if score >= 100:
        level = "앱 출시 단계"
    elif score >= 50:
        level = "고급 개발 AI"
    elif score >= 20:
        level = "중급 개발 AI"
    else:
        level = "초급 개발 AI"

    lines = []
    lines.append("[코코 성장 추세]")
    lines.append("")
    lines.append(f"기억: {facts_count}개")
    lines.append(f"취향: {likes_count}개")
    lines.append(f"습관: {habits_count}개")
    lines.append(f"관계: {relations_count}개")
    lines.append("")
    lines.append(f"프로젝트 기록: {project_count}개")
    lines.append(f"완료 목표: {completed_count}개")
    lines.append("")
    lines.append(f"성장 등급: {level}")
    lines.append("")
    lines.append("다음 단계:")
    lines.append("- 앱 UI 제작")
    lines.append("- 모바일 버전 준비")

    return "\n".join(lines)

def build_app_launch_checklist():
    lines = []

    lines.append("[앱 출시 준비 체크리스트]")
    lines.append("")
    lines.append("1. 핵심 기능 정리")
    lines.append("2. 앱 UI 화면 설계")
    lines.append("3. 실행 파일 만들기")
    lines.append("4. 설치 파일 만들기")
    lines.append("5. 테스트 버전 배포")
    lines.append("6. 오류 로그 수집")
    lines.append("7. 개인정보/보안 점검")
    lines.append("8. GitHub 릴리즈 정리")
    lines.append("")
    lines.append("추천 다음 작업:")
    lines.append("- 먼저 앱 UI 화면 설계부터 시작")

    return "\n".join(lines)

def coco_reply(user_input, memory=None, voice=False):
    if memory is None:
        memory = load_memory()

    user_input = user_input.strip()

    simple_text = user_input.replace("코코", "").strip()

    if simple_text in ["안녕", "안녕하세요", "하이"]:
        return "안녕하세요. 반가워요."

    if not user_input:
        return ""

    if "오늘 개발 정리해줘" in user_input:
        answer = build_project_review()
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if "코코 AI 개발 현황 보여줘" in user_input or "프로젝트 통계 보여줘" in user_input:
        answer = build_project_stats(memory)
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if user_input.startswith("프로젝트 목표"):
        goal = user_input.replace("프로젝트 목표", "").strip()
        if goal:
            answer = set_project_goal(goal)
        else:
            answer = "목표 내용을 말해줘."
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if "현재 목표 뭐야" in user_input:
        answer = get_project_goal()
        if voice:
            speak(clean_for_voice(answer))
        return answer
    
    if "코코 상태 보여줘" in user_input:
        try:
            import json
            import os

            chat_count = 0

            if os.path.exists("chat_history.json"):
                with open(
                    "chat_history.json",
                    "r",
                    encoding="utf-8"
                ) as f:
                    chat_count = len(json.load(f))

            memory_count = len(memory.get("facts", []))

            project_count = len(
                memory.get("projects", {})
            )

            answer = (
                "코코 AI 상태\n\n"
                "버전: 10.42\n"
                f"대화 기록 수: {chat_count}\n"
                f"기억 수: {memory_count}\n"
                f"프로젝트 수: {project_count}"
            )

            return answer

        except Exception as e:
            return f"상태 확인 오류: {e}"
        
    if user_input.startswith("대화 검색:"):
        try:
            import json
            import os

            keyword = (
                user_input
                .replace("대화 검색:", "")
                .strip()
            )

            if not keyword:
                return "검색어를 입력해줘."

            if not os.path.exists(
                "chat_history.json"
            ):
                return "대화 기록이 없습니다."

            with open(
                "chat_history.json",
                "r",
                encoding="utf-8"
            ) as f:
                history = json.load(f)

            results = []

            for item in history:
                message = item.get(
                    "message",
                    ""
                )

                if message.startswith("대화 검색:"):
                    continue

                if "[대화 검색 결과]" in message:
                    continue

                if keyword in message:
                    results.append(
                        f"{item.get('time')}\n"
                        f"{item.get('sender')}: "
                        f"{message}"
                    )

            if not results:
                return (
                    f"'{keyword}' "
                    "검색 결과가 없습니다."
                )

            return (
                "[대화 검색 결과]\n\n"
                + "\n\n".join(results[-10:])
            )

        except Exception as e:
            return f"검색 오류: {e}" 

    if "목표 완료" in user_input:
        answer = complete_project_goal()
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if "완료된 목표 보여줘" in user_input:
        answer = show_completed_goals()
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if "코코 성장 보고서 보여줘" in user_input or "성장 리포트 보여줘" in user_input:
        answer = build_growth_report(memory)
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if "코코 얼마나 성장했어" in user_input or "성장 추세 보여줘" in user_input:
        answer = build_growth_level_report(memory)
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if "앱 출시 준비 보여줘" in user_input or "출시 체크리스트 보여줘" in user_input:
        answer = build_app_launch_checklist()
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if "프로젝트 히스토리 보여줘" in user_input or "개발 기록 보여줘" in user_input:
        answer = show_project_history()
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if user_input.startswith("프로젝트 기록"):
        content = user_input.replace("프로젝트 기록", "").strip()
        if content:
            answer = add_project_history("10.35", "GUI 연결", content)
        else:
            answer = "기록할 내용을 말해줘."
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if user_input.startswith("프로젝트 검색"):
        keyword = user_input.replace("프로젝트 검색", "").strip()
        if keyword:
            answer = search_project_history(keyword)
        else:
            answer = "검색할 단어를 말해줘."
        if voice:
            speak(clean_for_voice(answer))
        return answer

    if user_input in ["종료", "끝", "exit", "quit"]:
        return "종료할게요."

    assistant_answer = personal_assistant_reply(user_input, memory)
    if assistant_answer:
        if voice:
            speak(clean_for_voice(assistant_answer))
        return assistant_answer

    goal_answer = handle_goal_command(user_input, memory)
    if goal_answer:
        save_memory(memory)
        if voice:
            speak(goal_answer)
        return goal_answer

    schedule_answer = handle_schedule_command(user_input, memory)
    if schedule_answer:
        save_memory(memory)
        if voice:
            speak(schedule_answer)
        return schedule_answer

    coach_answer = handle_coach_command(user_input, memory)
    if coach_answer:
        if voice:
            speak(coach_answer)
        return coach_answer

    summary_answer = handle_memory_summary_command(user_input, memory)
    if summary_answer:
        if voice:
            speak(summary_answer)
        return summary_answer

    dashboard_answer = handle_dashboard_command(user_input, memory)
    if dashboard_answer:
        if voice:
            speak(dashboard_answer)
        return dashboard_answer

    conversation_answer = natural_conversation(user_input, memory)
    if conversation_answer:
        if voice:
            speak(conversation_answer)
        return conversation_answer

    emotion_answer = handle_emotion(user_input, memory)
    if emotion_answer:
        if voice:
            speak(emotion_answer)
        return emotion_answer

    relationship_answer = handle_relationship_command(user_input, memory)
    if relationship_answer:
        save_memory(memory)
        if voice:
            speak(relationship_answer)
        return relationship_answer

    project_answer = handle_project_command(user_input, memory)
    if project_answer:
        if voice:
            speak(project_answer)
        return project_answer

    answer = process_command(user_input, memory)
    return answer

def main():
    memory = load_memory()

    memory["projects"]["코코 AI"] = (
        "코코 AI 9.5.3 진행 중. "
        "음성 입력과 음성 출력 연결 완료, "
        "텍스트 명령과 음성 명령을 함께 처리 가능."
    )
    save_memory(memory)

    startup_message = build_startup_message(memory)

    print()
    print(startup_message)
    print()

    speak(startup_voice_message(memory))

    briefing = build_morning_briefing(memory)

    print()
    print(briefing)
    print()

    speak(briefing_voice_message(memory))

    print("코코 AI 10.0 시작!")
    print(f"모델: {MODEL_NAME}")
    print("음성 입력/출력 연결 완료")
    print()
    print("명령어:")
    print("음성 모드 / 음성 대화")
    print("기억 보여줘 / 기억 상태 / 기억 검색:키워드 / 기억 삭제:키워드 / 기억해:내용")
    print("메모 저장:내용 / 메모 보여줘 / 메모 삭제:번호")
    print("현재 폴더 파일 보여줘 / 폴더 목록 보여줘 / 프로젝트 파일 상태 / 파일 읽기:파일명")
    print("웹 검색:검색어 / 검색:검색어")
    print("메모장 열어줘 / 계산기 열어줘 / 크롬 열어줘 / 탐색기 열어줘")
    print("네이버 열어줘 / 유튜브 열어줘 / 검색해줘:검색어")
    print("바탕화면 열어줘 / 다운로드 열어줘 / 코코 폴더 열어줘")
    print("종료")
    print()

    while True:
        user_input = input("나: ").strip()

        if not user_input:
            continue

        if "오늘 개발 정리해줘" in user_input:
            answer = build_project_review()

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "코코 AI 개발 현황 보여줘" in user_input or "프로젝트 통계 보여줘" in user_input:
            answer = build_project_stats(memory)

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if user_input.startswith("프로젝트 목표"):
            goal = user_input.replace("프로젝트 목표", "").strip()

            if goal:
                answer = set_project_goal(goal)
            else:
                answer = "목표 내용을 말해줘."

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "현재 목표 뭐야" in user_input:
            answer = get_project_goal()

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "목표 완료" in user_input:
            answer = complete_project_goal()

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "완료된 목표 보여줘" in user_input:
            answer = show_completed_goals()

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "코코 성장 보고서 보여줘" in user_input or "성장 리포트 보여줘" in user_input:
            answer = build_growth_report(memory)

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "코코 얼마나 성장했어" in user_input or "성장 추세 보여줘" in user_input:
            answer = build_growth_level_report(memory)

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "앱 출시 준비 보여줘" in user_input or "출시 체크리스트 보여줘" in user_input:
            answer = build_app_launch_checklist()

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if "프로젝트 히스토리 보여줘" in user_input or "개발 기록 보여줘" in user_input:
            answer = show_project_history()
            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if user_input.startswith("프로젝트 기록"):
            content = user_input.replace("프로젝트 기록", "").strip()

            if content:
                answer = add_project_history(
                    "10.26",
                    "프로젝트 히스토리 기록",
                    content
                )
            else:
                answer = "기록할 내용을 말해줘."

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if user_input.startswith("프로젝트 검색"):
            keyword = user_input.replace("프로젝트 검색", "").strip()

            if keyword:
                answer = search_project_history(keyword)
            else:
                answer = "검색할 단어를 말해줘."

            print("코코:", answer)
            speak(clean_for_voice(answer))
            continue

        if user_input in ["종료", "끝", "exit", "quit"]:
            print("코코: 종료합니다.")
            break

        if user_input == "음성 모드":
            voice_once(memory)
            continue

        if user_input == "음성 대화":
            voice_loop(memory)
            continue

        assistant_answer = personal_assistant_reply(user_input, memory)

        if assistant_answer:
            print("코코:", assistant_answer)
            speak(clean_for_voice(assistant_answer))
            continue

        goal_answer = handle_goal_command(user_input, memory)

        if goal_answer:
            print("코코:", goal_answer)
            save_memory(memory)
            speak(goal_answer)
            continue

        schedule_answer = handle_schedule_command(user_input, memory)

        if schedule_answer:
            print("코코:", schedule_answer)
            save_memory(memory)
            speak(schedule_answer)
            continue

        coach_answer = handle_coach_command(user_input, memory)

        if coach_answer:
            print("코코:", coach_answer)
            speak(coach_answer)
            continue

        summary_answer = handle_memory_summary_command(
            user_input,
            memory
        )

        if summary_answer:
            print("코코:", summary_answer)
            speak(summary_answer)
            continue

        dashboard_answer = handle_dashboard_command(
            user_input,
            memory
        )

        if dashboard_answer:
            print("코코:", dashboard_answer)
            speak(dashboard_answer)
            continue

        conversation_answer = natural_conversation(
            user_input,
            memory
        )

        if conversation_answer:
            print("코코:", conversation_answer)
            speak(conversation_answer)
            continue

        emotion_answer = handle_emotion(
            user_input,
            memory
        )

        if emotion_answer:
            print("코코:", emotion_answer)
            speak(emotion_answer)
            continue

        relationship_answer = handle_relationship_command(
            user_input,
            memory
        )

        if relationship_answer:
            print("코코:", relationship_answer)

            save_memory(memory)

            speak(relationship_answer)
            continue

        project_answer = handle_project_command(
            user_input,
            memory
        )

        if project_answer:
            print("코코:", project_answer)
            speak(project_answer)
            continue

        answer = process_command(user_input, memory)
        print("코코:", answer)

if __name__ == "__main__":
    main()