import tkinter as tk

from backend.stream_manager import SubtitlePayload


class SubtitleWindow:
    def __init__(self, topmost: bool = True):
        self.root = tk.Tk()
        self.root.title("\u0041\u0049\u540c\u58f0\u4f20\u8bd1\u5b57\u5e55")
        self.root.geometry("960x150+160+760")
        self.root.configure(bg="#111111")
        self.root.attributes("-topmost", topmost)
        self.root.attributes("-alpha", 0.86)

        self.original_label = tk.Label(
            self.root,
            text="\u7b49\u5f85\u82f1\u6587\u97f3\u9891...",
            font=("Microsoft YaHei UI", 15, "bold"),
            fg="#d7e5ff",
            bg="#111111",
            wraplength=900,
        )
        self.original_label.pack(fill=tk.X, padx=18, pady=(14, 4))

        self.translation_label = tk.Label(
            self.root,
            text="\u8bd1\u6587\u5c06\u5728\u8fd9\u91cc\u663e\u793a",
            font=("Microsoft YaHei UI", 24, "bold"),
            fg="#ffffff",
            bg="#111111",
            wraplength=900,
        )
        self.translation_label.pack(fill=tk.X, padx=18, pady=(2, 14))

    def update_subtitle(self, payload: SubtitlePayload) -> None:
        self.root.after(0, lambda: self._apply_update(payload))

    def _apply_update(self, payload: SubtitlePayload) -> None:
        self.original_label.config(text=payload.original)
        self.translation_label.config(text=payload.translation)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self.root.destroy()
