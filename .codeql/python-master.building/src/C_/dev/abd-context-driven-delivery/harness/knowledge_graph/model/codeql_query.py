"""CodeQL queries over TypeScript story tests and example factories.

These predicates match ``codeql/*.ql``. When a CodeQL database export is
absent, ``query_workspace`` runs the same queries against the source so the
graph still comes from the code — never from markdown.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .codeql_export import (
    CodeQLBackground,
    CodeQLExampleExport,
    CodeQLPracticeGraphExport,
    CodeQLScenario,
    CodeQLStep,
    CodeQLStory,
)

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".codeql"}
_STORY_FILE = re.compile(r".+_story\.test\.tsx?$")
_EXAMPLE_FILE = re.compile(r".+\.examples\.ts$")
_EXPORT = re.compile(r"^export const (\w+)\s*=", re.M)
_NEW_CLASS = re.compile(r"\bnew\s+([A-Z][A-Za-z0-9_]*)")
_CALL_NAMES = {"story", "scenario", "background", "given", "when", "then"}
_CHAIN_NAMES = {"and", "but"}
_KEYWORD = {
    "given": "Given",
    "when": "When",
    "then": "Then",
    "and": "And",
    "but": "But",
}
_PHASE = {"given": "given", "when": "when", "then": "then"}


@dataclass
class _Call:
    name: str
    text: str
    start: int
    line: int
    body_start: int = -1
    body_end: int = -1

    def contains(self, pos: int) -> bool:
        if self.body_start < 0 or self.body_end < 0:
            return False
        return self.body_start <= pos < self.body_end


def query_workspace(root: Path) -> CodeQLPracticeGraphExport:
    """Run the story and example queries over TypeScript under *root*."""
    return StorySourceQuery(root).run()


class StorySourceQuery:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self._source = ""
        self._calls: List[_Call] = []
        self._story_calls: List[_Call] = []
        self._scenario_calls: List[_Call] = []
        self._background_calls: List[_Call] = []
        self._file = ""

    def run(self) -> CodeQLPracticeGraphExport:
        stories: List[CodeQLStory] = []
        scenarios: List[CodeQLScenario] = []
        backgrounds: List[CodeQLBackground] = []
        steps: List[CodeQLStep] = []
        examples: List[CodeQLExampleExport] = []
        for path in self._iter_files():
            rel = self._rel(path)
            if _STORY_FILE.match(path.name) and path.name != "story-test.ts":
                s, sc, bg, st = self._query_story_file(path, rel)
                stories.extend(s)
                scenarios.extend(sc)
                backgrounds.extend(bg)
                steps.extend(st)
            if _EXAMPLE_FILE.match(path.name):
                examples.extend(self._query_example_file(path, rel))
        return CodeQLPracticeGraphExport(
            stories=stories,
            scenarios=scenarios,
            backgrounds=backgrounds,
            steps=steps,
            example_exports=examples,
        )

    def _iter_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            yield path

    def _rel(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.root)).replace("\\", "/")

    def _query_story_file(
        self, path: Path, rel: str
    ) -> Tuple[List[CodeQLStory], List[CodeQLScenario], List[CodeQLBackground], List[CodeQLStep]]:
        self._source = path.read_text(encoding="utf-8", errors="replace")
        self._file = rel
        calls = self._scan_calls(self._source)
        self._attach_bodies(calls)
        epic, sub_epic = self._owners_from_story_path(rel)
        self._story_calls = [c for c in calls if c.name == "story" and c.text]
        self._scenario_calls = [c for c in calls if c.name == "scenario" and c.text]
        self._background_calls = [c for c in calls if c.name == "background"]
        stories = [
            CodeQLStory(c.text, rel, epic=epic, sub_epic=sub_epic, line=c.line)
            for c in self._story_calls
        ]
        scenarios = self._scenarios()
        backgrounds = self._backgrounds()
        steps = self._steps([c for c in calls if c.name in _KEYWORD])
        return stories, scenarios, backgrounds, steps

    def _story_for(self, pos: int) -> str:
        for story in self._story_calls:
            if story.contains(pos):
                return story.text
        return self._story_calls[0].text if self._story_calls else ""

    def _scenarios(self) -> List[CodeQLScenario]:
        scenarios: List[CodeQLScenario] = []
        for call in self._scenario_calls:
            scenarios.append(
                CodeQLScenario(call.text, self._story_for(call.start), self._file, line=call.line)
            )
        return scenarios

    def _backgrounds(self) -> List[CodeQLBackground]:
        backgrounds: List[CodeQLBackground] = []
        for call in self._background_calls:
            end_line = self._source[: max(call.body_end, call.start)].count("\n") + 1
            backgrounds.append(
                CodeQLBackground(
                    call.text or "background",
                    self._story_for(call.start),
                    self._file,
                    line=call.line,
                    end_line=end_line,
                    scope=call.text if call.text in {"each", "all"} else "each",
                )
            )
        return backgrounds

    def _steps(self, step_calls: List[_Call]) -> List[CodeQLStep]:
        steps: List[CodeQLStep] = []
        last_phase_by_parent: dict[tuple[str, str], str] = {}
        for call in step_calls:
            scenario_name, background_name = self._step_parent(call.start)
            parent = (self._file, scenario_name or background_name)
            if call.name in _PHASE:
                last_phase_by_parent[parent] = _PHASE[call.name]
                phase = _PHASE[call.name]
            else:
                phase = last_phase_by_parent.get(parent, "then")
            steps.append(
                CodeQLStep(
                    keyword=_KEYWORD[call.name],
                    text=call.text,
                    file=self._file,
                    line=call.line,
                    story=self._story_for(call.start),
                    scenario=scenario_name,
                    background=background_name,
                    phase=phase,
                )
            )
        return steps

    def _step_parent(self, pos: int) -> Tuple[str, str]:
        for scenario in self._scenario_calls:
            if scenario.contains(pos):
                return scenario.text, ""
        for background in self._background_calls:
            if background.contains(pos):
                return "", background.text or "background"
        return "", ""

    def _owners_from_story_path(self, rel: str) -> Tuple[str, str]:
        parts = rel.replace("\\", "/").split("/")
        if "stories" not in parts:
            return "", ""
        idx = parts.index("stories") + 1
        rest = [p for p in parts[idx:] if p != "examples"]
        epic = self._display(rest[0]) if rest else ""
        sub = ""
        if len(rest) >= 2 and not _STORY_FILE.match(rest[1]):
            sub = self._display(rest[1])
        return epic, sub

    def _owners_from_example_path(self, rel: str) -> Tuple[str, str]:
        parts = rel.replace("\\", "/").split("/")
        if "examples" not in parts:
            return "", ""
        folder = parts[parts.index("examples") - 1] if parts.index("examples") > 0 else ""
        if folder == "stories":
            return "", ""
        kind = "sub_epic"
        if "stories" in parts:
            after = parts[parts.index("stories") + 1 :]
            if after and after[0] == folder:
                kind = "epic"
        return self._display(folder), kind

    def _display(self, slug: str) -> str:
        if not slug:
            return ""
        if " " in slug:
            return slug
        return slug.replace("-", " ").replace("_", " ").title()

    def _query_example_file(self, path: Path, rel: str) -> List[CodeQLExampleExport]:
        self._source = path.read_text(encoding="utf-8", errors="replace")
        owner, owner_kind = self._owners_from_example_path(rel)
        out: List[CodeQLExampleExport] = []
        matches = list(_EXPORT.finditer(self._source))
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(self._source)
            chunk = self._source[start:end]
            demonstrates = list(dict.fromkeys(_NEW_CLASS.findall(chunk)))
            out.append(
                CodeQLExampleExport(
                    export_name=match.group(1),
                    file=rel,
                    demonstrates=demonstrates,
                    line=self._source[: match.start()].count("\n") + 1,
                    owner=owner,
                    owner_kind=owner_kind,
                )
            )
        return out

    def _scan_calls(self, source: str) -> List[_Call]:
        self._source = source
        self._calls = []
        i = 0
        n = len(source)
        while i < n:
            if source[i] in " \t\r\n":
                i += 1
                continue
            nxt = self._skip_comment(i)
            if nxt != i:
                i = nxt
                continue
            if source[i] in "'\"`":
                i = self._skip_string(i)
                continue
            chain = self._scan_chain_call(i)
            if chain is not None:
                i = chain
                continue
            named = self._scan_named_call(i)
            if named is not None:
                i = named
                continue
            i += 1
        return self._calls

    def _scan_chain_call(self, i: int) -> Optional[int]:
        source = self._source
        n = len(source)
        if source[i] != "." or i + 1 >= n:
            return None
        if not self._is_ident_start(source[i + 1]):
            return None
        name, j = self._read_ident(i + 1)
        if name not in _CHAIN_NAMES:
            return None
        j = self._skip_ws(j)
        if j >= n or source[j] != "(":
            return None
        text, _end = self._first_string_arg(j)
        if text is not None:
            self._calls.append(_Call(name, text, i, self._line(i)))
        return j + 1

    def _scan_named_call(self, i: int) -> Optional[int]:
        source = self._source
        n = len(source)
        if not self._is_ident_start(source[i]):
            return None
        if i != 0 and self._is_ident_char(source[i - 1]):
            return None
        name, j = self._read_ident(i)
        if name not in _CALL_NAMES:
            return None
        j = self._skip_ws(j)
        if j >= n or source[j] != "(":
            return None
        text, _end = self._first_string_arg(j)
        if name == "background":
            self._calls.append(_Call(name, text or "background", i, self._line(i)))
            return j + 1
        if text is not None:
            self._calls.append(_Call(name, text, i, self._line(i)))
        return j + 1

    def _attach_bodies(self, calls: List[_Call]) -> None:
        for call in calls:
            if call.name not in {"story", "scenario", "background"}:
                continue
            span = self._callback_body_span(call.start)
            if span is None:
                continue
            call.body_start, call.body_end = span

    def _callback_body_span(self, call_pos: int) -> Optional[Tuple[int, int]]:
        paren_at = self._source.find("(", call_pos)
        if paren_at < 0:
            return None
        return self._skip_in_parens(paren_at + 1)

    def _skip_in_parens(self, i: int) -> Optional[Tuple[int, int]]:
        source = self._source
        n = len(source)
        depth = 1
        saw_arrow = False
        while i < n and depth > 0:
            nxt = self._skip_comment(i)
            if nxt != i:
                i = nxt
                continue
            ch = source[i]
            if ch in "'\"`":
                i = self._skip_string(i)
                continue
            if ch == "(":
                depth += 1
                i += 1
                continue
            if ch == ")":
                depth -= 1
                i += 1
                continue
            if source.startswith("=>", i):
                saw_arrow = True
                i += 2
                continue
            span = self._body_after_arrow(saw_arrow, i)
            if span is not None:
                return span
            i += 1
        return None

    def _body_after_arrow(self, saw_arrow: bool, i: int) -> Optional[Tuple[int, int]]:
        if not saw_arrow:
            return None
        if self._source[i] != "{":
            return None
        end = self._match_brace(i)
        if end < 0:
            return None
        return (i, end)

    def _match_brace(self, open_idx: int) -> int:
        depth = 0
        i = open_idx
        n = len(self._source)
        while i < n:
            nxt = self._skip_comment(i)
            if nxt != i:
                i = nxt
                continue
            ch = self._source[i]
            if ch in "'\"`":
                i = self._skip_string(i)
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        return -1

    def _first_string_arg(self, paren_idx: int) -> Tuple[Optional[str], int]:
        i = self._skip_ws(paren_idx + 1)
        if i < len(self._source) and self._source[i] in "'\"`":
            text, end = self._read_string(i)
            return text, end
        return None, paren_idx

    def _read_string(self, start: int) -> Tuple[str, int]:
        source = self._source
        quote = source[start]
        i = start + 1
        n = len(source)
        chars: List[str] = []
        while i < n:
            ch = source[i]
            if ch == "\\" and i + 1 < n:
                chars.append(source[i + 1])
                i += 2
                continue
            if quote == "`" and ch == "$" and i + 1 < n and source[i + 1] == "{":
                i = self._read_interpolation(i, chars)
                continue
            if ch == quote:
                return "".join(chars), i + 1
            if ch == "\n" and quote != "`":
                return "".join(chars), i
            chars.append(ch)
            i += 1
        return "".join(chars), i

    def _read_interpolation(self, i: int, chars: List[str]) -> int:
        chars.append("${")
        i += 2
        source = self._source
        n = len(source)
        depth = 1
        while i < n and depth:
            if source[i] == "{":
                depth += 1
                i += 1
                continue
            if source[i] != "}":
                chars.append(source[i])
                i += 1
                continue
            depth -= 1
            if depth == 0:
                chars.append("}")
                return i + 1
            i += 1
        return i

    def _skip_string(self, start: int) -> int:
        _text, end = self._read_string(start)
        return end

    def _skip_comment(self, i: int) -> int:
        source = self._source
        if source.startswith("//", i):
            nl = source.find("\n", i)
            return len(source) if nl < 0 else nl + 1
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            return len(source) if end < 0 else end + 2
        return i

    def _skip_ws(self, i: int) -> int:
        source = self._source
        n = len(source)
        while i < n and source[i] in " \t\r\n":
            i += 1
        return i

    def _is_ident_start(self, ch: str) -> bool:
        return ch.isalpha() or ch == "_" or ch == "$"

    def _is_ident_char(self, ch: str) -> bool:
        return ch.isalnum() or ch in {"_", "$"}

    def _read_ident(self, i: int) -> Tuple[str, int]:
        j = i
        source = self._source
        while j < len(source) and self._is_ident_char(source[j]):
            j += 1
        return source[i:j], j

    def _line(self, pos: int) -> int:
        return self._source[:pos].count("\n") + 1
