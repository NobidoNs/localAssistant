"""Централизованное управление промптами приложения."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

_PROMPTS_FILE = Path(__file__).parent.parent / "prompts.json"


@lru_cache(maxsize=1)
def _load_prompts_file() -> dict[str, Any]:
    """Загружает и кэширует промпты из JSON файла."""
    # Если файла нет - возвращаем пустой словарь
    if not _PROMPTS_FILE.exists():
        return {}
    
    # Если файл есть - открываем и читаем
    with _PROMPTS_FILE.open(encoding="utf-8") as f:
        return json.load(f)




def get_prompt(key: str) -> str:
    prompts = _load_prompts_file()
    prompt = prompts.get(key)
    return prompt


def reload_prompts() -> None:
    """Сбрасывает кэш промптов для перезагрузки из файла."""
    _load_prompts_file.cache_clear()

