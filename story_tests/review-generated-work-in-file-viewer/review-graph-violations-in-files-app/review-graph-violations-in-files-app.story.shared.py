"""Review Graph Violations In Files App: the shared scenarios the Python tiers replay.

Scenarios: story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/
review_graph_violations_in_files_app_story.test.md. Map: .context/story-map.md, (E) Review Graph Violations In Files App.

Steps reach the session only through the namespace a tier hands them (`world.Ticket`), so the domain spec and the cdd
tools spec replay the same steps. Only the scenarios built so far are here: Show Only Violating Nodes In Files App's
two scenarios.
"""

from __future__ import annotations

from expects import equal, expect

from space.kanban.story_test import SharedStories
from space.kanban.graph_view_examples import STORY_MAP
from space.kanban.graph_view_rule_examples import (
    LISTED_WITH_TICKET,
    STORY_NAME_CAPTURES_SYSTEM_MECHANIC,
    VIOLATIONS,
    entries_in,
    names_of,
    seed_checkout_flow_with_violating_stories,
    seed_checkout_flow_with_violations_in_two_practices,
)

shared_stories = SharedStories("Review Graph Violations In Files App")

LISTED = [STORY_MAP]


# --- Show Only Violating Nodes In Files App -----------------------------------------------------------------------


@shared_stories.scenario("Show Only Violating Nodes In Files App", "The Violations switch keeps only nodes that break a rule")
def _(s):
    @s.given("the Files app shows checkout-flow's graph with Stories and Clean Engineering on")
    def _(world):
        seed_checkout_flow_with_violations_in_two_practices(world)

    @s.when("the Person turns on Violations")
    def _(world):
        world.violating = {node_type: names_of(world, node_type, LISTED_WITH_TICKET, VIOLATIONS) for node_type in ("Story", "Parameter")}

    @s.then("the graph view holds only the nodes of Process Ticket Archive name, Handle Ticket Deletion name and Activate Ticket name")
    def _(world):
        expect(world.violating).to(equal({"Story": {"Process Ticket Archive", "Handle Ticket Deletion"}, "Parameter": {"x"}}))

    # A rule that requires a judge lists a node as a candidate, as story-name-captures-system-mechanic lists the two
    # stories, so a kept node's rules are those it breaks or is a candidate for, and never one it passes.
    @s.and_("each of them lists only the rules it breaks or is a candidate for")
    def _(world):
        kept = [entry for entry in entries_in(world, LISTED_WITH_TICKET, VIOLATIONS) if entry["type"] in ("Story", "Parameter")]
        statuses = {rule["status"] for entry in kept for rules in entry["children"] if rules.get("type") == "rules" for rule in rules["children"]}
        expect((bool(statuses), statuses - {"violating", "candidate"})).to(equal((True, set())))


@shared_stories.scenario("Show Only Violating Nodes In Files App", "Choosing a rule keeps only the nodes that break it")
def _(s):
    @s.given("the Files app shows checkout-flow's violating nodes")
    def _(world):
        seed_checkout_flow_with_violating_stories(world)
        world.violating = names_of(world, "Story", LISTED, VIOLATIONS)

    @s.when("the Person chooses the rule story-name-captures-system-mechanic")
    def _(world):
        world.breaking = names_of(world, "Story", LISTED, {**VIOLATIONS, "rules": [STORY_NAME_CAPTURES_SYSTEM_MECHANIC]})

    @s.then("the graph view holds only Process Ticket Archive name and Handle Ticket Deletion name")
    def _(world):
        expect((world.breaking, "Delete Ticket" in world.violating)).to(equal(({"Process Ticket Archive", "Handle Ticket Deletion"}, False)))
