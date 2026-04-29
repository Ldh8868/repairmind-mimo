from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class KnowledgeChunk:
    source: str
    title: str
    content: str
    score: float = 0.0


def _tokenize(text: str) -> set[str]:
    text = text.lower()
    english = re.findall(r"[a-z0-9_+-]{2,}", text)
    chinese = re.findall(r"[\u4e00-\u9fff]", text)
    return set(english + chinese)


class KnowledgeBase:
    """A tiny local knowledge base.

    For the first GitHub demo this avoids external infrastructure.
    It can later be replaced by a vector database without changing API routes.
    """

    def __init__(self, manuals_dir: Path | None = None) -> None:
        self.manuals_dir = manuals_dir or Path(__file__).resolve().parents[1] / "data" / "manuals"
        self.chunks = self._load_chunks(self.manuals_dir)

    def _load_chunks(self, manuals_dir: Path) -> List[KnowledgeChunk]:
        chunks: List[KnowledgeChunk] = []
        for file_path in sorted(manuals_dir.glob("*.md")):
            raw = file_path.read_text(encoding="utf-8")
            sections = re.split(r"\n(?=## )", raw)
            for idx, section in enumerate(sections):
                title_match = re.search(r"^#+\s+(.+)$", section.strip(), flags=re.MULTILINE)
                title = title_match.group(1).strip() if title_match else f"Section {idx + 1}"
                chunks.append(KnowledgeChunk(source=file_path.name, title=title, content=section.strip()))
        return chunks

    def search(self, query: str, category: str = "other", limit: int = 4) -> List[KnowledgeChunk]:
        query_tokens = _tokenize(f"{category} {query}")
        scored: List[KnowledgeChunk] = []
        for chunk in self.chunks:
            chunk_tokens = _tokenize(f"{chunk.title} {chunk.content}")
            if not chunk_tokens:
                continue
            overlap = len(query_tokens & chunk_tokens)
            category_bonus = 2 if category in chunk.source else 0
            safety_bonus = 1 if "安全" in chunk.content or "risk" in chunk.content.lower() else 0
            score = overlap + category_bonus + safety_bonus
            if score > 0:
                scored.append(KnowledgeChunk(chunk.source, chunk.title, chunk.content, float(score)))
        return sorted(scored, key=lambda c: c.score, reverse=True)[:limit]

    def list_sources(self) -> List[str]:
        return sorted({chunk.source for chunk in self.chunks})

    def format_chunks(self, chunks: Iterable[KnowledgeChunk]) -> str:
        blocks = []
        for chunk in chunks:
            blocks.append(f"[source={chunk.source} title={chunk.title}]\n{chunk.content}")
        return "\n\n---\n\n".join(blocks)
