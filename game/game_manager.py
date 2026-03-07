"""Менеджер игровых сессий."""

from typing import Dict, Any

from ai.base_ai import BaseAI
from ai.gigachat_ai import GigaChatAI
from ai.openai_ai import OpenAICompatibleAI
from config import Config
from database.db_manager import DatabaseManager
from .cities_game import CitiesGame


_AI_FACTORIES = {
    "gigachat": lambda: GigaChatAI(Config.GIGACHAT_CREDENTIALS),
    "gpt4o": lambda: OpenAICompatibleAI(
        api_key=Config.VSEGPT_API_KEY,
        base_url=Config.VSEGPT_BASE_URL,
        model=Config.VSEGPT_MODEL,
    ),
}

AI_DISPLAY_NAMES = {
    "gigachat": "GigaChat (Сбер)",
    "gpt4o": "GPT-4o (OpenAI)",
}


class GameManager:
    """Управляет играми всех пользователей."""

    def __init__(self, db: DatabaseManager):
        self._games: Dict[int, CitiesGame] = {}
        self._ai_providers: Dict[int, BaseAI] = {}
        self._ai_keys: Dict[int, str] = {}
        self._db = db

    def _create_ai(self, ai_key: str, chat_id: int) -> BaseAI:
        """Создаёт AI-провайдер с подключённой БД."""
        ai = _AI_FACTORIES[ai_key]()
        ai.set_db(self._db)
        ai.set_chat_id(chat_id)
        return ai

    def set_ai(self, chat_id: int, ai_key: str) -> str:
        if ai_key not in _AI_FACTORIES:
            return "❌ Неизвестная модель."
        self._ai_providers[chat_id] = self._create_ai(ai_key, chat_id)
        self._ai_keys[chat_id] = ai_key
        return f"✅ Модель переключена на *{AI_DISPLAY_NAMES[ai_key]}*"

    def get_ai(self, chat_id: int) -> BaseAI:
        if chat_id not in self._ai_providers:
            self.set_ai(chat_id, "gigachat")
        return self._ai_providers[chat_id]

    def get_ai_name(self, chat_id: int) -> str:
        key = self._ai_keys.get(chat_id, "gigachat")
        return AI_DISPLAY_NAMES.get(key, "AI")

    def start_game(self, chat_id: int) -> str:
        self._games[chat_id] = CitiesGame()
        ai_name = self.get_ai_name(chat_id)
        return (
            f"🏙️ *Игра в города начата!*\n"
            f"🤖 Соперник: {ai_name}\n\n"
            f"Назови любой город:"
        )

    def stop_game(self, chat_id: int) -> str:
        if chat_id in self._games:
            game = self._games.pop(chat_id)
            return (
                f"🛑 Игра остановлена.\n"
                f"📊 Сыграно ходов: {game.move_count}\n"
                f"/start — новая игра"
            )
        return "Нет активной игры. /start — начать."

    def process_city(self, chat_id: int, city_input: str) -> Dict[str, Any]:
        if chat_id not in self._games:
            return {"error": "Игра не начата. Нажми /start"}

        ai = self.get_ai(chat_id)
        ai.set_chat_id(chat_id)
        game = self._games[chat_id]

        return game.process_turn(
            city_input,
            ai.is_valid_city,
            lambda letter, used: ai.get_city(letter, used, Config.MAX_AI_ATTEMPTS),
        )

    def get_city_info(self, chat_id: int, city_name: str) -> str:
        ai = self.get_ai(chat_id)
        ai.set_chat_id(chat_id)
        return ai.get_city_info(city_name)

    def game_exists(self, chat_id: int) -> bool:
        return chat_id in self._games

    def get_db_stats(self) -> str:
        """Статистика БД."""
        count = self._db.get_logs_count()
        return f"📊 Всего запросов к AI в БД: {count}"