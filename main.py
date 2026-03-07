"""Точка входа — запуск бота."""

from config import Config
from database.db_manager import DatabaseManager
from game.game_manager import GameManager
from audio.audio_processor import AudioProcessor
from bot.telegram_bot import TelegramBot


def main():
    Config.validate()
    print("✅ Конфигурация проверена")

    # Инициализация БД
    db = DatabaseManager(Config.DATABASE_URL)

    # Инициализация компонентов
    game_manager = GameManager(db)
    audio_processor = AudioProcessor()

    print("✅ GameManager создан")
    print("✅ AudioProcessor создан")

    # Запуск бота
    bot = TelegramBot(
        token=Config.TELEGRAM_BOT_TOKEN,
        game_manager=game_manager,
        audio_processor=audio_processor,
    )

    bot.run()


if __name__ == "__main__":
    main()