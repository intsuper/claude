"""Shared data model for a normalized comment from any source."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Comment:
    """A single customer comment, normalized across all sources."""

    source: str  # "facebook" | "gorgias" | "judgeme"
    id: str
    author: str
    text: str
    created_at: str  # ISO-8601 string as returned by the source
    rating: Optional[int] = None  # only Judge.me reviews carry a rating
    url: Optional[str] = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def pretty(self) -> str:
        stars = f" {'★' * self.rating}{'☆' * (5 - self.rating)}" if self.rating else ""
        head = f"[{self.source}]{stars} {self.author} — {self.created_at}"
        body = (self.text or "").strip()
        return f"{head}\n  {body}"
