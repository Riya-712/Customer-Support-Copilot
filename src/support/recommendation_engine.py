from pydantic import BaseModel, Field

class Recommendation(BaseModel):
    action:str
    reason:str
    required_verification:list[str]=[]
    confidence:float=Field(ge=0,le=1)

class RecommendationEngine:
    def recommend(self,intent,knowledge_available,context_available=True):
        if not context_available: return Recommendation(action="manual_review",reason="Customer or order context could not be verified.",required_verification=["customer identity/order reference"],confidence=.98)
        if not knowledge_available: return Recommendation(action="manual_review",reason="No authoritative knowledge was retrieved for the case.",required_verification=["applicable NovaMart policy"],confidence=.95)
        mapping={"return_request":"approve_return","refund_request":"verify_refund_status","delivery_delay":"provide_tracking_information","order_tracking":"provide_tracking_information","payment_failure":"escalate_to_billing","duplicate_charge":"escalate_to_billing","damaged_item":"request_more_information","wrong_item":"request_more_information","warranty":"escalate_to_technical_support","account_issue":"escalate_to_technical_support","shipping_question":"explain_policy","coupon_issue":"explain_policy","exchange_request":"explain_policy","order_cancellation":"explain_policy","product_question":"explain_policy"}
        action=mapping.get(intent,"manual_review")
        return Recommendation(action=action,reason=f"Recommended from verified intent '{intent}' and retrieved policy evidence.",required_verification=[],confidence=.8)
