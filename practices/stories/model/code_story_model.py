"""CodeStoryMap - a StoryMap stored as a source-code tree.

Layout produced (identical shape across TS/Python/Java backends):

    <tests-root>/
      <epic-slug>/
        <sub-epic-slug>/
          <sub-epic-slug>.<ext>              # leaf file for this Epic
          <nested-sub-epic-slug>/
            <nested-sub-epic-slug>.<ext>     # nested leaf file when the Epic is not a leaf

A leaf Epic is one with no nested Epics of its own. Only leaf Epics get
`<sub-epic-slug>.<ext>` leaf files; if a previously-leaf Epic gains a nested
Epic, its own leaf file disappears.

Backends override `_render_leaf_file(sub_epic, epic)` and `_render_epic_helper(epic)`
to produce their language-specific text.

Hand-written regions inside a leaf file are marked with:

    <lang-comment> HAND-WRITTEN START <label>
    ... user code ...
    <lang-comment> HAND-WRITTEN END <label>

On re-render, the base looks up existing content, extracts hand-written blocks,
and inlines them into the newly generated file.

load fills this map from the files. save writes this map's epics and stories.
render and parse call those so existing callers keep working.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Union

from practices.stories.model.story_model import (
    Background,
    Epic,
    Increment,
    Scenario,
    Step,
    StepType,
    Story,
    StoryMap,
)


class CodeStoryMapError(Exception):
    """Raised when a folder tree is not a valid code story map."""


class CodeStoryNode:
    """Name forms shared by every code node. slug is the kebab folder name."""

    def slug(self) -> str:
        return re.sub(r"[^0-9a-z]+", "-", self.name.strip().lower()).strip("-") or "unnamed"

    def snake(self) -> str:
        return re.sub(r"[^0-9a-z]+", "_", self.name.strip().lower()).strip("_") or "unnamed"

    def pascal(self) -> str:
        parts = [word for word in re.split(r"[^0-9A-Za-z]+", self.name.strip()) if word]
        return "".join(word[:1].upper() + word[1:].lower() for word in parts) or "Unnamed"

    def camel(self) -> str:
        parts = [word for word in re.split(r"[^0-9A-Za-z]+", self.name.strip()) if word]
        if not parts:
            return "unnamed"
        first = parts[0].lower()
        rest = "".join(word[:1].upper() + word[1:].lower() for word in parts[1:])
        return first + rest

    @classmethod
    def name_from_slug(cls, slug: str) -> str:
        return slug.replace("-", " ").title()


class CodeScenario(Scenario, CodeStoryNode):
    """One scenario. Steps, ands, and examples are the story-model shape on every language."""

    _STEP_TYPES = {
        "given": StepType.GIVEN,
        "when": StepType.WHEN,
        "then": StepType.THEN,
    }

    def read(self, body: str, example_names: List[str] | None = None) -> None:
        self.steps = self.steps_from(self.calls_in(body))
        for name in example_names or []:
            if re.search(rf"\b{re.escape(name)}\b", body):
                self.examples[name] = name

    def calls_in(self, body: str) -> List[tuple]:
        raise NotImplementedError

    @classmethod
    def scenario_blocks(cls, content: str) -> List[tuple]:
        raise NotImplementedError

    @classmethod
    def backgrounds_in(cls, content: str) -> List[Background]:
        raise NotImplementedError

    @classmethod
    def example_names(cls, content: str) -> List[str]:
        raise NotImplementedError

    @classmethod
    def create(cls, scenario) -> List[str]:
        raise NotImplementedError

    @classmethod
    def steps_from(cls, calls: List[tuple]) -> List[Step]:
        steps: List[Step] = []
        previous: Optional[Step] = None
        for keyword, text in calls:
            word = keyword.lower()
            if word in ("and", "but") and previous is not None:
                previous.ands = [
                    *previous.ands,
                    Step(text, previous.step_type, len(previous.ands) + 1, keyword=word),
                ]
                continue
            step_type = cls._STEP_TYPES.get(word)
            if step_type is None:
                continue
            step = Step(text, step_type, len(steps) + 1, keyword=word)
            steps.append(step)
            previous = step
        return steps

    @classmethod
    def balanced(cls, text: str, open_at: int) -> str:
        depth = 0
        for index in range(open_at, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    return text[open_at + 1:index]
        return text[open_at + 1:]

    @classmethod
    def outside_scenarios(cls, body: str) -> str:
        pieces: List[str] = []
        index = 0
        while True:
            found = body.find("scenario(", index)
            if found < 0:
                pieces.append(body[index:])
                break
            pieces.append(body[index:found])
            arrow = body.find("=>", found)
            brace = body.find("{", arrow if arrow >= 0 else found)
            if brace < 0:
                break
            inner = cls.balanced(body, brace)
            index = brace + len(inner) + 2
        return "".join(pieces)


class CodeStory(Story, CodeStoryNode):
    scenario_type = CodeScenario

    @classmethod
    def load_all(cls, content: str) -> List["CodeStory"]:
        """Every story in one sub-epic file. A language splits the file."""
        return [cls.load(content, "")]

    def write(self, parent: str, files: Dict[str, str], tests_root: str) -> None:
        """A language story writes its file. The base story has no file."""
        return

    def add_scenario(self, name: str, body: str, example_names: List[str]) -> None:
        scenario = self.scenario_type(name=name, sequential_order=len(self.scenarios) + 1, story_name=self.name)
        scenario.read(body, example_names)
        self.scenarios.append(scenario)

    def fill(self, content: str) -> None:
        scenario_type = type(self).scenario_type
        self.backgrounds = scenario_type.backgrounds_in(content)
        examples = scenario_type.example_names(content)
        for name, body in scenario_type.scenario_blocks(content):
            self.add_scenario(name, body, examples)

    @classmethod
    def load(cls, content: str, story_slug: str) -> "CodeStory":
        """Read a language file into this story. Each language overrides it."""
        raise NotImplementedError

    @classmethod
    def create(cls, story: Story, **kwargs) -> str:
        """Write this story in the language file. Each language overrides it."""
        raise NotImplementedError

    @classmethod
    def from_source(cls, content: str, story_slug: str) -> "CodeStory":
        return cls.load(content, story_slug)


class CodeIncrement(Increment, CodeStoryNode):
    pass


class CodeEpic(Epic, CodeStoryNode):
    def write(self, parent: str, files: Dict[str, str], tests_root: str) -> None:
        """A sub-epic that has stories is one file in the parent folder.

        An epic that has child epics is a folder. Those children write into it.
        The lowest sub-epic does not get a folder of its own.
        """
        if self.epics:
            folder = f"{parent}/{self.slug()}"
            self._write_folder(folder, files, tests_root)
            for child in self.epics:
                child.write(folder, files, tests_root)
            if self.stories:
                self._write_stories(folder, files, tests_root)
            return
        self._write_stories(parent, files, tests_root)

    def _file_stories(self) -> List[Story]:
        return list(self.stories)

    def _write_stories(self, parent: str, files: Dict[str, str], tests_root: str) -> None:
        """One file named for this sub-epic. Each language writes its own text."""
        return

    def _write_folder(self, folder: str, files: Dict[str, str], tests_root: str) -> None:
        return

    @staticmethod
    def epic_name_in(content: str) -> str:
        match = re.search(r"Epic:\s*(.+)", content)
        return match.group(1).strip() if match else ""


class CodeStoryMap(StoryMap):
    """Source-tree story map. The epics and stories are the story map. load and save are the files."""

    LEAF_EXTENSION: str = ""
    LANGUAGE_LINE_COMMENT: str = "//"
    epic_type = CodeEpic
    story_type = CodeStory
    increment_type = CodeIncrement

    def __init__(self, source: "StoryMap | str | None" = None, tests_root: str | None = None):
        if isinstance(source, str):
            tests_root = source
            source = None
        super().__init__(source)
        self._tests_root = ("tests" if tests_root is None else tests_root).strip("/")

    def strip_tests_root_prefix(self, parts: list[str]) -> list[str] | None:
        """Drop the workspace-relative deploy prefix from a rendered file path."""
        if not self._tests_root:
            return parts
        root_parts = [p for p in self._tests_root.split("/") if p]
        if not root_parts:
            return parts
        if len(parts) < len(root_parts) or parts[: len(root_parts)] != root_parts:
            return None
        return parts[len(root_parts) :]

    @property
    def tests_root(self) -> str:
        return self._tests_root

    def save(self, previous: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Write this story map's epics and stories to source files."""
        tree: Dict[str, str] = {}
        previous_tree = previous or {}
        for epic in self.epics:
            self._render_epic(
                epic=epic,
                epic_slug=self._folder_slug(epic, self.epics),
                tree=tree,
                previous_tree=previous_tree,
            )
        return tree

    def render(
        self,
        canonical: StoryMap,
        previous: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        return type(self)(canonical, tests_root=self._tests_root).save(previous)

    def load(self, external: Dict[str, str]) -> "CodeStoryMap":
        """Read source files into this story map's epics and stories."""
        if not isinstance(external, dict):
            raise CodeStoryMapError("Tree must be a mapping of paths to file content")
        self.epics.clear()
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
                epic = self.epic_for(epic_slug)
                epics_by_slug[epic_slug] = epic
            if len(rest) < 2:
                continue
            *sub_epic_slugs, _file_name = rest
            current_sub_epic = self.sub_epic_for(epic, sub_epic_slugs)
            if current_sub_epic is not None:
                self._leaf_file_name = _file_name
                self._leaf_content = external[path]
                self._hydrate_leaf_sub_epic_from_content(current_sub_epic)
        if not self.epics and external:
            raise CodeStoryMapError(
                "Tree contains no recognisable Epic folders under the tests root"
            )
        return self

    def parse(self, external: Dict[str, str]) -> "CodeStoryMap":
        return type(self)(self._tests_root).load(external)

    def epic_for(self, slug: str) -> Epic:
        for epic in self.epics:
            if epic.slug() == slug:
                return epic
        epic = self.epic_type(self.epic_type.name_from_slug(slug), len(self.epics) + 1)
        self.append_epic(epic)
        return epic

    def take_sub_epic_file(self, parts: List[str], content: str) -> bool:
        """A file named for the lowest sub-epic. Its folder is a parent epic.

        A file whose folder slug matches the file slug is a story folder from
        the older layout. That file stays with the language's story-folder load.
        """
        if len(parts) < 2:
            return False
        filename = parts[-1]
        stem_slug = self._file_stem_slug(filename)
        if not stem_slug or parts[-2] == stem_slug:
            return False
        epic_name = CodeEpic.epic_name_in(content)
        leaf_slug = CodeEpic(epic_name).slug() if epic_name else stem_slug
        if not leaf_slug:
            return False
        epic = self.epic_for(parts[0])
        sub = self.sub_epic_for(epic, [*parts[1:-1], leaf_slug])
        if epic_name:
            sub.name = epic_name
        for story in self.story_type.load_all(content):
            sub.append_story(story)
        return True

    def _file_stem_slug(self, filename: str) -> str:
        for suffix in ("_story.test.ts", "_story.test.py", "_story.test.js", "Story.java"):
            if filename.endswith(suffix):
                stem = filename[: -len(suffix)]
                if suffix == "Story.java":
                    return re.sub(r"(?<!^)(?=[A-Z])", "-", stem).lower()
                return stem.replace("_", "-")
        return ""

    def sub_epic_for(self, epic: Epic, slugs: List[str]) -> Epic:
        parent = epic
        current: Optional[Epic] = None
        for slug in slugs:
            found = next((item for item in parent.epics if item.slug() == slug), None)
            if found is None:
                found = self.epic_type(self.epic_type.name_from_slug(slug), len(parent.epics) + 1)
                parent.append_epic(found)
            current = found
            parent = found
        if current is None:
            raise CodeStoryMapError("A story file needs a sub-epic folder")
        return current

    def _hydrate_leaf_sub_epic_from_content(self, current_sub_epic: Epic) -> None:
        # WHY: language backends override this to reconstruct story and scenario
        # structure when parsing generated source trees back into StoryMap.
        return None

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
        if not epic.epics and helper_content is None:
            tree[self._epic_marker_path(epic_root)] = self._render_epic_marker(epic)
        for sub_epic in epic.epics:
            self._render_sub_epic(
                sub_epic=sub_epic,
                sibling_epics=epic.epics,
                parent_path=epic_root,
                owning_epic=epic,
                tree=tree,
                previous_tree=previous_tree,
            )

    def _render_sub_epic(
        self,
        sub_epic: Epic,
        sibling_epics: List[Epic],
        parent_path: str,
        owning_epic: Epic,
        tree: Dict[str, str],
        previous_tree: Dict[str, str],
    ) -> None:
        folder = f"{parent_path}/{self._folder_slug(sub_epic, sibling_epics)}"
        for nested in sub_epic.epics:
            self._render_sub_epic(
                sub_epic=nested,
                sibling_epics=sub_epic.epics,
                parent_path=folder,
                owning_epic=owning_epic,
                tree=tree,
                previous_tree=previous_tree,
            )
        if sub_epic.stories or not sub_epic.epics:
            leaf_path = f"{folder}/{sub_epic.slug()}{self.LEAF_EXTENSION}"
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
        node: Union[Epic, Epic],
        siblings: List[Union[Epic, Epic]],
    ) -> str:
        base = node.slug()
        duplicate_count = sum(
            1 for sibling in siblings if sibling.slug() == base
        )
        if duplicate_count <= 1:
            return base
        return f"{base}--{node.sequential_order}"

    def _render_leaf_file(self, sub_epic: Epic, owning_epic: Epic) -> str:
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
