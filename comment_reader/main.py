"""CLI entry point: read customer comments from Facebook, Gorgias, Judge.me.

Usage:
    python -m comment_reader.main                 # all sources, pretty print
    python -m comment_reader.main --source gorgias --limit 50
    python -m comment_reader.main --json > comments.json
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .config import load_config
from .models import Comment
from .sources import facebook, gorgias, judgeme

SOURCES = {
    "facebook": (facebook.fetch, lambda c: c.facebook),
    "gorgias": (gorgias.fetch, lambda c: c.gorgias),
    "judgeme": (judgeme.fetch, lambda c: c.judgeme),
}


def collect(selected: List[str], limit: int) -> List[Comment]:
    cfg = load_config()
    results: List[Comment] = []
    for name in selected:
        fetch_fn, pick = SOURCES[name]
        print(f"Fetching {name}…", file=sys.stderr)
        results.extend(fetch_fn(pick(cfg), limit))
    # newest first across all sources (ISO-8601 sorts lexically)
    results.sort(key=lambda c: c.created_at or "", reverse=True)
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read customer comments from all channels.")
    parser.add_argument(
        "--source",
        action="append",
        choices=sorted(SOURCES),
        help="Limit to specific source(s); repeatable. Default: all.",
    )
    parser.add_argument("--limit", type=int, default=30, help="Max comments per source.")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text.")
    args = parser.parse_args(argv)

    selected = args.source or sorted(SOURCES)
    comments = collect(selected, args.limit)

    if args.json:
        json.dump([c.to_dict() for c in comments], sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        if not comments:
            print("\nNo comments returned. Check that credentials are set (see .env.example).")
            return 0
        print(f"\n{len(comments)} comment(s):\n")
        for c in comments:
            print(c.pretty())
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
