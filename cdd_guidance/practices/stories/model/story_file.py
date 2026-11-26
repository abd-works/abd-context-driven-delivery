"""A story file in code, read once into its stories and the file's own code around them. Each language's model picks the
kind of file once (`CodeStoryMap.story_file`): a file whose blocks it reads (*BlockStoryFile*: a story, background,
scenario, and step each written as a *StoryBlock*), a screen spec, a shared story file, or, for a language that reads no
blocks, the text alone. A story made from a block reads its code from that block (`CodeStory.from_block`), so no story
is matched to a block by its name.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from cdd_guidance.practices.source_code import CallGraph, CodeBody, CodeLanguage, InsideLines, WrittenBlock
from cdd_guidance.practices.stories.model.story_map_files import source_at

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.code_story_map import CodeStoryMap
    from cdd_guidance.practices.stories.model.story_map import Background, Scenario, Story


# A statement a realization writes at the top of a step: a call, its value named first when what it returns matters next
# (``line = cart.addLine(plan)``, ``cart = new Cart(customerProfile)``).
_STATEMENT = re.compile(r"^(?:[A-Za-z_$][\w$]*\s*=\s*)?(?:new\s+)?[A-Za-z_$][\w$.]*\s*\(.*\)\s*;?$")


def _realization_statement(text: str) -> bool:
    """Whether a comment line is a statement or a comment of a realization, not a sentence about the step."""
    return text.startswith("//") or _STATEMENT.match(text.strip()) is not None


def _is_realization(graph: CallGraph) -> bool:
    """Whether the comments a step opens with are its realization: an arrow among them, or every line a statement."""
    calls = [entry for entry in graph if entry.kind == "call"]
    if any(entry.kind in ("out", "in") for entry in graph):
        return True
    return bool(calls) and all(_STATEMENT.match(entry.text) for entry in calls)


class StoryBlock(ABC):
    """One block of a story file as its language finds it: a story, background, scenario, or step call. A node reads
    its own code from its block whichever language it was written in."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name its call gives, such as a story's or a scenario's."""

    @property
    @abstractmethod
    def line_span(self) -> Tuple[int, int]:
        """Its first and last line, counted from 0."""

    @property
    @abstractmethod
    def opening_line(self) -> int:
        """The line, counted from 0, its call is written on."""

    @property
    @abstractmethod
    def is_chained(self) -> bool:
        """Whether it is a step chained onto the one before it, not a statement of its own."""

    @property
    @abstractmethod
    def inside_lines(self) -> List[str]:
        """The lines inside it."""

    @property
    @abstractmethod
    def body(self) -> CodeBody:
        """The code inside it, as a step holds it."""

    @property
    @abstractmethod
    def language(self) -> CodeLanguage:
        """The language its file is written in."""

    def realization(self) -> CallGraph:
        """The call graph a step block opens with as comments, as a story file writes a step's realization: the
        statements of the flow, each a call such as ``cart = new Cart(customerProfile)`` or ``CartRepository.update(cart)``
        or a ``//`` comment naming the Given they set up, with the calls a statement makes indented under it
        (``-> Book.reserve(1)``). Empty when it opens with none, such as a block holding only a comment that says the
        step is not written yet."""
        sign = self.language.line_comment
        lines = [line.strip() for line in self.body_text.splitlines() if line.strip()]
        written: List[str] = []
        for line in lines:
            text = line[len(sign):].removeprefix(" ") if line.startswith(sign) else None
            if text is None or not text.strip():
                break
            if written and not text.startswith(" ") and not _realization_statement(text):
                break
            written.append(text)
        graph = CallGraph().read("\n".join(written))
        return graph if _is_realization(graph) else CallGraph()


    @property
    @abstractmethod
    def body_text(self) -> str:
        """The code inside it, as written."""

    @property
    @abstractmethod
    def text(self) -> str:
        """The whole block, as written."""

    @abstractmethod
    def written(self, lead: List[str]) -> WrittenBlock:
        """Its lines as read, the lead above it included, to write back."""

    @abstractmethod
    def split_inside(self, children: Sequence["StoryBlock"]) -> Tuple[List[str], List[List[str]], List[str]]:
        """Its inside lines around children: those before the first, those leading each, and those after the last."""

    @abstractmethod
    def scenarios(self) -> List["StoryBlock"]:
        """The scenario blocks inside it."""

    @abstractmethod
    def backgrounds(self, scenarios: Sequence["StoryBlock"]) -> List["StoryBlock"]:
        """The background blocks inside it, before scenarios."""

    @abstractmethod
    def steps(self, skip: Sequence["StoryBlock"]) -> List["StoryBlock"]:
        """The step blocks inside it, leaving out those inside skip."""

    @abstractmethod
    def setup(self, children: Sequence["StoryBlock"]) -> CodeBody:
        """The lines inside it no child holds: the code its scenarios share."""


def flat_steps(steps: Sequence) -> List:
    """Every step with its ands after it, in the order the file has them."""
    return [line for step in steps for line in (step, *step.ands)]


def read_step_code(owner: "Scenario | Background", blocks: Sequence[StoryBlock]) -> None:
    """Each of owner's steps, ands included, reads the step block in the same place in the file."""
    for step, block in zip(flat_steps(owner.steps), blocks):
        step.read_code(block)


class StoryFile:
    """One story file in code, read once: its stories, and the file's own code around them (``own_code``), none for a
    file whose code is not kept. This kind reads the stories from the text alone, as a language that reads no blocks
    does; the project is the folder the files it reads, such as an examples module, are found in."""

    def __init__(self, model: CodeStoryMap, path: str, content: str, project: Optional[Path] = None) -> None:
        self.model = model
        self.path = path
        self.text = content
        self.lines = content.split("\n")
        self.project = project

    def story_blocks(self) -> Optional[List[StoryBlock]]:
        """Each story block in the file, in order; None, since this kind reads no block."""
        return None

    @property
    def stories(self) -> List["Story"]:
        return self._read[0]

    @property
    def own_code(self) -> Optional[WrittenBlock]:
        return self._read[1]

    @cached_property
    def _read(self) -> Tuple[List["Story"], Optional[WrittenBlock]]:
        return self.read_text(), None

    def read_text(self) -> List["Story"]:
        """The stories the text writes, read without its blocks: the named fallback for a file whose blocks cannot be
        read, such as a Python story test with a syntax error."""
        return self.model.story_class.load_all(self.text)


class BlockStoryFile(StoryFile, ABC):
    """A story file whose language finds its blocks: each story is made from the block written for it and placed on its
    lines, and the file's own code above, between, and below them is kept to write back."""

    @property
    def language(self) -> CodeLanguage:
        return self.model.language

    @abstractmethod
    def story_blocks(self) -> Optional[List[StoryBlock]]:
        """Each story block in the file, in order; None when the file cannot be read."""

    @cached_property
    def _read(self) -> Tuple[List["Story"], Optional[WrittenBlock]]:
        blocks = self.story_blocks()
        if blocks is None:
            return self.read_text(), None
        written, leads = self._written_around(blocks)
        if not blocks:
            return self.read_text(), written
        story_class = self.model.story_class
        imports = story_class.syntax.example_imports(self.text)
        stories = []
        for block, lead in zip(blocks, leads):
            story = story_class.from_block(block, lead, "\n".join([imports, self.comment_above(block), block.text]))
            story.source = source_at(self.path, block.line_span[0] + 1, block.line_span[1] + 1)
            stories.append(story)
        return stories, written

    def _written_around(self, blocks: List[StoryBlock]) -> Tuple[WrittenBlock, List[List[str]]]:
        """The file's own code above, between, and below blocks, kept to write back to its path, and the lines that lead
        each block."""
        written = WrittenBlock(self.language, None, [])
        written.path = self.path
        written.inside, leads, written.closing = InsideLines(self.lines, (0, len(self.lines))).split(
            [block.line_span for block in blocks]
        )
        return written, leads

    def comment_above(self, block: StoryBlock) -> str:
        """The comment lines right above block, which describe the story it holds, up to the code before them."""
        start = index = block.line_span[0]
        while index > 0 and self._describes(self.lines[index - 1]):
            index -= 1
        return "\n".join(self.lines[index:start])

    def _describes(self, line: str) -> bool:
        """Whether a line can be part of the comment above a block: a blank line or a comment line in any language."""
        return not line.strip() or line.strip().startswith(("/*", "*", "//", "#"))
