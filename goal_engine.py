def get_goals(memory):
    if "goals" not in memory:
        memory["goals"] = []

    return memory["goals"]


def add_goal(memory, goal_text):
    goals = get_goals(memory)

    goal_text = goal_text.strip()

    if not goal_text:
        return "추가할 목표 내용을 말해줘."

    for goal in goals:
        if goal.get("title") == goal_text:
            return "이미 같은 목표가 있어."

    goals.append({
        "title": goal_text,
        "done": False
    })

    return f"목표를 추가했어: {goal_text}"


def show_goals(memory):
    goals = get_goals(memory)

    if not goals:
        return "아직 등록된 목표가 없어."

    lines = ["현재 목표 목록:"]

    for i, goal in enumerate(goals, start=1):
        status = "완료" if goal.get("done") else "진행중"
        lines.append(f"{i}. [{status}] {goal.get('title')}")

    return "\n".join(lines)


def complete_goal(memory, goal_text):
    goals = get_goals(memory)
    goal_text = goal_text.strip()

    for goal in goals:
        if goal_text in goal.get("title", ""):
            goal["done"] = True
            return f"목표를 완료 처리했어: {goal.get('title')}"

    return "해당 목표를 찾지 못했어."


def delete_goal(memory, goal_text):
    goals = get_goals(memory)
    goal_text = goal_text.strip()

    for goal in goals:
        if goal_text in goal.get("title", ""):
            removed = goal.get("title")
            goals.remove(goal)
            return f"목표를 삭제했어: {removed}"

    return "삭제할 목표를 찾지 못했어."


def recommend_today_goal(memory):
    goals = get_goals(memory)

    active_goals = [goal for goal in goals if not goal.get("done")]

    if not active_goals:
        return "진행 중인 목표가 없어. 먼저 목표를 하나 추가해보자."

    first_goal = active_goals[0].get("title")

    return (
        "오늘은 이 목표를 우선하는 게 좋아:\n\n"
        f"- {first_goal}\n\n"
        "이유는 아직 완료되지 않은 목표 중 가장 먼저 등록된 목표라서,\n"
        "지금 흐름을 이어가기 좋기 때문이야."
    )


def handle_goal_command(user_input, memory):
    text = user_input.strip()

    if text.startswith("목표 추가:"):
        goal_text = text.replace("목표 추가:", "", 1)
        return add_goal(memory, goal_text)

    if text.startswith("목표 완료:"):
        goal_text = text.replace("목표 완료:", "", 1)
        return complete_goal(memory, goal_text)

    if text.startswith("목표 삭제:"):
        goal_text = text.replace("목표 삭제:", "", 1)
        return delete_goal(memory, goal_text)

    if "목표 보여" in text or "목표 목록" in text or "내 목표 보여" in text:
        return show_goals(memory)

    if "오늘 목표" in text or "목표 추천" in text:
        return recommend_today_goal(memory)

    return None