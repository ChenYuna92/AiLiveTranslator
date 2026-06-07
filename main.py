import threading
import time

from backend.audio_capture import AudioCapture
from backend.speech_rec import SpeechRecognizer
from backend.stream_manager import StreamManager, SubtitlePayload
from backend.text_correct import TextCorrector
from backend.translate_core import Translator
from backend.tts import SpeechPlayer
from frontend.main_window import ControlWindow
from frontend.subtitle_view import SubtitleWindow
from utils.common import get_nested, load_dotenv, load_json_config
from utils.logger import get_logger


def main() -> None:
    load_dotenv()
    config = load_json_config()
    logger = get_logger("\u4e3b\u7a0b\u5e8f")
    sample_rate = int(get_nested(config, "audio.sample_rate", 16000))

    subtitle = SubtitleWindow(topmost=bool(get_nested(config, "ui.topmost", True)))
    audio = AudioCapture(
        sample_rate=sample_rate,
        chunk_seconds=float(get_nested(config, "audio.chunk_seconds", 2.0)),
    )
    recognizer = SpeechRecognizer(
        model_size=str(get_nested(config, "asr.model_size", "tiny")),
        language=str(get_nested(config, "asr.language", "en")),
        device=str(get_nested(config, "asr.device", "cpu")),
        compute_type=str(get_nested(config, "asr.compute_type", "int8")),
        beam_size=int(get_nested(config, "asr.beam_size", 3)),
        initial_prompt=str(get_nested(config, "asr.initial_prompt", "")),
    )
    translator = Translator(
        region=str(get_nested(config, "translation.region", "ap-shanghai")),
        source_lang=str(get_nested(config, "translation.source_lang", "en")),
        target_lang=str(get_nested(config, "translation.target_lang", "zh")),
    )
    corrector = TextCorrector()
    speaker = SpeechPlayer(enabled=bool(get_nested(config, "ui.speak_translation", False)))
    manager = StreamManager(
        recognizer=recognizer,
        translator=translator,
        corrector=corrector,
        speaker=speaker,
        on_subtitle=subtitle.update_subtitle,
        sample_rate=sample_rate,
        context_seconds=float(get_nested(config, "stream.context_seconds", 6.0)),
        min_update_seconds=float(get_nested(config, "stream.min_update_seconds", 1.0)),
        min_translate_words=int(get_nested(config, "stream.min_translate_words", 9)),
        max_wait_seconds=float(get_nested(config, "stream.max_wait_seconds", 3.0)),
    )

    def start(device_id):
        try:
            manager.start()
            audio.set_callback(manager.push_audio)
            audio.start_capture(device_id=device_id)
            logger.info("\u5f00\u59cb\u4f20\u8bd1")
        except Exception as exc:
            logger.error("\u542f\u52a8\u5931\u8d25: %s", exc)

    def stop():
        audio.stop_capture()
        manager.stop()
        logger.info("\u5df2\u6682\u505c")

    def demo():
        samples = [
            SubtitlePayload("Did you get the camera?", "\u4f60\u62ff\u5230\u76f8\u673a\u4e86\u5417\uff1f"),
            SubtitlePayload(
                "We need to make sure the audio is clean.",
                "\u6211\u4eec\u9700\u8981\u786e\u4fdd\u97f3\u9891\u8db3\u591f\u6e05\u6670\u3002",
            ),
            SubtitlePayload(
                "Then the translation can follow the speaker.",
                "\u8fd9\u6837\u7ffb\u8bd1\u5c31\u80fd\u8ddf\u4e0a\u8bf4\u8bdd\u4eba\u7684\u8282\u594f\u3002",
            ),
        ]

        def loop():
            for item in samples:
                subtitle.update_subtitle(item)
                time.sleep(1.8)

        threading.Thread(target=loop, daemon=True).start()

    ControlWindow(AudioCapture.list_devices(), on_start=start, on_stop=stop, on_demo=demo)
    subtitle.run()
    stop()


if __name__ == "__main__":
    main()
