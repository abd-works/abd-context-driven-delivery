"""Review Fidelity Outputs: the shared scenarios the Python tiers replay.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md.
Map: .context/story-map.md#e-review-fidelity-outputs. Model: .context/kanban-model.md.

Steps reach the board only through the World a tier hands them (`world.Ticket`), so the domain spec and the cdd tools
spec replay the same steps.

Covered by the board app's TypeScript client specs in space/kanban/app, not here, because they have no Python
operation: Browse Ticket Folder "Group a stage's files under their folders" (the files panel groups them); View
Fidelity Files "Go back to the list when the last tab closes"; Review Fidelity "Keep Review off until Validate is
clean" (the tile's action bar). The Thens of the scenarios below that only the page shows (a toast, a panel that does
not open) are left to those specs too.

The scenarios name the story map `.context/story-map.md`. The story_map fidelity declares its markdown at
`.context/story-map.md` and its drawio at `.context/story-map.drawio` (cdd_guidance/practices/stories/stories.md), so
`Ticket.files` lists `.context/story-map.md`; the Thens that list `.context/story-map.md` fail until the declaration and
the scenarios agree.
"""

from __future__ import annotations

from expects import contain, end_with, equal, expect

from space.kanban.session_board_examples import (
    BILLING_REPORT,
    CHECKOUT_FLOW,
    CHECKOUT_FLOW_REPORT,
    EVERY_DISCOVERY_FIDELITY_REVIEWED,
    NO_SUCH_FIDELITY,
    NO_SUCH_TICKET,
    OUTSIDE_FILE,
    PET_VISITS,
    SPEC_MINE,
    SPEC_THEIRS,
    STORY_MAP,
    STORY_MAP_FILE,
    STORY_MAP_REPORT,
    STORY_MAP_TEXT,
    STORY_MAP_VALIDATED_CLEAN,
    generated,
    reviewed,
    validated,
)
from space.kanban.story_test import SharedStories, expect_action, expect_no_next, expect_placed, expect_refused, refusal_of
from space.kanban.ticket import FidelityNotFoundError, TicketNotFoundError
from space.session.file_manager import PathOutsideRootsError

shared_stories = SharedStories("Review Fidelity Outputs")


def log_lines(world, seed) -> list[str]:
    return (world.project.sessions / seed.name / "session.log").read_text(encoding="utf-8").splitlines()


@shared_stories.scenario("List Ticket Files", "List a fidelity's files with whether each exists")
def _(s):
    @s.given("checkout-flow's story map .context/story-map.md is there and .context/story-map.drawio is not")
    def _(world):
        world.project.seed_file(STORY_MAP_FILE, STORY_MAP_TEXT)
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("the Person lists checkout-flow's story_map files")
    def _(world):
        world.files = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).files())

    @s.then("the files panel lists .context/story-map.md as there")
    def _(world):
        expect(world.files["markdown"]).to(equal([{"path": STORY_MAP_FILE, "exists": True}]))

    @s.but_("no file of another fidelity is listed")
    def _(world):
        expect(sorted(world.files)).to(equal(["drawio", "markdown"]))


@shared_stories.scenario("List Ticket Files", "List only what the ticket's branch changed")
def _(s):
    @s.given("the ticket pet-visits works on the whole repository on its own branch pet-visits")
    def _(world):
        # The repository's own spec is committed on main before pet-visits branches from it.
        world.project.seed_file(SPEC_THEIRS)
        world.project.seed_git_checkout()
        world.project.seed_branch(PET_VISITS.name, checked_out=True)
        world.project.seed_session(PET_VISITS)

    @s.and_("the repository holds src/theirs_spec.py and its branch added src/mine_spec.py")
    def _(world):
        world.project.seed_file(SPEC_MINE)

    @s.when("the Person lists pet-visits' bdd behavior files")
    def _(world):
        world.files = world.data_of(world.Ticket.load(PET_VISITS.name).work.progress_of("bdd-behavior").files())

    @s.then("the files panel lists src/mine_spec.py")
    def _(world):
        expect([entry["path"] for entry in world.files["python"]]).to(equal([SPEC_MINE]))

    @s.but_("src/theirs_spec.py is not listed")
    def _(world):
        expect(SPEC_THEIRS in [entry["path"] for entry in world.files["python"]]).to(equal(False))


@shared_stories.scenario("List Ticket Files", "Say in a toast when the list cannot be read")
def _(s):
    @s.given("the board shows no ticket named no-such-ticket")
    def _(world):
        # A new project's board shows no tickets.
        pass

    @s.when("the Person lists no-such-ticket's story_map files")
    def _(world):
        world.refusal = refusal_of(lambda: world.Ticket.load(NO_SUCH_TICKET).work.progress_of(STORY_MAP).files())

    @s.then("a toast says cdd fidelity-progress.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board")
    def _(world):
        expect_refused(world.refusal, TicketNotFoundError, "no ticket named 'no-such-ticket' on the board")


@shared_stories.scenario("Browse Ticket Folder", "Browse the ticket's session folder")
def _(s):
    @s.given("checkout-flow's session folder holds its log and validation-reports/stories-story-map-20261101T100000.md")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_report(CHECKOUT_FLOW, CHECKOUT_FLOW_REPORT)

    @s.when("the Person browses checkout-flow's session folder")
    def _(world):
        world.files = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.folder_files())

    @s.then("the files panel lists .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md under its folder")
    def _(world):
        expect(world.files).to(contain({"path": f".sessions/{CHECKOUT_FLOW.name}/validation-reports/{STORY_MAP_REPORT}.md", "exists": True}))


@shared_stories.scenario("View Fidelity Files", "Open one tab per format, generated or not")
def _(s):
    @s.given("checkout-flow's story map is .context/story-map.md and .context/story-map.drawio is not there")
    def _(world):
        world.project.seed_file(STORY_MAP_FILE, STORY_MAP_TEXT)
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("the Person views checkout-flow's story_map files")
    def _(world):
        ticket = world.Ticket.load(CHECKOUT_FLOW.name)
        world.files = world.data_of(ticket.work.progress_of(STORY_MAP).files())
        world.opened = world.data_of(ticket.session.read_file(path=STORY_MAP_FILE))

    @s.then("the files panel shows the tabs .context/story-map.md and .context/story-map.drawio")
    def _(world):
        expect([entry["path"] for entry in [*world.files["markdown"], *world.files["drawio"]]]).to(equal([STORY_MAP_FILE, ".context/story-map.drawio"]))

    @s.and_("the .context/story-map.md tab shows # Check Out Order")
    def _(world):
        expect(world.opened["text"].splitlines()[0]).to(equal("# Check Out Order"))

    @s.and_("the drawio tab says it is not generated yet")
    def _(world):
        expect(world.files["drawio"][0]["exists"]).to(equal(False))


@shared_stories.scenario("View Fidelity Files", "Refuse a file outside the repository")
def _(s):
    @s.given("checkout-flow's repository is the project folder")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("a file outside the repository is asked for")
    def _(world):
        world.refusal = refusal_of(lambda: world.Ticket.load(CHECKOUT_FLOW.name).session.read_file(path=OUTSIDE_FILE))

    @s.then("the board says ../secrets.txt is not a file in this repository")
    def _(world):
        expect_refused(world.refusal, PathOutsideRootsError, "../secrets.txt is outside the session's roots")


@shared_stories.scenario("Review Fidelity", "Review a fidelity after a clean validate")
def _(s):
    @s.given("billing-report's story map is generated and its latest validate passed with no graph-rule")
    def _(world):
        world.project.seed_session(BILLING_REPORT.with_log(*STORY_MAP_VALIDATED_CLEAN))

    @s.when("the Person reviews story_map on billing-report")
    def _(world):
        world.reviewed = world.data_of(world.Ticket.load(BILLING_REPORT.name).work.progress_of(STORY_MAP).finish_review())

    @s.then("billing-report's session log ends with review stories story_map")
    def _(world):
        expect(log_lines(world, BILLING_REPORT)[-1]).to(end_with(" review stories story_map"))

    @s.and_("the story_map tile marks Review ✓ and the fidelity is done")
    def _(world):
        expect((world.reviewed["actions"]["review"], world.reviewed["state"])).to(equal(("done", "done")))


@shared_stories.scenario("Review Fidelity", "Ignore a review recorded before a clean validate")
def _(s):
    @s.given("pet-visits' session log has generate, then review, then validate Stories story_map")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(generated("stories", "story_map"), reviewed("stories", "story_map"), validated("Stories", "story_map")))

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("the story_map tile marks Review ○")
    def _(world):
        expect_action(world.read, STORY_MAP, "review", "to_do")


@shared_stories.scenario("Review Fidelity", "Refuse a fidelity the ticket does not have")
def _(s):
    @s.given("billing-report's story map passed validate")
    def _(world):
        world.project.seed_session(BILLING_REPORT.with_log(*STORY_MAP_VALIDATED_CLEAN))

    @s.when("the Person reviews stories-no_such_fidelity")
    def _(world):
        world.refusal = refusal_of(lambda: world.Ticket.load(BILLING_REPORT.name).work.progress_of(NO_SUCH_FIDELITY).finish_review())

    @s.then("the board says no fidelity named stories-no_such_fidelity on ticket billing-report")
    def _(world):
        expect_refused(world.refusal, FidelityNotFoundError, "no fidelity named 'stories-no_such_fidelity' on ticket 'billing-report'")

    @s.but_("no review line is written for stories-story-map")
    def _(world):
        expect([line for line in log_lines(world, BILLING_REPORT) if " review " in line]).to(equal([]))


@shared_stories.scenario("Review Fidelity", "Complete a stage's work")
def _(s):
    @s.given("pet-visits has every Discovery fidelity generated, validated, and reviewed")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(*EVERY_DISCOVERY_FIDELITY_REVIEWED))

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("pet-visits waits in Discovery's Done")
    def _(world):
        expect_placed(world.read, "Discovery", is_done=True)

    @s.and_("it has no next step")
    def _(world):
        expect_no_next(world.read)
