import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_evaluation_split_is_held_out():
    tickets=json.loads((ROOT/'data/tickets.json').read_text())
    ev=json.loads((ROOT/'data/evaluation_tickets.json').read_text())
    assert len(ev)>=20
    assert {x['ticket_id'] for x in ev}.isdisjoint({x['ticket_id'] for x in tickets[:-20]})
    assert [x['ticket_id'] for x in ev]==[x['ticket_id'] for x in tickets[-20:]]

def test_knowledge_documents_have_metadata():
    docs=list((ROOT/'data/knowledge_base').glob('*.md'))
    assert len(docs)>=20
    for p in docs:
        text=p.read_text()
        assert text.startswith('---')
        for field in ['document_id','category','product_category','version','effective_date']:
            assert f'{field}:' in text
