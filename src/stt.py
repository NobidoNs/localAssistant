"""Модуль для распознавания речи (Speech-to-Text) через Whisper."""

from __future__ import annotations

from pathlib import Path

import whisper


class SpeechToText:
    """Обёртка над Whisper для локального распознавания речи."""

    def __init__(self, model_name: str = "base"):
        """
        Инициализирует модель Whisper.

        Args:
            model_name: Название модели Whisper (tiny, base, small, medium, large)
        """
        print(f"[STT] Загружаем модель Whisper ({model_name})...")
        self.model = whisper.load_model(model_name)
        print("[STT] Модель загружена.")

    def transcribe(self, audio_path: Path, language: str = "ru") -> str:
        """
        Преобразует аудиофайл в текст.

        Args:
            audio_path: Путь к аудиофайлу
            language: Язык распознавания (по умолчанию русский)

        Returns:
            Распознанный текст
        """
        result = self.model.transcribe(str(audio_path), language=language)
        return result.get("text", "").strip()

