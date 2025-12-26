"""Основной класс сервера, объединяющий все компоненты."""

from __future__ import annotations

import contextlib

from core.voice_recorder import RecorderConfig, VoiceRecorder

from .config import AppConfig
from .llm import OllamaClient
from .stt import SpeechToText
from .tts import SileroTTS


class StrongServer:
    """Комбинирует распознавание речи, LLM и TTS в единый сервер."""

    def __init__(self, config: AppConfig, recorder_config: RecorderConfig | None = None):
        """
        Инициализирует сервер со всеми компонентами.

        Args:
            config: Конфигурация приложения
            recorder_config: Конфигурация записи голоса
        """
        self.config = config
        if recorder_config is None:
            recorder_config = RecorderConfig(
                sample_rate=config.recorder_sample_rate,
                chunk=config.recorder_chunk,
                silence_threshold=config.recorder_silence_threshold,
                silence_duration=config.recorder_silence_duration,
                max_recording=config.recorder_max_recording,
            )
        self.recorder = VoiceRecorder(recorder_config)
        self.stt = SpeechToText(config.whisper_model)
        self.llm = OllamaClient(
            model=config.ollama_model, system_prompt=config.system_prompt
        )
        self.tts = SileroTTS(speaker=config.tts_model)

    def run(self):
        """Основной цикл работы приложения."""
        print("[Starting] VoiceToNights сервисы запущены")
        print("[Info] Скажите 'стоп', 'выход' или 'заверши' для завершения работы\n")

        try:
            while True:
                # Записываем голосовую команду
                audio_path = self.recorder.capture_phrase()
                if not audio_path:
                    continue

                # Распознаём речь
                try:
                    user_text = self.stt.transcribe(audio_path)
                finally:
                    with contextlib.suppress(OSError):
                        audio_path.unlink()

                if not user_text:
                    print("[Warn] Whisper не распознал текст. Повторите команду.\n")
                    continue

                print(f"[User] Вы сказали: {user_text}")

                # Проверяем команду остановки
                if self._should_stop(user_text):
                    print("[Info] Завершаю работу по команде пользователя.")
                    break

                # Получаем ответ от LLM
                answer = self.llm.ask(user_text)
                if answer:
                    print()
                    self.tts.speak(answer)
                    print()

        except KeyboardInterrupt:
            print("\n[Info] Прервано пользователем.")

    @staticmethod
    def _should_stop(text: str) -> bool:
        """
        Проверяет, является ли текст командой остановки.

        Args:
            text: Текст для проверки

        Returns:
            True, если это команда остановки
        """
        normalized = text.lower().strip()
        stop_commands = {"стоп", "остановись", "выход", "пока", "заверши", "завершить"}
        return normalized in stop_commands or normalized.startswith("заверши")

