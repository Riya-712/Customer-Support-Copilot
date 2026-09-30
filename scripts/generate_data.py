"""Validate the generated NovaMart data and create a held-out evaluation split.
The 20 held-out tickets are never indexed into the support_tickets Chroma collection.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=ROOT/'data'
tickets=json.loads((data/'tickets.json').read_text())
assert len(tickets)==1000
held_out=tickets[-20:]
(data/'evaluation_tickets.json').write_text(json.dumps(held_out,indent=2))
print(f"Validated {len(tickets)} tickets and created {len(held_out)} held-out evaluation tickets.")
