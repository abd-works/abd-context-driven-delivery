"""Offer and write Context Decision Records (CDRs) under the current session workpath .context/cdr/."""
from __future__ import annotations

import re
from pathlib import Path

from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.guidance_actions import load_document
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp
from space.session.session import Session

_FORMAT_PATH = Path(__file__).parent / "CDR-FORMAT.md"
_CDR_NAME_RE = re.compile(r"^(\d{4})-")

@agent_toolset
class RecordDecisions:
    """Offer CDRs sparingly and persist them under the current session workpath .context/cdr/."""

    def _cdr_dir(self) -> Path:
        """CDR directory is the current session workpath ``.context/cdr``."""
        session = Session.current()
        if session is None or session.workpath is None:
            raise ValueError("no current session")
        return Path(session.workpath) / ".context" / "cdr"

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

    def _cdr_path(self, slug: str, number: int | None = None) -> Path:
        """Resolve a CDR path; number defaults to next available (semi-pure)."""
        cdr_dir = self._cdr_dir()
        n = number if number is not None else self._next_cdr_number(cdr_dir)
        return cdr_dir / f"{n:04d}-{slug}.md"

    @mcp
    @skill
    @agent_tool
    def read_cdr_format(self) -> str:
        """Return CDR-FORMAT.md - when to offer a CDR, template, numbering, and optional sections.
        Read this before offering or writing a CDR."""
        return _FORMAT_PATH.read_text(encoding="utf-8")

    @mcp
    @skill
    @agent_tool
    def list_cdrs(self) -> str:
        """List CDR files under the current session workpath .context/cdr/.
        Returns newline-separated paths sorted by filename; empty string if missing or empty."""
        cdr_dir = self._cdr_dir()
        if not cdr_dir.is_dir():
            return ""
        return "\n".join(str(path) for path in sorted(cdr_dir.glob("*.md")))

    @mcp
    @skill
    @agent_tool
    def write_cdr(
        self,
        slug: str,
        content: str = "",
        paths: list[str] | str | None = None,
    ) -> str:
        """Write one Context Decision Record to the current session workpath .context/cdr/{NNNN}-{slug}.md.
        NNNN is the next sequential number under .context/cdr/. Creates the directory lazily.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the record body in content.
        content: in-process text. Leave this empty on an MCP call.
        slug: kebab-case short name (e.g. 'event-sourced-orders').
        Returns the resolved path. Call immediately when a qualifying decision crystallises - do not batch."""
        target = self._cdr_path(slug)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(load_document(content, paths).strip() + "\n", encoding="utf-8")
        return str(target)

    @mcp
    @skill
    @agent_instructions
    def record_decisions_session(self) -> str:
        """Offer and write Context Decision Records (CDRs) sparingly as decisions crystallise during the wrapped action - never batch; never invent decisions."""
        """Step 1 - Read the format once via read_cdr_format. Internalise the three-criteria gate and the minimal template."""
        tools(self.read_cdr_format())
        """Step 2 - Optionally call list_cdrs so you do not re-record an already-captured decision. Records live under the current session workpath .context/cdr/."""
        tools(self.list_cdrs())
        """Step 3 - During the session (grill, sketch, or generate), watch for decisions that meet ALL three: hard to reverse, surprising without context, and a real trade-off. If any criterion is missing, skip the CDR."""
        """Step 4 - When a qualifying decision crystallises, offer a CDR briefly (title + one-line gist). If the user accepts, write the record to a file and call write_cdr immediately with a kebab slug and paths set to that file. Do not pass the record body. Do not batch; do not wait until the end."""
        """Step 5 - Keep CDRs short. Prefer a single paragraph. Add Status / Considered Options / Consequences only when they add genuine value."""
        return "CDR session active."
