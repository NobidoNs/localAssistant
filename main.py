"""Главная точка входа для VoiceToNights - голосовой ассистент."""
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импортов
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import AppConfig
from src.server import StrongServer


def main():
    """Запуск приложения."""
    # Загружаем конфигурацию
    config_path = Path(__file__).parent / "config.json"
    config = AppConfig.from_file(config_path)
    
    # Устанавливаем системный промпт по умолчанию, если не задан
    if config.system_prompt is None:
        default_config = AppConfig.default()
        config.system_prompt = default_config.system_prompt

    # Создаём и запускаем сервер
    server = StrongServer(config=config)
    server.run()


if __name__ == "__main__":
    main()
