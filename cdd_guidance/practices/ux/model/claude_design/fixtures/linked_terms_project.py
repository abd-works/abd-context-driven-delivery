"""The project the story explorer's class-card specs render: a domain model holding Cart and Line, and a story map whose
Choose Plan steps link cart and line to them, as a scenarios file read from ``stories/`` links them, one step linking
cart to Line. Its Given and When are realized; its Thens are not. The project sits in a folder of its own, which goes
when the project does."""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from cdd_guidance.practices.source_code.call_graph import CallGraph
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownStep
from cdd_guidance.practices.stories.model.story_map import Epic, Scenario, StepType, Story, StoryMap
from cdd_guidance.practices.stories.model.story_map_files import source_at
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap

DOMAIN_MODEL = """# Domain model

### Cart <<Aggregate Root>> <<Entity>>

A cart holds the lines a Customer picks.

---

+ add(line)
\t+ total

### Line <<Entity>>

A line on a plan.
"""

CART_CARD = "domain/domain-model.md#cart-aggregate-root-entity"
LINE_CARD = "domain/domain-model.md#line-entity"
_CART = f"../{CART_CARD}"
_LINE = f"../{LINE_CARD}"
_STEP_LINE = re.compile(r"\*(\w+)\* (.*)$")


class LinkedTermsProject:
    """The project's folder, its story map, and the story explorer a canvas renders from it."""

    def __init__(self) -> None:
        self._folder = tempfile.TemporaryDirectory(prefix="cdd-linked-terms-")
        self.root = Path(self._folder.name).resolve()
        (self.root / "domain").mkdir()
        (self.root / "domain" / "domain-model.md").write_text(DOMAIN_MODEL, encoding="utf-8")

    def remove(self) -> None:
        self._folder.cleanup()

    def story_map(self) -> StoryMap:
        story_map = StoryMap()
        epic, sub_epic, story = Epic("Onboard A Customer", 1), Epic("Select Plan", 1), Story("Choose Plan", 1)
        scenario = Scenario("See the plan catalog", 1)
        scenario.steps = [
            self._step(f"*Given* the Customer has a ++[cart]({_CART})++", StepType.GIVEN, 1, "Cart.create()"),
            self._step("*When* the Customer opens My Paradise", StepType.WHEN, 2, "Catalog.open()\n  -> Plan.list()"),
            self._step(f"*Then* the ++[cart]({_CART})++ holds a ++[line]({_LINE})++ and no carts", StepType.THEN, 3),
            self._step(f"*Then* the ++[cart]({_LINE})++ is still empty", StepType.THEN, 4),
        ]
        story.scenarios.append(scenario)
        sub_epic.stories.append(story)
        epic.epics.append(sub_epic)
        story_map.epics.append(epic)
        return story_map

    def explorer(self) -> str:
        """The explorer page, its screen showing Choose Plan and naming none of its steps, so each action and its
        outcome is a step group: the Given and the When, then the two Thens."""
        screen = Screen("Plan catalog", 1)
        screen.prototype = "plan-catalog.dc.html"
        screen.show_story("Choose Plan")
        ux_map = UxMap.create()
        ux_map.append_screen(screen)
        files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=ux_map, files_root=self.root)).render(self.story_map()))
        return files["project/screens/explorer.dc.html"]

    def _step(self, line: str, phase: StepType, order: int, realization: str = "") -> MarkdownStep:
        """A step read from line of a scenarios file in stories/, as the scenarios reader reads one."""
        keyword, text = _STEP_LINE.match(line).groups()
        step = MarkdownStep(text, phase, order)
        step.keyword = keyword
        step.source = source_at("stories/choose-plan.md", order)
        step.read_from(line)
        if realization:
            step.call_graph = CallGraph().read(realization)
        return step
