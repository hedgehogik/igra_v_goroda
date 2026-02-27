"""Логика игры в города."""

from typing import Callable, Dict, Any, Set
from config import Config


class CitiesGame:
    """Одна игровая сессия."""

    def __init__(self):
        self.last_city: str | None = None
        self.used_cities: Set[str] = set()
        self.move_count: int = 0

    @staticmethod
    def last_letter(city: str) -> str:
        """Определяет последнюю «игровую» букву."""
        for ch in reversed(city.lower()):
            if ch not in Config.SKIP_LETTERS:
                return ch
        return city[-1].lower()

    def process_turn(
        self,
        city_input: str,
        is_valid_city: Callable[[str], bool],
        get_ai_city: Callable[[str, Set[str]], str],
    ) -> Dict[str, Any]:
        """Обрабатывает ход пользователя и делает ответный ход AI."""
        city = city_input.strip().title()

        if not city or not city.replace(" ", "").replace("-", "").isalpha():
            return {"error": "Не распознано название города. Попробуй ещё раз!"}

        if not is_valid_city(city):
            return {"error": f'"{city}" — не существует или это не город!'}

        if self.last_city and city[0].lower() != self.last_letter(self.last_city):
            expected = self.last_letter(self.last_city).upper()
            return {"error": f"Нужен город на букву «{expected}»!"}

        if city in self.used_cities:
            return {"error": f"Город «{city}» уже был!"}

        self.used_cities.add(city)
        self.last_city = city
        self.move_count += 1
        next_letter = self.last_letter(city)

        ai_city = get_ai_city(next_letter, self.used_cities)

        if not ai_city:
            return {
                "winner": True,
                "message": f"Ты выиграл! AI сдался после {self.move_count} ходов. 🎉",
            }

        self.used_cities.add(ai_city)
        self.last_city = ai_city
        self.move_count += 1
        next_user_letter = self.last_letter(ai_city)

        return {
            "success": True,
            "user_city": city,
            "ai_city": ai_city,
            "next_letter": next_user_letter,
            "move_count": self.move_count,
            "text_response": (
                f"🤖 {ai_city}\n\n"
                f"Твой ход — город на «{next_user_letter.upper()}»:"
            ),
        }