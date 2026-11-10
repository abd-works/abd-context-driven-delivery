"""Reads a brace-language story file's blocks as written: stories, backgrounds, scenarios, and step calls.

TypeScript and JavaScript story files share one shape - `story(...)`, `scenario(...)`, `background(...)`, and
`given(...)` calls whose callbacks hold code - so one reader gives each story node the code it was read with.
"""

from __future__ import annotations

import re
from typing import Callable, List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage, WrittenBlock
from cdd_guidance.practices.stories.model.code_story_model import flat_steps
from cdd_guidance.practices.stories.model.story_reader import StoryReader
from cdd_guidance.practices.stories.model.story_model import Background, Scenario, Step, Story

_QUOTED = r"(['\"`])((?:\\.|(?!\1).)*)\1"
_STORY = re.compile(r"(?m)^[ \t]*(?:shareStory|story)\s*\(\s*" + _QUOTED)
_SCENARIO = re.compile(r"(?<![.\w])scenario\s*\(\s*" + _QUOTED)
_BACKGROUND = re.compile(r"(?<![.\w])background\s*\(")
_STEP = re.compile(r"(?<![.\w])(given|when|then|and|but)\s*\(\s*(['\"`])((?:\\.|(?!\2).)*)\2")
_CHAINED = re.compile(r"\s*\.(and|but)\s*\(\s*(['\"`])((?:\\.|(?!\2).)*)\2")


class BraceCall:
    """One call whose last argument is a callback: where it starts, its callback braces, and where it ends."""

    def __init__(self, text: str, start: int, open_paren: int, name: str) -> None:
        self.start = start
        self.name = name
        self.close = self._matching(text, open_paren, "(", ")")
        arrow = text.find("=>", open_paren, self.close if self.close is not None else len(text))
        self.brace = text.find("{", arrow if arrow >= 0 else open_paren, self.close if self.close is not None else len(text))
        self.inner_end = self._matching(text, self.brace, "{", "}") if self.brace >= 0 else None
        end = (self.close + 1) if self.close is not None else start
        self.end = end + 1 if text.startswith(";", end) else end

    @property
    def is_whole(self) -> bool:
        return self.close is not None and self.brace >= 0 and self.inner_end is not None

    def body(self, text: str) -> str:
        return text[self.brace + 1 : self.inner_end] if self.is_whole else ""

    def _matching(self, text: str, open_index: int, opener: str, closer: str) -> Optional[int]:
        """The index of the bracket that closes the one at open_index; None when the text never closes it."""
        depth = 0
        for index in range(open_index, len(text)):
            if text[index] == opener:
                depth += 1
            elif text[index] == closer:
                depth -= 1
                if depth == 0:
                    return index
        return None


class BraceStoryReader(StoryReader[BraceCall]):
    """Reads one story file and gives each story, background, scenario, and step the code it was written with."""

    def __init__(self, language: CodeLanguage, content: str, unescape: Callable[[str], str]) -> None:
        super().__init__(language, content)
        self._text = content
        self._unescape = unescape

    def story_blocks(self) -> List[BraceCall]:
        return self._calls(_STORY, 0, len(self._text), group=2)

    def name_of(self, block: BraceCall) -> str:
        return block.name

    def line_span(self, block: BraceCall) -> Tuple[int, int]:
        return self._line(block.start), self._line(block.end - 1)

    def read_story(self, story: Story, call: BraceCall, lead: List[str]) -> None:
        scenarios = self._calls(_SCENARIO, call.brace + 1, call.inner_end, group=2)
        first = scenarios[0].start if scenarios else call.inner_end
        backgrounds = self._calls(_BACKGROUND, call.brace + 1, first)
        for background, block in zip(story.backgrounds, backgrounds):
            self._read_steps(background, block)
        written = self._written(call, lead)
        written.inside, leads, written.closing = WrittenBlock.split_inside(
            self._lines, self._inside(call), [self.line_span(scenario) for scenario in scenarios]
        )
        story.setup = self._setup(call, self._spans(backgrounds + scenarios))
        pending = list(story.scenarios)
        for block, scenario_lead in zip(scenarios, leads):
            scenario = self.take(pending, block.name)
            if scenario is not None:
                self._read_scenario(scenario, block, scenario_lead)
        written.key = story.code_key
        story.written = written

    def _spans(self, calls: List[BraceCall]) -> List[Tuple[int, int]]:
        return [(call.start, call.end) for call in calls]

    def _read_scenario(self, scenario: Scenario, call: BraceCall, lead: List[str]) -> None:
        backgrounds = self._calls(_BACKGROUND, call.brace + 1, call.inner_end)
        for background, block in zip(scenario.backgrounds, backgrounds):
            self._read_steps(background, block)
        chains = self._read_steps(scenario, call, skip=backgrounds)
        scenario.setup = self._setup(call, self._spans(backgrounds) + chains)
        written = self._written(call, lead)
        written.inside = self._lines[slice(*self._inside(call))]
        written.key = scenario.code_key
        scenario.written = written

    def _read_steps(self, owner: "Scenario | Background", call: BraceCall, skip: Optional[List[BraceCall]] = None) -> List[Tuple[int, int]]:
        """Each step call's body onto the owner's steps, in file order. A step whose text differs keeps no body."""
        chains = self._chains(call.brace + 1, call.inner_end, skip or [])
        calls = [link for chain in chains for link in chain]
        for step, link in zip(flat_steps(owner.steps), calls):
            if step.text == link.name:
                step.body = CodeBody(link.body(self._text), self._language)
        return [(chain[0].start, chain[-1].end) for chain in chains]

    def _chains(self, begin: int, end: int, skip: List[BraceCall]) -> List[List[BraceCall]]:
        """Each step statement: a given/when/then call and the .and/.but calls chained onto it."""
        taken = [(block.start, block.end) for block in skip]
        chains: List[List[BraceCall]] = []
        for match in _STEP.finditer(self._text, begin, end):
            if any(start <= match.start() < stop for start, stop in taken):
                continue
            chain = [BraceCall(self._text, match.start(), self._text.index("(", match.start()), self._unescape(match.group(3)))]
            while chain[-1].close is not None:
                chained = _CHAINED.match(self._text, chain[-1].close + 1)
                if chained is None:
                    break
                chain.append(BraceCall(self._text, chained.start(), self._text.index("(", chained.start()), self._unescape(chained.group(3))))
            chains.append(chain)
            taken.append((chain[0].start, chain[-1].end))
        return chains

    def _calls(self, pattern: re.Pattern, begin: int, end: int, group: int = 0) -> List[BraceCall]:
        """The calls matching pattern between begin and end that are not inside another one found first."""
        found: List[BraceCall] = []
        for match in pattern.finditer(self._text, begin, end):
            if found and match.start() < found[-1].end:
                continue
            name = self._unescape(match.group(group)) if group else ""
            call = BraceCall(self._text, match.start(), self._text.index("(", match.start()), name)
            if call.is_whole:
                found.append(call)
        return found

    def _written(self, call: BraceCall, lead: List[str]) -> WrittenBlock:
        start, brace, inner_end, end = (self._line(index) for index in (call.start, call.brace, call.inner_end, call.end - 1))
        written = WrittenBlock(self._language, None, lead, self._lines[start : brace + 1])
        written.close = self._lines[inner_end : end + 1]
        return written

    def _inside(self, call: BraceCall) -> Tuple[int, int]:
        return self._line(call.brace) + 1, self._line(call.inner_end)

    def _setup(self, call: BraceCall, children: List[Tuple[int, int]]) -> CodeBody:
        """The lines inside a block that belong to no child block: shared fields and helpers."""
        first, last = self._inside(call)
        covered = {line for start, end in children for line in range(self._line(start), self._line(end - 1) + 1)}
        kept = [self._lines[index] for index in range(first, last) if index not in covered]
        return CodeBody(re.sub(r"\n\s*\n(\s*\n)+", "\n\n", "\n".join(kept)), self._language)

    def _line(self, index: int) -> int:
        return self._text.count("\n", 0, index)
