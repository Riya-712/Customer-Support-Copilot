import time, logging
from dataclasses import dataclass
from src.support.intent_classifier import IntentClassifier
from src.support.summarizer import TicketSummarizer
from src.support.customer_context import CustomerContextService
from src.support.response_generator import ResponseGenerator
from src.support.recommendation_engine import RecommendationEngine
from src.rag.retriever import ChromaRetriever

logger=logging.getLogger(__name__)
@dataclass
class TicketAnalysisResult:
    ticket_analysis: object
    customer_context: dict
    intent: object
    similar_tickets: list
    knowledge: list
    response: object
    recommendation: object
    latency_ms: float
    llm_model: str
    embedding_model: str
    errors: list

class TicketAnalyzer:
    def __init__(self):
        self.retriever=ChromaRetriever(); self.context=CustomerContextService(); self.intent=IntentClassifier(); self.summarizer=TicketSummarizer(); self.responses=ResponseGenerator(); self.recommendations=RecommendationEngine()
    def analyze(self,ticket):
        ticket={k:v for k,v in ticket.items() if not k.startswith("ground_truth_") and k not in {"historical_summary","historical_resolution","queue_intent"}}
        started=time.perf_counter(); errors=[]
        ctx=self.context.get_context(ticket)
        query=f"{ticket.get('subject','')}\n{ticket.get('message','')}"
        kb=self.retriever.search_knowledge_base(query)
        similar=[r for r in self.retriever.search_similar_tickets(query, self.retriever.top_k+1) if r["metadata"].get("ticket_id") != ticket.get("ticket_id")][:self.retriever.top_k]
        try: intent=self.intent.classify(ticket)
        except Exception as e: logger.exception('Intent classification failed'); errors.append(str(e)); intent=None
        try: summary=self.summarizer.analyze(ticket)
        except Exception as e: logger.exception('Summarization failed'); errors.append(str(e)); summary=None
        response=None
        if intent and kb:
            try: response=self.responses.generate(ticket,ctx,kb,similar,intent.intent)
            except Exception as e: logger.exception('Response generation failed'); errors.append(str(e))
        if response is None:
            from src.support.response_generator import ResponseResult
            response=ResponseResult(summary=summary.summary if summary else "",suggested_response="Insufficient information — manual review recommended.",recommended_action="manual_review",required_verification=["review ticket and applicable policy"],grounding_notes="No sufficiently grounded response could be generated.",citations=[])
        recommendation=self.recommendations.recommend(intent.intent if intent else "other",bool(kb),bool(ctx.get('customer')))
        return TicketAnalysisResult(summary,ctx,intent,similar,kb,response,recommendation,(time.perf_counter()-started)*1000,getattr(self.intent.llm,'model','unknown'),self.retriever.embedding.model_name,errors)
