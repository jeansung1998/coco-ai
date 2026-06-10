import ollama
import json
from datetime import datetime

from memory import load_memory, save_memory, add_fact, delete_fact, update_fact
from logger import save_log


def remember(memory, user_input):
    text = user_input.strip()

    if text.startswith("내 이름을") and text.endswith("으로 수정"):
        new_name = text.replace("내 이름을", "").replace("으로 수정", "").strip()
        old_name = memory["profile"].get("name", "아직 모름")
        memory["profile"]["name"] = new_name
        return f"이름을 수정했습니다. ({old_name} → {new_name})"

    if text.startswith("내가 좋아하는 색을") and text.endswith("으로 수정"):
        new_color = text.replace("내가 좋아하는 색을", "").replace("으로 수정", "").strip()
        old_color = memory["likes"].get("color", "아직 모름")
        memory["likes"]["color"] = new_color
        return f"좋아하는 색을 수정했습니다. ({old_color} → {new_color})"

    if text.startswith("내가 좋아하는 음식을") and text.endswith("으로 수정"):
        new_food = text.replace("내가 좋아하는 음식을", "").replace("으로 수정", "").strip()
        old_food = memory["likes"].get("food", "아직 모름")
        memory["likes"]["food"] = new_food
        return f"좋아하는 음식을 수정했습니다. ({old_food} → {new_food})"

    if text.startswith("내 프로젝트를") and text.endswith("으로 수정"):
        new_project = text.replace("내 프로젝트를", "").replace("으로 수정", "").strip()
        old_project = memory["projects"].get("main", "아직 모름")
        memory["projects"]["main"] = new_project
        return f"프로젝트를 수정했습니다. ({old_project} → {new_project})"

    if "을" in text and "으로 수정" in text:
        old_keyword = text.split("을")[0].strip()
        new_content = text.split("을", 1)[1].replace("으로 수정", "").strip()

        old_content = update_fact(memory, old_keyword, new_content)

        if old_content:
            return f"기억을 수정했습니다. ({old_content} → {new_content})"
        else:
            return f"수정할 기억을 찾지 못했습니다. ({old_keyword})"

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

    if text.endswith("삭제"):
        keyword = text.replace("삭제", "").strip()

        if delete_fact(memory, keyword):
            return f"기억을 삭제했습니다. ({keyword})"
        else:
            return f"해당 기억을 찾지 못했습니다. ({keyword})"

    if text.startswith("기억해"):
        fact = text.replace("기억해", "").strip()

        if add_fact(memory, fact):
            return f"기억했습니다. ({fact})"
        else:
            return f"이미 기억하고 있습니다. ({fact})"

    auto_patterns = [
        "나는 ",
        "내 취미는 ",
        "내 목표는 ",
        "내 꿈은 ",
        "나는 지금 ",
        "나는 앞으로 "
    ]

    for pattern in auto_patterns:
        if text.startswith(pattern):
            if add_fact(memory, text):
                return f"자동 기억했습니다. ({text})"
            else:
                return f"이미 기억하고 있습니다. ({text})"

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
        lines = []

        lines.append("[프로필]")
        lines.append(f"- 이름: {memory['profile'].get('name', '아직 모름')}")

        lines.append("")
        lines.append("[좋아하는 것]")
        lines.append(f"- 음식: {memory['likes'].get('food', '아직 모름')}")
        lines.append(f"- 색: {memory['likes'].get('color', '아직 모름')}")

        lines.append("")
        lines.append("[프로젝트]")
        lines.append(f"- 메인 프로젝트: {memory['projects'].get('main', '아직 모름')}")

        lines.append("")
        lines.append("[기타 기억]")

        facts = memory.get("facts", [])

        if facts:
            for item in facts:
                lines.append(f"- {item['content']}")
        else:
            lines.append("- 아직 없음")

        return "\n".join(lines)

    return None


def ask_coco(memory, user_input):
    prompt = f"""
너의 이름은 코코 AI다.
너는 사용자의 개인 AI 비서다.
항상 한국어로 대답한다.
사용자의 기억을 참고한다.

사용자 기억:
{json.dumps(memory, ensure_ascii=False, indent=2)}

사용자 질문:
{user_input}
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


def main():
    memory = load_memory()

    print("코코 AI 7.9 시작!")
    print("모델: llama3.2")
    print(f"기억: {len(memory.get('facts', []))}개 로드 완료")
    print("로그: 연결 완료")
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
            save_log(user_input, remembered)
            continue

        recalled = recall(memory, user_input)

        if recalled:
            print("코코:", recalled)
            save_log(user_input, recalled)
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
        save_log(user_input, answer)

        print("코코:", answer)


if __name__ == "__main__":
    main()