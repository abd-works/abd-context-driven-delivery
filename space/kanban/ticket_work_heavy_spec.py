"""Heavy spec: a ticket's work through a real cdd server, on a clone with its own origin, as chats meet it.

Opening, pushing, pulling, switching, and closing tickets on branches and in worktrees, each checked against git. The
examples run in order, as one person's day of work: each context acts once, then its examples look at the result."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.mcp.spec_support import SpecChat, SpecServer

TOOLSETS = (
    "space.kanban.board:Board",
    "space.kanban.board:Stage",
    "space.kanban.ticket:Ticket",
    "space.kanban.ticket:FidelityProgress",
    "space.session.session:Session",
    "space.session.sessions:Sessions",
    "space.session.practices.practice_session_output:PracticeSessionOutput",
    "space.repo.repo:Repo",
    # The board lists every practice's fidelities; importing one practice registers them all.
    "cdd_guidance.practices.stories.stories:Stories",
    # A stage's steps are the actions registered for it; importing one action registers them all.
    "cdd_guidance.actions.generate.generate:Generate",
)
# A process id no running Claude Code has, for a chat process this spec writes the session file of.
MOVED_CHAT_PROCESS = "999999"


def git(folder: Path, *arguments: str) -> str:
    return subprocess.run(["git", *arguments], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()


class TicketClone:
    """A bare origin, the clone a person works in, and another clone that pushes from elsewhere."""

    def __init__(self) -> None:
        self.top = Path(tempfile.mkdtemp(prefix="cdd-ticket-work-"))
        self.origin = self.top / "origin.git"
        self.work = self.top / "work"
        self.other = self.top / "other"
        git(self.top, "init", "-q", "--bare", "-b", "main", str(self.origin))
        git(self.top, "clone", "-q", str(self.origin), str(self.work))
        self._as_person(self.work, "work")
        (self.work / "README.md").write_text("# Work\n", encoding="utf-8")
        git(self.work, "checkout", "-q", "-b", "main")
        git(self.work, "add", "-A")
        git(self.work, "commit", "-q", "-m", "start")
        git(self.work, "push", "-q", "-u", "origin", "main")
        git(self.top, "clone", "-q", str(self.origin), str(self.other))
        self._as_person(self.other, "elsewhere")

    def _as_person(self, folder: Path, name: str) -> None:
        git(folder, "config", "user.name", name)
        git(folder, "config", "user.email", f"{name}@example.test")

    @property
    def branch(self) -> str:
        return git(self.work, "rev-parse", "--abbrev-ref", "HEAD")

    def branches(self) -> list[str]:
        return git(self.work, "branch", "--format=%(refname:short)").splitlines()

    def origin_branches(self) -> list[str]:
        refs = git(self.top, "--git-dir", str(self.origin), "for-each-ref", "--format=%(refname:short)", "refs/heads")
        return refs.splitlines()

    def subject(self, ref: str = "HEAD", folder: Path | None = None) -> str:
        return git(folder or self.work, "log", "-1", "--format=%s", ref)

    def subjects(self, ref: str) -> list[str]:
        return git(self.work, "log", "--format=%s", ref).splitlines()

    def tracked(self, ref: str, path: str) -> list[str]:
        return git(self.work, "ls-tree", "-r", "--name-only", ref, path).splitlines()

    def worktree_of(self, branch: str) -> Path | None:
        for block in git(self.work, "worktree", "list", "--porcelain").split("\n\n"):
            lines = block.splitlines()
            if f"branch refs/heads/{branch}" in lines:
                return Path(lines[0].removeprefix("worktree "))
        return None

    def push_from_elsewhere(self, branch: str, file: str, text: str, message: str) -> None:
        git(self.other, "fetch", "-q", "origin")
        git(self.other, "checkout", "-q", "-B", branch, f"origin/{branch}")
        (self.other / file).write_text(text, encoding="utf-8")
        git(self.other, "add", "-A")
        git(self.other, "commit", "-q", "-m", message)
        git(self.other, "push", "-q", "origin", branch)

    def remove(self) -> None:
        shutil.rmtree(self.top, ignore_errors=True)


def board_tickets(board: dict) -> set[str]:
    return {ticket["name"] for column in board["columns"] for key in ("in_progress", "done", "tickets") for ticket in column.get(key, [])}


with description("a ticket's work through the cdd server") as self:
    with before.all:
        self.config = Path(tempfile.mkdtemp(prefix="cdd-claude-config-"))
        self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
        self.server = SpecServer(TOOLSETS)
        self.server.start()
        self.clone = TicketClone()
        self.chat = SpecChat(self.server, self.clone.work)

    with after.all:
        self.server.stop()
        self.clone.remove()
        shutil.rmtree(self.config, ignore_errors=True)
        if self.prior_config is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

    with context("in a new clone"):
        with it("should have main open"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("main"))

    # (S) Person --> Open Ticket Session
    with context("that a ticket is created"):
        with before.all:
            self.created = self.chat.answer("ticket.create", title="Walk worktree")

        with it("should name the ticket after its title"):
            expect(self.created["name"]).to(equal("walk-worktree"))

        with it("should make its session folder"):
            expect((self.clone.work / ".sessions" / "walk-worktree" / "session.json").is_file()).to(be_true)

    # (S) Person --> Activate Ticket
    with context("that the ticket is opened in its own worktree"):
        with before.all:
            self.chat.answer("ticket.activate", ticket="walk-worktree")
            self.worktree = self.clone.worktree_of("walk-worktree")
            self.ticket_chat = SpecChat(self.server, self.worktree)

        with it("should make a worktree on its branch"):
            expect(self.worktree is not None and self.worktree.is_dir()).to(be_true)

        with it("should leave the clone's own folder on main"):
            expect(self.clone.branch).to(equal("main"))

        with it("should keep main as the session of the chat that opened it"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("main"))

        with it("should give a chat in the worktree the ticket's session"):
            expect(self.ticket_chat.answer("sessions.current")["name"]).to(equal("walk-worktree"))

        with it("should keep its session folder in the clone's own .sessions"):
            expect((self.clone.work / ".sessions" / "walk-worktree" / "session.json").is_file()).to(be_true)

    # (S) Repo --> Push Branch
    with context("that work is pushed from the worktree"):
        with before.all:
            self.worktree = self.clone.worktree_of("walk-worktree")
            (self.worktree / "feature.txt").write_text("first\n", encoding="utf-8")
            SpecChat(self.server, self.worktree).answer("repo.push_commit", message="Add feature", untracked=True, sync_remote=True)

        with it("should commit the work on the worktree's branch"):
            expect(self.clone.subject(folder=self.worktree)).to(equal("Add feature"))

        with it("should push the branch to origin"):
            expect(self.clone.subject("origin/walk-worktree")).to(equal("Add feature"))

        with it("should leave main without that commit"):
            expect(self.clone.subjects("main")).not_to(contain("Add feature"))

        # The ticket's record lives on main; its branch carries the session's work folder, its log and the rest.
        with it("should carry its session's work folder on the ticket's branch"):
            changed = git(self.clone.work, "diff", "--name-only", "main...walk-worktree").splitlines()
            expect(changed).to(contain(".sessions/walk-worktree/session.log"))

        with it("should carry no session files but its work folder's on the ticket's branch"):
            changed = git(self.clone.work, "diff", "--name-only", "main...walk-worktree").splitlines()
            expect([path for path in changed if path.startswith(".sessions/") and not path.startswith(".sessions/walk-worktree/")]).to(equal([]))

        with it("should carry no record on the ticket's branch"):
            changed = git(self.clone.work, "diff", "--name-only", "main...walk-worktree").splitlines()
            expect(changed).not_to(contain(".sessions/walk-worktree/session.json"))

    with context("that work was pushed to its branch from elsewhere"):
        with before.all:
            self.worktree = self.clone.worktree_of("walk-worktree")
            self.clone.push_from_elsewhere("walk-worktree", "elsewhere.txt", "from elsewhere\n", "Change from elsewhere")
            (self.worktree / "feature.txt").write_text("second\n", encoding="utf-8")
            SpecChat(self.server, self.worktree).answer("repo.push_commit", message="Change feature", untracked=True, sync_remote=True)

        with it("should bring that work in"):
            expect((self.worktree / "elsewhere.txt").is_file()).to(be_true)

        with it("should push its own commit after it"):
            expect(self.clone.subjects("origin/walk-worktree")).to(contain("Change feature", "Change from elsewhere"))

    # (S) Person --> Close Ticket
    with context("that the ticket is closed, its branch merged and deleted"):
        with before.all:
            self.worktree = self.clone.worktree_of("walk-worktree")
            leaving = ["handoff", "commit", "push", "merge", "delete_branch", "delete_worktree"]
            self.chat.answer("ticket.close", ticket="walk-worktree", leaving=leaving)

        with it("should remove the worktree"):
            expect(self.worktree.exists()).to(equal(False))

        with it("should merge its work into main"):
            expect(((self.clone.work / "feature.txt").is_file(), (self.clone.work / "elsewhere.txt").is_file())).to(equal((True, True)))

        with it("should delete its branch here"):
            expect(self.clone.branches()).not_to(contain("walk-worktree"))

        with it("should delete its branch on origin"):
            expect(self.clone.origin_branches()).not_to(contain("walk-worktree"))

        with it("should move its session among the closed sessions"):
            expect((self.clone.work / ".sessions" / "_complete" / "walk-worktree").is_dir()).to(be_true)

        with it("should leave main the session of the chat that closed it"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("main"))

        with it("should commit the closed ticket's record on main"):
            expect(self.clone.tracked("origin/main", ".sessions/_complete/walk-worktree")).to(contain(".sessions/_complete/walk-worktree/session.json"))

        # The branch merges first, so its work folder lands beside the record and moves with it.
        with it("should take its merged work along among the closed sessions on main"):
            expect(self.clone.tracked("origin/main", ".sessions/_complete/walk-worktree")).to(contain(".sessions/_complete/walk-worktree/session.log"))

        with it("should leave nothing of it among the open sessions on main"):
            expect(self.clone.tracked("origin/main", ".sessions/walk-worktree")).to(equal([]))

    # Another ticket is another chat and worktree: nothing is left or moved.
    with context("that a person opens two tickets, each worked on in its own chat"):
        with before.all:
            for title in ("Walk one", "Walk two"):
                self.chat.answer("ticket.create", title=title)
            self.chat.answer("ticket.activate", ticket="walk-one")
            self.chat.answer("ticket.activate", ticket="walk-two")
            one, two = self.clone.worktree_of("walk-one"), self.clone.worktree_of("walk-two")
            self.sessions_of = (SpecChat(self.server, one).answer("sessions.current")["name"], SpecChat(self.server, two).answer("sessions.current")["name"])
            (one / "one.txt").write_text("one\n", encoding="utf-8")
            SpecChat(self.server, one).answer("repo.push_commit", message="Work on one", untracked=True, sync_remote=True)
            self.board_with_both = board_tickets(self.chat.answer("board.show"))
            self.chat.answer("ticket.activate", ticket="walk-one")
            self.one_again = self.clone.worktree_of("walk-one")
            self.one = one
            leaving = ["commit", "push", "merge", "delete_branch", "delete_worktree"]
            for ticket in ("walk-one", "walk-two"):
                self.chat.answer("ticket.close", ticket=ticket, leaving=leaving)

        with it("should give each ticket's chat its own ticket"):
            expect(self.sessions_of).to(equal(("walk-one", "walk-two")))

        with it("should keep both tickets on the board"):
            expect(self.board_with_both).to(contain("walk-one", "walk-two"))

        with it("should open the first ticket again in the worktree it has"):
            expect(self.one_again).to(equal(self.one))

        with it("should bring the work of each closed ticket to main"):
            expect(self.clone.tracked("origin/main", "one.txt")).to(contain("one.txt"))

        with it("should delete both branches once closed"):
            expect(self.clone.branches()).not_to(contain("walk-one", "walk-two"))

        with it("should keep the clone's own folder on main throughout"):
            expect(self.clone.branch).to(equal("main"))

    # (S) Person --> Close Ticket
    with context("that origin's main moved on before a ticket is closed with its branch merged"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk land")
            self.chat.answer("ticket.activate", ticket="walk-land")
            worktree = self.clone.worktree_of("walk-land")
            (worktree / "land.txt").write_text("land\n", encoding="utf-8")
            SpecChat(self.server, worktree).answer("repo.push_commit", message="Land it", untracked=True, sync_remote=True)
            self.clone.push_from_elsewhere("main", "on-main.txt", "pushed to main elsewhere\n", "Main from elsewhere")
            self.chat.answer("ticket.close", ticket="walk-land", leaving=["commit", "push", "merge", "delete_branch"])

        with it("should bring origin's change into main"):
            expect((self.clone.work / "on-main.txt").is_file()).to(be_true)

        with it("should merge the ticket's branch into main"):
            expect((self.clone.work / "land.txt").is_file()).to(be_true)

        with it("should push main with both"):
            expect(self.clone.subjects("origin/main")).to(contain("Main from elsewhere", "Land it"))

    # (S) Repo --> Push Commit
    with context("that a push from a ticket's chat meets a real conflict"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk conflict")
            self.chat.answer("ticket.activate", ticket="walk-conflict")
            worktree = self.clone.worktree_of("walk-conflict")
            ticket_chat = SpecChat(self.server, worktree)
            (worktree / "shared.txt").write_text("mine\n", encoding="utf-8")
            ticket_chat.answer("repo.push_commit", message="Mine", untracked=True, sync_remote=True)
            self.clone.push_from_elsewhere("walk-conflict", "shared.txt", "theirs\n", "Theirs")
            (worktree / "shared.txt").write_text("mine again\n", encoding="utf-8")
            _, self.error = ticket_chat.call("repo.push_commit", message="Mine again", untracked=True, sync_remote=True)
            # A linked worktree keeps its merge state in its own git folder.
            self.merging = (Path(git(worktree, "rev-parse", "--absolute-git-dir")) / "MERGE_HEAD").exists()
            self.kept = self.clone.subject(folder=worktree)
            git(worktree, "reset", "-q", "--hard", "origin/walk-conflict")
            self.chat.answer("ticket.close", ticket="walk-conflict", leaving=["delete_branch"])

        with it("should refuse the push, naming the conflict"):
            expect(self.error.lower()).to(contain("conflict"))

        with it("should leave no merge half done"):
            expect(self.merging).to(equal(False))

        with it("should keep the commit made in the worktree"):
            expect(self.kept).to(equal("Mine again"))

        with it("should keep the clone's own folder on main"):
            expect(self.clone.branch).to(equal("main"))

    # (S) Person --> Close Active Session
    with context("that a ticket is closed with its branch merged while the clone's own folder holds an edit nobody committed"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk beside")
            self.chat.answer("ticket.activate", ticket="walk-beside")
            (self.clone.worktree_of("walk-beside") / "beside.txt").write_text("the ticket's work\n", encoding="utf-8")
            (self.clone.work / "README.md").write_text("# Work\nthe person's own edit\n", encoding="utf-8")
            self.chat.answer("ticket.close", ticket="walk-beside", leaving=["commit", "push", "merge", "delete_branch", "delete_worktree"])
            self.left_uncommitted = git(self.clone.work, "status", "--porcelain", "--", "README.md")
            self.readme_on_origin = git(self.clone.work, "show", "origin/main:README.md")
            git(self.clone.work, "checkout", "-q", "--", "README.md")

        with it("should bring the ticket's work to main on origin"):
            expect(self.clone.tracked("origin/main", "beside.txt")).to(equal(["beside.txt"]))

        with it("should leave the person's edit uncommitted in the clone's own folder"):
            expect(self.left_uncommitted).to(equal("M README.md"))

        with it("should keep the person's edit off origin's main"):
            expect(self.readme_on_origin).not_to(contain("the person's own edit"))

    # (S) Person --> Close Active Session
    # Exploratory testing, gizmo-17: the person's own edit in the clone's folder was committed on main under the
    # ticket's name and pushed.
    with context("that a ticket is closed with its branch merged while the clone's own folder holds an uncommitted edit to a file the ticket changed"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk overlap")
            self.chat.answer("ticket.activate", ticket="walk-overlap")
            self.overlap_worktree = self.clone.worktree_of("walk-overlap")
            (self.overlap_worktree / "README.md").write_text("# Work\nthe ticket's line\n", encoding="utf-8")
            (self.clone.work / "README.md").write_text("# Work\nthe person's own line\n", encoding="utf-8")
            self.main_before = git(self.clone.work, "rev-parse", "main")
            _, self.error = self.chat.call("ticket.close", ticket="walk-overlap", leaving=["commit", "push", "merge", "delete_branch", "delete_worktree"])
            self.main_after = git(self.clone.work, "rev-parse", "main")
            self.left_uncommitted = git(self.clone.work, "status", "--porcelain", "--", "README.md")
            self.readme_on_origin = git(self.clone.work, "show", "origin/main:README.md")
            self.ticket_head = self.clone.subject("walk-overlap")
            self.still_open = (self.clone.work / ".sessions" / "walk-overlap" / "session.json").is_file()
            self.worktree_kept = self.overlap_worktree.is_dir() and self.clone.worktree_of("walk-overlap") == self.overlap_worktree
            git(self.clone.work, "checkout", "-q", "--", "README.md")
            self.chat.answer("ticket.close", ticket="walk-overlap", leaving=["delete_branch"])

        with it("should refuse the close, naming the file the clone's own folder holds uncommitted"):
            expect(self.error).to(contain("walk-overlap is not closed: the repository's own folder holds uncommitted changes to README.md"))

        with it("should leave the person's edit uncommitted in the clone's own folder"):
            expect(self.left_uncommitted).to(equal("M README.md"))

        with it("should commit nothing on main"):
            expect(self.main_after).to(equal(self.main_before))

        with it("should keep the person's edit off origin's main"):
            expect(self.readme_on_origin).not_to(contain("the person's own line"))

        with it("should commit nothing of the ticket's work, since the close changed nothing"):
            expect(self.ticket_head).not_to(equal("walk-overlap: leave session"))

        with it("should keep the ticket's worktree"):
            expect(self.worktree_kept).to(be_true)

        with it("should keep the ticket among the open sessions"):
            expect(self.still_open).to(be_true)

    # (S) Person --> Close Active Session
    with context("that a ticket is closed with its branch merged into a main it conflicts with"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk clash")
            self.chat.answer("ticket.activate", ticket="walk-clash")
            self.clash_worktree = self.clone.worktree_of("walk-clash")
            (self.clash_worktree / "clash.txt").write_text("the ticket's line\n", encoding="utf-8")
            self.clone.push_from_elsewhere("main", "clash.txt", "main's line\n", "Main's line")
            _, self.error = self.chat.call("ticket.close", ticket="walk-clash", leaving=["commit", "push", "merge", "delete_branch", "delete_worktree"])
            self.merging = (self.clone.work / ".git" / "MERGE_HEAD").exists()
            self.still_open = (self.clone.work / ".sessions" / "walk-clash" / "session.json").is_file()
            self.worktree_kept = self.clash_worktree.is_dir() and self.clone.worktree_of("walk-clash") == self.clash_worktree
            self.on_board = self.chat.answer("ticket.close_choices", ticket="walk-clash")["choices"]
            self.chat.answer("ticket.close", ticket="walk-clash", leaving=["delete_branch"])

        with it("should refuse the close, saying the branch does not merge into main"):
            expect(self.error).to(contain("walk-clash does not merge into main"))

        with it("should leave no merge half done on main"):
            expect(self.merging).to(equal(False))

        with it("should keep the ticket's worktree"):
            expect(self.worktree_kept).to(be_true)

        with it("should keep the ticket among the open sessions"):
            expect(self.still_open).to(be_true)

        with it("should still offer to delete its worktree"):
            expect(self.on_board).to(contain("delete_worktree"))

    # (S) Person --> Close Active Session
    # Exploratory testing, gizmo-12: a close that chose only to delete the worktree committed and pushed its work.
    with context("that a ticket is closed with only its worktree deleted while that worktree holds work nobody committed"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk drop")
            self.chat.answer("ticket.activate", ticket="walk-drop")
            self.drop_worktree = self.clone.worktree_of("walk-drop")
            (self.drop_worktree / "README.md").write_text("# Work\nchanged, never committed\n", encoding="utf-8")
            (self.drop_worktree / "notes.txt").write_text("never added\n", encoding="utf-8")
            self.drop_choices = self.chat.answer("ticket.close_choices", ticket="walk-drop")
            self.drop_head = git(self.clone.work, "rev-parse", "walk-drop")
            self.dropped = self.chat.answer("ticket.close", ticket="walk-drop", leaving=["delete_worktree"])

        with it("should warn, before the close, that deleting the worktree without a commit loses that work"):
            expect(self.drop_choices["warning"]).to(contain("without a commit", "README.md", "notes.txt"))

        with it("should list the files that work is in among the closing choices"):
            expect(sorted(self.drop_choices["unsaved_work"])).to(contain("README.md", "notes.txt"))

        with it("should commit nothing on the ticket's branch"):
            expect(git(self.clone.work, "rev-parse", "walk-drop")).to(equal(self.drop_head))

        with it("should push nothing of the ticket's branch to origin"):
            expect(self.clone.origin_branches()).not_to(contain("walk-drop"))

        with it("should remove the worktree"):
            expect(self.drop_worktree.exists()).to(equal(False))

        with it("should name in its answer the files whose work went with the worktree"):
            expect(sorted(self.dropped["dropped_work"])).to(contain("README.md", "notes.txt"))

    # (S) Person --> Activate Ticket
    # Exploratory testing, gizmo-02: activating a closed ticket opened its worktree but left it in Complete, its folder
    # among the closed sessions, so a chat in that worktree got a session kept under _complete.
    with context("that a closed ticket is activated"):
        with before.all:
            self.chat.answer("ticket.activate", ticket="walk-drop")
            self.reopened_worktree = self.clone.worktree_of("walk-drop")
            self.reopened_in_worktree = self.reopened_worktree is not None and self.reopened_worktree.is_dir()
            self.reopened = next(ticket for column in self.chat.answer("board.show")["columns"] for key in ("in_progress", "done", "tickets") for ticket in column.get(key, []) if ticket["name"] == "walk-drop")
            self.reopened_session = SpecChat(self.server, self.reopened_worktree).answer("sessions.current")["name"]
            self.reopened_folder = (self.clone.work / ".sessions" / "walk-drop" / "session.json").is_file()
            self.left_closed = (self.clone.work / ".sessions" / "_complete" / "walk-drop").exists()
            self.chat.answer("ticket.close", ticket="walk-drop", leaving=["delete_branch"])

        with it("should open it in its own worktree"):
            expect(self.reopened_in_worktree).to(be_true)

        with it("should move its folder back among the open sessions"):
            expect((self.reopened_folder, self.left_closed)).to(equal((True, False)))

        with it("should put it back on a stage of the board"):
            expect(self.reopened["is_closed"]).to(equal(False))

        with it("should give a chat in its worktree its session"):
            expect(self.reopened_session).to(equal("walk-drop"))

    # (S) Person --> Activate Ticket
    with context("that a ticket is activated while a folder left on no branch is where its worktree goes"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk stuck")
            self.chat.answer("ticket.activate", ticket="walk-stuck")
            self.stuck = self.clone.worktree_of("walk-stuck")
            git(self.stuck, "checkout", "-q", "--detach")
            git(self.clone.work, "branch", "-q", "-D", "walk-stuck")
            _, self.error = self.chat.call("ticket.activate", ticket="walk-stuck")
            git(self.clone.work, "worktree", "remove", "--force", str(self.stuck))

        with it("should refuse to open it, naming the ticket"):
            expect(self.error).to(contain("walk-stuck cannot open in a worktree"))

        with it("should name the folder in the way"):
            expect(self.error).to(contain(self.stuck.name))

    # (S) Person --> Delete Ticket
    with context("that a ticket open in its own worktree, with work not saved, is deleted"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk gone")
            self.chat.answer("ticket.activate", ticket="walk-gone")
            self.gone = self.clone.worktree_of("walk-gone")
            (self.gone / "unsaved.txt").write_text("not committed\n", encoding="utf-8")
            self.chat.answer("ticket.delete", ticket="walk-gone")

        with it("should save that work on its branch on origin"):
            expect(self.clone.tracked("origin/walk-gone", "unsaved.txt")).to(equal(["unsaved.txt"]))

        with it("should remove its worktree"):
            expect((self.gone.exists(), self.clone.worktree_of("walk-gone"))).to(equal((False, None)))

        with it("should remove its session folder"):
            expect((self.clone.work / ".sessions" / "walk-gone").exists()).to(equal(False))

    # (S) Person --> Archive Ticket
    with context("that a ticket open in its own worktree, with work not saved, is archived"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk shelf")
            self.chat.answer("ticket.activate", ticket="walk-shelf")
            self.shelf = self.clone.worktree_of("walk-shelf")
            (self.shelf / "unsaved.txt").write_text("not committed\n", encoding="utf-8")
            self.chat.answer("ticket.archive", ticket="walk-shelf")

        with it("should save that work on its branch on origin"):
            expect(self.clone.tracked("origin/walk-shelf", "unsaved.txt")).to(equal(["unsaved.txt"]))

        with it("should remove its worktree"):
            expect((self.shelf.exists(), self.clone.worktree_of("walk-shelf"))).to(equal((False, None)))

        with it("should move its session folder among the archived sessions"):
            expect((self.clone.work / ".sessions" / "_archive" / "walk-shelf" / "session.json").is_file()).to(be_true)

    # Only Windows refuses to move or delete a folder a running program works in.
    if os.name == "nt":
        # (S) Person --> Delete Ticket
        with context("that a ticket whose session folder a running program holds open is deleted"):
            with before.all:
                self.chat.answer("ticket.create", title="Walk held")
                held = self.clone.work / ".sessions" / "walk-held"
                holder = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"], cwd=held)
                _, self.error = self.chat.call("ticket.delete", ticket="walk-held")
                self.kept = sorted(file.name for file in held.iterdir())
                self.on_board = "walk-held" in board_tickets(self.chat.answer("board.show"))
                holder.kill()
                holder.wait()

            with it("should refuse the delete, naming the folder that is held open"):
                expect(self.error).to(contain("walk-held", "close what holds it open"))

            with it("should keep the session's record and log"):
                expect(self.kept).to(contain("session.json", "session.log"))

            with it("should keep the ticket on the board"):
                expect(self.on_board).to(be_true)

    # (S) Person --> Switch Session
    with context("that a session is switched to and closed"):
        with before.all:
            self.chat.answer("sessions.switch", name="walk-side", create=True)
            self.opened = self.chat.answer("sessions.current")["name"]
            self.chat.answer("session.close", session=".sessions/walk-side/session.json")

        with it("should open that session"):
            expect(self.opened).to(equal("walk-side"))

        with it("should open main once it is closed"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("main"))

    with context("with two chats in the same clone"):
        with before.all:
            self.first = SpecChat(self.server, self.clone.work)
            self.second = SpecChat(self.server, self.clone.work)
            self.first.answer("sessions.switch", name="walk-first", create=True)

        with it("should keep the second chat's own open session"):
            expect(self.second.answer("sessions.current")["name"]).to(equal("main"))

        with it("should keep the first chat's session open"):
            expect(self.first.answer("sessions.current")["name"]).to(equal("walk-first"))

    # The desktop app starts a chat in a spare folder and moves it into the project later, in the same process.
    with context("with a chat that moved out of the spare folder it connected from"):
        with before.all:
            spare = self.clone.top / "spare"
            spare.mkdir()
            session_file = self.config / "sessions" / f"{MOVED_CHAT_PROCESS}.json"
            session_file.parent.mkdir(parents=True, exist_ok=True)
            session_file.write_text(json.dumps({"pid": int(MOVED_CHAT_PROCESS), "sessionId": str(uuid.uuid4()), "cwd": str(self.clone.work)}), encoding="utf-8")
            moved = SpecChat(self.server, spare, "unnamed", MOVED_CHAT_PROCESS)
            moved.answer("sessions.switch", name="walk-moved", create=True)
            (self.clone.work / "moved.txt").write_text("moved chat\n", encoding="utf-8")
            moved.answer("repo.push_commit", message="From a moved chat", untracked=True, sync_remote=False)
            self.spare = spare

        with it("should keep its session in the clone"):
            expect((self.clone.work / ".sessions" / "walk-moved").is_dir()).to(be_true)

        with it("should write nothing in the spare folder"):
            expect((self.spare / ".sessions").exists()).to(equal(False))

        with it("should commit its work in the clone"):
            expect(self.clone.subject()).to(equal("From a moved chat"))
