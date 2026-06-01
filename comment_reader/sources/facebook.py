"""Fetch comments on a Facebook Page's posts via the Graph API.

Requires a Page access token (long-lived recommended) and the Page ID.
We read the page feed and expand the comments edge on each post.

Docs: https://developers.facebook.com/docs/graph-api/reference/page/feed
"""

from __future__ import annotations

from typing import List

import requests

from ..config import FacebookConfig
from ..models import Comment

TIMEOUT = 30


def fetch(cfg: FacebookConfig, limit: int = 30) -> List[Comment]:
    if not cfg.ready:
        print("  · facebook: skipped (credentials not set)")
        return []

    base = f"https://graph.facebook.com/{cfg.api_version}"
    out: List[Comment] = []

    # Pull recent posts, each with its comments expanded.
    url = f"{base}/{cfg.page_id}/feed"
    params = {
        "access_token": cfg.access_token,
        "fields": "id,comments.limit(50){id,message,from,created_time,permalink_url}",
        "limit": 25,
    }

    try:
        while url and len(out) < limit:
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()

            for post in payload.get("data", []):
                for c in (post.get("comments") or {}).get("data", []):
                    sender = c.get("from") or {}
                    out.append(
                        Comment(
                            source="facebook",
                            id=str(c.get("id")),
                            author=sender.get("name") or "Facebook user",
                            text=c.get("message") or "",
                            created_at=c.get("created_time", ""),
                            url=c.get("permalink_url"),
                            extra={"post_id": post.get("id")},
                        )
                    )
                    if len(out) >= limit:
                        break
                if len(out) >= limit:
                    break

            # Follow paging cursor; params already baked into the `next` URL.
            url = (payload.get("paging") or {}).get("next")
            params = None
    except requests.HTTPError as e:
        print(f"  · facebook: API error {e.response.status_code}: {e.response.text[:200]}")
    except requests.RequestException as e:
        print(f"  · facebook: request failed: {e}")

    return out
