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

import json
import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, Union

from harness.annotations.name import Name
from cdd_guidance.practices.source_code import BracketStructure
from cdd_guidance.practices.source_code import CodeBody, CodeLanguage, WrittenBlock
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
from cdd_guidance.practices.stories.model.reshaped_story_file import ReshapedStoryFile
from harness.guidance.practice_formats import Reshaped, Written
from cdd_guidance.practices.stories.model.story_recording import StorySources
from cdd_guidance.practices.stories.model.story_file import CodeBlock, flat_steps, read_step_code
from cdd_guidance.practices.stories.model.story_writing import OUTLINE_EXAMPLES, SCENARIO_EXAMPLES, StoryFilePlace, StoryWriting, as_read

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_file import StoryFile


class CodeStoryModelError(Exception):
    """Raised when a folder tree is not a valid code story map."""


# A story file whose header gives no order sorts after every one that does.
_UNORDERED = (10**6,)
_EPIC_HEADER = re.compile(r"Epic:\s*(.+)")
_BACKGROUND_HEADING = re.compile(r"\s*(?:#|//|\*)\s*background:\s*(.+)")
_BACKGROUND_STEP = re.compile(r"\s*(?:#|//|\*)\s*background-step:\s*(\w+)\s*\|\s*(.*)")
# A story test names its tier after the story; the tier is not part of the story's name.
_TIER_NEUTRAL = re.compile(r"\s*\(tier-neutral\)\.?\s*$")
_STEP_TYPES = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}


# The comment that carries a scenario's example rows, by name, and says whether the scenario is an outline.
_EXAMPLE_ROWS = re.compile(rf"(?P<kind>{SCENARIO_EXAMPLES}|{OUTLINE_EXAMPLES}):\s*(?P<rows>\{{.*\}})")


def unescaped(quoted: str) -> str:
    """A quoted name or step text as it reads once its escapes are taken out: the one unescape every language uses."""
    return quoted.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


class CodeStoryNode:
    """Name forms shared by every code node; the kebab folder name is the story node's own slug."""

    def snake(self) -> str:
        return Name(self.name).title_snake or "unnamed"


class StorySyntax:
    """How one language's story files write stories, scenarios and steps: the patterns its story tests are read by.
    A language gives its own patterns, and its own reading where a pattern cannot say it; the story and scenario
    classes of the language read their text through the one syntax they hold (``syntax``)."""

    # How a language opens a scenario, with the scenario's name in the group `name`.
    scenario_pattern: re.Pattern = re.compile(r"(?!)")
    # How a language imports example names from an examples module, with the names in the group `names`; none for a
    # language whose story files import no examples.
    import_pattern: Optional[re.Pattern] = None
    # The comment line that lists the examples a story file uses.
    examples_line: re.Pattern = re.compile(r"(?<![-\w])examples:\s*(.+)")
    # What opens a line of the comment that describes a story in this language.
    description_mark = r"\*\s*"
    # Where a file's next story starts, and what a piece of the file holds when it is a story.
    story_start: re.Pattern = re.compile(r"(?!)")
    story_mark: re.Pattern = re.compile(r"Story:")
    # The story's name as a story file writes it, in the group `name`.
    story_name_pattern: re.Pattern = re.compile(r"Story:\s*(?P<name>.+)")

    def steps_in(self, body: str) -> List[Step]:
        """The steps the step calls in a body of this language make."""
        return self.steps_from(self._calls_in(body))

    def steps_from(self, calls: List[tuple]) -> List[Step]:
        """A step for each (keyword, text) call, an And or But chained onto the step before it."""
        steps: List[Step] = []
        previous: Optional[Step] = None
        for keyword, text in calls:
            word = keyword.lower()
            if word in ("and", "but") and previous is not None:
                previous.continue_with(word, text)
                continue
            step_type = StepType.THEN if word == "but" else _STEP_TYPES.get(word)
            if step_type is None:
                continue
            step = Step(text, step_type, len(steps) + 1)
            step.keyword = word
            steps.append(step)
            previous = step
        return steps

    def scenario_blocks(self, content: str) -> List[tuple]:
        """(name, body) of each scenario in a file; a scenario runs to the next one."""
        matches = list(self.scenario_pattern.finditer(content))
        blocks = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
            blocks.append((match.group("name").strip(), content[match.end() : end]))
        return blocks

    def backgrounds_in(self, content: str) -> List[Background]:
        """The backgrounds a story's text writes."""
        raise NotImplementedError(f"{type(self).__name__} must read its backgrounds")

    def example_names(self, content: str) -> List[str]:
        """The example names a story file imports and the ones its examples comment lists, each once, in order."""
        listed = [match.group("names") for match in self.import_pattern.finditer(content)] if self.import_pattern is not None else []
        listed += [match.group(1) for match in self.examples_line.finditer(content)]
        names: List[str] = []
        for part in (part for line in listed for part in line.split(",")):
            name = part.strip().split(" as ")[-1].strip()
            if name and name != "(" and name not in names:
                names.append(name)
        return names

    def example_imports(self, content: str) -> str:
        """The lines of a story file that import its examples, which every story in the file reads its example names
        from."""
        pattern = self.import_pattern
        return "\n".join(match.group(0) for match in pattern.finditer(content)) if pattern is not None else ""

    def story_name(self, content: str) -> str:
        """The story's name as the text of one story writes it, without the tier a story test names after it. Every
        language reads a name this one way, so a story test's scenarios find the story of the same name on the map."""
        found = self._name_in(content)
        return _TIER_NEUTRAL.sub("", found.strip() if found else "").strip()

    def story_texts(self, content: str) -> List[str]:
        """The text of each story in one file: the file split where each story starts, each piece that holds a story."""
        return [piece for piece in self.story_start.split(content) if self.story_mark.search(piece)]

    def _calls_in(self, body: str) -> List[tuple]:
        """The (keyword, text) of each step call in a body of this language."""
        raise NotImplementedError(f"{type(self).__name__} must read its step calls")

    def _name_in(self, content: str) -> Optional[str]:
        """The story's name as the text of one story writes it; None when it writes none."""
        match = self.story_name_pattern.search(content)
        return match.group("name") if match else None

    def _balanced(self, text: str, open_at: int) -> str:
        close = BracketStructure(text).closing_bracket(open_at)
        return text[open_at + 1 : close] if close is not None else text[open_at + 1 :]

    def _outside_scenarios(self, body: str) -> str:
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
            inner = self._balanced(body, brace)
            index = brace + len(inner) + 2
        return "".join(pieces)


class CodeScenario(Scenario, CodeStoryNode):
    """One scenario. Steps, ands, and examples are the story-model shape on every language."""

    syntax = StorySyntax()
    """How this language writes its story files, which every scenario of the language reads its text through."""

    def read(self, body: str, example_names: List[str] | None = None) -> None:
        body = self._take_background_comments(body)
        self.steps = self.syntax.steps_in(body)
        for name in example_names or []:
            if re.search(rf"\b{re.escape(name)}\b", body):
                self.examples[name] = name
        self._take_example_rows(body)

    def _take_example_rows(self, body: str) -> None:
        """The rows its examples comment carries, each example by name with its values; rows marked as an outline's
        make this scenario an outline."""
        rows = _EXAMPLE_ROWS.search(body)
        if rows is None:
            return
        self.is_outline = rows.group("kind") == OUTLINE_EXAMPLES
        for name, cells in json.loads(rows.group("rows")).items():
            self.examples[name] = cells or name

    def _take_background_comments(self, body: str) -> str:
        """The body without its background comments, which become this scenario's background."""
        kept: List[str] = []
        calls: List[tuple] = []
        names: List[str] = []
        for line in body.splitlines(keepends=True):
            heading = _BACKGROUND_HEADING.match(line)
            step = _BACKGROUND_STEP.match(line)
            if heading:
                names.append(heading.group(1).strip())
            elif step:
                calls.append((step.group(1), step.group(2).strip()))
            else:
                kept.append(line)
        if names or calls:
            self._take_background(names[-1] if names else "background", calls)
        return "".join(kept)

    def _take_background(self, name: str, calls: List[tuple]) -> None:
        background = Background(name, 1)
        background.steps = self.syntax.steps_from(calls)
        self.backgrounds = [background]

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


class CodeStory(Story, CodeStoryNode):
    scenario_type = CodeScenario
    syntax = CodeScenario.syntax
    """How this language writes its story files: the syntax its scenarios read their text through."""

    def _read_description(self, content: str) -> None:
        """The actor, kind, domain terms, and evidence the story's comment names; a story whose comment names no kind
        is a user story."""
        mark = self.syntax.description_mark
        actor = re.search(rf"{mark}Actor:\s*(.+)", content, re.MULTILINE)
        if actor:
            self.actors = [actor.group(1).strip()]
        kind = re.search(rf"{mark}Kind:\s*(user|system|technical)\b", content, re.MULTILINE)
        if kind:
            self.story_type = StoryType.from_mark(kind.group(1))
        terms = re.search(rf"{mark}Domain terms:\s*(.+)$", content, re.MULTILINE)
        if terms:
            self.domain_terms = [term.strip() for term in terms.group(1).split(",") if term.strip()]
        evidence = re.search(rf"{mark}Evidence:\s*([A-Za-z][A-Za-z ,-]*)", content, re.MULTILINE)
        if evidence:
            self.evidence = [part.strip() for part in evidence.group(1).split(",") if part.strip()]

    @classmethod
    def load_all(cls, content: str) -> List["CodeStory"]:
        """Every story in one sub-epic file: the file split where each story starts, each piece that holds a story
        read as one; the whole file as one story when no piece does."""
        stories = [cls.load(piece) for piece in cls.syntax.story_texts(content)]
        return stories or [cls.load(content)]

    @classmethod
    def load_file(cls, content: str, project: Optional[Path]) -> List["CodeStory"]:
        """Every story in one story file of project, the folder its paths are named from; a language whose story files
        read other files of the project, such as an examples module, finds them there."""
        return cls.load_all(content)

    @classmethod
    def load(cls, content: str, scenario_blocks: Optional[List[CodeBlock]] = None) -> "CodeStory":
        """The story the text of one story holds: its name, its description, then its backgrounds and scenarios, one
        for each of scenario_blocks when its story file found them, else as the text writes them."""
        story = cls(cls.syntax.story_name(content), 1)
        story._read_description(content)
        story._fill(content, scenario_blocks)
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

    def _add_scenario(self, name: str, body: str, example_names: List[str]) -> None:
        scenario = self.scenario_type(name=name, sequential_order=len(self.scenarios) + 1)
        scenario.read(body, example_names)
        self.scenarios.append(scenario)

    def _take_background_examples(self, content: str) -> None:
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
            return self.syntax.scenario_blocks(content)
        return [(item.name, item.body_text) for item in scenario_blocks]

    def _fill(self, content: str, scenario_blocks: Optional[List[CodeBlock]] = None) -> None:
        examples = self.syntax.example_names(content)
        backgrounds = self.syntax.backgrounds_in(content)
        for background in backgrounds:
            for name in examples:
                if re.search(rf"\b{re.escape(name)}\b", getattr(background, "body", "")):
                    background.examples[name] = name
        self.backgrounds = backgrounds
        self._take_background_examples(content)
        for name, body in self._scenario_texts(content, scenario_blocks):
            self._add_scenario(name, body, examples)
        if self.backgrounds and self.backgrounds[0].examples:
            self._share_background_examples()

    def _share_background_examples(self) -> None:
        """Give each scenario background that holds no examples those of the story's own background."""
        shared = self.backgrounds[0].examples
        for background in (background for scenario in self.scenarios for background in scenario.backgrounds):
            if not background.examples:
                background.examples = shared.clone(background)


class CodeIncrement(Increment, CodeStoryNode):
    pass


class CodeEpic(Epic, CodeStoryNode):
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

    def is_story_file(self, path: "str | Path") -> bool:
        """True when the file at path is a story file in this language, which this model's story type reads."""
        posix = str(path).replace("\\", "/")
        return posix.endswith(self.story_file_suffixes) and self.not_story_paths.search(posix) is None

    def __init__(self, source: "StoryModel | str | None" = None, tests_root: str | None = None):
        if isinstance(source, str):
            tests_root = source
            source = None
        self._project: Optional[Path] = None
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
        return self._write_epics({})

    def render(self, canonical: StoryModel, written: Written = Written()) -> Dict[str, str]:
        """Write canonical to source files. The previous files are the tree already on disk, each file's text by its
        path: whatever canonical has no code for in this language takes that tree's code for the same epic, story,
        scenario, and step."""
        previous = written.previous
        if isinstance(previous, str) and previous:
            raise CodeStoryModelError("previous must be the path-to-content map of the story tree already on disk")
        model = self.copy_of(canonical)
        if previous:
            model._adopt_code(self.parse(previous))
        return model.save()

    def copy_of(self, source: Optional[StoryModel]) -> "CodeStoryModel":
        """source in this language, with this model's settings; an empty map when source is None."""
        return type(self)(source, tests_root=self._tests_root)

    def reshape(self, rendered: str, existing: str) -> Reshaped:
        """rendered, the text a render made for one story file, written onto existing, the text that file holds now:
        the file keeps every line it has, gains the steps, scenarios and stories only the render holds, each empty,
        and marks those only the file holds as no longer in the model (*ReshapedStoryFile*). The Render action asks
        it of the format's adapter before it writes onto a story file already there."""
        return ReshapedStoryFile(self, rendered, existing).reshaped()

    language: Optional[CodeLanguage] = None

    @cached_property
    def writing(self) -> StoryWriting:
        """How this model's language writes its story files, made once."""
        return self.writing_type(self.language)

    def _write_epics(self, files: Dict[str, str]) -> Dict[str, str]:
        """Every epic's folder and story files, added to files, laid out as the acceptance tests fidelity declares
        them: an epic and each sub-epic is a folder, and each story a file in a folder of its own under it."""
        for epic in self.epics:
            self._write_epic(epic, self.tests_root, f"{self.tests_root}/{epic.slug}/examples", files)
        return files

    @property
    def read_from_code(self) -> bool:
        """Some story in this tree was read from a file in this language."""
        stories = [story for epic in self.descendants.epics() for story in epic.stories]
        read = [written for story in stories for written in (story.written, story.file_written) if written is not None]
        return any(written.language is self.language for written in read)

    def story_file(self, content: str) -> Optional["StoryFile"]:
        """The story file content is, as this language finds its blocks; None for a language that does not read its
        blocks, whose stories are written generically."""
        return None

    def _write_epic(self, epic: Epic, parent: str, examples_folder: str, files: Dict[str, str]) -> None:
        """An epic is a folder under parent, which its sub-epics and its own stories write into; examples_folder is
        the examples folder of the top-level epic above it."""
        folder = f"{parent}/{epic.slug}"
        for child in epic.epics:
            self._write_epic(child, folder, examples_folder, files)
        for written, stories in self._story_files(epic):
            path, text = self.writing.story_file(StoryFilePlace(epic, stories, folder, examples_folder), written)
            files[path] = text

    def _story_files(self, epic: Epic) -> List[Tuple[Optional[WrittenBlock], List[Story]]]:
        """The epic's stories by the story file each is written to. The stories read together from one file of this
        language go back to it together, while their epic keeps the name it was read with: a shared story file, or
        a file a person wrote several stories in. Every other story has a file of its own."""
        files: List[Tuple[Optional[WrittenBlock], List[Story]]] = []
        for story in epic.stories:
            written = as_read(story.file_written, self.language, epic.name)
            together = next((stories for kept, stories in files if kept is not None and kept is written), None)
            if together is not None:
                together.append(story)
            else:
                files.append((written, [story]))
        return files

    def _adopt_code(self, kept: "CodeStoryModel") -> None:
        """Each epic, story, background, scenario, and step without code in this language takes kept's code
        for the node with the same name."""
        if self.language is None:
            return
        epics = {epic.name: epic for epic in kept.descendants.epics()}
        stories = {story.name: story for epic in epics.values() for story in epic.stories}
        for epic in self.descendants.epics():
            self._take_code(epic, epics.get(epic.name))
            for story in epic.stories:
                self._take_story_code(story, stories.get(story.name))

    def _take_story_code(self, story: Story, kept: Optional[Story]) -> None:
        """A story, its backgrounds, its scenarios, and theirs take kept's code for the nodes with the same name."""
        if kept is None:
            return
        self._take_code(story, kept)
        if story.file_written is None or story.file_written.language is not self.language:
            story.file_written = kept.file_written
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

    def _take_code(self, node: Union[Epic, Story, Background, Scenario], kept: Optional[Union[Epic, Story, Background, Scenario]]) -> None:
        language = self.language
        if kept is None:
            return
        if node.written is None or node.written.language is not language:
            node.written = kept.written
        if node.setup.language is not language:
            node.setup = kept.setup

    def _take_step_bodies(self, node: Union[Background, Scenario], kept: Optional[Union[Background, Scenario]]) -> None:
        if kept is None:
            return
        language = self.language
        bodies = {step.text: step.body for step in flat_steps(kept.steps)}
        for step in flat_steps(node.steps):
            step.body = step.body.in_language_of(bodies.get(step.text, CodeBody()), language)

    def load(self, external: Dict[str, str], *, on_file: Optional[Callable[[str], None]] = None, project: Optional[Path] = None) -> "CodeStoryModel":
        """This story map's epics and stories from the story files in external, path to text, under the tests root:
        each file one sub-epic, in the order its header gives. on_file hears each file as it is read. A story file that
        reads other files of project, such as its examples module, finds them there."""
        if not isinstance(external, dict):
            raise CodeStoryModelError(f"{type(self).__name__} reads a path-to-content dict of story files")
        self.epics.clear()
        self.sources = StorySources()
        self._project = project
        for path, text in external.items():
            self.sources.add(path, text)
        paths = [path for path in self._ordered_paths(external) if self.is_story_file(path)]
        with self.batch_schema_sync():
            for index, path in enumerate(paths, start=1):
                if on_file is not None:
                    on_file(f"{index}/{len(paths)} · {path}")
                self._read_story_file(path, external[path])
        return self

    def parse(self, text: Dict[str, str], file: str = "") -> "CodeStoryModel":
        """A new map read from the story files in text, each file's text by its path, with this model's settings."""
        return self.copy_of(None).load(text)


    def _ordered_paths(self, external: Dict[str, str]) -> List[str]:
        def key(path: str) -> tuple:
            match = re.search(r"Orders:\s*([0-9.]+)", external.get(path, ""))
            order = tuple(int(part) for part in match.group(1).split(".") if part) if match else _UNORDERED
            return (order, path)

        return sorted(external, key=key)

    def _epic_for(self, slug: str) -> Epic:
        for epic in self.epics:
            if epic.slug == slug:
                return epic
        epic = self.epic_type(self._name_from_slug(slug), len(self.epics) + 1)
        self.epics.append(epic)
        return epic

    def _read_story_file(self, path: str, content: str) -> None:
        """The stories of one story file go on the epic or sub-epic its folders name; a file outside the tests root,
        or at its top, holds none.

        A story test that holds one story, in a folder named as the file is, is that story's own file, as the
        acceptance tests fidelity declares it: the folders above the story's are its epic and sub-epics. Any other
        file, a shared story file and a screen spec among them, is one sub-epic's: a parent folder with the same slug as the file, or as the epic its header names, is that sub-epic,
        so the file is not a second level, and a file in its own top folder is the epic itself.
        """
        parts = self._under_tests_root(path.strip("/").replace("\\", "/").split("/"))
        stem_slug = self._stem_slug(parts[-1]) if parts is not None and len(parts) >= 2 else ""
        if not stem_slug:
            return
        source_file = path.replace("\\", "/")
        stories, written = self.stories_of(content, source_file, self._project)
        epic_name = self._epic_name_in(content)
        folders = parts[:-1]
        epic_slug = (Name(epic_name).title_slug or "unnamed") if epic_name else ""
        if parts[-1].endswith(self.story_file_suffixes[0]) and epic_slug != stem_slug and self._is_a_story_s_own(stories, folders, stem_slug):
            slugs = folders[:-1]
        else:
            slugs = self._epic_slugs(folders, stem_slug, epic_slug or stem_slug)
        holder = self._epic_for(slugs[0]) if len(slugs) == 1 else self._sub_epic_for(self._epic_for(slugs[0]), slugs[1:])
        if epic_name:
            holder.name = epic_name
        self._take_stories(holder, stories, written, content, source_file)

    def _is_a_story_s_own(self, stories: list, folders: List[str], stem_slug: str) -> bool:
        """Whether a story test is one story's own: it holds that story alone, named as the file is, in a folder of
        the same name under at least one epic's folder."""
        if len(stories) != 1 or len(folders) < 2 or folders[-1] != stem_slug:
            return False
        return (Name(stories[0].name).title_slug or "unnamed") == stem_slug

    def _take_stories(self, holder: Epic, stories: list, written: Optional[WrittenBlock], content: str, source_file: str) -> None:
        """The file's stories onto the epic that holds them, each with where it is, the code it was written with, and
        the file it was read with."""
        if written is not None:
            written.key = holder.name
        for story in stories:
            if source_file and not story.has_source_file:
                line = self._quoted_name_line(content, story.name)
                story.source = source_at(source_file, line)
            story.file_written = written
            holder.stories.append(story)

    def _quoted_name_line(self, content: str, name: str) -> int:
        """The line that quotes name, counted from 1; the first line when none does."""
        for index, line in enumerate(content.splitlines(), start=1):
            if f"'{name}'" in line or f'"{name}"' in line:
                return index
        return 1

    def _stem_slug(self, filename: str) -> str:
        """The kebab slug of a story file's name without the story-file suffix it ends with; empty for any other file."""
        suffix = next((item for item in self.story_file_suffixes if filename.endswith(item)), None)
        return Name(filename[: -len(suffix)]).kebab if suffix else ""

    def _epic_slugs(self, folders: List[str], stem_slug: str, leaf_slug: str) -> List[str]:
        """The epic, then each sub-epic, a story file sits in, from the folders above it under the tests root. A last
        folder with the file's or its epic's slug is that sub-epic, not a second level; a file in its own top folder is
        the epic itself."""
        folders = folders[:-1] if folders and folders[-1] in (stem_slug, leaf_slug) else list(folders)
        if not folders:
            return [leaf_slug]
        nested = folders[1:]
        return [folders[0], *(nested if nested and nested[-1] == leaf_slug else [*nested, leaf_slug])]

    def _epic_name_in(self, content: str) -> str:
        """The epic a story file's header names; empty when it names none."""
        match = _EPIC_HEADER.search(content)
        return match.group(1).strip() if match else ""

    def _name_from_slug(self, slug: str) -> str:
        """An epic's name from the folder it is read from, for a file whose header names none."""
        return slug.replace("-", " ").title()

    def stories_of(self, content: str, source_file: str, project: Optional[Path] = None) -> tuple:
        """The stories of one story file at source_file, each with the code its scenarios and steps are written with,
        and the file's own code around them; none of that code when this language does not read a file's blocks. A
        story file that reads other files of project, such as an examples module, finds them there."""
        code = self.story_file(content)
        read = code.stories(self.story_type, source_file, project) if code is not None else None
        return read if read is not None else (self.story_type.load_file(content, project), None)

    def _sub_epic_for(self, epic: Epic, slugs: List[str]) -> Epic:
        parent = epic
        current: Optional[Epic] = None
        for slug in slugs:
            found = next((item for item in parent.epics if item.slug == slug), None)
            if found is None:
                found = self.epic_type(self._name_from_slug(slug), len(parent.epics) + 1)
                parent.epics.append(found)
            current = found
            parent = found
        if current is None:
            raise CodeStoryModelError("A story file needs a sub-epic folder")
        return current
