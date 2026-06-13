def handle_emotion(user_input, memory):
    text = user_input.strip()

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

    if "힘들" in text:
        return (
            "최근에도 꾸준히 코코 AI를 개발해왔어.\n"
            "지금까지 진행한 걸 보면 충분히 잘하고 있어.\n\n"
            "오늘은 너무 무리하지 않는 것도 중요해."
        )

    if "피곤" in text:
        return (
            f"현재 일정이 {len(active_schedules)}개 있고,\n"
            "계속 여러 작업을 진행 중이야.\n\n"
            "잠깐 쉬고 다시 하는 것도 좋은 방법이야."
        )

    if "기분 좋" in text or "행복" in text:
        return (
            "좋네.\n\n"
            "그 기세로 코코 AI도 한 단계 발전시켜보자."
        )

    if "짜증" in text:
        return (
            "무슨 일이 있었는지 이야기해줄래?\n\n"
            "원인을 알면 같이 생각해볼 수 있어."
        )

    if "불안" in text:
        return (
            "불안할 때는 해야 할 일을 작은 단위로 나누는 게 도움이 돼.\n\n"
            "지금도 충분히 잘 진행하고 있어."
        )

    if "우울" in text:
        return (
            "요즘 조금 지칠 수 있는 상황일 수도 있겠네.\n\n"
            "잠시 쉬면서 컨디션을 챙기는 것도 중요해."
        )

    return None