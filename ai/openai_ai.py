"""AI-провайдер на основе OpenAI-совместимого API (VseGPT)."""

from openai import OpenAI
from .base_ai import BaseAI


class OpenAICompatibleAI(BaseAI):
    """Провайдер для OpenAI-совместимых API (VseGPT и т.д.)."""

    def __init__(self, api_key: str, base_url: str, model: str = "openai/gpt-4o-mini"):
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    @property
    def name(self) -> str:
        return "GPT-4o"

    def ask(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты помощник для игры в города. "
                            "Отвечай кратко и точно. "
                            "Когда тебя просят назвать город — пиши ТОЛЬКО название, "
                            "без страны, без скобок, без пояснений."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=200,
            )
            result = response.choices[0].message.content.strip()
            preview = result[:80].replace("\n", " ")
            print(f"  🤖 [{self.name}] → {preview}...")
            return result
        except Exception as e:
            print(f"  ❌ [{self.name}] Ошибка: {e}")
            return ""
