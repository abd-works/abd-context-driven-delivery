"""SharedStoryFile. A Python shared story file (``*.story.shared.py``) read as the code of its stories' scenarios.

A shared story file holds the scenarios the Python tiers replay: ``@shared_stories.scenario("Story", "Scenario")`` is one
scenario of one story, and each ``@s.given(...)``, ``@s.when(...)``, ``@s.then(...)``, ``@s.and_(...)``, or
``@s.but_(...)`` function inside it is one step, written in the story test's words, whose body is the step's code. A step
also runs the helper functions of the file it calls, so its code is its own function and theirs. The examples are the
fixtures the file imports from its examples module (``from space.kanban.session_board_examples import CHECKOUT_FLOW``):
each one a scenario names is one of its examples, with the fields its fixture is built with, and with the names and
reads the statements that use it hold, which link it to the classes it shows and the properties it is read through.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

from cdd_guidance.practices.clean_engineering.model.code_body import PYTHON, CodeBody
from cdd_guidance.practices.stories.model.story_model import Example, StepType

SHARED_SUFFIX = ".story.shared.py"
_SHARED_MARK = re.compile(r"@\w+\.scenario\(")
_SCENARIO = "scenario"
_PHASES = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}
_CONTINUATIONS = {"and_": "And", "but_": "But"}
_IDENTIFIER = re.compile(r"[A-Za-z_]\w*")
_EXAMPLES_MODULE = re.compile(r"examples$")


class FixtureExample(Example):
    """An example a shared story file takes from its examples module: its fixture's fields as its value, and the facts
    the statements that use it give, which it records with in place of the facts a story file's own example reads."""

    def __init__(self, name: str, value: Any = None, sequential_order: int = 0, scope=None, facts: dict | None = None) -> None:
        super().__init__(name, value, sequential_order, scope)
        self.fixture_facts = dict(facts or {})

    def recorded_facts(self, recording, file: str) -> dict:
        return dict(self.fixture_facts)

    def clone(self) -> "FixtureExample":
        value = dict(self.value) if isinstance(self.value, dict) else self.value
        return type(self)(self.name, value, self.sequential_order, self.scope, self.fixture_facts)


@dataclass(frozen=True)
class StepCode:
    """One step function of a scenario: the kind its decorator names (``when``, ``and_``), the words it is written in,
    and the function."""

    kind: str
    words: str
    function: ast.FunctionDef


@dataclass(frozen=True)
class Fixture:
    """One fixture of an examples module: the fields it is built with, and the names its definition holds."""

    cells: dict
    names: tuple[str, ...]


class FixtureModule:
    """An examples module's fixtures, by the name each is bound to, read from its source without running it: a fixture
    built by a dataclass of the module has a field for each argument, named as the class declares them; a text or a
    number is one value."""

    def __init__(self, text: str) -> None:
        self._tree = ast.parse(text) if text else ast.Module(body=[], type_ignores=[])
        self._text = text

    @cached_property
    def fixtures(self) -> dict[str, Fixture]:
        found: dict[str, Fixture] = {}
        for node in self._tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                definition = ast.get_source_segment(self._text, node) or ""
                found[node.targets[0].id] = Fixture(self._cells(node.value), tuple(dict.fromkeys(_IDENTIFIER.findall(definition))))
        return found

    @cached_property
    def _fields(self) -> dict[str, list[str]]:
        """Each class of the module with its annotated fields, in the order it declares them."""
        return {
            node.name: [item.target.id for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]
            for node in self._tree.body
            if isinstance(node, ast.ClassDef)
        }

    def _cells(self, value: ast.expr) -> dict:
        """The fields of a fixture built by calling a class of the module; one value for anything else."""
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in self._fields:
            fields = self._fields[value.func.id]
            cells = {"group": value.func.id}
            cells.update({name: self._shown(arg) for name, arg in zip(fields, value.args)})
            cells.update({keyword.arg: self._shown(keyword.value) for keyword in value.keywords if keyword.arg})
            return cells
        return {"value": self._shown(value)}

    def _shown(self, value: ast.expr) -> str:
        if isinstance(value, ast.Constant):
            return str(value.value)
        return ast.get_source_segment(self._text, value) or ""


class SharedStoryFile:
    """One shared story file's text, parsed once, with the folders its examples module is looked for in."""

    def __init__(self, text: str, search: list[Path] | None = None) -> None:
        self.text = text
        self._tree = ast.parse(text)
        self._lines = text.splitlines()
        self._search = [Path(folder) for folder in (search if search is not None else [Path.cwd(), *map(Path, sys.path)])]

    @staticmethod
    def holds(text: str) -> bool:
        """True for the text of a shared story file: it declares its scenarios with ``@<stories>.scenario(...)``."""
        return bool(_SHARED_MARK.search(text))

    def stories(self, story_type: type) -> list:
        """The stories of the file, each with its scenarios in the order the file writes them."""
        stories: dict[str, Any] = {}
        for function in self._tree.body:
            named = _decorated_with(function, frozenset({_SCENARIO}))
            if named is None or len(named) < 2:
                continue
            story = stories.setdefault(named[0], story_type(named[0], len(stories) + 1))
            story.scenarios.append(self._scenario(story, named[1], function))
        return list(stories.values())

    def _scenario(self, story, name: str, function: ast.FunctionDef):
        scenario = story.scenario_type(name=name, sequential_order=len(story.scenarios) + 1)
        for step in self._steps_of(function):
            self._add_step(scenario, step)
        scenario_text = self._code_of(function)
        for name_used, example in self._examples.items():
            if re.search(rf"\b{re.escape(name_used)}\b", scenario_text):
                scenario.examples[name_used] = example.clone()
        return scenario

    def _add_step(self, scenario, code: StepCode) -> None:
        """Put the step code writes on scenario, as the kind its decorator names, its body the code it runs; an And or
        But continues the step before it, in that step's phase."""
        continued = scenario.steps[-1] if code.kind in _CONTINUATIONS and scenario.steps else None
        phase = _PHASES.get(code.kind) or (continued.step_type if continued is not None else StepType.GIVEN)
        order = len(continued.ands if continued is not None else scenario.steps) + 1
        made = scenario.step_type(code.words, phase, order, keyword=_CONTINUATIONS.get(code.kind, code.kind.capitalize()))
        made.body = CodeBody(self._code_of(code.function), PYTHON)
        if continued is not None:
            continued.ands = [*continued.ands, made]
        else:
            scenario.steps.append(made)

    def _steps_of(self, function: ast.FunctionDef) -> list[StepCode]:
        """The step functions of a scenario's function, in order."""
        steps = []
        for item in function.body:
            words = _decorated_with(item, frozenset({*_PHASES, *_CONTINUATIONS}))
            if words:
                steps.append(StepCode(_decorator_name(item), words[0], item))
        return steps

    def _code_of(self, function: ast.FunctionDef) -> str:
        """The function's lines, comments included, then those of each helper function of the file it calls, once."""
        seen: list[str] = []
        texts: list[str] = []
        pending = [function]
        while pending:
            current = pending.pop(0)
            texts.append("\n".join(self._lines[current.lineno - 1 : current.end_lineno]))
            for called in sorted({_called(node) for node in ast.walk(current) if isinstance(node, ast.Call)}):
                if called in self._helpers and called not in seen:
                    seen.append(called)
                    pending.append(self._helpers[called])
        return "\n".join(texts)

    @cached_property
    def _helpers(self) -> dict[str, ast.FunctionDef]:
        """The file's own module-level functions, which its steps call, by name."""
        return {node.name: node for node in self._tree.body if isinstance(node, ast.FunctionDef) and _decorated_with(node, frozenset({_SCENARIO})) is None}

    @cached_property
    def _examples(self) -> dict[str, FixtureExample]:
        """Each fixture the file imports from its examples module, as an example with the facts its uses give; a
        function the module offers is no fixture."""
        found: dict[str, FixtureExample] = {}
        for module, names in self._imports():
            fixtures = FixtureModule(self._module_text(module)).fixtures
            for name in (imported for imported in names if imported in fixtures):
                found[name] = FixtureExample(name, fixtures[name].cells, facts=self._facts_of(name, fixtures[name]))
        return found

    def _imports(self) -> list[tuple[str, list[str]]]:
        return [
            (node.module, [alias.asname or alias.name for alias in node.names])
            for node in self._tree.body
            if isinstance(node, ast.ImportFrom) and node.module and _EXAMPLES_MODULE.search(node.module)
        ]

    def _module_text(self, module: str) -> str:
        """The examples module's text, from the first folder searched that holds it; empty when none does."""
        relative = Path(*module.split(".")).with_suffix(".py")
        found = next((folder / relative for folder in self._search if (folder / relative).is_file()), None)
        return found.read_text(encoding="utf-8") if found is not None else ""

    def _facts_of(self, name: str, fixture: Fixture) -> dict:
        """The names an example shows and the members read off it: the names of its definition and of every statement
        of the file that uses it, and each ``NAME.member`` the file reads."""
        statements = [
            ast.get_source_segment(self.text, node) or ""
            for node in ast.walk(self._tree)
            if isinstance(node, (ast.Expr, ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return))
            and any(isinstance(inner, ast.Name) and inner.id == name for inner in ast.walk(node))
        ]
        names = {*fixture.names, *(found for statement in statements for found in _IDENTIFIER.findall(statement))}
        reads = re.findall(rf"\b{re.escape(name)}\.(\w+)", self.text)
        return {"source_names": sorted(names), "source_reads": sorted(set(reads))}


def _decorated_with(node: ast.AST, names: frozenset[str]) -> list[str] | None:
    """The string arguments of node's decorator called one of names; none for any other node."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and _called(decorator) in names:
            return [arg.value for arg in decorator.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
    return None


def _decorator_name(node: ast.FunctionDef) -> str:
    return next(_called(decorator) for decorator in node.decorator_list if isinstance(decorator, ast.Call))


def _called(call: ast.Call) -> str:
    """The name a call ends in: ``when`` for ``s.when(...)``, ``board_of`` for ``board_of(world)``."""
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return func.id if isinstance(func, ast.Name) else ""
