from pydantic import BaseModel
from src.llm.groq_client import GroqClient
from src.llm.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT, INTENT_TAXONOMY

class TicketAnalysis(BaseModel):
    summary: str
    customer_issue: str
    requested_outcome: str
    important_details: list[str]
    intent: str
    confidence: float

class TicketSummarizer:
    def __init__(self,llm=None): self.llm=llm or GroqClient()
    def analyze(self,ticket:dict)->TicketAnalysis:
        prompt=ANALYSIS_PROMPT+f"\nAllowed intents: {', '.join(INTENT_TAXONOMY)}\nTicket:\n{ticket.get('subject','')}\n{ticket.get('message','')}"
        result=self.llm.complete_json(SYSTEM_PROMPT,prompt)
        return TicketAnalysis.model_validate(result.data)
