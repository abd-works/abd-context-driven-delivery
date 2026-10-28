"""CodeStoryModel - a StoryModel stored as a source-code tree.

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

Every story, background, scenario, and step read from a file keeps the code it was written with
(`written`, `setup`, and each step's `body`). Rendered back in the same language and unchanged, a node
is written exactly as read; otherwise it is spelled again with its bodies kept.

load fills this map from the files. save writes this map's epics and stories.
render and parse call those so existing callers keep working.
"""

from __future__ import annotations

import re
import textwrap
from typing import Dict, List, Optional, Tuple, Union

from cdd_guidance.practices.clean_engineering.model.call_graph import render_call_graph_block
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage, WrittenBlock, WrittenKey
from cdd_guidance.practices.stories.model.story_model import (
    Background,
    Epic,
    Increment,
    Scenario,
    Step,
    StepType,
    Story,
    StoryModel,
)


class CodeStoryModelError(Exception):
    """Raised when a folder tree is not a valid code story map."""


StepClause = Tuple[Step, str, List[Step]]
# One step, the verb it opens with, and the steps a language chains onto it.


def example_names_of(stories: List[Story]) -> List[str]:
    names: List[str] = []
    for story in stories:
        for scenario in story.scenarios:
            for name in scenario.examples:
                if name not in names:
                    names.append(name)
    return names


def flat_steps(steps: List[Step]) -> List[Step]:
    """Every step with its ands after it, in the order the file has them."""
    return [line for step in steps for line in (step, *step.ands)]


def as_read(written: Optional[WrittenBlock], language: CodeLanguage, key: WrittenKey) -> Optional[WrittenBlock]:
    """The lines a node was read with, while it is still in this language with the same key; otherwise None."""
    return written if written is not None and written.is_in(language, key) else None


def joined(lines: List[str], child: List[str], raw: bool, gap: List[str]) -> List[str]:
    """A child's lines after its parent's. A raw child brings the blank lines above it; a generic one gets the
    language's gap, unless it is the first thing inside its parent or a blank line is already there."""
    if raw or not lines or not lines[-1].strip():
        return lines + child
    return lines + gap + child


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
        body = self._take_background_comments(body)
        self.steps = self.steps_from(self.calls_in(body))
        for name in example_names or []:
            if re.search(rf"\b{re.escape(name)}\b", body):
                self.examples[name] = name

    @staticmethod
    def background_lines(scenario, prefix: str) -> List[str]:
        lines: List[str] = []
        for background in scenario.backgrounds:
            lines.append(f"{prefix}background: {background.name}")
            for step in background.steps:
                lines.append(f"{prefix}background-step: {step.keyword} | {step.text}")
                for extra in step.ands:
                    lines.append(f"{prefix}background-step: {extra.keyword} | {extra.text}")
        return lines

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

    @staticmethod
    def background_example_line(story: Story, prefix: str) -> str:
        import json

        if not story.backgrounds or not story.backgrounds[0].examples:
            return ""
        payload = {
            name: example.cells()
            for name, example in story.backgrounds[0].examples.items()
        }
        return f"{prefix}background-examples: {json.dumps(payload, ensure_ascii=False)}"

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

    def fill(self, content: str) -> None:
        scenario_type = type(self).scenario_type
        examples = scenario_type.example_names(content)
        backgrounds = scenario_type.backgrounds_in(content)
        for background in backgrounds:
            for name in examples:
                if re.search(rf"\b{re.escape(name)}\b", getattr(background, "body", "")):
                    background.examples[name] = name
        self.backgrounds = backgrounds
        self._take_background_examples(content)
        for name, body in scenario_type.scenario_blocks(content):
            self.add_scenario(name, body, examples)
        if self.backgrounds and self.backgrounds[0].examples:
            for scenario in self.scenarios:
                for background in scenario.backgrounds:
                    if background.examples:
                        continue
                    background.examples = self.backgrounds[0].examples.clone(background)

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
    """Source-tree story map. The epics and stories are the story map. load and save are the files."""

    LEAF_EXTENSION: str = ""
    LANGUAGE_LINE_COMMENT: str = "//"
    epic_type = CodeEpic
    story_type = CodeStory
    increment_type = CodeIncrement

    def __init__(self, source: "StoryModel | str | None" = None, tests_root: str | None = None):
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

    def save(self) -> Dict[str, str]:
        """Write this story map's epics and stories to source files."""
        tree: Dict[str, str] = {}
        for epic in self.epics:
            self._render_epic(
                epic=epic,
                epic_slug=self._folder_slug(epic, self.epics),
                tree=tree,
            )
        return tree

    def render(
        self,
        canonical: StoryModel,
        previous: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Write canonical to source files. previous is the tree already on disk: whatever canonical has
        no code for in this language takes that tree's code for the same epic, story, scenario, and step."""
        if isinstance(previous, str) and previous:
            raise CodeStoryModelError("previous must be the path-to-content map of the story tree already on disk")
        model = self._copy_of(canonical)
        if previous:
            model.adopt_code(self.parse(previous))
        return model.save()

    def _copy_of(self, canonical: StoryModel) -> "CodeStoryModel":
        """canonical in this language, with this model's settings."""
        return type(self)(canonical, tests_root=self._tests_root)

    # -- The one story render. A language model overrides only the spelling operations further down.

    language: Optional[CodeLanguage] = None
    scenario_indent = "  "
    scenario_gap = [""]
    # The blank lines a language writes between two generic scenarios; Python writes them back to back.
    statement_end = ""

    def write_epics(self, files: Dict[str, str]) -> Dict[str, str]:
        """Every epic's folders and sub-epic files, added to files."""
        for epic in self.epics:
            self._write_epic(epic, self.tests_root, files)
        return files

    def read_from_code(self) -> bool:
        """Some sub-epic or story in this tree was read from a file in this language."""
        nodes = [node for epic in self.all_epics() for node in (epic, *epic.stories)]
        return any(node.written is not None and node.written.language is self.language for node in nodes)

    def story_text(self, story: Story) -> str:
        return "\n".join(self.story_lines(story) + [""])

    def story_lines(self, story: Story) -> List[str]:
        """Read in this language and unchanged: every line as read. Each scenario decides for itself."""
        written = as_read(story.written, self.language, story.code_key)
        lines = written.lead + written.heading + written.inside if written is not None else self._story_head(story)
        lines = self._scenarios_after(lines, story)
        if written is not None:
            return lines + written.closing + written.close
        return lines + ([] if story.scenarios else self.no_scenarios_lines()) + self.story_close()

    def _scenarios_after(self, lines: List[str], story: Story) -> List[str]:
        opened = len(lines)
        for scenario in story.scenarios:
            gap = [] if len(lines) == opened else self.scenario_gap
            lines = joined(lines, self.scenario_lines(scenario, self.scenario_indent), self._is_as_read(scenario), gap)
        return lines

    def scenario_lines(self, scenario: Scenario, indent: str) -> List[str]:
        """Read in this language and unchanged: every line as read. Otherwise the generic spelling, bodies kept."""
        written = as_read(scenario.written, self.language, scenario.code_key)
        if written is not None:
            return written.lead + written.heading + written.inside + written.closing + written.close
        inner = indent + self.language.indent
        lines = self.scenario_open(scenario, indent) + scenario.setup.lines_in(self.language, inner, "")
        for background in scenario.backgrounds:
            lines.extend(self.scenario_background_lines(background, inner))
        if scenario.examples:
            lines.extend(self.examples_lines(scenario, inner))
        for clause in self.clauses(scenario.steps):
            lines.extend(self.step_lines(clause, inner))
        if not scenario.steps and scenario.setup.is_empty:
            lines.extend(f"{inner}{line}" for line in self.empty_block())
        return lines + self.scenario_close(indent)

    def step_lines(self, clause: "StepClause", indent: str) -> List[str]:
        """One step and the steps chained onto it, each with its body. A body not written yet gets the placeholder."""
        step, verb, continuations = clause
        lines = [self.step_open(verb, step, indent)] + self.body_lines(step, indent + self.language.indent)
        lines.extend(line for line in [self.step_close(indent)] if line is not None)
        for extra in [*step.ands, *continuations]:
            lines.append(self.and_open(extra, indent))
            lines.extend(self.body_lines(extra, self.and_body_indent(indent)))
            lines.extend(line for line in [self.and_close(indent)] if line is not None)
        lines[-1] += self.statement_end
        return lines

    def body_lines(self, step: Step, indent: str) -> List[str]:
        """The step's body; an empty one carries the realization call graph as comments above the placeholder."""
        scaffold: List[str] = []
        if step.body.is_empty and step.call_graph:
            graph = textwrap.dedent(render_call_graph_block(step.call_graph)).splitlines()
            scaffold = [f"{indent}{self.language.comment(line)}" for line in graph]
        return scaffold + step.body.lines_in(self.language, indent, self.step_placeholder())

    def clauses(self, steps: List[Step]) -> List["StepClause"]:
        """(step, the verb it opens with, steps chained onto it). Each language decides what chains."""
        return [(step, self.verb(step), []) for step in steps]

    def verb(self, step: Step) -> str:
        return step.keyword.lower()

    def read_code(self, content: str, stories: List[Story], path: str) -> Optional[WrittenBlock]:
        """Give each story, background, scenario, and step the code it was written with; return the file's own code.
        A language that cannot read its blocks returns None and its stories are written generically."""
        return None

    def file_name(self, epic: Epic) -> str:
        raise NotImplementedError(f"{type(self).__name__} must name its story files")

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell its file header")

    def folder_files(self, epic: Epic, folder: str, files: Dict[str, str]) -> None:
        """Files an epic folder holds besides its sub-epics; none unless a language adds them."""
        return

    def story_open(self, story: Story) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell story_open")

    def story_close(self) -> List[str]:
        return []

    def story_background_lines(self, background: Background) -> List[str]:
        return []

    def no_scenarios_lines(self) -> List[str]:
        return []

    def scenario_open(self, scenario: Scenario, indent: str) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell scenario_open")

    def scenario_close(self, indent: str) -> List[str]:
        return []

    def scenario_background_lines(self, background: Background, indent: str) -> List[str]:
        return []

    def examples_lines(self, scenario: Scenario, indent: str) -> List[str]:
        return [f"{indent}{self.language.comment('examples: ' + ', '.join(scenario.examples))}"]

    def step_open(self, verb: str, step: Step, indent: str) -> str:
        raise NotImplementedError(f"{type(self).__name__} must spell step_open")

    def step_close(self, indent: str) -> Optional[str]:
        return None

    def and_open(self, step: Step, indent: str) -> str:
        raise NotImplementedError(f"{type(self).__name__} must spell and_open")

    def and_body_indent(self, indent: str) -> str:
        return indent + self.language.indent

    def and_close(self, indent: str) -> Optional[str]:
        return None

    def step_placeholder(self) -> str:
        raise NotImplementedError(f"{type(self).__name__} must spell step_placeholder")

    def empty_block(self) -> List[str]:
        """What a scenario with nothing in it needs to stay valid code."""
        return []

    def _write_epic(self, epic: Epic, parent: str, files: Dict[str, str]) -> None:
        """An epic with child epics is a folder its children write into; a sub-epic with stories is one file."""
        if not epic.epics:
            self._write_stories(epic, parent, files)
            return
        folder = f"{parent}/{epic.slug()}"
        self.folder_files(epic, folder, files)
        for child in epic.epics:
            self._write_epic(child, folder, files)
        self._write_stories(epic, folder, files)

    def _write_stories(self, epic: Epic, parent: str, files: Dict[str, str]) -> None:
        """One file for a sub-epic's stories: back to the path it was read from, else named for the sub-epic."""
        if not epic.stories:
            return
        written = as_read(epic.written, self.language, epic.name)
        path = written.path if written is not None else f"{parent}/{self.file_name(epic)}"
        files[path] = self._file_text(epic, parent, written)

    def _file_text(self, epic: Epic, parent: str, written: Optional[WrittenBlock]) -> str:
        """The file's code above and below its stories as read, else the file header; each story renders itself."""
        lines = list(written.inside) if written is not None else self.file_header(epic, parent)
        opened = len(lines)
        for story in epic.stories:
            gap = [] if len(lines) == opened else [""]
            lines = joined(lines, self.story_lines(story), self._is_as_read(story), gap)
        return "\n".join(lines + (written.closing if written is not None else [""]))

    def _story_head(self, story: Story) -> List[str]:
        lines = self.story_open(story) + story.setup.lines_in(self.language, self.language.indent, "")
        for background in story.backgrounds:
            lines.extend(self.story_background_lines(background))
        return lines

    def _is_as_read(self, node: Union[Story, Scenario]) -> bool:
        return as_read(node.written, self.language, node.code_key) is not None

    def adopt_code(self, kept: "CodeStoryModel") -> None:
        """Each epic, story, background, scenario, and step without code in this language takes kept's code
        for the node with the same name."""
        if self.language is None:
            return
        epics = {epic.name: epic for epic in kept.all_epics()}
        stories = {story.name: story for epic in epics.values() for story in epic.stories}
        for epic in self.all_epics():
            self._take_code(epic, epics.get(epic.name))
            for story in epic.stories:
                self._take_story_code(story, stories.get(story.name))

    def all_epics(self) -> List[Epic]:
        found, pending = [], list(self.epics)
        while pending:
            epic = pending.pop(0)
            found.append(epic)
            pending.extend(epic.epics)
        return found

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

    def load(self, external: Dict[str, str]) -> "CodeStoryModel":
        """Read source files into this story map's epics and stories."""
        if not isinstance(external, dict):
            raise CodeStoryModelError("Tree must be a mapping of paths to file content")
        self.epics.clear()
        epics_by_slug: Dict[str, Epic] = {}
        for path in self._ordered_paths(external):
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
            raise CodeStoryModelError(
                "Tree contains no recognisable Epic folders under the tests root"
            )
        return self

    def parse(self, external: Dict[str, str]) -> "CodeStoryModel":
        return type(self)(self._tests_root).load(external)

    def _ordered_paths(self, external: Dict[str, str]) -> List[str]:
        def key(path: str) -> tuple:
            match = re.search(r"Orders:\s*([0-9.]+)", external.get(path, ""))
            order = tuple(int(part) for part in match.group(1).split(".") if part) if match else (10**6,)
            return (order, path)

        return sorted(external, key=key)

    def epic_for(self, slug: str) -> Epic:
        for epic in self.epics:
            if epic.slug() == slug:
                return epic
        epic = self.epic_type(self.epic_type.name_from_slug(slug), len(self.epics) + 1)
        self.append_epic(epic)
        return epic

    def take_sub_epic_file(self, parts: List[str], content: str, source_file: str = "") -> bool:
        """One file is one sub-epic. Every story in the file belongs to it.

        A parent folder with the same slug is that sub-epic, so the file is not a second level.
        A file in its own top folder is the epic itself, and its stories sit on the epic.
        """
        if len(parts) < 2:
            return False
        stem_slug = self._file_stem_slug(parts[-1])
        if not stem_slug:
            return False
        epic_name = CodeEpic.epic_name_in(content)
        leaf_slug = CodeEpic(epic_name).slug() if epic_name else stem_slug
        if not leaf_slug:
            return False
        folders = list(parts[:-1])
        if folders[-1] == stem_slug:
            folders = folders[:-1]
        if not folders:
            holder = self.epic_for(stem_slug)
        else:
            epic = self.epic_for(folders[0])
            nested = folders[1:]
            if not nested or nested[-1] != leaf_slug:
                nested = [*nested, leaf_slug]
            holder = self.sub_epic_for(epic, nested)
        if epic_name:
            holder.name = epic_name
        self._take_stories(holder, content, source_file.replace("\\", "/"))
        return True

    def _take_stories(self, holder: Epic, content: str, source_file: str) -> None:
        """The file's stories onto the sub-epic that holds them, each with where it is and the code it was written with."""
        from cdd_guidance.practices.stories.model.source_location import SourceLocation

        stories = self.story_type.load_all(content)
        for story in stories:
            if source_file:
                line = self._quoted_name_line(content, story.name)
                story.source = SourceLocation(source_file, line, line)
            holder.append_story(story)
        written = self.read_code(content, stories, source_file)
        if written is not None:
            written.key = holder.name
            holder.written = written

    def _quoted_name_line(self, content: str, name: str) -> int:
        for index, line in enumerate(content.splitlines(), start=1):
            if f"'{name}'" in line or f'"{name}"' in line:
                return index
        return 1

    def _file_stem_slug(self, filename: str) -> str:
        for suffix in (
            ".story.shared.ts",
            "_story.test.ts",
            "_story.spec.ts",
            "_story.test.py",
            "_story.test.js",
            "Story.java",
        ):
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
            raise CodeStoryModelError("A story file needs a sub-epic folder")
        return current

    def _hydrate_leaf_sub_epic_from_content(self, current_sub_epic: Epic) -> None:
        # WHY: language backends override this to reconstruct story and scenario
        # structure when parsing generated source trees back into StoryModel.
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
            )

    def _render_sub_epic(
        self,
        sub_epic: Epic,
        sibling_epics: List[Epic],
        parent_path: str,
        owning_epic: Epic,
        tree: Dict[str, str],
    ) -> None:
        folder = f"{parent_path}/{self._folder_slug(sub_epic, sibling_epics)}"
        for nested in sub_epic.epics:
            self._render_sub_epic(
                sub_epic=nested,
                sibling_epics=sub_epic.epics,
                parent_path=folder,
                owning_epic=owning_epic,
                tree=tree,
            )
        if sub_epic.stories or not sub_epic.epics:
            leaf_path = f"{folder}/{sub_epic.slug()}{self.LEAF_EXTENSION}"
            tree[leaf_path] = self._render_leaf_file(sub_epic, owning_epic)

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
