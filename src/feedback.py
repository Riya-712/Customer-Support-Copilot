import json
from datetime import datetime, timezone
from pydantic import BaseModel
from src.config import project_path
class Feedback(BaseModel):
    ticket_id:str; helpful:bool; reason:str|None=None; comment:str|None=None; response_accepted:bool|None=None; created_at:str|None=None

def save_feedback(feedback:Feedback):
    feedback.created_at=feedback.created_at or datetime.now(timezone.utc).isoformat()
    p=project_path('data/feedback.jsonl'); p.parent.mkdir(exist_ok=True)
    with p.open('a',encoding='utf-8') as f: f.write(feedback.model_dump_json()+'\n')

def load_feedback():
    p=project_path('data/feedback.jsonl')
    if not p.exists(): return []
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
