"""See Work On Session Board: the shared scenarios the Python tiers replay.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md; Restrict Actions To Active Session is in harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md.
Map: .context/story-map.md#e-see-work-on-session-board. Model: .context/kanban-model.md.

Steps reach the board only through the namespace a tier hands them (`world.Board`, `world.Ticket`), so the domain spec
and the cdd tools spec replay the same steps. Every Then asserts what the board returns, as the data
fields its classes mark, which the board app draws from.

Covered by the board app's TypeScript client specs in space/kanban/app, not here, because they have no Python
operation: Arrange Board And Details (all three); Arrange Side Panel (all four); Display Board "Say the cdd server is
not connected", "Install the board again", "Say why the board's install failed", "Keep the newer board when an older read answers late", "Announce a
ticket that moved", "Announce a fidelity done"; Display Ticket Card "Draw the card's title, age, and fidelity
segments", "Name the active ticket on the chat's status line"; Display Ticket Details "Show the active ticket with no
card pressed", "Show main when no other ticket is opened", "Say another session must be activated to act on
a locked ticket", "Expand one ticket's card at a time", "Open a card on the fidelity of a pressed segment"; Open Board
"Find the board from a chat"; Restrict Actions To Active Session (all three: Active session only is the board app's
own setting); Set Stage WIP Limit "Change nothing for a limit that is not a whole number". The Thens of the scenarios
below that only the page shows (the band, the outline, the polling) are left to those specs too.
"""

from __future__ import annotations

from datetime import datetime, timezone

from expects import be_none, be_true, equal, expect

from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ux.ux import Ux
from harness.catalog_generator.catalog_practice import CatalogPractice
from harness.installation.json_file import JsonFileUnreadable
from space.session.sessions import BoardPractices
from space.repo.repo import Repo
from space.kanban.session_board_examples import (
    BACK_TO_BACKLOG,
    BILLING_REPORT,
    BROKEN,
    BROKEN_SESSION_JSON,
    BROWSE_PETS,
    CHECKOUT_FLOW,
    CHILD,
    DISCOVERY_FIDELITY_SLUGS,
    DISCOVERY_LIMIT,
    GENERATED_UX_MOCKUP,
    GIFT_CARDS_HELD,
    GIFT_CARDS_HELD_FILE,
    LOWERED_DISCOVERY_LIMIT,
    MAIN,
    MOVE_ME,
    OLD_SPIKE,
    PET_VISITS,
    RAISED_DISCOVERY_LIMIT,
    RETURNS_AND_REFUNDS_UNHEADED,
    SEARCH_THE_CATALOG,
    SECOND_SPEC,
    SIGN_UP,
    STAMP,
    SURFACE_FIXTURE_PROJECT,
    seed_surface_fixture,
)
from space.kanban.story_test import SharedStories, active_in, column_in, expect_backlog, expect_placed, expect_refused, names_in, next_in, progress_in, refusal_of, ticket_in

shared_stories = SharedStories("See Work On Session Board")

STAGES = ("Discovery", "Specification", "Implementation")


@shared_stories.scenario("Open Board", "Open the board on a project")
def _(s):
    @s.given("the board of project cdd-board-surface-fixture shows 10 tickets")
    def _(world):
        seed_surface_fixture(world.project)

    @s.and_("its session checkout-flow, titled Checkout flow, is the active ticket")
    def _(world):
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("the Person opens the session board at http://127.0.0.1:8778")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("the header reads cdd-board-surface-fixture · 10 tickets · active: Checkout flow")
    def _(world):
        tickets = [name for column in world.read["columns"] for name in names_in(column)]
        header = (world.read["project"], len(tickets), active_in(world.read)["title"])
        expect(header).to(equal((SURFACE_FIXTURE_PROJECT, 10, "Checkout flow")))


@shared_stories.scenario("Display Board", "Draw the columns of the board")
def _(s):
    @s.given("a board with the Stories, DDD, and UX practices chosen")
    def _(world):
        world.board = world.Board(Repo(world.project.root), BoardPractices(CatalogPractice.of_practices([Stories(), Ddd(), Ux()])))

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.board.show())

    @s.then("the columns read Backlog, Discovery, Specification, Implementation, and Complete, in that order")
    def _(world):
        expect([column["name"] for column in world.read["columns"]]).to(equal(["Backlog", *STAGES, "Complete"]))

    @s.and_("each stage shows an In progress list and a Done list")
    def _(world):
        expect([("in_progress" in column_in(world.read, stage), "done" in column_in(world.read, stage)) for stage in STAGES]).to(equal([(True, True)] * 3))

    @s.and_("the Discovery stage requires story_map, bounded_context, and ia, each through Generate and Validate")
    def _(world):
        required = ([fidelity["slug"] for fidelity in column_in(world.read, "Discovery")["work_required"]], world.board.column("Discovery").steps)
        expect(required).to(equal((["stories-story-map", "ddd-bounded-context", "ux-ia"], ["generate", "validate"])))


@shared_stories.scenario("Display Board", "Show a failing tool in a toast")
def _(s):
    @s.given("the session folder .sessions/broken holds a session.json that is not JSON")
    def _(world):
        world.project.seed_session(BROKEN)
        world.project.seed_session_json_text(BROKEN, BROKEN_SESSION_JSON)

    @s.when("the session board reads the board")
    def _(world):
        world.refusal = refusal_of(lambda: world.data_of(world.Board.load().show()))

    @s.then("a toast says cdd board.show failed: JsonFileUnreadable: .sessions/broken/session.json is not a readable JSON object (Expecting property name enclosed in double quotes: line 1 column 2 (char 1))")
    def _(world):
        broken = world.project.sessions / BROKEN.name / "session.json"
        expect_refused(world.refusal, JsonFileUnreadable, f"{broken} is not a readable JSON object (Expecting property name enclosed in double quotes: line 1 column 2 (char 1))")


@shared_stories.scenario("Display Backlog Items As Tickets", "Show each idea file in the Backlog")
def _(s):
    @s.given("the repository's .sessions/_backlog/ holds search-the-catalog.md headed Search the catalog with the text An idea.")
    def _(world):
        world.idea_file = world.project.seed_backlog_file(SEARCH_THE_CATALOG)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("the Backlog column shows the backlog item Search the catalog")
    def _(world):
        expect_backlog(world.read, [SEARCH_THE_CATALOG.heading])

    @s.and_("selecting it shows its text An idea. in the details")
    def _(world):
        expect(column_in(world.read, "Backlog")["items"][0]["text"]).to(equal("An idea."))

    @s.and_("its last activity is when search-the-catalog.md last changed")
    def _(world):
        changed = datetime.fromtimestamp(world.idea_file.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        expect(column_in(world.read, "Backlog")["items"][0]["last_activity"]).to(equal(changed))


@shared_stories.scenario("Display Backlog Items As Tickets", "Show a ticket kept in the Backlog under its own file")
def _(s):
    @s.given("the Backlog folder holds the folder gift-cards with its session log and gift-cards.md headed Gift cards")
    def _(world):
        world.project.seed_session(GIFT_CARDS_HELD)

    @s.and_("gift-cards.md holds the text Sell them at the till.")
    def _(world):
        world.project.seed_backlog_file(GIFT_CARDS_HELD_FILE, folder=GIFT_CARDS_HELD.name)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("the Backlog column shows one backlog item Gift cards with the text Sell them at the till.")
    def _(world):
        expect([(item["title"], item["text"]) for item in column_in(world.read, "Backlog")["items"]]).to(equal([("Gift cards", "Sell them at the till.")]))

    @s.but_("no stage shows a ticket for gift-cards")
    def _(world):
        expect(ticket_in(world.read, "gift-cards")).to(be_none)


@shared_stories.scenario("Display Backlog Items As Tickets", "Name an item that has no heading by its file name")
def _(s):
    @s.given("the Backlog folder holds returns-and-refunds.md with no # heading")
    def _(world):
        world.project.seed_backlog_file(RETURNS_AND_REFUNDS_UNHEADED)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("the Backlog column shows the backlog item Returns and refunds")
    def _(world):
        expect_backlog(world.read, ["Returns and refunds"])


@shared_stories.scenario("Display Ticket Card", "Show every work session as a ticket")
def _(s):
    @s.given("the repository's .sessions/ holds the work sessions pet-visits and sign-up, the closed session browse-pets, main, and the archived session old-spike")
    def _(world):
        for seed in (PET_VISITS, SIGN_UP, BROWSE_PETS, MAIN, OLD_SPIKE):
            world.project.seed_session(seed)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("the Discovery stage shows the tickets main, Pet visits, and Sign up")
    def _(world):
        expect([ticket["title"] for ticket in column_in(world.read, "Discovery")["in_progress"]]).to(equal([MAIN.title, "Pet visits", "Sign up"]))

    @s.and_("the Complete column shows Browse pets")
    def _(world):
        expect([ticket["title"] for ticket in column_in(world.read, "Complete")["tickets"]]).to(equal(["Browse pets"]))

    @s.but_("old-spike is not on the board")
    def _(world):
        expect(ticket_in(world.read, OLD_SPIKE.name)).to(be_none)


@shared_stories.scenario("Display Ticket Card", "Place a ticket in the stage of its latest move")
def _(s):
    @s.given("the session log of the ticket second-spec ends with move Specification")
    def _(world):
        world.project.seed_session(SECOND_SPEC)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("second-spec shows In progress in the Specification stage")
    def _(world):
        expect_placed(ticket_in(world.read, SECOND_SPEC.name), "Specification", is_done=False)


@shared_stories.scenario("Display Ticket Card", "Place a ticket with no move in the stage of its latest work")
def _(s):
    @s.given("the session log of the ticket pet-visits has one line, generate /work/ux ux mockup html ux")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(GENERATED_UX_MOCKUP))

    @s.but_("it has no move line")
    def _(world):
        # The log seeded above is that one line, so nothing more is seeded.
        pass

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("pet-visits shows in the Specification stage")
    def _(world):
        expect(ticket_in(world.read, PET_VISITS.name)["column"]["name"]).to(equal("Specification"))


@shared_stories.scenario("Display Ticket Card", "Follow work into a later stage")
def _(s):
    @s.given("a person moved pet-visits into Discovery")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(f"{STAMP} move Discovery no-chat"))

    @s.and_("pet-visits' ux mockup was generated after that move")
    def _(world):
        world.project.seed_log_line(PET_VISITS, GENERATED_UX_MOCKUP)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("pet-visits shows in the Specification stage")
    def _(world):
        expect(ticket_in(world.read, PET_VISITS.name)["column"]["name"]).to(equal("Specification"))


@shared_stories.scenario("Display Ticket Card", "Keep a person's move until the next work")
def _(s):
    @s.given("pet-visits' ux mockup was generated")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(GENERATED_UX_MOCKUP))

    @s.and_("a person then moved pet-visits back into Discovery")
    def _(world):
        world.project.seed_log_line(PET_VISITS, f"{STAMP} move Discovery no-chat")

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("pet-visits shows in the Discovery stage")
    def _(world):
        expect(ticket_in(world.read, PET_VISITS.name)["column"]["name"]).to(equal("Discovery"))


@shared_stories.scenario("Display Ticket Card", "Follow work back into an earlier stage")
def _(s):
    @s.given("a person moved pet-visits into Implementation")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(f"{STAMP} move Implementation no-chat"))

    @s.and_("pet-visits' ux mockup was generated after that move")
    def _(world):
        world.project.seed_log_line(PET_VISITS, GENERATED_UX_MOCKUP)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("pet-visits shows in the Specification stage")
    def _(world):
        expect(ticket_in(world.read, PET_VISITS.name)["column"]["name"]).to(equal("Specification"))


@shared_stories.scenario("Display Ticket Card", "Outline the active ticket")
def _(s):
    @s.given("the repository's .sessions/session.json names checkout-flow as the open session")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    # The thick orange outline is drawn by ticket-card-view.tsx from the active ticket named here.
    @s.then("the header names Checkout flow as active")
    def _(world):
        expect((world.read["active"]["name"], active_in(world.read)["title"])).to(equal((CHECKOUT_FLOW.name, "Checkout flow")))


@shared_stories.scenario("Display Ticket Details", "Show the ticket of a card pressed anywhere")
def _(s):
    @s.given("the ticket billing-report is In progress in Discovery with nothing recorded")
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person selects billing-report's card")
    def _(world):
        world.selected = world.data_of(world.Ticket.load(BILLING_REPORT.name))

    @s.then("the details show Billing report, root whole repository, and Discovery · in progress")
    def _(world):
        expect((world.selected["title"], world.selected["session"]["workpath"], world.selected["column"]["name"], world.selected["is_done"])).to(equal(("Billing report", "", "Discovery", False)))

    @s.and_("the details say No handoff yet and Next: stories-story-map, generate")
    def _(world):
        expect((world.selected["session"]["handoff"], world.selected["next"]["fidelity"]["slug"], next_in(world.selected)["next_action"])).to(equal(("", "stories-story-map", "generate")))

    @s.and_("the details show a tile for each enabled fidelity with its fidelity progress")
    def _(world):
        expect({slug: progress_in(world.selected, slug)["state"] for slug in DISCOVERY_FIDELITY_SLUGS}).to(equal(dict.fromkeys(DISCOVERY_FIDELITY_SLUGS, "not_started")))


@shared_stories.scenario("Display Ticket Details", "Name a split ticket by the ticket it came from")
def _(s):
    @s.given("the ticket child has scope story and parent epic in its session.json")
    def _(world):
        world.project.seed_session(CHILD)

    @s.when("the Person selects child's card")
    def _(world):
        world.selected = world.data_of(world.Ticket.load(CHILD.name))

    @s.then("the details read child · story of epic")
    def _(world):
        expect((world.selected["title"], world.selected["session"]["scope"], world.selected["session"]["parent"])).to(equal(("child", "story", "epic")))


@shared_stories.scenario("Set Stage WIP Limit", "Set a stage's limit")
def _(s):
    @s.given("the Discovery stage has the limit 3")
    def _(world):
        world.project.seed_wip_limits({"Discovery": DISCOVERY_LIMIT})

    @s.when("the Person sets Discovery's limit to 4")
    def _(world):
        world.read = world.data_of(world.Stage.load("Discovery").set_wip_limit(limit=RAISED_DISCOVERY_LIMIT))

    @s.then("Discovery shows the limit 4")
    def _(world):
        expect(world.read["wip_limit"]).to(equal(RAISED_DISCOVERY_LIMIT))

    @s.and_("the limit is still 4 when the board is read again")
    def _(world):
        expect(column_in(world.data_of(world.Board.load().show()), "Discovery")["wip_limit"]).to(equal(RAISED_DISCOVERY_LIMIT))


@shared_stories.scenario("Set Stage WIP Limit", "Give every stage a limit of 3 until a person sets one")
def _(s):
    @s.given("the repository has no .sessions/_board.json")
    def _(world):
        # A new project has no board file until a person sets a limit.
        pass

    @s.when("the session board reads the board")
    def _(world):
        world.read = world.data_of(world.Board.load().show())

    @s.then("Discovery, Specification, and Implementation each show the limit 3")
    def _(world):
        expect([column_in(world.read, stage)["wip_limit"] for stage in STAGES]).to(equal([DISCOVERY_LIMIT] * 3))


@shared_stories.scenario("Set Stage WIP Limit", "Show a stage over its limit")
def _(s):
    @s.given("the Discovery stage holds the tickets billing-report, move-me, and back-to-backlog")
    def _(world):
        for seed in (BILLING_REPORT, MOVE_ME, BACK_TO_BACKLOG):
            world.project.seed_session(seed)

    @s.when("the Person sets Discovery's limit to 2")
    def _(world):
        world.read = world.data_of(world.Stage.load("Discovery").set_wip_limit(limit=LOWERED_DISCOVERY_LIMIT))

    @s.then("Discovery's count shows in red, over its limit")
    def _(world):
        expect(world.read["is_over_limit"]).to(be_true)
