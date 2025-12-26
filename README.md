# Local Assistant

Голосовой ассистент с использованием Whisper (STT), Ollama (LLM) и Silero (TTS).

## Описание

VoiceToNights — это голосовой ассистент, который:
1. Записывает голосовые команды с микрофона (VAD)
2. Преобразует речь в текст через Whisper
3. Отправляет запрос в локальную LLM через Ollama
4. Озвучивает ответ через Silero TTS

## Установка

### 1. Клонируйте репозиторий

```bash
git clone github.com/NobidoNs/localAssistant
cd VoiceToNights
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Установите ffmpeg

**Windows:**
```bash
winget install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 5. Установите и запустите Ollama

**Установка:**
- Windows/Mac: скачайте с [ollama.ai](https://ollama.ai)
- Linux: `curl -fsSL https://ollama.ai/install.sh | sh`

**Запуск сервера:**
```bash
ollama serve
```

**Скачайте модель (в другом терминале):**
```bash
ollama pull llama3.1:8b
```

## Использование

Запустите приложение:

```bash
python main.py
```

Скажите команду или задайте вопрос в микрофон. Для завершения работы скажите: **"стоп"**, **"выход"** или **"заверши"**.

## Конфигурация

### config.json

Отредактируйте `config.json` для настройки параметров:

```json
{
    "ollama_model": "llama3.1:8b",
    "whisper_model": "base",
    "tts_model": "kseniya",
    "tts_speed": 1.0,
    "tts_volume": 1.0,
    "tts_sample_rate": 48000,
    "tts_gap_seconds": 0.25
}
```

**Параметры:**
- `ollama_model` — модель Ollama (например, "llama3.1:8b", "mistral", "codellama")
- `whisper_model` — модель Whisper: `tiny`, `base`, `small`, `medium`, `large`
- `tts_model` — голосовой профиль Silero: `xenia`, `aidar`, `baya`, `kseniya`, `eugene`
- `tts_speed` — скорость воспроизведения (1.0 = нормальная)
- `tts_volume` — громкость (1.0 = максимальная)
- `tts_sample_rate` — частота дискретизации аудио (48000 по умолчанию)
- `tts_gap_seconds` — пауза между предложениями в секундах
- `system_prompt` — системный промпт для LLM (опционально, по умолчанию используется из `prompts.json`)

### prompts.json

Файл содержит системные промпты для LLM:

```json
{
    "system_prompt_default": "Ты — дружелюбный ассистент StrongServer. Отвечай кратко и по делу, используя русский язык."
}
```

Можно добавить дополнительные промпты и использовать их через `src.prompts.get_prompt(key)`.

## Разработка

Для получения информации о процессе разработки и принципах архитектуры см. [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

См. файл LICENSE.
