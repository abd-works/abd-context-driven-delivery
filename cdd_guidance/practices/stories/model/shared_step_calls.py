"""SharedStepCalls. What each step of the Python shared story files (``*.story.shared.py``) calls, so a step a markdown
story test writes in words links to the operations its acceptance test runs.

A shared story file replays the story test's scenarios: ``@shared_stories.scenario("Story", "Scenario")`` holds one
scenario, and each ``@s.given(...)``, ``@s.when(...)``, ``@s.then(...)``, ``@s.and_(...)``, or ``@s.but_(...)`` inside
it is one step, written in the story test's words. A step calls the operations its body calls, and those its
realization comments name (``# Board.show()``, ``#   -> checkout-flow.text``).
"""

from __future__ import annotations

import ast
import re
from functools import cached_property
from pathlib import Path

from harness.graph.skipped_folders import scanned_files

_SHARED_SUFFIX = ".story.shared.py"
_SCENARIO = "scenario"
_STEPS = frozenset({"given", "when", "then", "and_", "but_"})
_REALIZED_CALL = re.compile(r"([A-Za-z_]\w*)\s*\(")
_REALIZED_READ = re.compile(r"->\s*[\w-]+\.(\w+)")
_KEYWORD = re.compile(r"^(?:given|when|then|and|but)\s+")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_MARKS = re.compile(r"\+\+|\*\*|[*`]")


def step_words(text: str) -> str:
    """A step's words as both a story test and a shared story file write them: no keyword, links, or marks, in lower
    case, with no closing full stop."""
    plain = _MARKS.sub("", _LINK.sub(r"\1", str(text)))
    words = " ".join(plain.split()).casefold()
    return _KEYWORD.sub("", words).rstrip(".")


class SharedStepCalls:
    """The names each step of the shared story files under one folder calls, by its story, scenario, and words; read
    from the files the first time a step asks."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def called_by(self, story: str, scenario: str, step: str) -> set[str]:
        """The names the shared step of story and scenario written as step calls; none when no shared file holds it."""
        return self._calls.get((story.casefold(), scenario.casefold(), step_words(step)), set())

    @cached_property
    def _calls(self) -> dict[tuple[str, str, str], set[str]]:
        found: dict[tuple[str, str, str], set[str]] = {}
        for path in scanned_files(self.root, {".py"}):
            if path.name.endswith(_SHARED_SUFFIX):
                found.update(_SharedFile(path.read_text(encoding="utf-8")).calls())
        return found


class _SharedFile:
    """One shared story file's text, parsed."""

    def __init__(self, text: str) -> None:
        self._lines = text.splitlines()
        self._tree = ast.parse(text)

    def calls(self) -> dict[tuple[str, str, str], set[str]]:
        """Each step's names, keyed by its story, scenario, and words."""
        found: dict[tuple[str, str, str], set[str]] = {}
        for scenario in ast.walk(self._tree):
            named = _decorated(scenario, frozenset({_SCENARIO}))
            if named is None or len(named) < 2:
                continue
            for step in scenario.body:
                words = _decorated(step, _STEPS)
                if words:
                    found[(named[0].casefold(), named[1].casefold(), step_words(words[0]))] = self._names_in(step)
        return found

    def _names_in(self, step: ast.FunctionDef) -> set[str]:
        """The names step's body calls, and those the realization comments on its lines call or read."""
        called = {_called_name(node) for node in ast.walk(step) if isinstance(node, ast.Call)}
        comments = [line.strip()[1:] for line in self._lines[step.lineno - 1 : step.end_lineno] if line.strip().startswith("#")]
        for comment in comments:
            called.update(_REALIZED_CALL.findall(comment))
            called.update(_REALIZED_READ.findall(comment))
        return {name for name in called if name}


def _decorated(node: ast.AST, names: frozenset[str]) -> list[str] | None:
    """The string arguments of node's decorator called one of names (``@s.when("...")``); none for any other node."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and _called_name(decorator) in names:
            return [arg.value for arg in decorator.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
    return None


def _called_name(call: ast.Call) -> str:
    """The name a call ends in: ``show`` for ``board.show()``, ``load`` for ``load()``."""
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return func.id if isinstance(func, ast.Name) else ""
