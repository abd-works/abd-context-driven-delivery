"""Switch Files App Between Files And Graph: the shared scenarios the Python tiers replay.

Scenarios: story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/
switch_files_app_between_files_and_graph_story.test.md. Map: .context/story-map.md, (E) Switch Files App
Between Files And Graph.

Steps reach the session only through the namespace a tier hands them (`world.Ticket`), so the domain spec and the cdd
tools spec replay the same steps. A file is named from the project, as the Files app names it.

Covered by the Files app's own specs (`harness/files_app/app/files/files-graph.spec.ts`), not here, because only the page
shows them: the file bar's Graph button, each tree drawn collapsed, the open file kept open, switching back to the files,
the practice toggles and the chat bar's dots narrowing the graph, files opening below the first, folds opening around the
selected nodes, and the page scrolling to them. The Thens below check what the session answers the page for each: the
practice trees of the files listed, and the lines a selected node covers in each file.
"""

from __future__ import annotations

from expects import contain, equal, expect

from space.kanban.story_test import SharedStories
from space.session.graph_view_examples import (
    BOARD_CODE,
    LISTED,
    STORY_MAP,
    STORY_TEST,
    TICKET_CODE,
    node_id_of,
    seed_checkout_flow_with_graph_files,
    session_of,
)

shared_stories = SharedStories("Switch Files App Between Files And Graph")

def names_in(world, paths: list[str]) -> list[str]:
    """Every node's name in the trees answered for paths, each branch opened as the page opens it."""
    session = session_of(world)
    return [name for tree in world.data_of(session.graph_trees(paths=paths)) for name in opened_names(world, tree, paths)]


def opened_names(world, entry: dict, paths: list[str]) -> list[str]:
    if entry["children_left_out"]:
        entry = world.data_of(session_of(world).graph_branch(node_id=entry["node_id"], paths=paths)) or entry
    below = [child for child in entry["children"] if "children_left_out" in child]
    return [entry["name"], *(name for child in below for name in opened_names(world, child, paths))]


def lines_of(world, name: str) -> list[tuple[str, int, int]]:
    ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, name, LISTED), paths=LISTED))
    return [(found["path"], found["start_line"], found["end_line"]) for found in ranges]


# --- Switch Files App To Graph View -------------------------------------------------------------------------------


@shared_stories.scenario("Switch Files App To Graph View", "The graph view shows the practice trees of the listed files")
def _(s):
    @s.given("the Files app lists checkout-flow's Stories and Clean Engineering files")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, LISTED)

    @s.then("the file bar shows the Stories and Clean Engineering practice trees")
    def _(world):
        expect(world.names).to(contain("stories", "clean_engineering", "Delete Ticket", "Ticket", "Board"))


@shared_stories.scenario("Switch Files App To Graph View", "The Stories tree holds the project's story map")
def _(s):
    @s.given("the project's .context holds checkout-flow's story map, and an old story map is left in harness/.context/stories")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, [STORY_MAP])

    @s.then("the Stories tree holds Delete Ticket, but none of the old story map's epics")
    def _(world):
        expect(("Delete Ticket" in world.names, "Run Old Layout" in world.names)).to(equal((True, False)))


@shared_stories.scenario("Switch Files App To Graph View", "The Stories tree holds a story listed only by its story test in code")
def _(s):
    @s.given("the Files app lists only the code formats, so of the Stories files only Delete Ticket's story test")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, [STORY_TEST])

    @s.then("the Stories tree holds Manage Tickets, Remove Tickets and Delete Ticket, with the scenario its story test holds")
    def _(world):
        expect(world.names).to(contain("Manage Tickets", "Remove Tickets", "Delete Ticket", "a ticket is deleted"))


@shared_stories.scenario("Switch Files App To Graph View", "A story map listed in markdown and drawio is read once, from its markdown")
def _(s):
    @s.given("the Files app lists checkout-flow's story map in markdown and in drawio")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(".context/story-map.drawio", world.project.root.joinpath(STORY_MAP).read_text(encoding="utf-8").replace("Manage Tickets", "Manage Tickets In Drawio"))

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, [STORY_MAP, ".context/story-map.drawio"])

    @s.then("the Stories tree holds Delete Ticket once, from the markdown")
    def _(world):
        expect((world.names.count("Delete Ticket"), "Manage Tickets In Drawio" in world.names)).to(equal((1, False)))


# --- Filter Graph Like The File List ------------------------------------------------------------------------------


@shared_stories.scenario("Filter Graph Like The File List", "The Changed button keeps only the nodes of changed files")
def _(s):
    @s.given("the Files app shows checkout-flow's graph with Clean Engineering on")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person turns the Changed button on, so the file bar lists only ticket.py of the code")
    def _(world):
        world.names = names_in(world, [TICKET_CODE])

    @s.then("the Clean Engineering tree holds Ticket and its operations, but not Board")
    def _(world):
        expect(("Ticket" in world.names, "activate" in world.names, "Board" in world.names)).to(equal((True, True, False)))


# --- Open Several Files From Graph Nodes --------------------------------------------------------------------------


@shared_stories.scenario("Open Several Files From Graph Nodes", "Selecting a node opens its file")
def _(s):
    @s.given("the Files app shows checkout-flow's graph")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects Ticket.activate")
    def _(world):
        world.lines = lines_of(world, "activate")

    @s.then("ticket.py opens at the lines Ticket.activate covers")
    def _(world):
        expect(world.lines).to(equal([(TICKET_CODE, 2, 3)]))


@shared_stories.scenario("Open Several Files From Graph Nodes", "Selecting a folder's node opens every listed file below it")
def _(s):
    @s.given("the Files app shows checkout-flow's graph")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the Clean Engineering root, which no file's lines hold")
    def _(world):
        world.lines = lines_of(world, "clean_engineering")

    @s.then("ticket.py and board.py both open, board.py at the lines Board covers")
    def _(world):
        expect(sorted(world.lines)).to(equal([(BOARD_CODE, 1, 3), (TICKET_CODE, 1, 9)]))
