"""Fetch product reviews from Judge.me.

Judge.me auth is token-based via query params: api_token + shop_domain.
Each review's `body` is the customer comment.

Docs: https://judge.me/api/docs
"""

from __future__ import annotations

from typing import List

import requests

from ..config import JudgeMeConfig
from ..models import Comment

BASE = "https://judge.me/api/v1"
TIMEOUT = 30
PER_PAGE = 100


def fetch(cfg: JudgeMeConfig, limit: int = 30) -> List[Comment]:
    if not cfg.ready:
        print("  · judgeme: skipped (credentials not set)")
        return []

    out: List[Comment] = []
    page = 1

    try:
        while len(out) < limit:
            params = {
                "api_token": cfg.api_token,
                "shop_domain": cfg.shop_domain,
                "per_page": min(PER_PAGE, limit - len(out)),
                "page": page,
            }
            resp = requests.get(f"{BASE}/reviews", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            reviews = resp.json().get("reviews", [])
            if not reviews:
                break

            for r in reviews:
                reviewer = r.get("reviewer") or {}
                author = reviewer.get("name") or reviewer.get("email") or "Anonymous"
                out.append(
                    Comment(
                        source="judgeme",
                        id=str(r.get("id")),
                        author=author,
                        text=r.get("body") or "",
                        created_at=r.get("created_at", ""),
                        rating=r.get("rating"),
                        extra={
                            "title": r.get("title"),
                            "product_external_id": r.get("product_external_id"),
                            "verified": r.get("verified"),
                        },
                    )
                )
                if len(out) >= limit:
                    break
            page += 1
    except requests.HTTPError as e:
        print(f"  · judgeme: API error {e.response.status_code}: {e.response.text[:200]}")
    except requests.RequestException as e:
        print(f"  · judgeme: request failed: {e}")

    return out
