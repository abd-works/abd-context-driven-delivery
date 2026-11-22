"""Explore Graph In Files App: the shared scenarios the Python tiers replay.

Scenarios: story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/
explore_graph_in_files_app_story.test.md. Map: .context/story-map.md, (E) Explore Graph In Files App.

Steps reach the session only through the namespace a tier hands them (`world.Ticket`), so the domain spec and the cdd
tools spec replay the same steps. Only the scenarios built so far are here: Expand Practice Tree In Files App, Follow
Relationships Under Node In Files App, Filter Graph By Node Type And Connector In Files App, Apply Pattern Overlays In
Files App and Open Calls Across Files In Files App. Covered by the Files app's own specs (`harness/files_app/app/files/files-graph.spec.ts`),
not here, because only the page shows them: each node's kind mark, the load steps while the graph reads, and a call
opened in place in the source view. The Thens below check what the session answers the page for each.
"""

from __future__ import annotations

from expects import equal, expect

from space.kanban.story_test import SharedStories
from space.kanban.graph_view_examples import BOARD_CODE, LISTED, STORY_MAP, TICKET_CODE, node_id_of, seed_checkout_flow_with_graph_files, session_of
from space.kanban.graph_view_rule_examples import (
    CHECKOUT_FLOW_WITH_DDD,
    LERN,
    LERN_DOMAIN_TIER_RULES,
    LISTED_WITH_DOMAIN_TIER,
    NO_NODE_FILTER,
    OPERATIONS,
    OPERATIONS_ON_INVOKES,
    TICKET_DOMAIN_TIER,
    names_of,
    rule_slugs_on,
    seed_checkout_flow_with_both_tickets,
)

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


@shared_stories.scenario("Follow Relationships Under Node In Files App", "Selecting a related node opens the related node alone, in its own file")
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

    @s.then("board.py opens at Board.reread, but ticket.py, which holds Ticket.delete, is no longer open")
    def _(world):
        expect(world.lines).to(equal([(BOARD_CODE, 2, 3)]))


# --- Filter Graph By Node Type And Connector In Files App ---------------------------------------------------------

# Seed: the Files app listing ticket.py but not board.py.
TICKET_LISTED = [STORY_MAP, TICKET_CODE]


@shared_stories.scenario("Filter Graph By Node Type And Connector In Files App", "Choosing a node type keeps only those nodes")
def _(s):
    @s.given("the Files app shows checkout-flow's graph with Clean Engineering on")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person filters the graph to operations")
    def _(world):
        world.operations = names_of(world, "Operation", LISTED, OPERATIONS)
        world.parameters = names_of(world, "Parameter", LISTED, OPERATIONS)
        world.choices = world.data_of(session_of(world).graph_filter_choices(practices=[], node_types=OPERATIONS["types"]))

    @s.then("the Clean Engineering tree holds Ticket.activate, Ticket.close, Ticket.delete and Board.reread")
    def _(world):
        expect((world.operations, world.parameters)).to(equal(({"activate", "close", "delete", "reread"}, set())))

    @s.then("the connectors and rules offered narrow to the ones operations carry")
    def _(world):
        operation_rules = [rule for rule in world.choices["rules"] if rule.split(".")[-2] == "Operation"]
        expect((world.choices["relationships"], operation_rules == world.choices["rules"])).to(equal((["owns", "hasParameter", "invokes"], True)))


@shared_stories.scenario("Filter Graph By Node Type And Connector In Files App", "Choosing a connector keeps the nodes on that edge")
def _(s):
    @s.given("the Files app shows checkout-flow's graph filtered to operations")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person filters the graph to the invokes connector")
    def _(world):
        world.operations = names_of(world, "Operation", LISTED, OPERATIONS_ON_INVOKES)

    @s.then("the tree holds Ticket.delete and Board.reread, but not Ticket.activate or Ticket.close")
    def _(world):
        expect(world.operations).to(equal({"delete", "reread"}))


@shared_stories.scenario("Filter Graph By Node Type And Connector In Files App", "A node filter narrows only the files listed")
def _(s):
    @s.given("the Files app lists ticket.py but not board.py")
    def _(world):
        seed_checkout_flow_with_graph_files(world)

    @s.when("the Person filters the graph to operations")
    def _(world):
        world.operations = names_of(world, "Operation", TICKET_LISTED, OPERATIONS)

    @s.then("the Clean Engineering tree holds Ticket.activate, Ticket.close and Ticket.delete, but not Board.reread")
    def _(world):
        expect(world.operations).to(equal({"activate", "close", "delete"}))


@shared_stories.scenario("Filter Graph By Node Type And Connector In Files App", "Changing the file list keeps the node filter")
def _(s):
    @s.given("the graph is filtered to operations and the Files app lists ticket.py alone")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        names_of(world, "Operation", TICKET_LISTED, OPERATIONS)

    @s.when("the Person lists board.py too")
    def _(world):
        world.operations = names_of(world, "Operation", LISTED, OPERATIONS)
        world.parameters = names_of(world, "Parameter", LISTED, OPERATIONS)

    @s.then("Board.reread joins the Clean Engineering tree, and the graph stays filtered to operations")
    def _(world):
        expect((world.operations, world.parameters)).to(equal(({"activate", "close", "delete", "reread"}, set())))


@shared_stories.scenario("Filter Graph By Node Type And Connector In Files App", "None clears a filter list")
def _(s):
    @s.given("the graph is filtered to operations")
    def _(world):
        seed_checkout_flow_with_graph_files(world)
        names_of(world, "Operation", LISTED, OPERATIONS)

    @s.when("the Person clears the node types with None")
    def _(world):
        world.classes = names_of(world, "OoadClass", LISTED, NO_NODE_FILTER)
        world.parameters = names_of(world, "Parameter", LISTED, NO_NODE_FILTER)

    @s.then("the graph view holds every node of the files listed again")
    def _(world):
        expect((world.classes, world.parameters)).to(equal(({"Ticket", "Board"}, {"board"})))


# --- Apply Pattern Overlays In Files App -------------------------------------------------------------------------


@shared_stories.scenario("Apply Pattern Overlays In Files App", "The graph view shows the overlays the session chose")
def _(s):
    @s.given("checkout-flow's session has the LERN overlay chosen on the chat bar")
    def _(world):
        seed_checkout_flow_with_both_tickets(world)
        world.Ticket.load(CHECKOUT_FLOW_WITH_DDD.name).choose_overlays(overlays=[LERN])

    @s.when("the Person switches the file bar to the graph view")
    def _(world):
        world.on_typescript = rule_slugs_on(world, "Ticket", TICKET_DOMAIN_TIER, LISTED_WITH_DOMAIN_TIER)
        world.on_python = rule_slugs_on(world, "Ticket", TICKET_CODE, LISTED_WITH_DOMAIN_TIER)

    @s.then("Ticket in ticket.ts carries LERN's Domain tier rules among its rules, but Ticket in ticket.py carries none")
    def _(world):
        expect((world.on_typescript.issuperset(LERN_DOMAIN_TIER_RULES), world.on_python & set(LERN_DOMAIN_TIER_RULES))).to(equal((True, set())))


@shared_stories.scenario("Apply Pattern Overlays In Files App", "An overlay taken off leaves the graph view")
def _(s):
    @s.given("the Files app shows checkout-flow's graph with LERN applied")
    def _(world):
        seed_checkout_flow_with_both_tickets(world)
        world.Ticket.load(CHECKOUT_FLOW_WITH_DDD.name).choose_overlays(overlays=[LERN])
        world.before = rule_slugs_on(world, "Ticket", TICKET_DOMAIN_TIER, LISTED_WITH_DOMAIN_TIER)

    @s.when("the Person takes LERN off the session")
    def _(world):
        world.chips = world.data_of(world.Ticket.load(CHECKOUT_FLOW_WITH_DDD.name).choose_overlays(overlays=[]))

    @s.then("the LERN rules on Ticket in ticket.ts leave the graph view")
    def _(world):
        after = rule_slugs_on(world, "Ticket", TICKET_DOMAIN_TIER, LISTED_WITH_DOMAIN_TIER)
        expect((world.before.issuperset(LERN_DOMAIN_TIER_RULES), after & set(LERN_DOMAIN_TIER_RULES))).to(equal((True, set())))

    @s.then("the chat bar's LERN chip shows off")
    def _(world):
        expect({chip["pattern"]: chip["is_chosen"] for chip in world.chips}[LERN]).to(equal(False))


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
