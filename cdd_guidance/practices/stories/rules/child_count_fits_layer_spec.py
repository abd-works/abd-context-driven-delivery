"""An epic or sub-epic is sized by its layer: 3-9 children under a node that holds sub-epics, 2-9 stories under a
sub-epic, 4-9 stories under a top epic. A two-layer map, whose epics each hold a few sub-epics of a few stories, passes."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.story_model import Epic, Story
from cdd_guidance.practices.stories.rules.story_map import ChildCountFitsLayer
from harness.graph.graph import Graph, Node, Source
from harness.graph.rule_context import RuleCheckContext
from harness.graph.rule_fixture import SchemaRuleRun
from harness.graph.saved_graph import NodeIdentity


def _epic(name: str, *, sub_epics: tuple = (), stories: int = 0) -> Epic:
    """An epic holding the given sub-epics and that many stories, each child knowing its parent."""
    epic = Epic(name, 1)
    for child in sub_epics:
        child.parent = epic
        epic.epics.append(child)
    for order in range(stories):
        story = Story(f"Submit Order {order + 1}", order + 1)
        story.parent = epic
        epic.stories.append(story)
    return epic


def _hits(epic: Epic) -> list[str]:
    """What child-count-fits-layer reports on the epic once its map facts are loaded, as validate runs it."""
    epic.load_map_facts()
    node_type = "SubEpic" if epic.is_sub_epic else "Epic"
    node = Node(Graph().practices.named("stories"), NodeIdentity(type=node_type, node_id=f"stories:{node_type}:{epic.name}", name=epic.name), Source(".", 1, 1))
    for fact in ("child_count", "child_label", "child_band", "child_target"):
        node.set_fact(fact, getattr(epic, fact))
    node.practice.reading.in_graph.hold(node)
    return SchemaRuleRun(ChildCountFitsLayer(), RuleCheckContext(node.practice)).node_hits(node)


with description("child count fits layer") as self:
    with context("with a top epic that holds three sub-epics of two or three stories"):
        with before.each:
            self.subs = (_epic("Place New Order", stories=3), _epic("Track Order Status", stories=2), _epic("Cancel Order", stories=2))
            self.epic = _epic("Manage Customer Orders", sub_epics=self.subs)

        with it("should pass the epic, since a node holding sub-epics groups 3-9 outcomes"):
            expect(_hits(self.epic)).to(equal([]))

        with it("should pass a sub-epic of two stories, since its sibling sub-epics carry the breadth"):
            expect(_hits(self.subs[1])).to(equal([]))

    with context("with a top epic that holds seven sub-epics"):
        with it("should pass the epic, since seven is inside 3-9 children"):
            epic = _epic("Onboard A Customer", sub_epics=tuple(_epic(f"Get Sim {n}", stories=2) for n in range(7)))
            expect(_hits(epic)).to(equal([]))

    with context("with a top epic that holds ten sub-epics"):
        with it("should flag the epic outside 3-9 children"):
            epic = _epic("Onboard A Customer", sub_epics=tuple(_epic(f"Get Sim {n}", stories=2) for n in range(10)))
            expect(_hits(epic)).to(equal(["epic 'Onboard A Customer': 10 children (target 3-9)"]))

    with context("with a top epic that holds two sub-epics"):
        with it("should flag the epic, since two sub-epics are too few to group"):
            epic = _epic("Onboard A Customer", sub_epics=(_epic("Authenticate User", stories=4), _epic("Get Sim", stories=2)))
            expect(_hits(epic)).to(equal(["epic 'Onboard A Customer': 2 children (target 3-9)"]))

    with context("with a top epic that holds one sub-epic"):
        with it("should flag the epic, since one sub-epic is no grouping"):
            epic = _epic("Onboard A Customer", sub_epics=(_epic("Authenticate User", stories=4),))
            expect(_hits(epic)).to(equal(["epic 'Onboard A Customer': 1 children (target 3-9)"]))

    with context("with a sub-epic that holds one story"):
        with it("should flag the sub-epic outside 2-9 stories"):
            sub = _epic("Load Customer", stories=1)
            _epic("Create Customer", sub_epics=(sub, _epic("Verify Account", stories=3)))
            expect(_hits(sub)).to(equal(["sub-epic 'Load Customer': 1 stories (target 2-9)"]))

    with context("with a flat top epic"):
        with it("should pass four stories"):
            expect(_hits(_epic("Track Order Status", stories=4))).to(equal([]))

        with it("should flag three stories, which usually make a sub-epic of a neighbouring epic"):
            expect(_hits(_epic("Track Order Status", stories=3))).to(equal(["epic 'Track Order Status': 3 stories (target 4-9)"]))

        with it("should flag ten stories"):
            expect(_hits(_epic("Track Order Status", stories=10))).to(equal(["epic 'Track Order Status': 10 stories (target 4-9)"]))

    with context("with an epic whose children are not written yet"):
        with it("should pass"):
            expect(_hits(_epic("Track Order Status"))).to(equal([]))
