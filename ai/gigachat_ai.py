"""AI-провайдер GigaChat."""

from langchain.chat_models.gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from .base_ai import BaseAI


class GigaChatAI(BaseAI):
    """Провайдер GigaChat."""

    def __init__(self, credentials: str):
        super().__init__()
        self._llm = GigaChat(
            credentials=credentials,
            verify_ssl_certs=False,
            temperature=0.7,
            max_tokens=200,
        )

    @property
    def name(self) -> str:
        return "GigaChat"

    def _raw_ask(self, prompt: str) -> str:
        try:
            messages = [
                SystemMessage(
                    content=(
                        "Ты помощник для игры в города. "
                        "Отвечай кратко и точно. "
                        "Когда просят назвать город — пиши ТОЛЬКО название."
                    )
                ),
                HumanMessage(content=prompt),
            ]
            response = self._llm.invoke(messages)
            result = response.content.strip()
            preview = result[:80].replace("\n", " ")
            print(f"  🤖 [{self.name}] → {preview}...")
            return result
        except Exception as e:
            print(f"  ❌ [{self.name}] Ошибка: {e}")
            return ""
