# @toolset-manifest python -m tools manifest handoff.handoff:Handoff
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Handoff - compact the current session so a fresh agent can continue.

Writes into the sprint folder (session.folder) when destination is a named sprint -
not the OS temp directory.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from workspace import Session, docs_dir
from primitives.actions.action import action
from tools.tool import tool, toolset

_STATE_NAMES = (
    "grill-answers.md",
    "cdd-sketch.md",
    "module-context.md",
)

_RESERVED_SLUGS = frozenset({"handoff", "handoff-latest", "latest"})


@toolset
class Handoff:
    """Compact the current conversation into a handoff for the next agent session."""

    # ------------------------------------------------------------------
    # Private helpers (pure unless noted)
    # ------------------------------------------------------------------

    def _kebab_focus(self, focus: str) -> str:
        """Turn next_focus / label into a short kebab fragment (pure)."""
        cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in focus.strip())
        while "--" in cleaned:
            cleaned = cleaned.replace("--", "-")
        return cleaned.strip("-")

    def _archive_slug(self, focus: str = "", today: date | None = None) -> str:
        """Build archive slug handoff-YYYY-MM-DD or handoff-YYYY-MM-DD-{focus} (pure)."""
        day = (today or date.today()).isoformat()
        fragment = self._kebab_focus(focus) if focus else ""
        if fragment:
            return f"handoff-{day}-{fragment}"
        return f"handoff-{day}"

    def _resolve_archive_slug(self, slug: str = "", focus: str = "", today: date | None = None) -> str:
        """Prefer explicit archive slug; otherwise date (+ optional focus). Never plain handoff (pure)."""
        cleaned = (slug or "").strip()
        if cleaned.startswith("handoff-") and cleaned not in _RESERVED_SLUGS:
            return cleaned
        fragment = (focus or "").strip()
        if not fragment and cleaned and cleaned not in _RESERVED_SLUGS:
            fragment = cleaned
        return self._archive_slug(focus=fragment, today=today)

    def _handoffs_dir(self, destination: str) -> Path:
        """Resolve handoffs/ archive folder under docs_dir(destination) (pure)."""
        return docs_dir(destination) / "handoffs"

    def _handoff_path(self, destination: str, slug: str) -> Path:
        """Resolve archive handoff markdown under docs_dir(destination)/handoffs/ (pure)."""
        return self._handoffs_dir(destination) / f"{slug}.md"

    def _latest_handoff_path(self, destination: str) -> Path:
        """Resolve handoff-latest.md at docs root (resume pointer; not in handoffs/) (pure)."""
        return docs_dir(destination) / "handoff-latest.md"

    def _context_dir(self, destination: str) -> Path:
        """Alias for docs_dir - kept for specs / callers (pure)."""
        return docs_dir(destination)

    def _read_if_exists(self, path: Path) -> str | None:
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")

    def _summarize_cdd_sketch(self, text: str) -> dict:
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
                    section = None
        summary["log_tail"] = log_lines[-5:]
        return summary

    def _grill_headings(self, text: str) -> list[str]:
        """Extract ### headings from grill-answers.md (pure)."""
        return [
            line[4:].strip()
            for line in text.splitlines()
            if line.startswith("### ")
        ]

    def _find_context_index(self, start: Path) -> Path | None:
        """Walk up from start looking for ``.context/context-index.md``."""
        for folder in [start, *start.resolve().parents]:
            candidate = folder / ".context" / "context-index.md"
            if candidate.is_file():
                return candidate
        return None

    def _collect_state(self, destination: str) -> dict:
        """Assemble generator / grill / CDD state under destination (pure + IO)."""
        context = docs_dir(destination)
        sketches = sorted(str(p) for p in context.glob("*-sketch.md")) if context.is_dir() else []
        named: dict[str, str | None] = {}
        for name in _STATE_NAMES:
            path = context / name
            named[name] = str(path) if path.is_file() else None

        cdd_path = context / "cdd-sketch.md"
        cdd_text = self._read_if_exists(cdd_path)
        grill_path = context / "grill-answers.md"
        grill_text = self._read_if_exists(grill_path)
        index_path = self._find_context_index(Path(destination))
        index_text = self._read_if_exists(index_path) if index_path else None

        return {
            "destination": str(Path(destination)),
            "working_folder": str(context),
            "sketches": sketches,
            "named_artifacts": named,
            "context_index_path": str(index_path) if index_path else None,
            "context_index": index_text,
            "cdd": self._summarize_cdd_sketch(cdd_text) if cdd_text else None,
            "grill_answers_exists": grill_text is not None,
            "grill_answers_chars": len(grill_text) if grill_text else 0,
            "grill_headings": self._grill_headings(grill_text) if grill_text else [],
        }

    def _maybe_close_sprint(self, destination: str, handoff_name: str) -> None:
        """If destination is a sprint under sessions/, write End on session.md."""
        dest = Path(destination)
        if dest.parent.name != "sessions":
            return
        working = str(dest.parent.parent.parent)
        Session.load(working, dest.name).close(outcome="handoff written", handoff=handoff_name)

    # ------------------------------------------------------------------
    # Public tools / actions
    # ------------------------------------------------------------------

    @tool
    def resolve_working_folder(self, destination: str) -> str:
        """Resolve docs folder via docs_dir(destination).
        For a sprint ({path}/.context/sessions/{name}/) writes flat there; otherwise
        {destination}/.context/. Creates the folder if missing. Returns absolute path."""
        folder = docs_dir(destination)
        folder.mkdir(parents=True, exist_ok=True)
        return str(folder.resolve())

    @tool
    def collect_session_state(self, destination: str) -> str:
        """Collect generator, grilling, and CDD progress state under destination.
        destination defaults to the host generator session.folder (sprint under {session.path}/.context/sessions/{name}/) or session.path.
        Returns JSON with: working_folder, sketches, named_artifacts (grill-answers,
        cdd-sketch, module-context), context_index_path + context_index (workspace
        tool roots), cdd summary (fidelity/scope/flow/open/done/log_tail),
        and grill_answers headings. Call this before drafting the handoff - do not invent state."""
        return json.dumps(self._collect_state(destination), indent=2)

    @tool
    def write_handoff(
        self,
        destination: str,
        content: str,
        slug: str = "",
        focus: str = "",
    ) -> str:
        """Persist an archived handoff under docs_dir(destination)/handoffs/{slug}.md
        and overwrite handoff-latest.md at the docs root as the stable resume pointer.

        Naming: slug defaults to handoff-YYYY-MM-DD, or handoff-YYYY-MM-DD-{focus}
        when focus (or a non-archive slug) is provided. Do not use plain 'handoff'
        or 'handoff-latest' as the archive name - those are reserved.

        When destination is a sprint under sessions/, closes the Session (End section).
        Returns the archive handoff path."""
        archive_slug = self._resolve_archive_slug(slug=slug, focus=focus)
        if archive_slug in _RESERVED_SLUGS or archive_slug == "handoff-latest":
            raise ValueError(
                f"Invalid handoff archive slug {archive_slug!r}; "
                "use handoff-YYYY-MM-DD or handoff-YYYY-MM-DD-{focus}"
            )
        primary = self._handoff_path(destination, archive_slug)
        primary.parent.mkdir(parents=True, exist_ok=True)
        primary.write_text(content, encoding="utf-8")
        latest = self._latest_handoff_path(destination)
        latest.parent.mkdir(parents=True, exist_ok=True)
        latest.write_text(content, encoding="utf-8")
        self._maybe_close_sprint(destination, f"handoffs/{primary.name}")
        return str(primary.resolve())

    @action
    def handoff_session(self, destination: str, next_focus: str = "") -> str:
        """Compact the current conversation into a handoff document under the session working folder so a fresh agent can continue. Tailor the doc to {{next_focus}} when provided."""
        """Step 1 - Resolve the working folder: call resolve_working_folder(destination) where destination is the host generator session.folder (sprint under {session.path}/.context/sessions/{name}/) or session.path. Never the OS temp directory."""
        self.resolve_working_folder()
        """Step 2 - Call collect_session_state(destination). Use the returned JSON as ground truth for generator state (sketches), grilling state (grill-answers headings), and CDD progress (cdd-sketch fidelity/flow/open/done). Read named artifact files only when you need specifics; prefer paths and short summaries."""
        self.collect_session_state()
        """Step 3 - Draft the handoff in chat first. Required sections:
        1. Next session focus (from next_focus, or 'not specified')
        2. Resume in three lines - (a) stage x active generator/skill x scope, (b) last work accepted or in flight, (c) exact next action / skill / generator to invoke
        3. Generator state - active toolset(s), fidelity, sketch paths from collect_session_state; include context_index_path and the Current tool=root lines (where Stories/CE/Bdd/Ux put work - defaults or overrides)
        4. Grilling / skills state - grill-answers path + heading list; suggested skills the next agent should invoke
        5. CDD progress - fidelity, scope, flow status/recommend/next, open items, done, log tail (omit if no cdd-sketch)
        6. Artifacts to read - paths only; always list context-index.md when present; do not duplicate PRDs, plans, ADRs, issues, commits, diffs, or full grill/sketch bodies
        7. Open questions / risks - only what is not already captured in grill-answers or the sketch"""
        """Step 4 - Redact secrets (API keys, passwords, PII). Keep the document short enough that a fresh agent can act without re-reading the whole chat."""
        """Step 5 - Call write_handoff(destination, content, focus=next_focus) so the archive is
        handoffs/handoff-YYYY-MM-DD or handoffs/handoff-YYYY-MM-DD-{{kebab-focus}} and
        handoff-latest.md (docs root) is updated. Never write a plain handoff.md archive.
        Confirm the archive path to the user and paste the three-line resume."""
        self.write_handoff()
        return f"Handoff written for {date.today().isoformat()} under {{{{destination}}}}."
