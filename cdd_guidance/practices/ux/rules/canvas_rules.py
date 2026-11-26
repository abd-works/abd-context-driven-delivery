"""The story canvas rules, at the mockup fidelity: a UX map's screens ported to the Claude Design canvas beside it
(``<ux root>/design-canvas/``) are prototypes that follow the scenario and step the story explorer hands them, with a
state for every scenario they show, and the explorer lists each scenario once. Each rule reads the canvas version the
map's own file leads to (*PortedCanvas*); a map with no canvas beside it has no screens ported yet, so these rules find
nothing on it."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.stories.model.story_tree import KEY_SEPARATOR, StoryTree
from cdd_guidance.practices.ux.model.claude_design.canvas_explorer import CanvasExplorer
from cdd_guidance.practices.ux.model.claude_design.screen_artboard import PortedCanvas

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

# The props the story explorer hands a screen, and the ones the screen must read to follow it.
EXPLORER_PROPS = ("story", "scenario", "step", "go")
FOLLOWED_PROPS = ("scenario", "step")


def ported_canvas(node: Node) -> Optional[PortedCanvas]:
    """The canvas version node's UX map is ported to, found from the file the map was read from."""
    source = node.source
    if not source.root or not source.file:
        return None
    return PortedCanvas.of_map_file(Path(source.root, source.file), Path(source.root))


class ScreenIsAPrototype(PracticeGraphRule):
    """A screen on the canvas is the prototype's own screen ported to an artboard, not a screenshot of it."""

    slug = "screen-is-a-prototype"
    node_types = ("Screen",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        canvas = ported_canvas(node)
        if canvas is None:
            return []
        prototype, image = getattr(node, "prototype", ""), getattr(node, "image", "")
        if not prototype:
            return [Finding(node, f"Screen {node.name!r} shows only its screenshot ({image}) on the canvas; it has no prototype artboard.")] if image else []
        artboard = canvas.artboard(prototype)
        if artboard is None:
            return [Finding(node, f"Screen {node.name!r} names the prototype {prototype}, which the canvas version does not hold.")]
        if artboard.shows_only_a_picture:
            return [Finding(node, f"Screen {node.name!r} is only a screenshot on the canvas ({prototype}); port the prototype's own markup and logic.")]
        return []


class ScreenFollowsScenario(PracticeGraphRule):
    """A screen's artboard declares the story, scenario, step and go props the explorer hands it, and its logic reads
    the scenario and the step."""

    slug = "screen-follows-scenario"
    node_types = ("Screen",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        canvas = ported_canvas(node)
        artboard = canvas.artboard(getattr(node, "prototype", "")) if canvas is not None else None
        if artboard is None:
            return []
        undeclared = [prop for prop in EXPLORER_PROPS if prop not in artboard.declared_props]
        unread = [f"props.{prop}" for prop in FOLLOWED_PROPS if not artboard.reads_prop(prop)]
        problems = ([f"does not declare {', '.join(undeclared)} in data-props"] if undeclared else []) + (
            [f"its logic never reads {', '.join(unread)}"] if unread else [])
        if not problems:
            return []
        return [Finding(node, f"Screen {node.name!r} ({node.prototype}) {'; '.join(problems)}, so it cannot show the scenario and step the explorer selects.")]


class EveryScenarioHasAState(PracticeGraphRule):
    """Every scenario of the stories a screen shows has a state on the screen's artboard, or a fixture the screen loads
    from the canvas's fixtures bundle. A scenario another screen shows is that screen's to load."""

    slug = "every-scenario-has-a-state"
    node_types = ("Screen",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        canvas = ported_canvas(node)
        artboard = canvas.artboard(getattr(node, "prototype", "")) if canvas is not None else None
        if artboard is None:
            return []
        stateless = [key for key, name in self._scenarios(node, context)
                     if not artboard.names(name) and not (artboard.loads_fixtures and canvas.fixtures_name(name))]
        if not stateless:
            return []
        return [Finding(node, f"Screen {node.name!r} has no state or fixture for: {', '.join(stateless)}.")]

    @staticmethod
    def _scenarios(node: Node, context: RuleCheckContext) -> list[tuple[str, str]]:
        """Each scenario the screen shows, by its key (``Story › Scenario``) and its own name: those it shows itself,
        and those of the stories it shows that no other screen shows."""
        shown: dict[str, str] = {StoryTree.key_of(scenario): scenario.name for scenario in context.targets(node, "showsScenarios")}
        for story in context.targets(node, "shows"):
            for scenario in getattr(story, "scenarios", []) or []:
                elsewhere = [screen for screen in context.targets(scenario, "shownOn") if screen is not node]
                if not elsewhere:
                    shown.setdefault(f"{story.name}{KEY_SEPARATOR}{scenario.name}", scenario.name)
        return list(shown.items())


class ScenarioListedOnce(PracticeGraphRule):
    """The canvas's story explorer lists each scenario once under its story."""

    slug = "scenario-listed-once"
    node_types = ("UxMap",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        canvas = ported_canvas(node)
        explorer = CanvasExplorer(canvas.project) if canvas is not None else None
        if explorer is None or not explorer.exists():
            return []
        findings = []
        for story, scenarios in explorer.stories():
            for name, times in Counter(scenario.name for scenario in scenarios).items():
                if times > 1:
                    findings.append(Finding(node, f"The story explorer lists {story}{KEY_SEPARATOR}{name} {times} times."))
        return findings
