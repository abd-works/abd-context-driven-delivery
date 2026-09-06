"""CodeStoryMap — abstract base that renders a canonical StoryMap as a source-code tree.

Layout produced (identical shape across TS/Python/Java backends):

    <tests-root>/
      <epic-slug>/
        <sub-epic-slug>/
          <sub-epic-slug>.<ext>              # leaf file for this SubEpic
          <nested-sub-epic-slug>/
            <nested-sub-epic-slug>.<ext>     # nested leaf file when the SubEpic is not a leaf

A leaf SubEpic is one with no nested SubEpics of its own. Only leaf SubEpics get
`<sub-epic-slug>.<ext>` leaf files; if a previously-leaf SubEpic gains a nested
SubEpic, its own leaf file disappears.

Backends override `_render_leaf_file(sub_epic, epic)` and `_render_epic_helper(epic)`
to produce their language-specific text.

Hand-written regions inside a leaf file are marked with:

    <lang-comment> HAND-WRITTEN START <label>
    ... user code ...
    <lang-comment> HAND-WRITTEN END <label>

On re-render, the base looks up existing content, extracts hand-written blocks,
and inlines them into the newly generated file.

**Uniform Callable Surface.** This base implements the surface declared in the
Multi-Format Story Rendering mechanism (see src/architecture-context.md):

    parse(external: Dict[str, str]) -> StoryMap
    render(canonical: StoryMap, previous: Optional[Dict[str, str]] = None) -> Dict[str, str]
    sync(external: Dict[str, str], canonical: StoryMap) -> UpdateReport

Concrete backends (TypeScriptStoryMap, PythonStoryMap, JavaStoryMap) only
override the language-specific hooks below. Nothing about the public seam
varies between them.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Union

from src.core.stories.nodes import Epic, Story, SubEpic
from src.core.stories.story_map import StoryMap
from src.core.stories.update_report import UpdateReport


class CodeStoryMapError(Exception):
    """Raised when a folder tree is not a valid code story map."""


def to_kebab(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", name.strip().lower()).strip("-") or "unnamed"


def to_snake(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "_", name.strip().lower()).strip("_") or "unnamed"


def to_upper_snake(name: str) -> str:
    return to_snake(name).upper()


def to_pascal(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name.strip()) if w]
    return "".join(w[:1].upper() + w[1:].lower() for w in parts) or "Unnamed"


def to_camel(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name.strip()) if w]
    if not parts:
        return "unnamed"
    first = parts[0].lower()
    rest = "".join(w[:1].upper() + w[1:].lower() for w in parts[1:])
    return first + rest


class CodeStoryMap:
    """Abstract base for source-tree backends of a Story Map."""

    LEAF_EXTENSION: str = ""
    LANGUAGE_LINE_COMMENT: str = "//"

    def __init__(self, tests_root: str = "tests"):
        self._tests_root = tests_root.strip("/") or "tests"

    @property
    def tests_root(self) -> str:
        return self._tests_root

    def render(
        self,
        canonical: StoryMap,
        previous: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Return a `{file_path: content}` mapping for the whole canonical tree.

        If `previous` is provided, every hand-written region in a matching
        existing file is copied through byte-for-byte.
        """

        tree: Dict[str, str] = {}
        previous_tree = previous or {}
        for epic in canonical.epics:
            self._render_epic(
                epic=epic,
                epic_slug=self._folder_slug(epic, canonical.epics),
                tree=tree,
                previous_tree=previous_tree,
            )
        return tree

    def parse(self, external: Dict[str, str]) -> StoryMap:
        # WHY: reconstruct by walking every leaf file path — the shape encodes
        # the Epic/SubEpic hierarchy uniquely.
        if not isinstance(external, dict):
            raise CodeStoryMapError("Tree must be a mapping of paths to file content")

        story_map = StoryMap()
        epics_by_slug: Dict[str, Epic] = {}

        for path in sorted(external):
            parts = path.split("/")
            if not parts or parts[0] != self._tests_root:
                continue
            if len(parts) < 3:
                continue
            _, epic_slug, *rest = parts

            epic = epics_by_slug.get(epic_slug)
            if epic is None:
                epic = Epic(epic_slug, len(story_map.epics) + 1)
                epics_by_slug[epic_slug] = epic
                story_map.epics.append(epic)

            # WHY: depth-3 paths like `<tests>/<epic>/<epic_helper>.py` are
            # Epic-level helper files (Python, Java backends). They register
            # the Epic but contribute no SubEpics.
            if len(rest) < 2:
                continue
            *sub_epic_slugs, _file_name = rest

            current_sub_epics = epic.sub_epics
            current_sub_epic: Optional[SubEpic] = None
            for slug in sub_epic_slugs:
                existing = next(
                    (s for s in current_sub_epics if to_kebab(s.name) == slug),
                    None,
                )
                if existing is None:
                    existing = SubEpic(slug, len(current_sub_epics) + 1)
                    current_sub_epics.append(existing)
                current_sub_epics = existing.sub_epics
                current_sub_epic = existing

            if current_sub_epic is not None:
                self._hydrate_leaf_sub_epic_from_content(
                    current_sub_epic=current_sub_epic,
                    file_name=_file_name,
                    content=external[path],
                )

        if not story_map.epics and external:
            raise CodeStoryMapError(
                "Tree contains no recognisable Epic folders under the tests root"
            )
        return story_map

    def _hydrate_leaf_sub_epic_from_content(
        self, current_sub_epic: SubEpic, file_name: str, content: str
    ) -> None:
        # WHY: language backends override this to reconstruct story and scenario
        # structure when parsing generated source trees back into StoryMap.
        return None

    def sync(
        self, external: Dict[str, str], canonical: StoryMap
    ) -> UpdateReport:
        parsed = self.parse(external)
        return canonical.translate_from(parsed)

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(
            p for p in tree if p.endswith(self.LEAF_EXTENSION) and self._is_leaf_path(p)
        )

    def folders_of(self, tree: Dict[str, str]) -> List[str]:
        folders: set = set()
        for path in tree:
            parts = path.split("/")
            for i in range(1, len(parts)):
                folders.add("/".join(parts[:i]))
        return sorted(folders)

    def _is_leaf_path(self, path: str) -> bool:
        parts = path.split("/")
        return len(parts) >= 4 and parts[-1].endswith(self.LEAF_EXTENSION)

    def _render_epic(
        self,
        epic: Epic,
        epic_slug: str,
        tree: Dict[str, str],
        previous_tree: Dict[str, str],
    ) -> None:
        epic_root = f"{self._tests_root}/{epic_slug}"
        helper_content = self._render_epic_helper(epic)
        if helper_content is not None:
            helper_path = self._epic_helper_path(epic_root, epic)
            tree[helper_path] = helper_content
        if not epic.sub_epics and helper_content is None:
            tree[self._epic_marker_path(epic_root)] = self._render_epic_marker(epic)
        for sub_epic in epic.sub_epics:
            self._render_sub_epic(
                sub_epic=sub_epic,
                sibling_sub_epics=epic.sub_epics,
                parent_path=epic_root,
                owning_epic=epic,
                tree=tree,
                previous_tree=previous_tree,
            )

    def _render_sub_epic(
        self,
        sub_epic: SubEpic,
        sibling_sub_epics: List[SubEpic],
        parent_path: str,
        owning_epic: Epic,
        tree: Dict[str, str],
        previous_tree: Dict[str, str],
    ) -> None:
        folder = f"{parent_path}/{self._folder_slug(sub_epic, sibling_sub_epics)}"
        for nested in sub_epic.sub_epics:
            self._render_sub_epic(
                sub_epic=nested,
                sibling_sub_epics=sub_epic.sub_epics,
                parent_path=folder,
                owning_epic=owning_epic,
                tree=tree,
                previous_tree=previous_tree,
            )
        if sub_epic.stories or not sub_epic.sub_epics:
            leaf_path = f"{folder}/{to_kebab(sub_epic.name)}{self.LEAF_EXTENSION}"
            generated = self._render_leaf_file(sub_epic, owning_epic)
            previous = previous_tree.get(leaf_path)
            if previous is not None:
                generated = self._preserve_hand_written(previous, generated)
            tree[leaf_path] = generated

    def _epic_helper_path(self, epic_root: str, epic: Epic) -> str:
        return ""  # WHY: only backends that need a helper (Python, Java) override.

    def _render_epic_helper(self, epic: Epic) -> Optional[str]:
        # WHY: TypeScript backend needs no per-Epic helper file; Python/Java do.
        return None

    def _epic_marker_path(self, epic_root: str) -> str:
        return f"{epic_root}/.epic"

    def _render_epic_marker(self, epic: Epic) -> str:
        return f"epic:{epic.name}\n"

    def _folder_slug(
        self,
        node: Union[Epic, SubEpic],
        siblings: List[Union[Epic, SubEpic]],
    ) -> str:
        base = to_kebab(node.name)
        duplicate_count = sum(
            1 for sibling in siblings if to_kebab(sibling.name) == base
        )
        if duplicate_count <= 1:
            return base
        return f"{base}--{node.sequential_order}"

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        raise NotImplementedError

    def _preserve_hand_written(self, previous: str, generated: str) -> str:
        # WHY: every HAND-WRITTEN region in `previous` survives regeneration
        # byte-for-byte. Blocks whose label matches a placeholder in `generated`
        # are inlined at that placeholder; every other hand-written block is
        # appended to the end of the generated file in original order.
        line_comment = self.LANGUAGE_LINE_COMMENT
        marker_start = f"{line_comment} HAND-WRITTEN START"
        marker_end = f"{line_comment} HAND-WRITTEN END"
        pattern = re.compile(
            re.escape(marker_start) + r"\s*(\S*)\s*\n(.*?)\n" + re.escape(marker_end),
            re.DOTALL,
        )

        found_blocks = []
        for match in pattern.finditer(previous):
            found_blocks.append((match.group(1), match.group(2)))
        if not found_blocks:
            return generated

        labels_in_generated = {m.group(1) for m in pattern.finditer(generated)}

        def substitute(match: re.Match) -> str:
            label = match.group(1)
            for stored_label, stored_body in found_blocks:
                if stored_label == label:
                    return f"{marker_start} {label}\n{stored_body}\n{marker_end}"
            return match.group(0)

        result = pattern.sub(substitute, generated)

        appended = [
            f"{marker_start} {label}\n{body}\n{marker_end}"
            for label, body in found_blocks
            if label not in labels_in_generated
        ]
        if appended:
            if not result.endswith("\n"):
                result += "\n"
            result += "\n" + "\n".join(appended) + "\n"
        return result
