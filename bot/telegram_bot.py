"""Telegram-бот: обработчики команд и сообщений."""

import telebot
from telebot.types import BotCommand

from audio.audio_processor import AudioProcessor
from game.game_manager import GameManager
from .keyboards import model_selection_keyboard, city_info_keyboard


HELP_TEXT = (
    "🏙️ *Бот «Города» с AI*\n\n"
    "*Команды:*\n"
    "/start — начать новую игру\n"
    "/stop — остановить игру\n"
    "/model — выбрать AI-модель\n"
    "/voice — голосовые ответы\n"
    "/text — текстовые ответы\n"
    "/stats — статистика запросов\n"
    "/help — эта справка\n\n"
    "*Как играть:*\n"
    "Напиши или произнеси название города.\n"
    "AI ответит городом на последнюю букву.\n"
    "Побеждает тот, чей соперник не сможет ответить!"
)


class TelegramBot:
    """Основной класс Telegram-бота."""

    def __init__(self, token: str, game_manager: GameManager, audio_processor: AudioProcessor):
        self.bot = telebot.TeleBot(token, parse_mode="Markdown")
        self.gm = game_manager
        self.audio = audio_processor
        self._voice_modes: dict[int, bool] = {}
        self._setup_commands()
        self._register_handlers()

    def _setup_commands(self):
        """Регистрирует команды в меню Telegram."""
        commands = [
            BotCommand("start", "Начать новую игру"),
            BotCommand("stop", "Остановить игру"),
            BotCommand("model", "Выбрать AI-модель"),
            BotCommand("voice", "Голосовые ответы"),
            BotCommand("text", "Текстовые ответы"),
            BotCommand("stats", "Статистика запросов к AI"),
            BotCommand("help", "Справка"),
        ]
        self.bot.set_my_commands(commands)
        print("✅ Команды меню зарегистрированы")

    def _is_voice_mode(self, chat_id: int) -> bool:
        return self._voice_modes.get(chat_id, False)

    def _send_voice_and_text(self, chat_id: int, text: str, voice_text: str | None = None):
        audio_path = self.audio.text_to_speech(voice_text or text)
        if audio_path:
            try:
                with open(audio_path, "rb") as f:
                    self.bot.send_voice(chat_id, f)
            finally:
                self.audio.cleanup(audio_path)
        self.bot.send_message(chat_id, text)

    def _register_handlers(self):

        @self.bot.message_handler(commands=["start"])
        def cmd_start(m):
            msg = self.gm.start_game(m.chat.id)
            self.bot.send_message(m.chat.id, msg)

        @self.bot.message_handler(commands=["stop"])
        def cmd_stop(m):
            msg = self.gm.stop_game(m.chat.id)
            self.bot.send_message(m.chat.id, msg)

        @self.bot.message_handler(commands=["model"])
        def cmd_model(m):
            current = self.gm.get_ai_name(m.chat.id)
            self.bot.send_message(
                m.chat.id,
                f"Текущая модель: *{current}*\n\nВыбери модель:",
                reply_markup=model_selection_keyboard(),
            )

        @self.bot.message_handler(commands=["voice"])
        def cmd_voice(m):
            self._voice_modes[m.chat.id] = True
            self.bot.send_message(m.chat.id, "🔊 Голосовые ответы включены")

        @self.bot.message_handler(commands=["text"])
        def cmd_text(m):
            self._voice_modes[m.chat.id] = False
            self.bot.send_message(m.chat.id, "📝 Текстовые ответы включены")

        @self.bot.message_handler(commands=["stats"])
        def cmd_stats(m):
            stats = self.gm.get_db_stats()
            self.bot.send_message(m.chat.id, stats)

        @self.bot.message_handler(commands=["help"])
        def cmd_help(m):
            self.bot.send_message(m.chat.id, HELP_TEXT)

        @self.bot.message_handler(content_types=["voice"])
        def on_voice(m):
            if not self.gm.game_exists(m.chat.id):
                self.bot.send_message(m.chat.id, "❌ Игра не начата. Нажми /start")
                return

            file_info = self.bot.get_file(m.voice.file_id)
            file_url = (
                f"https://api.telegram.org/file/bot{self.bot.token}/{file_info.file_path}"
            )
            self.bot.send_message(m.chat.id, "🎤 Распознаю голос...")

            recognized = self.audio.speech_to_text(file_url)

            if recognized.startswith("⚠️"):
                self.bot.send_message(m.chat.id, recognized)
                return

            self.bot.send_message(m.chat.id, f'Распознано: *"{recognized}"*')
            self._handle_city_input(m.chat.id, recognized, is_voice=True)

        @self.bot.message_handler(func=lambda m: True)
        def on_text(m):
            if not self.gm.game_exists(m.chat.id):
                self.bot.send_message(
                    m.chat.id,
                    "👋 Привет! Нажми /start чтобы начать игру в города.\n"
                    "Нажми /help для справки."
                )
                return
            self._handle_city_input(m.chat.id, m.text, is_voice=False)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("model_"))
        def on_model_select(call):
            ai_key = call.data.replace("model_", "")
            result = self.gm.set_ai(call.message.chat.id, ai_key)
            self.bot.answer_callback_query(call.id, "✅ Модель обновлена")
            self.bot.edit_message_text(
                result,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
        def on_city_info(call):
            city_name = call.data.replace("info_", "")
            self.bot.answer_callback_query(call.id, "⏳ Загружаю...")
            info = self.gm.get_city_info(call.message.chat.id, city_name)
            self.bot.send_message(
                call.message.chat.id,
                f"🏙️ *{city_name}*\n\n{info}",
            )

    def _handle_city_input(self, chat_id: int, city_text: str, is_voice: bool = False):
        self.bot.send_chat_action(chat_id, "typing")

        result = self.gm.process_city(chat_id, city_text)

        if "error" in result:
            self.bot.send_message(chat_id, f"❌ {result['error']}")
            return

        if "winner" in result:
            self.bot.send_message(chat_id, f"🎉 {result['message']}")
            self.gm.stop_game(chat_id)
            return

        response_text = result["text_response"]
        ai_city = result["ai_city"]
        use_voice = self._is_voice_mode(chat_id) or is_voice

        if use_voice:
            self._send_voice_and_text(chat_id, response_text, voice_text=ai_city)
        else:
            self.bot.send_message(chat_id, response_text)

        self.bot.send_message(
            chat_id,
            "👇",
            reply_markup=city_info_keyboard(ai_city),
        )

    def run(self):
        print("🚀 Бот запущен и готов к работе!")
        print("   Нажмите Ctrl+C для остановки.\n")
        self.bot.infinity_polling(timeout=60, long_polling_timeout=60)