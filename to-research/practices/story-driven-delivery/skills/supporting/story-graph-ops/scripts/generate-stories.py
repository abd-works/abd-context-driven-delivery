#!/usr/bin/env python3
"""
generate-stories.py  (pml-domain)
==================================
Reads pml-my/docs/stories/story-graph.json and writes *-stories.ts files
into pml-domain/tests/, one file per sub-epic (or per flat epic).

Usage (from anywhere):
    python generate-stories.py [--dry-run]
"""

import json
import re
import sys
import textwrap
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

DOMAIN_ROOT = Path(__file__).parent.parent          # pml-domain/
MY_ROOT     = DOMAIN_ROOT.parent / "pml-my"         # pml-my/
GRAPH_FILE  = MY_ROOT / "docs/stories/story-graph.json"
TESTS_DIR   = Path(__file__).parent                 # pml-domain/tests/

# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------

def to_slug(name: str) -> str:
    s = re.sub(r"['\u2019]", "", name)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def to_const(name: str) -> str:
    s = re.sub(r"['\u2019]", "", name)
    return re.sub(r"[^A-Z0-9]+", "_", s.upper()).strip("_")

def to_camel(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name.strip())
    if not parts:
        return ""
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:] if p)

def ts_str(s: str) -> str:
    escaped = s.replace("\\", "\\\\").replace("`", "\\`")
    return "`" + escaped + "`"

# ---------------------------------------------------------------------------
# Parse raw AC text strings into Step dicts
# ---------------------------------------------------------------------------

GHERKIN_KW = {"GIVEN", "WHEN", "THEN", "AND", "BUT"}

def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
          .replace("\u201c", '"').replace("\u201d", '"')
          .replace("\u2013", "-").replace("\u2014", "-"))
    return re.sub(r"[^\x00-\x7F]+", "", s).strip()

def parse_ac_text(raw: str) -> list:
    """
    Convert a raw AC string like:
      "When X\nThen Y\nAnd Z"
    into a list of step dicts: [{"when": "X"}, {"then": "Y"}, {"and": "Z"}]
    """
    steps = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("—") or stripped.startswith("-"):
            # bullet continuation — append to previous Then text
            if steps and stripped:
                kw, prev = next(iter(steps[-1].items()))
                bullet = clean_text(stripped.lstrip("—- "))
                if bullet:
                    steps[-1] = {kw: prev + "; " + bullet}
            continue
        m = re.match(r"^(\w+)\s+(.*)", stripped)
        if m:
            kw = m.group(1).upper()
            if kw in GHERKIN_KW:
                text = clean_text(m.group(2))
                if text:
                    steps.append({kw.lower(): text})
                continue
        # continuation of previous step
        if steps and stripped:
            kw, prev = next(iter(steps[-1].items()))
            cont = clean_text(stripped)
            if cont:
                steps[-1] = {kw: prev + " " + cont}
    return steps

# ---------------------------------------------------------------------------
# Walk story-graph.json
# ---------------------------------------------------------------------------

FLAT_EPICS = {"app-availability", "manage-profile", "view-home-dashboard"}

def iter_sub_epics(graph: dict):
    """Yield (epic_name, sub_epic_name_or_None, [story_dicts])."""
    for epic in graph.get("epics", []):
        ename = epic["name"]
        if "sub_epics" in epic:
            for sub in epic["sub_epics"]:
                stories = []
                for grp in sub.get("story_groups", []):
                    stories.extend(grp.get("stories", []))
                yield ename, sub["name"], stories
        else:
            stories = []
            for grp in epic.get("story_groups", []):
                stories.extend(grp.get("stories", []))
            yield ename, None, stories

def ts_path_for(epic_name: str, sub_epic_name) -> Path:
    es = to_slug(epic_name)
    ss = to_slug(sub_epic_name) if sub_epic_name else es
    if es in FLAT_EPICS or es == ss:
        return TESTS_DIR / es / f"{es}-stories.ts"
    return TESTS_DIR / es / ss / f"{ss}-stories.ts"

def depth_from(ts_path: Path) -> str:
    parts = ts_path.relative_to(TESTS_DIR).parts
    return "../" * (len(parts) - 1) + "story-types"

# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def render_step(step: dict, indent: int = 6) -> str:
    ind = " " * indent
    kw, text = next(iter(step.items()))
    return f"{ind}{{ {kw}: {ts_str(text)} }},"

def scenario_key(steps: list, idx: int) -> str:
    when_text = ""
    then_text = ""
    for step in steps:
        kw, text = next(iter(step.items()))
        if kw == "when" and not when_text:
            when_text = text
        elif kw in ("then", "but") and not then_text:
            then_text = text
    combined = (when_text + " " + then_text).strip()
    words = re.sub(r"[^a-zA-Z0-9 ]+", " ", combined).split()[:10]
    key = to_camel(" ".join(words))
    return key if key else f"scenario{idx + 1}"

def human_name(key: str) -> str:
    return re.sub(r"([A-Z])", r" \1", key).lower().strip()

def generate_story_const(story: dict) -> str:
    name   = story["name"]
    actor  = story.get("story_type", "")
    raw_acs = story.get("acceptance_criteria", [])
    acs    = [parse_ac_text(raw) for raw in raw_acs if raw]
    acs    = [ac for ac in acs if ac]  # drop empty

    cname  = to_const(name)
    out    = []
    out.append(f"export const {cname} = {{")
    out.append(f"  story: {ts_str(name)},")
    out.append(f"  actor: {ts_str(actor)},")
    out.append("")
    out.append("  acceptance_criteria: [")
    for ac in acs:
        out.append("    [")
        for step in ac:
            out.append("  " + render_step(step, 4))
        out.append("    ],")
    if not acs:
        out.append("    // TODO: add acceptance criteria")
    out.append("  ] as const satisfies readonly AcceptanceCriterion[],")
    out.append("")
    out.append("  domain_terms: [] as const,")
    out.append("  evidence: [] as const,")
    out.append("")

    for idx, ac in enumerate(acs):
        key = scenario_key(ac, idx)
        out.append(f"  {key}: {{")
        out.append(f"    name: {ts_str(human_name(key))},")
        out.append("    steps: [")
        for step in ac:
            out.append("  " + render_step(step, 4))
        out.append("    ] as const satisfies readonly Step[],")
        out.append("  },")
        out.append("")

    if not acs:
        out.append("  // TODO: add scenarios")
        out.append("")

    out.append("} as const")
    return "\n".join(out)

def generate_file(epic_name: str, sub_epic_name, stories: list, ts_path: Path) -> str:
    depth  = depth_from(ts_path)
    parts  = []

    parts.append(f"import type {{ Step, AcceptanceCriterion, Background }} from '{depth}'")
    parts.append("")

    for story in stories:
        bar  = "=" * 77
        parts.append(f"// {bar}")
        parts.append(f"// STORY: {story['name']}")
        parts.append(f"// {bar}")
        parts.append("")
        parts.append(generate_story_const(story))
        parts.append("")

    return "\n".join(parts)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Reading {GRAPH_FILE} ...")
    graph = json.loads(GRAPH_FILE.read_text(encoding="utf-8"))

    for epic_name, sub_epic_name, stories in iter_sub_epics(graph):
        ts_path = ts_path_for(epic_name, sub_epic_name)
        content = generate_file(epic_name, sub_epic_name, stories, ts_path)

        if DRY_RUN:
            rel = ts_path.relative_to(TESTS_DIR)
            print(f"  [DRY] {rel}")
            print(textwrap.indent(content[:400], "    "))
            print("    ...")
        else:
            ts_path.parent.mkdir(parents=True, exist_ok=True)
            ts_path.write_text(content, encoding="utf-8")
            rel = ts_path.relative_to(TESTS_DIR)
            n   = len(stories)
            print(f"  ok  {rel}  ({n} stor{'y' if n == 1 else 'ies'})")

    print("\nDone." if not DRY_RUN else "\nDry-run complete.")

if __name__ == "__main__":
    main()
