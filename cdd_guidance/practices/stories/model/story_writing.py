"""StoryWriting - how one language writes a story map's stories into its story files.

A code format holds one writing for its language beside the reader of its story files (*StoryFile*). The writing is
the one story render every language shares: a node read in this language and unchanged is written exactly as read,
and any other node is spelled again with its bodies kept. What a language spells differently it gives as data (the
lines and templates below) or, where a template cannot say it, as its own operation (`story_open`, the background
lines, `file_header`).
"""

from __future__ import annotations

import json
import re
import textwrap
from typing import Dict, List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage, WrittenBlock, WrittenKey
from cdd_guidance.practices.stories.model.story_model import Background, Epic, Scenario, Step, Story, StoryType

# The comment that carries a scenario's example rows in a story file, by whether the scenario is an outline.
SCENARIO_EXAMPLES = "scenario-examples"
OUTLINE_EXAMPLES = "outline-examples"
# A name Python, TypeScript, JavaScript and Java can all import.
_IMPORTABLE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class StepClause:
    """One step, the verb it opens with, and the steps a language chains onto it."""

    def __init__(self, step: Step, verb: str) -> None:
        self.step = step
        self.verb = verb
        self.continuations: List[Step] = []


def example_names_of(stories: List[Story]) -> List[str]:
    """Each example the stories' scenarios use whose name a language can import, once, in order: what a new story file
    imports. An example named in words, as a table row of a scenarios file is, is no name in code, so it stays on the
    scenario's examples comment."""
    names: List[str] = []
    for story in stories:
        for scenario in story.scenarios:
            names.extend(name for name in scenario.examples if name not in names and _IMPORTABLE.fullmatch(name))
    return names


def as_read(written: Optional[WrittenBlock], language: Optional[CodeLanguage], key: WrittenKey) -> Optional[WrittenBlock]:
    """The lines a node was read with, while it is still in this language with the same key; otherwise None."""
    return written if written is not None and written.is_in(language, key) else None


def story_description(story: Story, prefix: str) -> List[str]:
    """The story's actor and, when it is not a user story, its kind, as the lines of its comment; the outline
    notations name a kind the same way, only when it is not user."""
    lines: List[str] = []
    actor = (story.actors[0] if story.actors else "").strip()
    if actor:
        lines.append(f"{prefix}Actor: {actor}")
    if story.story_type is not StoryType.USER:
        lines.append(f"{prefix}Kind: {StoryType(story.story_type).value}")
    return lines


def background_examples_line(story: Story, prefix: str) -> List[str]:
    """The examples the story's background holds, as the one comment line a story file carries them on; none when it
    holds none."""
    if not story.backgrounds or not story.backgrounds[0].examples:
        return []
    payload = {name: example.cells() for name, example in story.backgrounds[0].examples.items()}
    return [f"{prefix}background-examples: {json.dumps(payload, ensure_ascii=False)}"]


def scenario_examples_lines(scenario: Scenario) -> List[str]:
    """The examples of scenario as the comment lines a story file carries them on: their names, then, when a row
    holds values or the scenario is an outline, each row by its name, marked as an outline's rows or a scenario's.
    None for a scenario with no examples."""
    if not scenario.examples:
        return []
    rows = {name: example.cells() for name, example in scenario.examples.items()}
    names = ["examples: " + ", ".join(scenario.examples)]
    if not scenario.is_outline and not any(rows.values()):
        return names
    kind = OUTLINE_EXAMPLES if scenario.is_outline else SCENARIO_EXAMPLES
    return [*names, f"{kind}: {json.dumps(rows, ensure_ascii=False)}"]


def own_backgrounds(scenario: Scenario) -> List[Background]:
    """The backgrounds scenario holds that its story does not already write once for all its scenarios: those with
    steps the story's own backgrounds do not hold."""
    shared = [_step_texts(background) for background in getattr(scenario.parent, "backgrounds", [])]
    return [background for background in scenario.backgrounds if background.steps and _step_texts(background) not in shared]


def _step_texts(background: Background) -> List[tuple]:
    return [(step.keyword.lower(), step.text) for step in background.steps]


class StoryWriting:
    """How one language writes stories: the generic render, and the spelling the language gives as data."""

    file_name_template = "{snake}"
    """A sub-epic's story file name, from the sub-epic's `snake` or `pascal` name."""
    scenario_indent = "  "
    scenario_gap = [""]
    """The blank lines between two generic scenarios; Python writes them back to back."""
    statement_end = ""
    quote_mark = "'"
    """The quote a story, scenario, or step name is written in."""
    story_closing: List[str] = []
    no_scenarios: List[str] = []
    """What a story with no scenario holds."""
    empty_block: List[str] = []
    """What a scenario with nothing in it needs to stay valid code."""
    placeholder = ""
    """The body of a step not written yet."""
    scenario_opening = "{indent}{name}"
    scenario_closing = ""
    step_opening = "{indent}{verb}({text})"
    step_closing = ""
    and_opening = "{indent}{verb}({text})"
    and_closing = ""
    and_verbs = ("and", "but")
    """The verb an And step and a But step are chained with."""
    and_body_depth = 1
    """How many indents deeper than its step an And step's body sits."""
    chains_repeated_phase = False
    """Whether a step repeating the previous step's phase is chained onto it rather than opening a new clause."""
    verbs: Dict[str, str] = {}
    """The verb a step opens with, by its keyword; a keyword not listed opens with default_verb, else itself."""
    default_verb = ""

    def __init__(self, language: Optional[CodeLanguage]) -> None:
        self.language = language

    heading_template: List[str] = []
    """The lines that open a new story file, from the sub-epic's `name` and its `orders`."""

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        """The lines that open a new story file; a language whose file imports its helpers adds them."""
        return [self._filled(line, name=epic.name, orders=epic.order_path()) for line in self.heading_template]

    def story_file(self, epic: Epic, parent: str, written: Optional[WrittenBlock]) -> Tuple[str, str]:
        """The path and text of the story file holding a sub-epic's stories, written under the folder parent: back to
        the path it was read from with the code above and below its stories as read, else named for the sub-epic and
        opened with the file header. Each story renders itself."""
        if written is not None:
            path, lines = written.path, list(written.inside)
        else:
            path = f"{parent}/{self._filled(self.file_name_template, snake=epic.snake(), pascal=epic.pascal())}"
            lines = self.file_header(epic, parent)
        opened = len(lines)
        for story in epic.stories:
            gap = [] if len(lines) == opened else [""]
            lines = (lines if self._is_as_read(story) else self._spaced(lines, gap)) + self.story_lines(story)
        return path, "\n".join(lines + (written.closing if written is not None else [""]))

    def story_text(self, story: "Story") -> str:
        return "\n".join(self.story_lines(story) + [""])

    def story_lines(self, story: "Story") -> List[str]:
        """Read in this language and unchanged: every line as read. Each scenario decides for itself."""
        written = as_read(story.written, self.language, story.code_key)
        lines = written.lead + written.heading + written.inside if written is not None else self._story_head(story)
        lines = self._scenarios_after(lines, story)
        if written is not None:
            return lines + written.closing + written.close
        return lines + ([] if story.scenarios else list(self.no_scenarios)) + list(self.story_closing)

    def story_open(self, story: "Story") -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell story_open")

    def story_background_lines(self, background: "Background") -> List[str]:
        return []

    def scenario_background_lines(self, background: "Background", indent: str) -> List[str]:
        return []

    def _quoted(self, text: str) -> str:
        """text as a quoted name in this language, its backslashes and quotes escaped."""
        mark = self.quote_mark
        return mark + re.sub(r"[\\" + mark + "]", lambda found: "\\" + found.group(0), text) + mark

    def _clauses(self, steps: List["Step"]) -> List[StepClause]:
        """(step, the verb it opens with, steps chained onto it)."""
        clauses: List[StepClause] = []
        for step in steps:
            if self.chains_repeated_phase and clauses and step.step_type == clauses[-1].step.step_type:
                clauses[-1].continuations.append(step)
            else:
                clauses.append(StepClause(step, self._verb(step)))
        return clauses

    def _verb(self, step: "Step") -> str:
        return self.verbs.get(step.keyword) or self.default_verb or step.keyword.lower()

    def _step_lines(self, clause: StepClause, indent: str) -> List[str]:
        """One step and the steps chained onto it, each with its body. A body not written yet gets the placeholder."""
        step = clause.step
        lines = [self._step_open(clause.verb, step, indent)] + self._body_lines(step, indent + self.language.indent)
        lines.extend(self._closing(self.step_closing, indent))
        for extra in [*step.ands, *clause.continuations]:
            lines.append(self._and_open(extra, indent))
            lines.extend(self._body_lines(extra, indent + self.language.indent * self.and_body_depth))
            lines.extend(self._closing(self.and_closing, indent))
        lines[-1] += self.statement_end
        return lines

    def _is_as_read(self, node: "Story | Scenario") -> bool:
        return as_read(node.written, self.language, node.code_key) is not None

    def _spaced(self, lines: List[str], gap: List[str]) -> List[str]:
        """lines with the language's gap after them, for a child written anew: none when they are empty, the child
        being the first thing inside its parent, or already end in a blank line. A child written as read brings the
        blank lines above it itself."""
        return lines if not lines or not lines[-1].strip() else lines + gap

    def _story_head(self, story: "Story") -> List[str]:
        lines = self.story_open(story) + story.setup.lines_in(self.language, self.language.indent, "")
        for background in story.backgrounds:
            lines.extend(self.story_background_lines(background))
        return lines

    def _scenarios_after(self, lines: List[str], story: Story) -> List[str]:
        opened = len(lines)
        for scenario in story.scenarios:
            gap = [] if len(lines) == opened else self.scenario_gap
            lines = (lines if self._is_as_read(scenario) else self._spaced(lines, gap)) + self._scenario_lines(scenario, self.scenario_indent)
        return lines

    def _scenario_lines(self, scenario: "Scenario", indent: str) -> List[str]:
        """Read in this language and unchanged: every line as read. Otherwise the generic spelling, bodies kept."""
        written = as_read(scenario.written, self.language, scenario.code_key)
        if written is not None:
            return written.lead + written.heading + written.inside + written.closing + written.close
        inner = indent + self.language.indent
        lines = [self._filled(self.scenario_opening, indent=indent, name=self._quoted(scenario.name))]
        lines += scenario.setup.lines_in(self.language, inner, "")
        for background in own_backgrounds(scenario):
            lines.extend(self.scenario_background_lines(background, inner))
        lines.extend(f"{inner}{self.language.comment(line)}" for line in scenario_examples_lines(scenario))
        for clause in self._clauses(scenario.steps):
            lines.extend(self._step_lines(clause, inner))
        if not scenario.steps and scenario.setup.is_empty:
            lines.extend(f"{inner}{line}" for line in self.empty_block)
        return lines + self._closing(self.scenario_closing, indent)

    def _step_open(self, verb: str, step: "Step", indent: str) -> str:
        return self._filled(self.step_opening, indent=indent, verb=verb, text=self._quoted(step.text), callback=self._callback(step))

    def _and_open(self, step: "Step", indent: str) -> str:
        verb = self.and_verbs[1] if step.keyword == "But" else self.and_verbs[0]
        return self._filled(self.and_opening, indent=indent, verb=verb, text=self._quoted(step.text), callback=self._callback(step))

    def _callback(self, step: "Step") -> str:
        """The opening of a step's callback in a language that writes one; async when its body awaits."""
        return "async () => {" if step.body.mentions("await") else "() => {"

    def _closing(self, template: str, indent: str) -> List[str]:
        return [self._filled(template, indent=indent)] if template else []

    def _filled(self, template: str, **values) -> str:
        """One of this language's templates with its values in place."""
        return template.format(**values)

    def _body_lines(self, step: "Step", indent: str) -> List[str]:
        """The step's body; an empty one carries the realization call graph as comments above the placeholder."""
        scaffold: List[str] = []
        if step.body.is_empty and step.call_graph:
            graph = textwrap.dedent(step.call_graph.block()).splitlines()
            scaffold = [f"{indent}{self.language.comment(line)}" for line in graph]
        return scaffold + step.body.lines_in(self.language, indent, self.placeholder)
