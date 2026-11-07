"""Given / When / Then written once for a sub-epic and replayed on every tier, on Mamba.

A sub-epic's `{sub_epic}.story.shared.py` registers its scenarios on one `SharedStories`. Each tier's spec file loads
that file and replays the scenarios with its own tier: the domain tier hands the steps the domain classes themselves,
and the server tier hands them the same operations reached through the cdd tools. A step reaches the board only
through its `World`, so one step proves one behaviour on every tier.

Mamba collects example groups as classes, so `replay` builds one class per story and one per scenario, and the spec
file binds them at module scope with `globals().update(...)` (the Python form CDR 0002 gives a tier file).

```
file: space/kanban/story_test.py
```
"""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Callable, Protocol

GIVEN, WHEN, THEN = "given", "when", "then"
# Mamba runs the classes and functions of a group in the order of their names, so each name starts with its place.
ORDER_DIGITS = 8

StepBody = Callable[["World"], None]


class World(SimpleNamespace):
    """What one scenario's steps share: the throwaway project, the board's operations as the tier reaches them, and
    whatever an earlier step answered. A tier builds a new one for every scenario, so no scenario sees another's state."""


class Tier(Protocol):
    """How a spec file runs its scenarios: `open` wires a World on a new throwaway project, `close` takes it down."""

    name: str

    def open(self) -> World: ...

    def close(self, world: World) -> None: ...


@dataclass
class Step:
    kind: str
    text: str
    body: StepBody


@dataclass
class Scenario:
    """One scenario of one story: its steps in the order the scenario states them."""

    story: str
    name: str
    steps: list[Step] = field(default_factory=list)

    def given(self, text: str) -> Callable[[StepBody], StepBody]:
        return self._step(GIVEN, text)

    def when(self, text: str) -> Callable[[StepBody], StepBody]:
        return self._step(WHEN, text)

    def then(self, text: str) -> Callable[[StepBody], StepBody]:
        return self._step(THEN, text)

    def and_(self, text: str) -> Callable[[StepBody], StepBody]:
        return self._step(self._continued_kind(), text)

    def but_(self, text: str) -> Callable[[StepBody], StepBody]:
        return self._step(self._continued_kind(), text)

    def _continued_kind(self) -> str:
        return self.steps[-1].kind if self.steps else GIVEN

    def _step(self, kind: str, text: str) -> Callable[[StepBody], StepBody]:
        def registered(body: StepBody) -> StepBody:
            self.steps.append(Step(kind, text, body))
            return body

        return registered


class SharedStories:
    """Every scenario of one sub-epic, in the order its stories and scenarios are written."""

    def __init__(self, sub_epic: str) -> None:
        self.sub_epic = sub_epic
        self._scenarios: list[Scenario] = []

    def scenario(self, story: str, name: str) -> Callable[[Callable[[Scenario], None]], Scenario]:
        """Register the scenario that the decorated function writes the steps of."""

        def registered(write_steps: Callable[[Scenario], None]) -> Scenario:
            written = Scenario(story, name)
            write_steps(written)
            self._scenarios.append(written)
            return written

        return registered

    @property
    def scenarios(self) -> list[Scenario]:
        return list(self._scenarios)

    @property
    def stories(self) -> list[str]:
        return list(dict.fromkeys(scenario.story for scenario in self._scenarios))


def load_shared(spec_file: str, sub_epic_slug: str) -> SharedStories:
    """The SharedStories of `{sub_epic_slug}.story.shared.py` beside spec_file. Its name holds dots and dashes, so it
    is loaded from its path rather than imported by name."""
    path = Path(spec_file).resolve().with_name(f"{sub_epic_slug}.story.shared.py")
    module_spec = importlib.util.spec_from_file_location(f"{_slug(sub_epic_slug)}_story_shared", path)
    module: ModuleType = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.shared_stories


def replay(shared: SharedStories, tier: Tier, left_out: dict[str, str] | None = None) -> dict[str, type]:
    """Mamba example groups for every shared scenario this tier runs: one group per story, and in it one group per
    scenario with one example per Then. left_out names each scenario the tier cannot reach and why."""
    skipped = left_out or {}
    unknown = sorted(set(skipped) - {scenario.name for scenario in shared.scenarios})
    if unknown:
        raise LookupError(f"{shared.sub_epic} has no shared scenario named {', '.join(unknown)}")
    groups: dict[str, type] = {}
    for index, story in enumerate(shared.stories):
        scenarios = [scenario for scenario in shared.scenarios if scenario.story == story and scenario.name not in skipped]
        if scenarios:
            name = _ordered(index, f"Story_{_slug(story)}")
            groups[name] = _group(name, f"{story} ({tier.name})", {_ordered(place, f"Scenario_{_slug(scenario.name)}"): _scenario_group(scenario, tier, place) for place, scenario in enumerate(scenarios)})
    return groups


def refusal_of(operation: Callable[[], Any]) -> Exception | None:
    """The exception operation raised, or none when it ran: a When that expects a refusal keeps it for its Thens."""
    try:
        operation()
    except Exception as refused:  # noqa: BLE001 - the Then names the refusal it expects
        return refused
    return None


def ticket_in(board: dict, name: str) -> dict | None:
    """The ticket named name as the board shows it, in whichever column holds it; none when no column does."""
    columns = board["columns"]
    return next((ticket for column in columns for key in ("in_progress", "done", "tickets") for ticket in column.get(key, []) if ticket["name"] == name), None)


def column_in(board: dict, name: str) -> dict:
    return next(column for column in board["columns"] if column["name"] == name)


def names_in(column: dict) -> list[str]:
    """The tickets a column shows, In progress before Done."""
    return [ticket["name"] for key in ("in_progress", "done", "tickets") for ticket in column.get(key, [])]


def progress_in(ticket: dict, fidelity: str) -> dict:
    """The progress of the fidelity slug names, such as stories-story-map, as the ticket shows it."""
    return next(progress for progress in ticket["progress"] if progress["slug"] == fidelity)


def expect_placed(ticket: dict, column: str, is_done: bool) -> None:
    """The ticket shows in column, in its Done when is_done, else In progress."""
    actual = (ticket["column"]["name"], ticket["is_done"])
    if actual != (column, is_done):
        raise AssertionError(f"expected {ticket['name']} in {column} {'Done' if is_done else 'In progress'}, but it is in {actual[0]} {'Done' if actual[1] else 'In progress'}")


def expect_actions(ticket: dict, fidelity: str, generate: str, validate: str, review: str) -> None:
    """The fidelity's Generate, Validate, and Review each read to_do, in_progress, or done on the ticket."""
    expected = {"generate": generate, "validate": validate, "review": review}
    actual = progress_in(ticket, fidelity)["actions"]
    if actual != expected:
        raise AssertionError(f"expected {fidelity} on {ticket['name']} to read {expected}, but it reads {actual}")


def expect_action(ticket: dict, fidelity: str, action: str, state: str) -> None:
    """One of the fidelity's Generate, Validate, and Review reads state on the ticket."""
    _expect_equal(progress_in(ticket, fidelity)["actions"][action], state, f"{fidelity} {action} on {ticket['name']}")


def expect_held_on_violations(ticket: dict, fidelity: str) -> None:
    """The fidelity's Validate is in progress until its violations are fixed, and its segment shows violations."""
    progress = progress_in(ticket, fidelity)
    _expect_equal((progress["actions"]["validate"], progress["state"]), ("in_progress", "violations"), f"{fidelity} on {ticket['name']}")


def expect_no_next(ticket: dict) -> None:
    """Run next has nothing to run on the ticket."""
    _expect_equal(ticket["next"], None, f"the next step of {ticket['name']}")


def expect_active(board: dict, name: str | None) -> None:
    """The board names the ticket of the session saved as open; none while no ticket's session is."""
    _expect_equal(board["active"] and board["active"]["name"], name, "the active ticket")


def expect_backlog(board: dict, titles: list[str]) -> None:
    """The Backlog column shows these backlog items, in order."""
    _expect_equal([item["title"] for item in column_in(board, "Backlog")["items"]], titles, "the Backlog")


def expect_session_folder(sessions: Path, folder: str, name: str) -> None:
    """The session's folder, session.json and all, sits in folder under .sessions/ (empty for the open sessions)."""
    if not (sessions / folder / name / "session.json").is_file():
        raise AssertionError(f"expected the folder of {name} in .sessions/{folder}")


def expect_commit_count(project: Any, branch: str, count: int) -> None:
    """The branch holds count commits: the fixture's own, and one more for each commit the board made on it."""
    _expect_equal(project.git("rev-list", "--count", branch), str(count), f"the commits on {branch}")


def _expect_equal(actual: Any, expected: Any, subject: str) -> None:
    if actual != expected:
        raise AssertionError(f"expected {subject} to be {expected!r}, but it is {actual!r}")


def expect_refused(refusal: Exception | None, kind: type[Exception], message: str) -> None:
    """The operation was refused with kind, saying message."""
    if not isinstance(refusal, kind) or str(refusal) != message:
        raise AssertionError(f"expected {kind.__name__}: {message}, but got {type(refusal).__name__}: {refusal}")


def _scenario_group(scenario: Scenario, tier: Tier, place: int) -> type:
    """A group whose before_all runs the scenario's steps in order on one World. A Then cannot wait for the examples to
    run, since a later When changes what it sees, so each Then's outcome is kept and its example raises it."""
    outcomes: dict[int, BaseException | None] = {}
    thens = [index for index, step in enumerate(scenario.steps) if step.kind == THEN]

    def before_all(context: Any) -> None:
        world = tier.open()
        failed: BaseException | None = None
        try:
            for index, step in enumerate(scenario.steps):
                if failed is not None:
                    outcomes[index] = failed
                    continue
                try:
                    step.body(world)
                    outcomes[index] = None
                except BaseException as broken:  # noqa: BLE001 - kept for the example of this Then to raise
                    outcomes[index] = broken
                    if step.kind != THEN:
                        failed = StepFailed(step, broken)
        finally:
            tier.close(world)

    members: dict[str, Any] = {"before_all": before_all}
    for order, index in enumerate(thens):
        step = scenario.steps[index]
        label = f"Then {step.text}" if order == 0 or scenario.steps[index - 1].kind != THEN else step.text
        members[_ordered(order, _slug(step.text))] = _example(label, outcomes, index)
    return _group(_ordered(place, f"Scenario_{_slug(scenario.name)}"), scenario.name, members)


class StepFailed(AssertionError):
    """A Given or When that broke, so every Then after it fails with it."""

    def __init__(self, step: Step, broken: BaseException) -> None:
        super().__init__(f"{step.kind} {step.text!r} failed: {type(broken).__name__}: {broken}")


def _example(label: str, outcomes: dict[int, BaseException | None], index: int) -> Callable[[Any], None]:
    def example(context: Any) -> None:
        outcome = outcomes.get(index)
        if outcome is not None:
            raise outcome

    example._example = True
    example._example_name = label if label.startswith("it ") else f"it {label}"
    example._tags = []
    example._pending = False
    return example


def _group(class_name: str, description: str, members: dict[str, Any]) -> type:
    group = type(class_name, (), dict(members))
    group._example_group = True
    group._example_name = description
    group._tags = []
    group._pending = False
    group._shared = False
    return group


def _ordered(place: int, name: str) -> str:
    return f"{place:0{ORDER_DIGITS}d}__{name}"


def _slug(value: str) -> str:
    return re.sub(r"[^0-9a-z]+", "_", value.strip().lower()).strip("_") or "step"
