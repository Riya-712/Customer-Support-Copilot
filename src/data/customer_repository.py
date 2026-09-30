import json
from src.config import project_path

class CustomerRepository:
    def __init__(self):
        self.rows={x["customer_id"]:x for x in json.loads(project_path("data/customers.json").read_text())}
    def get_customer(self, customer_id): return self.rows.get(customer_id)
