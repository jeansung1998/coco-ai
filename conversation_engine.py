def natural_conversation(user_input, memory):
    text = user_input.strip()

    goals = memory.get("goals", [])
    schedules = memory.get("schedules", [])
    habits = memory.get("habits", {})

    active_goals = [
        g for g in goals
        if not g.get("done")
    ]

    if "피곤" in text:
        count = len(schedules)

        return (
            f"최근 일정이 {count}개 있고,\n"
            "계속 여러 작업을 진행하고 있어서\n"
            "피곤할 수 있어.\n\n"
            "오늘은 너무 무리하지 않는 것도 중요해."
        )

    if "힘들" in text:
        return (
            "최근에도 꾸준히 코코 AI를 개발해왔어.\n"
            "지금까지 진행한 걸 보면 충분히 잘하고 있어."
        )

    if "뭐하지" in text:
        if active_goals:
            return (
                "지금은 이 목표를 진행하는 걸 추천해.\n\n"
                f"- {active_goals[0]['title']}"
            )

    if "심심" in text:
        return (
            "코코 AI 기능 하나를 개선하거나\n"
            "기존 기능을 테스트해보는 건 어때?"
        )

    return None