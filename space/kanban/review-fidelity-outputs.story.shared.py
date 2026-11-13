"""Review Fidelity Outputs: the shared scenarios the Python tiers replay.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md.
Map: .context/story-map.md#e-review-fidelity-outputs. Model: .context/kanban-model.md.

Steps reach the board only through the namespace a tier hands them (`world.Ticket`), so the domain spec and the cdd tools
spec replay the same steps.

Covered by the board app's TypeScript client specs in space/kanban/app, not here, because they have no Python
operation: List Ticket Files "Filter the tabs to the files the ticket's branch changed" and "Clear the changed-files
filter" (the page filters on each file's is_changed); every scenario of Browse Ticket Files By Practice (the practice
filters and the tabs grouped and colored by practice are the page's); Open Session Files From Details "Open the
workpath folder from the details" (file-manager.list). The Thens of the scenarios below that only the page shows (a
tab's color) are left to those specs too.

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
    NO_SUCH_FIDELITY,
    PET_VISITS,
    SPEC_MINE,
    SPEC_THEIRS,
    STORY_MAP,
    STORY_MAP_FILE,
    STORY_MAP_REPORT,
    STORY_MAP_TEXT,
    STORY_MAP_VALIDATED_CLEAN,
    generated,
    validated,
)
from space.kanban.story_test import SharedStories, expect_action, expect_no_next, expect_placed, expect_refused, refusal_of
from space.kanban.board import FidelityNotFoundError

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

    @s.then("the files panel shows a .context/story-map.md tab, as there")
    def _(world):
        expect(world.files["markdown"]).to(equal([{"path": STORY_MAP_FILE, "exists": True, "is_changed": False}]))

    @s.but_("no file of another fidelity shows")
    def _(world):
        expect(sorted(world.files)).to(equal(["drawio", "markdown"]))


@shared_stories.scenario("List Ticket Files", "List every file of the fidelity, changed or not")
def _(s):
    @s.given("the ticket pet-visits works on its own branch pet-visits")
    def _(world):
        # The repository's own spec is committed on main before pet-visits branches from it.
        world.project.seed_file(SPEC_THEIRS)
        world.project.seed_git_checkout()
        world.project.seed_branch(PET_VISITS.name, checked_out=True)
        world.project.seed_session(PET_VISITS)

    @s.and_("its bdd behavior files are src/theirs_spec.py and src/mine_spec.py, and its branch added src/mine_spec.py")
    def _(world):
        world.project.seed_file(SPEC_MINE)

    @s.when("the Person lists pet-visits' bdd behavior files")
    def _(world):
        world.files = world.data_of(world.Ticket.load(PET_VISITS.name).work.progress_of("bdd-behavior").files())

    @s.then("the tabs show src/theirs_spec.py and src/mine_spec.py")
    def _(world):
        # Each file says whether the branch changed it, which the changed-files filter on the page reads.
        changed = {entry["path"]: entry["is_changed"] for entry in world.files["python"]}
        expect(changed).to(equal({SPEC_MINE: True, SPEC_THEIRS: False}))


@shared_stories.scenario("View Fidelity Files", "Open one tab per format, colored by its practice, generated or not")
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

    @s.then("the tabs along the top show .context/story-map.md and .context/story-map.drawio, both in Stories' color")
    def _(world):
        expect([entry["path"] for entry in [*world.files["markdown"], *world.files["drawio"]]]).to(equal([STORY_MAP_FILE, ".context/story-map.drawio"]))

    @s.and_("the .context/story-map.md tab shows # Check Out Order")
    def _(world):
        expect(world.opened["text"].splitlines()[0]).to(equal("# Check Out Order"))

    @s.and_("the drawio tab says it is not generated yet")
    def _(world):
        expect(world.files["drawio"][0]["exists"]).to(equal(False))


@shared_stories.scenario("Open Session Files From Details", "Open the session folder from the session button")
def _(s):
    @s.given("the session button shows ticket checkout-flow's own session")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_report(CHECKOUT_FLOW, CHECKOUT_FLOW_REPORT)

    @s.but_("not main, and not expanded")
    def _(world):
        # The button is the ticket's own; main and the expanded card are the page's to tell apart.
        pass

    @s.when("the Person opens checkout-flow's session from its session button")
    def _(world):
        world.files = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.folder_files())

    @s.then("the file view shows .sessions/checkout-flow")
    def _(world):
        expect(world.files).to(contain({"path": f".sessions/{CHECKOUT_FLOW.name}/validation-reports/{STORY_MAP_REPORT}.md", "exists": True, "is_changed": False}))
