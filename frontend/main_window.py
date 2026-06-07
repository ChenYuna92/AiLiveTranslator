import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from backend.audio_capture import AudioDevice


class ControlWindow:
    def __init__(
        self,
        devices: list[AudioDevice],
        on_start: Callable[[Optional[int]], None],
        on_stop: Callable[[], None],
        on_demo: Callable[[], None],
    ):
        self.root = tk.Toplevel()
        self.root.title("\u0041\u0049\u540c\u58f0\u4f20\u8bd1\u52a9\u624b")
        self.root.geometry("420x230+80+80")
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_demo = on_demo
        self.devices = devices

        tk.Label(self.root, text="\u97f3\u9891\u8f93\u5165\u6e90").pack(anchor="w", padx=14, pady=(14, 4))
        self.device_box = ttk.Combobox(self.root, state="readonly")
        values = ["\u7cfb\u7edf\u9ed8\u8ba4\u8f93\u5165"] + [device.label for device in devices]
        self.device_box["values"] = values
        self.device_box.current(0)
        self.device_box.pack(fill=tk.X, padx=14)

        self.status_label = tk.Label(self.root, text="\u72b6\u6001\uff1a\u672a\u542f\u52a8", anchor="w")
        self.status_label.pack(fill=tk.X, padx=14, pady=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=14, pady=4)
        tk.Button(button_frame, text="\u5f00\u59cb\u4f20\u8bd1", command=self.start).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(button_frame, text="\u6682\u505c", command=self.stop).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(button_frame, text="\u5b57\u5e55\u6f14\u793a", command=self.demo).pack(side=tk.LEFT)

    def start(self) -> None:
        index = self.device_box.current()
        device_id = None if index <= 0 else self.devices[index - 1].id
        self.status_label.config(text="\u72b6\u6001\uff1a\u6b63\u5728\u4f20\u8bd1")
        self.on_start(device_id)

    def stop(self) -> None:
        self.status_label.config(text="\u72b6\u6001\uff1a\u5df2\u6682\u505c")
        self.on_stop()

    def demo(self) -> None:
        self.status_label.config(text="\u72b6\u6001\uff1a\u5b57\u5e55\u6f14\u793a")
        self.on_demo()
