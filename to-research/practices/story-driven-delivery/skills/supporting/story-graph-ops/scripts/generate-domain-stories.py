#!/usr/bin/env python3
"""
generate-domain-stories.py
==========================
Generates pml-domain/tests/**/*-stories.ts from:
  1. pml-my/docs/stories/story-graph.json        -- hierarchy, actor, raw AC text
  2. pml-domain/generated/acceptance-criteria.md -- domain_terms, evidence (supplement)
  3. Existing pml-domain/tests/**/*-stories.ts   -- fixture exports to preserve

Usage (from pml-domain/tests/):
    python generate-domain-stories.py [--dry-run]

Does NOT touch pml-my/tests/.
"""

import json
import re
import sys
import textwrap
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

_DOMAIN_ROOT = Path(__file__).parent.parent           # pml-domain/
_MY_ROOT     = _DOMAIN_ROOT.parent / "pml-my"         # pml-my/

GRAPH_FILE   = _MY_ROOT / "docs/stories/story-graph.json"
DOMAIN_AC    = _DOMAIN_ROOT / "generated/acceptance-criteria.md"
TESTS_DIR    = Path(__file__).parent                   # pml-domain/tests/

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

def ts_array(items: list, indent: int = 4) -> str:
    ind = " " * indent
    inner = [f"'{it}'" for it in items]
    if sum(len(x) for x in inner) < 60:
        return "[" + ", ".join(inner) + "] as const"
    body = ",\n".join(ind + "  " + x for x in inner)
    return f"[\n{body},\n{ind}] as const"

# ---------------------------------------------------------------------------
# Parse raw AC text from story-graph.json into Step arrays
# ---------------------------------------------------------------------------

GHERKIN_KW = {"GIVEN", "WHEN", "THEN", "AND", "BUT"}

def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
          .replace("\u201c", '"').replace("\u201d", '"')
          .replace("\u2013", "-").replace("\u2014", "-"))
    s = re.sub(r"[^\x00-\x7F]+", "", s).strip()
    return s

def parse_ac_text(raw_ac: str) -> list:
    """Parse one raw AC string into list of {kw: text} step dicts."""
    steps: list = []
    cur_kw:   str | None = None
    cur_text: list = []

    for line in raw_ac.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r"^(Given|When|Then|And|But)\s+(.*)", stripped, re.IGNORECASE)
        if m:
            if cur_kw and cur_text:
                steps.append({cur_kw: clean_text(" ".join(cur_text))})
            cur_kw   = m.group(1).lower()
            cur_text = [m.group(2).strip()]
        elif cur_kw:
            cur_text.append(stripped)

    if cur_kw and cur_text:
        steps.append({cur_kw: clean_text(" ".join(cur_text))})

    return steps

# ---------------------------------------------------------------------------
# Parse story-graph.json — primary source for structure + ACs
# ---------------------------------------------------------------------------

def parse_graph(path: Path) -> list:
    """
    Returns a list of sub-epic groups:
      [{epic, sub_epic, ts_path, stories: [{story, actor, acs, domain_terms, evidence}]}]
    """
    graph = json.loads(path.read_text(encoding="utf-8"))
    groups: list = []

    for epic in graph.get("epics", []):
        epic_name = epic["name"]
        epic_slug = to_slug(epic_name)

        def make_story(s: dict) -> dict:
            acs = []
            for raw in s.get("acceptance_criteria", []):
                steps = parse_ac_text(raw)
                if steps:
                    acs.append(steps)
            return {
                "story":        s["name"],
                "actor":        s.get("story_type", ""),
                "acs":          acs,
                "domain_terms": [],
                "evidence":     [],
            }

        if "sub_epics" in epic:
            for sub in epic["sub_epics"]:
                sub_name = sub["name"]
                sub_slug = to_slug(sub_name)
                stories = [
                    make_story(s)
                    for sg in sub.get("story_groups", [])
                    for s  in sg.get("stories", [])
                ]
                ts_path = TESTS_DIR / epic_slug / sub_slug / f"{sub_slug}-stories.ts"
                groups.append({
                    "epic":     epic_name,
                    "sub_epic": sub_name,
                    "ts_path":  ts_path,
                    "stories":  stories,
                })
        else:
            # Flat epic — single file at epic level
            stories = [
                make_story(s)
                for sg in epic.get("story_groups", [])
                for s  in sg.get("stories", [])
            ]
            ts_path = TESTS_DIR / epic_slug / f"{epic_slug}-stories.ts"
            groups.append({
                "epic":     epic_name,
                "sub_epic": None,
                "ts_path":  ts_path,
                "stories":  stories,
            })

    return groups

# ---------------------------------------------------------------------------
# Parse pml-domain/generated/acceptance-criteria.md for domain_terms + evidence
# ---------------------------------------------------------------------------

def parse_domain_ac(path: Path) -> dict:
    """
    Returns {story_slug: {"domain_terms": [...], "evidence": [...]}}
    Used to supplement story-graph data with domain vocabulary and sources.
    """
    if not path.exists():
        print(f"  [warn] Domain AC file not found: {path}")
        return {}

    text = path.read_text(encoding="utf-8", errors="replace")
    result: dict = {}
    cur_slug:     str | None = None
    section:      str        = ""

    for raw in text.splitlines():
        line = raw.rstrip()

        # Story heading: ### Story: `Name`
        m = re.match(r"^### Story: `(.+)`", line)
        if m:
            cur_slug = to_slug(m.group(1).strip())
            result[cur_slug] = {"domain_terms": [], "evidence": []}
            section = ""
            continue

        if cur_slug is None:
            continue

        # Section markers
        if re.match(r"^#### Domain terms", line, re.IGNORECASE):
            section = "terms"
            continue
        if re.match(r"^#### Evidence", line, re.IGNORECASE):
            section = "evidence"
            continue
        if re.match(r"^####", line):
            section = ""
            continue

        # Domain terms: "- *term*"
        if section == "terms":
            m = re.match(r"^-\s+\*(.+?)\*\s*$", line)
            if m:
                result[cur_slug]["domain_terms"].append(m.group(1).strip())
            continue

        # Evidence table rows — capture Location column (3rd column)
        if section == "evidence":
            # | num | source | location |
            m = re.match(r"^\|\s*\d+\s*\|[^|]+\|([^|]+)\|", line)
            if m:
                loc = clean_text(m.group(1))
                # Strip backtick noise
                loc = re.sub(r"[`]", "", loc).strip()
                if loc and loc.lower() not in ("location", "---", ""):
                    result[cur_slug]["evidence"].append(loc)
            continue

    return result

# ---------------------------------------------------------------------------
# Extract fixture lines from existing *-stories.ts (preserve non-story consts)
# ---------------------------------------------------------------------------

def extract_fixture_lines(ts_path: Path) -> list:
    """
    Keep: fixture constants (ROUTE, EXPECTED_ELEMENTS, EXAMPLES_*, imports).
    Drop: story consts (story: inside), decorator lines (@story etc.), BACKGROUND,
          type declarations, story-types import (re-added by generator).
    """
    if not ts_path.exists():
        return []

    lines = ts_path.read_text(encoding="utf-8", errors="replace").splitlines()

    # Pass 1 — identify consts to skip
    skip_consts: set = {"BACKGROUND"}
    i = 0
    while i < len(lines):
        m = re.match(r"^export const (\w+)\s*=\s*\{", lines[i])
        if m:
            cname  = m.group(1)
            window = "\n".join(lines[i : i + 12])
            if (re.search(r"\bstory\s*:", window) or
                    re.search(r"@story\(", window) or
                    cname.endswith("_SCENARIOS")):
                skip_consts.add(cname)
        i += 1

    result: list = []
    i = 0

    def brace_delta(s: str) -> int:
        return s.count("{") + s.count("[") - s.count("}") - s.count("]")

    while i < len(lines):
        line  = lines[i]
        strip = line.strip()

        if not strip:
            result.append("")
            i += 1
            continue

        # Decorator lines — skip
        if re.match(r"^@\w+\(", strip):
            i += 1
            continue

        # Type declarations — skip
        if re.match(r"^(export\s+)?type\s+\w+", strip):
            while i < len(lines) and not lines[i].rstrip().endswith(";"):
                i += 1
            i += 1
            continue

        # story-types import — skip (re-added by generator)
        if re.match(r"^import\s+type\s+.*story-types", strip):
            i += 1
            continue

        # Other imports — keep
        if re.match(r"^import\s+", strip):
            result.append(line)
            i += 1
            continue

        # Re-exports
        if re.match(r"^export\s+\{", strip):
            result.append(line)
            i += 1
            continue

        # export const
        m = re.match(r"^export const (\w+)\s*=", strip)
        if m:
            cname = m.group(1)
            if cname in skip_consts:
                depth = brace_delta(strip)
                i += 1
                while i < len(lines) and depth > 0:
                    depth += brace_delta(lines[i])
                    i += 1
                continue
            else:
                # Keep entire block
                result.append(line)
                depth = brace_delta(strip)
                i += 1
                while i < len(lines) and depth > 0:
                    result.append(lines[i])
                    depth += brace_delta(lines[i])
                    i += 1
                continue

        # Skip section separators / story-block comments
        if strip.startswith("//"):
            if (strip == "//" or
                    re.match(r"^//\s*=+\s*$", strip) or
                    re.match(r"^//\s*(STORY|Sub-epic|Source|Story Map):", strip)):
                i += 1
                continue
            result.append(line)
            i += 1
            continue

        # Skip bare "} as const" endings (story block closers)
        if strip in ("} as const", "} as const;"):
            i += 1
            continue

        i += 1

    # De-dup consecutive blanks, strip trailing blanks
    cleaned: list = []
    prev_blank = False
    for l in result:
        if not l.strip():
            if not prev_blank:
                cleaned.append("")
            prev_blank = True
        else:
            cleaned.append(l)
            prev_blank = False
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    return cleaned

# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def render_step(step: dict, indent: int = 6) -> str:
    kw, text = next(iter(step.items()))
    return " " * indent + f"{{ {kw}: {ts_str(text)} }},"

def scenario_key(ac: list, idx: int) -> str:
    when_text = ""
    then_text = ""
    for step in ac:
        kw, text = next(iter(step.items()))
        if kw == "when" and not when_text:
            when_text = text
        elif kw in ("then", "but") and not then_text:
            then_text = text
    combined = (when_text + " " + then_text).strip()
    words = re.sub(r"[^a-zA-Z0-9 ]+", " ", combined).split()[:10]
    key = to_camel(" ".join(words))
    return key if key else f"scenario{idx + 1}"

def generate_story_const(d: dict, const_name: str) -> str:
    acs   = d.get("acs", [])
    terms = d.get("domain_terms", [])
    evs   = d.get("evidence", [])
    actor = d.get("actor", "")

    out: list = []
    out.append(f"export const {const_name} = {{")
    out.append(f"  story: {ts_str(d['story'])},")
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
    out.append(f"  domain_terms: {ts_array(terms)},")
    out.append(f"  evidence: {ts_array(evs)},")
    out.append("")

    for idx, ac in enumerate(acs):
        key   = scenario_key(ac, idx)
        human = re.sub(r"([A-Z])", r" \1", key).lower().strip()
        out.append(f"  {key}: {{")
        out.append(f"    name: {ts_str(human)},")
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

def depth_from(ts_path: Path) -> str:
    parts = ts_path.relative_to(TESTS_DIR).parts
    return "../" * (len(parts) - 1) + "story-types"

def generate_file(stories_data: list, fixture_lines: list, ts_path: Path) -> str:
    depth = depth_from(ts_path)
    parts: list = []

    parts.append(f"import type {{ Step, AcceptanceCriterion, Background }} from '{depth}'")
    parts.append("")

    if fixture_lines:
        parts.extend(fixture_lines)
        parts.append("")

    parts.append("// =============================================================================")
    parts.append("// BACKGROUND  (optional -- remove if no shared Given applies to this sub-epic)")
    parts.append("// =============================================================================")
    parts.append("")
    parts.append("export const BACKGROUND = [")
    parts.append("  { given: '<shared precondition -- update or remove this block>' },")
    parts.append("] as const satisfies Background")
    parts.append("")

    for s in stories_data:
        const_name = to_const(s["story"])
        bar = "=" * 77
        parts.append(f"// {bar}")
        parts.append(f"// STORY: {s['story']}")
        parts.append(f"// {bar}")
        parts.append("")
        parts.append(generate_story_const(s, const_name))
        parts.append("")

    return "\n".join(parts)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Reading story graph ...")
    groups = parse_graph(GRAPH_FILE)
    total_stories = sum(len(g["stories"]) for g in groups)
    print(f"  -> {total_stories} stories across {len(groups)} files")

    print("Reading domain AC (supplementary domain_terms + evidence) ...")
    domain_ac = parse_domain_ac(DOMAIN_AC)
    print(f"  -> {len(domain_ac)} domain story entries")

    # Merge domain_terms + evidence into each story
    for group in groups:
        for story in group["stories"]:
            slug = to_slug(story["story"])
            if slug in domain_ac:
                story["domain_terms"] = domain_ac[slug].get("domain_terms", [])
                story["evidence"]     = domain_ac[slug].get("evidence", [])

    for group in groups:
        ts_path      = group["ts_path"]
        fixture_lines = extract_fixture_lines(ts_path)
        content      = generate_file(group["stories"], fixture_lines, ts_path)

        if DRY_RUN:
            rel = ts_path.relative_to(TESTS_DIR)
            print(f"\n  [DRY] {rel}")
            print(textwrap.indent(content[:600], "    "))
            print("    ...")
        else:
            ts_path.parent.mkdir(parents=True, exist_ok=True)
            ts_path.write_text(content, encoding="utf-8")
            rel = ts_path.relative_to(TESTS_DIR)
            print(f"  ok  {rel}")

    print("\nDone." if not DRY_RUN else "\nDry-run complete.")

if __name__ == "__main__":
    main()
