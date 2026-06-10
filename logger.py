from datetime import datetime

LOG_FILE = "logs.txt"


def save_log(user_input, answer):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{now}]\n")
        f.write(f"사용자: {user_input}\n")
        f.write(f"코코: {answer}\n")
        f.write("-" * 50 + "\n")