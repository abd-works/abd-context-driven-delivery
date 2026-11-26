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
from typing import TYPE_CHECKING, Any

from cdd_guidance.practices.source_code import PYTHON, CodeBody
from cdd_guidance.practices.stories.model.story_file import StoryFile
from cdd_guidance.practices.stories.model.story_map import Example, ExampleValue, Scenario, StepType, Story
from cdd_guidance.practices.stories.model.story_map_files import source_at

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_recording import StoryRecording

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

    def __init__(self, name: str, example_value: ExampleValue = None, facts: dict | None = None, declared: tuple | None = None) -> None:
        super().__init__(name, example_value)
        self.fixture_facts = dict(facts or {})
        self._declared = declared

    def recorded_facts(self, recording: "StoryRecording", file: str) -> dict:
        return dict(self.fixture_facts)

    @property
    def declaration(self) -> tuple | None:
        """The examples module the fixture is defined in, and its definition's first and last line."""
        return self._declared

    def clone(self) -> "FixtureExample":
        cloned = type(self)(self.name, dict(self.value) if isinstance(self.value, dict) else self.value, self.fixture_facts, self._declared)
        cloned.sequential_order, cloned.scope = self.sequential_order, self.scope
        return cloned


@dataclass(frozen=True)
class StepCode:
    """One step function of a scenario: the kind its decorator names (``when``, ``and_``), the words it is written in,
    and the function."""

    kind: str
    words: str
    function: ast.FunctionDef


@dataclass(frozen=True)
class Fixture:
    """One fixture of an examples module: the fields it is built with, the names its definition holds, and the first and
    last line of its definition."""

    cells: dict
    names: tuple[str, ...]
    lines: tuple[int, int] = (0, 0)


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
                found[node.targets[0].id] = Fixture(self._cells(node.value), tuple(dict.fromkeys(_IDENTIFIER.findall(definition))), (node.lineno, node.end_lineno or node.lineno))
        return found

    @cached_property
    def _fields(self) -> dict[str, list[str]]:
        """Each class of the module with its annotated fields, in the order it declares them."""
        return {
            node.name: [item.target.id for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]
            for node in self._tree.body
            if isinstance(node, ast.ClassDef)
        }

    def _cells(self, built: ast.expr) -> dict:
        """The fields of a fixture built by calling a class of the module; one value for anything else."""
        if isinstance(built, ast.Call) and isinstance(built.func, ast.Name) and built.func.id in self._fields:
            fields = self._fields[built.func.id]
            cells = {"group": built.func.id}
            cells.update({name: self._shown(arg) for name, arg in zip(fields, built.args)})
            cells.update({keyword.arg: self._shown(keyword.value) for keyword in built.keywords if keyword.arg})
            return cells
        return {"value": self._shown(built)}

    def _shown(self, expression: ast.expr) -> str:
        if isinstance(expression, ast.Constant):
            return str(expression.value)
        return ast.get_source_segment(self._text, expression) or ""


class SharedStoryFile(StoryFile):
    """One shared story file, read once: its stories, each with its scenarios in the order the file writes them. Its
    examples module is looked for in the project first, then in the folders Python imports from. Its own code is not
    kept."""

    @cached_property
    def _read(self) -> tuple[list, None]:
        return self._stories(), None

    @cached_property
    def _tree(self) -> ast.Module:
        return ast.parse(self.text)

    @cached_property
    def _lines(self) -> list[str]:
        return self.text.splitlines()

    @cached_property
    def _search(self) -> list[Path]:
        return [*([Path(self.project)] if self.project is not None else []), Path.cwd(), *map(Path, sys.path)]

    def _stories(self) -> list:
        """The stories of the file, each with its scenarios in the order the file writes them."""
        story_class = self.model.story_class
        stories: dict[str, Any] = {}
        for function in self._tree.body:
            named = self._decorated_with(function, frozenset({_SCENARIO}))
            if named is None or len(named) < 2:
                continue
            story = stories.setdefault(named[0], story_class(named[0], len(stories) + 1))
            story.scenarios.append(self._scenario(story, named[1], function))
        return list(stories.values())

    def _scenario(self, story: Story, name: str, function: ast.FunctionDef) -> Scenario:
        scenario = story.scenario_class(name=name, sequential_order=len(story.scenarios) + 1)
        first = min([function.lineno, *(decorator.lineno for decorator in function.decorator_list)])
        scenario.source = source_at(self.path, first, function.end_lineno or first)
        for step in self._steps_of(function):
            self._add_step(scenario, step)
        scenario_text = self._code_of(function)
        for name_used, example in self._examples.items():
            if re.search(rf"\b{re.escape(name_used)}\b", scenario_text):
                scenario.examples[name_used] = example.clone()
        return scenario

    def _add_step(self, scenario: Scenario, code: StepCode) -> None:
        """Put the step code writes on scenario, as the kind its decorator names, its body the code it runs; an And or
        But continues the step before it, in that step's phase."""
        continued = scenario.steps[-1] if code.kind in _CONTINUATIONS and scenario.steps else None
        phase = _PHASES.get(code.kind) or (continued.step_type if continued is not None else StepType.GIVEN)
        order = len(continued.ands if continued is not None else scenario.steps) + 1
        made = scenario.step_class(code.words, phase, order)
        made.keyword = _CONTINUATIONS.get(code.kind, code.kind.capitalize())
        made.body = CodeBody(self._code_of(code.function), PYTHON)
        if continued is not None:
            continued.ands = [*continued.ands, made]
        else:
            scenario.steps.append(made)

    def _steps_of(self, function: ast.FunctionDef) -> list[StepCode]:
        """The step functions of a scenario's function, in order."""
        steps = []
        for item in function.body:
            words = self._decorated_with(item, frozenset({*_PHASES, *_CONTINUATIONS}))
            if words:
                steps.append(StepCode(self._decorator_name(item), words[0], item))
        return steps

    def _code_of(self, function: ast.FunctionDef) -> str:
        """The function's lines, comments included, then those of each helper function of the file it calls, once."""
        seen: list[str] = []
        texts: list[str] = []
        pending = [function]
        while pending:
            current = pending.pop(0)
            texts.append("\n".join(self._lines[current.lineno - 1 : current.end_lineno]))
            for called in sorted({self._called(node) for node in ast.walk(current) if isinstance(node, ast.Call)}):
                if called in self._helpers and called not in seen:
                    seen.append(called)
                    pending.append(self._helpers[called])
        return "\n".join(texts)

    @cached_property
    def _helpers(self) -> dict[str, ast.FunctionDef]:
        """The file's own module-level functions, which its steps call, by name."""
        return {node.name: node for node in self._tree.body if isinstance(node, ast.FunctionDef) and self._decorated_with(node, frozenset({_SCENARIO})) is None}

    @cached_property
    def _examples(self) -> dict[str, FixtureExample]:
        """Each fixture the file imports from its examples module, as an example with the facts its uses give; a
        function the module offers is no fixture."""
        found: dict[str, FixtureExample] = {}
        for module, names in self._imports():
            path = self._module_path(module)
            fixtures = FixtureModule(path.read_text(encoding="utf-8") if path is not None else "").fixtures
            for name in (imported for imported in names if imported in fixtures):
                declared = (path, *fixtures[name].lines)
                found[name] = FixtureExample(name, fixtures[name].cells, facts=self._facts_of(name, fixtures[name]), declared=declared)
        return found

    def _imports(self) -> list[tuple[str, list[str]]]:
        return [
            (node.module, [alias.asname or alias.name for alias in node.names])
            for node in self._tree.body
            if isinstance(node, ast.ImportFrom) and node.module and _EXAMPLES_MODULE.search(node.module)
        ]

    def _module_path(self, module: str) -> Path | None:
        """The examples module's file, in the first folder searched that holds it; none when none does."""
        relative = Path(*module.split(".")).with_suffix(".py")
        return next((folder / relative for folder in self._search if (folder / relative).is_file()), None)

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

    def _decorated_with(self, node: ast.AST, names: frozenset[str]) -> list[str] | None:
        """The string arguments of node's decorator called one of names; none for any other node."""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return None
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and self._called(decorator) in names:
                return [arg.value for arg in decorator.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
        return None

    def _decorator_name(self, node: ast.FunctionDef) -> str:
        return next(self._called(decorator) for decorator in node.decorator_list if isinstance(decorator, ast.Call))

    def _called(self, call: ast.Call) -> str:
        """The name a call ends in: ``when`` for ``s.when(...)``, ``board_of`` for ``board_of(world)``."""
        func = call.func
        if isinstance(func, ast.Attribute):
            return func.attr
        return func.id if isinstance(func, ast.Name) else ""


def is_shared_story_file(text: str) -> bool:
    """True for the text of a shared story file: it declares its scenarios with ``@<stories>.scenario(...)``."""
    return bool(_SHARED_MARK.search(text))
