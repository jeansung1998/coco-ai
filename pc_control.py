import os
import subprocess
import webbrowser
import urllib.parse


PROJECT_FOLDER = r"C:\coco-ai"


def normalize(text):
    return text.strip().replace(" ", "").lower()


def open_notepad():
    os.system("start notepad")
    return "메모장을 실행했습니다."


def open_calculator():
    os.system("start calc")
    return "계산기를 실행했습니다."


def open_explorer():
    os.system("start explorer")
    return "탐색기를 실행했습니다."


def get_user_folder(folder_name):
    home = os.path.expanduser("~")

    folders = {
        "바탕화면": [os.path.join(home, "Desktop"), os.path.join(home, "OneDrive", "Desktop")],
        "다운로드": [os.path.join(home, "Downloads")],
        "문서": [os.path.join(home, "Documents"), os.path.join(home, "OneDrive", "Documents")],
        "사진": [os.path.join(home, "Pictures"), os.path.join(home, "OneDrive", "Pictures")],
        "음악": [os.path.join(home, "Music")],
        "동영상": [os.path.join(home, "Videos")],
        "코코": [PROJECT_FOLDER],
        "코코폴더": [PROJECT_FOLDER],
        "프로젝트": [PROJECT_FOLDER],
        "프로젝트폴더": [PROJECT_FOLDER],
    }

    candidates = folders.get(folder_name)

    if not candidates:
        return None

    for path in candidates:
        if os.path.exists(path):
            return path

    return candidates[0]


def open_folder(path):
    path = path.strip()

    if not path:
        return "열 폴더 경로가 없습니다."

    shortcut_path = get_user_folder(normalize(path))
    if shortcut_path:
        path = shortcut_path

    if not os.path.exists(path):
        return f"폴더를 찾지 못했습니다: {path}"

    if not os.path.isdir(path):
        return f"폴더가 아닙니다: {path}"

    subprocess.Popen(["explorer", path])
    return f"폴더를 열었습니다: {path}"


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
    chrome_path = find_chrome_path()

    if chrome_path:
        subprocess.Popen([chrome_path])
        return "크롬을 실행했습니다."

    webbrowser.open("https://www.google.com")
    return "기본 브라우저로 구글을 열었습니다."


def open_website(url, name=None):
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
    original = text.strip()
    cmd = normalize(original)

    if cmd in ["메모장열어줘", "메모장실행", "메모장켜줘"]:
        return open_notepad()

    if cmd in ["계산기열어줘", "계산기실행", "계산기켜줘"]:
        return open_calculator()

    if cmd in ["탐색기열어줘", "탐색기실행", "파일탐색기열어줘"]:
        return open_explorer()

    if cmd in ["크롬열어줘", "크롬실행", "구글크롬열어줘"]:
        return open_chrome()

    if cmd in ["바탕화면열어줘", "바탕화면열기"]:
        return open_folder("바탕화면")

    if cmd in ["다운로드열어줘", "다운로드열기"]:
        return open_folder("다운로드")

    if cmd in ["문서열어줘", "문서열기"]:
        return open_folder("문서")

    if cmd in ["사진열어줘", "사진열기"]:
        return open_folder("사진")

    if cmd in ["음악열어줘", "음악열기"]:
        return open_folder("음악")

    if cmd in ["동영상열어줘", "동영상열기"]:
        return open_folder("동영상")

    if cmd in ["코코폴더열어줘", "코코열어줘", "프로젝트폴더열어줘"]:
        return open_folder("코코")

    if original.startswith("폴더 열어줘:"):
        path = original.replace("폴더 열어줘:", "", 1).strip()
        return open_folder(path)

    if original.startswith("폴더 열기:"):
        path = original.replace("폴더 열기:", "", 1).strip()
        return open_folder(path)

    if cmd in ["네이버열어줘", "네이버실행"]:
        return open_website("https://www.naver.com", "네이버")

    if cmd in ["구글열어줘", "구글실행"]:
        return open_website("https://www.google.com", "구글")

    if cmd in ["유튜브열어줘", "유튜브실행"]:
        return open_website("https://www.youtube.com", "유튜브")

    if cmd in ["깃허브열어줘", "깃허브실행", "github열어줘"]:
        return open_website("https://github.com", "깃허브")

    if cmd in ["챗gpt열어줘", "챗지피티열어줘", "chatgpt열어줘"]:
        return open_website("https://chatgpt.com", "챗GPT")

    if original.startswith("사이트 열어줘:"):
        url = original.replace("사이트 열어줘:", "", 1).strip()
        return open_website(url)

    if original.startswith("웹사이트 열어줘:"):
        url = original.replace("웹사이트 열어줘:", "", 1).strip()
        return open_website(url)

    if original.startswith("검색해줘:"):
        keyword = original.replace("검색해줘:", "", 1).strip()
        return google_search(keyword)

    if original.startswith("구글 검색:"):
        keyword = original.replace("구글 검색:", "", 1).strip()
        return google_search(keyword)

    if original.startswith("유튜브 검색:"):
        keyword = original.replace("유튜브 검색:", "", 1).strip()
        return youtube_search(keyword)

    return None