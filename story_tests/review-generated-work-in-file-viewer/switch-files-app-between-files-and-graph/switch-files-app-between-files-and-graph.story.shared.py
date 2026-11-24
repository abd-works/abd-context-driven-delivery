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
from space.kanban.graph_view_examples import (
    opened_entries,
    opened_entry_named,
    BOARD_CODE,
    CHECKOUT_FLOW_IN_SPACE,
    CHECKOUT_FLOW_READING_NO_CODE,
    EXAMPLES_SCENARIOS,
    EXAMPLES_SCENARIOS_SECOND_LINES,
    EXAMPLES_SCENARIOS_TEXT,
    LISTED,
    STORY_MAP,
    STORY_MAP_TEXT,
    STORY_MAP_WITH_REOPEN_TEXT,
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
    STEP_STORY_HELPER_WHEN,
    STEP_STORY_WHEN_CALL_LINE,
    STEP_STORY_WHEN_LINE,
    TICKET_EXAMPLES,
    TICKET_EXAMPLES_CONSTANT_LINE,
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
    return [entry["name"] for entry, _above in opened_entries(world, paths)]


def names_above(world, name: str, paths: list[str]) -> list[str]:
    """The names of the nodes above the node named name in the trees answered for paths, from its tree's root down."""
    return opened_entry_named(world, name, paths)[1]


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


@shared_stories.scenario("Switch Files App To Graph View", "A story map listed with a code story test keeps every epic of the map")
def _(s):
    @s.given("checkout-flow's story map holds Manage Tickets and Plan Releases, with Plan Releases' story Cut Release")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(STORY_MAP, STORY_MAP_TEXT + "(E) Plan Releases\n    (S) Person --> Cut Release\n")

    @s.and_("the Files app lists the story map with Delete Ticket's and Restore Ticket's story tests")
    def _(world):
        world.listed = [STORY_MAP, STORY_TEST, RESTORE_TEST]

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.names = names_in(world, world.listed)

    @s.then("the Stories tree holds Manage Tickets and Plan Releases, with Cut Release, read from the story map")
    def _(world):
        expect(world.names).to(contain("Manage Tickets", "Plan Releases", "Cut Release"))

    @s.then("Delete Ticket is the story map's story, holding the scenario its story test holds")
    def _(world):
        ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, "Delete Ticket", world.listed), paths=world.listed))
        expect([found["path"] for found in ranges]).to(equal([STORY_MAP, STORY_TEST]))

    @s.then("Restore Ticket, which only its story test holds, sits under Manage Tickets and Remove Tickets")
    def _(world):
        expect((names_above(world, "Restore Ticket", world.listed), world.names.count("Restore Ticket"))).to(equal((["stories", "Manage Tickets", "Remove Tickets"], 1)))


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


@shared_stories.scenario("Open Several Files From Graph Nodes", "Selecting a scenario opens only its own lines, not the examples module its example comes from")
def _(s):
    @s.given("the Files app shows the Stories tree of Delete Ticket's story test, whose Then observes CHECKOUT_TICKET from the examples module")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person selects the scenario a ticket on the board is deleted")
    def _(world):
        ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, "a ticket on the board is deleted", STEP_LISTED), paths=STEP_LISTED))
        world.lines = [(found["path"], found["start_line"], found["end_line"]) for found in ranges]

    @s.then("only the story test opens, at lines 7 to 19, its decorator through its Then")
    def _(world):
        expect(world.lines).to(equal([(STEP_STORY, 7, 19)]))


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


# Seed: the Files app listing the story map and Reopen Ticket's scenarios.
REOPEN_LISTED = [STORY_MAP, EXAMPLES_SCENARIOS]


@shared_stories.scenario("Open Story Scenarios Across Files", "Selecting a markdown story's second scenario spans its own lines, not the examples the story declares")
def _(s):
    @s.given("the Files app shows the Stories tree of Reopen Ticket's scenarios, whose Examples table both of its scenarios use")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(EXAMPLES_SCENARIOS, EXAMPLES_SCENARIOS_TEXT)
        world.project.seed_file(STORY_MAP, STORY_MAP_WITH_REOPEN_TEXT)

    @s.when("the Person selects the scenario Refuse a ticket still open")
    def _(world):
        ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, "Refuse a ticket still open", REOPEN_LISTED), paths=REOPEN_LISTED))
        world.lines = [(found["path"], found["start_line"], found["end_line"]) for found in ranges]

    @s.then("the scenarios file opens at lines 20 to 24, its heading through its Then, but not from the first scenario or the Examples table")
    def _(world):
        expect(world.lines).to(equal([(EXAMPLES_SCENARIOS, *EXAMPLES_SCENARIOS_SECOND_LINES)]))


# --- Open Linked Sections In Place --------------------------------------------------------------------------------

BROKEN_LINKS = "notes/broken-links.md"
BROKEN_LINKS_TEXT = (
    "# Notes\n"
    "\n"
    "See the [missing heading](../space/kanban/.context/kanban-model.md#no-such-heading).\n"
    "See the [missing file](../nowhere/gone.md#board).\n"
)

# A story map written with headings, as Stories writes it: Delete Ticket's heading, on line 3, holds a link.
HEADED_MAP = "notes/headed-map.md"
HEADED_MAP_TEXT = "# Story Map\n\n### (S) Person --> [Delete Ticket](../story_tests/manage-tickets/remove-tickets/remove_tickets_story.test.md)\n\nThe Person removes a ticket.\n\n### (S) Person --> Restore Ticket\n"
LINKS_TO_HEADED_MAP = "notes/links-to-headed-map.md"
LINKS_TO_HEADED_MAP_TEXT = "See the [story map](headed-map.md#s-person----delete-ticket) for where this story sits.\n"
# A story test in Python whose Given, on line 5, links a domain term, and whose When calls code that reads as a link.
LINKING_STORY_TEST = "story_tests/manage-tickets/remove-tickets/linking_story.test.py"
LINKING_STORY_TEST_TEXT = (
    "from story_test import given, scenario, story, when\n"
    "\n"
    'with story("Delete Ticket"):\n'
    '    with scenario("a ticket is deleted"):\n'
    '        with given("a [board](../../../space/kanban/.context/kanban-model.md#board) with a ticket"):\n'
    "            pass\n"
    '        with when("the Person deletes it"):\n'
    "            handlers[name](event)\n"
    "# Model: ../../../space/kanban/.context/kanban-model.md\n"
)
LINKING_STORY_TEST_GIVEN_LINE = 5
LINKING_STORY_TEST_MODEL_LINE = 9


def callouts_of(world, path: str) -> list[tuple[int, str, int, int]]:
    """Each callout session.file answers for path that opens something: the line it sits on, and the file and lines it opens."""
    found = world.data_of(session_of(world).file(path=path))["callouts"]
    return [(callout["line"], callout["section"]["path"], callout["section"]["start_line"], callout["section"]["end_line"]) for callout in found if not callout["missing"]]


def missing_of(world, path: str) -> list[tuple[int, str]]:
    """Each callout session.file answers for path whose link names something not there: its line and what it says is missing."""
    found = world.data_of(session_of(world).file(path=path))["callouts"]
    return [(callout["line"], callout["missing"]) for callout in found if callout["missing"]]


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
        expect([callout for callout in world.callouts if callout[0] == SCENARIOS_THEN_LINE]).to(equal([(SCENARIOS_THEN_LINE, KANBAN_MODEL, 3, 5)]))


@shared_stories.scenario("Open Linked Sections In Place", "A link to a whole file opens the file in place")
def _(s):
    @s.given("Delete Ticket's Given links the ticket to space/kanban/ticket.py, naming no heading")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person views the scenarios file")
    def _(world):
        world.callouts = callouts_of(world, SCENARIOS)

    @s.then("line 7 carries a callout to ticket.py's lines 1 to 9, the whole file")
    def _(world):
        expect([callout for callout in world.callouts if callout[0] == SCENARIOS_GIVEN_LINE]).to(equal([(SCENARIOS_GIVEN_LINE, TICKET_CODE, 1, 9)]))


@shared_stories.scenario("Open Linked Sections In Place", "A link to a heading that holds a link opens the heading's section")
def _(s):
    @s.given("a story map's heading for Delete Ticket holds a link to its scenarios, and a markdown file links to that heading")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(HEADED_MAP, HEADED_MAP_TEXT)
        world.project.seed_file(LINKS_TO_HEADED_MAP, LINKS_TO_HEADED_MAP_TEXT)

    @s.when("the Person views the linking file")
    def _(world):
        world.callouts = callouts_of(world, LINKS_TO_HEADED_MAP)

    @s.then("line 1 carries a callout to the map's lines 3 to 5, the heading's section")
    def _(world):
        expect(world.callouts).to(equal([(1, HEADED_MAP, 3, 5)]))


@shared_stories.scenario("Open Linked Sections In Place", "A link to a heading or a file not there says what is not there")
def _(s):
    @s.given("a markdown file links to a heading its target does not have, and to a file not there")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(BROKEN_LINKS, BROKEN_LINKS_TEXT)

    @s.when("the Person views it")
    def _(world):
        world.missing = missing_of(world, BROKEN_LINKS)

    @s.then("line 3's callout says the kanban model has no heading no-such-heading, and line 4's that nowhere/gone.md is not there")
    def _(world):
        expect(world.missing).to(equal([(3, f"{KANBAN_MODEL} has no heading #no-such-heading"), (4, "nowhere/gone.md is not there")]))


@shared_stories.scenario("Open Linked Sections In Place", "A story test in code opens the domain term a step links")
def _(s):
    @s.given("a Python story test's Given links the board to the Board section of the kanban's class model, its When calls handlers[name](event), and its last line reads # Model: with the model's path")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(LINKING_STORY_TEST, LINKING_STORY_TEST_TEXT)

    @s.when("the Person views the story test")
    def _(world):
        world.callouts = callouts_of(world, LINKING_STORY_TEST)
        world.missing = missing_of(world, LINKING_STORY_TEST)

    @s.then("the Given's line carries a callout to the model's lines 3 to 5, the Board section")
    def _(world):
        expect(world.callouts[0]).to(equal((LINKING_STORY_TEST_GIVEN_LINE, KANBAN_MODEL, 3, 5)))

    @s.and_("its `# Model:` line, which names the kanban's class model, carries a callout to the model's lines 1 to 9, the whole file")
    def _(world):
        expect(world.callouts[1:]).to(equal([(LINKING_STORY_TEST_MODEL_LINE, KANBAN_MODEL, 1, 9)]))

    @s.and_("the call's line carries none, since code that reads as a link to no file is not one")
    def _(world):
        expect(world.missing).to(equal([]))


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


@shared_stories.scenario("Follow Story Steps To Code", "A step in a Python story test invokes only the code it tests, never the test's own functions")
def _(s):
    @s.given("the Files app shows the Stories tree of Delete Ticket's Python shared story test, whose Given calls its seed ticket_on_board, whose When calls Ticket.delete, and whose Then calls the file's own helper ticket_left")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person opens the Given, the When and the Then")
    def _(world):
        world.given = related_under(world, "given a ticket on the board", "invokes")
        world.when = related_under(world, "when the Person deletes it", "invokes")
        world.then = related_under(world, "then the checkout ticket is gone", "invokes")

    @s.then("the When shows an invokes group holding delete, Ticket's operation in Clean Engineering")
    def _(world):
        expect(world.when).to(equal(["delete"]))

    @s.then("the Given and the Then show no invokes group, since the seed and the helper are the story test's own code")
    def _(world):
        expect((world.given, world.then)).to(equal(([], [])))


@shared_stories.scenario("Follow Story Steps To Code", "Selecting an operation a step invokes opens just that operation")
def _(s):
    @s.given("the Files app shows the Stories tree of Delete Ticket's Python shared story test, its When opened to the invokes group holding delete")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        expect(related_under(world, "when the Person deletes it", "invokes")).to(equal(["delete"]))

    @s.when("the Person selects delete")
    def _(world):
        ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, "delete", STEP_LISTED), paths=STEP_LISTED))
        world.lines = [(found["path"], found["start_line"], found["end_line"]) for found in ranges]

    @s.then("ticket.py opens at lines 8 to 9, delete's own lines, and the shared story test, whose When invokes it, does not open")
    def _(world):
        expect(world.lines).to(equal([(TICKET_CODE, 8, 9)]))


@shared_stories.scenario("Follow Story Steps To Code", "Selecting an example a step observes opens its definition")
def _(s):
    @s.given("the Files app shows the Stories tree of Delete Ticket's Python shared story test, whose Then observes CHECKOUT_TICKET, imported from ticket_story_examples.py")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        expect(related_under(world, "then the checkout ticket is gone", "observes")).to(equal(["CHECKOUT_TICKET"]))

    @s.when("the Person selects CHECKOUT_TICKET in the Then's observes group")
    def _(world):
        ranges = world.data_of(session_of(world).graph_node_ranges(node_id=node_id_of(world, "CHECKOUT_TICKET", STEP_LISTED), paths=STEP_LISTED))
        world.lines = [(found["path"], found["start_line"], found["end_line"]) for found in ranges]

    @s.then("ticket_story_examples.py opens at line 5, where CHECKOUT_TICKET is defined, and the shared story test, whose Then observes it, does not open")
    def _(world):
        expect(world.lines).to(equal([(TICKET_EXAMPLES, TICKET_EXAMPLES_CONSTANT_LINE, TICKET_EXAMPLES_CONSTANT_LINE)]))


@shared_stories.scenario("Follow Story Steps To Code", "A story test's callouts sit on the step that invokes them")
def _(s):
    @s.given("the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose docstring names the class Ticket")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        session_of(world).graph_trees(paths=STEP_LISTED)

    @s.when("the Person views the shared story test")
    def _(world):
        world.steps = world.data_of(session_of(world).file(path=STEP_STORY, rules=True))["steps"]

    @s.then("the line of the When that calls Ticket.delete carries a callout titled Ticket.delete, but the Given's line, calling only its seed, and the docstring's line carry none")
    def _(world):
        found = [(callout["line"], callout["title"], callout["target"]["file"]) for step in world.steps for callout in step["callouts"] if callout["kind"] == "call"]
        expect(found).to(equal([(STEP_STORY_WHEN_CALL_LINE, "Ticket.delete", TICKET_CODE)]))


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


@shared_stories.scenario("Follow Story Steps To Code", "A markdown When is not asked to invoke code before a realization names it")
def _(s):
    @s.given("checkout-flow's Delete Ticket scenarios in markdown, whose When the Person deletes the ticket's card names no code, and Clean Engineering read")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person views the scenarios file with the rules the whole working copy breaks")
    def _(world):
        world.violations = world.data_of(session_of(world).file(path=SCENARIOS, cross_file=True))["violations"]

    @s.then("the When carries no finding that it invokes nothing, since only a step backed by code can name the code it invokes")
    def _(world):
        found = [found["violation"]["message"] for found in world.violations if "invokes" in found["violation"]["message"]]
        expect(found).to(equal([]))


@shared_stories.scenario("Follow Story Steps To Code", "A When in a story test that calls none of the code it tests is flagged")
def _(s):
    @s.given("Delete Ticket's Python shared story test, whose When the Person looks up the deleted ticket calls only the file's own helper ticket_left")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person views the shared story test with its own rules")
    def _(world):
        world.violations = world.data_of(session_of(world).file(path=STEP_STORY, rules=True))["violations"]

    @s.then("that When carries the code-steps-invoke-code finding, and the When that calls Ticket.delete carries none")
    def _(world):
        flagged = [found["violation"]["message"] for found in world.violations if found["violation"]["rule"] == "code-steps-invoke-code"]
        expect((len(flagged), any(STEP_STORY_HELPER_WHEN in message for message in flagged))).to(equal((1, True)))


@shared_stories.scenario("Follow Story Steps To Code", "A story test outside the session's folder shows the rules it breaks")
def _(s):
    @s.given("checkout-flow works in the folder space, and Delete Ticket's Python shared story test, under story_tests outside it, has a When that calls only the file's own helper ticket_left")
    def _(world):
        seed_checkout_flow_with_graph_files(world, CHECKOUT_FLOW_IN_SPACE)

    @s.when("the Person views the shared story test with its own rules")
    def _(world):
        world.opened = world.data_of(session_of(world).file(path=STEP_STORY, rules=True))

    @s.then("the story test's steps are read, and that When carries the code-steps-invoke-code finding")
    def _(world):
        flagged = [found["violation"]["message"] for found in world.opened["violations"] if found["violation"]["rule"] == "code-steps-invoke-code"]
        expect((bool(world.opened["folds"]), any(STEP_STORY_HELPER_WHEN in message for message in flagged))).to(equal((True, True)))


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


# --- Filter Callouts Like The Graph -------------------------------------------------------------------------------

# Seed: a note of no practice that links to another, and one that links to a heading the kanban's class model lacks.
READING_NOTE = "notes/reading.md"
READING_NOTE_TEXT = "See the [plain note](plain.md).\n"
PLAIN_NOTE = "notes/plain.md"
MISLINKED_NOTE = "notes/mislinked.md"
MISLINKED_NOTE_TEXT = "See the [swimlane](../space/kanban/.context/kanban-model.md#no-such-heading).\n"
# Seed: a note at the project's top that links to a file not there.
GONE_LINK_NOTE = "gone-link.md"
GONE_LINK_NOTE_TEXT = "See [what was here](nowhere/gone.md).\n"
# Interaction: the files the page lists with Clean Engineering turned off, and with it on.
STORIES_LISTED = [STORY_MAP, SCENARIOS]
STORIES_AND_CODE_LISTED = [STORY_MAP, SCENARIOS, TICKET_CODE, KANBAN_MODEL]
STEP_STORY_THEN_LINE = 17


def shown_callouts_of(world, path: str, paths: list[str] | None) -> list[tuple[int, str]]:
    """Each callout session.file answers for path with the files at paths listed: its line and the file it opens."""
    found = world.data_of(session_of(world).file(path=path, paths=paths))["callouts"]
    return [(callout["line"], callout["section"]["path"]) for callout in found]


def reached_by_steps(world, paths: list[str] | None = STEP_LISTED, node_filter: dict | None = None) -> dict[int, list[str]]:
    """What each step of Delete Ticket's shared story test carries, by the step's line, as session.file answers it for
    the files at paths and node_filter: the names it invokes, then those it observes."""
    steps = world.data_of(session_of(world).file(path=STEP_STORY, rules=True, paths=paths, node_filter=node_filter))["steps"]
    return {step["line"]: [callout["target"]["name"] for callout in step["callouts"]] for step in steps}


def seed_step_story_graph(world) -> None:
    """Seed: checkout-flow's files, and its graph read from Delete Ticket's shared story test and the code it reaches."""
    seed_checkout_flow_with_graph_files(world)
    session_of(world).graph_trees(paths=STEP_LISTED)


@shared_stories.scenario("Filter Callouts Like The Graph", "A practice turned off leaves out the callouts into its files")
def _(s):
    @s.given("Delete Ticket's Given links the ticket to space/kanban/ticket.py and its Then links the board to the kanban's class model, both files of Clean Engineering")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person views the scenarios file with Clean Engineering turned off, then on again")
    def _(world):
        world.turned_off = shown_callouts_of(world, SCENARIOS, STORIES_LISTED)
        world.turned_on = shown_callouts_of(world, SCENARIOS, STORIES_AND_CODE_LISTED)

    @s.then("with it off, the scenarios file carries no callout")
    def _(world):
        expect(world.turned_off).to(equal([]))

    @s.then("with it on again, line 7 carries its callout into ticket.py and line 9 its callout into the class model")
    def _(world):
        expect(world.turned_on).to(equal([(SCENARIOS_GIVEN_LINE, TICKET_CODE), (SCENARIOS_THEN_LINE, KANBAN_MODEL)]))


@shared_stories.scenario("Filter Callouts Like The Graph", "A callout into a file no practice declares shows whatever is turned off")
def _(s):
    @s.given("a note, notes/reading.md, links to notes/plain.md, and no fidelity declares either")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(READING_NOTE, READING_NOTE_TEXT)
        world.project.seed_file(PLAIN_NOTE, "# Plain\n")

    @s.when("the Person views notes/reading.md with every practice turned off, so no file is listed")
    def _(world):
        world.callouts = shown_callouts_of(world, READING_NOTE, [])

    @s.then("line 1 carries its callout into notes/plain.md")
    def _(world):
        expect(world.callouts).to(equal([(1, PLAIN_NOTE)]))


@shared_stories.scenario("Filter Callouts Like The Graph", "A link to a heading not there, in a file left out, says nothing")
def _(s):
    @s.given("a markdown file of no practice links to a heading the kanban's class model does not have")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(MISLINKED_NOTE, MISLINKED_NOTE_TEXT)

    @s.when("the Person views it with Clean Engineering turned off, then with the class model listed")
    def _(world):
        session = session_of(world)
        world.turned_off = world.data_of(session.file(path=MISLINKED_NOTE, paths=STORIES_LISTED))["callouts"]
        world.listed = world.data_of(session.file(path=MISLINKED_NOTE, paths=STORIES_AND_CODE_LISTED))["callouts"]

    @s.then("with Clean Engineering off, the line carries no callout")
    def _(world):
        expect(world.turned_off).to(equal([]))

    @s.then("with the class model listed, the line's callout says the model has no heading no-such-heading")
    def _(world):
        expect([callout["missing"] for callout in world.listed]).to(equal([f"{KANBAN_MODEL} has no heading #no-such-heading"]))


@shared_stories.scenario("Filter Callouts Like The Graph", "A link to a file not there says so whatever is turned off")
def _(s):
    @s.given("a markdown file links to nowhere/gone.md, a file not there")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        world.project.seed_file(GONE_LINK_NOTE, GONE_LINK_NOTE_TEXT)

    @s.when("the Person views it with every practice turned off, so no file is listed")
    def _(world):
        world.callouts = world.data_of(session_of(world).file(path=GONE_LINK_NOTE, paths=[]))["callouts"]

    @s.then("the line's callout says nowhere/gone.md is not there")
    def _(world):
        expect([callout["missing"] for callout in world.callouts]).to(equal(["nowhere/gone.md is not there"]))


@shared_stories.scenario("Filter Callouts Like The Graph", "A connector left out of the node filter leaves out what a step reaches by it")
def _(s):
    @s.given("the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose When invokes Ticket.delete and whose Then observes CHECKOUT_TICKET")
    def _(world):
        seed_step_story_graph(world)

    @s.when("the Person views the shared story test with observes left out of the graph view's connectors, then with invokes left out instead")
    def _(world):
        world.without_observes = reached_by_steps(world, node_filter={"relationships": ["invokes"]})
        world.without_invokes = reached_by_steps(world, node_filter={"relationships": ["observes"]})

    @s.then("with observes left out, the When's line carries delete, and the Then's line carries nothing")
    def _(world):
        expect(world.without_observes).to(equal({STEP_STORY_WHEN_LINE: ["delete"]}))

    @s.then("with invokes left out, the Then's line carries CHECKOUT_TICKET, and the When's line carries nothing")
    def _(world):
        expect(world.without_invokes).to(equal({STEP_STORY_THEN_LINE: ["CHECKOUT_TICKET"]}))


@shared_stories.scenario("Filter Callouts Like The Graph", "A node type left out of the node filter leaves out the nodes of that type a step reaches")
def _(s):
    @s.given("the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose When invokes Ticket.delete, an operation, and whose Then observes CHECKOUT_TICKET, an example")
    def _(world):
        seed_step_story_graph(world)

    @s.when("the Person views the shared story test with the node filter narrowed to operations")
    def _(world):
        world.reached = reached_by_steps(world, node_filter={"types": ["Operation"]})

    @s.then("the When's line carries delete, and the Then's line carries nothing")
    def _(world):
        expect(world.reached).to(equal({STEP_STORY_WHEN_LINE: ["delete"]}))


@shared_stories.scenario("Filter Callouts Like The Graph", "A step keeps what it reaches in the files listed with it")
def _(s):
    @s.given("the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test, whose Then observes CHECKOUT_TICKET in ticket_story_examples.py, the examples file Stories declares")
    def _(world):
        seed_step_story_graph(world)

    @s.when("the Person views the shared story test with the story test and its examples file listed")
    def _(world):
        world.reached = reached_by_steps(world, paths=[STEP_STORY, TICKET_EXAMPLES])

    @s.then("the Then's line carries CHECKOUT_TICKET, and the When's line carries nothing, since ticket.py is Clean Engineering's and is not listed")
    def _(world):
        expect(world.reached).to(equal({STEP_STORY_THEN_LINE: ["CHECKOUT_TICKET"]}))


@shared_stories.scenario("Filter Callouts Like The Graph", "A read that sends no filter holds every callout")
def _(s):
    @s.given("the Files app shows checkout-flow's graph of Delete Ticket's Python shared story test")
    def _(world):
        seed_step_story_graph(world)

    @s.when("an agent reads the shared story test, sending no files listed and no node filter")
    def _(world):
        world.reached = reached_by_steps(world, paths=None)

    @s.then("the When's line carries delete and the Then's line carries CHECKOUT_TICKET")
    def _(world):
        expect(world.reached).to(equal({STEP_STORY_WHEN_LINE: ["delete"], STEP_STORY_THEN_LINE: ["CHECKOUT_TICKET"]}))
