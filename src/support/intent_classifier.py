from pydantic import BaseModel, Field
from src.llm.groq_client import GroqClient
from src.llm.prompts import SYSTEM_PROMPT, INTENT_PROMPT, INTENT_TAXONOMY

class IntentResult(BaseModel):
    intent: str
    confidence: float = Field(ge=0, le=1)
    reason: str

class IntentClassifier:
    def __init__(self, llm=None): self.llm=llm or GroqClient()
    def classify(self, ticket: dict) -> IntentResult:
        prompt=INTENT_PROMPT.format(taxonomy=", ".join(INTENT_TAXONOMY)) + f"\nTicket:\n{ticket.get('subject','')}\n{ticket.get('message','')}"
        result=self.llm.complete_json(SYSTEM_PROMPT,prompt)
        parsed=IntentResult.model_validate(result.data)
        if parsed.intent not in INTENT_TAXONOMY: parsed.intent="other"
        return parsed
