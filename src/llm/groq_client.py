import json
import logging
import time
from dataclasses import dataclass
from src.config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class LLMResult:
    data: dict
    latency_ms: float
    model: str

class GroqClient:
    def __init__(self):
        settings = get_settings()
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured. Add it to .env.")
        from groq import Groq
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.temperature = settings.temperature

    def complete_json(self, system_prompt: str, user_prompt: str) -> LLMResult:
        started = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return LLMResult(data=data, latency_ms=(time.perf_counter()-started)*1000, model=self.model)
        except Exception:
            logger.exception("Groq request failed")
            raise
