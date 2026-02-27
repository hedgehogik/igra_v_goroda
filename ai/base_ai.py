"""Базовый класс AI-провайдера с улучшенной очисткой ответов."""

import re
from abc import ABC, abstractmethod
from typing import Set


class BaseAI(ABC):
    """Абстрактный базовый класс для AI-провайдеров."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Название провайдера для отображения."""
        ...

    @abstractmethod
    def ask(self, prompt: str) -> str:
        """Отправляет запрос AI и возвращает текстовый ответ."""
        ...

    @staticmethod
    def _clean_city_name(raw: str) -> str:
        """
        Очищает ответ AI от мусора.
        'Эль-Пасо (США)' → 'Эль-Пасо'
        'Город: Москва.' → 'Москва'
        'Набережные Челны (уже исключён),\nНеаполь...' → 'Набережные Челны'
        """
        if not raw:
            return ""

        # Берём только первую строку (AI иногда выдаёт списки)
        text = raw.strip().split("\n")[0].strip()

        # Убираем скобки и их содержимое: (США), (Россия) и т.д.
        text = re.sub(r"\s*\(.*?\)", "", text)

        # Убираем префиксы вроде "Город:", "Ответ:" и т.д.
        text = re.sub(r"^(город|ответ|city)\s*[:—–-]\s*", "", text, flags=re.IGNORECASE)

        # Убираем точки, кавычки, восклицательные знаки по краям
        text = text.strip('."\'!?;:,* ')

        # Убираем номера списка: "1. Москва" → "Москва"
        text = re.sub(r"^\d+[\.\)]\s*", "", text)

        # Если остались только буквы, пробелы, дефисы — ОК
        # Иначе пробуем извлечь первое «слово-город»
        if not re.match(r"^[а-яА-ЯёЁa-zA-Z\s\-]+$", text):
            # Пытаемся взять первые слова до первого странного символа
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
            f'Город "{city_name}" существует? Ответь ТОЛЬКО одним словом: ДА или НЕТ.'
        )
        return "ДА" in response.upper() and "НЕТ" not in response.upper()

    def get_city(self, letter: str, used_cities: Set[str], max_attempts: int = 3) -> str:
        """Получает город от AI на указанную букву."""
        used_on_letter = [c for c in used_cities if c[0].lower() == letter.lower()]

        prompt = (
            f'Назови один реальный город мира на букву "{letter.upper()}". '
        )
        if used_on_letter:
            prompt += f"НЕ используй эти города: {', '.join(used_on_letter)}. "
        prompt += (
            "В ответе напиши ТОЛЬКО название города, "
            "без страны, без скобок, без пояснений. "
            "Одно слово или словосочетание."
        )

        for attempt in range(max_attempts):
            raw = self.ask(prompt).strip()
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
        return self.ask(prompt)