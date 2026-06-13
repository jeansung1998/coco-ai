from datetime import datetime


def build_morning_briefing(memory):
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

    today = datetime.now().strftime("%Y-%m-%d")

    lines = []

    lines.append("=================")
    lines.append("코코 AI 아침 브리핑")
    lines.append("=================")
    lines.append("")
    lines.append(f"오늘 날짜: {today}")
    lines.append("")

    lines.append(f"현재 목표: {len(active_goals)}개")
    lines.append(f"현재 일정: {len(active_schedules)}개")
    lines.append("")

    if active_goals:
        lines.append("대표 프로젝트:")
        lines.append(active_goals[0]["title"])
        lines.append("")

    if active_schedules:
        lines.append("가장 가까운 일정:")
        lines.append(active_schedules[0]["title"])
        lines.append("")

    if active_goals:
        lines.append("오늘 추천 작업:")
        lines.append(active_goals[0]["title"])
        lines.append("")

    lines.append("오늘도 한 단계씩 진행해보자.")

    return "\n".join(lines)