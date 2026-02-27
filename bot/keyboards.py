"""Клавиатуры и кнопки."""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from game.game_manager import AI_DISPLAY_NAMES


def model_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора AI-модели."""
    kb = InlineKeyboardMarkup(row_width=1)
    for key, display in AI_DISPLAY_NAMES.items():
        kb.add(InlineKeyboardButton(f"🤖 {display}", callback_data=f"model_{key}"))
    return kb


def city_info_keyboard(city_name: str) -> InlineKeyboardMarkup:
    """Кнопка «Информация о городе»."""
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            f"ℹ️ О городе {city_name}",
            callback_data=f"info_{city_name}",
        )
    )
    return kb