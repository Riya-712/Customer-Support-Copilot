import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.ingest import ingest_knowledge, ingest_tickets
print(f'Knowledge chunks indexed: {ingest_knowledge()}')
print(f'Training tickets indexed: {ingest_tickets()}')
