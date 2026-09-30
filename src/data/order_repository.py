import json
from src.config import project_path

class OrderRepository:
    def __init__(self):
        self.rows=json.loads(project_path("data/orders.json").read_text())
        self.by_id={x["order_id"]:x for x in self.rows}
    def get_order(self, order_id): return self.by_id.get(order_id)
    def get_customer_orders(self, customer_id): return sorted([x for x in self.rows if x["customer_id"]==customer_id], key=lambda x:x["order_date"], reverse=True)
