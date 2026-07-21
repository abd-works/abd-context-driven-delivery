"""Markdown tree adapter for the stories CLI.

Given a `StoryMap`, produce a `{path: contents}` mapping the CLI can dump to
disk. Today only `story-map.md` is emitted, because that is the only
Markdown artifact stories/src has a first-class renderer for
(`MarkdownStoryMap` in `markdown_story_map.py`).

When adapters for `thin-slice.md`, `scenarios/*.md`, and `story-context.md`
land, this function is the single place to grow — the CLI does not need to
change.

Signature parity with the code backends
---------------------------------------

- `story_map` — canonical StoryMap (matches `render_ts_tree` etc.).
- `tests_root` — sub-folder prefix. Defaults to `""` because Markdown
  artifacts sit at the workspace root by convention (`story-map.md`,
  `thin-slice.md`) — no `tests/` intermediary.
- `include_shared` — accepted for parity and ignored. Markdown has no
  shared/template files.
"""

from __future__ import annotations

from typing import Dict

from stories.document.markdown.nodes import MarkdownStoryMap
from stories.story_model.story_map import StoryMap


def render_md_tree(
    story_map: StoryMap,
    *,
    tests_root: str = "",
    include_shared: bool = True,
) -> Dict[str, str]:
    """Render Markdown artifacts for `story_map`.

    Returns an empty dict when the story map has no epics — no point writing
    an empty `story-map.md`. Callers can rely on `if not tree:` to detect
    that case rather than probing artifact-by-artifact.
    """
    _ = include_shared  # accepted for CLI parity; markdown has no shared files
    if not story_map or not story_map.epics:
        return {}

    md = MarkdownStoryMap()
    prefix = tests_root.strip("/")
    story_map_path = f"{prefix}/story-map.md" if prefix else "story-map.md"
    return {story_map_path: md.render(story_map)}
