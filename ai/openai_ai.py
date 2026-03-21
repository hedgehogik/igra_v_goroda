"""AI-провайдер OpenAI-совместимый."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .base_ai import BaseAI


class OpenAICompatibleAI(BaseAI):
    """Провайдер для VseGPT и совместимых API."""

    def __init__(self, api_key: str, base_url: str, model: str = "openai/gpt-4o-mini"):
        super().__init__()
        self._llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.7,
            max_tokens=200,
        )
        self._model = model

    @property
    def name(self) -> str:
        return "GPT-4o"

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
