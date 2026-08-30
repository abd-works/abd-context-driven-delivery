"""One-shot live smoke test: add_theme sets label + project board Theme.

Run from repo root:
  .\\.venv\\Scripts\\python.exe utilities/git/_verify_theme_live.py

Creates a throwaway issue, verifies label and board Theme, then closes it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
for part in ("", "utilities", "primitives", "context_tools"):
    p = str(_REPO / part) if part else str(_REPO)
    if p not in sys.path:
        sys.path.insert(0, p)

from git.git import Repo  # noqa: E402


def _theme_from_item(item: dict) -> str | None:
    top = item.get("theme")
    if top:
        return str(top).strip()
    field_values = item.get("fieldValues") or {}
    nodes = field_values.get("nodes") if isinstance(field_values, dict) else field_values
    for field in nodes or []:
        if not isinstance(field, dict):
            continue
        field_meta = field.get("field") or {}
        if str(field_meta.get("name") or "") == "Theme":
            return str(field.get("name") or field.get("text") or "").strip() or None
    return None


def main() -> int:
    repo = Repo.open(_REPO)
    repo.attach_project("abd-works", 1)
    title = "[theme-verify] delete me — board Theme smoke test"
    ticket = repo.create_ticket(
        title,
        "Automated smoke test for add_theme → project Theme field. Safe to close.",
    )
    ticket.set_status("Backlog")
    ticket.add_theme("cli-agent")

    owner, name = repo.owner_repo()
    num = ticket.number
    print(f"ISSUE={owner}/{name}#{num}")

    labels_raw = repo._gh("issue", "view", str(num), "--json", "labels")
    labels = [x["name"] for x in json.loads(labels_raw).get("labels", [])]
    print(f"LABELS={labels}")

    items_raw = repo._gh(
        "project",
        "item-list",
        "1",
        "--owner",
        "abd-works",
        "--format",
        "json",
        "--limit",
        "200",
    )
    items = json.loads(items_raw).get("items", [])
    theme_value = None
    for item in items:
        content = item.get("content") or {}
        if content.get("number") == num:
            theme_value = _theme_from_item(item)
            break

    print(f"BOARD_THEME={theme_value!r}")

    ok = "theme:cli-agent" in labels and theme_value == "cli-agent"
    print(f"PASS={ok}")

    ticket.close()
    print("CLOSED=yes")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
