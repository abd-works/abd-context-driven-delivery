"""The walk of a story canvas's screens: before a canvas version is published, each screen the story explorer plays is
rendered at the scenarios it shows, and every value the scenarios' steps name is looked for on it.

For each scenario the explorer lists with a prototype screen, the screen's artboard is rendered once for each step group
the explorer lists for that scenario, with the ``story``, ``scenario``, ``step``, ``stepIndex`` and ``stepKind`` props the explorer
hands it when the reader picks that group. A scenario with one action has two groups, its Givens and When, then its
Thens; a scenario with two actions has three, so the outcome between them is walked too. The values each step names (*StepValues*: quoted text,
dollar amounts, codes written in capitals with digits, phone numbers, and numbers of four or more digits) are looked
for in the text the screen shows at that render (*ShownText*). The report (*ScreenWalkReport*) says per step what was
found and what is missing, and names each miss as ``Story › Scenario › value``, which is what
``CanvasVersion.publish_at`` refuses to publish over unless the person accepts it.

The screens are rendered whole in Node by ``screen_render.cjs`` beside this file: the scripts each artboard loads, its
DCLogic built with the props and mounted, its x-dc template drawn with the components it imports from the global scope
and the artboards it dc-imports, through a small React that draws each component once. A screen that does not render
is reported as missing at that scenario, with the error.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, List, Mapping, Optional, Sequence

from cdd_guidance.practices.stories.model.story_tree import KEY_SEPARATOR
from cdd_guidance.practices.ux.model.claude_design.canvas_explorer import CanvasExplorer, ExplorerScenario

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_map import Scenario, StoryMap
    from harness.design_canvas.versions import CanvasVersion

_RENDERER = Path(__file__).with_name("screen_render.cjs")
# What the miss of a screen that did not render names in place of a value.
UNRENDERED = "(screen did not render)"
# The name a prototype takes beside the screens while the walk draws it next to the production view standing in for it.
BESIDE_SUFFIX = ".beside.dc.html"
# The most lines of text a difference shows for each side.
_DIFFERENCE_LINES = 6
# What the miss of an action that leaves its screen as it was names before the action.
STILL = "(screen stays as it was after)"


class ScreenWalkUnavailable(RuntimeError):
    """The walk renders screens in Node, and Node is not on the PATH or the renderer stopped."""


@dataclass(frozen=True)
class StepValue:
    """One value a step names: as the step writes it (``written``), and the text a screen shows it with (``shown``)."""

    written: str
    kind: str

    @property
    def shown(self) -> str:
        return self.written[1:-1] if self.kind == "quoted" else self.written


# The marks a story map's steps carry around terms and actors, which no screen shows.
_MARKUP = (re.compile(r"\*\*|\+\+|`"), re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])"))
# Each kind of value, in the order they are taken: a value inside another is taken once, as the outer one.
_KINDS = (
    ("quoted", re.compile(r'"[^"\n]+"|“[^”\n]+”')),
    ("amount", re.compile(r"\$\d{1,3}(?:,\d{3})+(?:\.\d+)?|\$\d+(?:\.\d+)?")),
    ("phone", re.compile(r"\+?\(?\d[\d ().-]{5,}\d")),
    ("code", re.compile(r"\b(?=[A-Z0-9]*[A-Z])(?=[A-Z0-9]*\d)[A-Z0-9]{3,}\b")),
    ("number", re.compile(r"(?<![\d$.,])\d{4,}(?![\d])")),
)
_PHONE_DIGITS = 7


def _digits(text: str) -> str:
    return re.sub(r"\D", "", text)


class StepValues:
    """The values a step's text names, in the order it names them."""

    def __init__(self, text: str) -> None:
        plain = _MARKUP[1].sub(r"\1", _MARKUP[0].sub("", text))
        self.values = self._taken(plain)

    @staticmethod
    def _taken(text: str) -> List[StepValue]:
        found: list[tuple[int, StepValue]] = []
        open_text = text
        for kind, pattern in _KINDS:
            for match in pattern.finditer(open_text):
                written = match.group(0).strip()
                if kind == "phone" and len(_digits(written)) < _PHONE_DIGITS:
                    continue
                if kind == "quoted" and written.startswith("“"):
                    written = f'"{written[1:-1]}"'
                found.append((match.start(), StepValue(written, kind)))
                open_text = open_text[:match.start()] + " " * (match.end() - match.start()) + open_text[match.end():]
        unique: dict[str, StepValue] = {}
        for _, value in sorted(found, key=lambda place: place[0]):
            unique.setdefault(value.written, value)
        return list(unique.values())


def _normal(text: str) -> str:
    """text as values are compared in it: lower case, one kind of quote and dash, and single spaces."""
    text = text.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[−–—]", "-", text)
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)
    # A screen that draws the currency sign in an element of its own shows "$ 0"; it reads as "$0".
    text = re.sub(r"\$\s+(?=\d)", "$", text)
    return re.sub(r"\s+", " ", text).strip()


def _loose(text: str) -> str:
    """text with its spaces and punctuation left out, so a quoted line the screen draws across several elements, or
    with other separators, still reads as the line the step quotes."""
    return re.sub(r"[\s·,.:;!?()'\"…\-]", "", _normal(text))


class ShownText:
    """The text a screen shows at one render: its words, the values in its fields, and its aria-labels."""

    def __init__(self, text: str) -> None:
        self.text = text
        self._normal = _normal(text)
        self._loose = _loose(text)

    def shows(self, value: StepValue) -> bool:
        if value.kind == "phone":
            return self._shows_phone(_digits(value.shown))
        if value.kind == "amount":
            return re.search(rf"{re.escape(_normal(value.shown))}(?![\d])", self._normal) is not None
        if value.kind == "number":
            return re.search(rf"(?<![\d]){re.escape(value.shown)}(?![\d])", self._normal) is not None
        return _loose(value.shown) in self._loose

    def _shows_phone(self, digits: str) -> bool:
        for match in _KINDS[2][1].finditer(self.text):
            run = _digits(match.group(0))
            if len(run) >= _PHONE_DIGITS and (run == digits or digits.endswith(run) or run.endswith(digits)):
                return True
        return False


@dataclass(frozen=True)
class WalkedStep:
    """One step as the walk checked it: its story and scenario, the screen it was rendered on, the step's line, the
    values the screen showed and the ones it left out, and why the screen did not render when it did not."""

    story: str
    scenario: str
    screen: str
    step: str
    found: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    error: str = ""

    @property
    def place(self) -> str:
        return f"{self.story}{KEY_SEPARATOR}{self.scenario}"


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


class ScreenWalkReport:
    """What a walk found, step by step, each action whose screen stays as it was (*stills*), and each step where a
    production view shows other text than the prototype it stands in for (*differences*). Its ``misses`` are what
    ``CanvasVersion.publish_at`` refuses to publish over; the differences are for the person to read."""

    def __init__(self, steps: Sequence[WalkedStep], stills: Sequence["StillAction"] = (), differences: Sequence["ScreenDifference"] = ()) -> None:
        self.steps = list(steps)
        self.stills = list(stills)
        self.differences = list(differences)

    @property
    def misses(self) -> List[str]:
        """Each value a screen leaves out, once, as ``Story › Scenario › value``; a screen that did not render is one
        miss at its scenario; and each action that leaves its screen as it was, as ``Story › Scenario › STILL: When …``."""
        found: dict[str, None] = {}
        for step in self.steps:
            for value in ([UNRENDERED] if step.error else step.missing):
                found.setdefault(f"{step.place}{KEY_SEPARATOR}{value}", None)
        for still in self.stills:
            found.setdefault(still.miss, None)
        return list(found)

    def markdown(self) -> str:
        """The report as a markdown table: one line for each step walked."""
        lines = ["| Story › Scenario | Screen | Step | Found | Missing |", "| --- | --- | --- | --- | --- |"]
        for step in self.steps:
            missing = f"{UNRENDERED[:-1]}: {step.error})" if step.error else ", ".join(step.missing)
            lines.append(f"| {_cell(step.place)} | {_cell(step.screen)} | {_cell(step.step)} | {_cell(', '.join(step.found))} | {_cell(missing)} |")
        if self.stills:
            lines += ["", "Actions that leave the screen as it was, so a reader who presses on the screen sees nothing happen:", "",
                      "| Story › Scenario | Screen | Action |", "| --- | --- | --- |"]
            lines += [f"| {_cell(still.place)} | {_cell(still.screen)} | {_cell(still.step)} |" for still in self.stills]
        if self.differences:
            lines += ["", "Production views beside the prototype they stand in for: the text each shows that the other does not "
                          "(the walk draws text, not layout, so layout is not compared):", "",
                      "| Story › Scenario | Screen | Step | Only in production | Only in the prototype |", "| --- | --- | --- | --- | --- |"]
            lines += [f"| {_cell(each.place)} | {_cell(each.screen)} | {_cell(each.step)} | {_cell(each.production_text)} | {_cell(each.prototype_text)} |"
                      for each in self.differences]
        return "\n".join(lines) + "\n"

    def write(self, path: Path) -> Path:
        """Save the report's table at path."""
        path.write_text(self.markdown(), encoding="utf-8")
        return path


@dataclass(frozen=True)
class _Stop:
    """One render of a scenario's screen: the step group the explorer hands it, at its position in the scenario, and the
    steps whose values it shows. *played* is the scenario as the screen loads it, an outline's example row by its own
    name."""

    scenario: ExplorerScenario
    artboard: Optional[Path]
    lines: List[str]
    index: int
    played: str = ""

    @property
    def name(self) -> str:
        return self.played or self.scenario.name

    @property
    def props(self) -> dict:
        """The props the explorer hands the screen when the reader picks this step group."""
        return {"story": self.scenario.story, "scenario": self.name, "step": "\n".join(self.lines), "stepIndex": self.index,
                "stepKind": self.scenario.kind_of(self.index)}


class StoryCanvasWalk:
    """The walk of one canvas version's screens: what each screen the explorer plays shows at its scenarios' steps."""

    def __init__(self, version: "CanvasVersion") -> None:
        self.version = version
        self.explorer = CanvasExplorer(version.folder / "project")

    def walk(self, story_map: "StoryMap", beside: Optional[Mapping[str, str]] = None) -> ScreenWalkReport:
        """Render each scenario's screen at every step group the explorer lists for it, as the reader picks them, and
        report the values its steps name that each render shows and leaves out. *beside* holds, by screen slug, the
        artboard of the prototype a production view stands in for; each such screen is drawn as both at every step,
        and the text they show differently is reported."""
        stories = {story.name: story for story in story_map.descendants.stories()}
        stops: list[_Stop] = []
        unmatched: list[WalkedStep] = []
        for scenario in self.explorer.scenarios():
            artboard = self.explorer.artboard_of(scenario)
            if artboard is None:
                continue
            if self._scenario_in(stories, scenario) is None:
                unmatched.append(WalkedStep(scenario.story, scenario.name, scenario.screen, "", error="the story map holds no scenario of this name under this story"))
                continue
            stops.extend(_Stop(scenario, artboard, group.split("\n"), index, played.name)
                         for played in scenario.played() for index, group in enumerate(played.groups) if group)
        rendered = self._rendered(stops)
        steps = [step for stop, text in zip(stops, rendered) for step in _checked(stop, text)]
        return ScreenWalkReport([*unmatched, *steps], _still_actions(stops, rendered), self._differences(stops, rendered, beside or {}))

    def _differences(self, stops: Sequence[_Stop], rendered: Sequence[dict], beside: Mapping[str, str]) -> List["ScreenDifference"]:
        """Each step where a production view and the prototype it stands in for show other text. The prototype is
        written beside the screens only while it is drawn (``<slug>.beside.dc.html``), so the canvas never holds it."""
        compared = [(stop, result) for stop, result in zip(stops, rendered) if stop.scenario.screen in beside and "error" not in result]
        if not compared:
            return []
        folder = self.version.folder / "project" / "screens"
        written = []
        try:
            for slug in {stop.scenario.screen for stop, _ in compared}:
                path = folder / f"{slug}{BESIDE_SUFFIX}"
                path.write_text(beside[slug], encoding="utf-8")
                written.append(path)
            prototype = _render([{"artboard": str((folder / f"{stop.scenario.screen}{BESIDE_SUFFIX}").resolve()), "props": stop.props}
                                 for stop, _ in compared])
        finally:
            for path in written:
                path.unlink(missing_ok=True)
        found = (ScreenDifference.of(stop, result, drawn) for (stop, result), drawn in zip(compared, prototype))
        return [difference for difference in found if difference is not None]

    @staticmethod
    def _scenario_in(stories: dict, scenario: ExplorerScenario) -> Optional["Scenario"]:
        story = stories.get(scenario.story)
        return next((own for own in story.scenarios if own.name == scenario.name), None) if story is not None else None

    def _rendered(self, stops: Sequence[_Stop]) -> List[dict]:
        """Each stop's render: the text its screen shows, or why it did not render."""
        jobs = []
        for stop in stops:
            if not stop.artboard.is_file():
                jobs.append(None)
                continue
            jobs.append({"artboard": str(stop.artboard.resolve()), "props": stop.props})
        results = iter(_render([job for job in jobs if job is not None]))
        return [next(results) if job is not None else {"error": f"the canvas holds no screens/{stop.scenario.screen}.dc.html"}
                for job, stop in zip(jobs, stops)]


def _render(jobs: List[dict]) -> List[dict]:
    """Each job rendered by screen_render.cjs: {"text": ...} or {"error": ...}."""
    if not jobs:
        return []
    node = shutil.which("node")
    if node is None:
        raise ScreenWalkUnavailable("The walk renders screens in Node, and node is not on the PATH; install Node.js and walk again.")
    answer = subprocess.run([node, str(_RENDERER)], input=json.dumps({"jobs": jobs}), capture_output=True, text=True, encoding="utf-8")
    if answer.returncode != 0:
        raise ScreenWalkUnavailable(f"The screen renderer stopped: {answer.stderr.strip()}")
    return json.loads(answer.stdout)


def _checked(stop: _Stop, rendered: dict) -> List[WalkedStep]:
    """Each line of stop checked against what its screen showed."""
    scenario = stop.scenario
    if "error" in rendered:
        return [WalkedStep(scenario.story, stop.name, scenario.screen, stop.lines[-1].strip(), error=rendered["error"])]
    shown = ShownText(rendered["text"])
    steps = []
    for line in stop.lines:
        values = StepValues(line).values
        steps.append(WalkedStep(scenario.story, stop.name, scenario.screen, line.strip(),
                                [value.written for value in values if shown.shows(value)],
                                [value.written for value in values if not shown.shows(value)]))
    return steps


@dataclass(frozen=True)
class StillAction:
    """An action a scenario takes (a When, with its And lines) after which its screen shows what it showed before: the
    scenario on its screen, and the action's first line."""

    story: str
    scenario: str
    screen: str
    step: str

    @property
    def place(self) -> str:
        return f"{self.story}{KEY_SEPARATOR}{self.scenario}"

    @property
    def miss(self) -> str:
        return f"{self.place}{KEY_SEPARATOR}{STILL}: {self.step}"


_KEYWORD = re.compile(r"^\s*(Given|When|Then|And|But)\b")


def _actions(groups: Sequence[List[str]]) -> List[tuple]:
    """Each action of a scenario's step groups, as (its first line, the group holding it, whether its group ends on it):
    a run of When lines, an And or But taking the phase of the line it continues."""
    found: list[tuple] = []
    for index, lines in enumerate(groups):
        phase, opened = "", None
        for place, line in enumerate(lines):
            keyword = (_KEYWORD.match(line) or [None, ""])[1]
            phase = phase if keyword in ("And", "But", "") else keyword.lower()
            if phase == "when" and opened is None:
                opened = line.strip()
            if phase != "when" and opened is not None:
                found.append((opened, index, False))
                opened = None
        if opened is not None:
            found.append((opened, index, True))
    return found


def _still_actions(stops: Sequence["_Stop"], rendered: Sequence[dict]) -> List[StillAction]:
    """Each action, of each scenario a screen plays, after which the screen shows the same text as before it. An action
    that ends its step group is shown before on that group and after on the next; one inside a group, followed by its
    outcome, is shown after on that group and before on the one ahead of it. An action with no group on one side has no
    state of its own, so the screen stays as it was too. A screen that did not render is reported by the value check."""
    played: dict[tuple, list] = {}
    for stop, result in zip(stops, rendered):
        played.setdefault((stop.scenario.story, stop.name, stop.scenario.screen), []).append((stop.index, stop.lines, result))
    stills: List[StillAction] = []
    for (story, scenario, screen), shown in played.items():
        by_index = {index: result for index, _, result in shown}
        if any("error" in result for result in by_index.values()):
            continue
        groups = [lines for _, lines, _ in sorted(shown, key=lambda each: each[0])]
        indexes = sorted(by_index)
        for step, at, ends in _actions(groups):
            index = indexes[at]
            before, after = (index, index + 1) if ends else (index - 1, index)
            if before not in by_index or after not in by_index or by_index[before]["text"] == by_index[after]["text"]:
                stills.append(StillAction(story, scenario, screen, step))
    return stills


@dataclass(frozen=True)
class ScreenDifference:
    """One step where a production view shows other text than the prototype it stands in for: the lines only the
    production view shows, the lines only the prototype shows, or why the prototype did not draw."""

    story: str
    scenario: str
    screen: str
    step: str
    only_in_production: tuple = ()
    only_in_prototype: tuple = ()
    error: str = ""

    @property
    def place(self) -> str:
        return f"{self.story}{KEY_SEPARATOR}{self.scenario}"

    @property
    def production_text(self) -> str:
        return " / ".join(self.only_in_production[:_DIFFERENCE_LINES]) + (" …" if len(self.only_in_production) > _DIFFERENCE_LINES else "")

    @property
    def prototype_text(self) -> str:
        if self.error:
            return f"(the prototype did not draw: {self.error})"
        return " / ".join(self.only_in_prototype[:_DIFFERENCE_LINES]) + (" …" if len(self.only_in_prototype) > _DIFFERENCE_LINES else "")

    @property
    def line(self) -> str:
        """The difference as one line of the render summary."""
        return f"{self.place} on {self.screen}, {self.step}: production only [{self.production_text}]; prototype only [{self.prototype_text}]"

    @classmethod
    def of(cls, stop: "_Stop", production: dict, prototype: dict) -> Optional["ScreenDifference"]:
        """How the two drawings of stop's screen differ; none when they show the same text."""
        step = stop.lines[-1].strip()
        if "error" in prototype:
            return cls(stop.scenario.story, stop.name, stop.scenario.screen, step, error=str(prototype["error"]))
        shown, drawn = _text_lines(production["text"]), _text_lines(prototype["text"])
        only_production = tuple(line for line in shown if line not in drawn)
        only_prototype = tuple(line for line in drawn if line not in shown)
        if not only_production and not only_prototype:
            return None
        return cls(stop.scenario.story, stop.name, stop.scenario.screen, step, only_production, only_prototype)


def _text_lines(text: str) -> List[str]:
    """The lines a screen shows, each with its spaces made single, blank ones left out, each once."""
    found: dict[str, None] = {}
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            found.setdefault(line, None)
    return list(found)
