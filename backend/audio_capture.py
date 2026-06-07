from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np
import sounddevice as sd


@dataclass(frozen=True)
class AudioDevice:
    id: int
    name: str
    channels: int

    @property
    def label(self) -> str:
        return f"{self.id}: {self.name} ({self.channels}通道)"


class AudioCapture:
    def __init__(self, sample_rate: int = 16000, chunk_seconds: float = 1.0):
        self.sample_rate = sample_rate
        self.block_size = int(sample_rate * 0.1)
        self.chunk_samples = int(sample_rate * chunk_seconds)
        self.stream: Optional[sd.InputStream] = None
        self.callback: Optional[Callable[[np.ndarray], None]] = None
        self.buffer: List[float] = []
        self.running = False

    @staticmethod
    def list_devices() -> List[AudioDevice]:
        devices = []
        for index, device in enumerate(sd.query_devices()):
            channels = int(device.get("max_input_channels", 0))
            if channels > 0:
                devices.append(AudioDevice(index, str(device.get("name", "未知输入设备")), channels))
        return devices

    def set_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        self.callback = callback

    def start_capture(self, device_id: Optional[int] = None) -> None:
        if self.running:
            return
        self.running = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.block_size,
            device=device_id,
            callback=self._on_audio,
        )
        self.stream.start()

    def stop_capture(self) -> None:
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _on_audio(self, indata, frames, time_info, status) -> None:
        if not self.running:
            return
        self.buffer.extend(indata.reshape(-1).astype(np.float32).tolist())
        while len(self.buffer) >= self.chunk_samples:
            chunk = np.array(self.buffer[: self.chunk_samples], dtype=np.float32)
            self.buffer = self.buffer[self.chunk_samples :]
            if self.callback:
                self.callback(chunk)
