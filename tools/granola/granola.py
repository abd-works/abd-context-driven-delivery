"""Granola - file unorganized Granola notes into folders, and bring notes into a folder's .context.

Granola itself is reached through the Granola MCP connector (list_meetings,
list_meeting_folders, create_folder, add_note_to_folder, get_meetings).
The recipes tell the agent which Granola calls to make; the tools here do the
local work - render the filing plan for confirmation and write context files.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_CONTEXT_SUBFOLDER = "granola"


@agent_toolset
class Granola:
    """Organize Granola notes into folders and capture notes as independent .context files."""

    def __init__(self, path: str = ".") -> None:
        """Anchor relative folders at {path}."""
        self._root = Path(path)
        super().__init__()

    @property
    def root(self) -> Path:
        """Workspace root that relative folders resolve against."""
        return self._root

    def _slug(self, title: str) -> str:
        """Kebab-case slug for a note title (pure)."""
        slug = _SLUG_RE.sub("-", title.lower()).strip("-")
        return slug[:60].rstrip("-") or "untitled"

    def _context_dir(self, folder: str) -> Path:
        """Resolve {folder}/.context/granola under the root (pure)."""
        return (self._root / folder / ".context" / _CONTEXT_SUBFOLDER).resolve()

    @mcp
    @skill
    @agent_tool
    def format_filing_plan(self, plan: str) -> str:
        """Render a filing plan for the user to confirm.
        plan: JSON list of {"note_id", "title", "date", "folder", "new_folder": bool, "reason"}.
        Returns markdown grouped by folder, new folders marked (new), with a total count.
        Every note appears exactly once; a note with an empty folder is listed under Review Before Filing."""
        entries = json.loads(plan)
        groups: dict[str, list[dict]] = {}
        new_folders: set[str] = set()
        for entry in entries:
            folder = entry.get("folder") or "Review Before Filing"
            groups.setdefault(folder, []).append(entry)
            if entry.get("new_folder"):
                new_folders.add(folder)
        lines = [f"Filing plan - {len(entries)} notes into {len(groups)} folders", ""]
        for folder in sorted(groups):
            marker = " (new)" if folder in new_folders else ""
            lines.append(f"## {folder}{marker}")
            for entry in groups[folder]:
                reason = f" - {entry['reason']}" if entry.get("reason") else ""
                lines.append(f"- {entry.get('title') or 'Untitled'} ({entry.get('date', '')}){reason}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    @mcp
    @skill
    @agent_tool
    def list_note_context(self, folder: str) -> str:
        """List Granola context files already in {folder}/.context/granola.
        Returns newline-separated paths sorted by filename; empty string when there are none."""
        context_dir = self._context_dir(folder)
        if not context_dir.is_dir():
            return ""
        return "\n".join(str(path) for path in sorted(context_dir.glob("*.md")))

    @mcp
    @skill
    @agent_tool
    def write_note_context(self, folder: str, note_id: str, title: str, date: str, url: str, content: str) -> str:
        """Write one Granola note as an independent context file in {folder}/.context/granola/{date}-{slug}.md.
        date: YYYY-MM-DD of the meeting. content: the note's summary and notes as markdown, verbatim from Granola.
        Front matter marks the file as Granola source with note_id, title, date and url.
        Overwrites the file for the same note so re-running refreshes it. Returns the written path."""
        context_dir = self._context_dir(folder)
        context_dir.mkdir(parents=True, exist_ok=True)
        target = context_dir / f"{date}-{self._slug(title)}.md"
        front = "\n".join([
            "---",
            "source: granola",
            f"note_id: {note_id}",
            f"title: {json.dumps(title)}",
            f"date: {date}",
            f"url: {url}",
            "---",
        ])
        target.write_text(f"{front}\n\n# {title}\n\n{content.strip()}\n", encoding="utf-8")
        return str(target)

    @mcp
    @skill
    @agent_instructions
    def organize(self, scope: str = "unfiled") -> str:
        """Suggest a folder for each unorganized Granola note; after the user confirms, create any new folders and file the notes."""
        """Step 1 - Call Granola list_meeting_folders to learn the existing folders, their ids and visibility.
        Call Granola list_meetings with a custom range covering all history (paginate until has_more is false).
        Keep the notes that match {{scope}}: "unfiled" means notes whose folders element is empty; "all" means every note."""
        """Step 2 - For each note, read its title and note headings; call Granola get_meetings on notes whose title is blank, generic ("New note") or ambiguous.
        Prefer an existing folder. Propose a new folder only when several notes share a theme no existing folder covers.
        Put notes you cannot place with confidence in "Review Before Filing" with a short reason."""
        tools(self.format_filing_plan())
        """Step 3 - Show the rendered plan to the user and ask for confirmation. Apply any changes they ask for and show the plan again.
        Create and move nothing until the user confirms."""
        """Step 4 - On confirmation, call Granola create_folder for each new folder (private unless the user asked for a shared folder),
        then Granola add_note_to_folder for each note into its folder id. A note is added, not moved: leave existing folder memberships alone unless the user asks to remove them (Granola remove_note_from_folder)."""
        """Step 5 - Report folders created, notes filed per folder, and any call that failed."""
        return "Granola notes in scope {{scope}} organized after user confirmation."

    @mcp
    @skill
    @agent_instructions
    def context(self, notes: str, folder: str) -> str:
        """Bring one or more Granola notes into {folder}/.context as independent context files, one file per note."""
        """Step 1 - Resolve {{notes}} to Granola note ids: use ids or Granola URLs as given; for titles or topics call Granola search_meetings, and confirm with the user when a name matches more than one note."""
        tools(self.list_note_context())
        """Step 2 - Call Granola get_meetings for the resolved ids to get each note's title, date, url, summary and notes."""
        tools(self.write_note_context())
        """Step 3 - Call write_note_context once per note with the note content verbatim. Each file stands alone: do not merge notes or summarise across them."""
        """Step 4 - Report the paths written under {{folder}}/.context/granola."""
        return "Granola notes {{notes}} captured into {{folder}}/.context/granola."
