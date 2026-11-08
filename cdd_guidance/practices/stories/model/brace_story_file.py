"""A brace-language story file as its blocks: stories, backgrounds, scenarios, and step calls.

TypeScript and JavaScript story files share one shape - `story(...)`, `scenario(...)`, `background(...)`, and
`given(...)` calls whose callbacks hold code - so one file finds the blocks each story node reads its code from.
"""

from __future__ import annotations

import re
from typing import List, Sequence, Tuple

from cdd_guidance.practices.clean_engineering.model.code_body import BraceCall, CodeBody, WrittenBlock
from cdd_guidance.practices.stories.model.code_story_model import unescaped
from cdd_guidance.practices.stories.model.story_file import CodeBlock, StoryFile

_QUOTED = r"(['\"`])((?:\\.|(?!\1).)*)\1"
_STORY = re.compile(r"(?m)^[ \t]*(?:shareStory|story)\s*\(\s*" + _QUOTED)
_SCENARIO = re.compile(r"(?<![.\w])scenario\s*\(\s*" + _QUOTED)
_BACKGROUND = re.compile(r"(?<![.\w])background\s*\(")
_STEP = re.compile(r"(?<![.\w])(given|when|then|and|but)\s*\(\s*(['\"`])((?:\\.|(?!\2).)*)\2")
_CHAINED = re.compile(r"\s*\.(and|but)\s*\(\s*(['\"`])((?:\\.|(?!\2).)*)\2")


class BraceStoryFile(StoryFile):
    """One brace-language story file: its story calls, and the calls inside each."""

    def story_blocks(self) -> List[CodeBlock]:
        return self.calls(_STORY, 0, len(self.text), group=2)

    def calls(self, pattern: re.Pattern, begin: int, end: int, group: int = 0) -> List["BraceBlock"]:
        """The calls matching pattern between begin and end that are not inside another one found first."""
        found: List[BraceBlock] = []
        for match in pattern.finditer(self.text, begin, end):
            if found and match.start() < found[-1].call.end:
                continue
            name = unescaped(match.group(group)) if group else ""
            call = BraceCall(self.text, match.start(), self.text.index("(", match.start()), name)
            if call.is_whole:
                found.append(BraceBlock(self, call))
        return found

    def step_calls(self, begin: int, end: int, skip: Sequence["BraceBlock"]) -> List["BraceBlock"]:
        """Each step call between begin and end, outside skip: a given/when/then call, then each .and/.but chained
        onto it."""
        taken = [(block.call.start, block.call.end) for block in skip]
        found: List[BraceBlock] = []
        for match in _STEP.finditer(self.text, begin, end):
            if any(start <= match.start() < stop for start, stop in taken):
                continue
            link = self._call_at(match.start(), match.group(3))
            chain = [link]
            while link.close is not None:
                chained = _CHAINED.match(self.text, link.close + 1)
                if chained is None:
                    break
                link = self._call_at(chained.start(), chained.group(3))
                chain.append(link)
            found.extend(BraceBlock(self, call) for call in chain)
            taken.append((chain[0].start, chain[-1].end))
        return found

    def line(self, index: int) -> int:
        """The line, counted from 0, that the character at index sits on."""
        return self.text.count("\n", 0, index)

    def _call_at(self, start: int, name: str) -> BraceCall:
        return BraceCall(self.text, start, self.text.index("(", start), unescaped(name))


class BraceBlock(CodeBlock):
    """One call in a brace-language story file whose callback holds code."""

    def __init__(self, file: BraceStoryFile, call: BraceCall) -> None:
        self.file = file
        self.call = call

    @property
    def name(self) -> str:
        return self.call.name

    @property
    def line_span(self) -> Tuple[int, int]:
        return self.file.line(self.call.start), self.file.line(self.call.end - 1)

    @property
    def inside_lines(self) -> List[str]:
        return self.file.lines[slice(*self._inside)]

    @property
    def body(self) -> CodeBody:
        return CodeBody(self.call.body, self.file.language)

    def written(self, lead: List[str]) -> WrittenBlock:
        start, brace, inner_end, end = (self.file.line(index) for index in (self.call.start, self.call.brace, self.call.inner_end, self.call.end - 1))
        written = WrittenBlock(self.file.language, None, lead, self.file.lines[start : brace + 1])
        written.close = self.file.lines[inner_end : end + 1]
        return written

    def split_inside(self, children: Sequence[CodeBlock]) -> Tuple[List[str], List[List[str]], List[str]]:
        return WrittenBlock.split_inside(self.file.lines, self._inside, [child.line_span for child in children])

    def scenarios(self) -> List[CodeBlock]:
        return self.file.calls(_SCENARIO, self.call.brace + 1, self.call.inner_end, group=2)

    def backgrounds(self, scenarios: Sequence[CodeBlock]) -> List[CodeBlock]:
        first = scenarios[0].call.start if scenarios else self.call.inner_end
        return self.file.calls(_BACKGROUND, self.call.brace + 1, first)

    def steps(self, skip: Sequence[CodeBlock]) -> List[CodeBlock]:
        return self.file.step_calls(self.call.brace + 1, self.call.inner_end, skip)

    def setup(self, children: Sequence[CodeBlock]) -> CodeBody:
        first, last = self._inside
        covered = {line for child in children for line in range(child.line_span[0], child.line_span[1] + 1)}
        kept = [self.file.lines[index] for index in range(first, last) if index not in covered]
        return CodeBody(re.sub(r"\n\s*\n(\s*\n)+", "\n\n", "\n".join(kept)), self.file.language)

    @property
    def _inside(self) -> Tuple[int, int]:
        return self.file.line(self.call.brace) + 1, self.file.line(self.call.inner_end)
