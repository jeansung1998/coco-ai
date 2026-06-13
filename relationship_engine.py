def get_people(memory):
    if "people" not in memory:
        memory["people"] = {}

    return memory["people"]


def remember_relationship(memory, text):
    people = get_people(memory)

    patterns = [
        ("는 내 친구야", "친구"),
        ("는 우리 팀장이야", "팀장"),
        ("는 개발자야", "개발자"),
        ("는 내 동료야", "동료"),
        ("는 내 가족이야", "가족"),
    ]

    for pattern, role in patterns:
        if pattern in text:
            name = text.replace(pattern, "").strip()

            if name:
                people[name] = role
                return f"{name} 정보를 기억했어. ({role})"

    return None


def who_is_person(memory, text):
    people = get_people(memory)

    if not text.endswith("는 누구야?"):
        return None

    name = text.replace("는 누구야?", "").strip()

    if name in people:
        return f"{name}는 네 {people[name]}야."

    return f"{name}에 대한 정보가 없어."


def list_people(memory):
    people = get_people(memory)

    if not people:
        return "기억된 사람이 없어."

    lines = ["기억된 사람 목록"]

    for name, role in people.items():
        lines.append(f"- {name}: {role}")

    return "\n".join(lines)


def handle_relationship_command(user_input, memory):
    text = user_input.strip()

    remembered = remember_relationship(memory, text)

    if remembered:
        return remembered

    person_answer = who_is_person(memory, text)

    if person_answer:
        return person_answer

    if text in [
        "사람 목록",
        "기억된 사람",
        "사람 보여줘"
    ]:
        return list_people(memory)

    return None