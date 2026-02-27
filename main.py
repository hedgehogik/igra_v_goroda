"""Точка входа — запуск бота."""

from config import Config
from game.game_manager import GameManager
from audio.audio_processor import AudioProcessor
from bot.telegram_bot import TelegramBot


def main():
    Config.validate()
    print("✅ Конфигурация проверена")

    game_manager = GameManager()
    audio_processor = AudioProcessor()

    print("✅ GameManager создан")
    print("✅ AudioProcessor создан")

    bot = TelegramBot(
        token=Config.TELEGRAM_BOT_TOKEN,
        game_manager=game_manager,
        audio_processor=audio_processor,
    )

    bot.run()


if __name__ == "__main__":
    main()