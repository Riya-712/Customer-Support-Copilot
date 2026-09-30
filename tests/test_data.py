import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_dataset_counts():
    assert len(json.loads((ROOT/"data/customers.json").read_text())) == 500
    assert len(json.loads((ROOT/"data/orders.json").read_text())) == 1500
    assert len(json.loads((ROOT/"data/products.json").read_text())) == 300
    assert len(json.loads((ROOT/"data/tickets.json").read_text())) == 1000

def test_ticket_has_eval_labels():
    tickets = json.loads((ROOT/"data/tickets.json").read_text())
    assert all("ground_truth_intent" in t for t in tickets)

def test_inference_loader_excludes_eval_labels():
    from src.data.ticket_repository import TicketRepository
    t = json.loads((ROOT/"data/tickets.json").read_text())[0]
    clean = TicketRepository.for_inference(t)
    assert not any(k.startswith("ground_truth_") for k in clean)
