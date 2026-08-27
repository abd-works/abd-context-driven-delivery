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

from harness.harness_tool import prompt
from workspace import WorkSession, Workspace, docs_dir
from primitives.actions.action import agent_instructions
from tools.tool import agent_tool, toolset

_STATE_NAMES = (
    "grill-answers.md",
    "cdd-sketch.md",
    "module-context.md",
)

_RESERVED_SLUGS = frozenset({"handoff", "handoff-latest", "latest"})


@toolset
class Handoff:
    """Compact the current conversation into a handoff for the next agent session."""

    def __init__(self, path: str = ".") -> None:
        self.workspace = Workspace(str(path))
        self.workspace.load()

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

    def _context_search_roots(self, destination: str) -> list[Path]:
        """Docs folder for destination, plus parent ``.context`` when destination is a sprint."""
        primary = docs_dir(destination)
        roots = [primary]
        if primary.parent.name == "sessions":
            parent_ctx = primary.parent.parent
            if parent_ctx.is_dir() and parent_ctx.name == ".context":
                roots.append(parent_ctx)
        return roots

    def _first_existing(self, roots: list[Path], name: str) -> Path | None:
        for root in roots:
            candidate = root / name
            if candidate.is_file():
                return candidate
        return None

    def _session_record(self, destination: str) -> dict[str, str] | None:
        """Load session.md Start fields + hand-written progress body when destination is a sprint."""
        dest = Path(destination)
        if dest.parent.name != "sessions":
            return None
        working = str(dest.parent.parent.parent)
        loaded = WorkSession.load(working, dest.name)
        if not loaded.session_md.is_file():
            return None
        return {
            "name": loaded.name or dest.name,
            "goal": loaded.goal,
            "fidelities": loaded.fidelities,
            "contexts": loaded.contexts,
            "progress": loaded.body,
            "started": loaded.started,
        }

    def _collect_state(self, destination: str) -> dict:
        """Assemble generator / grill / CDD / session state under destination (pure + IO)."""
        roots = self._context_search_roots(destination)
        context = roots[0]
        sketches: list[str] = []
        seen_sketches: set[str] = set()
        for root in roots:
            if not root.is_dir():
                continue
            for path in sorted(root.glob("*-sketch.md")):
                if path.name in seen_sketches:
                    continue
                seen_sketches.add(path.name)
                sketches.append(str(path))

        named: dict[str, str | None] = {}
        for name in _STATE_NAMES:
            found = self._first_existing(roots, name)
            named[name] = str(found) if found else None

        cdd_path = self._first_existing(roots, "cdd-sketch.md")
        cdd_text = self._read_if_exists(cdd_path) if cdd_path else None
        grill_path = self._first_existing(roots, "grill-answers.md")
        grill_text = self._read_if_exists(grill_path) if grill_path else None
        index_path = self._find_context_index(Path(destination))
        index_text = self._read_if_exists(index_path) if index_path else None
        session = self._session_record(destination)

        return {
            "destination": str(Path(destination)),
            "working_folder": str(context),
            "sketches": sketches,
            "named_artifacts": named,
            "context_index_path": str(index_path) if index_path else None,
            "context_index": index_text,
            "session": session,
            "cdd": self._summarize_cdd_sketch(cdd_text) if cdd_text else None,
            "grill_answers_exists": grill_text is not None,
            "grill_answers_chars": len(grill_text) if grill_text else 0,
            "grill_headings": self._grill_headings(grill_text) if grill_text else [],
        }

    def _bullet_lines(self, items: list[str]) -> str:
        if not items:
            return "- (none)"
        return "\n".join(f"- {item}" for item in items)

    def _artifact_lines(self, state: dict) -> str:
        lines: list[str] = []
        session = state.get("session") or {}
        if session.get("progress"):
            lines.append(str(Path(state["working_folder"]) / "session.md"))
        for path in state.get("sketches") or []:
            lines.append(path)
        for path in (state.get("named_artifacts") or {}).values():
            if path:
                lines.append(path)
        if state.get("context_index_path"):
            lines.append(state["context_index_path"])
        if not lines:
            return "- (none recorded)"
        # preserve order, drop duplicates
        seen: set[str] = set()
        unique: list[str] = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique.append(line)
        return "\n".join(f"- `{line}`" for line in unique)

    def _resume_block(self, state: dict, next_focus: str) -> str:
        session = state.get("session") or {}
        cdd = state.get("cdd") or {}
        focus = (next_focus or "").strip() or "(not specified)"
        stage = session.get("fidelities") or cdd.get("fidelity") or "(unset)"
        scope = session.get("goal") or cdd.get("scope") or "(unset)"
        log_tail = cdd.get("log_tail") or []
        last_work = log_tail[-1] if log_tail else "(see session progress below)"
        if session.get("progress"):
            first_progress = next(
                (line.strip()[2:].strip() for line in session["progress"].splitlines() if line.strip().startswith("- ")),
                last_work,
            )
            last_work = first_progress
        next_action = (next_focus or "").strip() or cdd.get("flow_next") or "(not specified)"
        return (
            f"- **Stage:** {stage}\n"
            f"- **Last work:** {last_work}\n"
            f"- **Next action:** {next_action}\n"
            f"- **Next focus:** {focus}"
        )

    def _render_handoff_markdown(self, state: dict, *, next_focus: str = "") -> str:
        """Render handoff-latest content from collected state â€” no agent drafting step."""
        session = state.get("session") or {}
        cdd = state.get("cdd") or {}
        title_name = session.get("name") or Path(state["destination"]).name
        lines = [
            f"# Handoff â€” {title_name} ({date.today().isoformat()})",
            "",
            "## Resume",
            "",
            self._resume_block(state, next_focus),
            "",
        ]
        if session.get("progress"):
            lines.extend(["## Session progress", "", session["progress"].strip(), ""])
        if session.get("goal"):
            lines.extend(
                [
                    "## Session",
                    "",
                    f"- **goal:** {session.get('goal') or '(unset)'}",
                    f"- **fidelities:** {session.get('fidelities') or '(unset)'}",
                    f"- **contexts:** {session.get('contexts') or '(unset)'}",
                    "",
                ]
            )
        if cdd:
            lines.extend(
                [
                    "## CDD progress",
                    "",
                    f"- **fidelity:** {cdd.get('fidelity') or '(unset)'}",
                    f"- **scope:** {cdd.get('scope') or '(unset)'}",
                    f"- **flow status:** {cdd.get('flow_status') or '(unset)'}",
                    f"- **flow recommend:** {cdd.get('flow_recommend') or '(unset)'}",
                    f"- **flow next:** {cdd.get('flow_next') or '(unset)'}",
                    "",
                    "### Open",
                    "",
                    self._bullet_lines(cdd.get("open") or []),
                    "",
                    "### Done",
                    "",
                    self._bullet_lines(cdd.get("done") or []),
                    "",
                    "### Log tail",
                    "",
                    self._bullet_lines(cdd.get("log_tail") or []),
                    "",
                ]
            )
        if state.get("grill_headings"):
            lines.extend(
                [
                    "## Grill headings",
                    "",
                    self._bullet_lines(state["grill_headings"]),
                    "",
                ]
            )
        lines.extend(["## Artifacts to read", "", self._artifact_lines(state), ""])
        return "\n".join(lines).rstrip() + "\n"

    def _maybe_close_sprint(self, destination: str, handoff_name: str) -> None:
        """If destination is a sprint under sessions/, write End on session.md."""
        dest = Path(destination)
        if dest.parent.name != "sessions":
            return
        working = str(dest.parent.parent.parent)
        WorkSession.load(working, dest.name).close(outcome="handoff written", handoff=handoff_name)

    # ------------------------------------------------------------------
    # Public tools / actions
    # ------------------------------------------------------------------

    @agent_tool
    def resolve_working_folder(self, destination: str) -> str:
        """Resolve docs folder via docs_dir(destination).
        For a sprint ({path}/.context/sessions/{name}/) writes flat there; otherwise
        {destination}/.context/. Creates the folder if missing. Returns absolute path."""
        folder = docs_dir(destination)
        folder.mkdir(parents=True, exist_ok=True)
        return str(folder.resolve())

    @agent_tool
    def collect_session_state(self, destination: str) -> str:
        """Collect generator, grilling, and CDD progress state under destination.
        destination defaults to the host generator session.folder (sprint under {session.path}/.context/sessions/{name}/) or session.path.
        Returns JSON with: working_folder, sketches, named_artifacts (grill-answers,
        cdd-sketch, module-context), context_index_path + context_index (workspace
        tool roots), cdd summary (fidelity/scope/flow/open/done/log_tail),
        and grill_answers headings. Call this before drafting the handoff - do not invent state."""
        return json.dumps(self._collect_state(destination), indent=2)

    @agent_tool
    def compact_handoff(self, destination: str, next_focus: str = "") -> str:
        """Write handoff-latest.md from session folder state in one call.

        Resolves the working folder, collects generator/grill/CDD/session state,
        renders a structured handoff template, writes the dated archive under
        handoffs/, updates handoff-latest.md, and closes the sprint session when
        destination is under sessions/. Returns the archive path."""
        self.resolve_working_folder(destination)
        content = self.preview_handoff(destination, next_focus=next_focus)
        return self.write_handoff(destination, content, focus=next_focus)

    def preview_handoff(self, destination: str, next_focus: str = "") -> str:
        """Collect + render handoff markdown without writing files or closing a sprint."""
        state = self._collect_state(destination)
        return self._render_handoff_markdown(state, next_focus=next_focus)

    @agent_tool
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

        When destination is a sprint under sessions/, closes the WorkSession (End section).
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

    @prompt
    @agent_instructions
    def handoff_session(self, destination: str, next_focus: str = "") -> str:
        """Compact the current session into a handoff document under the session working folder so a fresh agent can continue. Tailor the doc to {{next_focus}} when provided."""
        """If a work session is already open, open a turn for this handoff. Do not open a session."""
        session = self.workspace.current_work_session
        if session is not None:
            session.turn.action = "handoff"
        """Call compact_handoff(destination, next_focus). Tell the user the returned archive path and paste the Resume block from the written file."""
        self.compact_handoff()
        """If a turn is open, finish it. If there is no session, skip."""
        if session is not None and session.open_turn is not None:
            session.open_turn.finish(result="handoff written")
        return "Handoff written for {{destination}}."
