def recent_memory_summary(memory):
    likes = memory.get("likes", {})
    habits = memory.get("habits", {})
    facts = memory.get("facts", [])

    lines = ["최근 기억 요약"]

    if likes:
        lines.append("")
        lines.append("[취향]")
        for k, v in likes.items():
            lines.append(f"- {k}: {v}")

    if habits:
        lines.append("")
        lines.append("[습관]")
        for k, v in habits.items():
            lines.append(f"- {k}: {v}")

    if facts:
        lines.append("")
        lines.append(f"기억 개수: {len(facts)}개")

    return "\n".join(lines)


def recent_goal_summary(memory):
    goals = memory.get("goals", [])

    if not goals:
        return "등록된 목표가 없어."

    lines = ["최근 목표"]

    for goal in goals[-5:]:
        status = "완료" if goal.get("done") else "진행중"
        lines.append(f"- [{status}] {goal['title']}")

    return "\n".join(lines)


def recent_schedule_summary(memory):
    schedules = memory.get("schedules", [])

    if not schedules:
        return "등록된 일정이 없어."

    lines = ["최근 일정"]

    for item in schedules[-5:]:
        status = "완료" if item.get("done") else "예정"
        lines.append(
            f"- [{status}] {item['date']} {item['title']}"
        )

    return "\n".join(lines)


def project_summary(memory):
    goals = memory.get("goals", [])

    if goals:
        return (
            "현재 가장 중요한 프로젝트는\n"
            f"'{goals[0]['title']}' 로 보여."
        )

    return (
        "현재 목표 데이터가 부족해서 "
        "대표 프로젝트를 판단하기 어려워."
    )


def overall_status(memory):
    goal_count = len(memory.get("goals", []))
    schedule_count = len(memory.get("schedules", []))
    habit_count = len(memory.get("habits", {}))

    return (
        "현재 상태 요약\n\n"
        f"목표: {goal_count}개\n"
        f"일정: {schedule_count}개\n"
        f"습관: {habit_count}개\n\n"
        "코코 AI는 정상적으로 성장 중이야."
    )


def handle_memory_summary_command(user_input, memory):
    text = user_input.strip()

    if "최근 기억" in text:
        return recent_memory_summary(memory)

    if "최근 목표" in text:
        return recent_goal_summary(memory)

    if "최근 일정" in text:
        return recent_schedule_summary(memory)

    if "내 프로젝트" in text:
        return project_summary(memory)

    if "내 상태" in text:
        return overall_status(memory)

    return None