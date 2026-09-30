from dataclasses import dataclass
import re

@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict

def chunk_markdown(text: str, metadata: dict, chunk_size: int = 900, overlap: int = 120) -> list[Chunk]:
    clean = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(clean) <= chunk_size:
        return [Chunk(f"{metadata['document_id']}-0", clean, metadata)]
    chunks, start, index = [], 0, 0
    while start < len(clean):
        end = min(len(clean), start + chunk_size)
        if end < len(clean):
            boundary = clean.rfind("\n", start + chunk_size//2, end)
            if boundary > start:
                end = boundary
        piece = clean[start:end].strip()
        if piece:
            chunks.append(Chunk(f"{metadata['document_id']}-{index}", piece, metadata))
            index += 1
        if end >= len(clean): break
        start = max(end - overlap, start + 1)
    return chunks
