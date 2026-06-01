"""Fetch inbound customer messages from Gorgias.

Gorgias auth is HTTP Basic: (login email, API key). We read the
/api/messages endpoint and keep only messages that came *from the
customer* (from_agent == False), which is the closest equivalent to a
"customer comment".

Docs: https://developers.gorgias.com/reference/
"""

from __future__ import annotations

from typing import List

import requests

from ..config import GorgiasConfig
from ..models import Comment

TIMEOUT = 30


def fetch(cfg: GorgiasConfig, limit: int = 30) -> List[Comment]:
    if not cfg.ready:
        print("  · gorgias: skipped (credentials not set)")
        return []

    base = f"https://{cfg.domain}.gorgias.com/api"
    out: List[Comment] = []
    cursor = None

    try:
        while len(out) < limit:
            params = {
                "limit": min(100, limit - len(out)),
                "order_by": "created_datetime:desc",
            }
            if cursor:
                params["cursor"] = cursor

            resp = requests.get(
                f"{base}/messages",
                params=params,
                auth=(cfg.email, cfg.api_key),
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            payload = resp.json()

            for msg in payload.get("data", []):
                if msg.get("from_agent"):
                    continue  # skip replies sent by your team
                sender = msg.get("sender") or {}
                author = sender.get("name") or sender.get("email") or "Unknown"
                text = msg.get("body_text") or msg.get("stripped_text") or ""
                out.append(
                    Comment(
                        source="gorgias",
                        id=str(msg.get("id")),
                        author=author,
                        text=text,
                        created_at=msg.get("created_datetime", ""),
                        url=msg.get("uri"),
                        extra={
                            "channel": msg.get("channel"),
                            "ticket_id": msg.get("ticket_id"),
                        },
                    )
                )
                if len(out) >= limit:
                    break

            meta = payload.get("meta") or {}
            cursor = meta.get("next_cursor")
            if not cursor:
                break
    except requests.HTTPError as e:
        print(f"  · gorgias: API error {e.response.status_code}: {e.response.text[:200]}")
    except requests.RequestException as e:
        print(f"  · gorgias: request failed: {e}")

    return out
