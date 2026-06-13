def startup_voice_message(memory):
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

    lines.append(
        f"현재 목표는 {len(active_goals)}개입니다."
    )

    lines.append(
        f"현재 일정은 {len(active_schedules)}개입니다."
    )

    if active_goals:
        lines.append(
            f"현재 대표 프로젝트는 {active_goals[0]['title']} 입니다."
        )

    lines.append("오늘도 개발을 이어갈까요?")

    return "\n".join(lines)


def briefing_voice_message(memory):
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

    lines.append(
        "아침 브리핑을 시작합니다."
    )

    lines.append(
        f"현재 목표는 {len(active_goals)}개입니다."
    )

    lines.append(
        f"현재 일정은 {len(active_schedules)}개입니다."
    )

    if active_goals:
        lines.append(
            f"오늘 추천 작업은 {active_goals[0]['title']} 입니다."
        )

    return "\n".join(lines)