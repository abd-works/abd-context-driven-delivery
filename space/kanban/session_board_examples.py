"""The named examples of the Session Board's scenarios, one fixture per example.

**Seed** examples are state the repository owns: a session's folder under `.sessions/` with its `session.json` and
`session.log`, an idea file in `.sessions/_backlog/`, the open session in `.sessions/session.json`, the WIP limits in
`.sessions/_board.json`, a file of the project, and the git checkout and its origin. The repository is the board's
storage boundary and no separate system stands behind it, so `SessionsProject` writes these where the board reads them,
the way `space/kanban/app/test-utils/fixture-repo.ts` writes the board app's fixture project.

**Interaction** examples are what a person types or chooses on the board: a title, an idea's text, a limit, a folder,
a fidelity. They are passed to the board's operations in a When.

The ticket names, titles, and log lines are those of `fixture-repo.ts` and of the scenarios in
`harness/.context/stories/move-work-forward-on-session-board/`, so the Python tiers and the board app agree on one example world.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path

import cdd_guidance.actions  # noqa: F401 - registers the actions and the practices, as the cdd server does when it loads every toolset
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's pattern overlays, as the cdd server does when it loads every toolset
from harness.process.git import Git
from harness.graph.saved_graph import SavedGraph, SavedNode, SavedPractice
from harness.graph.violation import Violation
from space.kanban.board import Board
from space.repo.mock_repo import MockGit
from space.session.throwaway_project import ThrowawayProject
from space.work_state import WorkState

STAMP = "2026-11-01T10:00:00Z"
STORY_MAP_FILE = ".context/story-map.md"
STORY_MAP_TEXT = "# Check Out Order\n\n## Payment\n\n- Enter Card Details\n- Handle Payment\n- Confirm Order\n"
STORY_MAP_REPORT = "stories-story-map-20261101T100000"


def saved_practice(practice: str, node_id: str, file: str, line: int, *hits: tuple[str, str]) -> SavedPractice:
    """Seed: one practice of a graph validate saved, as the saved graph keeps it: one story node at file and line, and
    each hit, a rule and its message, on that node."""
    node = SavedNode(node_id, "", "Story", practice, file, line, line, "", {})
    found = [Violation(rule, message, practice=practice, node_id=node_id, location=file, line=line, end_line=line) for rule, message in hits]
    return SavedPractice(practice, "", {}, [node], [], found)


def saved_graph(*practices: SavedPractice) -> dict:
    """Seed: the graph validate saves beside its report, in the shape the saved graph writes."""
    return SavedGraph([], {practice.name: practice for practice in practices}).document


STORY_MAP_GRAPH = saved_graph(saved_practice("stories", "node-1", STORY_MAP_FILE, 6, ("verb-noun-format", "Name the story with a verb")))
GRAPH_EXAMPLES = Path(__file__).resolve().parents[2] / "harness" / "graph" / "_examples" / "input"
ENTITY_ROOT_FILE = "src/account-credentials/account-credentials.ts"
STORY_FILE = "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts"


def generated(practice: str, fidelity: str, stamp: str = STAMP) -> str:
    """The line Generate writes on a fidelity, as the board app's fixture writes it."""
    return f"{stamp} generate /work {practice} {fidelity} markdown {practice} no-chat"


def validated(practice_class: str, fidelity: str, violations: str = "", stamp: str = STAMP) -> str:
    """The line Validate writes; violations names each graph-rule hit, and none is a clean validate."""
    return f"{stamp} validate {practice_class} {fidelity} {violations} no-chat".replace("  ", " ")


def every_action(practice: str, practice_class: str, fidelity: str) -> tuple[str, ...]:
    return (generated(practice, fidelity), validated(practice_class, fidelity))


DISCOVERY_FIDELITIES = (("stories", "Stories", "story_map"), ("ddd", "Ddd", "bounded_context"), ("ux", "Ux", "ia"), ("clean_engineering", "CleanEngineering", "modules"), ("bdd", "Bdd", "behavior"))
EVERY_DISCOVERY_FIDELITY_DONE = tuple(line for entry in DISCOVERY_FIDELITIES for line in every_action(*entry))
STORY_MAP_VALIDATED_CLEAN = (generated("stories", "story_map"), validated("Stories", "story_map"))
STORY_MAP_VIOLATION = f"graph-rule verb-noun-format {STORY_MAP_FILE}:6"
STORY_MAP_HELD_ON_VIOLATIONS = (generated("stories", "story_map"), validated("Stories", "story_map", STORY_MAP_VIOLATION))
MOVED_INTO_SPECIFICATION = f"{STAMP} move Specification no-chat"


@dataclass(frozen=True)
class SessionSeed:
    """Seed: a work session's folder as the board reads it. folder is where it sits under .sessions/: open, closed,
    _archive, or _backlog for a ticket moved back. workpath is a folder of the project the session chose to work in,
    such as `work` for the scenarios' /work; empty for a session that works in the whole project."""

    name: str
    title: str
    log: tuple[str, ...] = ()
    folder: str = ""
    fields: dict = field(default_factory=dict)
    workpath: str = ""

    def with_log(self, *lines: str) -> SessionSeed:
        return replace(self, log=tuple(lines))


@dataclass(frozen=True)
class BacklogFileSeed:
    """Seed: an idea file in .sessions/_backlog/; heading is empty for a file that has no # heading."""

    file_name: str
    heading: str
    text: str


@dataclass(frozen=True)
class ReportSeed:
    """Seed: a validation report Validate saved in a session's validation-reports, with the graph it checked beside it
    when graph is given."""

    name: str
    text: str = "# Graph rule validation\n"
    graph: dict | None = None


@dataclass(frozen=True)
class TicketTitle:
    """Interaction: what a person types to open a ticket, and the folder or parent they choose for it."""

    title: str
    scope: str = "feature"
    parent: str = ""
    path: str = ""


@dataclass(frozen=True)
class BacklogIdea:
    """Interaction: the title and text a person types into the new backlog item form."""

    title: str
    text: str


# --- Seed: sessions, idea files, and files the repository holds -------------------------------------------------

# The board app's fixture project (space/kanban/app/test-utils/fixture-repo.ts).
CHECKOUT_FLOW = SessionSeed("checkout-flow", "Checkout flow", STORY_MAP_HELD_ON_VIOLATIONS)
CHECKOUT_FLOW_REPORT = ReportSeed(STORY_MAP_REPORT, graph=STORY_MAP_GRAPH)
BILLING_REPORT = SessionSeed("billing-report", "Billing report")
MOVE_ME = SessionSeed("move-me", "Move me")
BACK_TO_BACKLOG = SessionSeed("back-to-backlog", "Back to backlog", (generated("stories", "story_map"),))
PRICING_RULES = SessionSeed("pricing-rules", "Pricing rules", (MOVED_INTO_SPECIFICATION, generated("stories", "scenarios"), validated("Stories", "scenarios")))
READY_TO_MOVE = SessionSeed("ready-to-move", "Ready to move", (f"{STAMP} done Discovery no-chat",))
SECOND_SPEC = SessionSeed("second-spec", "Second spec", (MOVED_INTO_SPECIFICATION,))
ALMOST_SHIPPED = SessionSeed("almost-shipped", "Almost shipped", (f"{STAMP} move Implementation no-chat", f"{STAMP} done Implementation no-chat"))
SHIPPED_WORK = SessionSeed("shipped-work", "Shipped work", folder="_complete")
SEARCH_THE_CATALOG = BacklogFileSeed("search-the-catalog.md", "Search the catalog", "An idea.")
SURFACE_FIXTURE_PROJECT = "cdd-board-surface-fixture"
SURFACE_FIXTURE_TICKETS = (CHECKOUT_FLOW, BILLING_REPORT, MOVE_ME, BACK_TO_BACKLOG, PRICING_RULES, READY_TO_MOVE, SECOND_SPEC, ALMOST_SHIPPED, SHIPPED_WORK)

# The scenarios' own sessions.
PET_VISITS = SessionSeed("pet-visits", "Pet visits")
SIGN_UP = SessionSeed("sign-up", "Sign up")
BROWSE_PETS = SessionSeed("browse-pets", "Browse pets", folder="_complete")
OLD_SPIKE = SessionSeed("old-spike", "Old spike", folder="_archive")
MAIN = SessionSeed("main", "Main")
BROKEN = SessionSeed("broken", "Broken")
BROKEN_SESSION_JSON = "{broken"
CHILD = SessionSeed("child", "child", fields={"scope": "story", "parent": "epic"})
ALPHA = SessionSeed("alpha", "Alpha", workpath="work")
GIFT_CARDS_HELD = SessionSeed("gift-cards", "Gift cards", (generated("stories", "story_map"),), folder="_backlog")
SIGN_UP_HELD = SessionSeed("sign-up", "Sign up", (f"{STAMP} move Discovery no-chat",), folder="_backlog")

# The scenarios' own child tickets: a session.json naming its parent, and one pulled out of it.
DONE_IN_DISCOVERY = f"{STAMP} done Discovery no-chat"
ENTER_CARD_DETAILS_CHILD = SessionSeed("enter-card-details", "Enter card details", fields={"scope": "story", "parent": "checkout-flow"})
ENTER_CARD_DETAILS_IN_SPECIFICATION = ENTER_CARD_DETAILS_CHILD.with_log(MOVED_INTO_SPECIFICATION)
ENTER_CARD_DETAILS_PULLED_OUT_DONE = replace(ENTER_CARD_DETAILS_CHILD.with_log(DONE_IN_DISCOVERY), fields={**ENTER_CARD_DETAILS_CHILD.fields, "pulled_out": True})
CONFIRM_ORDER_CHILD = SessionSeed("confirm-order", "Confirm order", fields={"scope": "story", "parent": "checkout-flow"})
CONFIRM_ORDER_DONE_IN_DISCOVERY = CONFIRM_ORDER_CHILD.with_log(DONE_IN_DISCOVERY)
CONFIRM_ORDER_PULLED_OUT_DONE = replace(CONFIRM_ORDER_DONE_IN_DISCOVERY, fields={**CONFIRM_ORDER_CHILD.fields, "pulled_out": True})
PULLED_OUT_TITLE = "Checkout flow.Enter card details"

# The scenarios' own session log lines.
GENERATED_STORY_MAP_IN_TWO_FOLDERS = f"{STAMP} generate /work, /work/docs stories story_map markdown stories no-chat"
GENERATED_UX_MOCKUP = f"{STAMP} generate /work/ux ux mockup html ux no-chat"

# The scenarios' own idea files.
GIFT_CARDS_HELD_FILE = BacklogFileSeed("gift-cards.md", "Gift cards", "Sell them at the till.")
SIGN_UP_HELD_FILE = BacklogFileSeed("sign-up.md", "Sign up", "")
RETURNS_AND_REFUNDS = BacklogFileSeed("returns-and-refunds.md", "Returns and refunds", "Refund an order.")
RETURNS_AND_REFUNDS_UNHEADED = BacklogFileSeed("returns-and-refunds.md", "", "Refund an order.")
GIFT_CARDS_IN_BACKLOG = BacklogFileSeed("gift-cards.md", "Gift cards", "Sell gift cards.")
# The text a ticket's idea file holds, its session folder's <name>.md.
CHECKOUT_FLOW_TEXT = "Pay for the basket."
CONFIRM_ORDER_TEXT = "Show the order and take the payment."


def idea_file_text(heading: str, text: str) -> str:
    """Seed: an idea file as a started backlog item leaves it in a session folder, its heading and its text."""
    return f"# {heading}\n\n{text}\n"

# The scenarios' own files in a session folder or the project.
LATEST_HANDOFF = "handoff-20261101T120000.md"
HANDOFF_TEXT = "# Handoff\n"
EARLIER_HANDOFF = "handoff-20261031T090000.md"
EARLIER_HANDOFF_TEXT = "# Earlier handoff\n"
SPEC_THEIRS = "src/theirs_spec.py"
SPEC_MINE = "src/mine_spec.py"
# The active ticket's work not yet committed, as kanban_tools_spec writes work.txt before a ticket is left, so leaving
# it has something to commit or to leave alone.
WORK_FILE = "work.txt"
WORK_TEXT = "Checkout flow work\n"

# --- Interaction: what a person types or chooses on the board ----------------------------------------------------

GIFT_CARDS_IDEA = BacklogIdea("Gift cards", "Sell gift cards.")
PET_VISITS_TICKET = TicketTitle("Pet visits")
BILLING_REPORT_ON_SRC_BILLING = TicketTitle("Billing report", path="src/billing")
ENTER_CARD_DETAILS = TicketTitle("Enter card details", scope="story", parent="checkout-flow")
STORY_MAP = "stories-story-map"
DISCOVERY_FIDELITY_SLUGS = tuple(f"{practice}-{fidelity}".replace("_", "-") for practice, _, fidelity in DISCOVERY_FIDELITIES)
DISCOVERY_LIMIT = 3
RAISED_DISCOVERY_LIMIT = 4
LOWERED_DISCOVERY_LIMIT = 2
VISITS_ROOT = "src/visits"
BILLING_ROOT = "src/billing"
OUTSIDE_FILE = "../secrets.txt"
NO_SUCH_TICKET = "no-such-ticket"
EDITED_CHECKOUT_FLOW_TEXT = "Pay for the basket by card."
PET_VISITS_TEXT = "Book a visit for a pet."
EDITED_GIFT_CARDS_TEXT = "Sell gift cards at the till."
EDITED_CONFIRM_ORDER_TEXT = "Show the order, then take the payment."
BILLING_TAG = "billing"
URGENT_TAG = "urgent"
NO_SUCH_FIDELITY = "stories-no_such_fidelity"

# --- What the board answers with ---------------------------------------------------------------------------------

# The commit Ticket.activate and Ticket.close make of the work of the ticket being left.
LEAVE_SESSION_COMMIT = "checkout-flow: leave session"


@cache
def _empty_repository() -> Path:
    """An empty git repository on main, with the spec's committer in its config and no sample hooks, made once for the
    process: every example that needs a checkout copies its .git folder rather than starting git to make one."""
    folder = Path(tempfile.mkdtemp(prefix="cdd-empty-repository-"))
    Git(folder).run("init", "-q", "-b", "main", "--template=")
    with (folder / ".git" / "config").open("a", encoding="utf-8") as config:
        config.write("[user]\n\tname = Story Spec\n\temail = story-spec@example.invalid\n")
    return folder / ".git"


# --- Review Files In Viewer: checkout-flow working in src/checkout, its order.py, and the comments on it -----------

CHECKOUT_FLOW_IN_SRC_CHECKOUT = SessionSeed("checkout-flow", "Checkout flow", workpath="src/checkout")
CHECKOUT_FLOW_IN_CONTEXT = SessionSeed("checkout-flow", "Checkout flow", workpath="harness/.context")
ORDER_FILE = "src/checkout/order.py"
PLACE_LINES = (
    "    def place(self, cart: Cart) -> Order:",
    "        if not cart.items:",
    "            raise EmptyCartError(cart.id)",
)
# Seed: order.py, the place lines at 12 to 14 and other code below them, so comments can sit on lines 30 and 40 too.
ORDER_TEXT = "".join(f"{line}\n" for line in (*[f"# order line {number}" for number in range(1, 12)], *PLACE_LINES, *[f"# order line {number}" for number in range(15, 42)]))
EDITED_LINE_14 = '            raise EmptyCartError(cart.id, "a cart needs one item to be placed")'
README_FILE = "src/checkout/README.md"
README_TEXT = "# Checkout\n"
CHECKOUT_CHAT = "checkout-chat"
# Seed: the graph checkout-flow saved in its folder, naming files from its root src/checkout: class Order on lines 5 to
# 41 of order.py, its operation place on 12 to 14, and one rule broken on place.
ORDER_CLASS_LINES = (5, 41)
ORDER_RULE = ("vocabulary-traces-to-source", "EmptyCartError should say which cart and why")
ORDER_GRAPH = SavedGraph([], {"clean_engineering": SavedPractice("clean_engineering", "", {}, [
    SavedNode("order", "Order", "OoadClass", "clean_engineering", "order.py", *ORDER_CLASS_LINES, "", {}),
    SavedNode("order-place", "place", "Operation", "clean_engineering", "order.py", 12, 14, "", {"owner": "Order"}),
], [], [Violation(*ORDER_RULE, practice="clean_engineering", node_id="order-place", location="order.py", line=12, end_line=14)])}).document


@dataclass(frozen=True)
class FileCommentExample:
    """Interaction: what a person selected in a file and the comment they wrote on it."""

    path: str
    start_line: int
    end_line: int
    selected_text: str
    text: str

    @property
    def anchor(self) -> str:
        return f"{self.path}:L{self.start_line}-L{self.end_line}"


EMPTY_CART_COMMENT = FileCommentExample(ORDER_FILE, 12, 14, "\n".join(PLACE_LINES), "an empty cart should say which cart and why")
LINE_30_COMMENT = FileCommentExample(ORDER_FILE, 30, 31, "# order line 30\n# order line 31", "name these lines")
LINE_40_COMMENT = FileCommentExample(ORDER_FILE, 40, 41, "# order line 40\n# order line 41", "drop these lines")
EMPTY_CART_FILL = "\n".join([
    "src/checkout/order.py:12-14: an empty cart should say which cart and why",
    *(f"> {12 + offset} | {line}" for offset, line in enumerate(PLACE_LINES)),
    "",
    "session=.sessions/checkout-flow/session.json",
])



def seed_checkout_flow(world) -> None:
    """Seed: checkout-flow working in src/checkout, holding order.py."""
    world.project.seed_session(CHECKOUT_FLOW_IN_SRC_CHECKOUT)
    world.project.seed_file(ORDER_FILE, ORDER_TEXT)


def seed_connected_chat(world) -> None:
    """Seed: the chat checkout-chat checked in, and assigned to checkout-flow."""
    world.Chat.load(CHECKOUT_CHAT).check_in(is_busy=False)
    world.Ticket.load(CHECKOUT_FLOW_IN_SRC_CHECKOUT.name).assign_chat(chat=CHECKOUT_CHAT)


def seed_file_comments(world, *comments: FileCommentExample, sent_to: str = "") -> None:
    """Seed: checkout-flow's file comments holding comments, each sent to the chat sent_to when it names one."""
    file_comments = world.Ticket.load(CHECKOUT_FLOW_IN_SRC_CHECKOUT.name).session.file_comments
    for comment in comments:
        file_comments.add(path=comment.path, start_line=comment.start_line, end_line=comment.end_line, text=comment.text)
        if sent_to:
            file_comments.send(anchor=comment.anchor, chat=sent_to)


def seed_comment_shown_in_chat(world) -> None:
    """Seed: the empty-cart comment sent to checkout-chat, which took it, showed it, and started a turn on it."""
    seed_checkout_flow(world)
    seed_connected_chat(world)
    seed_file_comments(world, EMPTY_CART_COMMENT, sent_to=CHECKOUT_CHAT)
    chat = world.Chat.load(CHECKOUT_CHAT)
    taken = world.data_of(chat.check_in(is_busy=False))
    chat.confirm(message=taken[0]["message"], is_shown=True)
    chat.check_in(is_busy=True)

class SessionsProject(ThrowawayProject):
    """A throwaway project named by CDD_PROJECT while a scenario runs, whose `.sessions/` and files a scenario seeds."""

    def __init__(self, name: str = "project", mocks_git: bool = False) -> None:
        super().__init__(name)
        self.sessions = self.root / ".sessions"
        self.sessions.mkdir(parents=True)
        # Real git for the tiers that prove it, else our Repo, Branch, and Worktrees mocked in memory.
        self.checkout: GitCheckout | MockCheckout = MockCheckout(self) if mocks_git else GitCheckout(self)

    def seed_session(self, seed: SessionSeed) -> Path:
        folder = self.sessions / seed.folder / seed.name
        folder.mkdir(parents=True, exist_ok=True)
        # A chosen workpath counts only when its folder is there (Sessions.root_of), so the seed makes it.
        workpath = self.root / seed.workpath
        workpath.mkdir(parents=True, exist_ok=True)
        fields = {"name": seed.name, "title": seed.title, "scope": "feature", "workpath": str(workpath), "repo_path": str(self.root), **seed.fields}
        (folder / "session.json").write_text(json.dumps(fields), encoding="utf-8")
        (folder / "session.log").write_text("".join(f"{line}\n" for line in seed.log), encoding="utf-8")
        return folder

    def seed_log_line(self, seed: SessionSeed, line: str) -> None:
        """Seed a line a prior action or move left at the end of the session's log."""
        with (self.sessions / seed.folder / seed.name / "session.log").open("a", encoding="utf-8") as log:
            log.write(f"{line}\n")

    def seed_session_fields(self, seed: SessionSeed, **fields: object) -> None:
        """Seed fields a person's choices saved in the session's session.json, such as a root or an output override."""
        path = self.sessions / seed.folder / seed.name / "session.json"
        path.write_text(json.dumps({**json.loads(path.read_text(encoding="utf-8")), **fields}), encoding="utf-8")

    def seed_session_json_text(self, seed: SessionSeed, text: str) -> None:
        (self.sessions / seed.folder / seed.name / "session.json").write_text(text, encoding="utf-8")

    def seed_backlog_file(self, item: BacklogFileSeed, folder: str = "") -> Path:
        path = self.sessions / "_backlog" / folder / item.file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        heading = f"# {item.heading}\n\n" if item.heading else ""
        path.write_text(f"{heading}{item.text}\n", encoding="utf-8")
        return path

    def seed_active(self, seed: SessionSeed) -> None:
        """The session saved as open, through WorkState, as Sessions.switch saves it."""
        WorkState(self.root).session = seed.name

    def seed_wip_limits(self, limits: dict[str, int]) -> None:
        Board.load(self.root).file.write_text(json.dumps({"wip_limits": limits}), encoding="utf-8")

    def seed_report(self, seed: SessionSeed, report: ReportSeed) -> Path:
        folder = self.sessions / seed.folder / seed.name / "validation-reports"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{report.name}.md").write_text(report.text, encoding="utf-8")
        if report.graph is not None:
            (folder / f"{report.name}.json").write_text(json.dumps(report.graph), encoding="utf-8")
        return folder / f"{report.name}.md"

    def seed_session_file(self, seed: SessionSeed, name: str, text: str) -> Path:
        path = self.sessions / seed.folder / seed.name / name
        path.write_text(text, encoding="utf-8")
        return path

    def seed_file(self, relative: str, text: str = "") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def seed_folders(self, *relatives: str) -> None:
        for relative in relatives:
            (self.root / relative).mkdir(parents=True, exist_ok=True)

    def seed_graph_example(self, relative: str) -> Path:
        """A file of the graph's example project, copied to the same path in this project."""
        return self.seed_file(relative, (GRAPH_EXAMPLES / relative).read_text(encoding="utf-8"))

    # Git: each seeds or asks the project's checkout, real git or the mocked one.

    def seed_git_checkout(self) -> None:
        """The project as a git checkout on main, its files committed. Session folders are the board's record and belong
        on main, so .sessions/ is tracked, as in a CDD repository; only the hook logs and chat injections are ignored."""
        self.seed_file(".gitignore", ".sessions/**/logs/\n.sessions/**/chat-injections/\n")
        self.checkout.seed_git_checkout()

    def seed_origin(self) -> None:
        """An origin beside the project, holding main."""
        self.checkout.seed_origin()

    def seed_branch(self, name: str, checked_out: bool = True, pushed: bool = False) -> None:
        self.checkout.seed_branch(name, checked_out, pushed)

    def seed_worktree(self, branch: str, folder: Path) -> None:
        """A new branch checked out in its own worktree at folder, as the Claude desktop app makes one."""
        self.checkout.seed_worktree(branch, folder)

    def current_branch(self, folder: Path | None = None) -> str:
        """The branch the project, or the checkout at folder, has checked out."""
        return self.checkout.current_branch(folder or self.root)

    def uncommitted(self, path: str = "") -> list[str]:
        """The files, or the file at path, the project has changed and not committed, as paths from its top."""
        return self.checkout.uncommitted(path)

    def origin_log(self, branch: str) -> list[str]:
        """The commit subjects origin holds on branch, newest first."""
        return self.checkout.origin_log(branch)

    def origin_files(self, branch: str, under: str) -> list[str]:
        """The files origin's branch holds under the path under, as paths from the top."""
        return self.checkout.origin_files(branch, under)

    def has_branch(self, name: str) -> bool:
        return self.checkout.has_branch(name)

    def origin_has_branch(self, name: str) -> bool:
        return self.checkout.origin_has_branch(name)


class GitCheckout:
    """The project's git, for real: the tiers that prove what the board does to a repository."""

    def __init__(self, project: SessionsProject) -> None:
        self._project = project

    def seed_git_checkout(self) -> None:
        shutil.copytree(_empty_repository(), self._project.root / ".git")
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "Fixture")

    def seed_origin(self) -> None:
        Git(self._project.folder).run("init", "-q", "--bare", str(self._origin))
        self._git("remote", "add", "origin", str(self._origin))
        self._git("push", "-q", "-u", "origin", "main")

    def seed_branch(self, name: str, checked_out: bool, pushed: bool) -> None:
        self._git("branch", name)
        if checked_out:
            self._git("checkout", "-q", name)
        if pushed:
            self._git("push", "-q", "-u", "origin", name)

    def seed_worktree(self, branch: str, folder: Path) -> None:
        self._git("worktree", "add", "-q", "-b", branch, str(folder))

    def current_branch(self, folder: Path) -> str:
        return Git(folder).run("rev-parse", "--abbrev-ref", "HEAD")

    def uncommitted(self, path: str) -> list[str]:
        listed = self._git("status", "--porcelain", *(["--", path] if path else [])).splitlines()
        return [line[3:].strip('"') for line in listed if line.strip()]

    def origin_log(self, branch: str) -> list[str]:
        return Git(self._origin).run("log", "--format=%s", branch).splitlines()

    def origin_files(self, branch: str, under: str) -> list[str]:
        return self._git("ls-tree", "-r", "--name-only", f"origin/{branch}", under).splitlines()

    def has_branch(self, name: str) -> bool:
        return bool(self._git("branch", "--list", name).strip())

    def origin_has_branch(self, name: str) -> bool:
        return bool(self._git("ls-remote", "--heads", "origin", name).strip())

    @property
    def _origin(self) -> Path:
        return self._project.folder / "origin.git"

    def _git(self, *arguments: str) -> str:
        return Git(self._project.root).run(*arguments)


class MockCheckout:
    """The project's git mocked: our Repo, Branch, and Worktrees answered from a *MockGit* held in memory, for the quick
    tiers, so no scenario starts git; what they do to a repository is proven against real git by the heavy tiers."""

    def __init__(self, project: SessionsProject) -> None:
        self._project = project
        self.held = MockGit(project.root)
        # The board finds the project's repository where it finds every checkout's, so it works on the mock from now on.
        self.held.serve(project.root)

    def seed_git_checkout(self) -> None:
        self.held.make_clone()

    def seed_origin(self) -> None:
        self.held.add_origin()

    def seed_branch(self, name: str, checked_out: bool, pushed: bool) -> None:
        self.held.add_branch(name)
        if checked_out:
            self.held.check_out(self.held.root, name)
        if pushed:
            self.held.push(name)

    def seed_worktree(self, branch: str, folder: Path) -> None:
        self.held.add_worktree(branch, folder)

    def current_branch(self, folder: Path) -> str:
        return self.held.branch_of(folder.resolve())

    def uncommitted(self, path: str) -> list[str]:
        return self.held.uncommitted(self.held.root, self.held.root / path if path else None)

    def origin_log(self, branch: str) -> list[str]:
        return list(reversed(self.held.origin_logs.get(branch, [])))

    def origin_files(self, branch: str, under: str) -> list[str]:
        return sorted(path for path in self.held.origin_trees.get(branch, {}) if path == under or path.startswith(f"{under}/"))

    def has_branch(self, name: str) -> bool:
        return self.held.has_branch(name)

    def origin_has_branch(self, name: str) -> bool:
        return self.held.origin_has_branch(name)


def seed_surface_fixture(project: SessionsProject) -> None:
    """The board app's fixture project: nine tickets, one backlog item, and the story map."""
    for seed in SURFACE_FIXTURE_TICKETS:
        project.seed_session(seed)
    project.seed_report(CHECKOUT_FLOW, CHECKOUT_FLOW_REPORT)
    project.seed_backlog_file(SEARCH_THE_CATALOG)
    project.seed_file(STORY_MAP_FILE, STORY_MAP_TEXT)


def seed_checkout_flow_held_on_violations(project: SessionsProject) -> None:
    """checkout-flow with its story map generated and validated with verb-noun-format on .context/story-map.md line 6,
    and that validation's report saved with its graph."""
    project.seed_file(STORY_MAP_FILE, STORY_MAP_TEXT)
    project.seed_session(CHECKOUT_FLOW)
    project.seed_report(CHECKOUT_FLOW, CHECKOUT_FLOW_REPORT)


def seed_checkout_flow_open(project: SessionsProject) -> None:
    """checkout-flow saved as the open session, the session Claude Code works in."""
    project.seed_session(CHECKOUT_FLOW)
    project.seed_active(CHECKOUT_FLOW)


def seed_checkout_flow_open_on_main(project: SessionsProject) -> None:
    """checkout-flow open on a git checkout that has main alone, with its work not yet committed."""
    project.seed_git_checkout()
    project.seed_file(WORK_FILE, WORK_TEXT)
    seed_checkout_flow_open(project)


def seed_checkout_flow_open_on_pushed_main(project: SessionsProject) -> None:
    """checkout-flow open on main, pushed to origin, with its work not yet committed: a session with no branch of its own."""
    project.seed_git_checkout()
    project.seed_origin()
    project.seed_file(WORK_FILE, WORK_TEXT)
    seed_checkout_flow_open(project)


def seed_checkout_flow_open_on_its_pushed_branch(project: SessionsProject) -> None:
    """checkout-flow open on its own branch, checked out and pushed to origin, with its work not yet committed."""
    project.seed_git_checkout()
    project.seed_origin()
    project.seed_branch(CHECKOUT_FLOW.name, checked_out=True, pushed=True)
    project.seed_file(WORK_FILE, WORK_TEXT)
    seed_checkout_flow_open(project)
