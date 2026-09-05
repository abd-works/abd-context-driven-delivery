#!/usr/bin/env python3
"""Scanner: every story name listed in thin-slicing.md must exactly match
a story name in story-graph.json.

Catches the class of bug where an agent abbreviates, renames, or trims a
story name (e.g. "Load FX Resource Catalog" instead of
"Load FX Resource Catalog (FxRepo.data)") so that the story is never
linked to any increment in the graph.

Exit codes:
  0  — all story names are exact matches (or no thin-slicing.md / graph found)
  1  — one or more story names do not match
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Parsing thin-slicing.md
# ---------------------------------------------------------------------------

# Matches bullet lines under "Stories in this increment" sections.
# Accepts lines like:  - Story Name   or  - *Story Name*
_BULLET = re.compile(r"^\s*-\s+\*?([^*()\n]+?)\*?\s*(?:-\(.*?\))?\s*$")
# Strip any accidental "Actor --> " prefix that slipped through
_ACTOR_PREFIX = re.compile(r"^\w[\w ]*\s*-->\s*")


def _parse_thin_slice_stories(path: Path) -> list[tuple[int, str]]:
    """Return [(line_no, story_name), …] from all story bullets."""
    results: list[tuple[int, str]] = []
    in_stories_block = False
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        # Enter / leave story block
        if re.match(r"\*\*Stories in this increment", stripped):
            in_stories_block = True
            continue
        if stripped.startswith("**") and in_stories_block:
            in_stories_block = False
        if stripped.startswith("###") or stripped.startswith("##"):
            in_stories_block = False

        if in_stories_block:
            m = _BULLET.match(line)
            if m:
                name = m.group(1).strip().strip("*").strip()
                name = _ACTOR_PREFIX.sub("", name).strip()
                if name:
                    results.append((lineno, name))
    return results


# ---------------------------------------------------------------------------
# Loading canonical story names from story-graph.json
# ---------------------------------------------------------------------------

def _collect_story_names(graph: dict) -> set[str]:
    names: set[str] = set()

    def _walk(node: dict) -> None:
        for sg in node.get("story_groups", []):
            for s in sg.get("stories", []):
                n = s.get("name", "").strip()
                if n:
                    names.add(n)
        for se in node.get("sub_epics", []):
            _walk(se)

    for epic in graph.get("epics", []):
        _walk(epic)
    return names


# ---------------------------------------------------------------------------
# Violation dict helper (matches run_scanners.py format)
# ---------------------------------------------------------------------------

def _violation(location: str, message: str) -> dict:
    return {
        "rule": "story-names-must-be-exact-match",
        "violation_message": message,
        "location": location,
        "severity": "error",
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="Project root (where story-graph.json and thin-slicing.md live)")
    parser.add_argument("--skill-root", default=None, help="Skill root (unused — accepted for runner compatibility)")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()

    # Locate story-graph.json
    graph_path = workspace / "story-graph.json"
    if not graph_path.is_file():
        # Try docs/ sub-folder (common layout)
        graph_path = workspace / "docs" / "story-graph.json"
    if not graph_path.is_file():
        print(f"# story-name-exact-match-scanner: story-graph.json not found under {workspace} — skipping", file=sys.stderr)
        return 0

    # Locate thin-slicing.md
    slice_path = workspace / "thin-slicing.md"
    if not slice_path.is_file():
        slice_path = workspace / "docs" / "thin-slicing.md"
    if not slice_path.is_file():
        print(f"# story-name-exact-match-scanner: thin-slicing.md not found under {workspace} — skipping", file=sys.stderr)
        return 0

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    canonical = _collect_story_names(graph)

    bullets = _parse_thin_slice_stories(slice_path)

    violations: list[dict] = []
    for lineno, name in bullets:
        if name not in canonical:
            location = f"{slice_path.name}:{lineno}"
            # Suggest the closest canonical name if possible
            lower_name = name.lower()
            candidates = [c for c in canonical if c.lower().startswith(lower_name[:20])]
            hint = f" (closest canonical: {candidates[0]!r})" if candidates else ""
            violations.append(_violation(
                location,
                f"Story name {name!r} in thin-slicing.md does not exactly match any story in story-graph.json.{hint} "
                f"Copy the name verbatim from story-map.md or story-graph.json — including any parenthetical qualifiers.",
            ))

    for v in violations:
        print(repr(v))

    if violations:
        print(f"\n# {len(violations)} story-name mismatch(es) found. "
              f"Fix thin-slicing.md so every story name is copied verbatim from story-graph.json.",
              file=sys.stderr)
        return 1

    print(f"# story-name-exact-match-scanner: all {len(bullets)} story names verified — OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
