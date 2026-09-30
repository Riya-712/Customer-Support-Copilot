from src.data.customer_repository import CustomerRepository
from src.data.order_repository import OrderRepository
from src.data.ticket_repository import TicketRepository

class CustomerContextService:
    def __init__(self): self.customers=CustomerRepository(); self.orders=OrderRepository(); self.tickets=TicketRepository()
    def get_context(self, ticket: dict) -> dict:
        customer=self.customers.get_customer(ticket.get("customer_id"))
        if not customer: return {"customer":None,"relevant_order":None,"recent_orders":[],"previous_tickets":[]}
        order=self.orders.get_order(ticket.get("order_id")) if ticket.get("order_id") else None
        recent=self.orders.get_customer_orders(customer["customer_id"])[:5]
        previous=[t for t in self.tickets.get_customer_tickets(customer["customer_id"], limit=6) if t["ticket_id"]!=ticket["ticket_id"]][:5]
        # Minimal fields only; evaluation labels are deliberately excluded.
        safe_customer={k:customer[k] for k in ["customer_id","name","city","loyalty_tier","signup_date","preferred_categories"]}
        safe_orders=[{k:o[k] for k in ["order_id","order_date","status","total_amount","payment_method","promised_delivery_date","shipping_city"]} for o in recent]
        safe_previous=[{k:t[k] for k in ["ticket_id","created_at","subject","category","message"]} for t in previous]
        return {"customer":safe_customer,"relevant_order":order,"recent_orders":safe_orders,"previous_tickets":safe_previous}
