"""How the markdown story formats mark up text and steps: names without their links, backticks, and emphasis, and a
step as the `*Given* a cart` line it is read from and written as."""

from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.stories.model.markdown.links import unlink
from cdd_guidance.practices.stories.model.story_model import Step

_BOLD_TERM = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_VALUE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_STEP_CONTINUATION = re.compile(r"^(And|But)\s+", re.IGNORECASE)


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


class MarkdownStep(Step):
    """Step whose text may still carry a markdown And or But prefix."""

    def __init__(self, *args, read_line: Optional[str] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # The keyword, text, and line the step was read with, so an unchanged step is written back as read.
        self.markdown_line: Optional[tuple] = (self.keyword, self.text, read_line) if read_line is not None else None

    def line_as_read(self) -> Optional[str]:
        """The line this step was read from, while its keyword and text are unchanged; otherwise None."""
        if self.markdown_line is None or self.markdown_line[:2] != (self.keyword, self.text):
            return None
        return self.markdown_line[2]

    def display_text(self) -> str:
        """Step text without a leading And or But. The keyword already says which."""
        return _STEP_CONTINUATION.sub("", self.text).strip()



def step_marks(text: str) -> dict:
    """What a step line's markup names: its bold terms are the concepts, the first its actor, and its italic values the
    values."""
    actor = _BOLD_TERM.search(text)
    return {
        "concepts": _BOLD_TERM.findall(text),
        "values": [value.strip("`").strip() for value in _ITALIC_VALUE.findall(text) if value],
        "actor": actor.group(1).strip() if actor else "",
    }


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
