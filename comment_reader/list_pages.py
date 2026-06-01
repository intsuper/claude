"""Helper: list the Facebook Pages the FACEBOOK_ACCESS_TOKEN can manage.

Run this in CI (where the token lives) to discover your Page ID, then set
it as the FACEBOOK_PAGE_ID secret. Prints name + id; never prints the token.

    python -m comment_reader.list_pages
"""

from __future__ import annotations

import os
import sys

import requests

API_VERSION = os.environ.get("FACEBOOK_API_VERSION", "v19.0").strip() or "v19.0"
TIMEOUT = 30


def main() -> int:
    token = (os.environ.get("FACEBOOK_ACCESS_TOKEN") or "").strip()
    if not token:
        print("FACEBOOK_ACCESS_TOKEN is not set.", file=sys.stderr)
        return 1

    base = f"https://graph.facebook.com/{API_VERSION}"
    found = []

    # A user token exposes managed pages via /me/accounts.
    url = f"{base}/me/accounts"
    params = {"access_token": token, "fields": "id,name,category", "limit": 100}
    try:
        while url:
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
            found.extend(payload.get("data", []))
            url = (payload.get("paging") or {}).get("next")
            params = None

        # If the token is itself a Page token, /me/accounts is empty;
        # /me then returns that single page.
        if not found:
            resp = requests.get(
                f"{base}/me",
                params={"access_token": token, "fields": "id,name,category"},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            me = resp.json()
            if me.get("id"):
                found.append(me)
    except requests.HTTPError as e:
        print(f"Graph API error {e.response.status_code}: {e.response.text[:300]}", file=sys.stderr)
        return 1
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1

    if not found:
        print("No pages found for this token.")
        return 0

    print(f"\nFound {len(found)} page(s). Set FACEBOOK_PAGE_ID to the one you want:\n")
    for p in found:
        cat = f"  ({p.get('category')})" if p.get("category") else ""
        print(f"  {p.get('name', '?')}{cat}")
        print(f"      FACEBOOK_PAGE_ID = {p.get('id')}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
