def build_startup_message(memory):
    goals = memory.get("goals", [])
    schedules = memory.get("schedules", [])

    active_goals = [
        g for g in goals
        if not g.get("done")
    ]

    active_schedules = [
        s for s in schedules
        if not s.get("done")
    ]

    lines = []

    lines.append("안녕하세요.")
    lines.append("코코 AI입니다.")
    lines.append("")

    lines.append(f"현재 목표: {len(active_goals)}개")
    lines.append(f"현재 일정: {len(active_schedules)}개")
    lines.append("")

    if active_goals:
        lines.append("대표 프로젝트:")
        lines.append(active_goals[0]["title"])
        lines.append("")

        lines.append("오늘 추천:")
        lines.append(active_goals[0]["title"])
        lines.append("")

    lines.append("오늘도 개발을 이어갈까요?")

    return "\n".join(lines)