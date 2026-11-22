"""The lines of a read scenarios document, each a *ReadLine* that writes itself back as the model now stands: a line
kept as written, a heading, the step lines of one owner, an example row, or the lines of a node held in place (a
scenario in its story, a story in its document). So an unchanged document is written back byte for byte, and a
heading, step, or example changed on the model is written anew where it was read."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

from cdd_guidance.practices.stories.model.markdown.markup import MarkdownExample, MarkdownStep, step_line

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_model import Background, Scenario, Step


class ReadLine(ABC):
    """One line, or one held node's lines, of a read scenarios document."""

    @abstractmethod
    def written(self, steps: SectionSteps) -> str:
        """The line as the model now stands; steps writes the step lines of the section it is in."""


class KeptLine(ReadLine):
    """A line kept as written: a blank line, a heading the model does not hold, a paragraph, a fenced realization."""

    def __init__(self, text: str) -> None:
        self.text = text

    def written(self, steps: SectionSteps) -> str:
        return self.text


class HeadingLine(ReadLine):
    """The heading of a node: what it said when read (said) and the line as written (text). The node writes it back as
    read while it says the same, and anew once it changed. A story's heading names its node once the story is made."""

    def __init__(self, node: Any, said: Any, text: str) -> None:
        self.node = node
        self.said = said
        self.text = text

    def written(self, steps: SectionSteps) -> str:
        return self.node.heading_written(self)


class StepLines(ReadLine):
    """Where one step line of owner, a scenario or a background, was read."""

    def __init__(self, owner: "Scenario | Background") -> None:
        self.owner = owner

    def written(self, steps: SectionSteps) -> str:
        return steps.write(self.owner)


class ExampleLine(ReadLine):
    """Where an example's row was read, written as the example now says it."""

    def __init__(self, example: MarkdownExample) -> None:
        self.example = example

    def written(self, steps: SectionSteps) -> str:
        return self.example.line()


class HeldLines(ReadLine):
    """The lines of a node read in place: a scenario under its story, or a story in its document, written as the node
    now stands while what holds it still holds it, and not at all once it was taken off."""

    def __init__(self, node: Any) -> None:
        self.node = node

    def written(self, steps: SectionSteps) -> str:
        return self.node.document_text() if steps.holds(self.node) else ""


class SectionSteps:
    """Writes the step lines of one section. Each step line stands where its step was read; a step unchanged on the
    model keeps its line, and steps added on the model follow the owner's last line, which writes every step still
    pending. It knows the nodes the section still holds."""

    def __init__(self, lines: Sequence[ReadLine], held: Sequence[Any] = ()) -> None:
        self._held = list(held)
        self._pending: Dict[int, list] = {}
        self._left: Dict[int, int] = {}
        for line in lines:
            if isinstance(line, StepLines):
                self._left[id(line.owner)] = self._left.get(id(line.owner), 0) + 1

    def holds(self, node: Any) -> bool:
        return any(held is node for held in self._held)

    def write(self, owner: "Scenario | Background") -> str:
        pending = self._pending.setdefault(id(owner), self._steps_of(owner))
        self._left[id(owner)] -= 1
        if self._left[id(owner)] > 0:
            return self._line(*pending.pop(0)) if pending else ""
        written = "".join(self._line(*entry) for entry in pending)
        pending.clear()
        return written

    def _steps_of(self, owner: "Scenario | Background") -> list:
        """Each step of owner and each step chained onto it, marked as a continuation, in the order they are written."""
        pending = []
        for step in owner.steps:
            pending.append((step, False))
            pending.extend((extra, True) for extra in step.ands)
        return pending

    def _line(self, step: "Step", continuation: bool) -> str:
        as_read = step.line_as_read() if isinstance(step, MarkdownStep) else None
        if as_read is not None:
            return as_read
        indent = "  " if continuation else ""
        return f"{indent}{step_line(step)}  \n"


def written_lines(lines: Sequence[ReadLine], held: Sequence[Any] = ()) -> str:
    """Every line of one section as the model now stands, the nodes it still holds among held."""
    steps = SectionSteps(lines, held)
    return "".join(line.written(steps) for line in lines)


class ReadScenarioDocument:
    """A scenarios document as it was read: its lines, the epic or sub-epic its stories are on (holder), and the
    heading that names that epic (tree), none when the document has none. It writes itself as it reads now: each line
    as it was read, each story it still holds as it now stands, and the stories added since after them."""

    def __init__(self, lines: List[ReadLine], holder: Any, tree: Optional[HeadingLine], story_class: type) -> None:
        self.lines = lines
        self.holder = holder
        self.tree = tree
        self._story_class = story_class

    def text(self) -> str:
        out = [written_lines(self.lines, self.holder.stories)]
        held = [line.node for line in self.lines if isinstance(line, HeldLines)]
        added = [story for story in self.holder.stories if not any(story is node for node in held)]
        out.extend((story if isinstance(story, self._story_class) else self._story_class.copy_of(story)).document_text() for story in added)
        return "".join(out)
