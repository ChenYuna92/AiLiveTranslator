from difflib import SequenceMatcher


class TextCorrector:
    def __init__(self):
        self.previous_original = ""
        self.previous_translation = ""

    def correct_original(self, text: str) -> str:
        return " ".join(text.split())

    def correct_translation(self, text: str) -> str:
        return " ".join(text.split())

    def should_update(self, original: str, translation: str) -> bool:
        if not original or not translation:
            return False
        if self.previous_original and SequenceMatcher(None, self.previous_original.lower(), original.lower()).ratio() > 0.9:
            return False
        self.previous_original = original
        self.previous_translation = translation
        return True
