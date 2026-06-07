import queue
import re
import threading
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Callable, Optional

import numpy as np

from backend.speech_rec import SpeechRecognizer
from backend.text_correct import TextCorrector
from backend.translate_core import Translator
from backend.tts import SpeechPlayer
from utils.logger import get_logger


@dataclass
class SubtitlePayload:
    original: str
    translation: str


class StreamManager:
    def __init__(
        self,
        recognizer: SpeechRecognizer,
        translator: Translator,
        corrector: TextCorrector,
        speaker: SpeechPlayer,
        on_subtitle: Callable[[SubtitlePayload], None],
        sample_rate: int = 16000,
        context_seconds: float = 6.0,
        min_update_seconds: float = 1.0,
        min_translate_words: int = 8,
        max_wait_seconds: float = 2.8,
    ):
        self.recognizer = recognizer
        self.translator = translator
        self.corrector = corrector
        self.speaker = speaker
        self.on_subtitle = on_subtitle
        self.sample_rate = sample_rate
        self.context_samples = int(sample_rate * context_seconds)
        self.min_update_seconds = min_update_seconds
        self.min_translate_words = min_translate_words
        self.max_wait_seconds = max_wait_seconds
        self.audio_queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=3)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.logger = get_logger("调度")
        self.audio_context = np.zeros(0, dtype=np.float32)
        self.pending_text = ""
        self.last_original = ""
        self.last_translation = ""
        self.last_update_at = 0.0
        self.pending_started_at = 0.0
        self.silence_seconds = 0.0

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.pending_started_at = time.monotonic()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        self._reset_context()
        if self.thread:
            self.thread.join(timeout=1.0)

    def push_audio(self, audio: np.ndarray) -> None:
        if not self.running:
            return
        while self.audio_queue.full():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        try:
            self.audio_queue.put_nowait(audio)
        except queue.Full:
            self.logger.warning("音频队列已满，丢弃当前片段")

    def _loop(self) -> None:
        while self.running:
            try:
                audio = self.audio_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if self._is_silent_audio(audio):
                self._handle_silence(audio)
                continue

            self.silence_seconds = 0.0
            self._append_audio(audio)
            result = self.recognizer.recognize(self.audio_context)
            text = self.corrector.correct_original(result.text)
            candidate = self._build_candidate(text)
            if not candidate or not self._ready_to_translate(candidate):
                continue

            translation = self.corrector.correct_translation(self.translator.translate(candidate))
            if not translation or not self._should_update(candidate, translation):
                continue

            self.last_original = candidate
            self.last_translation = translation
            self.last_update_at = time.monotonic()
            self.on_subtitle(SubtitlePayload(original=candidate, translation=translation))
            self.speaker.speak(translation)

            if self._is_sentence_end(candidate):
                self._reset_context()

    def _append_audio(self, audio: np.ndarray) -> None:
        self.audio_context = np.concatenate([self.audio_context, audio.astype(np.float32)])
        if self.audio_context.size > self.context_samples:
            self.audio_context = self.audio_context[-self.context_samples :]

    def _handle_silence(self, audio: np.ndarray) -> None:
        self.silence_seconds += audio.size / max(self.sample_rate, 1)
        if self.silence_seconds >= 0.8:
            self._reset_context()

    def _build_candidate(self, text: str) -> str:
        text = self._remove_noise(text.strip())
        if not text:
            return ""
        candidate = self._current_sentence(text)
        if not candidate:
            return ""
        if not self.pending_text or SequenceMatcher(None, self.pending_text.lower(), candidate.lower()).ratio() < 0.75:
            self.pending_text = candidate
            self.pending_started_at = time.monotonic()
        return candidate

    def _ready_to_translate(self, text: str) -> bool:
        now = time.monotonic()
        if now - self.last_update_at < self.min_update_seconds:
            return False
        words = self._word_count(text)
        if words < 4:
            return False
        if self._is_sentence_end(text):
            return True
        if words >= self.min_translate_words:
            return True
        return now - self.pending_started_at >= self.max_wait_seconds and words >= 6

    def _should_update(self, original: str, translation: str) -> bool:
        if not self.last_original:
            return True
        original_similarity = SequenceMatcher(None, self.last_original.lower(), original.lower()).ratio()
        translation_similarity = SequenceMatcher(None, self.last_translation, translation).ratio()
        return not (original_similarity > 0.92 and translation_similarity > 0.88)

    def _reset_context(self) -> None:
        self.audio_context = np.zeros(0, dtype=np.float32)
        self.pending_text = ""
        self.pending_started_at = time.monotonic()
        self.silence_seconds = 0.0

    @staticmethod
    def _current_sentence(text: str) -> str:
        parts = re.split(r"(?<=[.!?])\s+", text)
        parts = [part.strip() for part in parts if part.strip()]
        if not parts:
            return ""
        if len(parts[-1].split()) >= 4:
            return parts[-1]
        return parts[-2] if len(parts) >= 2 else parts[-1]

    @staticmethod
    def _remove_noise(text: str) -> str:
        normalized = re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()
        bad = {"thank you for watching", "thanks for watching", "thank you", "music", "applause"}
        if normalized in bad or "thank you for watching" in normalized:
            return ""
        words = text.split()
        if len(words) >= 8:
            cleaned = [word.strip(".,!?;:").lower() for word in words]
            half = len(words) // 2
            for size in range(min(10, half), 2, -1):
                if cleaned[-size:] == cleaned[-2 * size : -size]:
                    return " ".join(words[:-size])
        return text

    @staticmethod
    def _is_silent_audio(audio: np.ndarray) -> bool:
        if audio.size == 0:
            return True
        rms = float(np.sqrt(np.mean(np.square(audio))))
        peak = float(np.max(np.abs(audio)))
        return rms < 0.003 and peak < 0.02

    @staticmethod
    def _is_sentence_end(text: str) -> bool:
        return bool(re.search(r"[.!?]$", text.strip()))

    @staticmethod
    def _word_count(text: str) -> int:
        return len([word for word in text.split() if word.strip(".,!?;:")])
