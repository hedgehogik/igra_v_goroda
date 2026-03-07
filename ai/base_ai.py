"""Базовый класс AI-провайдера с логированием в БД."""

import re
import time
from abc import ABC, abstractmethod
from typing import Set, Optional

from database.db_manager import DatabaseManager


class BaseAI(ABC):
    """Абстрактный базовый класс для AI-провайдеров."""

    def __init__(self):
        self._db: Optional[DatabaseManager] = None
        self._current_chat_id: Optional[int] = None

    def set_db(self, db: DatabaseManager) -> None:
        """Устанавливает менеджер БД для логирования."""
        self._db = db

    def set_chat_id(self, chat_id: int) -> None:
        """Устанавливает текущий chat_id для логирования."""
        self._current_chat_id = chat_id

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def _raw_ask(self, prompt: str) -> str:
        """Непосредственный запрос к API (без логирования)."""
        ...

    def ask(self, prompt: str, prompt_type: str = "general") -> str:
        """Отправляет запрос с логированием в БД."""
        start_time = time.time()
        response = self._raw_ask(prompt)
        duration = time.time() - start_time

        # Логируем в БД
        if self._db:
            self._db.log_request(
                ai_provider=self.name,
                prompt=prompt,
                response=response,
                chat_id=self._current_chat_id,
                prompt_type=prompt_type,
                duration_sec=round(duration, 3),
            )

        return response

    @staticmethod
    def _clean_city_name(raw: str) -> str:
        """Очищает ответ AI от мусора."""
        if not raw:
            return ""

        text = raw.strip().split("\n")[0].strip()
        text = re.sub(r"\s*\(.*?\)", "", text)
        text = re.sub(r"^(город|ответ|city)\s*[:—–-]\s*", "", text, flags=re.IGNORECASE)
        text = text.strip('."\'!?;:,* ')
        text = re.sub(r"^\d+[\.\)]\s*", "", text)

        if not re.match(r"^[а-яА-ЯёЁa-zA-Z\s\-]+$", text):
            match = re.match(r"^([а-яА-ЯёЁa-zA-Z\s\-]+)", text)
            if match:
                text = match.group(1).strip()
            else:
                return ""

        return text.strip()

    def is_valid_city(self, city_name: str) -> bool:
        """Проверяет, является ли строка реальным городом."""
        if not city_name:
            return False

        cleaned = city_name.replace(" ", "").replace("-", "")
        if not cleaned.isalpha():
            return False

        if len(city_name) < 2:
            return False

        response = self.ask(
            f'Город "{city_name}" существует? Ответь ТОЛЬКО одним словом: ДА или НЕТ.',
            prompt_type="city_validation",
        )
        return "ДА" in response.upper() and "НЕТ" not in response.upper()

    def get_city(self, letter: str, used_cities: Set[str], max_attempts: int = 3) -> str:
        """Получает город от AI на указанную букву."""
        used_on_letter = [c for c in used_cities if c[0].lower() == letter.lower()]

        prompt = f'Назови один реальный город мира на букву "{letter.upper()}". '
        if used_on_letter:
            prompt += f"НЕ используй эти города: {', '.join(used_on_letter)}. "
        prompt += (
            "В ответе напиши ТОЛЬКО название города, "
            "без страны, без скобок, без пояснений."
        )

        for attempt in range(max_attempts):
            raw = self.ask(prompt, prompt_type="city_generation").strip()
            city = self._clean_city_name(raw)

            if not city:
                print(f"  ⚠️ Пустой результат после очистки: '{raw}'")
                continue

            city = city.title()
            print(f"  🔍 [{self.name}] Проверяем: {city}")

            if city in used_cities:
                print(f"  ❌ Город {city} уже использован")
                prompt += f" Город {city} уже был, назови другой."
                continue

            if self.is_valid_city(city):
                print(f"  ✅ Город {city} принят")
                return city

            print(f"  ❌ Город {city} не прошёл проверку (попытка {attempt + 1})")

        return ""

    def get_city_info(self, city_name: str) -> str:
        """Возвращает краткую информацию о городе."""
        prompt = (
            f"Расскажи кратко о городе {city_name} в 3-4 предложениях. "
            f"Укажи страну, интересные факты или достопримечательности."
        )
        return self.ask(prompt, prompt_type="city_info")