import re
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Chunk:
    chunk_id: str
    page: int
    text: str

def _clean_text(s: str) -> str:
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def chunk_pages(pages: List[Dict[str, Any]], chunk_size: int = 800, overlap: int = 120) -> List[Chunk]:
    """
    pages: [{ "page": int, "text": str }, ...]
    Splits each page into overlapping character-based chunks.
    Keeps page number for citations later.
    """
    chunks: List[Chunk] = []
    for p in pages:
        page_no = int(p["page"])
        text = _clean_text(p["text"] or "")
        if not text:
            continue

        start = 0
        n = len(text)
        while start < n:
            end = min(start + chunk_size, n)
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"c_{uuid.uuid4().hex[:12]}",
                        page=page_no,
                        text=chunk_text,
                    )
                )

            if end == n:
                break
            start = max(0, end - overlap)

    return chunks
