"""How the markdown story formats mark up text and steps: names without their links, backticks, and emphasis, and a
step as the `*Given* a cart` line it is read from and written as."""

from __future__ import annotations

import re
from typing import Dict, List, NamedTuple, Optional

from cdd_guidance.practices.stories.model.markdown.links import unlink
from cdd_guidance.practices.stories.model.story_map import Example, Step

_BOLD_TERM = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_VALUE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
# An underlined term written as a link, ++[cart](domain-model.md#cart-…)++: the label is the term the step names.
_LINKED_TERM = re.compile(r"\+\+\[([^\]\n]+)\]\([^)\n]*\)\+\+")
_STEP_CONTINUATION = re.compile(r"^(And|But)\s+", re.IGNORECASE)
TABLE_LINE = re.compile(r"^\s*\|(.+)\|\s*$")
# A step line as markdown writes one: `*Given* a cart`.
STEP_LINE = re.compile(r"^\s*\*(Given|When|Then|And|But)\*\s")


def strip_backticks(text: str) -> str:
    """The text without the backticks wrapped around it."""
    s = text.strip()
    while s.startswith("`") and s.endswith("`") and len(s) >= 2:
        s = s[1:-1].strip()
    return s


def strip_markup(text: str) -> str:
    """The text without its links, backticks, and the emphasis wrapped around it."""
    s = strip_backticks(unlink(text))
    while s.startswith("*") and s.endswith("*") and len(s) >= 2:
        s = strip_backticks(s[1:-1].strip())
    return strip_backticks(s)


class ExampleRowLine(NamedTuple):
    """The line an example row was read from, as written, and the headers of the table it sits in."""

    line: str
    headers: List[str]

    def written(self, cells: Dict[str, str], read: Dict[str, str]) -> str:
        """The line with each cell whose value differs from read written as cells says it, every other cell, the
        indent and the line ending as read."""
        found = TABLE_LINE.match(self.line)
        read_cells = [cell.strip() for cell in found.group(1).split("|")] if found else []
        kept = [index < len(read_cells) and cells.get(header, "") == read.get(header, "") for index, header in enumerate(self.headers)]
        written = [read_cells[index] if kept[index] else cells.get(header, "").replace("|", "/") for index, header in enumerate(self.headers)]
        body = self.line.rstrip("\r\n")
        indent = body[: len(body) - len(body.lstrip())]
        return f"{indent}| {' | '.join(written)} |{self.line[len(body):]}"


class MarkdownExample(Example):
    """An example read from a row of a markdown examples table. It keeps the row's line and its table's headers, so an
    unchanged example is written back as read, an edited one changes only the cells the edit changed, and one taken off
    its scope writes no line."""

    def __init__(self, name: str, fields: "Dict[str, str] | str", read: ExampleRowLine) -> None:
        super().__init__(name, fields)
        self.read = read
        self.read_row: Dict[str, str] = dict(self.row)

    def line(self) -> str:
        """Its row as it stands now: the line it was read from while no cell under its headers changed, the line with
        the changed cells written anew otherwise, and nothing once it has left its scope."""
        if self.parent is None:
            return ""
        row = self.row
        if all(row.get(header, "") == self.read_row.get(header, "") for header in self.read.headers):
            return self.read.line
        return self.read.written(row, self.read_row)

    def clone(self) -> "MarkdownExample":
        """A copy that still writes the row it was read from."""
        copied = type(self)(self.name, dict(self.value) if isinstance(self.value, dict) else self.value, self.read)
        copied.sequential_order, copied.scope, copied.read_row = self.sequential_order, self.scope, dict(self.read_row)
        return copied


class MarkdownStep(Step):
    """Step whose text may still carry a markdown And or But prefix."""

    markdown_line: Optional[tuple] = None
    """The keyword, text, and line the step was read with, so an unchanged step is written back as read; None for a
    step read from no line."""

    def read_from(self, line: str) -> None:
        """Keep line as the one this step was read from, with the keyword and text it says now, and take the concepts,
        values and actor its markup names: its bold terms are the concepts, the first its actor, and its italic values
        the values. The step's text keeps its words without their links, so the underlined terms the line links are
        kept as its linked terms."""
        self.markdown_line = (self.keyword, self.text, line)
        self.linked_terms = [term.strip() for term in _LINKED_TERM.findall(line)]
        actor = _BOLD_TERM.search(self.text)
        self.concepts = _BOLD_TERM.findall(self.text)
        self.values = [value.strip("`").strip() for value in _ITALIC_VALUE.findall(self.text) if value]
        self.actor = actor.group(1).strip() if actor else ""

    def line_as_read(self) -> Optional[str]:
        """The line this step was read from, while its keyword and text are unchanged; otherwise None."""
        if self.markdown_line is None or self.markdown_line[:2] != (self.keyword, self.text):
            return None
        return self.markdown_line[2]

    def display_text(self) -> str:
        """Step text without a leading And or But. The keyword already says which."""
        return _STEP_CONTINUATION.sub("", self.text).strip()



def step_prose(step: Step) -> str:
    """A step's text as markdown writes it after its keyword: without a leading And or But on a markdown step."""
    return step.display_text() if isinstance(step, MarkdownStep) else step.text


def step_line(step: Step) -> str:
    """One step as markdown writes it: `*Given* a cart`."""
    return f"*{step.keyword}* {step_prose(step)}"


def step_lines(step: Step) -> List[str]:
    """A step and the steps chained onto it as markdown lines, with its realization fence when it has a call graph."""
    lines = [step_line(step)] + [step_line(extra) for extra in step.ands]
    if getattr(step, "call_graph", None):
        lines.extend(["", "```realization", step.call_graph.block(), "```"])
    return lines


# How the scenarios template ends a step line that another step line follows: two spaces, a markdown line break.
_LINE_BREAK = "  "
# How the scenarios template indents an And or But under the step it continues.
_CONTINUATION_INDENT = "  "


def step_block_lines(steps: List[Step]) -> List[str]:
    """Steps as the scenarios template writes them: each step, the And and But lines chained onto it indented under
    it, its realization fence after them, and every step line that another step line follows ending in a line break."""
    lines: List[str] = []
    for step in steps:
        lines.append(step_line(step))
        lines.extend(_CONTINUATION_INDENT + step_line(extra) for extra in step.ands)
        if getattr(step, "call_graph", None):
            lines.extend(["", "```realization", step.call_graph.block(), "```", ""])
    return [line + _LINE_BREAK if STEP_LINE.match(line) and index + 1 < len(lines) and STEP_LINE.match(lines[index + 1]) else line for index, line in enumerate(lines)]

