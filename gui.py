import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import threading
import json
import os
import coco
import voice


class CocoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("코코 AI 데스크탑 모드 10.39")
        self.root.geometry("760x640")

        self.memory = coco.load_memory()
        self.voice_output_enabled = True
        self.chat_history_file = "chat_history.json"

        self.title_label = tk.Label(
            root,
            text="코코 AI",
            font=("맑은 고딕", 24, "bold")
        )
        self.title_label.pack(pady=10)

        self.status_label = tk.Label(
            root,
            text="상태: 대기 중",
            font=("맑은 고딕", 11)
        )
        self.status_label.pack(pady=2)

        self.chat_area = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            height=22
        )
        self.chat_area.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

        self.chat_area.tag_config("user", lmargin1=20, lmargin2=20)
        self.chat_area.tag_config("coco", lmargin1=20, lmargin2=20)
        self.chat_area.tag_config("time", foreground="gray")

        self.load_chat_history()
        self.add_message("코코", "코코 AI 10.41 대화 기록을 불러왔습니다.", save=False)

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=15, pady=10, fill=tk.X)

        self.user_input = tk.Entry(
            self.input_frame,
            font=("맑은 고딕", 12)
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.send_button = tk.Button(
            self.input_frame,
            text="전송",
            font=("맑은 고딕", 12),
            width=8,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)

        self.mic_button = tk.Button(
            self.input_frame,
            text="🎤 듣기",
            font=("맑은 고딕", 12),
            width=10,
            command=self.start_voice_input
        )
        self.mic_button.pack(side=tk.RIGHT, padx=(0, 8))

        self.user_input.bind("<Return>", self.send_message)
        self.root.bind("<Control-l>", self.clear_screen_shortcut)
        self.root.bind("<Control-L>", self.clear_screen_shortcut)

        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(pady=5)

        self.voice_button = tk.Button(
            self.bottom_frame,
            text="🔊 음성 ON",
            font=("맑은 고딕", 11),
            width=12,
            command=self.toggle_voice_output
        )
        self.voice_button.grid(row=0, column=0, padx=5)

        self.clear_button = tk.Button(
            self.bottom_frame,
            text="화면 지우기",
            font=("맑은 고딕", 11),
            width=12,
            command=self.clear_screen
        )
        self.clear_button.grid(row=0, column=1, padx=5)

        self.exit_button = tk.Button(
            self.bottom_frame,
            text="종료",
            font=("맑은 고딕", 11),
            width=12,
            command=self.root.destroy
        )
        self.exit_button.grid(row=0, column=2, padx=5)

        self.user_input.focus()

    def set_status(self, text):
        self.status_label.config(text=f"상태: {text}")
        self.root.update_idletasks()

    def get_time(self):
        return datetime.now().strftime("%H:%M")

    def add_message(self, sender, message, save=True):
        now = self.get_time()

        if sender == "나":
            self.chat_area.insert(tk.END, f"[{now}] 나\n", "time")
            self.chat_area.insert(tk.END, f"{message}\n\n", "user")
        else:
            self.chat_area.insert(tk.END, f"[{now}] 코코\n", "time")
            self.chat_area.insert(tk.END, f"{message}\n\n", "coco")

        self.chat_area.see(tk.END)

        if save:
            self.save_chat_message(sender, message)

    def save_chat_message(self, sender, message):
        data = []

        if os.path.exists(self.chat_history_file):
            try:
                with open(
                    self.chat_history_file,
                    "r",
                    encoding="utf-8"
                ) as f:
                    data = json.load(f)

            except Exception:
                data = []

        data.append({
            "time": datetime.now().isoformat(
                timespec="seconds"
            ),
            "sender": sender,
            "message": message
        })

        with open(
            self.chat_history_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
        )

    def load_chat_history(self):
        if not os.path.exists(self.chat_history_file):
            return

        try:
            with open(self.chat_history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        recent_messages = data[-20:]

        for item in recent_messages:
            sender = item.get("sender", "코코")
            message = item.get("message", "")

            if message:
                self.add_message(sender, message, save=False)                

    def send_message(self, event=None):
        text = self.user_input.get().strip()

        if not text:
            return

        self.handle_user_text(text)

    def handle_user_text(self, text):
        self.add_message("나", text)
        self.user_input.delete(0, tk.END)

        self.set_status("처리 중")

        try:
            response = coco.coco_reply(text, self.memory, voice=False)
        except Exception as e:
            response = f"오류가 발생했습니다: {e}"

        self.add_message("코코", response)
        self.speak_response(response)

        if text in ["종료", "끝", "exit", "quit"]:
            self.root.destroy()
            return

        if not self.voice_output_enabled:
            self.set_status("대기 중")

    def speak_response(self, response):
        if not self.voice_output_enabled:
            return

        thread = threading.Thread(
            target=self.speak_worker,
            args=(response,)
        )
        thread.daemon = True
        thread.start()

    def speak_worker(self, response):
        try:
            self.root.after(0, lambda: self.set_status("말하는 중"))
            voice.speak(response)
        except Exception as e:
            print(f"음성 출력 오류: {e}")
        finally:
            self.root.after(0, lambda: self.set_status("대기 중"))

    def toggle_voice_output(self):
        self.voice_output_enabled = not self.voice_output_enabled

        if self.voice_output_enabled:
            self.voice_button.config(text="🔊 음성 ON")
            self.add_message("코코", "음성 출력을 켰습니다.")
        else:
            self.voice_button.config(text="🔇 음성 OFF")
            self.add_message("코코", "음성 출력을 껐습니다.")

        self.set_status("대기 중")

    def start_voice_input(self):
        self.mic_button.config(state=tk.DISABLED, text="듣는 중...")
        self.set_status("듣는 중")
        self.add_message("코코", "듣는 중입니다. 말씀해주세요.")

        thread = threading.Thread(target=self.voice_input_worker)
        thread.daemon = True
        thread.start()

    def voice_input_worker(self):
        text = voice.listen()
        self.root.after(0, lambda: self.finish_voice_input(text))

    def finish_voice_input(self, text):
        self.mic_button.config(state=tk.NORMAL, text="🎤 듣기")

        if not text:
            self.add_message("코코", "말을 인식하지 못했습니다.")
            self.set_status("대기 중")
            return

        self.handle_user_text(text)

    def clear_screen(self):
        self.chat_area.delete("1.0", tk.END)
        self.add_message("코코", "화면을 지웠습니다.")
        self.set_status("대기 중")

    def clear_screen_shortcut(self, event=None):
        self.clear_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = CocoGUI(root)
    root.mainloop()