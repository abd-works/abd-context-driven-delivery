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
    CHECKOUT_FLOW_READING_NO_CODE,
    LISTED,
    STORY_MAP,
    RESTORE_TEST,
    SCENARIOS,
    SCENARIOS_GIVEN_LINE,
    SCENARIOS_SCENARIO_LINE,
    SCENARIOS_STORY_LINE,
    SCENARIOS_THEN_LINE,
    SCENARIOS_WHEN_LINE,
    KANBAN_MODEL,
    SHARED_STORY,
    STEP_LISTED,
    STEP_STORY,
    STEP_STORY_GIVEN_LINE,
    STEP_STORY_WHEN_LINE,
    TICKET_EXAMPLES,
    STORY_MAP_DELETE_LINE,
    STORY_TEST,
    TICKET_CODE,
    WITH_LISTED,
    WITH_STORY,
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

    @s.then("the Stories tree holds Delete Ticket, and none of the old story map's epics")
    def _(world):
        expect(("Delete Ticket" in world.names, "Run Old Layout" in world.names)).to(equal((True, False)))


@shared_stories.scenario("Switch Files App To Graph View", "The Stories tree holds a story listed only by its story test in code")
def _(s):
    @s.given("the Files app lists only the code formats, so of the Stories files only Delete Ticket's and Restore Ticket's story tests")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, [STORY_TEST, RESTORE_TEST])

    @s.then("the Stories tree holds Manage Tickets, Remove Tickets and Delete Ticket from the story test's folders, with its scenario")
    def _(world):
        expect(world.names).to(contain("Manage Tickets", "Remove Tickets", "Delete Ticket", "a ticket is deleted"))

    @s.then("it holds Restore Ticket too, which has a story test but is not on the markdown map yet")
    def _(world):
        expect("Restore Ticket" in world.names).to(equal(True))


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


@shared_stories.scenario("Switch Files App To Graph View", "The Stories tree holds a story's scenarios listed in markdown")
def _(s):
    @s.given("the Files app lists only the markdown formats: checkout-flow's story map and Delete Ticket's scenarios")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, [STORY_MAP, SCENARIOS])

    @s.then("Delete Ticket holds its scenario and its steps from the scenarios file")
    def _(world):
        expect(world.names).to(contain("Delete Ticket", "a ticket is deleted", "given a ticket on the board"))


@shared_stories.scenario("Switch Files App To Graph View", "A story listed only by its story map holds its scenarios")
def _(s):
    @s.given("the Files app lists only checkout-flow's story map, .context/story-map.md")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.but_("not Delete Ticket's scenarios file under story_tests")
    def _(world):
        pass

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, [STORY_MAP])

    @s.then("Delete Ticket holds its scenario and its steps, read from its scenarios file")
    def _(world):
        expect(world.names).to(contain("Delete Ticket", "a ticket is deleted", "given a ticket on the board"))


# --- Filter Graph Like The File List ------------------------------------------------------------------------------


@shared_stories.scenario("Filter Graph Like The File List", "The Changed button keeps only the nodes of changed files")
def _(s):
    @s.given("the Files app shows checkout-flow's graph with Clean Engineering on")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person narrows the files to those the branch changed, so the file bar lists only ticket.py of the code")
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


def shared_story_lines(world, name: str) -> list[tuple[str, int, int]]:
    ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, name, [SHARED_STORY]), paths=[SHARED_STORY]))
    return [(found["path"], found["start_line"], found["end_line"]) for found in ranges]


@shared_stories.scenario("Open Several Files From Graph Nodes", "Selecting a scenario in a Python story test spans its whole function")
def _(s):
    @s.given("the Files app shows the Stories tree of Remove Tickets' shared story test")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the scenario a ticket is deleted")
    def _(world):
        world.lines = shared_story_lines(world, "a ticket is deleted")

    @s.then("the shared story test opens at lines 7 to 15, its decorator through the last line of its function")
    def _(world):
        expect(world.lines).to(equal([(SHARED_STORY, 7, 15)]))


@shared_stories.scenario("Open Several Files From Graph Nodes", "Selecting a step in a Python story test spans its whole function")
def _(s):
    @s.given("the Files app shows the Stories tree of Remove Tickets' shared story test")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the Given step a ticket on the board")
    def _(world):
        world.lines = shared_story_lines(world, "given a ticket on the board")

    @s.then("the shared story test opens at lines 9 to 11, the Given's decorator through its function")
    def _(world):
        expect(world.lines).to(equal([(SHARED_STORY, 9, 11)]))


@shared_stories.scenario("Open Several Files From Graph Nodes", "Selecting a story in a Python story test spans its scenarios")
def _(s):
    @s.given("the Files app shows the Stories tree of Remove Tickets' shared story test")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the story Delete Ticket")
    def _(world):
        world.lines = shared_story_lines(world, "Delete Ticket")

    @s.then("the shared story test opens at lines 7 to 22, its first scenario through its last")
    def _(world):
        expect(world.lines).to(equal([(SHARED_STORY, 7, 22)]))


@shared_stories.scenario("Open Several Files From Graph Nodes", "Selecting a step opens its scenarios file at the step's line")
def _(s):
    @s.given("the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the Given step a ticket on the board")
    def _(world):
        listed = [STORY_MAP, SCENARIOS]
        ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, "given a ticket on the board", listed), paths=listed))
        world.lines = [(found["path"], found["start_line"]) for found in ranges]

    @s.then("the scenarios file opens at the Given's own line")
    def _(world):
        expect(world.lines).to(equal([(SCENARIOS, SCENARIOS_GIVEN_LINE)]))


# --- Open Story Scenarios Across Files ----------------------------------------------------------------------------


def story_map_lines(world, name: str) -> list[tuple[str, int, int]]:
    listed = [STORY_MAP, SCENARIOS]
    ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, name, listed), paths=listed))
    return [(found["path"], found["start_line"], found["end_line"]) for found in ranges]


@shared_stories.scenario("Open Story Scenarios Across Files", "Selecting a story map story opens its scenarios file too")
def _(s):
    @s.given("the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the story Delete Ticket")
    def _(world):
        world.lines = story_map_lines(world, "Delete Ticket")

    @s.then("the story map opens at Delete Ticket's line, and the scenarios file below it from Delete Ticket's heading through its scenario")
    def _(world):
        expect(world.lines).to(equal([(STORY_MAP, STORY_MAP_DELETE_LINE, STORY_MAP_DELETE_LINE), (SCENARIOS, SCENARIOS_STORY_LINE, SCENARIOS_THEN_LINE)]))


@shared_stories.scenario("Open Story Scenarios Across Files", "Selecting a story map sub-epic opens its scenarios file from its heading")
def _(s):
    @s.given("the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the sub-epic Remove Tickets")
    def _(world):
        world.lines = story_map_lines(world, "Remove Tickets")

    @s.then("the scenarios file opens from its Sub-epic: Remove Tickets heading, on line 1, through its last scenario")
    def _(world):
        scenarios = [lines for lines in world.lines if lines[0] == SCENARIOS]
        expect(scenarios).to(equal([(SCENARIOS, 1, SCENARIOS_THEN_LINE)]))


@shared_stories.scenario("Open Story Scenarios Across Files", "Selecting a markdown scenario spans its heading through its last step")
def _(s):
    @s.given("the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the scenario a ticket is deleted")
    def _(world):
        world.lines = story_map_lines(world, "a ticket is deleted")

    @s.then("the scenarios file opens at lines 5 to 9, its heading through its Then")
    def _(world):
        expect(world.lines).to(equal([(SCENARIOS, SCENARIOS_SCENARIO_LINE, SCENARIOS_THEN_LINE)]))


# --- Open Linked Sections In Place --------------------------------------------------------------------------------

BROKEN_LINKS = "notes/broken-links.md"
BROKEN_LINKS_TEXT = (
    "# Notes\n"
    "\n"
    "See the [missing heading](../space/kanban/.context/kanban-model.md#no-such-heading).\n"
    "See the [missing file](../nowhere/gone.md#board).\n"
)


def callouts_of(world, path: str) -> list[tuple[int, str, int, int]]:
    """Each callout session.file answers for path: the line it sits on, and the file and lines of the section it opens."""
    found = world.data_of(session_of(world).file(path=path))["callouts"]
    return [(callout["line"], callout["section"]["path"], callout["section"]["start_line"], callout["section"]["end_line"]) for callout in found]


@shared_stories.scenario("Open Linked Sections In Place", "A story map story opens its scenarios in place")
def _(s):
    @s.given("checkout-flow's story map links Delete Ticket to the Story: Delete Ticket heading of its scenarios")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person views the story map")
    def _(world):
        world.callouts = callouts_of(world, STORY_MAP)

    @s.then("line 5 carries a callout to the scenarios file's lines 3 to 9, holding Delete Ticket and its scenario")
    def _(world):
        expect(world.callouts).to(equal([(STORY_MAP_DELETE_LINE, SCENARIOS, SCENARIOS_STORY_LINE, SCENARIOS_THEN_LINE)]))


@shared_stories.scenario("Open Linked Sections In Place", "A scenario's domain term opens its class in the markdown model")
def _(s):
    @s.given("Delete Ticket's Then links the board to the Board section of the kanban's class model")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person views the scenarios file")
    def _(world):
        world.callouts = callouts_of(world, SCENARIOS)

    @s.then("line 9 carries a callout to the model's lines 3 to 5, the Board section")
    def _(world):
        expect(world.callouts).to(equal([(SCENARIOS_THEN_LINE, KANBAN_MODEL, 3, 5)]))


@shared_stories.scenario("Open Linked Sections In Place", "A link to a heading no file holds carries no callout")
def _(s):
    @s.given("a markdown file links to a heading its target does not have, and to a file not there")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(BROKEN_LINKS, BROKEN_LINKS_TEXT)

    @s.when("the Person views it")
    def _(world):
        world.callouts = callouts_of(world, BROKEN_LINKS)

    @s.then("neither line carries a callout")
    def _(world):
        expect(world.callouts).to(equal([]))


# --- Follow Story Steps To Code -----------------------------------------------------------------------------------


def related_under(world, step: str, group: str, paths: list[str] = STEP_LISTED) -> list[str]:
    """The names in step's relationship group, in the trees of the files at paths, each branch opened as the page opens
    it."""
    session = session_of(world)
    opened = world.data_of(session.graph_branch(node_id=node_id_of(world, step, paths), paths=paths))
    held = next((child for child in opened["children"] if child["name"] == group), None)
    if held is None:
        return []
    branch = world.data_of(session.graph_branch(node_id=held["node_id"], paths=paths))
    return [child["name"] for child in branch["children"] if "children_left_out" in child]


@shared_stories.scenario("Follow Story Steps To Code", "A step in a Python story test invokes the functions and operations it calls")
def _(s):
    @s.given("the Files app shows the Stories tree of Delete Ticket's Python shared story test, whose Given calls the function ticket_on_board and whose When calls Ticket.delete")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person opens the Given and the When")
    def _(world):
        world.given = related_under(world, "given a ticket on the board", "invokes")
        world.when = related_under(world, "when the Person deletes it", "invokes")

    @s.then("the Given shows an invokes group holding ticket_on_board")
    def _(world):
        expect(world.given).to(equal(["ticket_on_board"]))

    @s.then("the When shows an invokes group holding delete")
    def _(world):
        expect(world.when).to(equal(["delete"]))


@shared_stories.scenario("Follow Story Steps To Code", "A story test's callouts sit on the step that invokes them")
def _(s):
    @s.given("the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose docstring names the class Ticket")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        session_of(world).graph_trees(paths=STEP_LISTED)

    @s.when("the Person views the shared story test")
    def _(world):
        world.steps = world.data_of(session_of(world).file(path=STEP_STORY, rules=True))["steps"]

    @s.then("the When's line carries a callout to Ticket.delete, and the Given's line a callout to ticket_on_board, but the docstring's line carries none")
    def _(world):
        found = [(step["line"], [target["name"] for target in step["invokes"]], [target["file"] for target in step["invokes"]]) for step in world.steps]
        expect(found).to(equal([(STEP_STORY_GIVEN_LINE, ["ticket_on_board"], [TICKET_EXAMPLES]), (STEP_STORY_WHEN_LINE, ["delete"], [TICKET_CODE])]))


@shared_stories.scenario("Follow Story Steps To Code", "A step in a with-block Python story test invokes the operation its block calls")
def _(s):
    @s.given("the Files app shows the Stories tree of Archive Ticket's Python story test, whose `with when` block calls Ticket.delete on an object it holds")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person opens the When")
    def _(world):
        world.when = related_under(world, "when the Person archives it", "invokes", WITH_LISTED)

    @s.then("the When shows an invokes group holding delete")
    def _(world):
        expect(world.when).to(equal(["delete"]))


@shared_stories.scenario("Follow Story Steps To Code", "A step's invokes are not judged while the session reads no Clean Engineering")
def _(s):
    @s.given("checkout-flow works with Clean Engineering off, and Archive Ticket's Python story test's `with when` block calls Ticket.delete")
    def _(world):
        seed_checkout_flow_with_graph_files(world, CHECKOUT_FLOW_READING_NO_CODE)

    @s.when("the Person views the story test with the rules the whole working copy breaks")
    def _(world):
        world.violations = world.data_of(session_of(world).file(path=WITH_STORY, cross_file=True))["violations"]

    @s.then("the When carries no conforms-to-schema finding, since no operation is read for it to invoke")
    def _(world):
        found = [found["violation"]["message"] for found in world.violations if found["violation"]["rule"] == "conforms-to-schema"]
        expect([message for message in found if "'when the Person archives it'" in message]).to(equal([]))


@shared_stories.scenario("Open Story Scenarios Across Files", "Selecting a markdown step spans its own line, whatever its prose holds")
def _(s):
    @s.given("the Files app shows the Stories tree of checkout-flow's story map and Delete Ticket's scenarios")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the When step the Person deletes the ticket's card")
    def _(world):
        world.lines = story_map_lines(world, "when the Person deletes the ticket's card")

    @s.then("the scenarios file opens at the When's own line alone")
    def _(world):
        expect(world.lines).to(equal([(SCENARIOS, SCENARIOS_WHEN_LINE, SCENARIOS_WHEN_LINE)]))
