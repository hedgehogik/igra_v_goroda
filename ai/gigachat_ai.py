"""AI-провайдер на основе GigaChat (Сбер)."""

from gigachat import GigaChat
from .base_ai import BaseAI


class GigaChatAI(BaseAI):
    """Провайдер GigaChat."""

    def __init__(self, credentials: str):
        self._client = GigaChat(credentials=credentials, verify_ssl_certs=False)

    @property
    def name(self) -> str:
        return "GigaChat"

    def ask(self, prompt: str) -> str:
        try:
            response = self._client.chat(prompt)
            result = response.choices[0].message.content
            preview = result[:80].replace("\n", " ")
            print(f"  🤖 [{self.name}] → {preview}...")
            return result
        except Exception as e:
            print(f"  ❌ [{self.name}] Ошибка: {e}")
            return ""