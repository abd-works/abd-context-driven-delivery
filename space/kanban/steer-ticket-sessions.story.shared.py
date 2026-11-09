"""Steer Ticket Sessions: the shared scenarios the Python tiers replay.

Scenarios: move-work-forward-on-session-board/steer-ticket-sessions/*/*_story.test.py.
Map: .context/story-map.md#e-steer-ticket-sessions. Model: .context/kanban-model.md.

Steps reach the board only through the World a tier hands them (`world.Ticket`, `world.BacklogItem`, `world.Board`),
so the domain spec and the cdd tools spec replay the same steps.

Covered by the board app's TypeScript client specs in space/kanban/app, not here, because they have no Python
operation: Add Backlog Item "Keep Add off with no title"; Open Ticket Session "Ask a chat to open a ticket", "Keep +
Ticket off with no chat"; Close Active Session "Close the active session from its card" (a slash command sent to the
chat); Activate Ticket "Cancel the switch"; Split Ticket Into Child Tickets "Keep Split off where nothing can take the
prompt", "Keep Split off on a closed ticket", "Keep Split off on a locked ticket", and the fill of the prompt in "Ask
the chat to split a ticket into child tickets"; Write Ticket Handoff (all three: the board app fills the chat's
prompt, and the chat's mod checks in). The Thens of the scenarios below that only the page shows (a selected card, a
dialog's choices as it opens, a toast's wording) are left to those specs too.
"""

from __future__ import annotations

import json
from pathlib import Path

from expects import be_false, be_none, be_true, contain, end_with, equal, expect

from space.kanban.session_board_examples import (
    ALMOST_SHIPPED,
    BACK_TO_BACKLOG,
    BILLING_REPORT,
    BILLING_REPORT_ON_SRC_BILLING,
    BILLING_ROOT,
    CHECKOUT_FLOW,
    EARLIER_HANDOFF,
    EARLIER_HANDOFF_TEXT,
    ENTER_CARD_DETAILS,
    GIFT_CARDS_IDEA,
    GIFT_CARDS_IN_BACKLOG,
    HANDOFF_TEXT,
    LATEST_HANDOFF,
    LEAVE_SESSION_COMMIT,
    MOVE_ME,
    NO_SUCH_TICKET,
    PET_VISITS,
    PET_VISITS_TICKET,
    READY_TO_MOVE,
    RETURNS_AND_REFUNDS,
    SECOND_SPEC,
    SHIPPED_WORK,
    SIGN_UP_HELD,
    SIGN_UP_HELD_FILE,
    VISITS_ROOT,
    generated,
    seed_checkout_flow_open_on_its_pushed_branch,
    seed_checkout_flow_open_on_main,
    seed_checkout_flow_open_on_pushed_main,
)
from space.kanban.story_test import (
    SharedStories,
    column_in,
    expect_active,
    expect_backlog,
    expect_commit_count,
    expect_placed,
    expect_refused,
    expect_session_folder,
    names_in,
    next_in,
    refusal_of,
    ticket_in,
)
from space.kanban.board import NotAStageError
from space.kanban.ticket import TicketNotFoundError

shared_stories = SharedStories("Steer Ticket Sessions")


def tickets_on(board: dict) -> list[str]:
    return [name for column in board["columns"] for name in names_in(column)]


@shared_stories.scenario("Add Backlog Item", "Add an idea to the Backlog")
def _(s):
    @s.given("the Backlog column has no backlog item titled Gift cards")
    def _(world):
        # A new project's Backlog holds no items.
        pass

    @s.when("the Person adds the backlog item Gift cards with the text Sell gift cards.")
    def _(world):
        world.BacklogItem.create(title=GIFT_CARDS_IDEA.title, text=GIFT_CARDS_IDEA.text)

    @s.then("the Backlog shows Gift cards with the text Sell gift cards.")
    def _(world):
        items = column_in(world.data_of(world.Board.load().show()), "Backlog")["items"]
        expect([(item["title"], item["text"]) for item in items]).to(equal([(GIFT_CARDS_IDEA.title, GIFT_CARDS_IDEA.text)]))


@shared_stories.scenario("Add Backlog Item", "Start a backlog item in a chosen folder")
def _(s):
    @s.given("the backlog item Gift cards is in the Backlog")
    def _(world):
        world.project.seed_backlog_file(GIFT_CARDS_IN_BACKLOG)

    @s.and_("the repository has the folders src/billing and src/visits")
    def _(world):
        world.project.seed_folders(BILLING_ROOT, VISITS_ROOT)

    @s.when("the Person starts Gift cards")
    def _(world):
        world.folders = world.Board.load().folders(path="")

    @s.then("the roots dialog lists the top folders of the repository")
    def _(world):
        expect(world.folders).to(equal(["src"]))

    @s.and_("Gift cards is still in the Backlog")
    def _(world):
        expect_backlog(world.data_of(world.Board.load().show()), [GIFT_CARDS_IN_BACKLOG.heading])

    @s.when("the Person chooses src/visits as its root")
    def _(world):
        world.started = world.data_of(world.BacklogItem.load(GIFT_CARDS_IN_BACKLOG.heading).start(path=VISITS_ROOT))

    @s.then("the ticket gift-cards is In progress in Discovery with root src/visits")
    def _(world):
        expect_placed(world.started, "Discovery", is_done=False)
        expect(world.started["session"]["workpath"]).to(equal(VISITS_ROOT))


@shared_stories.scenario("Add Backlog Item", "Keep the idea file with the new ticket")
def _(s):
    @s.given("the backlog item Returns and refunds is the file .sessions/_backlog/returns-and-refunds.md")
    def _(world):
        world.idea_file = world.project.seed_backlog_file(RETURNS_AND_REFUNDS)
        world.idea_text = world.idea_file.read_text(encoding="utf-8")

    @s.when("the Person starts Returns and refunds on the whole repository")
    def _(world):
        world.started = world.data_of(world.BacklogItem.load(RETURNS_AND_REFUNDS.heading).start(scope="feature"))

    @s.then("the ticket returns-and-refunds is In progress in Discovery")
    def _(world):
        expect_placed(world.started, "Discovery", is_done=False)

    @s.and_("its session folder holds returns-and-refunds.md, text and all")
    def _(world):
        kept = world.project.sessions / "returns-and-refunds" / RETURNS_AND_REFUNDS.file_name
        expect(kept.read_text(encoding="utf-8")).to(equal(world.idea_text))

    @s.and_("its session log names the item's file")
    def _(world):
        expect((world.project.sessions / "returns-and-refunds" / "session.log").read_text(encoding="utf-8")).to(contain(str(world.idea_file)))

    @s.but_("the Backlog no longer shows Returns and refunds")
    def _(world):
        expect_backlog(world.data_of(world.Board.load().show()), [])


@shared_stories.scenario("Add Backlog Item", "Bring a ticket back from the Backlog with its work")
def _(s):
    @s.given("the ticket sign-up was moved back out of Discovery and waits in the Backlog as the backlog item Sign up")
    def _(world):
        world.project.seed_backlog_file(SIGN_UP_HELD_FILE, folder=SIGN_UP_HELD.name)

    @s.and_("its folder .sessions/_backlog/sign-up/ keeps its session log")
    def _(world):
        world.project.seed_session(SIGN_UP_HELD)

    @s.when("the Person starts Sign up")
    def _(world):
        world.started = world.data_of(world.BacklogItem.load(SIGN_UP_HELD.title).start())

    @s.then("sign-up is back on the board with its session log and session.json")
    def _(world):
        folder = world.project.sessions / SIGN_UP_HELD.name
        back = (world.started["name"], (folder / "session.log").read_text(encoding="utf-8"), (folder / "session.json").is_file())
        expect(back).to(equal((SIGN_UP_HELD.name, f"{SIGN_UP_HELD.log[0]}\n", True)))

    @s.but_("no new ticket is opened")
    def _(world):
        expect(tickets_on(world.data_of(world.Board.load().show()))).to(equal([SIGN_UP_HELD.name]))


@shared_stories.scenario("Open Ticket Session", "Open a new ticket")
def _(s):
    @s.given("checkout-flow is the active ticket")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("the Person opens a new ticket titled Pet visits")
    def _(world):
        world.opened = world.data_of(world.Ticket.create(title=PET_VISITS_TICKET.title, scope=PET_VISITS_TICKET.scope))

    @s.then("pet-visits is In progress in Discovery, titled Pet visits")
    def _(world):
        expect_placed(world.opened, "Discovery", is_done=False)
        expect((world.opened["name"], world.opened["title"])).to(equal(("pet-visits", PET_VISITS_TICKET.title)))

    @s.and_("its next step is Generate on stories-story-map")
    def _(world):
        expect((world.opened["next"]["fidelity"]["slug"], next_in(world.opened)["next_action"])).to(equal(("stories-story-map", "generate")))

    @s.and_("checkout-flow is still the active ticket")
    def _(world):
        expect_active(world.data_of(world.Board.load().show()), CHECKOUT_FLOW.name)


@shared_stories.scenario("Open Ticket Session", "Open a ticket on a folder of the repository")
def _(s):
    @s.given("the repository has the folder src/billing")
    def _(world):
        world.project.seed_folders(BILLING_ROOT)

    @s.when("the Person opens a ticket titled Billing report on src/billing")
    def _(world):
        world.opened = world.data_of(world.Ticket.create(title=BILLING_REPORT_ON_SRC_BILLING.title, scope=BILLING_REPORT_ON_SRC_BILLING.scope, path=BILLING_REPORT_ON_SRC_BILLING.path))

    @s.then("billing-report's session works in src/billing")
    def _(world):
        saved = json.loads((world.project.sessions / "billing-report" / "session.json").read_text(encoding="utf-8"))
        expect(saved["workpath"]).to(equal(str((world.project.root / BILLING_ROOT).resolve())))

    @s.and_("the details show its root as src/billing")
    def _(world):
        expect(world.opened["session"]["workpath"]).to(equal(BILLING_ROOT))


@shared_stories.scenario("Open Ticket Session", "Choose a ticket's root")
def _(s):
    @s.given("checkout-flow works on the whole repository")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.and_("the repository has src/billing and src/visits under src")
    def _(world):
        world.project.seed_folders(BILLING_ROOT, VISITS_ROOT)

    @s.when("the Person browses src for checkout-flow's root")
    def _(world):
        world.folders = world.Board.load().folders(path="src")

    @s.then("the roots dialog lists src/billing and src/visits")
    def _(world):
        expect(world.folders).to(equal([BILLING_ROOT, VISITS_ROOT]))

    @s.when("the Person chooses src/visits as checkout-flow's root")
    def _(world):
        world.chosen = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.choose_workpath(path=VISITS_ROOT))

    @s.then("checkout-flow's root reads src/visits")
    def _(world):
        expect(world.chosen["workpath"]).to(equal(VISITS_ROOT))

    @s.and_("each practice's default root sits under src/visits")
    def _(world):
        expect(all(entry["root"].startswith(VISITS_ROOT) for entry in world.chosen["practices"].values())).to(be_true)


@shared_stories.scenario("Open Ticket Session", "Choose one practice's root and go back to its default")
def _(s):
    @s.given("checkout-flow's Stories practice writes under its default root")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.ticket = world.Ticket.load(CHECKOUT_FLOW.name)

    @s.when("the Person chooses src/billing for checkout-flow's Stories root")
    def _(world):
        world.chosen = world.data_of(world.ticket.session.practice("stories").choose_root(path=BILLING_ROOT))

    @s.then("the Stories root reads src/billing, chosen by the Person")
    def _(world):
        expect((world.chosen["root"], world.chosen["is_root_chosen"])).to(equal((BILLING_ROOT, True)))

    @s.and_("every other practice stays on its default root")
    def _(world):
        expect([name for name, entry in world.data_of(world.ticket)["session"]["practices"].items() if entry["is_root_chosen"]]).to(equal(["stories"]))

    @s.when("the Person puts Stories back on its default root")
    def _(world):
        world.chosen = world.data_of(world.ticket.session.practice("stories").use_default_root())

    @s.then("the Stories root is the default again")
    def _(world):
        expect(world.chosen["is_root_chosen"]).to(be_false)


@shared_stories.scenario("Close Active Session", "Complete the active ticket with its work committed")
def _(s):
    @s.given("checkout-flow is the active ticket, on its own branch")
    def _(world):
        seed_checkout_flow_open_on_its_pushed_branch(world.project)
        world.ticket = world.Ticket.load(CHECKOUT_FLOW.name)

    @s.when("the Person moves checkout-flow into Complete")
    def _(world):
        world.leaving = world.data_of(world.ticket.branch())

    @s.then("a dialog headed Close session Checkout flow offers commit and push, chosen")
    def _(world):
        expect(world.leaving["is_checked_out"]).to(be_true)

    @s.when("the Person confirms")
    def _(world):
        world.closed = world.data_of(world.ticket.close(leaving=["commit", "push"]))

    @s.then("checkout-flow shows in Complete and is selected")
    def _(world):
        expect(world.closed["column"]["name"]).to(equal("Complete"))

    @s.and_("a toast says Checkout flow: committed, pushed · Session Checkout flow closed")
    def _(world):
        expect(world.project.origin_log(CHECKOUT_FLOW.name)[0]).to(equal(LEAVE_SESSION_COMMIT))

    @s.and_("no ticket is active")
    def _(world):
        expect_active(world.data_of(world.Board.load().show()), None)


@shared_stories.scenario("Close Active Session", "Commit the closed session's folder and return to main")
def _(s):
    @s.given("checkout-flow is the active ticket, on its own branch, with its session folder tracked")
    def _(world):
        seed_checkout_flow_open_on_its_pushed_branch(world.project)
        # The fixture's checkout ignores .sessions/; a project that tracks it sees the folder move in git.
        world.project.seed_file(".gitignore", "")

    @s.when("the Person closes checkout-flow, committing and pushing")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).close(leaving=["commit", "push"])

    @s.then("nothing is left uncommitted")
    def _(world):
        expect(world.project.git("status", "--porcelain").strip()).to(equal(""))

    @s.and_("the checkout is back on main")
    def _(world):
        expect(world.project.git("branch", "--show-current").strip()).to(equal("main"))


@shared_stories.scenario("Close Active Session", "Offer to commit a branch open in its worktree")
def _(s):
    @s.given("checkout-flow is the active ticket, its branch open in its own worktree")
    def _(world):
        seed_checkout_flow_open_on_main(world.project)
        world.Ticket.load(CHECKOUT_FLOW.name).open_worktree()

    @s.when("the Person closes checkout-flow")
    def _(world):
        world.choices = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).close_choices())

    @s.then("the close dialog offers a handoff, and to commit and push checkout-flow")
    def _(world):
        expect((world.choices["branch"], world.choices["chosen"])).to(equal((CHECKOUT_FLOW.name, ["handoff", "commit", "push"])))


@shared_stories.scenario("Close Active Session", "Close a session whose work is on main")
def _(s):
    @s.given("checkout-flow is the active ticket, its work on main")
    def _(world):
        seed_checkout_flow_open_on_pushed_main(world.project)
        world.ticket = world.Ticket.load(CHECKOUT_FLOW.name)

    @s.when("the Person closes checkout-flow")
    def _(world):
        world.leaving = world.data_of(world.ticket.work_branch())

    @s.then("the close dialog offers to commit and push main")
    def _(world):
        expect((world.leaving["name"], world.leaving["is_checked_out"])).to(equal(("main", True)))

    @s.when("the Person confirms")
    def _(world):
        world.closed = world.data_of(world.ticket.close(leaving=["commit", "push"]))

    @s.then("main on origin holds the commit checkout-flow: leave session")
    def _(world):
        expect(world.project.origin_log("main")[0]).to(equal(LEAVE_SESSION_COMMIT))

    @s.and_("the checkout is still on main")
    def _(world):
        expect(world.project.git("branch", "--show-current").strip()).to(equal("main"))

    @s.and_("checkout-flow shows in Complete")
    def _(world):
        expect(world.closed["column"]["name"]).to(equal("Complete"))


@shared_stories.scenario("Close Active Session", "Write a handoff for the session being closed")
def _(s):
    @s.given("checkout-flow is the active ticket, its story map held on violations")
    def _(world):
        seed_checkout_flow_open_on_main(world.project)

    @s.when("the Person closes checkout-flow with Create handoff chosen")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).close(leaving=["handoff"])

    @s.then("checkout-flow's folder in .sessions/_complete holds a handoff")
    def _(world):
        world.handoffs = sorted((world.project.sessions / "_complete" / CHECKOUT_FLOW.name).glob("handoff-*.md"))
        expect(len(world.handoffs)).to(equal(1))

    @s.and_("the handoff names stories-story-map as what comes next")
    def _(world):
        expect(world.handoffs[0].read_text(encoding="utf-8")).to(contain("stories-story-map"))


@shared_stories.scenario("Close Active Session", "Complete a ticket that has no branch of its own")
def _(s):
    @s.given("checkout-flow is the active ticket")
    def _(world):
        seed_checkout_flow_open_on_main(world.project)

    @s.but_("it has no branch of its own")
    def _(world):
        # The checkout seeded above has main alone.
        pass

    @s.when("the Person moves checkout-flow into Complete and confirms")
    def _(world):
        world.closed = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).close(leaving=[]))

    @s.then("checkout-flow shows in Complete")
    def _(world):
        expect(world.closed["column"]["name"]).to(equal("Complete"))

    @s.and_("its folder is in .sessions/_complete/checkout-flow")
    def _(world):
        expect_session_folder(world.project.sessions, "_complete", CHECKOUT_FLOW.name)

    @s.but_("nothing is committed")
    def _(world):
        expect_commit_count(world.project, "HEAD", 1)


@shared_stories.scenario("Move Ticket", "Move a ticket on to the next column")
def _(s):
    @s.given("the ticket ready-to-move is in Discovery's Done")
    def _(world):
        world.project.seed_session(READY_TO_MOVE)

    @s.when("the Person moves ready-to-move on")
    def _(world):
        world.moved = world.data_of(world.Ticket.load(READY_TO_MOVE.name).move_next())

    @s.then("ready-to-move is In progress in Specification and selected")
    def _(world):
        expect_placed(world.moved, "Specification", is_done=False)

    @s.and_("its session log ends with move Specification")
    def _(world):
        log = (world.project.sessions / READY_TO_MOVE.name / "session.log").read_text(encoding="utf-8")
        expect(log.splitlines()[-1]).to(end_with(" move Specification"))


@shared_stories.scenario("Move Ticket", "Drag a ticket into a stage's Done whatever its work")
def _(s):
    @s.given("the ticket move-me is In progress in Discovery with nothing done")
    def _(world):
        world.project.seed_session(MOVE_ME)

    @s.when("the Person moves move-me into Implementation's Done")
    def _(world):
        world.moved = world.data_of(world.Ticket.load(MOVE_ME.name).move_to(stage="Implementation", done=True))

    @s.then("move-me shows in Implementation's Done and is selected")
    def _(world):
        expect_placed(world.moved, "Implementation", is_done=True)


@shared_stories.scenario("Move Ticket", "Move a ticket back to the previous column")
def _(s):
    @s.given("the ticket second-spec is In progress in Specification")
    def _(world):
        world.project.seed_session(SECOND_SPEC)

    @s.when("the Person moves second-spec back")
    def _(world):
        world.moved = world.data_of(world.Ticket.load(SECOND_SPEC.name).move_previous())

    @s.then("second-spec shows in Discovery's Done")
    def _(world):
        expect_placed(world.moved, "Discovery", is_done=True)


@shared_stories.scenario("Move Ticket", "Move a ticket into the Backlog with its work")
def _(s):
    @s.given("the ticket back-to-backlog is In progress in Discovery with its story map generated")
    def _(world):
        world.project.seed_session(BACK_TO_BACKLOG)

    @s.when("the Person moves back-to-backlog into the Backlog")
    def _(world):
        world.Ticket.load(BACK_TO_BACKLOG.name).move_to(stage="Backlog")

    @s.then("the Backlog shows the backlog item Back to backlog and it is selected")
    def _(world):
        expect_backlog(world.data_of(world.Board.load().show()), [BACK_TO_BACKLOG.title])

    @s.but_("no stage shows back-to-backlog")
    def _(world):
        expect(ticket_in(world.data_of(world.Board.load().show()), BACK_TO_BACKLOG.name)).to(be_none)


@shared_stories.scenario("Move Ticket", "Close a ticket moved on past Implementation")
def _(s):
    @s.given("the ticket almost-shipped is in Implementation's Done")
    def _(world):
        world.project.seed_session(ALMOST_SHIPPED)

    @s.and_("almost-shipped is not the active ticket")
    def _(world):
        # No session is saved as open in a new project.
        pass

    @s.when("the Person moves almost-shipped on into Complete")
    def _(world):
        world.moved = world.data_of(world.Ticket.load(ALMOST_SHIPPED.name).move_next())

    @s.then("almost-shipped shows in Complete")
    def _(world):
        expect(world.moved["column"]["name"]).to(equal("Complete"))

    @s.and_("its folder is in .sessions/_complete/almost-shipped")
    def _(world):
        expect_session_folder(world.project.sessions, "_complete", ALMOST_SHIPPED.name)


@shared_stories.scenario("Move Ticket", "Reopen a ticket moved back out of Complete")
def _(s):
    @s.given("the closed ticket shipped-work is in Complete")
    def _(world):
        world.project.seed_session(SHIPPED_WORK)

    @s.when("the Person moves shipped-work back")
    def _(world):
        world.moved = world.data_of(world.Ticket.load(SHIPPED_WORK.name).move_previous())

    @s.then("shipped-work shows in Implementation's Done")
    def _(world):
        expect_placed(world.moved, "Implementation", is_done=True)

    @s.and_("its folder is back in .sessions/shipped-work")
    def _(world):
        expect_session_folder(world.project.sessions, "", SHIPPED_WORK.name)


@shared_stories.scenario("Move Ticket", "Refuse a move into a column that is not a stage")
def _(s):
    @s.given("the ticket billing-report is In progress in Discovery")
    def _(world):
        world.project.seed_session(BILLING_REPORT)
        world.ticket = world.Ticket.load(BILLING_REPORT.name)

    @s.and_("billing-report is not the active ticket")
    def _(world):
        # No session is saved as open in a new project.
        pass

    @s.when("the Person tries to move billing-report into Complete")
    def _(world):
        world.refusal = refusal_of(lambda: world.ticket.move_to(stage="Complete"))

    @s.then("Complete does not take billing-report")
    def _(world):
        expect_refused(world.refusal, NotAStageError, "'Complete' is not a stage a ticket can be moved into")

    @s.and_("billing-report stays In progress in Discovery")
    def _(world):
        expect_placed(world.data_of(world.ticket), "Discovery", is_done=False)


@shared_stories.scenario("Activate Ticket", "Switch to another ticket, committing, pushing, and merging the one left")
def _(s):
    @s.given("checkout-flow is the active ticket, on its own branch pushed to origin")
    def _(world):
        seed_checkout_flow_open_on_its_pushed_branch(world.project)

    @s.and_("billing-report has no branch in the repository")
    def _(world):
        world.project.seed_session(BILLING_REPORT)
        world.ticket = world.Ticket.load(BILLING_REPORT.name)

    @s.when("the Person activates billing-report")
    def _(world):
        world.leaving = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).branch())
        world.opening = world.data_of(world.ticket.branch())

    @s.then("a dialog headed Switch from Checkout flow to Billing report offers commit and push, chosen, and merge, not chosen")
    def _(world):
        expect(world.leaving["is_checked_out"]).to(be_true)

    @s.and_("it offers a branch for billing-report, chosen")
    def _(world):
        expect(world.opening["exists"]).to(be_false)

    @s.when("the Person chooses merge and confirms")
    def _(world):
        world.ticket.activate(leaving=["commit", "push", "merge"], opening=["branch"])

    @s.then("billing-report is the active ticket with a thick orange outline")
    def _(world):
        expect_active(world.data_of(world.Board.load().show()), BILLING_REPORT.name)

    @s.and_("a toast says Checkout flow: committed, pushed, merged to main · Billing report: branch created · Billing report is now active")
    def _(world):
        left_and_opened = (world.project.origin_log("main")[0], world.project.git("rev-parse", "--abbrev-ref", "HEAD"))
        expect(left_and_opened).to(equal((LEAVE_SESSION_COMMIT, BILLING_REPORT.name)))


OUTSIDE_BRANCH = "claude/checkout-flow-cef4bc"
OTHER_OUTSIDE_BRANCH = "claude/checkout-flow-9a1b2c"


def seed_checkout_flow_on_an_outside_worktree(project) -> Path:
    """checkout-flow's work on a branch and worktree the Claude desktop app made, named as it names them, with
    checkout-flow's session recording neither."""
    seed_checkout_flow_open_on_pushed_main(project)
    folder = project.folder / "checkout-flow-cef4bc"
    project.git("worktree", "add", "-q", "-b", OUTSIDE_BRANCH, str(folder))
    return folder


def recorded_checkout(world) -> tuple[str, str]:
    fields = json.loads((world.project.sessions / CHECKOUT_FLOW.name / "session.json").read_text(encoding="utf-8"))
    return fields.get("branch", ""), str(Path(fields["worktree"]).resolve()) if fields.get("worktree") else ""


@shared_stories.scenario("Activate Ticket", "Find a branch and worktree made outside CDD")
def _(s):
    @s.given("checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree")
    def _(world):
        world.worktree = seed_checkout_flow_on_an_outside_worktree(world.project)

    @s.but_("checkout-flow's session records no branch or worktree")
    def _(world):
        # The session seeded above records only its name and folders.
        pass

    @s.when("the Person picks checkout-flow to open")
    def _(world):
        world.opening = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).open_choices())

    @s.then("the open dialog offers nothing to create")
    def _(world):
        expect(world.opening["choices"]).to(equal([]))

    @s.and_("checkout-flow's session records claude/checkout-flow-cef4bc and its worktree")
    def _(world):
        expect(recorded_checkout(world)).to(equal((OUTSIDE_BRANCH, str(world.worktree.resolve()))))


@shared_stories.scenario("Activate Ticket", "Correct a branch the session records wrongly")
def _(s):
    @s.given("checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree")
    def _(world):
        world.worktree = seed_checkout_flow_on_an_outside_worktree(world.project)

    @s.but_("checkout-flow's session records a branch the repository no longer has")
    def _(world):
        session = world.project.sessions / CHECKOUT_FLOW.name / "session.json"
        session.write_text(json.dumps({**json.loads(session.read_text(encoding="utf-8")), "branch": "gone-branch", "worktree": "C:/nowhere"}), encoding="utf-8")

    @s.when("the Person picks checkout-flow to open")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).open_choices()

    @s.then("checkout-flow's session records claude/checkout-flow-cef4bc and its worktree")
    def _(world):
        expect(recorded_checkout(world)).to(equal((OUTSIDE_BRANCH, str(world.worktree.resolve()))))


@shared_stories.scenario("Activate Ticket", "Say which branches could be the session's rather than guess")
def _(s):
    @s.given("the repository has the branches claude/checkout-flow-cef4bc and claude/checkout-flow-9a1b2c")
    def _(world):
        seed_checkout_flow_open_on_pushed_main(world.project)
        world.project.git("branch", OUTSIDE_BRANCH)
        world.project.git("branch", OTHER_OUTSIDE_BRANCH)

    @s.when("the Person picks checkout-flow to open")
    def _(world):
        world.opening = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).open_choices())

    @s.then("the open dialog names both branches")
    def _(world):
        expect(sorted(world.opening["candidate_branches"])).to(equal(sorted([OUTSIDE_BRANCH, OTHER_OUTSIDE_BRANCH])))

    @s.and_("checkout-flow's session records no branch")
    def _(world):
        expect(recorded_checkout(world)[0]).to(equal(""))


@shared_stories.scenario("Activate Ticket", "Merge the branch left into main and keep it")
def _(s):
    @s.given("checkout-flow is the active ticket, on its own branch pushed to origin")
    def _(world):
        seed_checkout_flow_open_on_its_pushed_branch(world.project)
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person activates billing-report, committing, pushing, and merging checkout-flow")
    def _(world):
        world.Ticket.load(BILLING_REPORT.name).activate(leaving=["commit", "push", "merge"], opening=[])

    @s.then("main on origin holds checkout-flow's work")
    def _(world):
        expect(world.project.origin_log("main")).to(contain(LEAVE_SESSION_COMMIT))

    @s.and_("the checkout-flow branch is still there")
    def _(world):
        expect(world.project.git("branch", "--list", CHECKOUT_FLOW.name).strip()).to(equal(CHECKOUT_FLOW.name))


@shared_stories.scenario("Activate Ticket", "Delete the branch left once it is merged")
def _(s):
    @s.given("checkout-flow is the active ticket, on its own branch pushed to origin")
    def _(world):
        seed_checkout_flow_open_on_its_pushed_branch(world.project)
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person activates billing-report, committing, pushing, and deleting checkout-flow's branch")
    def _(world):
        world.Ticket.load(BILLING_REPORT.name).activate(leaving=["commit", "push", "delete_branch"], opening=[])

    @s.then("main on origin holds checkout-flow's work")
    def _(world):
        expect(world.project.origin_log("main")).to(contain(LEAVE_SESSION_COMMIT))

    @s.and_("the checkout-flow branch is gone")
    def _(world):
        expect(world.project.git("branch", "--list", CHECKOUT_FLOW.name).strip()).to(equal(""))


@shared_stories.scenario("Activate Ticket", "Delete the worktree left")
def _(s):
    @s.given("checkout-flow is the active ticket, its branch open in its own worktree")
    def _(world):
        seed_checkout_flow_open_on_pushed_main(world.project)
        world.project.seed_session(BILLING_REPORT)
        world.worktree = Path(world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).open_worktree())["worktree"])

    @s.when("the Person activates billing-report, committing, pushing, and deleting checkout-flow's worktree")
    def _(world):
        (world.worktree / "worked.txt").write_text("work\n", encoding="utf-8")
        world.Ticket.load(BILLING_REPORT.name).activate(leaving=["commit", "push", "delete_worktree"], opening=[])

    @s.then("the worktree folder is gone")
    def _(world):
        expect(world.worktree.exists()).to(be_false)

    @s.and_("checkout-flow's work is on its branch on origin")
    def _(world):
        expect(world.project.origin_log(CHECKOUT_FLOW.name)[0]).to(equal(LEAVE_SESSION_COMMIT))


@shared_stories.scenario("Activate Ticket", "Write a handoff for the session being left")
def _(s):
    @s.given("checkout-flow is the active ticket")
    def _(world):
        seed_checkout_flow_open_on_main(world.project)
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person activates billing-report with Create handoff chosen")
    def _(world):
        world.Ticket.load(BILLING_REPORT.name).activate(leaving=["handoff"], opening=[])

    @s.then("checkout-flow's session folder holds a handoff")
    def _(world):
        expect(len(list((world.project.sessions / CHECKOUT_FLOW.name).glob("handoff-*.md")))).to(equal(1))

    @s.but_("billing-report's session folder holds none")
    def _(world):
        expect(list((world.project.sessions / BILLING_REPORT.name).glob("handoff-*.md"))).to(equal([]))


@shared_stories.scenario("Activate Ticket", "Activate a ticket when the active one has no branch")
def _(s):
    @s.given("checkout-flow is the active ticket")
    def _(world):
        seed_checkout_flow_open_on_main(world.project)
        world.project.seed_session(BILLING_REPORT)

    @s.but_("checkout-flow has no branch of its own")
    def _(world):
        # The checkout seeded above has main alone.
        pass

    @s.when("the Person activates billing-report with nothing chosen")
    def _(world):
        world.Ticket.load(BILLING_REPORT.name).activate(leaving=[], opening=[])

    @s.then("billing-report is the active ticket")
    def _(world):
        expect_active(world.data_of(world.Board.load().show()), BILLING_REPORT.name)

    @s.and_("the branch checked out is as it was")
    def _(world):
        expect(world.project.git("rev-parse", "--abbrev-ref", "HEAD")).to(equal("main"))

    @s.but_("nothing is committed")
    def _(world):
        expect_commit_count(world.project, "HEAD", 1)


@shared_stories.scenario("Activate Ticket", "Commit nothing when the ticket left is not checked out")
def _(s):
    @s.given("checkout-flow is the active ticket and has a branch")
    def _(world):
        seed_checkout_flow_open_on_main(world.project)
        world.project.seed_branch(CHECKOUT_FLOW.name, checked_out=False)
        world.project.seed_session(BILLING_REPORT)

    @s.but_("that branch is not checked out")
    def _(world):
        # The branch seeded above was created without being checked out.
        pass

    @s.when("the Person activates billing-report with commit chosen")
    def _(world):
        world.Ticket.load(BILLING_REPORT.name).activate(leaving=["commit"], opening=[])

    @s.then("billing-report is the active ticket")
    def _(world):
        expect_active(world.data_of(world.Board.load().show()), BILLING_REPORT.name)

    @s.but_("nothing is committed on checkout-flow's branch")
    def _(world):
        expect_commit_count(world.project, CHECKOUT_FLOW.name, 1)


@shared_stories.scenario("Activate Ticket", "Create the ticket's branch on activation")
def _(s):
    @s.given("the git repository has no branch billing-report")
    def _(world):
        world.project.seed_git_checkout()
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person activates billing-report with a new branch")
    def _(world):
        world.Ticket.load(BILLING_REPORT.name).activate(leaving=[], opening=["branch"])

    @s.then("the repository has the branch billing-report")
    def _(world):
        expect(world.project.git("branch", "--list", BILLING_REPORT.name)).to(contain(BILLING_REPORT.name))

    @s.and_("billing-report is the active ticket")
    def _(world):
        expect_active(world.data_of(world.Board.load().show()), BILLING_REPORT.name)


@shared_stories.scenario("Split Ticket Into Child Tickets", "Ask the chat to split a ticket into child tickets")
def _(s):
    # The chat connected here, and the prompt the board app fills in it, are the board app's; this scenario starts
    # where the chat opens the child ticket through ticket.create.
    @s.given("checkout-flow is the active ticket and a chat is connected")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("the chat opens a child ticket Enter card details with parent checkout-flow")
    def _(world):
        world.opened = world.data_of(world.Ticket.create(title=ENTER_CARD_DETAILS.title, scope=ENTER_CARD_DETAILS.scope, parent=ENTER_CARD_DETAILS.parent))

    @s.then("enter-card-details is In progress in Discovery")
    def _(world):
        expect_placed(world.opened, "Discovery", is_done=False)

    @s.and_("its details read enter-card-details · story of checkout-flow")
    def _(world):
        expect((world.opened["name"], world.opened["session"]["scope"], world.opened["session"]["parent"])).to(equal(("enter-card-details", "story", CHECKOUT_FLOW.name)))


@shared_stories.scenario("Archive Ticket", "Archive a ticket off the board")
def _(s):
    @s.given("the ticket pet-visits is In progress in Discovery with its story map generated")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(generated("stories", "story_map")))

    @s.when("the Person archives pet-visits")
    def _(world):
        world.Ticket.load(PET_VISITS.name).archive()

    @s.then("no column shows pet-visits")
    def _(world):
        expect(ticket_in(world.data_of(world.Board.load().show()), PET_VISITS.name)).to(be_none)

    @s.and_("its folder is in .sessions/_archive/pet-visits")
    def _(world):
        expect_session_folder(world.project.sessions, "_archive", PET_VISITS.name)


@shared_stories.scenario("Archive Ticket", "Refuse to archive a ticket the board does not have")
def _(s):
    @s.given("the board shows no ticket named no-such-ticket")
    def _(world):
        # A new project's board shows no tickets.
        pass

    @s.when("the Person archives no-such-ticket")
    def _(world):
        world.refusal = refusal_of(lambda: world.Ticket.load(NO_SUCH_TICKET).archive())

    @s.then("the board says no ticket named 'no-such-ticket' on the board")
    def _(world):
        expect_refused(world.refusal, TicketNotFoundError, "no ticket named 'no-such-ticket' on the board")

    @s.but_("nothing is moved to .sessions/_archive")
    def _(world):
        expect((world.project.sessions / "_archive").exists()).to(be_false)


@shared_stories.scenario("Display Latest Handoff", "Show the latest handoff")
def _(s):
    @s.given("checkout-flow's session folder holds handoff-20261101T120000.md and an earlier handoff")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session_file(CHECKOUT_FLOW, EARLIER_HANDOFF, EARLIER_HANDOFF_TEXT)
        world.project.seed_session_file(CHECKOUT_FLOW, LATEST_HANDOFF, HANDOFF_TEXT)
        world.ticket = world.Ticket.load(CHECKOUT_FLOW.name)

    @s.when("the Person selects checkout-flow")
    def _(world):
        world.selected = world.data_of(world.ticket)

    @s.then("the details read Latest handoff: .sessions/checkout-flow/handoff-20261101T120000.md")
    def _(world):
        expect(world.selected["session"]["handoff"]).to(equal(f".sessions/{CHECKOUT_FLOW.name}/{LATEST_HANDOFF}"))

    @s.when("the Person opens the handoff")
    def _(world):
        world.opened = world.data_of(world.ticket.session.read_file(path=world.selected["session"]["handoff"]))

    @s.then("the files panel shows the handoff in a tab with its text # Handoff")
    def _(world):
        expect(world.opened["text"]).to(equal(HANDOFF_TEXT))


@shared_stories.scenario("Display Latest Handoff", "Say a ticket has no handoff")
def _(s):
    @s.given("billing-report's session folder holds no handoff")
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person selects billing-report")
    def _(world):
        world.selected = world.data_of(world.Ticket.load(BILLING_REPORT.name))

    @s.then("the details say No handoff yet")
    def _(world):
        expect(world.selected["session"]["handoff"]).to(equal(""))
