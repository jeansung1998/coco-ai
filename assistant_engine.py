def analyze_user(memory):
    likes = memory.get("likes", {})
    habits = memory.get("habits", {})
    facts = memory.get("facts", [])

    result = []

    result.append("지금까지 기억을 바탕으로 분석해볼게.")

    if likes:
        result.append("")
        result.append("[취향]")
        for k, v in likes.items():
            result.append(f"- {k}: {v}")

    if habits:
        result.append("")
        result.append("[습관]")
        for k, v in habits.items():
            result.append(f"- {k}: {v}")

    result.append("")
    result.append("[분석]")

    if len(habits) >= 3:
        result.append("너는 반복적인 습관이 비교적 뚜렷한 사람이야.")

    if "주말" in habits:
        result.append("주말에도 자기 프로젝트를 진행하는 성향이 있어.")

    result.append("직접 만들고 테스트하면서 배우는 스타일이 강해.")
    result.append("아이디어를 실제 결과물로 만드는 걸 좋아하는 편이야.")

    return "\n".join(result)


def user_strength(memory):
    strengths = [
        "실행력이 강함",
        "포기하지 않고 계속 시도함",
        "직접 만들어 보면서 배움",
        "장기 프로젝트를 꾸준히 진행함"
    ]

    return "너의 강점은:\n\n- " + "\n- ".join(strengths)


def user_weakness(memory):
    return (
        "가능한 약점을 분석해보면,\n\n"
        "- 한 번에 너무 많은 기능을 만들려고 할 수 있음\n"
        "- 큰 목표를 급하게 진행하려는 경향이 있음\n"
        "- 기능 추가에 집중하다가 정리를 미룰 수 있음\n\n"
        "그래서 기능 추가보다 안정화 시간을 따로 두는 게 좋아."
    )


def recommend_job(memory):
    return (
        "현재 기억을 기준으로 보면,\n\n"
        "- AI 개발자\n"
        "- 소프트웨어 개발자\n"
        "- 제품 기획자\n"
        "- 스타트업 창업가\n"
        "- 자동화 시스템 설계자\n\n"
        "방향이 잘 맞아 보여."
    )


def habit_analysis(memory):
    habits = memory.get("habits", {})

    if not habits:
        return "아직 분석할 습관 데이터가 부족해."

    text = ["현재 습관 분석 결과:"]

    for k, v in habits.items():
        text.append(f"- {k}: {v}")

    text.append("")
    text.append("전체적으로 꾸준히 반복하는 활동이 있는 편이야.")

    return "\n".join(text)


def today_advice(memory):
    return (
        "오늘의 조언:\n\n"
        "새 기능을 3개 추가하는 것보다\n"
        "기존 기능 1개를 완성하는 것이 더 가치 있을 수 있어.\n\n"
        "완성도를 우선해봐."
    )


def dev_advice(memory):
    return (
        "코코 AI 개발 조언:\n\n"
        "새 기능을 추가하기 전에\n"
        "GitHub 백업 → 테스트 → 기능 추가 순서로 진행해.\n\n"
        "장기적으로 훨씬 안정적인 프로젝트가 돼."
    )


def personal_assistant_reply(user_input, memory):
    text = user_input.strip()

    if "내 목표" in text:
        return (
            "네 목표는 코코 AI를 단순 챗봇이 아니라\n"
            "기억하고, 판단하고, 조언하고,\n"
            "PC까지 제어하는 개인 AI 비서로 성장시키는 거야."
        )

    if "내 장점" in text:
        return user_strength(memory)

    if "내 약점" in text:
        return user_weakness(memory)

    if "직업" in text or "잘 맞는 일" in text:
        return recommend_job(memory)

    if "습관 분석" in text:
        return habit_analysis(memory)

    if "오늘의 조언" in text:
        return today_advice(memory)

    if "개발 조언" in text:
        return dev_advice(memory)

    if "나를 분석" in text or "나는 어떤 사람" in text:
        return analyze_user(memory)

    return None