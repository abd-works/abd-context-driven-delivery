"""A story's prototype screen on the story canvas, built on the fixture bar (``fixture_screen.py``).

The screen loads the scenario the explorer picks through the bar, hands its markup the domain objects the scenario
bound under one named input (``domain_input``, such as ``cart``), and places the markup at the position its step group
keeps (which page, whether a sheet or dialog is open). Every value the markup shows comes through that input; positions
hold only where the screen is. A press on a button or link before the scenario's last outcome moves the explorer on to
the next Then.

The markup has one of three sources, each a small class with the same two parts, its head and its body:

- *WrittenMarkup* — written from scratch for the project, the main path;
- *AppPageMarkup* — taken from a page of an existing app the project can reach, its body and stylesheets;
- *PortedCanvasMarkup* — ported from another Claude Design canvas, drawn as that canvas's component through
  ``dc-import`` with the named input and each position setting as its attributes.

See ``story_canvas.md`` beside this file, *Prototype screens*."""

from __future__ import annotations

import json
import posixpath
import re
from dataclasses import dataclass, field

from pathlib import Path

from cdd_guidance.practices.ux.model.claude_design.fixture_screen import FixtureScreen, ScenarioSource
from cdd_guidance.practices.ux.model.claude_design.screen_files import ScreenFiles

# Screens live in project/screens/; the fixtures bundle in project/fixtures/.
FIXTURES_SCRIPT = '<script src="../fixtures/canvas-fixtures.js"></script>'


def _attribute_name(setting: str) -> str:
    """A setting's name as an HTML attribute: ``cartOpen`` is ``cart-open``."""
    return re.sub(r"([A-Z])", lambda letter: "-" + letter.group(1).lower(), setting)


class ScreenMarkup:
    """Where a screen's markup comes from: the head it loads (stylesheets, scripts) and the body it draws, given the
    named input the domain objects arrive under and the position settings its step groups keep. In the body,
    ``{{ <input> }}`` is the bound domain object and ``{{ position.<setting> }}`` the step group's position."""

    head: str
    files: ScreenFiles = ScreenFiles()

    def body_for(self, domain_input: str, position_settings: list[str]) -> str:
        raise NotImplementedError

    def copy_files(self, project: Path) -> list[Path]:
        """Copy the files the markup needs (*files*) into a canvas version's project folder."""
        return self.files.copy_into(project)


@dataclass(frozen=True)
class WrittenMarkup(ScreenMarkup):
    """Markup written from scratch for the project: its *head* and its *body*, which reads the named input and the
    position itself."""

    head: str
    body: str

    def body_for(self, domain_input: str, position_settings: list[str]) -> str:
        return self.body


_STYLESHEET_LINK = re.compile(r"<link\b[^>]*\brel=[\"']stylesheet[\"'][^>]*>", re.IGNORECASE)
_HREF = re.compile(r"\bhref=[\"']([^\"']+)[\"']", re.IGNORECASE)
_STYLE = re.compile(r"<style\b[^>]*>[\s\S]*?</style>", re.IGNORECASE)
_SCRIPT = re.compile(r"<script\b[^>]*>[\s\S]*?</script>\s*", re.IGNORECASE)
_BODY = re.compile(r"<body\b[^>]*>([\s\S]*?)</body>", re.IGNORECASE)


@dataclass(frozen=True)
class AppPageMarkup(ScreenMarkup):
    """Markup taken from a page of an existing app: the *page*'s HTML, its body drawn without the app's scripts (the
    canvas runs the screen's own logic, not the app's), its inline styles kept, and its linked stylesheets linked from
    *stylesheet_folder*, the canvas folder its *files* copy them into (``stylesheets`` names them)."""

    page: str
    stylesheet_folder: str = "../styles"
    files: ScreenFiles = field(default_factory=ScreenFiles)

    @property
    def stylesheets(self) -> tuple[str, ...]:
        """The page's linked stylesheets, as the page links them."""
        return tuple(href.group(1) for link in _STYLESHEET_LINK.findall(self.page) for href in [_HREF.search(link)] if href)

    @property
    def head(self) -> str:
        links = [f'<link rel="stylesheet" href="{self.stylesheet_folder}/{posixpath.basename(href)}">' for href in self.stylesheets]
        return "\n".join(links + _STYLE.findall(self.page))

    def body_for(self, domain_input: str, position_settings: list[str]) -> str:
        body = _BODY.search(self.page)
        return _SCRIPT.sub("", body.group(1) if body else self.page).strip()


@dataclass(frozen=True)
class PortedCanvasMarkup(ScreenMarkup):
    """Markup ported from another Claude Design canvas: its *component* (the ``.dc.html`` its *files* copy beside the
    screens, with the files it loads) drawn through ``dc-import``, with *attributes* it always takes (such as its
    theme), the named input, and each position setting; *head* loads the scripts and stylesheets the component needs;
    *size* is its hint size."""

    component: str
    head: str = ""
    attributes: dict[str, str] = field(default_factory=dict)
    size: str = "100%,100%"
    files: ScreenFiles = field(default_factory=ScreenFiles)

    def copy_files(self, project: Path) -> list[Path]:
        """Copy the files the component loads into a canvas version's project folder, and the component itself beside
        the screens as ``screens/<component>.dc.html``, where ``dc-import`` finds it."""
        return self.files.copy_into(project, f"screens/{self.component}.dc.html")

    def body_for(self, domain_input: str, position_settings: list[str]) -> str:
        fixed = [f'{name}="{value}"' for name, value in self.attributes.items()]
        given = [f'{domain_input}="{{{{ {domain_input} }}}}"'] + [f'{_attribute_name(setting)}="{{{{ position.{setting} }}}}"' for setting in position_settings]
        return f'<dc-import name="{self.component}" {" ".join(fixed + given)} hint-size="{self.size}"></dc-import>'


# The screen's own methods: what it takes from the fixture, the position for the step group on show, and the press that
# moves the explorer on. An outline's example row runs as '<outline>: <row>' and takes the outline's positions.
_OWN_METHODS = '''positions() {
return __POSITIONS__;
}
storyPosition() {
return __STORY_POSITION__;
}
fromFixture(repositories, scenario, examples, step, bindings) {
return { __INPUT__: (bindings && bindings.__INPUT__) || null };
}
paste(field) {
return {};
}
positionsFor(name) {
const positions = this.positions();
return positions[name] || positions[Object.keys(positions).filter((key) => name.indexOf(key + ': ') === 0).sort((a, b) => b.length - a.length)[0]] || null;
}
shownPosition() {
const groups = this.positionsFor(this.scenarioName());
if (!groups || !groups.length) return this.storyPosition();
return groups[Math.min(Math.max(0, Number(this.props.stepIndex) || 0), groups.length - 1)];
}
advance(event) {
const pressed = event && event.target && event.target.closest && event.target.closest('button, a');
const groups = this.positionsFor(this.scenarioName()) || [];
if (!pressed || !this.props.go || (Number(this.props.stepIndex) || 0) >= groups.length - 1) return;
setTimeout(() => this.props.go(this.storyName(), this.scenarioName(), 'Then'), 0);
}
'''


@dataclass(frozen=True)
class StoryScreen:
    """A story's prototype screen: *markup* from one of its sources, the scenario's bound domain objects under
    *domain_input*, and *positions*, for each scenario, one position per step group the explorer lists (an outline's
    rows take the outline's), with *story_position* for a scenario that keeps none. *path* is the screen's path for
    the dev seed paste; *artboard* its own canvas path, for the explorer's Edit link."""

    title: str
    story: str
    markup: ScreenMarkup
    domain_input: str
    positions: dict[str, list[dict]]
    story_position: dict = field(default_factory=dict)
    root_class: str = "story-screen"
    path: str = ""
    width: int = 390
    height: int = 844
    artboard: str = ""

    @property
    def position_settings(self) -> list[str]:
        """Every setting a position names, sorted."""
        return sorted({*self.story_position, *(setting for groups in self.positions.values() for group in groups for setting in group)})

    @property
    def html(self) -> str:
        if not self.domain_input.isidentifier():
            raise ValueError(f"the screen's named input must be a JavaScript name, not {self.domain_input!r}")
        body = (f'<div style="width: 100%; min-height: 100svh" onClickCapture="{{{{ advance }}}}">\n'
                f'{self.markup.body_for(self.domain_input, self.position_settings)}\n</div>')
        own = (_OWN_METHODS.replace("__POSITIONS__", json.dumps(self.positions)).replace("__STORY_POSITION__", json.dumps(self.story_position))
               .replace("__INPUT__", self.domain_input))
        return FixtureScreen(
            title=self.title,
            head="\n".join(part for part in (self.markup.head, FIXTURES_SCRIPT) if part),
            root_class=self.root_class,
            body=body,
            source=ScenarioSource(self.story, next(iter(self.positions), ""), self.path),
            own_methods=own,
            vals=f"{self.domain_input}: st.{self.domain_input} || null,\nposition: this.shownPosition(),\nadvance: (event) => this.advance(event)",
            width=self.width,
            height=self.height,
            artboard=self.artboard,
        ).html
