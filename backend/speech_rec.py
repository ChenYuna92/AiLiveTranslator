from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Optional

import numpy as np
from faster_whisper import WhisperModel

from utils.logger import get_logger


@dataclass
class SpeechResult:
    text: str
    start: float = 0.0
    end: float = 0.0


class SpeechRecognizer:
    def __init__(
        self,
        model_size: str = "tiny",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en",
        beam_size: int = 3,
        initial_prompt: str = "",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.beam_size = beam_size
        self.initial_prompt = initial_prompt
        self.model: Optional[WhisperModel] = None
        self.logger = get_logger("\u8bed\u97f3\u8bc6\u522b")

    def load(self) -> None:
        for candidate in self._model_candidates(self.model_size):
            try:
                self.logger.info("\u52a0\u8f7d Whisper \u6a21\u578b: %s", candidate)
                self.model = WhisperModel(candidate, device=self.device, compute_type=self.compute_type)
                self.model_size = candidate
                self.logger.info("Whisper \u6a21\u578b\u52a0\u8f7d\u5b8c\u6210: %s", candidate)
                return
            except Exception as exc:
                self.logger.warning("\u6a21\u578b %s \u52a0\u8f7d\u5931\u8d25: %s", candidate, exc)
        raise RuntimeError("\u6ca1\u6709\u53ef\u7528\u7684 Whisper \u6a21\u578b\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u6216\u4f7f\u7528\u5df2\u7f13\u5b58\u7684 tiny \u6a21\u578b")

    def recognize(self, audio: np.ndarray) -> SpeechResult:
        if self.model is None:
            self.load()
        if self._is_silence(audio):
            return SpeechResult("")
        try:
            segments, _ = self.model.transcribe(
                audio,
                language=self.language,
                beam_size=self.beam_size,
                temperature=0.0,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 350},
                condition_on_previous_text=True,
                initial_prompt=self.initial_prompt or None,
            )
            valid_segments = []
            for segment in segments:
                if getattr(segment, "no_speech_prob", 0.0) > 0.75:
                    continue
                if getattr(segment, "avg_logprob", 0.0) < -1.0:
                    continue
                valid_segments.append(segment.text.strip())
            text = " ".join(valid_segments).strip()
            if self._is_bad_text(text):
                return SpeechResult("")
            return SpeechResult(text=text, start=0.0, end=len(audio) / 16000)
        except Exception as exc:
            self.logger.error("\u8bc6\u522b\u5f02\u5e38: %s", exc)
            return SpeechResult("")

    @staticmethod
    def _is_silence(audio: np.ndarray) -> bool:
        if audio.size == 0:
            return True
        rms = float(np.sqrt(np.mean(np.square(audio))))
        peak = float(np.max(np.abs(audio)))
        return rms < 0.003 and peak < 0.02

    @staticmethod
    def _is_bad_text(text: str) -> bool:
        normalized = re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()
        hallucinations = {
            "thank you for watching",
            "thanks for watching",
            "thank you",
            "you",
            "bye",
            "goodbye",
            "music",
            "applause",
        }
        if normalized in hallucinations:
            return True
        if "thank you for watching" in normalized:
            return True
        words = [word.strip(".,!?;:").lower() for word in text.split() if word.strip(".,!?;:")]
        if len(words) < 2:
            return True
        if len(words) >= 6 and len(set(words)) <= 2:
            return True
        if len(words) >= 6 and all(word.isdigit() for word in words):
            return True
        return False

    @staticmethod
    def _model_candidates(preferred: str) -> List[str]:
        candidates = [preferred]
        cache = Path.home() / ".cache" / "huggingface" / "hub"
        if cache.exists():
            for path in cache.glob("models--Systran--faster-whisper-*"):
                name = path.name.replace("models--Systran--faster-whisper-", "")
                if name and name not in candidates:
                    candidates.append(name)
        if "tiny" not in candidates:
            candidates.append("tiny")
        return candidates
