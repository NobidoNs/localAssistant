"""Модуль для синтеза речи (Text-to-Speech) через Silero TTS."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
import torch
import silero as silero_pkg
from silero import silero_tts


class SileroTTS:
    """Обёртка над Silero TTS для озвучивания текста."""

    def __init__(
        self, speaker: str = "kseniya", sample_rate: int = 48000, device: str | None = None
    ):
        """
        Инициализирует Silero TTS модель.

        Args:
            speaker: Голосовой профиль ('xenia', 'aidar', 'baya', 'kseniya', 'eugene')
            sample_rate: Частота дискретизации аудио
            device: Устройство для вычислений ('cuda' или 'cpu'), если None - определит автоматически
        """
        self.speaker = speaker
        self.sample_rate = sample_rate
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        torch.set_num_threads(os.cpu_count() or 4)

        print(f"[TTS] Загружаем модель Silero TTS (speaker={speaker})...")
        self.model = self._load_model_with_retry()
        self.model.to(self.device)
        print("[TTS] Модель загружена.")

    def _load_model_with_retry(self):
        """Загружает модель Silero, очищая кеш если он повреждён."""
        cache_dir = Path.home() / ".cache" / "torch" / "silero_models"
        model_dir = Path(silero_pkg.__file__).resolve().parent / "model"

        try:
            mdl, _ = silero_tts(language="ru", speaker="v5_ru")
            return mdl
        except RuntimeError as exc:
            if "PytorchStreamReader" not in str(exc):
                raise
            print("[TTS] Обнаружен повреждённый кеш, очищаем...")
            shutil.rmtree(cache_dir, ignore_errors=True)
            shutil.rmtree(model_dir, ignore_errors=True)
            mdl, _ = silero_tts(language="ru", speaker="v5_ru")
            return mdl

    def _split_sentences(self, text: str) -> list[str]:
        """Разбивает текст на предложения."""
        try:
            from razdel import sentenize

            return [s.text.strip() for s in sentenize(text)]
        except Exception:
            text = re.sub(r"\s+", " ", text).strip()
            parts = re.split(r"(?<=[\.\!\?…])\s+", text)
            return [p.strip() for p in parts if p.strip()]

    def _fade_edges(self, x: np.ndarray, ms: float = 5.0) -> np.ndarray:
        """Применяет плавное затухание к краям аудио."""
        n = max(1, int(self.sample_rate * ms / 1000.0))
        if x.size < 2 * n:
            return x
        w = np.linspace(0.0, 1.0, n, dtype=np.float32)
        x[:n] *= w
        x[-n:] *= w[::-1]
        return x

    def _normalize_peak(self, x: np.ndarray, peak: float = 0.98) -> np.ndarray:
        """Нормализует аудио по пиковому уровню."""
        m = float(np.max(np.abs(x))) or 1.0
        return (x / m) * peak

    def _synthesize(self, sentence: str) -> np.ndarray:
        """Синтезирует аудио для одного предложения."""
        audio = self.model.apply_tts(text=sentence, speaker=self.speaker, sample_rate=self.sample_rate)
        audio = np.asarray(audio, dtype=np.float32)
        audio = self._normalize_peak(self._fade_edges(audio))
        return audio

    def _play_audio(self, audio: np.ndarray) -> None:
        """Воспроизводит аудио через sounddevice или системный плеер."""
        try:
            import sounddevice as sd

            sd.play(audio, self.sample_rate)
            sd.wait()
        except Exception:
            # Fallback на системный плеер
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                path = tmp.name
            sf.write(path, audio, self.sample_rate)
            try:
                if sys.platform == "darwin":
                    subprocess.run(["afplay", path], check=False)
                elif sys.platform.startswith("win"):
                    import winsound

                    winsound.PlaySound(path, winsound.SND_FILENAME)
                else:
                    subprocess.run(["ffplay", "-autoexit", "-nodisp", path], check=False)
            finally:
                try:
                    os.remove(path)
                except OSError:
                    pass

    def speak(self, text: str, gap_seconds: float = 0.25) -> None:
        """
        Озвучивает текст.

        Args:
            text: Текст для озвучивания
            gap_seconds: Пауза между предложениями в секундах
        """
        sentences = self._split_sentences(text)
        for idx, sentence in enumerate(sentences, 1):
            preview = sentence[:80] + ("..." if len(sentence) > 80 else "")
            print(f"▶ {idx}/{len(sentences)}: {preview}")
            audio = self._synthesize(sentence)
            self._play_audio(audio)
            if idx < len(sentences):
                time.sleep(gap_seconds)


def read_text(
    text: Optional[str] = None,
    *,
    file_path: Optional[str | Path] = None,
    speaker: str = "kseniya",
) -> None:
    """
    Озвучивает переданную строку либо содержимое файла (удобная функция для обратной совместимости).

    Args:
        text: Текст для озвучивания
        file_path: Путь к текстовому файлу
        speaker: Голосовой профиль
    """
    tts = SileroTTS(speaker=speaker)
    if file_path:
        target_text = Path(file_path).read_text(encoding="utf-8")
    elif text:
        target_text = text
    else:
        raise ValueError("Передайте текст напрямую или укажите путь к файлу.")

    tts.speak(target_text)

