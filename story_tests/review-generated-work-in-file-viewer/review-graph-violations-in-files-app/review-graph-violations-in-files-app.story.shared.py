"""Review Graph Violations In Files App: the shared scenarios the Python tiers replay.

Scenarios: story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/
review_graph_violations_in_files_app_story.test.md. Map: .context/story-map.md, (E) Review Graph Violations In Files App.

Steps reach the session only through the namespace a tier hands them (`world.Ticket`), so the domain spec and the cdd
tools spec replay the same steps. Only the scenarios built so far are here: Show Only Violating Nodes In Files App's
Choosing a rule keeps only the nodes that break it. Its Violations switch scenario waits for checkout-flow examples that
really break screen-story-budget, right-size-story-nodes and use-intention-revealing-names.
"""

from __future__ import annotations

from expects import equal, expect

from space.kanban.story_test import SharedStories
from space.session.graph_view_examples import STORY_MAP
from space.session.graph_view_rule_examples import VERB_NOUN_FORMAT, VIOLATIONS, names_of, seed_checkout_flow_with_violating_stories

shared_stories = SharedStories("Review Graph Violations In Files App")

LISTED = [STORY_MAP]


# --- Show Only Violating Nodes In Files App -----------------------------------------------------------------------


@shared_stories.scenario("Show Only Violating Nodes In Files App", "Choosing a rule keeps only the nodes that break it")
def _(s):
    @s.given("the Files app shows checkout-flow's violating nodes")
    def _(world):
        seed_checkout_flow_with_violating_stories(world)
        world.violating = names_of(world, "Story", LISTED, VIOLATIONS)

    @s.when("the Person chooses the rule verb-noun-format")
    def _(world):
        world.breaking = names_of(world, "Story", LISTED, {**VIOLATIONS, "rules": [VERB_NOUN_FORMAT]})

    @s.then("the graph view holds only Process Ticket Archive name and Handle Ticket Deletion name")
    def _(world):
        expect((world.breaking, "Delete Ticket" in world.violating)).to(equal(({"Process Ticket Archive", "Handle Ticket Deletion"}, False)))
