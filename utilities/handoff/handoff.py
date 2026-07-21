# @toolset-manifest python -m tools manifest handoff.handoff:Handoff
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Handoff — compact the current session so a fresh agent can continue.

Writes into the session working folder (where sketches, grill answers, and
generated docs already live) — not the OS temp directory.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from primitives.actions.action import action
from tools.tool import tool, toolset

_STATE_NAMES = (
    "grill-answers.md",
    "cdd-sketch.md",
    "module-context.md",
)


def _context_dir(destination: str) -> Path:
    """Resolve the .context directory under the session working folder (pure)."""
    return Path(destination) / ".context"


def _handoff_path(destination: str, slug: str = "handoff") -> Path:
    """Resolve `{destination}/.context/{slug}.md` (pure)."""
    return _context_dir(destination) / f"{slug}.md"


def _latest_handoff_path(destination: str) -> Path:
    """Resolve `{destination}/.context/handoff-latest.md` (pure)."""
    return _context_dir(destination) / "handoff-latest.md"


def _read_if_exists(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _summarize_cdd_sketch(text: str) -> dict:
    """Pull fidelity / flow / open / done lines from a cdd-sketch body (pure)."""
    summary: dict = {
        "fidelity": None,
        "scope": None,
        "flow_status": None,
        "flow_recommend": None,
        "flow_next": None,
        "open": [],
        "done": [],
        "log_tail": [],
    }
    section: str | None = None
    log_lines: list[str] = []
    in_log = False
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("fidelity:"):
            summary["fidelity"] = stripped.split(":", 1)[1].strip()
            continue
        if stripped.startswith("scope:"):
            summary["scope"] = stripped.split(":", 1)[1].strip()
            continue
        if stripped == "flow:":
            section = "flow"
            continue
        if stripped.startswith("## log"):
            in_log = True
            section = None
            continue
        if in_log:
            if stripped.startswith("- "):
                log_lines.append(stripped[2:].strip())
            continue
        if section == "flow":
            if stripped.startswith("status:"):
                summary["flow_status"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("recommend:"):
                summary["flow_recommend"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("next:"):
                summary["flow_next"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("open:"):
                section = "open"
            elif stripped.startswith("done:"):
                section = "done"
            continue
        if section in ("open", "done"):
            if stripped.startswith("done:"):
                section = "done"
                continue
            if stripped.startswith("open:"):
                section = "open"
                continue
            if stripped.startswith("- "):
                summary[section].append(stripped[2:].strip())
            elif stripped and not stripped.startswith("#"):
                # left the open/done lists
                section = None
    summary["log_tail"] = log_lines[-5:]
    return summary


def _collect_state(destination: str) -> dict:
    """Assemble generator / grill / CDD state under destination (pure + IO)."""
    context = _context_dir(destination)
    sketches = sorted(str(p) for p in context.glob("*-sketch.md")) if context.is_dir() else []
    named: dict[str, str | None] = {}
    for name in _STATE_NAMES:
        path = context / name
        named[name] = str(path) if path.is_file() else None

    cdd_path = context / "cdd-sketch.md"
    cdd_text = _read_if_exists(cdd_path)
    grill_path = context / "grill-answers.md"
    grill_text = _read_if_exists(grill_path)

    return {
        "destination": str(Path(destination)),
        "working_folder": str(context),
        "sketches": sketches,
        "named_artifacts": named,
        "cdd": _summarize_cdd_sketch(cdd_text) if cdd_text else None,
        "grill_answers_exists": grill_text is not None,
        "grill_answers_chars": len(grill_text) if grill_text else 0,
        "grill_headings": _grill_headings(grill_text) if grill_text else [],
    }


def _grill_headings(text: str) -> list[str]:
    """Extract ### headings from grill-answers.md (pure)."""
    return [
        line[4:].strip()
        for line in text.splitlines()
        if line.startswith("### ")
    ]


@toolset
class Handoff:
    """Compact the current conversation into a handoff for the next agent session."""

    @tool
    def resolve_working_folder(self, destination: str) -> str:
        """Resolve the session working folder where docs are generated.
        destination is the engagement / module folder already in play (same root used by
        save_sketch and write_grill_answer). Returns {destination}/.context as an absolute path.
        Creates the folder if missing."""
        folder = _context_dir(destination)
        folder.mkdir(parents=True, exist_ok=True)
        return str(folder.resolve())

    @tool
    def collect_session_state(self, destination: str) -> str:
        """Collect generator, grilling, and CDD progress state under destination.
        Returns JSON with: working_folder, sketches, named_artifacts (grill-answers,
        cdd-sketch, module-context), cdd summary (fidelity/scope/flow/open/done/log_tail),
        and grill_answers headings. Call this before drafting the handoff — do not invent state."""
        return json.dumps(_collect_state(destination), indent=2)

    @tool
    def write_handoff(
        self,
        destination: str,
        content: str,
        slug: str = "handoff",
    ) -> str:
        """Persist a handoff document to {destination}/.context/{slug}.md.
        Also overwrites {destination}/.context/handoff-latest.md for a stable resume pointer.
        destination is the session working root (same folder used for sketches / grill answers).
        Returns the primary handoff path."""
        primary = _handoff_path(destination, slug)
        primary.parent.mkdir(parents=True, exist_ok=True)
        primary.write_text(content, encoding="utf-8")
        latest = _latest_handoff_path(destination)
        if primary.resolve() != latest.resolve():
            latest.write_text(content, encoding="utf-8")
        return str(primary.resolve())

    @action
    def handoff_session(self, destination: str, next_focus: str = "") -> str:
        """Compact the current conversation into a handoff document under the session working folder so a fresh agent can continue. Tailor the doc to {{next_focus}} when provided."""
        """Step 1 — Resolve the working folder: call resolve_working_folder(destination). destination is where sketches, grill answers, and generated docs for this session already live — never the OS temp directory."""
        self.resolve_working_folder()
        """Step 2 — Call collect_session_state(destination). Use the returned JSON as ground truth for generator state (sketches), grilling state (grill-answers headings), and CDD progress (cdd-sketch fidelity/flow/open/done). Read named artifact files only when you need specifics; prefer paths and short summaries."""
        self.collect_session_state()
        """Step 3 — Draft the handoff in chat first. Required sections:
        1. Next session focus (from next_focus, or 'not specified')
        2. Resume in three lines — (a) stage × active generator/skill × scope, (b) last work accepted or in flight, (c) exact next action / skill / generator to invoke
        3. Generator state — active toolset(s), fidelity, sketch paths from collect_session_state
        4. Grilling / skills state — grill-answers path + heading list; suggested skills the next agent should invoke
        5. CDD progress — fidelity, scope, flow status/recommend/next, open items, done, log tail (omit if no cdd-sketch)
        6. Artifacts to read — paths only; do not duplicate PRDs, plans, ADRs, issues, commits, diffs, or full grill/sketch bodies
        7. Open questions / risks — only what is not already captured in grill-answers or the sketch"""
        """Step 4 — Redact secrets (API keys, passwords, PII). Keep the document short enough that a fresh agent can act without re-reading the whole chat."""
        """Step 5 — Call write_handoff(destination, content) with the final markdown. Confirm the written path to the user and paste the three-line resume."""
        self.write_handoff()
        return f"Handoff written for {date.today().isoformat()} under {{{{destination}}}}."
