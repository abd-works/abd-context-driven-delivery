"""Granola - file unorganized Granola notes into folders, and bring notes into a folder's .context.

Granola itself is reached through the Granola MCP connector (list_meetings,
list_meeting_folders, create_folder, add_note_to_folder, get_meetings).
The recipes tell the agent which Granola calls to make; the tools here do the
local work - render the filing plan for confirmation and write context files.
"""
from __future__ import annotations

import json
from pathlib import Path

from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.installation.context_config import CONTEXT_FOLDER
from harness.annotations.name import Name
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp

_CONTEXT_SUBFOLDER = "granola"
# A note's file is named for its date and title; a long title is cut so the name stays readable in a folder listing.
_TITLE_LENGTH_IN_FILE_NAME = 60
# Where the filing plan lists a note the agent could not place, and the folder name the organize recipe tells it to use.
REVIEW_FOLDER = "Review Before Filing"


@agent_toolset
class Granola:
    """Organize Granola notes into folders and capture notes as independent .context files, in the project the call
    works on."""

    def __init__(self, project: Path | str) -> None:
        self._root = Path(project).resolve()

    @classmethod
    @tool_subject
    def of_project(cls, project: Path) -> Granola:
        """Granola working in project, the project the running call names, so a relative folder is that project's."""
        return cls(project)

    @property
    def root(self) -> Path:
        """The project folder that relative folders resolve against."""
        return self._root

    def _slug(self, title: str) -> str:
        """The part of a note's file name that comes from its title."""
        slug = Name(title).title_slug
        return slug[:_TITLE_LENGTH_IN_FILE_NAME].rstrip("-") or "untitled"

    def _context_dir(self, folder: str) -> Path:
        """{folder}/.context/granola in the project."""
        return (self._root / folder / CONTEXT_FOLDER / _CONTEXT_SUBFOLDER).resolve()

    @mcp
    @skill
    @agent_tool
    def format_filing_plan(self, plan: str) -> str:
        """Render a filing plan for the user to confirm.
        plan: JSON list of {"note_id", "title", "date", "folder", "new_folder": bool, "reason"}.
        Returns markdown grouped by folder, new folders marked (new), with a total count.
        Every note appears exactly once; a note with an empty folder is listed under Review Before Filing."""
        notes = json.loads(plan)
        by_folder = self._by_folder(notes)
        new_folders = {self._folder_of(note) for note in notes if note.get("new_folder")}
        lines = [f"Filing plan - {len(notes)} notes into {len(by_folder)} folders", ""]
        for folder in sorted(by_folder):
            marker = " (new)" if folder in new_folders else ""
            lines += [f"## {folder}{marker}", *(self._plan_line(note) for note in by_folder[folder]), ""]
        return "\n".join(lines).rstrip() + "\n"

    def _folder_of(self, note: dict) -> str:
        return note.get("folder") or REVIEW_FOLDER

    def _by_folder(self, notes: list[dict]) -> dict[str, list[dict]]:
        """The plan's notes grouped by the folder each is filed in, in the order the plan lists them."""
        groups: dict[str, list[dict]] = {}
        for note in notes:
            groups.setdefault(self._folder_of(note), []).append(note)
        return groups

    def _plan_line(self, note: dict) -> str:
        reason = f" - {note['reason']}" if note.get("reason") else ""
        return f"- {note.get('title') or 'Untitled'} ({note.get('date', '')}){reason}"

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
        tools(self.format_filing_plan)
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
        tools(self.list_note_context)
        """Step 2 - Call Granola get_meetings for the resolved ids to get each note's title, date, url, summary and notes."""
        tools(self.write_note_context)
        """Step 3 - Call write_note_context once per note with the note content verbatim. Each file stands alone: do not merge notes or summarise across them."""
        """Step 4 - Report the paths written under {{folder}}/.context/granola."""
        return "Granola notes {{notes}} captured into {{folder}}/.context/granola."
