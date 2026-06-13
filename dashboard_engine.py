def build_dashboard(memory):
    goals = memory.get("goals", [])
    schedules = memory.get("schedules", [])
    facts = memory.get("facts", [])

    completed_goals = [
        g for g in goals
        if g.get("done")
    ]

    active_goals = [
        g for g in goals
        if not g.get("done")
    ]

    active_schedules = [
        s for s in schedules
        if not s.get("done")
    ]

    project_name = "없음"

    if active_goals:
        project_name = active_goals[0]["title"]

    lines = []

    lines.append("=================")
    lines.append("코코 AI 대시보드")
    lines.append("=================")
    lines.append("")

    lines.append(f"목표: {len(goals)}개")
    lines.append(f"완료 목표: {len(completed_goals)}개")
    lines.append("")

    lines.append(f"일정: {len(schedules)}개")
    lines.append(f"미완료 일정: {len(active_schedules)}개")
    lines.append("")

    lines.append(f"기억: {len(facts)}개")
    lines.append("")

    lines.append("대표 프로젝트:")
    lines.append(project_name)
    lines.append("")

    if active_goals:
        lines.append("오늘 추천:")
        lines.append(active_goals[0]["title"])

    return "\n".join(lines)


def handle_dashboard_command(user_input, memory):
    text = user_input.strip()

    if text in [
        "내 상태 보여줘",
        "대시보드 보여줘",
        "코코 상태 보여줘"
    ]:
        return build_dashboard(memory)

    return None