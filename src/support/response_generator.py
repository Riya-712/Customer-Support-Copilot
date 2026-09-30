from pydantic import BaseModel, Field
from src.llm.groq_client import GroqClient
from src.llm.prompts import SYSTEM_PROMPT, RESPONSE_PROMPT

ACTIONS=["request_more_information","provide_tracking_information","explain_policy","approve_return","verify_refund_status","escalate_to_billing","escalate_to_technical_support","escalate_to_manager","no_action_required","manual_review"]
class Citation(BaseModel): source_id:str; title:str; excerpt:str
class ResponseResult(BaseModel):
    summary:str
    suggested_response:str
    recommended_action:str
    required_verification:list[str]=[]
    grounding_notes:str
    citations:list[Citation]=[]

class ResponseGenerator:
    def __init__(self,llm=None): self.llm=llm or GroqClient()
    def generate(self,ticket,context,knowledge,similar,intent)->ResponseResult:
        prompt=RESPONSE_PROMPT+f"\nAllowed actions: {', '.join(ACTIONS)}\nIntent: {intent}\nVERIFIED CONTEXT:\n{context}\nKNOWLEDGE (authoritative):\n{knowledge}\nSIMILAR TICKETS (non-authoritative examples):\n{similar}\nTICKET:\n{ticket}"
        result=self.llm.complete_json(SYSTEM_PROMPT,prompt)
        parsed=ResponseResult.model_validate(result.data)
        if parsed.recommended_action not in ACTIONS: parsed.recommended_action="manual_review"
        allowed={r["id"]:r for r in knowledge}
        safe=[]
        for c in parsed.citations:
            source=allowed.get(c.source_id)
            if source:
                safe.append(Citation(source_id=c.source_id,title=str(source["metadata"].get("title",source["metadata"].get("document_id",c.source_id))),excerpt=source["document"][:500]))
        parsed.citations=safe
        if not parsed.citations:
            parsed.suggested_response="Insufficient information — manual review recommended."
            parsed.recommended_action="manual_review"
            parsed.grounding_notes="No valid knowledge-base citation was produced; response downgraded to manual review."
        return parsed
