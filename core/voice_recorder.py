"""Модуль для записи голосовых команд с микрофона."""

from __future__ import annotations

import audioop
import contextlib
import os
import tempfile
import time
import wave
from dataclasses import dataclass
from pathlib import Path

import pyaudio


@dataclass
class RecorderConfig:
    sample_rate: int
    chunk: int
    silence_threshold: int  # Чем ниже значение, тем чувствительнее
    silence_duration: float  # секунд тишины прежде чем остановиться
    max_recording: float  # ограничение на длину записи, секунд


class VoiceRecorder:
    """Захватывает короткие фразы с микрофона с автоматическим VAD."""

    def __init__(self, config: RecorderConfig):
        self.config = config
        self._pa = pyaudio.PyAudio()

    def __del__(self):
        with contextlib.suppress(Exception):
            self._pa.terminate()

    def capture_phrase(self):
        stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.config.sample_rate,
            input=True,
            frames_per_buffer=self.config.chunk,
        )

        frames: list[bytes] = []
        silent_chunks = 0
        recording_started = False
        start_ts = time.time()
        max_silence_chunks = int(
            (self.config.sample_rate / self.config.chunk) * self.config.silence_duration
        )

        print("[Mic] Скажите команду (Ctrl+C — выход)...")
        try:
            while True:
                data = stream.read(self.config.chunk, exception_on_overflow=False)
                rms = audioop.rms(data, 2)

                if rms > self.config.silence_threshold:
                    recording_started = True
                    frames.append(data)
                    silent_chunks = 0
                elif recording_started:
                    frames.append(data)
                    silent_chunks += 1
                    if silent_chunks >= max_silence_chunks:
                        break

                if time.time() - start_ts >= self.config.max_recording:
                    break
        finally:
            stream.stop_stream()
            stream.close()

        if not frames:
            print("[Warn] Не удалось распознать речь — попробуйте ещё раз.")
            return None

        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with contextlib.closing(wave.open(tmp_path, "wb")) as wav_file:  # type: ignore[arg-type]
            wav_file.setnchannels(1)
            wav_file.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
            wav_file.setframerate(self.config.sample_rate)
            wav_file.writeframes(b"".join(frames))

        return Path(tmp_path)

