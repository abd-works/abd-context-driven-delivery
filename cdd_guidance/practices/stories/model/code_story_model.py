"""CodeStoryModel - a StoryModel stored as a source-code tree.

Layout written, the same shape in every language:

    <tests-root>/
      <epic-slug>/
        <epic story file>                    # the epic's own stories, when it has any
        <sub-epic story file>                # one file per sub-epic that has no sub-epics of its own
        <sub-epic-slug>/
          <nested sub-epic story file>       # a sub-epic with sub-epics of its own is a folder

Each language names its story files (`file_name`) and spells the code inside them.

Every story, background, scenario, and step read from a file keeps the code it was written with
(`written`, `setup`, and each step's `body`). Rendered back in the same language and unchanged, a node
is written exactly as read; otherwise it is spelled again with its bodies kept.

load fills this map from the story files a language names (`is_story_file`), one way for every language; each
story reads its own text and then its own block of the file (`read_code`). save writes this map's epics and stories.
render writes another map in this language and parse reads a tree into a new map, through save and load.
"""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, Union

from harness.annotations.name import Name
from cdd_guidance.practices.clean_engineering.model.bracket_structure import BracketStructure
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage
from cdd_guidance.practices.stories.model.story_model import (
    Background,
    Epic,
    Increment,
    Scenario,
    Step,
    StepType,
    Story,
    StoryModel,
    StoryType,
)
from cdd_guidance.practices.stories.model.story_map_files import source_at
from cdd_guidance.practices.stories.model.story_file import CodeBlock, flat_steps, read_step_code
from cdd_guidance.practices.stories.model.story_writing import StoryWriting, as_read

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_file import StoryFile


class CodeStoryModelError(Exception):
    """Raised when a folder tree is not a valid code story map."""


def _quoted_name_line(content: str, name: str) -> int:
    """The line that quotes name, counted from 1; the first line when none does."""
    for index, line in enumerate(content.splitlines(), start=1):
        if f"'{name}'" in line or f'"{name}"' in line:
            return index
    return 1


def _file_stem_slug(filename: str, suffixes: Tuple[str, ...]) -> str:
    """The kebab slug of a story file's name without the story-file suffix it ends with; empty for any other file."""
    suffix = next((item for item in suffixes if filename.endswith(item)), None)
    return Name(filename[: -len(suffix)]).kebab if suffix else ""


def _epic_slugs(folders: List[str], stem_slug: str, leaf_slug: str) -> List[str]:
    """The epic, then each sub-epic, a story file sits in, from the folders above it under the tests root. A last
    folder with the file's or its epic's slug is that sub-epic, not a second level; a file in its own top folder is the
    epic itself."""
    folders = folders[:-1] if folders and folders[-1] in (stem_slug, leaf_slug) else list(folders)
    if not folders:
        return [leaf_slug]
    nested = folders[1:]
    return [folders[0], *(nested if nested and nested[-1] == leaf_slug else [*nested, leaf_slug])]


def _names_listed(lines: List[str]) -> List[str]:
    """Each name the comma-separated lines list, once, in order: an import's alias when it gives one."""
    names: List[str] = []
    for part in (part for line in lines for part in line.split(",")):
        name = part.strip().split(" as ")[-1].strip()
        if name and name != "(" and name not in names:
            names.append(name)
    return names


def unescaped(value: str) -> str:
    """A quoted name or step text as it reads once its escapes are taken out: the one unescape every language uses."""
    return value.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


class CodeStoryNode:
    """Name forms shared by every code node; the kebab folder name is the story node's own slug."""

    def snake(self) -> str:
        return Name(self.name).title_snake or "unnamed"

    def pascal(self) -> str:
        return Name(self.name).title_pascal or "Unnamed"

    def camel(self) -> str:
        return Name(self.name).title_camel or "unnamed"

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
        body = self._take_background_comments(body)
        self.steps = self.steps_from(self.calls_in(body))
        for name in example_names or []:
            if re.search(rf"\b{re.escape(name)}\b", body):
                self.examples[name] = name

    def _take_background_comments(self, body: str) -> str:
        kept: List[str] = []
        calls: List[tuple] = []
        name = "background"
        seen = False
        for line in body.splitlines(keepends=True):
            heading = re.match(r"\s*(?:#|//|\*)\s*background:\s*(.+)", line)
            step = re.match(r"\s*(?:#|//|\*)\s*background-step:\s*(\w+)\s*\|\s*(.*)", line)
            if heading:
                name = heading.group(1).strip()
                seen = True
                continue
            if step:
                calls.append((step.group(1), step.group(2).strip()))
                continue
            kept.append(line)
        if seen or calls:
            background = Background(name, 1)
            background.steps = self.steps_from(calls)
            self.backgrounds = [background]
        return "".join(kept)

    @classmethod
    def calls_in(cls, body: str) -> List[tuple]:
        """The (keyword, text) of each step call in a body of this language."""
        raise NotImplementedError

    # How a language opens a scenario, with the scenario's name in the group `name`.
    _SCENARIO: re.Pattern = re.compile(r"(?!)")
    # How a language imports example names from an examples module, with the names in the group `names`; none for a
    # language whose story files import no examples.
    _IMPORT: Optional[re.Pattern] = None
    # The comment line that lists the examples a story file uses.
    _EXAMPLES_LINE = re.compile(r"examples:\s*(.+)")

    def read_code(self, block: CodeBlock, lead: List[str]) -> None:
        """This scenario's code from the block it was written as: each background's and step's body, the code that is
        no step (`setup`), and the block's own lines (`written`)."""
        backgrounds = block.backgrounds([])
        for background, item in zip(self.backgrounds, backgrounds):
            read_step_code(background, item.steps([]))
        steps = block.steps(backgrounds)
        read_step_code(self, steps)
        self.setup = block.setup([*backgrounds, *steps])
        written = block.written(lead)
        written.inside = block.inside_lines
        written.key = self.code_key
        self.written = written

    @classmethod
    def scenario_blocks(cls, content: str) -> List[tuple]:
        """(name, body) of each scenario in a file; a scenario runs to the next one."""
        matches = list(cls._SCENARIO.finditer(content))
        blocks = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
            blocks.append((match.group("name").strip(), content[match.end() : end]))
        return blocks

    @classmethod
    def backgrounds_in(cls, content: str) -> List[Background]:
        raise NotImplementedError

    @classmethod
    def example_names(cls, content: str) -> List[str]:
        """The example names a story file imports and the ones its examples comment lists, each once, in order."""
        listed = [match.group("names") for match in cls._IMPORT.finditer(content)] if cls._IMPORT is not None else []
        listed += [match.group(1) for match in cls._EXAMPLES_LINE.finditer(content)]
        return _names_listed(listed)

    @classmethod
    def steps_from(cls, calls: List[tuple]) -> List[Step]:
        steps: List[Step] = []
        previous: Optional[Step] = None
        for keyword, text in calls:
            word = keyword.lower()
            if word == "and" and previous is not None:
                previous.ands = [
                    *previous.ands,
                    Step(text, previous.step_type, len(previous.ands) + 1, keyword=word),
                ]
                continue
            if word == "but" and previous is not None:
                previous.ands = [
                    *previous.ands,
                    Step(text, previous.step_type, len(previous.ands) + 1, keyword=word),
                ]
                continue
            step_type = StepType.THEN if word == "but" else cls._STEP_TYPES.get(word)
            if step_type is None:
                continue
            step = Step(text, step_type, len(steps) + 1, keyword=word)
            steps.append(step)
            previous = step
        return steps

    @classmethod
    def balanced(cls, text: str, open_at: int) -> str:
        close = BracketStructure(text).closing_bracket(open_at)
        return text[open_at + 1 : close] if close is not None else text[open_at + 1 :]

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

    # A story test names its tier after the story; the tier is not part of the story's name.
    _TIER_NEUTRAL = re.compile(r"\s*\(tier-neutral\)\.?\s*$")
    # What opens a line of the comment that describes a story in this language.
    description_mark = r"\*\s*"
    # Where a file's next story starts, and what a piece of the file holds when it is a story.
    _STORY_START: re.Pattern = re.compile(r"(?!)")
    _STORY_MARK: re.Pattern = re.compile(r"Story:")
    # The story's name as a story file writes it, in the group `name`.
    _NAME: re.Pattern = re.compile(r"Story:\s*(?P<name>.+)")

    def read_description(self, content: str) -> None:
        """The actor, kind, domain terms, and evidence the story's comment names; a story whose comment names no kind
        is a user story."""
        actor = re.search(rf"{self.description_mark}Actor:\s*(.+)", content, re.MULTILINE)
        if actor:
            self.actors = [actor.group(1).strip()]
        kind = re.search(rf"{self.description_mark}Kind:\s*(user|system|technical)\b", content, re.MULTILINE)
        if kind:
            self.story_type = StoryType.from_mark(kind.group(1))
        terms = re.search(rf"{self.description_mark}Domain terms:\s*(.+)$", content, re.MULTILINE)
        if terms:
            self.domain_terms = [term.strip() for term in terms.group(1).split(",") if term.strip()]
        evidence = re.search(rf"{self.description_mark}Evidence:\s*([A-Za-z][A-Za-z ,-]*)", content, re.MULTILINE)
        if evidence:
            self.evidence = [part.strip() for part in evidence.group(1).split(",") if part.strip()]

    @classmethod
    def example_imports(cls, content: str) -> str:
        """The lines of a story file that import its examples, which every story in the file reads its example names
        from."""
        pattern = cls.scenario_type._IMPORT
        return "\n".join(match.group(0) for match in pattern.finditer(content)) if pattern is not None else ""

    @classmethod
    def name_read(cls, found: Optional[str]) -> str:
        """The story's name as its story test wrote it. Every language reads a name this one way, so a story test's
        scenarios find the story of the same name on the map."""
        return cls._TIER_NEUTRAL.sub("", found.strip() if found else "").strip()

    @classmethod
    def name_in(cls, content: str) -> Optional[str]:
        """The story's name as the text of one story writes it; None when it writes none."""
        match = cls._NAME.search(content)
        return match.group("name") if match else None

    @classmethod
    def load_all(cls, content: str) -> List["CodeStory"]:
        """Every story in one sub-epic file: the file split where each story starts, each piece that holds a story
        read as one; the whole file as one story when no piece does."""
        stories = [cls.load(piece) for piece in cls._STORY_START.split(content) if cls._STORY_MARK.search(piece)]
        return stories or [cls.load(content)]

    @classmethod
    def load(cls, content: str, scenario_blocks: Optional[List[CodeBlock]] = None) -> "CodeStory":
        """The story the text of one story holds: its name, its description, then its backgrounds and scenarios, one
        for each of scenario_blocks when its story file found them, else as the text writes them."""
        story = cls(cls.name_read(cls.name_in(content)), 1)
        story.read_description(content)
        story.fill(content, scenario_blocks)
        return story

    @classmethod
    def from_block(cls, block: CodeBlock, lead: List[str], text: str) -> "CodeStory":
        """The story one block of a story file holds, read from its text (the file's example imports, the comment above
        the block, and the block) with one scenario for each scenario block in it, and its code read from the block."""
        scenarios = block.scenarios()
        story = cls.load(text, scenarios)
        story.read_code(block, lead, scenarios)
        return story

    def read_code(self, block: CodeBlock, lead: List[str], scenarios: List[CodeBlock]) -> None:
        """This story's code from the block it was written as: each background's step bodies, the code that is no
        background or scenario (`setup`), the block's own lines (`written`), and each scenario's code from its block."""
        backgrounds = block.backgrounds(scenarios)
        for background, item in zip(self.backgrounds, backgrounds):
            read_step_code(background, item.steps(scenarios))
        written = block.written(lead)
        written.inside, leads, written.closing = block.split_inside(scenarios)
        self.setup = block.setup([*backgrounds, *scenarios])
        for scenario, item, scenario_lead in zip(self.scenarios, scenarios, leads):
            scenario.read_code(item, scenario_lead)
        written.key = self.code_key
        self.written = written

    def add_scenario(self, name: str, body: str, example_names: List[str]) -> None:
        scenario = self.scenario_type(name=name, sequential_order=len(self.scenarios) + 1)
        scenario.read(body, example_names)
        self.scenarios.append(scenario)

    def _take_background_examples(self, content: str) -> None:
        import json

        match = re.search(r"background-examples:\s*(\{.*\})", content)
        if match is None or not self.backgrounds:
            return
        payload = json.loads(match.group(1))
        if not isinstance(payload, dict):
            return
        for name, cells in payload.items():
            self.backgrounds[0].examples[name] = cells if isinstance(cells, dict) else name

    def _scenario_texts(self, content: str, scenario_blocks: Optional[List[CodeBlock]]) -> List[tuple]:
        """(name, body) of each scenario: of each scenario block its story file found, else as the text writes them."""
        if scenario_blocks is None:
            return type(self).scenario_type.scenario_blocks(content)
        return [(item.name, item.body_text) for item in scenario_blocks]

    def fill(self, content: str, scenario_blocks: Optional[List[CodeBlock]] = None) -> None:
        scenario_type = type(self).scenario_type
        examples = scenario_type.example_names(content)
        backgrounds = scenario_type.backgrounds_in(content)
        for background in backgrounds:
            for name in examples:
                if re.search(rf"\b{re.escape(name)}\b", getattr(background, "body", "")):
                    background.examples[name] = name
        self.backgrounds = backgrounds
        self._take_background_examples(content)
        for name, body in self._scenario_texts(content, scenario_blocks):
            self.add_scenario(name, body, examples)
        if self.backgrounds and self.backgrounds[0].examples:
            for scenario in self.scenarios:
                for background in scenario.backgrounds:
                    if background.examples:
                        continue
                    background.examples = self.backgrounds[0].examples.clone(background)


class CodeIncrement(Increment, CodeStoryNode):
    pass


class CodeEpic(Epic, CodeStoryNode):
    @staticmethod
    def epic_name_in(content: str) -> str:
        match = re.search(r"Epic:\s*(.+)", content)
        return match.group(1).strip() if match else ""

    def order_path(self) -> str:
        orders = []
        node = self
        while node is not None and hasattr(node, "sequential_order"):
            parent = getattr(node, "parent", None)
            siblings = getattr(parent, "epics", None) if parent is not None else None
            if siblings is not None and node in siblings:
                orders.append(str(siblings.index(node)))
            else:
                orders.append(str(getattr(node, "sequential_order", 0) or 0))
            if parent is None or parent is node:
                break
            node = parent
        return ".".join(reversed(orders))


class CodeStoryModel(StoryModel):
    """Source-tree story map. The epics and stories are the story map: this model keeps the layout of the story files
    under the tests root (load, save), and the code a render adopts from the tree already on disk. How its language
    writes each story file is the writing it holds (`writing`), beside the reader of its story files (`story_file`)."""

    epic_type = CodeEpic
    story_type = CodeStory
    increment_type = CodeIncrement
    writing_type: type = StoryWriting
    """How this language writes its story files; the model makes one, with its language, the first time it writes."""
    story_file_suffixes: Tuple[str, ...] = ()
    """How a story file in this language ends, such as ``_story.test.py``; the first is the one this language writes.
    Empty for a language with no story files."""
    not_story_paths: re.Pattern = re.compile(r"(?!)")
    """A path that ends like a story file but holds no story, such as a file in an examples folder; a pattern that
    matches nothing in a language whose every such file is one."""

    @classmethod
    def is_story_file(cls, path: "str | Path") -> bool:
        """True when the file at path is a story file in this language, which this model's story type reads."""
        posix = str(path).replace("\\", "/")
        return posix.endswith(cls.story_file_suffixes) and cls.not_story_paths.search(posix) is None

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        """The story files in tree, path to text, in path order."""
        return sorted(path for path in tree if self.is_story_file(path))

    def __init__(self, source: "StoryModel | str | None" = None, tests_root: str | None = None):
        if isinstance(source, str):
            tests_root = source
            source = None
        super().__init__(source)
        self._tests_root = ("tests" if tests_root is None else tests_root).strip("/")

    def _under_tests_root(self, parts: List[str]) -> Optional[List[str]]:
        """A file path's folders below the tests root; None for a path outside it."""
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

    def save(self) -> Dict[str, str]:
        """Write this story map's epics and stories to source files."""
        return self.write_epics({})

    def render(
        self,
        canonical: StoryModel,
        previous: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Write canonical to source files. previous is the tree already on disk: whatever canonical has
        no code for in this language takes that tree's code for the same epic, story, scenario, and step."""
        if isinstance(previous, str) and previous:
            raise CodeStoryModelError("previous must be the path-to-content map of the story tree already on disk")
        model = self.copy_of(canonical)
        if previous:
            model._adopt_code(self.parse(previous))
        return model.save()

    def copy_of(self, source: Optional[StoryModel]) -> "CodeStoryModel":
        """source in this language, with this model's settings; an empty map when source is None."""
        return type(self)(source, tests_root=self._tests_root)

    language: Optional[CodeLanguage] = None

    @cached_property
    def writing(self) -> StoryWriting:
        """How this model's language writes its story files, made once."""
        return self.writing_type(self.language)

    def write_epics(self, files: Dict[str, str]) -> Dict[str, str]:
        """Every epic's folders and sub-epic files, added to files. A top-level epic is always a folder, so the
        file holding its own stories sits inside it and reads back onto that epic."""
        for epic in self.epics:
            if epic.epics:
                self._write_epic(epic, self.tests_root, files)
            else:
                self._write_stories(epic, f"{self.tests_root}/{epic.slug}", files)
        return files

    def read_from_code(self) -> bool:
        """Some sub-epic or story in this tree was read from a file in this language."""
        nodes = [node for epic in self.every_epic() for node in (epic, *epic.stories)]
        return any(node.written is not None and node.written.language is self.language for node in nodes)

    def story_file(self, content: str) -> Optional["StoryFile"]:
        """The story file content is, as this language finds its blocks; None for a language that does not read its
        blocks, whose stories are written generically."""
        return None

    def folder_files(self, epic: Epic, folder: str, files: Dict[str, str]) -> None:
        """Files an epic folder holds besides its sub-epics; none unless a language adds them."""
        return

    def _write_epic(self, epic: Epic, parent: str, files: Dict[str, str]) -> None:
        """An epic with child epics is a folder its children write into; a sub-epic with stories is one file."""
        if not epic.epics:
            self._write_stories(epic, parent, files)
            return
        folder = f"{parent}/{epic.slug}"
        self.folder_files(epic, folder, files)
        for child in epic.epics:
            self._write_epic(child, folder, files)
        self._write_stories(epic, folder, files)

    def _write_stories(self, epic: Epic, parent: str, files: Dict[str, str]) -> None:
        """One file for a sub-epic's stories: back to the path it was read from, else named for the sub-epic."""
        if not epic.stories:
            return
        path, text = self.writing.story_file(epic, parent, as_read(epic.written, self.language, epic.name))
        files[path] = text

    def _adopt_code(self, kept: "CodeStoryModel") -> None:
        """Each epic, story, background, scenario, and step without code in this language takes kept's code
        for the node with the same name."""
        if self.language is None:
            return
        epics = {epic.name: epic for epic in kept.every_epic()}
        stories = {story.name: story for epic in epics.values() for story in epic.stories}
        for epic in self.every_epic():
            self._take_code(epic, epics.get(epic.name))
            for story in epic.stories:
                self._take_story_code(story, stories.get(story.name))

    def _take_story_code(self, story: Story, kept: Optional[Story]) -> None:
        """A story, its backgrounds, its scenarios, and theirs take kept's code for the nodes with the same name."""
        if kept is None:
            return
        self._take_code(story, kept)
        self._take_children_code(story.backgrounds, kept.backgrounds)
        self._take_children_code(story.scenarios, kept.scenarios)
        for scenario in story.scenarios:
            match = next((other for other in kept.scenarios if other.name == scenario.name), None)
            if match is not None:
                self._take_children_code(scenario.backgrounds, match.backgrounds)

    def _take_children_code(self, nodes: list, kept: list) -> None:
        by_name = {other.name: other for other in kept}
        for node in nodes:
            match = by_name.get(node.name)
            self._take_code(node, match)
            self._take_step_bodies(node, match)

    def _take_code(self, node: Union[Epic, Story, Background, Scenario], kept) -> None:
        language = self.language
        if kept is None:
            return
        if node.written is None or node.written.language is not language:
            node.written = kept.written
        if node.setup.language is not language:
            node.setup = kept.setup

    def _take_step_bodies(self, node: Union[Background, Scenario], kept) -> None:
        if kept is None:
            return
        language = self.language
        bodies = {step.text: step.body for step in flat_steps(kept.steps)}
        for step in flat_steps(node.steps):
            step.body = step.body.in_language_of(bodies.get(step.text, CodeBody()), language)

    def load(self, external: Dict[str, str], *, on_file: Optional[Callable[[str], None]] = None) -> "CodeStoryModel":
        """This story map's epics and stories from the story files in external, path to text, under the tests root:
        each file one sub-epic, in the order its header gives. on_file hears each file as it is read."""
        if not isinstance(external, dict):
            raise CodeStoryModelError(f"{type(self).__name__} reads a path-to-content dict of story files")
        self.epics.clear()
        self.source_texts = dict(external)
        paths = [path for path in self._ordered_paths(external) if self.is_story_file(path)]
        with self.batch_schema_sync():
            for index, path in enumerate(paths, start=1):
                if on_file is not None:
                    on_file(f"{index}/{len(paths)} · {path}")
                self._read_story_file(path, external[path])
        return self

    def parse(self, external: Dict[str, str], *, on_file: Optional[Callable[[str], None]] = None) -> "CodeStoryModel":
        """A new map read from the story files in external, with this model's settings."""
        return self.copy_of(None).load(external, on_file=on_file)

    def _ordered_paths(self, external: Dict[str, str]) -> List[str]:
        def key(path: str) -> tuple:
            match = re.search(r"Orders:\s*([0-9.]+)", external.get(path, ""))
            order = tuple(int(part) for part in match.group(1).split(".") if part) if match else (10**6,)
            return (order, path)

        return sorted(external, key=key)

    def epic_for(self, slug: str) -> Epic:
        for epic in self.epics:
            if epic.slug == slug:
                return epic
        epic = self.epic_type(self.epic_type.name_from_slug(slug), len(self.epics) + 1)
        self.append_epic(epic)
        return epic

    def _read_story_file(self, path: str, content: str) -> None:
        """One file is one sub-epic. Every story in the file belongs to it; a file outside the tests root, or at its
        top, holds none.

        A parent folder with the same slug as the file, or as the epic its header names, is that sub-epic, so the
        file is not a second level. A file in its own top folder is the epic itself, and its stories sit on the epic.
        """
        parts = self._under_tests_root(path.strip("/").replace("\\", "/").split("/"))
        stem_slug = _file_stem_slug(parts[-1], self.story_file_suffixes) if parts is not None and len(parts) >= 2 else ""
        if not stem_slug:
            return
        epic_name = CodeEpic.epic_name_in(content)
        slugs = _epic_slugs(parts[:-1], stem_slug, (Name(epic_name).title_slug or "unnamed") if epic_name else stem_slug)
        holder = self.epic_for(slugs[0]) if len(slugs) == 1 else self.sub_epic_for(self.epic_for(slugs[0]), slugs[1:])
        if epic_name:
            holder.name = epic_name
        self._take_stories(holder, content, path.replace("\\", "/"))

    def _take_stories(self, holder: Epic, content: str, source_file: str) -> None:
        """The file's stories onto the sub-epic that holds them, each with where it is and the code it was written with."""
        code = self.story_file(content)
        read = code.stories(self.story_type, source_file) if code is not None else None
        stories, written = read if read is not None else (self.story_type.load_all(content), None)
        for story in stories:
            if source_file and not story.has_source_file:
                line = _quoted_name_line(content, story.name)
                story.source = source_at(source_file, line)
            holder.append_story(story)
        if written is not None:
            written.key = holder.name
            holder.written = written

    def sub_epic_for(self, epic: Epic, slugs: List[str]) -> Epic:
        parent = epic
        current: Optional[Epic] = None
        for slug in slugs:
            found = next((item for item in parent.epics if item.slug == slug), None)
            if found is None:
                found = self.epic_type(self.epic_type.name_from_slug(slug), len(parent.epics) + 1)
                parent.append_epic(found)
            current = found
            parent = found
        if current is None:
            raise CodeStoryModelError("A story file needs a sub-epic folder")
        return current
