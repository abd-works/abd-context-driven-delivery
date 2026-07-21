"""StoryContext — the `story-context.md` on-request aggregate placed at an epic or sub-epic root."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

from .source_location import SourceLocation

_H1 = re.compile(r"^#\s+(.+?)\s*$")
_STATUS_LABEL = re.compile(r"^\s*\*\*Status:\*\*", re.IGNORECASE)
_STORIES_IN_SCOPE_LABEL = re.compile(r"^\s*\*\*Stories in scope:\*\*", re.IGNORECASE)
_CONTEXT_NOTES_LABEL = re.compile(r"^\s*\*\*Context\s*/\s*notes:\*\*", re.IGNORECASE)
_ITALIC_BACKTICK_BULLET = re.compile(r"^\s*[-*]\s+\*?`?([^`*\n]+?)`?\*?\s*$")


@dataclass
class StoryContext:
    """One `story-context.md` file placed at the root of an epic or sub-epic folder.

    story-context.md is an on-request aggregate: it sits at the top of a story
    map (or, occasionally, at the top of a sub-epic being expanded) and gives
    humans a single-page narrative view over the machine-readable spec files
    below it. It is never emitted at a leaf/story folder.

    Fields describe what the file contained, so scanners can enforce placement
    and minimum shape without re-parsing text:

    - `folder` — folder that contained the file (relative to workspace root)
    - `title` — the H1 title (typically an epic or sub-epic verb–noun)
    - `has_status`, `has_stories_in_scope`, `has_context_notes` — presence flags
      for the labelled sections in the canonical template
    - `stories_in_scope` — the verb–noun items enumerated under Stories in scope
    - `is_leaf_folder` — true if the containing folder has no child sub-folders
      (i.e. a story-level folder); placement rule uses this to flag violations
    """

    folder: str = ""
    title: str = ""
    has_status: bool = False
    has_stories_in_scope: bool = False
    has_context_notes: bool = False
    stories_in_scope: List[str] = field(default_factory=list)
    is_leaf_folder: bool = False
    source: Optional[SourceLocation] = None

    @classmethod
    def from_workspace(cls, root: Path) -> List["StoryContext"]:
        """Find every story-context.md under *root* and parse each one."""
        root = Path(root).resolve()
        seen: set = set()
        contexts: List[StoryContext] = []
        for path in root.rglob("story-context.md"):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            contexts.append(cls._parse_file(path, root))
        return contexts

    @classmethod
    def _parse_file(cls, path: Path, root: Path) -> "StoryContext":
        rel_path = path.relative_to(root).as_posix() if path.is_absolute() else str(path)
        rel_folder = path.parent.relative_to(root).as_posix() if path.is_absolute() else ""
        text = path.read_text(encoding="utf-8", errors="replace")

        ctx = cls(
            folder=rel_folder or ".",
            source=SourceLocation(rel_path, 1),
            is_leaf_folder=cls._is_leaf_folder(path.parent),
        )

        in_stories_in_scope = False
        for line in text.splitlines():
            m = _H1.match(line)
            if m and not ctx.title:
                ctx.title = m.group(1).strip("`").strip()
                continue
            if _STATUS_LABEL.match(line):
                ctx.has_status = True
                in_stories_in_scope = False
                continue
            if _STORIES_IN_SCOPE_LABEL.match(line):
                ctx.has_stories_in_scope = True
                in_stories_in_scope = True
                continue
            if _CONTEXT_NOTES_LABEL.match(line):
                ctx.has_context_notes = True
                in_stories_in_scope = False
                continue
            if in_stories_in_scope:
                bullet = _ITALIC_BACKTICK_BULLET.match(line)
                if bullet:
                    ctx.stories_in_scope.append(bullet.group(1).strip())
                    continue
                if line.strip() and not line.startswith(" "):
                    in_stories_in_scope = False

        return ctx

    @staticmethod
    def _is_leaf_folder(folder: Path) -> bool:
        try:
            return not any(child.is_dir() for child in folder.iterdir())
        except OSError:
            return False
