#!/usr/bin/env python3
"""View events captured by the hook_test tester.

Usage:
    python3 hook_test/view_events.py                  # pretty summary of all events
    python3 hook_test/view_events.py --tail 10        # last N events, JSON
    python3 hook_test/view_events.py --hook stop      # filter by hook name
    python3 hook_test/view_events.py --counts         # count events per hook
    python3 hook_test/view_events.py --clear          # truncate the log

Nothing here changes hook behavior; it is a read-only helper you can invoke
manually to confirm that hooks fired.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HOOK_TEST_DIR = Path(__file__).resolve().parent
EVENTS_PATH = HOOK_TEST_DIR / "logs" / "events.jsonl"
PRETTY_PATH = HOOK_TEST_DIR / "logs" / "pretty.log"


def _load_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    out: list[dict] = []
    with EVENTS_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def cmd_counts() -> int:
    events = _load_events()
    counter: collections.Counter[str] = collections.Counter(e.get("hook", "?") for e in events)
    if not counter:
        print("No events recorded yet.")
        return 0
    width = max(len(k) for k in counter)
    for hook, count in counter.most_common():
        print(f"  {hook:<{width}}  {count}")
    print(f"  {'total':<{width}}  {sum(counter.values())}")
    return 0


def cmd_pretty() -> int:
    if not PRETTY_PATH.exists():
        print("No pretty log yet. Trigger some hooks first (see hook_test/README.md).")
        return 0
    sys.stdout.write(PRETTY_PATH.read_text(encoding="utf-8"))
    return 0


def cmd_tail(n: int, hook: str | None) -> int:
    events = _load_events()
    if hook:
        events = [e for e in events if e.get("hook") == hook]
    for event in events[-n:]:
        print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


def cmd_clear() -> int:
    for path in (EVENTS_PATH, PRETTY_PATH):
        if path.exists():
            path.unlink()
    print("Cleared hook_test logs.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tail", type=int, default=0, help="Show the last N events (full JSON).")
    parser.add_argument("--hook", type=str, default=None, help="Filter by hook name when using --tail.")
    parser.add_argument("--counts", action="store_true", help="Show a per-hook event count.")
    parser.add_argument("--clear", action="store_true", help="Delete the log files.")
    args = parser.parse_args()

    if args.clear:
        return cmd_clear()
    if args.counts:
        return cmd_counts()
    if args.tail:
        return cmd_tail(args.tail, args.hook)
    return cmd_pretty()


if __name__ == "__main__":
    raise SystemExit(main())
