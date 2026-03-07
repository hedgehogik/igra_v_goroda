"""Конфигурация приложения."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Главный класс конфигурации."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # GigaChat
    GIGACHAT_CREDENTIALS: str = os.getenv("GIGACHAT_CREDENTIALS", "")

    # VseGPT (OpenAI-compatible)
    VSEGPT_API_KEY: str = os.getenv("VSEGPT_API_KEY", "")
    VSEGPT_BASE_URL: str = os.getenv("VSEGPT_BASE_URL", "https://api.vsegpt.ru/v1")
    VSEGPT_MODEL: str = "openai/gpt-4o-mini"

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///cities_bot.db")

    # Игровые настройки
    MAX_AI_ATTEMPTS: int = 3
    SKIP_LETTERS: set = {"ь", "ы", "ъ", "й"}

    @classmethod
    def validate(cls) -> None:
        """Проверяет наличие обязательных переменных."""
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.GIGACHAT_CREDENTIALS:
            missing.append("GIGACHAT_CREDENTIALS")
        if not cls.VSEGPT_API_KEY:
            missing.append("VSEGPT_API_KEY")

        if missing:
            raise ValueError(
                f"Отсутствуют переменные окружения: {', '.join(missing)}\n"
                f"Создайте файл .env и заполните их."
            )