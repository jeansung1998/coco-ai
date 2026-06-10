import os
import subprocess
import webbrowser
import urllib.parse


PROJECT_FOLDER = r"C:\coco-ai"


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


def get_user_folder(folder_name):
    home = os.path.expanduser("~")

    folders = {
        "바탕화면": [
            os.path.join(home, "Desktop"),
            os.path.join(home, "OneDrive", "Desktop"),
        ],
        "다운로드": [
            os.path.join(home, "Downloads"),
        ],
        "문서": [
            os.path.join(home, "Documents"),
            os.path.join(home, "OneDrive", "Documents"),
        ],
        "사진": [
            os.path.join(home, "Pictures"),
            os.path.join(home, "OneDrive", "Pictures"),
        ],
        "음악": [
            os.path.join(home, "Music"),
        ],
        "동영상": [
            os.path.join(home, "Videos"),
        ],
        "프로젝트": [
            PROJECT_FOLDER,
        ],
        "코코": [
            PROJECT_FOLDER,
        ],
        "코코 폴더": [
            PROJECT_FOLDER,
        ],
    }

    candidates = folders.get(folder_name)

    if not candidates:
        return None

    for path in candidates:
        if os.path.exists(path):
            return path

    return candidates[0]


def open_folder(path):
    try:
        path = path.strip()

        if not path:
            return "열 폴더 경로가 없습니다."

        shortcut_path = get_user_folder(path)
        if shortcut_path:
            path = shortcut_path

        if not os.path.exists(path):
            return f"폴더를 찾지 못했습니다: {path}"

        if not os.path.isdir(path):
            return f"폴더가 아닙니다: {path}"

        subprocess.Popen(["explorer", path])
        return f"폴더를 열었습니다: {path}"

    except Exception as e:
        return f"폴더 열기 중 오류가 발생했습니다: {e}"


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


def open_website(url, name=None):
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

        if name:
            return f"{name}를 열었습니다."

        return f"웹사이트를 열었습니다: {url}"

    except Exception as e:
        return f"웹사이트 실행 중 오류가 발생했습니다: {e}"


def google_search(keyword):
    keyword = keyword.strip()

    if not keyword:
        return "검색할 내용이 없습니다."

    encoded = urllib.parse.quote(keyword)
    url = f"https://www.google.com/search?q={encoded}"

    return open_website(url, f"구글 검색 결과: {keyword}")


def youtube_search(keyword):
    keyword = keyword.strip()

    if not keyword:
        return "유튜브에서 검색할 내용이 없습니다."

    encoded = urllib.parse.quote(keyword)
    url = f"https://www.youtube.com/results?search_query={encoded}"

    return open_website(url, f"유튜브 검색 결과: {keyword}")


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

    if text in ["바탕화면 열어줘", "바탕화면 열기"]:
        return open_folder("바탕화면")

    if text in ["다운로드 열어줘", "다운로드 열기"]:
        return open_folder("다운로드")

    if text in ["문서 열어줘", "문서 열기"]:
        return open_folder("문서")

    if text in ["사진 열어줘", "사진 열기"]:
        return open_folder("사진")

    if text in ["음악 열어줘", "음악 열기"]:
        return open_folder("음악")

    if text in ["동영상 열어줘", "동영상 열기"]:
        return open_folder("동영상")

    if text in ["코코 폴더 열어줘", "코코 열어줘", "프로젝트 폴더 열어줘"]:
        return open_folder("코코")

    if text.startswith("폴더 열어줘:"):
        path = text.replace("폴더 열어줘:", "", 1).strip()
        return open_folder(path)

    if text.startswith("폴더 열기:"):
        path = text.replace("폴더 열기:", "", 1).strip()
        return open_folder(path)

    if text in ["네이버 열어줘", "네이버 실행"]:
        return open_website("https://www.naver.com", "네이버")

    if text in ["구글 열어줘", "구글 실행"]:
        return open_website("https://www.google.com", "구글")

    if text in ["유튜브 열어줘", "유튜브 실행"]:
        return open_website("https://www.youtube.com", "유튜브")

    if text in ["깃허브 열어줘", "깃허브 실행", "github 열어줘"]:
        return open_website("https://github.com", "깃허브")

    if text in ["챗GPT 열어줘", "챗지피티 열어줘", "chatgpt 열어줘"]:
        return open_website("https://chatgpt.com", "챗GPT")

    if text.startswith("사이트 열어줘:"):
        url = text.replace("사이트 열어줘:", "", 1).strip()
        return open_website(url)

    if text.startswith("웹사이트 열어줘:"):
        url = text.replace("웹사이트 열어줘:", "", 1).strip()
        return open_website(url)

    if text.startswith("검색해줘:"):
        keyword = text.replace("검색해줘:", "", 1).strip()
        return google_search(keyword)

    if text.startswith("구글 검색:"):
        keyword = text.replace("구글 검색:", "", 1).strip()
        return google_search(keyword)

    if text.startswith("유튜브 검색:"):
        keyword = text.replace("유튜브 검색:", "", 1).strip()
        return youtube_search(keyword)

    return None