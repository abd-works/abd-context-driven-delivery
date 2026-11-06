"""The named examples of the Session Board's scenarios, one fixture per example.

**Seed** examples are state the repository owns: a session's folder under `.sessions/` with its `session.json` and
`session.log`, an idea file in `.sessions/_backlog/`, the open session in `.sessions/session.json`, the WIP limits in
`.sessions/_board.json`, a file of the project, and the git checkout and its origin. The repository is the board's
storage boundary and no separate system stands behind it, so `SessionsProject` writes these where the board reads them,
the way `harness/kanban/app/test-utils/fixture-repo.ts` writes the board app's fixture project.

**Interaction** examples are what a person types or chooses on the board: a title, an idea's text, a limit, a folder,
a fidelity. They are passed to the board's operations in a When.

The ticket names, titles, and log lines are those of `fixture-repo.ts` and of the scenarios in
`move-work-forward-on-session-board/`, so the Python tiers and the board app agree on one example world.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path

from space.repo.repo import Repo
from space.session import Session
from space.work_state import WorkState

STAMP = "2026-11-01T10:00:00Z"
STORY_MAP_FILE = ".context/story-map.md"
STORY_MAP_TEXT = "# Check Out Order\n\n## Payment\n\n- Enter Card Details\n- Handle Payment\n- Confirm Order\n"
STORY_MAP_REPORT = "stories-story-map-20261101T100000"
STORY_MAP_GRAPH = {
    "practices": {
        "stories": {
            "nodes": [["node-1", "", "Story", "stories", STORY_MAP_FILE, 6, 6]],
            "rules": [["verb-noun-format", "node-1", "Name the story with a verb"]],
        },
    },
}
GRAPH_EXAMPLES = Path(__file__).resolve().parents[1] / "graph" / "_examples" / "input"
ENTITY_ROOT_FILE = "src/account-credentials/account-credentials.ts"
STORY_FILE = "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts"


def generated(practice: str, fidelity: str, stamp: str = STAMP) -> str:
    """The line Generate writes on a fidelity, as the board app's fixture writes it."""
    return f"{stamp} generate /work {practice} {fidelity} markdown {practice} no-chat"


def validated(practice_class: str, fidelity: str, violations: str = "", stamp: str = STAMP) -> str:
    """The line Validate writes; violations names each graph-rule hit, and none is a clean validate."""
    return f"{stamp} validate {practice_class} {fidelity} {violations} no-chat".replace("  ", " ")


def reviewed(practice: str, fidelity: str, stamp: str = STAMP) -> str:
    return f"{stamp} review /work {practice} {fidelity} markdown {practice} no-chat"


def every_action(practice: str, practice_class: str, fidelity: str) -> tuple[str, ...]:
    return (generated(practice, fidelity), validated(practice_class, fidelity), reviewed(practice, fidelity))


DISCOVERY_FIDELITIES = (("stories", "Stories", "story_map"), ("ddd", "Ddd", "bounded_context"), ("ux", "Ux", "ia"), ("clean_engineering", "CleanEngineering", "modules"), ("bdd", "Bdd", "behavior"))
EVERY_DISCOVERY_FIDELITY_REVIEWED = tuple(line for entry in DISCOVERY_FIDELITIES for line in every_action(*entry))
STORY_MAP_REVIEWED = every_action("stories", "Stories", "story_map")
STORY_MAP_VALIDATED_CLEAN = (generated("stories", "story_map"), validated("Stories", "story_map"))
STORY_MAP_VIOLATION = f"graph-rule verb-noun-format {STORY_MAP_FILE}:6"
STORY_MAP_HELD_ON_VIOLATIONS = (generated("stories", "story_map"), validated("Stories", "story_map", STORY_MAP_VIOLATION))
MOVED_INTO_SPECIFICATION = f"{STAMP} move Specification no-chat"


@dataclass(frozen=True)
class SessionSeed:
    """Seed: a work session's folder as the board reads it. folder is where it sits under .sessions/: open, closed,
    _archive, or _backlog for a ticket moved back."""

    name: str
    title: str
    log: tuple[str, ...] = ()
    folder: str = ""
    fields: dict = field(default_factory=dict)

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

# The board app's fixture project (harness/kanban/app/test-utils/fixture-repo.ts).
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
ALPHA_WORKPATH = "/work"
ALPHA = SessionSeed("alpha", "Alpha", fields={"workpath": ALPHA_WORKPATH})
GIFT_CARDS_HELD = SessionSeed("gift-cards", "Gift cards", (generated("stories", "story_map"),), folder="_backlog")
SIGN_UP_HELD = SessionSeed("sign-up", "Sign up", (f"{STAMP} move Discovery no-chat",), folder="_backlog")

# The scenarios' own session log lines.
GENERATED_STORY_MAP_IN_TWO_FOLDERS = f"{STAMP} generate /work, /work/docs stories story_map markdown stories no-chat"
GENERATED_UX_MOCKUP = f"{STAMP} generate /work/ux ux mockup html ux no-chat"
LOGGED_BEFORE_MOVES_WERE_NAMED_MOVE = (f"{STAMP} pull Specification no-chat", f"{STAMP} done Specification no-chat")

# The scenarios' own idea files.
GIFT_CARDS_HELD_FILE = BacklogFileSeed("gift-cards.md", "Gift cards", "Sell them at the till.")
SIGN_UP_HELD_FILE = BacklogFileSeed("sign-up.md", "Sign up", "")
RETURNS_AND_REFUNDS = BacklogFileSeed("returns-and-refunds.md", "Returns and refunds", "Refund an order.")
RETURNS_AND_REFUNDS_UNHEADED = BacklogFileSeed("returns-and-refunds.md", "", "Refund an order.")
GIFT_CARDS_IN_BACKLOG = BacklogFileSeed("gift-cards.md", "Gift cards", "Sell gift cards.")

# The scenarios' own files in a session folder or the project.
LATEST_HANDOFF = "handoff-20261101T120000.md"
HANDOFF_TEXT = "# Handoff\n"
EARLIER_HANDOFF = "handoff-20261031T090000.md"
EARLIER_HANDOFF_TEXT = "# Earlier handoff\n"
PET_VISITS_STORY_MAP_ROOT = "docs"
PET_VISITS_STORY_MAP_FILE = "docs/.context/story-map.md"
PET_VISITS_STORY_MAP_TEXT = "# Pet visits\n"
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
DISCOVERY_FIDELITY_SLUGS = tuple(f"{practice}-{fidelity}" for practice, _, fidelity in DISCOVERY_FIDELITIES)
DISCOVERY_LIMIT = 3
RAISED_DISCOVERY_LIMIT = 4
LOWERED_DISCOVERY_LIMIT = 2
VISITS_ROOT = "src/visits"
BILLING_ROOT = "src/billing"
OUTSIDE_FILE = "../secrets.txt"
NO_SUCH_TICKET = "no-such-ticket"
NO_SUCH_FIDELITY = "stories-no_such_fidelity"

# --- What the board answers with ---------------------------------------------------------------------------------

# The commit Ticket.activate and Ticket.close make of the work of the ticket being left.
LEAVE_SESSION_COMMIT = "checkout-flow: leave session"


class SessionsProject:
    """A throwaway project named by CDD_PROJECT while a scenario runs, whose `.sessions/` and files a scenario seeds."""

    def __init__(self, name: str = "project") -> None:
        self._parent = Path(tempfile.mkdtemp(prefix="session-board-story-"))
        self.root = (self._parent / name).resolve()
        self.sessions = self.root / ".sessions"
        self.sessions.mkdir(parents=True)
        self._saved = os.environ.get("CDD_PROJECT")
        os.environ["CDD_PROJECT"] = str(self.root)
        Session._current = None

    def close(self) -> None:
        Session._current = None
        if self._saved is None:
            os.environ.pop("CDD_PROJECT", None)
        else:
            os.environ["CDD_PROJECT"] = self._saved
        shutil.rmtree(self._parent, ignore_errors=True)

    def seed_session(self, seed: SessionSeed) -> Path:
        folder = self.sessions / seed.folder / seed.name
        folder.mkdir(parents=True, exist_ok=True)
        fields = {"name": seed.name, "title": seed.title, "scope": "feature", "workpath": str(self.root), "repo_path": str(self.root), **seed.fields}
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
        """The session saved as open, through WorkState, as Session.switch saves it."""
        WorkState(self.root).session = seed.name

    def seed_wip_limits(self, limits: dict[str, int]) -> None:
        Repo(self.root).board_file.write_text(json.dumps({"wip_limits": limits}), encoding="utf-8")

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

    def seed_git_checkout(self) -> None:
        """The project as a git checkout on main, its files committed and .sessions/ ignored, as fixture-repo.ts makes it."""
        self.seed_file(".gitignore", ".sessions/\n")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Story Spec")
        self.git("config", "user.email", "story-spec@example.invalid")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Fixture")

    def seed_origin(self) -> None:
        """A bare repository beside the project as its origin, holding main."""
        origin = self._parent / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(origin))
        self.git("push", "-q", "-u", "origin", "main")

    def seed_branch(self, name: str, checked_out: bool = True, pushed: bool = False) -> None:
        self.git("branch", name)
        if checked_out:
            self.git("checkout", "-q", name)
        if pushed:
            self.git("push", "-q", "-u", "origin", name)

    def seed_commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def git(self, *arguments: str, repository: Path | None = None) -> str:
        done = subprocess.run(["git", *arguments], cwd=repository or self.root, check=True, capture_output=True, text=True)
        return done.stdout.strip()

    def origin_log(self, branch: str) -> list[str]:
        """The commit subjects origin holds on branch, newest first."""
        return self.git("log", "--format=%s", branch, repository=self._parent / "origin.git").splitlines()


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


def seed_checkout_flow_open_on_its_pushed_branch(project: SessionsProject) -> None:
    """checkout-flow open on its own branch, checked out and pushed to origin, with its work not yet committed."""
    project.seed_git_checkout()
    project.seed_origin()
    project.seed_branch(CHECKOUT_FLOW.name, checked_out=True, pushed=True)
    project.seed_file(WORK_FILE, WORK_TEXT)
    seed_checkout_flow_open(project)
