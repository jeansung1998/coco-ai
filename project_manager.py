def project_status(memory):
    goals = memory.get("goals", [])
    schedules = memory.get("schedules", [])
    projects = memory.get("projects", {})

    active_goals = [
        g for g in goals
        if not g.get("done")
    ]

    active_schedules = [
        s for s in schedules
        if not s.get("done")
    ]

    lines = []

    lines.append("코코 AI 프로젝트 상태")
    lines.append("")

    if "코코 AI" in projects:
        lines.append("[프로젝트 기억]")
        lines.append(projects["코코 AI"])
        lines.append("")

    lines.append(f"진행 중 목표: {len(active_goals)}개")
    lines.append(f"미완료 일정: {len(active_schedules)}개")
    lines.append("")

    if active_goals:
        lines.append("현재 핵심 목표:")
        lines.append(active_goals[0]["title"])
    else:
        lines.append("현재 핵심 목표가 없어.")

    return "\n".join(lines)


def project_progress(memory):
    goals = memory.get("goals", [])

    if not goals:
        return "아직 목표가 없어서 진행률을 계산하기 어려워."

    total = len(goals)
    done = len([
        g for g in goals
        if g.get("done")
    ])

    percent = int((done / total) * 100)

    return (
        f"코코 AI 프로젝트 진행률은 약 {percent}%야.\n"
        f"전체 목표 {total}개 중 {done}개를 완료했어."
    )


def next_project_task(memory):
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

    if active_schedules:
        return (
            "다음 작업 추천:\n\n"
            f"먼저 일정부터 처리하는 게 좋아.\n"
            f"- {active_schedules[0]['title']}"
        )

    if active_goals:
        return (
            "다음 작업 추천:\n\n"
            f"현재 목표를 이어서 진행하는 게 좋아.\n"
            f"- {active_goals[0]['title']}"
        )

    return "현재 추천할 작업이 없어. 새 목표를 추가해보자."


def recent_dev_stage(memory):
    projects = memory.get("projects", {})

    if "코코 AI" in projects:
        return (
            "최근 개발 단계:\n\n"
            f"{projects['코코 AI']}"
        )

    return "최근 개발 단계 정보가 없어."


def handle_project_command(user_input, memory):
    text = user_input.strip()

    if "프로젝트 상태" in text:
        return project_status(memory)

    if "진행률" in text:
        return project_progress(memory)

    if "다음 작업" in text:
        return next_project_task(memory)

    if "최근 개발 단계" in text:
        return recent_dev_stage(memory)

    return None