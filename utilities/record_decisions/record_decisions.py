# @toolset-manifest python -m tools manifest record_decisions.record_decisions:RecordDecisions
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Offer and write Context Decision Records (CDRs) in .context/cdr/ as decisions crystallise."""
from __future__ import annotations

import re
from pathlib import Path

from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool

_FORMAT_PATH = Path(__file__).parent / "CDR-FORMAT.md"
_CDR_NAME_RE = re.compile(r"^(\d{4})-")


@agentic_toolset
class RecordDecisions:
    """Offer CDRs sparingly and persist them under .context/cdr/."""

    def _cdr_dir(self, root: str) -> Path:
        """Resolve the CDR directory under a workspace root (pure)."""
        return Path(root) / ".context" / "cdr"

    def _next_cdr_number(self, cdr_dir: Path) -> int:
        """Return the next sequential CDR number from existing files (pure)."""
        if not cdr_dir.is_dir():
            return 1
        highest = 0
        for path in cdr_dir.iterdir():
            if not path.is_file():
                continue
            match = _CDR_NAME_RE.match(path.name)
            if match:
                highest = max(highest, int(match.group(1)))
        return highest + 1

    def _cdr_path(self, root: str, slug: str, number: int | None = None) -> Path:
        """Resolve a CDR path; number defaults to next available (semi-pure)."""
        cdr_dir = self._cdr_dir(root)
        n = number if number is not None else self._next_cdr_number(cdr_dir)
        return cdr_dir / f"{n:04d}-{slug}.md"

    @agent_tool
    def read_cdr_format(self) -> str:
        """Return CDR-FORMAT.md - when to offer a CDR, template, numbering, and optional sections.
        Read this before offering or writing a CDR."""
        return _FORMAT_PATH.read_text(encoding="utf-8")

    @agent_tool
    def list_cdrs(self, root: str) -> str:
        """List CDR files under {root}/.context/cdr/.
        Returns newline-separated paths sorted by filename; empty string if missing or empty."""
        cdr_dir = self._cdr_dir(root)
        if not cdr_dir.is_dir():
            return ""
        return "\n".join(str(path) for path in sorted(cdr_dir.glob("*.md")))

    @agent_tool
    def write_cdr(self, root: str, slug: str, content: str) -> str:
        """Write one Context Decision Record to {root}/.context/cdr/{NNNN}-{slug}.md.
        NNNN is the next sequential number under .context/cdr/. Creates the directory lazily.
        content: full markdown following CDR-FORMAT.md (title + 1-3 sentence body; optional sections only when valuable).
        slug: kebab-case short name (e.g. 'event-sourced-orders').
        Returns the resolved path. Call immediately when a qualifying decision crystallises - do not batch."""
        target = self._cdr_path(root, slug)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.strip() + "\n", encoding="utf-8")
        return str(target)

    @prompt(name="record-decisions-session")
    @agent_instructions
    def record_decisions_session(self, root: str = ".") -> str:
        """Offer and write Context Decision Records (CDRs) sparingly as decisions crystallise during the wrapped action - never batch; never invent decisions."""
        """Step 1 - Read the format once via read_cdr_format. Internalise the three-criteria gate and the minimal template."""
        self.read_cdr_format()
        """Step 2 - Optionally call list_cdrs(root) so you do not re-record an already-captured decision."""
        self.list_cdrs()
        """Step 3 - During the session (grill, sketch, or generate), watch for decisions that meet ALL three: hard to reverse, surprising without context, and a real trade-off. If any criterion is missing, skip the CDR."""
        """Step 4 - When a qualifying decision crystallises, offer a CDR briefly (title + one-line gist). If the user accepts, call write_cdr immediately with a kebab slug and content matching CDR-FORMAT.md. Do not batch; do not wait until the end."""
        self.write_cdr()
        """Step 5 - Keep CDRs short. Prefer a single paragraph. Add Status / Considered Options / Consequences only when they add genuine value."""
        return "CDR session active for {{root}}."
