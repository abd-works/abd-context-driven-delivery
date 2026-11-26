"""Review Graph Violations In Files App: the shared scenarios the Python tiers replay.

Scenarios: story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/
review_graph_violations_in_files_app_story.test.md. Map: .context/story-map.md, (E) Review Graph Violations In Files App.

Steps reach the session only through the namespace a tier hands them (`world.Ticket`), so the domain spec and the cdd
tools spec replay the same steps. Only the scenarios built so far are here: Show Only Violating Nodes In Files App's
two scenarios and Fix Graph Violations From Files App's seven, whose fix is what session.graph_fix_prompt answers the page
to send the chat that opened it.
"""

from __future__ import annotations

from expects import equal, expect

from space.kanban.story_test import SharedStories
from space.kanban.graph_view_examples import CHECKOUT_FLOW, STORY_MAP, session_of
from space.kanban.session_board_examples import CHECKOUT_CHAT
from space.kanban.graph_view_rule_examples import (
    LISTED_WITH_TICKET,
    STORY_NAME_CAPTURES_SYSTEM_MECHANIC,
    VIOLATING_MAP_TEXT,
    VIOLATIONS,
    entries_in,
    names_of,
    seed_checkout_flow_with_violating_stories,
    seed_checkout_flow_with_violations_in_two_practices,
)

shared_stories = SharedStories("Review Graph Violations In Files App")

LISTED = [STORY_MAP]
# Interaction: the guidelines a fix of story-name-captures-system-mechanic names: the story map fidelity's, which state it.
STORY_MAP_GUIDELINES = "the stories-story-map guidelines"
# Interaction: the lines of the story map each violating story is read from, as the fix names them.
PROCESS_TICKET_ARCHIVE_LINES = f"{STORY_MAP}:5-5"
HANDLE_TICKET_DELETION_LINES = f"{STORY_MAP}:6-6"
# Interaction: the graph view's node filter keeping only the Stories practice's stories that break a rule, which leaves
# out Remove Tickets, an epic, and Ticket.activate's parameter x, a Clean Engineering node.
VIOLATING_STORIES_ONLY = {**VIOLATIONS, "practices": ["stories"], "types": ["Story"]}
# Seed: the story map once the chat has renamed Process Ticket Archive to Archive Ticket, a verb and a noun.
FIXED_MAP_TEXT = VIOLATING_MAP_TEXT.replace("Process Ticket Archive", "Archive Ticket")


def seed_violating_stories_opened_from_chat(world) -> None:
    """checkout-flow's violating stories, its ticket assigned checkout-chat, which has checked in."""
    seed_checkout_flow_with_violating_stories(world)
    world.Chat.load(CHECKOUT_CHAT).check_in(is_busy=False)
    world.Ticket.load(CHECKOUT_FLOW.name).assign_chat(chat=CHECKOUT_CHAT)


def fills_of(world) -> list[str]:
    """The fills sent to checkout-chat, newest first."""
    return [message["text"] for message in world.data_of(world.Chat.load(CHECKOUT_CHAT).messages()) if message["kind"] == "fill"]


def story_id(world, name: str) -> str:
    """The id of the story named name in the graph view of the story map."""
    return next(entry["node_id"] for entry in entries_in(world, LISTED, VIOLATIONS) if entry["type"] == "Story" and entry["name"] == name)


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


# --- Fix Graph Violations From Files App ---------------------------------------------------------------------------


@shared_stories.scenario("Fix Graph Violations From Files App", "Fixing one violation sends it alone to the chat")
def _(s):
    @s.given("the Files app shows checkout-flow's violating nodes, opened from the chat")
    def _(world):
        seed_checkout_flow_with_violating_stories(world)
        world.archive = story_id(world, "Process Ticket Archive")

    @s.when("the Person fixes Process Ticket Archive name")
    def _(world):
        world.fix = session_of(world).graph_fix_prompt(paths=LISTED, node_filter=VIOLATIONS, rule=STORY_NAME_CAPTURES_SYSTEM_MECHANIC, node_id=world.archive)

    @s.then("the chat that opened the page receives the fix for Process Ticket Archive name, with its node, file, lines, rule, excerpt and message")
    def _(world):
        named = [STORY_MAP_GUIDELINES, "Node: Process Ticket Archive (Story)", f"File: {PROCESS_TICKET_ARCHIVE_LINES}", f"Rule: {STORY_NAME_CAPTURES_SYSTEM_MECHANIC}", "Process Ticket Archive", "Violation: "]
        expect([part for part in named if part not in world.fix]).to(equal([]))

    @s.and_("Handle Ticket Deletion name stays unfixed")
    def _(world):
        expect("Handle Ticket Deletion" in world.fix).to(equal(False))


@shared_stories.scenario("Fix Graph Violations From Files App", "Fixing a rule sends every violation of it")
def _(s):
    @s.given("story-name-captures-system-mechanic holds Process Ticket Archive name and Handle Ticket Deletion name")
    def _(world):
        seed_checkout_flow_with_violating_stories(world)

    @s.when("the Person fixes the rule story-name-captures-system-mechanic")
    def _(world):
        world.fix = session_of(world).graph_fix_prompt(paths=LISTED, node_filter=VIOLATIONS, rule=STORY_NAME_CAPTURES_SYSTEM_MECHANIC)

    @s.then("the chat receives one fix for both story-name-captures-system-mechanic candidates")
    def _(world):
        expect((world.fix.startswith("Fix these 2 violations"), PROCESS_TICKET_ARCHIVE_LINES in world.fix, HANDLE_TICKET_DELETION_LINES in world.fix)).to(equal((True, True, True)))


@shared_stories.scenario("Fix Graph Violations From Files App", "Fixing all sends every violation the graph view shows")
def _(s):
    @s.given("the graph view shows only the Stories practice's 2 violations")
    def _(world):
        seed_checkout_flow_with_violations_in_two_practices(world)

    @s.when("the Person fixes all")
    def _(world):
        world.fix = session_of(world).graph_fix_prompt(paths=LISTED_WITH_TICKET, node_filter=VIOLATING_STORIES_ONLY)

    @s.then("the chat receives one fix for Process Ticket Archive name and Handle Ticket Deletion name")
    def _(world):
        expect((world.fix.startswith("Fix these 2 violations"), "Node: Process Ticket Archive (Story)" in world.fix, "Node: Handle Ticket Deletion (Story)" in world.fix)).to(equal((True, True, True)))

    @s.but_("not for the Clean Engineering violation, which the graph view does not show")
    def _(world):
        expect("(Parameter)" in world.fix).to(equal(False))


@shared_stories.scenario("Fix Graph Violations From Files App", "Fixing a rule in the file view comments on each place it breaks")
def _(s):
    @s.given("the Files app shows checkout-flow's story map with its rules, opened from checkout-chat, which has checked in")
    def _(world):
        seed_violating_stories_opened_from_chat(world)

    @s.when("the Person fixes the rule story-name-captures-system-mechanic in the file view")
    def _(world):
        session_of(world).file_comments.fix(path=STORY_MAP, chat=CHECKOUT_CHAT, rule=STORY_NAME_CAPTURES_SYSTEM_MECHANIC)

    @s.then("the checkout-chat queue holds one fill with a fix comment on Process Ticket Archive's line and one on Handle Ticket Deletion's line")
    def _(world):
        fills = fills_of(world)
        expect((len(fills), fills[0].count(f"Rule: {STORY_NAME_CAPTURES_SYSTEM_MECHANIC}"), fills[0].count(STORY_MAP_GUIDELINES), PROCESS_TICKET_ARCHIVE_LINES in fills[0], HANDLE_TICKET_DELETION_LINES in fills[0])).to(equal((1, 2, 2, True, True)))

    @s.and_("both comments show on the story map as sent")
    def _(world):
        expect([comment["state"] for comment in world.data_of(session_of(world).file_comments.on(path=STORY_MAP))]).to(equal(["sent", "sent"]))


@shared_stories.scenario("Fix Graph Violations From Files App", "Fixing one place in the file view sends it alone")
def _(s):
    @s.given("the Files app shows checkout-flow's story map with its rules, opened from checkout-chat, which has checked in")
    def _(world):
        seed_violating_stories_opened_from_chat(world)
        shown = world.data_of(session_of(world).file(path=STORY_MAP, rules=True))
        world.deletion = next(found for found in shown["violations"] if found["violation"]["rule"] == STORY_NAME_CAPTURES_SYSTEM_MECHANIC and found["range"]["start_line"] == 6)

    # Fix this one in the file view comments on the place's lines in the words Python wrote beside it, and sends it.
    @s.when("the Person fixes story-name-captures-system-mechanic on Handle Ticket Deletion's line in the file view")
    def _(world):
        comments = session_of(world).file_comments
        comments.add(path=STORY_MAP, start_line=6, end_line=6, text=world.deletion["correction_comment"])
        comments.send(anchor=world.data_of(comments.on(path=STORY_MAP))[-1]["anchor"], chat=CHECKOUT_CHAT)

    @s.then("the checkout-chat queue holds one fill with the fix comment on Handle Ticket Deletion's line alone")
    def _(world):
        fills = fills_of(world)
        expect((len(fills), fills[0].count(f"Rule: {STORY_NAME_CAPTURES_SYSTEM_MECHANIC}"), HANDLE_TICKET_DELETION_LINES in fills[0])).to(equal((1, 1, True)))


@shared_stories.scenario("Fix Graph Violations From Files App", "Fixing all in the file view sends every broken place")
def _(s):
    @s.given("the Files app shows checkout-flow's story map with its rules, opened from checkout-chat, which has checked in")
    def _(world):
        seed_violating_stories_opened_from_chat(world)
        world.broken = world.data_of(session_of(world).file(path=STORY_MAP, rules=True))["violations"]

    @s.when("the Person fixes all in the file view")
    def _(world):
        session_of(world).file_comments.fix(path=STORY_MAP, chat=CHECKOUT_CHAT)

    @s.then("the checkout-chat queue holds one fill with a fix comment on every place a rule breaks the story map")
    def _(world):
        fills = fills_of(world)
        expect((len(fills), [f"Rule: {found['violation']['rule']}" in fills[0] for found in world.broken].count(False), len(world.broken) > 2)).to(equal((1, 0, True)))


@shared_stories.scenario("Fix Graph Violations From Files App", "A fixed violation leaves the graph view once its file is read again")
def _(s):
    @s.given("the chat has worked on the fix for Process Ticket Archive name")
    def _(world):
        seed_checkout_flow_with_violating_stories(world)
        names_of(world, "Story", LISTED, VIOLATIONS)
        world.project.seed_file(STORY_MAP, FIXED_MAP_TEXT)

    @s.when("the Files app reads story-map.md again")
    def _(world):
        world.violating = names_of(world, "Story", LISTED, VIOLATIONS)

    @s.then("Process Ticket Archive name leaves the graph view")
    def _(world):
        expect("Process Ticket Archive" in world.violating).to(equal(False))

    @s.and_("Handle Ticket Deletion name stays")
    def _(world):
        expect(("Handle Ticket Deletion" in world.violating, "Handle Ticket Deletion" in session_of(world).graph_fix_prompt(paths=LISTED, node_filter=VIOLATIONS))).to(equal((True, True)))
