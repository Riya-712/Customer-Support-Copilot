import json
from src.config import project_path

class TicketRepository:
    def __init__(self): self.rows=json.loads(project_path("data/tickets.json").read_text())
    def get_ticket(self, ticket_id): return next((x for x in self.rows if x["ticket_id"]==ticket_id), None)
    def get_customer_tickets(self, customer_id, limit=5):
        rows=[x for x in self.rows if x["customer_id"]==customer_id]
        return sorted(rows,key=lambda x:x["created_at"], reverse=True)[:limit]
    def all_tickets(self): return self.rows
    @staticmethod
    def for_inference(ticket):
        excluded={k for k in ticket if k.startswith("ground_truth_")} | {"historical_summary","historical_resolution","queue_intent"}
        return {k:v for k,v in ticket.items() if k not in excluded}
