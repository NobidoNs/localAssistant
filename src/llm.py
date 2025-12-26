"""Модуль для работы с LLM через Ollama."""

from __future__ import annotations

import ollama


class OllamaClient:
    """Лёгкая обёртка над python-API Ollama."""

    def __init__(self, model: str = "llama3.1:8b", system_prompt: str | None = None):
        """
        Инициализирует клиент Ollama.

        Args:
            model: Название модели Ollama
            system_prompt: Системный промпт для модели
        """
        self.model = model
        self.system_prompt = system_prompt

    def ask(self, user_text: str, stream: bool = True) -> str:
        """
        Отправляет запрос в модель и получает ответ.

        Args:
            user_text: Текст пользователя
            stream: Включить потоковый вывод

        Returns:
            Ответ модели
        """
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_text})

        print("[LLM] Ollama думает...")
        stream_response = ollama.chat(
            model=self.model, messages=messages, stream=stream
        )

        if stream:
            chunks: list[str] = []
            for chunk in stream_response:
                delta = chunk["message"]["content"]
                print(delta, end="", flush=True)
                chunks.append(delta)
            print()
            return "".join(chunks).strip()
        else:
            response = stream_response["message"]["content"]
            print(response)
            return response.strip()

