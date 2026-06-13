def get_active_goals(memory):
    goals = memory.get("goals", [])
    return [g for g in goals if not g.get("done")]


def get_active_schedules(memory):
    schedules = memory.get("schedules", [])
    return [s for s in schedules if not s.get("done")]


def goal_progress(memory):
    goals = memory.get("goals", [])

    if not goals:
        return "아직 등록된 목표가 없어."

    total = len(goals)
    completed = len([g for g in goals if g.get("done")])

    percent = int((completed / total) * 100)

    return (
        f"목표 달성률은 {percent}%야.\n"
        f"전체 {total}개 중 {completed}개 완료했어."
    )


def show_active_goals(memory):
    goals = get_active_goals(memory)

    if not goals:
        return "현재 진행 중인 목표가 없어."

    lines = ["진행 중인 목표:"]

    for i, goal in enumerate(goals, start=1):
        lines.append(f"{i}. {goal['title']}")

    return "\n".join(lines)


def show_active_schedules(memory):
    schedules = get_active_schedules(memory)

    if not schedules:
        return "현재 미완료 일정이 없어."

    lines = ["미완료 일정:"]

    for i, item in enumerate(schedules, start=1):
        lines.append(
            f"{i}. {item['date']} - {item['title']}"
        )

    return "\n".join(lines)


def today_priority(memory):
    goals = get_active_goals(memory)

    if goals:
        return (
            "오늘 우선순위 추천:\n\n"
            f"1순위 목표: {goals[0]['title']}\n\n"
            "가장 먼저 등록된 미완료 목표부터 진행하는 걸 추천해."
        )

    return "먼저 목표를 추가해보자."


def development_advice(memory):
    return (
        "코코 AI 개발 우선순위:\n\n"
        "1. 안정화\n"
        "2. 테스트\n"
        "3. GitHub 백업\n"
        "4. 신규 기능 추가\n\n"
        "기능 수보다 안정성이 더 중요해."
    )


def procrastination_check(memory):
    goals = get_active_goals(memory)
    schedules = get_active_schedules(memory)

    if not goals and not schedules:
        return "현재 미루고 있는 항목은 없어 보여."

    text = []

    if goals:
        text.append(
            f"아직 완료되지 않은 목표가 {len(goals)}개 있어."
        )

    if schedules:
        text.append(
            f"미완료 일정이 {len(schedules)}개 있어."
        )

    text.append(
        "우선순위를 정해서 하나씩 처리하는 걸 추천해."
    )

    return "\n".join(text)


def handle_coach_command(user_input, memory):
    text = user_input.strip()

    if "오늘 뭐부터" in text:
        return today_priority(memory)

    if "개발 우선순위" in text:
        return development_advice(memory)

    if "목표 달성률" in text:
        return goal_progress(memory)

    if "미완료 목표" in text:
        return show_active_goals(memory)

    if "미완료 일정" in text:
        return show_active_schedules(memory)

    if "미루고 있는" in text:
        return procrastination_check(memory)

    return None