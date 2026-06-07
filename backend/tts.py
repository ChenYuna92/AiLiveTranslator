from utils.logger import get_logger


class SpeechPlayer:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.logger = get_logger("语音播报")
        self.engine = None
        if enabled:
            try:
                import pyttsx3

                self.engine = pyttsx3.init()
            except Exception as exc:
                self.logger.warning("语音播报初始化失败: %s", exc)
                self.enabled = False

    def speak(self, text: str) -> None:
        if not self.enabled or self.engine is None or not text:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as exc:
            self.logger.warning("语音播报失败: %s", exc)
