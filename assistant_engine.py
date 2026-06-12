def analyze_user(memory):
    likes = memory.get("likes", {})
    habits = memory.get("habits", {})
    profile = memory.get("profile", {})
    facts = memory.get("facts", [])

    lines = []

    lines.append("지금까지 기억을 바탕으로 보면,")

    if likes:
        like_text = ", ".join([f"{k}은/는 {v}" for k, v in likes.items()])
        lines.append(f"너의 취향은 {like_text} 쪽으로 보여.")

    if habits:
        habit_text = ", ".join([f"{k}에는 {v}" for k, v in habits.items()])
        lines.append(f"습관을 보면 {habit_text} 하는 편이야.")

    if facts:
        lines.append("또 여러 기억을 보면, 너는 직접 만들고 실험하면서 배우는 성향이 강해 보여.")

    lines.append("전체적으로 너는 아이디어를 실제 결과물로 만들고 싶어 하는 사람이고,")
    lines.append("코코 AI처럼 장기 프로젝트를 꾸준히 발전시키는 데 관심이 큰 사람으로 보여.")

    return "\n".join(lines)


def user_strength(memory):
    return (
        "내가 보기엔 너의 장점은 실행력이야.\n"
        "막연하게 생각만 하는 게 아니라 직접 설치하고, 오류를 확인하고, 고치면서 앞으로 나아가고 있어.\n"
        "또 포기하지 않고 단계별로 계속 밀고 가는 끈기도 강점이야."
    )


def user_goal(memory):
    return (
        "네 목표는 코코 AI를 단순 챗봇이 아니라,\n"
        "기억하고, 대화하고, 판단하고, PC를 제어하고, 너에게 조언까지 해주는 개인 AI 비서로 키우는 거야."
    )


def today_priority(memory):
    return (
        "오늘은 기능을 많이 늘리기보다 안정성을 우선하는 게 좋아.\n"
        "우선순위는 이렇게 추천할게.\n"
        "1. 지금까지 만든 기능이 정상 작동하는지 확인\n"
        "2. 기억 기반 대화가 자연스럽게 나오는지 테스트\n"
        "3. 문제가 없으면 다음 기능을 하나만 추가\n"
        "오늘은 코코 AI 10.11 대화형 개인 비서 엔진 테스트에 집중하는 게 좋아."
    )


def should_continue_coco(memory):
    return (
        "응, 계속하는 게 좋아.\n"
        "다만 한 번에 너무 많이 만들려고 하면 헷갈릴 수 있어.\n"
        "오늘은 코코 AI 개발을 계속하되, 목표를 하나로 줄이는 게 좋아.\n"
        "추천 목표는 '기억을 바탕으로 나를 분석하고 조언하는 기능 완성'이야."
    )


def personal_assistant_reply(user_input, memory):
    text = user_input.strip()

    if "내 목표" in text or "목표가 뭐" in text:
        return user_goal(memory)

    if "내 장점" in text or "장점은 뭐" in text:
        return user_strength(memory)

    if "오늘" in text and ("우선" in text or "뭘" in text or "해야" in text):
        return today_priority(memory)

    if "코코 AI 개발 계속" in text or "개발 계속할까" in text:
        return should_continue_coco(memory)

    if "나를 분석" in text or "기억을 바탕으로" in text or "나는 어떤 사람" in text:
        return analyze_user(memory)

    return None