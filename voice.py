import speech_recognition as sr
import pyttsx3
WAKE_WORDS = [
    "코코야",
    "코코",
    "야 코코",
    "야코코",
    "꼬꼬야",
    "코꼬야"
]


def remove_wake_word(text):
    if not text:
        return ""

    text = text.strip()

    for word in WAKE_WORDS:
        if text.startswith(word):
            return text.replace(word, "", 1).strip()

    return text

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.say(text)
        engine.runAndWait()
        return True

    except Exception as e:
        print(f"음성 출력 오류: {e}")
        return False


def listen():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("코코: 듣는 중입니다.")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)

            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=6
            )

        try:
            text = recognizer.recognize_google(
                audio,
                language="ko-KR"
            )

            return remove_wake_word(text)

        except sr.UnknownValueError:
            return ""

        except sr.RequestError:
            return ""

    except sr.WaitTimeoutError:
        return ""

    except:
        return ""


def is_exit_command(text):
    text = text.replace(" ", "").strip()

    exit_words = [
        "그만",
        "그만해",
        "그만하자",
        "멈춰",
        "멈처",
        "종료",
        "끝",
        "음성종료",
        "코코종료",
        "대화종료"
    ]

    return text in exit_words


def voice_test():
    speak("코코 음성 테스트를 시작합니다.")

    text = listen()

    if text:
        print("인식된 말:", text)
        speak(f"제가 들은 말은 {text} 입니다.")

    else:
        print("인식된 말이 없습니다.")
        speak("말을 인식하지 못했습니다.")