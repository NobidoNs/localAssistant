"""Модуль для загрузки и управления конфигурацией."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.prompts import get_prompt


@dataclass
class AppConfig:
    ollama_model: str | None = None
    whisper_model: str | None = None
    tts_model: str | None = None
    tts_speed: float | None = None
    tts_volume: float | None = None
    tts_sample_rate: int | None = None
    tts_gap_seconds: float | None = None
    system_prompt: str | None = None
    recorder_sample_rate: int | None = None
    recorder_chunk: int | None = None
    recorder_silence_threshold: int | None = None
    recorder_silence_duration: float | None = None
    recorder_max_recording: float | None = None

    @classmethod
    def from_file(cls, config_path: Path | str) -> AppConfig:
        """Загружает конфигурацию из JSON файла."""
        path = Path(config_path)
        if not path.exists():
            return cls()

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            ollama_model=data.get("ollama_model"),
            whisper_model=data.get("whisper_model"),
            tts_model=data.get("tts_model"),
            tts_speed=data.get("tts_speed"),
            tts_volume=data.get("tts_volume"),
            tts_sample_rate=data.get("tts_sample_rate"),
            tts_gap_seconds=data.get("tts_gap_seconds"),
            system_prompt=data.get("system_prompt"),
            recorder_sample_rate=data.get("recorder_sample_rate"),
            recorder_chunk=data.get("recorder_chunk"),
            recorder_silence_threshold=data.get("recorder_silence_threshold"),
            recorder_silence_duration=data.get("recorder_silence_duration"),
            recorder_max_recording=data.get("recorder_max_recording"),
        )

    @classmethod
    def default(cls) -> AppConfig:
        """Возвращает конфигурацию по умолчанию."""
        return cls(system_prompt=get_prompt("system_prompt_default"))

