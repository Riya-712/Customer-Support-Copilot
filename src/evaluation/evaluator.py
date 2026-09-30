import json, logging
from src.config import project_path
from src.data.ticket_repository import TicketRepository
from src.support.ticket_analyzer import TicketAnalyzer
from src.evaluation.metrics import accuracy, macro_f1, recall_at_k, precision_at_k, reciprocal_rank, mean

logger=logging.getLogger(__name__)
RELEVANT_KB_CATEGORIES={
    'return_request':{'Returns'}, 'refund_request':{'Refunds'}, 'delivery_delay':{'Shipping'}, 'order_tracking':{'Shipping'},
    'missing_delivery':{'Shipping'}, 'damaged_item':{'Returns'}, 'wrong_item':{'Returns'}, 'exchange_request':{'Exchanges'},
    'order_cancellation':{'Cancellations'}, 'payment_failure':{'Payments'}, 'duplicate_charge':{'Payments'}, 'coupon_issue':{'Loyalty'},
    'warranty':{'Warranty'}, 'product_question':{'Product'}, 'account_issue':{'Account'}, 'shipping_question':{'Shipping'}, 'other':set()
}
class Evaluator:
    def __init__(self): self.repo=TicketRepository()
    def held_out_tickets(self):
        p=project_path('data/evaluation_tickets.json')
        return json.loads(p.read_text()) if p.exists() else []
    def run(self, limit=None):
        rows=self.held_out_tickets()[:limit] if limit else self.held_out_tickets(); analyzer=TicketAnalyzer(); results=[]
        for ticket in rows:
            try:
                from src.data.ticket_repository import TicketRepository
                clean=TicketRepository.for_inference(ticket)
                r=analyzer.analyze(clean)
                kb_relevant=RELEVANT_KB_CATEGORIES.get(ticket['ground_truth_intent'],set())
                relevant_ids=[x['id'] for x in r.knowledge if x['metadata'].get('category') in kb_relevant]
                retrieved_ids=[x['id'] for x in r.knowledge]
                results.append({
                    'ticket_id':ticket['ticket_id'],'true_intent':ticket['ground_truth_intent'],'pred_intent':r.intent.intent if r.intent else 'other',
                    'similar_ids':[x['id'] for x in r.similar_tickets], 'kb_ids':retrieved_ids,
                    'kb_relevant_hits':relevant_ids,'recommended_action':r.recommendation.action,'ground_truth_action':ticket.get('ground_truth_action','manual_review'),
                    'grounded':bool(r.response.citations),'citation_correct':all(any(c.source_id==x['id'] for x in r.knowledge) for c in r.response.citations),
                    'latency_ms':r.latency_ms,'errors':r.errors
                })
            except Exception as e:
                logger.exception('Evaluation ticket failed'); results.append({'ticket_id':ticket['ticket_id'],'error':str(e)})
        valid=[x for x in results if 'true_intent' in x]
        ytrue=[x['true_intent'] for x in valid]; ypred=[x['pred_intent'] for x in valid]
        recall=[recall_at_k(x['kb_relevant_hits'],x['kb_ids'],5) for x in valid]
        precision=[precision_at_k(x['kb_relevant_hits'],x['kb_ids'],5) for x in valid]
        mrr=[reciprocal_rank(x['kb_relevant_hits'],x['kb_ids']) for x in valid]
        return {
            'n':len(valid),'intent_accuracy':accuracy(ytrue,ypred),'intent_macro_f1':macro_f1(ytrue,ypred),
            'retrieval_recall_at_5':mean(recall),'retrieval_precision_at_5':mean(precision),'retrieval_mrr':mean(mrr),
            'groundedness_rate':mean([x['grounded'] for x in valid]),'citation_correctness':mean([x['citation_correct'] for x in valid]),
            'recommendation_agreement':mean([x['recommended_action']==x['ground_truth_action'] for x in valid]),'results':results
        }
