"""Integrate Practice Content Editor Apps On Board: the shared scenarios the Python tiers replay for the knowledge graph a
ticket's graph widget and the board header open.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board/
integrate_practice_content_editor_apps_on_board_story.test.md (Filter Knowledge Graph To Ticket Scope, Filter Knowledge
Graph To Ticket Practices, Deploy Knowledge Graph App With Board State).
Model: harness/.context/editor-apps/.context/editor-apps-model.md#graph-extended.

A ticket's graph widget opens the Graph app on the ticket's worktree, where the ticket's session is the open one, so the
graph it loads is the ticket's session graph (`ticket.session.graph`); the board header opens it on the board's own
project. Left to other increments: Open Story UI On Ticket Scope, Invoke Story Explorer In Session Context, and the
refactors to web domain access, which are the pages' TypeScript.
"""

from __future__ import annotations

from expects import be, contain, equal, expect

from space.kanban.knowledge_graph_examples import BILLING_REPORT, CHECKOUT_FLOW, EVERY_PRACTICE, files_read, roots_loaded
from space.kanban.story_test import SharedStories

shared_stories = SharedStories("Integrate Practice Content Editor Apps On Board")

TICKET_SCOPE = "Filter Knowledge Graph To Ticket Scope"
TICKET_PRACTICES = "Filter Knowledge Graph To Ticket Practices"
BOARD_STATE = "Deploy Knowledge Graph App With Board State"


@shared_stories.scenario(TICKET_SCOPE, "The ticket's graph widget opens the graph on the ticket's practice roots")
def _(s):
    @s.given("checkout-flow's practice roots are harness/.context/stories, harness/.context/ux and harness/.context")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.project)
        BILLING_REPORT.seed_into(world.project)

    @s.when("the Person opens the knowledge graph from checkout-flow's graph widget")
    def _(world):
        world.graph = world.board().ticket(CHECKOUT_FLOW.name).session.graph
        world.graph.load_practice_roots(world.app_call())

    @s.then("the Graph app opens on checkout-flow's practice roots: harness/.context/stories, harness/.context/ux and harness/.context")
    def _(world):
        expect(roots_loaded(world.graph, world.project.root)).to(equal(CHECKOUT_FLOW.roots))

    @s.and_("no folder of billing-report is loaded")
    def _(world):
        expect(files_read(world.graph, world.project.root)).to(equal([f"{CHECKOUT_FLOW.roots['stories']}/story-map.md"]))


@shared_stories.scenario(TICKET_SCOPE, "Another ticket's graph widget rescopes the open graph")
def _(s):
    @s.given("the knowledge graph is open on checkout-flow's practice roots")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.project)
        BILLING_REPORT.seed_into(world.project)
        world.board().ticket(CHECKOUT_FLOW.name).session.graph.load_practice_roots(world.app_call())

    @s.when("the Person opens the knowledge graph from billing-report's graph widget")
    def _(world):
        world.graph = world.board().ticket(BILLING_REPORT.name).session.graph
        world.graph.load_practice_roots(world.app_call())

    @s.then("the Graph app shows billing-report's practice roots: billing/.context/stories and billing/.context")
    def _(world):
        expect(roots_loaded(world.graph, world.project.root)).to(equal(BILLING_REPORT.roots))

    @s.and_("no folder of checkout-flow is loaded")
    def _(world):
        expect(files_read(world.graph, world.project.root)).to(equal([f"{BILLING_REPORT.roots['stories']}/story-map.md"]))


# The graph openings table: what the graph was opened from and the practice trees it shows.
OPENINGS = [
    ("billing-report's graph widget", BILLING_REPORT.name, BILLING_REPORT.practices),
    ("checkout-flow's graph widget", CHECKOUT_FLOW.name, CHECKOUT_FLOW.practices),
    ("the board header", "main", list(EVERY_PRACTICE)),
]

for opened_from, ticket, practice_trees in OPENINGS:

    @shared_stories.scenario(TICKET_PRACTICES, f"The graph shows only the practices of what it was opened from: {opened_from}")
    def _(s, ticket=ticket, opened_from=opened_from, practice_trees=practice_trees):
        @s.given("billing-report has Stories and DDD enabled")
        def _(world):
            BILLING_REPORT.seed_into(world.project)

        @s.and_("checkout-flow has Stories, UX and Clean Engineering enabled")
        def _(world):
            CHECKOUT_FLOW.seed_into(world.project)

        @s.when(f"the Person opens the knowledge graph from {opened_from}")
        def _(world):
            world.graph = world.board().ticket(ticket).session.graph
            world.graph.load_practice_roots(world.app_call())

        @s.then(f"the graph shows the {', '.join(practice_trees)} trees")
        def _(world):
            expect(list(world.graph.inventory().practices)).to(contain(*practice_trees))

        @s.and_("it shows no tree of a practice not listed")
        def _(world):
            expect(list(world.graph.inventory().practices)).to(equal(practice_trees))


@shared_stories.scenario(BOARD_STATE, "The Graph app shares the board's state")
def _(s):
    @s.given("checkout-flow is the board's active ticket")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.project)
        BILLING_REPORT.seed_into(world.project)
        world.project.seed_active(CHECKOUT_FLOW.seed)

    @s.when("the Agent deploys the Graph app with the board's state")
    def _(world):
        world.call = world.app_call()
        world.graph = world.call.session.graph
        world.graph.load_practice_roots(world.call)

    @s.then("the Graph app works on the same session and graph as the board's active ticket")
    def _(world):
        expect(world.graph).to(be(world.board().active.session.graph))

    @s.when("the session open in the project becomes billing-report's, which the board then shows as active")
    def _(world):
        world.sessions.switch(BILLING_REPORT.name)
        world.graph = world.app_call().session.graph
        world.graph.load_practice_roots(world.app_call())

    @s.then("the board's active ticket is billing-report")
    def _(world):
        expect(world.board().active.name).to(equal(BILLING_REPORT.name))

    @s.and_("the graph shows billing-report's practice roots on its next read, without a reload")
    def _(world):
        expect(roots_loaded(world.graph, world.project.root)).to(equal(BILLING_REPORT.roots))
