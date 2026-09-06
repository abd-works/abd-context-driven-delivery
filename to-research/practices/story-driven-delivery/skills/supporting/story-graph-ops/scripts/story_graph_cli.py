#!/usr/bin/env python3
"""CLI for reading, searching, filtering, and writing ``story-graph.json`` without agile_bots.

Add ``…/story-graph-ops/scripts`` and ``…/execute-skill-using-skills-rules/scripts`` to PYTHONPATH, then:

  python story_graph_cli.py read --file path/to/story-graph.json
  python story_graph_cli.py names --file path/to/story-graph.json
  python story_graph_cli.py search --file ... --substring "Login"
  python story_graph_cli.py filter --file ... --stories "A","B" > subset.json
  python story_graph_cli.py sha --file path/to/story-graph.json
  python story_graph_cli.py write --file out.json < input.json
  python story_graph_cli.py write --file out.json --input in.json --expect-sha <hex>

Concurrency / parallel-run safety:

  - ``write`` takes an exclusive advisory lock at ``<file>.lock`` for the
    duration of the write. If another process holds the lock, the write is
    refused (exit 4). Stale locks (>300s) are auto-cleaned.
  - ``write`` also supports ``--expect-sha <hex>``: if the target file's
    current content hash does not match, the write is refused (exit 3).
    Capture the hash at read time with ``sha`` and pass it back on write.
  - ``--force`` on ``write`` bypasses both checks. Use only for recovery.
  - ``--no-lock`` skips the advisory lock (rarely needed; not recommended).

These safeguards backstop the planning-level rule that **parallel runs must
not edit the same slice of ``story-graph.json`` at the same time** (see
``SKILL.md`` → "Parallel runs and concurrent writes").
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set

# Allow running from repo without install: parent directory is on PYTHONPATH
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# --- concurrency helpers ----------------------------------------------------- #

_STALE_LOCK_SECONDS = 300  # 5 minutes


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _lock_path_for(target: Path) -> Path:
    return target.with_name(target.name + ".lock")


def _read_lock(lock: Path) -> Dict[str, Any]:
    try:
        return json.loads(lock.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _acquire_lock(target: Path, force: bool) -> Path | None:
    """Create an exclusive lock file next to *target*. Return its path, or None on failure.

    Returns the lock path on success. Raises SystemExit(4) if another live lock is held
    and ``force`` is false.
    """
    lock = _lock_path_for(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({
        "pid": os.getpid(),
        "acquired_at": time.time(),
        "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "",
    }).encode("utf-8")
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        existing = _read_lock(lock)
        age = time.time() - float(existing.get("acquired_at", 0) or 0)
        if age > _STALE_LOCK_SECONDS or force:
            # Stale or forced: remove and retry once.
            try:
                lock.unlink()
            except FileNotFoundError:
                pass
            try:
                fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except FileExistsError:
                print(
                    f"[error] could not acquire lock {lock} "
                    f"(held by pid={existing.get('pid')}, age={int(age)}s). "
                    "Another writer is active; retry later or pass --force.",
                    file=sys.stderr,
                )
                sys.exit(4)
        else:
            print(
                f"[error] concurrent write refused: lock {lock} is held by "
                f"pid={existing.get('pid')} (age={int(age)}s). "
                "Parallel runs must not edit the same graph file. "
                "Wait for the other writer, or pass --force if you are recovering a stale lock.",
                file=sys.stderr,
            )
            sys.exit(4)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)
    return lock


def _release_lock(lock: Path | None) -> None:
    if lock is None:
        return
    try:
        lock.unlink()
    except FileNotFoundError:
        pass


def _load_graph(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        print(f"[error] not a file: {path}", file=sys.stderr)
        sys.exit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_story_names(data: Dict[str, Any]) -> List[str]:
    from story_map import Story, StoryMap

    sm = StoryMap(data)
    names: List[str] = []
    for epic in sm.epics():
        for node in sm.walk(epic):
            if isinstance(node, Story) and node.name:
                names.append(node.name)
    return names


def cmd_read(args: argparse.Namespace) -> int:
    data = _load_graph(Path(args.file))
    if args.pretty:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, ensure_ascii=False))
    return 0


def cmd_names(args: argparse.Namespace) -> int:
    data = _load_graph(Path(args.file))
    for n in _collect_story_names(data):
        print(n)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    data = _load_graph(Path(args.file))
    sub = (args.substring or "").lower()
    hits = [n for n in _collect_story_names(data) if sub in n.lower()]
    for n in hits:
        print(n)
    return 0 if hits else 1


def cmd_filter(args: argparse.Namespace) -> int:
    from graph_filters import filter_story_graph_to_story_names

    data = _load_graph(Path(args.file))
    raw = args.stories or ""
    names: Set[str] = {s.strip() for s in raw.split(",") if s.strip()}
    out = filter_story_graph_to_story_names(data, names)
    if args.pretty:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(out, ensure_ascii=False))
    return 0


def cmd_sha(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"[error] not a file: {path}", file=sys.stderr)
        return 2
    print(_sha256_file(path))
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    path.parent.mkdir(parents=True, exist_ok=True)

    lock = None if args.no_lock else _acquire_lock(path, force=args.force)
    try:
        # Optimistic concurrency: if the caller captured a sha at read time and the
        # file changed since, refuse rather than clobber another writer's edit.
        if path.is_file() and args.expect_sha and not args.force:
            current = _sha256_file(path)
            if current != args.expect_sha:
                print(
                    f"[error] concurrent write refused: --expect-sha mismatch. "
                    f"expected={args.expect_sha} current={current}. "
                    "Re-read the file, merge your changes against the current content, "
                    "and retry. Pass --force only if you intend to clobber.",
                    file=sys.stderr,
                )
                return 3

        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}", file=sys.stderr)
        return 0
    finally:
        _release_lock(lock)


# ---------------------------------------------------------------------------
# generate: story-graph.json → *-stories.ts scaffolding
# ---------------------------------------------------------------------------

import re as _re


def _to_slug(name: str) -> str:
    s = _re.sub(r"['\u2019]", "", name)
    return _re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _to_const(name: str) -> str:
    s = _re.sub(r"['\u2019]", "", name)
    return _re.sub(r"[^A-Z0-9]+", "_", s.upper()).strip("_")


def _to_camel(name: str) -> str:
    parts = _re.split(r"[^a-zA-Z0-9]+", name.strip())
    if not parts:
        return ""
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:] if p)


def _ts_str(s: str) -> str:
    return "`" + s.replace("\\", "\\\\").replace("`", "\\`") + "`"


_GHERKIN_KW = {"GIVEN", "WHEN", "THEN", "AND", "BUT"}


def _clean(s: str) -> str:
    s = _re.sub(r"\s+", " ", s).strip()
    return (s.replace("\u2019", "'").replace("\u2018", "'")
             .replace("\u201c", '"').replace("\u201d", '"')
             .replace("\u2013", "-").replace("\u2014", "-"))


def _parse_ac_text(raw: str) -> list:
    steps: list = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("—") or stripped.startswith("-"):
            if steps:
                kw, prev = next(iter(steps[-1].items()))
                bullet = _clean(stripped.lstrip("—- "))
                if bullet:
                    steps[-1] = {kw: prev + "; " + bullet}
            continue
        m = _re.match(r"^(\w+)\s+(.*)", stripped)
        if m and m.group(1).upper() in _GHERKIN_KW:
            text = _clean(m.group(2))
            if text:
                steps.append({m.group(1).lower(): text})
            continue
        if steps and stripped:
            kw, prev = next(iter(steps[-1].items()))
            steps[-1] = {kw: _clean(prev + " " + stripped)}
    return steps


def _scenario_key(steps: list, idx: int) -> str:
    when_text = ""
    then_text = ""
    for step in steps:
        kw, text = next(iter(step.items()))
        if kw == "when" and not when_text:
            when_text = text
        elif kw in ("then", "but") and not then_text:
            then_text = text
    combined = (when_text + " " + then_text).strip()
    words = _re.sub(r"[^a-zA-Z0-9 ]+", " ", combined).split()[:10]
    key = _to_camel(" ".join(words))
    return key if key else f"scenario{idx + 1}"


def _human(key: str) -> str:
    return _re.sub(r"([A-Z])", r" \1", key).lower().strip()


def _render_step(step: dict, indent: int = 6) -> str:
    kw, text = next(iter(step.items()))
    return " " * indent + f"{{ {kw}: {_ts_str(text)} }},"


def _parse_scenario_steps(steps_raw: str) -> list:
    """Parse Gherkin step lines into [{kw: text}, ...] list.

    Handles plain 'Given/When/Then/And/But' prefixes (not bold AC format).
    """
    steps: list = []
    for line in steps_raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("---"):
            continue
        m = _re.match(r"^(Given|When|Then|And|But)\s+(.*)", stripped, _re.IGNORECASE)
        if m:
            kw = m.group(1).lower()
            text = _clean(m.group(2))
            if text:
                steps.append({kw: text})
        elif steps and stripped:
            # Continuation of previous step
            kw, prev = next(iter(steps[-1].items()))
            steps[-1] = {kw: _clean(prev + " " + stripped)}
    return steps


def _examples_const_name(story_name: str, scenario_name: str) -> str:
    """Generate a TypeScript constant name for an EXAMPLES_ARRAY."""
    s = _to_const(story_name)
    # Extract scenario number suffix from name like "Scenario Outline 1: ..."
    m = _re.search(r"(\d+)", scenario_name)
    suffix = f"_{m.group(1)}" if m else ""
    return f"{s}_EXAMPLES{suffix}"


def _render_examples_table(examples: list, const_name: str) -> list[str]:
    """Render examples tables as a typed EXAMPLES_ARRAY constant."""
    out: list[str] = []
    out.append(f"export const {const_name} = [")
    for table in examples:
        table_name = table.get("name", "")
        columns: list = table.get("columns", [])
        rows: list = table.get("rows", [])
        if not columns:
            continue
        out.append("  {")
        out.append(f"    name: {_ts_str(table_name)},")
        out.append(f"    columns: {json.dumps(columns)} as const,")
        out.append("    rows: [")
        for row in rows:
            cells = [json.dumps(c) for c in row]
            out.append(f"      [{', '.join(cells)}],")
        out.append("    ] as const,")
        out.append("  },")
    out.append("] as const")
    return out


def _generate_story_const(story: dict) -> str:
    name   = story["name"]
    actor  = story.get("story_type", "")
    acs    = [_parse_ac_text(r) for r in story.get("acceptance_criteria", []) if r]
    acs    = [a for a in acs if a]
    scenarios_data = story.get("scenarios", [])
    cname  = _to_const(name)

    out: list = []

    # Render EXAMPLES_ARRAY constants before the main export
    examples_consts: list[str] = []
    for sc in scenarios_data:
        if sc.get("type") == "outline" and sc.get("examples"):
            ex_name = _examples_const_name(name, sc.get("name", ""))
            examples_consts.extend(_render_examples_table(sc["examples"], ex_name))
            examples_consts.append("")

    out.extend(examples_consts)

    out.append(f"export const {cname} = {{")
    out.append(f"  story: {_ts_str(name)},")
    out.append(f"  actor: {_ts_str(actor)},")
    out.append("")
    out.append("  acceptance_criteria: [")
    for ac in acs:
        out.append("    [")
        for step in ac:
            out.append("  " + _render_step(step, 4))
        out.append("    ],")
    if not acs:
        out.append("    // TODO: add acceptance criteria")
    out.append("  ] as const satisfies readonly AcceptanceCriterion[],")
    out.append("")
    out.append("  domain_terms: [] as const,")
    out.append("  evidence: [] as const,")
    out.append("")

    # Render scenario objects from spec-by-example data if available
    if scenarios_data:
        for sc in scenarios_data:
            sc_name = sc.get("name", "")
            sc_type = sc.get("type", "plain")
            steps_raw = sc.get("steps", "")
            background_lines: list = sc.get("background", [])

            # Derive a camelCase key from the scenario name
            # Strip "Scenario Outline N: " or "Scenario N: " prefix for the key
            key_text = _re.sub(r"^Scenario\s+(Outline\s+)?\d+[:\s]+", "", sc_name, flags=_re.IGNORECASE).strip()
            words = _re.sub(r"[^a-zA-Z0-9 ]+", " ", key_text).split()[:10]
            key = _to_camel(" ".join(words)) if words else f"scenario{scenarios_data.index(sc) + 1}"

            steps = _parse_scenario_steps(steps_raw) if steps_raw else []
            background_steps = [_parse_ac_text("1. " + b.replace("\n", "\n   ")) for b in background_lines]
            background_steps = [s[0] if s else {} for s in background_steps if s]

            # Reference examples constant if outline
            ex_name = _examples_const_name(name, sc_name) if sc_type == "outline" and sc.get("examples") else None

            out.append(f"  {key}: {{")
            out.append(f"    name: {_ts_str(sc_name)},")
            if ex_name:
                out.append(f"    examples: {ex_name},")
            if background_steps:
                out.append("    background: [")
                for bg in background_steps:
                    if isinstance(bg, dict) and bg:
                        out.append("  " + _render_step(bg, 4))
                out.append("    ] as const satisfies readonly Step[],")
            out.append("    steps: [")
            for step in steps:
                out.append("  " + _render_step(step, 4))
            if not steps:
                out.append("      // TODO: add steps")
            out.append("    ] as const satisfies readonly Step[],")
            out.append("  },")
            out.append("")
    elif acs:
        # Fallback: derive scenario objects from acceptance criteria
        for idx, ac in enumerate(acs):
            key = _scenario_key(ac, idx)
            out.append(f"  {key}: {{")
            out.append(f"    name: {_ts_str(_human(key))},")
            out.append("    steps: [")
            for step in ac:
                out.append("  " + _render_step(step, 4))
            out.append("    ] as const satisfies readonly Step[],")
            out.append("  },")
            out.append("")
    else:
        out.append("  // TODO: add scenarios")
        out.append("")

    out.append("} as const")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# inject-spec command — merge specification-by-example.md into story-graph.json
# ---------------------------------------------------------------------------

_INJECT_STOP_WORDS = frozenset({"a", "an", "the", "and", "or", "of", "to", "for", "in", "on"})
_INJECT_GENERIC_TOKENS = frozenset({"view", "form", "page", "screen", "list", "section"})
_INJECT_SYNONYM_VERBS = {
    "expand": "view",
    "execute": "submit",
    "proceed": "submit",
    "activate": "confirm",
    "pick": "select",
    "keep": "select",
    "choose": "select",
}
# Explicit md-name → graph-name overrides for cases where Jaccard is insufficient.
_INJECT_NAME_MAP: dict[str, str] = {
    "Keep Existing Number": "Select a Phone Number",
    "Pick Vanity Number": "Select a Phone Number",
    "Select Checkout Plan": "Confirm Plan for Checkout",
    "Confirm SIM Type": "Select SIM Type",
    "Confirm ID Details": "Submit Identity Details",
    "Proceed to Payment": "Submit Payment",
    "Activate Customer": "View Activation Confirmation",
    "View Billing Page": "View Billing Summary",
    "View Pay-Now Confirmation": "View Pay Outstanding Balance Screen",
    "Execute Payment": "Submit Outstanding Balance Payment",
}
_INJECT_FUZZY_THRESHOLD = 0.6
_INJECT_STORY_HEADER = _re.compile(r"^##\s+Story:\s+(.+)", _re.MULTILINE)


def _inject_normalize(name: str) -> frozenset[str]:
    tokens = _re.sub(r"[^a-z0-9 ]", " ", name.lower()).split()
    result: list[str] = []
    for t in tokens:
        if t in _INJECT_STOP_WORDS:
            continue
        result.append(_INJECT_SYNONYM_VERBS.get(t, t))
    return frozenset(result)


def _inject_similarity(graph_name: str, md_name: str) -> float:
    a = _inject_normalize(graph_name)
    b = _inject_normalize(md_name)
    if not a or not b:
        return 0.0
    da = a - _INJECT_GENERIC_TOKENS
    db = b - _INJECT_GENERIC_TOKENS
    if not (da & db):
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def _inject_parse_table(text: str) -> dict | None:
    lines = [ln.strip() for ln in text.strip().splitlines()]
    table_lines = [ln for ln in lines if ln.startswith("|")]
    if len(table_lines) < 3:
        return None
    header = [c.strip() for c in table_lines[0].strip("|").split("|")]
    rows: list[list[str]] = []
    for row_line in table_lines[2:]:
        cells = [c.strip() for c in row_line.strip("|").split("|")]
        while len(cells) < len(header):
            cells.append("")
        rows.append(cells[: len(header)])
    return {"columns": header, "rows": rows}


def _inject_parse_examples(block: str) -> list[dict]:
    tables: list[dict] = []
    parts = _re.split(r"^###\s+(.+?):\s*$", block, flags=_re.MULTILINE)
    i = 1
    while i < len(parts) - 1:
        table_name = parts[i].strip()
        content = parts[i + 1]
        i += 2
        parsed = _inject_parse_table(content)
        if parsed:
            parsed["name"] = table_name
            tables.append(parsed)
    return tables


def _inject_parse_background(block: str) -> list[str]:
    steps: list[str] = []
    for line in block.strip().splitlines():
        line = line.strip()
        if _re.match(r"^(Given|When|Then|And|But)\b", line, _re.IGNORECASE):
            steps.append(line)
    return steps


def _inject_parse_step_lines(block: str) -> str:
    steps: list[str] = []
    for line in block.strip().splitlines():
        line = line.strip()
        if _re.match(r"^(Given|When|Then|And|But)\b", line, _re.IGNORECASE):
            steps.append(line)
    return "\n".join(steps)


def _inject_parse_outlines(block: str) -> list[dict]:
    outlines: list[dict] = []
    parts = _re.split(r"^(###\s+.+)$", block, flags=_re.MULTILINE)
    current_name: str | None = None
    steps_text = ""
    i = 1
    while i < len(parts):
        heading = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        i += 2
        if _re.match(r"^###\s+Scenario\s+(Outline\s+)?\d+", heading, _re.IGNORECASE):
            if current_name and steps_text:
                outlines.append({"name": current_name, "steps": steps_text.strip()})
            current_name = _re.sub(r"^###\s+", "", heading).strip()
            steps_text = ""
        elif _re.match(r"^###\s+Steps", heading, _re.IGNORECASE):
            steps_text = _inject_parse_step_lines(content)
    if current_name and steps_text:
        outlines.append({"name": current_name, "steps": steps_text.strip()})
    return outlines


def _inject_parse_plain_scenarios(block: str) -> list[dict]:
    scenarios: list[dict] = []
    parts = _re.split(r"^(###\s+Scenario\s+\d+:.+)$", block, flags=_re.MULTILINE)
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()
        content = parts[i + 1]
        i += 2
        name = _re.sub(r"^###\s+", "", heading).strip()
        steps = _inject_parse_step_lines(content)
        if steps:
            scenarios.append({"name": name, "steps": steps})
    return scenarios


def _inject_parse_story_block(block: str) -> list[dict]:
    sections = _re.split(r"^(##\s+\S.*?)$", block, flags=_re.MULTILINE)
    examples: list[dict] = []
    background: list[str] = []
    outline_scenarios: list[dict] = []
    i = 1
    while i < len(sections) - 1:
        heading = sections[i].strip()
        content = sections[i + 1]
        i += 2
        if _re.match(r"^##\s+Examples", heading):
            examples = _inject_parse_examples(content)
        elif _re.match(r"^##\s+Background", heading):
            background = _inject_parse_background(content)
        elif _re.match(r"^##\s+Scenarios", heading):
            outline_scenarios = _inject_parse_outlines(content)
    preamble = sections[0] if sections else block
    plain_scenarios = _inject_parse_plain_scenarios(preamble)
    result: list[dict] = []
    if outline_scenarios:
        for sc in outline_scenarios:
            d: dict = {"name": sc["name"], "type": "outline", "steps": sc["steps"]}
            if background:
                d["background"] = background
            if examples:
                d["examples"] = examples
            result.append(d)
    elif plain_scenarios:
        for sc in plain_scenarios:
            result.append({"name": sc["name"], "type": "plain", "steps": sc["steps"]})
    return result


def _inject_parse_spec(md_path: Path) -> dict[str, list[dict]]:
    text = md_path.read_text(encoding="utf-8")
    story_blocks = _INJECT_STORY_HEADER.split(text)
    if len(story_blocks) < 3:
        return {}
    result: dict[str, list[dict]] = {}
    i = 1
    while i < len(story_blocks) - 1:
        story_name = story_blocks[i].strip()
        block = story_blocks[i + 1]
        i += 2
        scenarios = _inject_parse_story_block(block)
        if scenarios:
            result[story_name] = scenarios
    return result


def _inject_all_stories(graph: dict) -> list[dict]:
    stories: list[dict] = []
    for epic in graph.get("epics", []):
        stories.extend(_inject_stories_from_node(epic))
    return stories


def _inject_stories_from_node(node: dict) -> list[dict]:
    stories: list[dict] = []
    for sg in node.get("story_groups", []):
        stories.extend(sg.get("stories", []))
    for sub in node.get("sub_epics", []):
        stories.extend(_inject_stories_from_node(sub))
    return stories


def _inject_apply(graph: dict, scenarios_by_story: dict[str, list[dict]]) -> tuple[int, list[str]]:
    graph_stories = _inject_all_stories(graph)
    name_to_idx = {s.get("name", ""): i for i, s in enumerate(graph_stories)}
    md_names = list(scenarios_by_story.keys())

    final: dict[str, tuple[int, float, str]] = {}

    for md_name in md_names:
        graph_name = _INJECT_NAME_MAP.get(md_name)
        if graph_name and graph_name in name_to_idx:
            final[md_name] = (name_to_idx[graph_name], 2.0, "explicit")

    for md_name in md_names:
        if md_name in final:
            continue
        if md_name in name_to_idx:
            final[md_name] = (name_to_idx[md_name], 1.0, "exact")

    remaining = [n for n in md_names if n not in final]
    candidates: list[tuple[float, str, int]] = []
    for md_name in remaining:
        for g_idx, story in enumerate(graph_stories):
            score = _inject_similarity(story.get("name", ""), md_name)
            if score >= _INJECT_FUZZY_THRESHOLD:
                candidates.append((score, md_name, g_idx))
    candidates.sort(reverse=True)

    used_graph: set[int] = {v[0] for v in final.values()}
    for score, md_name, g_idx in candidates:
        if md_name in final or g_idx in used_graph:
            continue
        final[md_name] = (g_idx, score, "fuzzy")
        used_graph.add(g_idx)

    matched: set[str] = set()
    updated = 0
    for md_name, (g_idx, score, match_type) in final.items():
        story = graph_stories[g_idx]
        graph_name = story.get("name", "")
        story["scenarios"] = scenarios_by_story[md_name]
        matched.add(md_name)
        updated += 1
        if match_type == "explicit":
            print(f"  [MAP]   {md_name!r} -> {graph_name!r}")
        elif match_type == "fuzzy":
            print(f"  [FUZZY] {md_name!r} -> {graph_name!r}  ({score:.2f})")

    return updated, [n for n in scenarios_by_story if n not in matched]


def cmd_inject_spec(args: argparse.Namespace) -> int:
    md_path = Path(args.spec)
    graph_path = Path(args.file)

    if not md_path.exists():
        print(f"[ERROR] Spec file not found: {md_path}", file=sys.stderr)
        return 1
    if not graph_path.exists():
        print(f"[ERROR] Graph file not found: {graph_path}", file=sys.stderr)
        return 1

    scenarios_by_story = _inject_parse_spec(md_path)
    if not scenarios_by_story:
        print(f"[FORMAT] No '## Story:' blocks found in {md_path.name}", file=sys.stderr)
        return 2

    print(f"[PARSE] Found scenarios for {len(scenarios_by_story)} stories in {md_path.name}")

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    updated, unmatched = _inject_apply(graph, scenarios_by_story)

    graph_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[WRITE] Updated {updated} stories in {graph_path.name}")

    if unmatched:
        print(f"\n[WARN] {len(unmatched)} story name(s) not matched in graph (no entry added):", file=sys.stderr)
        for name in unmatched:
            print(f"  - {name}", file=sys.stderr)

    print("[OK] inject-spec complete.")
    return 0


# ---------------------------------------------------------------------------
_FLAT_EPICS = {"app-availability", "manage-profile", "view-home-dashboard"}


def _iter_sub_epics(graph: dict):
    for epic in graph.get("epics", []):
        ename = epic["name"]
        if "sub_epics" in epic:
            for sub in epic["sub_epics"]:
                stories: list = []
                for grp in sub.get("story_groups", []):
                    stories.extend(grp.get("stories", []))
                yield ename, sub["name"], stories
        else:
            stories = []
            for grp in epic.get("story_groups", []):
                stories.extend(grp.get("stories", []))
            yield ename, None, stories


def _ts_path(tests_dir: Path, epic_name: str, sub_epic_name) -> Path:
    es = _to_slug(epic_name)
    ss = _to_slug(sub_epic_name) if sub_epic_name else es
    if es in _FLAT_EPICS or es == ss:
        return tests_dir / es / f"{es}-stories.ts"
    return tests_dir / es / ss / f"{ss}-stories.ts"


def _depth_from(ts_path: Path, tests_dir: Path) -> str:
    parts = ts_path.relative_to(tests_dir).parts
    return "../" * (len(parts) - 1) + "story-types"


def _generate_file(epic_name: str, sub_epic_name, stories: list,
                   ts_path: Path, tests_dir: Path) -> str:
    depth = _depth_from(ts_path, tests_dir)
    parts: list = []
    parts.append(f"import type {{ Step, AcceptanceCriterion, Background }} from '{depth}'")
    parts.append("")
    for story in stories:
        bar = "=" * 77
        parts.append(f"// {bar}")
        parts.append(f"// STORY: {story['name']}")
        parts.append(f"// {bar}")
        parts.append("")
        parts.append(_generate_story_const(story))
        parts.append("")
    return "\n".join(parts)


def cmd_generate(args: argparse.Namespace) -> int:
    graph_path = Path(args.file)
    tests_dir  = Path(args.output)
    dry_run    = args.dry_run

    graph = _load_graph(graph_path)

    for epic_name, sub_epic_name, stories in _iter_sub_epics(graph):
        ts_path = _ts_path(tests_dir, epic_name, sub_epic_name)
        content = _generate_file(epic_name, sub_epic_name, stories, ts_path, tests_dir)
        if dry_run:
            print(f"  [dry] {ts_path.relative_to(tests_dir)}")
        else:
            ts_path.parent.mkdir(parents=True, exist_ok=True)
            ts_path.write_text(content, encoding="utf-8")
            n = len(stories)
            print(f"  ok  {ts_path.relative_to(tests_dir)}  ({n} stor{'y' if n == 1 else 'ies'})")

    print("done." if not dry_run else "dry-run complete.")
    return 0


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="story_graph_cli", description="Story graph file operations")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("read", help="Print JSON story graph")
    r.add_argument("--file", required=True, help="Path to story-graph.json")
    r.add_argument("--pretty", action="store_true", help="Indent JSON")
    r.set_defaults(func=cmd_read)

    n = sub.add_parser("names", help="List story names (flat)")
    n.add_argument("--file", required=True)
    n.set_defaults(func=cmd_names)

    s = sub.add_parser("search", help="List story names containing substring (case-insensitive)")
    s.add_argument("--file", required=True)
    s.add_argument("--substring", required=True)
    s.set_defaults(func=cmd_search)

    f = sub.add_parser("filter", help="Emit graph subset containing only named stories")
    f.add_argument("--file", required=True)
    f.add_argument("--stories", required=True, help="Comma-separated story names")
    f.add_argument("--pretty", action="store_true")
    f.set_defaults(func=cmd_filter)

    sh = sub.add_parser(
        "sha",
        help="Print SHA-256 of the file content (capture this at read time for --expect-sha on write)",
    )
    sh.add_argument("--file", required=True)
    sh.set_defaults(func=cmd_sha)

    w = sub.add_parser("write", help="Write JSON from stdin (-) or --input file")
    w.add_argument("--file", required=True, help="Output path")
    w.add_argument("--input", default="-", help="Input JSON path or - for stdin")
    w.add_argument(
        "--expect-sha",
        dest="expect_sha",
        default=None,
        help="Refuse the write (exit 3) if the target file's current SHA-256 differs.",
    )
    w.add_argument(
        "--no-lock",
        dest="no_lock",
        action="store_true",
        help="Skip the advisory lock at <file>.lock (not recommended).",
    )
    w.add_argument(
        "--force",
        action="store_true",
        help="Override both the advisory lock and --expect-sha checks. Use only for recovery.",
    )
    w.set_defaults(func=cmd_write)

    inj = sub.add_parser(
        "inject-spec",
        help="Merge specification-by-example.md scenarios into story-graph.json",
    )
    inj.add_argument("--spec", required=True, help="Path to specification-by-example.md")
    inj.add_argument("--file", required=True, help="Path to story-graph.json (updated in place)")
    inj.set_defaults(func=cmd_inject_spec)

    g = sub.add_parser(
        "generate",
        help="Generate *-stories.ts scaffolding from story-graph.json",
    )
    g.add_argument("--file", required=True, help="Path to story-graph.json")
    g.add_argument("--output", required=True, help="Target tests directory (e.g. pml-domain/tests)")
    g.add_argument("--dry-run", action="store_true", help="Print file paths without writing")
    g.set_defaults(func=cmd_generate)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
