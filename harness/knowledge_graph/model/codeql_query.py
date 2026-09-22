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


def query_workspace(root: Path) -> CodeQLPracticeGraphExport:
    """Run the story and example queries over TypeScript under *root*."""
    root = Path(root).resolve()
    stories: List[CodeQLStory] = []
    scenarios: List[CodeQLScenario] = []
    backgrounds: List[CodeQLBackground] = []
    steps: List[CodeQLStep] = []
    examples: List[CodeQLExampleExport] = []

    for path in _iter_files(root):
        rel = _rel(path, root)
        if _STORY_FILE.match(path.name) and path.name != "story-test.ts":
            s, sc, bg, st = _query_story_file(path, rel)
            stories.extend(s)
            scenarios.extend(sc)
            backgrounds.extend(bg)
            steps.extend(st)
        if _EXAMPLE_FILE.match(path.name):
            examples.extend(_query_example_file(path, rel))

    return CodeQLPracticeGraphExport(
        stories=stories,
        scenarios=scenarios,
        backgrounds=backgrounds,
        steps=steps,
        example_exports=examples,
    )


def _iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        yield path


def _rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root)).replace("\\", "/")


def _query_story_file(
    path: Path, rel: str
) -> Tuple[List[CodeQLStory], List[CodeQLScenario], List[CodeQLBackground], List[CodeQLStep]]:
    source = path.read_text(encoding="utf-8", errors="replace")
    calls = _scan_calls(source)
    _attach_bodies(source, calls)

    epic, sub_epic = _owners_from_story_path(rel)
    story_calls = [c for c in calls if c.name == "story" and c.text]
    scenario_calls = [c for c in calls if c.name == "scenario" and c.text]
    background_calls = [c for c in calls if c.name == "background"]
    step_calls = [c for c in calls if c.name in _KEYWORD]

    stories = [
        CodeQLStory(c.text, rel, epic=epic, sub_epic=sub_epic, line=c.line)
        for c in story_calls
    ]

    def _story_for(pos: int) -> str:
        for story in story_calls:
            if _contains(story, pos):
                return story.text
        return story_calls[0].text if story_calls else ""

    scenarios = []
    for call in scenario_calls:
        scenarios.append(
            CodeQLScenario(call.text, _story_for(call.start), rel, line=call.line)
        )

    backgrounds = []
    for call in background_calls:
        end_line = source[: max(call.body_end, call.start)].count("\n") + 1
        backgrounds.append(
            CodeQLBackground(
                call.text or "background",
                _story_for(call.start),
                rel,
                line=call.line,
                end_line=end_line,
                scope=call.text if call.text in {"each", "all"} else "each",
            )
        )

    steps: List[CodeQLStep] = []
    last_phase_by_parent: dict[tuple[str, str], str] = {}
    for call in step_calls:
        scenario_name, background_name = _step_parent(
            call.start, scenario_calls, background_calls
        )
        parent = (rel, scenario_name or background_name)
        if call.name in _PHASE:
            phase = _PHASE[call.name]
            last_phase_by_parent[parent] = phase
        else:
            phase = last_phase_by_parent.get(parent, "then")
        steps.append(
            CodeQLStep(
                keyword=_KEYWORD[call.name],
                text=call.text,
                file=rel,
                line=call.line,
                story=_story_for(call.start),
                scenario=scenario_name,
                background=background_name,
                phase=phase,
            )
        )

    return stories, scenarios, backgrounds, steps


def _step_parent(
    pos: int,
    scenarios: List[_Call],
    backgrounds: List[_Call],
) -> Tuple[str, str]:
    for scenario in scenarios:
        if _contains(scenario, pos):
            return scenario.text, ""
    for background in backgrounds:
        if _contains(background, pos):
            return "", background.text or "background"
    return "", ""


def _contains(call: _Call, pos: int) -> bool:
    if call.body_start < 0 or call.body_end < 0:
        return False
    return call.body_start <= pos < call.body_end


def _owners_from_story_path(rel: str) -> Tuple[str, str]:
    parts = rel.replace("\\", "/").split("/")
    if "stories" in parts:
        idx = parts.index("stories") + 1
        rest = [p for p in parts[idx:] if p != "examples"]
        epic = _display(rest[0]) if rest else ""
        sub = ""
        if len(rest) >= 2 and not _STORY_FILE.match(rest[1]):
            sub = _display(rest[1])
        return epic, sub
    return "", ""


def _owners_from_example_path(rel: str) -> Tuple[str, str]:
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
    return _display(folder), kind


def _display(slug: str) -> str:
    if not slug:
        return ""
    if " " in slug:
        return slug
    return slug.replace("-", " ").replace("_", " ").title()


def _query_example_file(path: Path, rel: str) -> List[CodeQLExampleExport]:
    source = path.read_text(encoding="utf-8", errors="replace")
    owner, owner_kind = _owners_from_example_path(rel)
    out: List[CodeQLExampleExport] = []
    matches = list(_EXPORT.finditer(source))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        chunk = source[start:end]
        demonstrates = list(dict.fromkeys(_NEW_CLASS.findall(chunk)))
        out.append(
            CodeQLExampleExport(
                export_name=match.group(1),
                file=rel,
                demonstrates=demonstrates,
                line=source[: match.start()].count("\n") + 1,
                owner=owner,
                owner_kind=owner_kind,
            )
        )
    return out


def _scan_calls(source: str) -> List[_Call]:
    calls: List[_Call] = []
    i = 0
    n = len(source)
    while i < n:
        if source[i] in " \t\r\n":
            i += 1
            continue
        nxt = _skip_comment(source, i)
        if nxt != i:
            i = nxt
            continue
        if source[i] in "'\"`":
            i = _skip_string(source, i)
            continue
        if source[i] == "." and i + 1 < n and _is_ident_start(source[i + 1]):
            name, j = _read_ident(source, i + 1)
            if name in _CHAIN_NAMES:
                j = _skip_ws(source, j)
                if j < n and source[j] == "(":
                    text, _end = _first_string_arg(source, j)
                    if text is not None:
                        calls.append(_Call(name, text, i, _line(source, i)))
                    i = j + 1
                    continue
        if _is_ident_start(source[i]) and (i == 0 or not _is_ident_char(source[i - 1])):
            name, j = _read_ident(source, i)
            if name in _CALL_NAMES:
                j = _skip_ws(source, j)
                if j < n and source[j] == "(":
                    text, _end = _first_string_arg(source, j)
                    if name == "background":
                        calls.append(_Call(name, text or "background", i, _line(source, i)))
                    elif text is not None:
                        calls.append(_Call(name, text, i, _line(source, i)))
                    i = j + 1
                    continue
        i += 1
    return calls


def _attach_bodies(source: str, calls: List[_Call]) -> None:
    for call in calls:
        if call.name not in {"story", "scenario", "background"}:
            continue
        span = _callback_body_span(source, call.start)
        if span is not None:
            call.body_start, call.body_end = span


def _callback_body_span(source: str, call_pos: int) -> Optional[Tuple[int, int]]:
    paren_at = source.find("(", call_pos)
    if paren_at < 0:
        return None
    i = paren_at + 1
    n = len(source)
    depth = 1
    saw_arrow = False
    while i < n and depth > 0:
        nxt = _skip_comment(source, i)
        if nxt != i:
            i = nxt
            continue
        ch = source[i]
        if ch in "'\"`":
            i = _skip_string(source, i)
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif source.startswith("=>", i):
            saw_arrow = True
            i += 2
            continue
        elif saw_arrow and ch == "{":
            end = _match_brace(source, i)
            return (i, end) if end >= 0 else None
        i += 1
    return None


def _match_brace(source: str, open_idx: int) -> int:
    depth = 0
    i = open_idx
    n = len(source)
    while i < n:
        nxt = _skip_comment(source, i)
        if nxt != i:
            i = nxt
            continue
        ch = source[i]
        if ch in "'\"`":
            i = _skip_string(source, i)
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _first_string_arg(source: str, paren_idx: int) -> Tuple[Optional[str], int]:
    i = _skip_ws(source, paren_idx + 1)
    if i < len(source) and source[i] in "'\"`":
        text, end = _read_string(source, i)
        return text, end
    return None, paren_idx


def _read_string(source: str, start: int) -> Tuple[str, int]:
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
            chars.append("${")
            i += 2
            depth = 1
            while i < n and depth:
                if source[i] == "{":
                    depth += 1
                elif source[i] == "}":
                    depth -= 1
                    if depth == 0:
                        chars.append("}")
                        i += 1
                        break
                else:
                    chars.append(source[i])
                i += 1
            continue
        if ch == quote:
            return "".join(chars), i + 1
        if ch == "\n" and quote != "`":
            return "".join(chars), i
        chars.append(ch)
        i += 1
    return "".join(chars), i


def _skip_string(source: str, start: int) -> int:
    _text, end = _read_string(source, start)
    return end


def _skip_comment(source: str, i: int) -> int:
    if source.startswith("//", i):
        nl = source.find("\n", i)
        return len(source) if nl < 0 else nl + 1
    if source.startswith("/*", i):
        end = source.find("*/", i + 2)
        return len(source) if end < 0 else end + 2
    return i


def _skip_ws(source: str, i: int) -> int:
    n = len(source)
    while i < n and source[i] in " \t\r\n":
        i += 1
    return i


def _is_ident_start(ch: str) -> bool:
    return ch.isalpha() or ch == "_" or ch == "$"


def _is_ident_char(ch: str) -> bool:
    return ch.isalnum() or ch in {"_", "$"}


def _read_ident(source: str, i: int) -> Tuple[str, int]:
    j = i
    while j < len(source) and _is_ident_char(source[j]):
        j += 1
    return source[i:j], j


def _line(source: str, pos: int) -> int:
    return source[:pos].count("\n") + 1
