"""Тесты для модуля LLM."""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm import OllamaClient
from src.config import AppConfig

def test_ollama_client_ask():
    """Тест отправки запроса и получения ответа от Ollama."""
    # Загружаем конфигурацию
    config = AppConfig.from_file(project_root / "config.json")
    
    # Создаём клиент с моделью из конфига
    model = config.ollama_model
    client = OllamaClient(model=model)
    
    # Отправляем простой запрос
    user_message = "Привет! Ответь одним словом: 'работает'"
    response = client.ask(user_message, stream=False)
    
    # Проверяем, что получили ответ (не пустой)
    assert response is not None, "Ответ не должен быть None"
    assert len(response) > 0, "Ответ не должен быть пустым"
    assert isinstance(response, str), "Ответ должен быть строкой"
    
    print(f"\n[TEST] Получен ответ: {response}")
    print(f"[TEST] Длина ответа: {len(response)} символов")

if __name__ == "__main__":
    test_ollama_client_ask()