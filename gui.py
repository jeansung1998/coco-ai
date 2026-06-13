import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import threading
import coco
import voice


class CocoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("코코 AI 데스크탑 모드 10.37")
        self.root.geometry("740x590")

        self.memory = coco.load_memory()

        self.title_label = tk.Label(
            root,
            text="코코 AI",
            font=("맑은 고딕", 24, "bold")
        )
        self.title_label.pack(pady=10)

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

        self.add_message("코코", "GUI 음성 모드가 연결되었습니다.")

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

        self.clear_button = tk.Button(
            self.bottom_frame,
            text="화면 지우기",
            font=("맑은 고딕", 11),
            width=12,
            command=self.clear_screen
        )
        self.clear_button.grid(row=0, column=0, padx=5)

        self.exit_button = tk.Button(
            self.bottom_frame,
            text="종료",
            font=("맑은 고딕", 11),
            width=12,
            command=self.root.destroy
        )
        self.exit_button.grid(row=0, column=1, padx=5)

        self.user_input.focus()

    def get_time(self):
        return datetime.now().strftime("%H:%M")

    def add_message(self, sender, message):
        now = self.get_time()

        if sender == "나":
            self.chat_area.insert(tk.END, f"[{now}] 나\n", "time")
            self.chat_area.insert(tk.END, f"{message}\n\n", "user")
        else:
            self.chat_area.insert(tk.END, f"[{now}] 코코\n", "time")
            self.chat_area.insert(tk.END, f"{message}\n\n", "coco")

        self.chat_area.see(tk.END)

    def send_message(self, event=None):
        text = self.user_input.get().strip()

        if not text:
            return

        self.handle_user_text(text)

    def handle_user_text(self, text):
        self.add_message("나", text)
        self.user_input.delete(0, tk.END)

        try:
            response = coco.coco_reply(text, self.memory, voice=False)
        except Exception as e:
            response = f"오류가 발생했습니다: {e}"

        self.add_message("코코", response)

        if text in ["종료", "끝", "exit", "quit"]:
            self.root.destroy()

    def start_voice_input(self):
        self.mic_button.config(state=tk.DISABLED, text="듣는 중...")
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
            return

        self.handle_user_text(text)

    def clear_screen(self):
        self.chat_area.delete("1.0", tk.END)
        self.add_message("코코", "화면을 지웠습니다.")

    def clear_screen_shortcut(self, event=None):
        self.clear_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = CocoGUI(root)
    root.mainloop()