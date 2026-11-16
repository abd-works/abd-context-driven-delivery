"""Explore Graph In Files App: the shared scenarios the Python tiers replay.

Scenarios: story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/
explore_graph_in_files_app_story.test.md. Map: .context/story-map.md, (E) Explore Graph In Files App.

Steps reach the session only through the namespace a tier hands them (`world.Ticket`), so the domain spec and the cdd
tools spec replay the same steps. Only the scenarios built so far are here: Expand Practice Tree In Files App and Open
Calls Across Files In Files App. Covered by the Files app's own specs (`harness/files_app/app/files/files-graph.spec.ts`),
not here, because only the page shows them: each node's kind mark, the load steps while the graph reads, and a call
opened in place in the source view. The Thens below check what the session answers the page for each.
"""

from __future__ import annotations

from expects import equal, expect

from space.kanban.story_test import SharedStories
from space.session.graph_view_examples import BOARD_CODE, LISTED, node_id_of, seed_checkout_flow_with_graph_files, session_of

shared_stories = SharedStories("Explore Graph In Files App")


# --- Expand Practice Tree In Files App ----------------------------------------------------------------------------


@shared_stories.scenario("Expand Practice Tree In Files App", "Opening a node shows one level of its children")
def _(s):
    @s.given("the Files app shows checkout-flow's graph with the Clean Engineering tree collapsed")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person opens Ticket")
    def _(world):
        world.ticket = world.data_of(session_of(world).graph_branch(node_id=node_id_of(world, "Ticket", LISTED), paths=LISTED))

    @s.then("Ticket shows its operations, but their own children stay hidden until they are opened")
    def _(world):
        operations = [child for child in world.ticket["children"] if "children_left_out" in child]
        shown_below = [grandchild for child in operations for grandchild in child["children"] if "children_left_out" in grandchild]
        expect(([child["name"] for child in operations], shown_below)).to(equal((["activate", "close", "delete"], [])))


# --- Follow Relationships Under Node In Files App -----------------------------------------------------------------


@shared_stories.scenario("Follow Relationships Under Node In Files App", "An operation lists the operations it invokes")
def _(s):
    @s.given("the Files app shows checkout-flow's graph with Ticket opened")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person opens Ticket.delete")
    def _(world):
        world.delete = world.data_of(session_of(world).graph_branch(node_id=node_id_of(world, "delete", LISTED), paths=LISTED))

    @s.then("Ticket.delete shows an invokes group holding Board.reread")
    def _(world):
        invokes = next(child for child in world.delete["children"] if child["name"] == "invokes")
        opened = world.data_of(session_of(world).graph_branch(node_id=invokes["node_id"], paths=LISTED))
        expect([child["name"] for child in opened["children"] if "children_left_out" in child]).to(equal(["reread"]))


@shared_stories.scenario("Follow Relationships Under Node In Files App", "Selecting a related node opens its file beside the open one")
def _(s):
    @s.given("Ticket.delete is selected and ticket.py is open")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        session = session_of(world)
        delete = world.data_of(session.graph_branch(node_id=node_id_of(world, "delete", LISTED), paths=LISTED))
        invokes = next(child for child in delete["children"] if child["name"] == "invokes")
        world.invoked = world.data_of(session.graph_branch(node_id=invokes["node_id"], paths=LISTED))["children"][0]

    @s.when("the Person selects Board.reread under Ticket.delete's invokes")
    def _(world):
        ranges = world.data_of(session_of(world).graph_node_ranges(node_id=world.invoked["node_id"], paths=LISTED))
        world.lines = [(found["path"], found["start_line"], found["end_line"]) for found in ranges]

    @s.then("board.py opens beside ticket.py, at Board.reread")
    def _(world):
        expect(world.lines).to(equal([(BOARD_CODE, 2, 3)]))


# --- Open Calls Across Files In Files App -------------------------------------------------------------------------


@shared_stories.scenario("Open Calls Across Files In Files App", "A call to an operation in another file opens in place")
def _(s):
    @s.given("the Files app shows checkout-flow's graph and ticket.py is open")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        session_of(world).graph_trees(paths=LISTED)

    @s.when("the source view reads the members it opens calls from")
    def _(world):
        world.members = {member["name"]: member for member in world.data_of(session_of(world).graph_members())}

    @s.then("Board.reread, from board.py, is among them with its lines, so the call to it in Ticket.delete opens in place")
    def _(world):
        reread = world.members["reread"]
        expect((reread["file"].endswith("board.py"), reread["owner"], "delete" in world.members)).to(equal((True, "Board", True)))


@shared_stories.scenario("Open Calls Across Files In Files App", "Calls open in place only once the graph is read")
def _(s):
    @s.given("the Files app lists checkout-flow's files and the graph view was never shown")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person opens ticket.py")
    def _(world):
        world.members = world.data_of(session_of(world).graph_members())

    @s.then("its calls show as written, with no fold to open them")
    def _(world):
        expect(world.members).to(equal([]))
