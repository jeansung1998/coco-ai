from datetime import datetime, timedelta


def get_schedules(memory):
    if "schedules" not in memory:
        memory["schedules"] = []

    return memory["schedules"]


def today_text():
    return datetime.now().strftime("%Y-%m-%d")


def tomorrow_text():
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def add_schedule(memory, schedule_text):
    schedules = get_schedules(memory)
    schedule_text = schedule_text.strip()

    if not schedule_text:
        return "추가할 일정 내용을 말해줘."

    date = "미정"
    title = schedule_text

    if schedule_text.startswith("오늘 "):
        date = today_text()
        title = schedule_text.replace("오늘 ", "", 1).strip()

    elif schedule_text.startswith("내일 "):
        date = tomorrow_text()
        title = schedule_text.replace("내일 ", "", 1).strip()

    schedules.append({
        "date": date,
        "title": title,
        "done": False
    })

    return f"일정을 추가했어: [{date}] {title}"


def show_schedules(memory):
    schedules = get_schedules(memory)

    if not schedules:
        return "아직 등록된 일정이 없어."

    lines = ["현재 일정 목록:"]

    for i, item in enumerate(schedules, start=1):
        status = "완료" if item.get("done") else "예정"
        lines.append(f"{i}. [{status}] {item.get('date')} - {item.get('title')}")

    return "\n".join(lines)


def show_schedules_by_date(memory, target_date, label):
    schedules = get_schedules(memory)

    matched = [
        item for item in schedules
        if item.get("date") == target_date
    ]

    if not matched:
        return f"{label} 등록된 일정이 없어."

    lines = [f"{label} 일정:"]

    for i, item in enumerate(matched, start=1):
        status = "완료" if item.get("done") else "예정"
        lines.append(f"{i}. [{status}] {item.get('title')}")

    return "\n".join(lines)


def complete_schedule(memory, keyword):
    schedules = get_schedules(memory)
    keyword = keyword.strip()

    for item in schedules:
        if keyword in item.get("title", ""):
            item["done"] = True
            return f"일정을 완료 처리했어: {item.get('title')}"

    return "완료할 일정을 찾지 못했어."


def delete_schedule(memory, keyword):
    schedules = get_schedules(memory)
    keyword = keyword.strip()

    for item in schedules:
        if keyword in item.get("title", ""):
            removed = item.get("title")
            schedules.remove(item)
            return f"일정을 삭제했어: {removed}"

    return "삭제할 일정을 찾지 못했어."


def handle_schedule_command(user_input, memory):
    text = user_input.strip()

    if text.startswith("일정 추가:"):
        schedule_text = text.replace("일정 추가:", "", 1).strip()
        return add_schedule(memory, schedule_text)

    if text.startswith("일정 완료:"):
        keyword = text.replace("일정 완료:", "", 1).strip()
        return complete_schedule(memory, keyword)

    if text.startswith("일정 삭제:"):
        keyword = text.replace("일정 삭제:", "", 1).strip()
        return delete_schedule(memory, keyword)

    if text in ["일정 보여줘", "일정 목록", "내 일정 보여줘"]:
        return show_schedules(memory)

    if text in ["오늘 일정", "오늘 일정 보여줘"]:
        return show_schedules_by_date(memory, today_text(), "오늘")

    if text in ["내일 일정", "내일 일정 보여줘"]:
        return show_schedules_by_date(memory, tomorrow_text(), "내일")

    return None