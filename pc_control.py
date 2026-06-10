import os
import subprocess
import webbrowser


def open_notepad():
    try:
        os.system("start notepad")
        return "메모장을 실행했습니다."
    except Exception as e:
        return f"메모장 실행 중 오류가 발생했습니다: {e}"


def open_calculator():
    try:
        os.system("start calc")
        return "계산기를 실행했습니다."
    except Exception as e:
        return f"계산기 실행 중 오류가 발생했습니다: {e}"


def open_explorer():
    try:
        os.system("start explorer")
        return "탐색기를 실행했습니다."
    except Exception as e:
        return f"탐색기 실행 중 오류가 발생했습니다: {e}"


def find_chrome_path():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]

    for path in chrome_paths:
        if os.path.exists(path):
            return path

    return None


def open_chrome():
    try:
        chrome_path = find_chrome_path()

        if chrome_path:
            subprocess.Popen([chrome_path])
            return "크롬을 실행했습니다."

        webbrowser.open("https://www.google.com")
        return "크롬 경로를 직접 찾지는 못했지만, 기본 브라우저로 구글을 열었습니다."

    except Exception as e:
        return f"크롬 실행 중 오류가 발생했습니다: {e}"


def open_website(url):
    try:
        url = url.strip()

        if not url:
            return "열 웹사이트 주소가 없습니다."

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        chrome_path = find_chrome_path()

        if chrome_path:
            subprocess.Popen([chrome_path, url])
        else:
            webbrowser.open(url)

        return f"웹사이트를 열었습니다: {url}"

    except Exception as e:
        return f"웹사이트 실행 중 오류가 발생했습니다: {e}"


def handle_pc_command(text):
    text = text.strip()

    if text in ["메모장 열어줘", "메모장 실행", "메모장 켜줘"]:
        return open_notepad()

    if text in ["계산기 열어줘", "계산기 실행", "계산기 켜줘"]:
        return open_calculator()

    if text in ["탐색기 열어줘", "탐색기 실행", "파일 탐색기 열어줘"]:
        return open_explorer()

    if text in ["크롬 열어줘", "크롬 실행", "구글 크롬 열어줘"]:
        return open_chrome()

    if text.startswith("사이트 열어줘:"):
        url = text.replace("사이트 열어줘:", "", 1).strip()
        return open_website(url)

    if text.startswith("웹사이트 열어줘:"):
        url = text.replace("웹사이트 열어줘:", "", 1).strip()
        return open_website(url)

    return None