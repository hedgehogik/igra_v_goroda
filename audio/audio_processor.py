"""Распознавание речи и синтез голоса."""

import io
import os
import tempfile

import gtts
import requests
import speech_recognition as sr
from pydub import AudioSegment


class AudioProcessor:
    """Обработка голосовых сообщений."""

    def __init__(self):
        self._recognizer = sr.Recognizer()

    def speech_to_text(self, voice_file_url: str) -> str:
        """Конвертирует голосовое сообщение (OGG) в текст."""
        try:
            response = requests.get(voice_file_url, timeout=30)
            response.raise_for_status()

            audio_segment = AudioSegment.from_ogg(io.BytesIO(response.content))
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)

            with sr.AudioFile(wav_io) as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.record(source)

            text = self._recognizer.recognize_google(audio, language="ru-RU")
            print(f"  🎤 Распознано: {text}")
            return text

        except sr.UnknownValueError:
            return "⚠️ Не удалось распознать речь"
        except sr.RequestError as e:
            return f"⚠️ Ошибка сервиса распознавания: {e}"
        except Exception as e:
            return f"⚠️ Ошибка обработки аудио: {e}"

    @staticmethod
    def text_to_speech(text: str, lang: str = "ru") -> str | None:
        """Конвертирует текст в MP3 и возвращает путь к файлу."""
        try:
            tts = gtts.gTTS(text=text, lang=lang, slow=False)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tmp.name)
            tmp.close()
            return tmp.name
        except Exception as e:
            print(f"  ❌ Ошибка синтеза речи: {e}")
            return None

    @staticmethod
    def cleanup(file_path: str | None) -> None:
        """Удаляет временный файл."""
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass