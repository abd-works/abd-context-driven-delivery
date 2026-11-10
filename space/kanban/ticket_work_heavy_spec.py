"""Heavy spec: a ticket's work through a real cdd server, on a clone with its own origin, as chats meet it.

Opening, pushing, pulling, switching, and closing tickets on branches and in worktrees, each checked against git. The
examples run in order, as one person's day of work: each context acts once, then its examples look at the result."""
import asyncio
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

from harness.mcp.mcp_daemon import CHAT_HEADER, CHAT_PROCESS_HEADER, PROJECT_HEADER
from harness.mcp.spec_support import SpecServer

TOOLSETS = (
    "space.kanban.board:Board",
    "space.kanban.board:Stage",
    "space.kanban.ticket:Ticket",
    "space.kanban.ticket:FidelityProgress",
    "space.session.session:Session",
    "space.session.sessions:Sessions",
    "space.session.practice_session_output:PracticeSessionOutput",
    "space.repo.repo:Repo",
    # The board lists every practice's fidelities; importing one practice registers them all.
    "cdd_guidance.practices.stories.stories:Stories",
)
CALL_SECONDS = 180
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


class Chat:
    """A chat as the cdd server meets it: the folder it connected from, its id, and optionally its Claude Code process."""

    def __init__(self, server: SpecServer, project: Path, chat_id: str = "", process: str = "") -> None:
        self._server = server
        self._headers = {PROJECT_HEADER: str(project), CHAT_HEADER: chat_id or str(uuid.uuid4())}
        if process:
            self._headers[CHAT_PROCESS_HEADER] = process

    def call(self, tool: str, **arguments) -> tuple[object, str]:
        """The tool's answer and an empty error, or no answer and the error the server gave."""
        return asyncio.run(self._call(tool, arguments))

    def answer(self, tool: str, **arguments) -> object:
        value, error = self.call(tool, **arguments)
        if error:
            raise AssertionError(f"{tool} failed: {error}")
        return value

    async def _call(self, tool: str, arguments: dict) -> tuple[object, str]:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        async with streamablehttp_client(self._server.url, headers=self._headers, timeout=CALL_SECONDS, sse_read_timeout=CALL_SECONDS) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments)
        text = result.content[0].text if result.content else ""
        if result.isError:
            return None, text
        try:
            return json.loads(text), ""
        except ValueError:
            return text, ""


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
        self.chat = Chat(self.server, self.clone.work)

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
            self.created = self.chat.answer("ticket.create", title="Walk branch")

        with it("should name the ticket after its title"):
            expect(self.created["name"]).to(equal("walk-branch"))

        with it("should make its session folder"):
            expect((self.clone.work / ".sessions" / "walk-branch" / "session.json").is_file()).to(be_true)

    # (S) Person --> Activate Ticket
    with context("that the ticket is opened on its branch"):
        with before.all:
            self.chat.answer("ticket.activate", ticket="walk-branch", opening=["branch"])

        with it("should check its branch out"):
            expect(self.clone.branch).to(equal("walk-branch"))

        with it("should open its session"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("walk-branch"))

        with it("should have pushed its session folder to main first"):
            expect(self.clone.tracked("origin/main", ".sessions/walk-branch")).to(contain(".sessions/walk-branch/session.json"))

    # (S) Repo --> Push Branch
    with context("that work is pushed from its branch"):
        with before.all:
            (self.clone.work / "feature.txt").write_text("first\n", encoding="utf-8")
            self.chat.answer("repo.push_commit", message="Add feature", untracked=True, sync_remote=True)

        with it("should commit the work on its branch"):
            expect(self.clone.subject()).to(equal("Add feature"))

        with it("should push the branch to origin"):
            expect(self.clone.subject("origin/walk-branch")).to(equal("Add feature"))

    with context("that work was pushed to its branch from elsewhere"):
        with before.all:
            self.clone.push_from_elsewhere("walk-branch", "elsewhere.txt", "from elsewhere\n", "Change from elsewhere")
            (self.clone.work / "feature.txt").write_text("second\n", encoding="utf-8")
            self.chat.answer("repo.push_commit", message="Change feature", untracked=True, sync_remote=True)

        with it("should bring that work in"):
            expect((self.clone.work / "elsewhere.txt").is_file()).to(be_true)

        with it("should push its own commit after it"):
            expect(self.clone.subjects("origin/walk-branch")).to(contain("Change feature", "Change from elsewhere"))

    # (S) Person --> Open Main
    with context("that main is opened again, merging the ticket's work"):
        with before.all:
            self.chat.answer("board.open_main", leaving=["handoff", "commit", "push", "merge"])

        with it("should check main out"):
            expect(self.clone.branch).to(equal("main"))

        with it("should merge the ticket's work into main"):
            expect((self.clone.work / "feature.txt").is_file()).to(be_true)

        with it("should open main"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("main"))

    with context("that a ticket is opened in its own worktree"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk worktree")
            self.chat.answer("ticket.activate", ticket="walk-worktree", opening=["worktree"])
            self.worktree = self.clone.worktree_of("walk-worktree")

        with it("should make a worktree on its branch"):
            expect(self.worktree is not None and self.worktree.is_dir()).to(be_true)

        with it("should leave the main clone on main"):
            expect(self.clone.branch).to(equal("main"))

        with it("should give the worktree its session folder"):
            expect((self.worktree / ".sessions" / "walk-worktree" / "session.json").is_file()).to(be_true)

        with it("should keep its session folder committed on main"):
            expect(self.clone.tracked("main", ".sessions/walk-worktree")).to(contain(".sessions/walk-worktree/session.json"))

        with it("should open its session"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("walk-worktree"))

    with context("that work is pushed from the worktree"):
        with before.all:
            worktree = self.clone.worktree_of("walk-worktree")
            (worktree / "in-worktree.txt").write_text("worktree work\n", encoding="utf-8")
            self.chat.answer("repo.push_commit", message="Work in worktree", untracked=True, sync_remote=True)
            self.worktree = worktree

        with it("should commit the work on the worktree's branch"):
            expect(self.clone.subject(folder=self.worktree)).to(equal("Work in worktree"))

        with it("should leave main without that commit"):
            expect(self.clone.subjects("main")).not_to(contain("Work in worktree"))

        with it("should push the worktree's branch to origin"):
            expect(self.clone.origin_branches()).to(contain("walk-worktree"))

    # (S) Person --> Close Ticket
    with context("that the worktree's ticket is closed, its branch merged and deleted"):
        with before.all:
            self.worktree = self.clone.worktree_of("walk-worktree")
            leaving = ["handoff", "commit", "push", "merge", "delete_branch", "delete_worktree"]
            self.chat.answer("ticket.close", ticket="walk-worktree", leaving=leaving)

        with it("should remove the worktree"):
            expect(self.worktree.exists()).to(equal(False))

        with it("should merge its work into main"):
            expect((self.clone.work / "in-worktree.txt").is_file()).to(be_true)

        with it("should delete its branch here"):
            expect(self.clone.branches()).not_to(contain("walk-worktree"))

        with it("should delete its branch on origin"):
            expect(self.clone.origin_branches()).not_to(contain("walk-worktree"))

        with it("should move its session among the closed sessions"):
            expect((self.clone.work / ".sessions" / "_complete" / "walk-worktree").is_dir()).to(be_true)

        with it("should open main"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("main"))

    # (S) Repo --> Switch Worktree
    with context("that the repo tools push a branch, move it to a worktree, and close both"):
        with before.all:
            self.chat.answer("repo.switch_branch", name="walk-repo")
            (self.clone.work / "repo.txt").write_text("repo work\n", encoding="utf-8")
            self.chat.answer("repo.push_commit", message="Repo work", untracked=True, sync_remote=True)
            self.chat.answer("repo.switch_worktree", name="walk-repo")
            self.worktree = self.clone.worktree_of("walk-repo")
            (self.worktree / "repo-worktree.txt").write_text("more\n", encoding="utf-8")
            self.chat.answer("repo.close_worktree", commit_message="Close worktree")
            self.after_worktree = self.clone.subject("origin/walk-repo")
            self.chat.answer("repo.close_branch", name="walk-repo", commit_message="Close branch")

        with it("should push the worktree's last work before removing it"):
            expect(self.after_worktree).to(equal("Close worktree"))

        with it("should remove the worktree"):
            expect(self.worktree.exists()).to(equal(False))

        with it("should merge the branch into main"):
            expect((self.clone.work / "repo-worktree.txt").is_file()).to(be_true)

        with it("should delete the branch here"):
            expect(self.clone.branches()).not_to(contain("walk-repo"))

        with it("should delete the branch on origin"):
            expect(self.clone.origin_branches()).not_to(contain("walk-repo"))

        with it("should push main with the merge"):
            expect(self.clone.subject("origin/main")).to(equal(self.clone.subject("main")))

    with context("that a person switches between two tickets on their branches"):
        with before.all:
            for title in ("Walk one", "Walk two"):
                self.chat.answer("ticket.create", title=title)
            self.chat.answer("ticket.activate", ticket="walk-one", opening=["branch"])
            (self.clone.work / "one.txt").write_text("one\n", encoding="utf-8")
            self.chat.answer("ticket.activate", ticket="walk-two", leaving=["handoff", "commit", "push"], opening=["branch"])
            self.on_two = (self.clone.branch, self.chat.answer("sessions.current")["name"])
            self.board_on_two = board_tickets(self.chat.answer("board.show"))
            self.chat.answer("ticket.activate", ticket="walk-one", leaving=["commit", "push"], opening=["branch"])
            self.on_one = self.clone.branch
            for ticket in ("walk-one", "walk-two"):
                self.chat.answer("ticket.close", ticket=ticket, leaving=["commit", "push", "merge", "delete_branch"])

        with it("should bring the work of the ticket it left to main once that ticket closes"):
            expect(self.clone.tracked("origin/main", "one.txt")).to(contain("one.txt"))

        with it("should open the ticket switched to"):
            expect(self.on_two).to(equal(("walk-two", "walk-two")))

        with it("should keep both tickets on the board on either branch"):
            expect(self.board_on_two).to(contain("walk-one", "walk-two"))

        with it("should switch back to the first ticket's branch"):
            expect(self.on_one).to(equal("walk-one"))

        with it("should delete both branches once closed"):
            expect(self.clone.branches()).not_to(contain("walk-one", "walk-two"))

        with it("should end on main"):
            expect(self.clone.branch).to(equal("main"))

    with context("that a ticket is created while the clone is on another ticket's branch"):
        with before.all:
            self.chat.answer("ticket.create", title="Walk a")
            self.chat.answer("ticket.activate", ticket="walk-a", opening=["branch"])
            self.chat.answer("ticket.create", title="Walk b")
            self.chat.answer("ticket.activate", ticket="walk-b", leaving=["commit", "push"], opening=["branch"])
            self.board = board_tickets(self.chat.answer("board.show"))
            self.on = self.clone.branch
            for ticket in ("walk-b", "walk-a"):
                self.chat.answer("ticket.close", ticket=ticket, leaving=["commit", "push", "merge", "delete_branch"])

        with it("should open the new ticket on its branch"):
            expect(self.on).to(equal("walk-b"))

        with it("should push the new ticket's session folder to main"):
            expect(self.clone.tracked("origin/main", ".sessions/_complete/walk-b")).to(contain(".sessions/_complete/walk-b/session.json"))

        with it("should keep both tickets on the board"):
            expect(self.board).to(contain("walk-a", "walk-b"))

    # (S) Repo --> Close Branch
    with context("that origin's main moved on before a branch is closed"):
        with before.all:
            self.clone.push_from_elsewhere("main", "on-main.txt", "pushed to main elsewhere\n", "Main from elsewhere")
            self.chat.answer("repo.switch_branch", name="walk-land")
            (self.clone.work / "land.txt").write_text("land\n", encoding="utf-8")
            self.chat.answer("repo.close_branch", name="walk-land", commit_message="Land it")

        with it("should bring origin's change into main"):
            expect((self.clone.work / "on-main.txt").is_file()).to(be_true)

        with it("should merge the branch into main"):
            expect((self.clone.work / "land.txt").is_file()).to(be_true)

        with it("should push main with both"):
            expect(self.clone.subjects("origin/main")).to(contain("Main from elsewhere"))

    with context("that a push meets a real conflict"):
        with before.all:
            self.chat.answer("repo.switch_branch", name="walk-conflict")
            (self.clone.work / "shared.txt").write_text("mine\n", encoding="utf-8")
            self.chat.answer("repo.push_commit", message="Mine", untracked=True, sync_remote=True)
            self.clone.push_from_elsewhere("walk-conflict", "shared.txt", "theirs\n", "Theirs")
            (self.clone.work / "shared.txt").write_text("mine again\n", encoding="utf-8")
            _, self.error = self.chat.call("repo.push_commit", message="Mine again", untracked=True, sync_remote=True)
            self.merge_head = (self.clone.work / ".git" / "MERGE_HEAD").exists()
            self.kept = self.clone.subject()
            git(self.clone.work, "reset", "-q", "--hard", "origin/walk-conflict")
            self.chat.answer("repo.switch_branch", name="main")

        with it("should refuse the push, naming the conflict"):
            expect(self.error.lower()).to(contain("conflict"))

        with it("should leave no merge half done"):
            expect(self.merge_head).to(equal(False))

        with it("should keep the commit made here"):
            expect(self.kept).to(equal("Mine again"))

        with it("should switch back to main afterwards"):
            expect(self.clone.branch).to(equal("main"))

    # (S) Person --> Switch Session
    with context("that a session is switched to and closed"):
        with before.all:
            self.chat.answer("sessions.switch", name="walk-side")
            self.opened = self.chat.answer("sessions.current")["name"]
            self.chat.answer("session.close", session=".sessions/walk-side/session.json")

        with it("should open that session"):
            expect(self.opened).to(equal("walk-side"))

        with it("should open main once it is closed"):
            expect(self.chat.answer("sessions.current")["name"]).to(equal("main"))

    with context("with two chats in the same clone"):
        with before.all:
            self.first = Chat(self.server, self.clone.work)
            self.second = Chat(self.server, self.clone.work)
            self.first.answer("sessions.switch", name="walk-first")

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
            moved = Chat(self.server, spare, "unnamed", MOVED_CHAT_PROCESS)
            moved.answer("sessions.switch", name="walk-moved")
            (self.clone.work / "moved.txt").write_text("moved chat\n", encoding="utf-8")
            moved.answer("repo.push_commit", message="From a moved chat", untracked=True, sync_remote=False)
            self.spare = spare

        with it("should keep its session in the clone"):
            expect((self.clone.work / ".sessions" / "walk-moved").is_dir()).to(be_true)

        with it("should write nothing in the spare folder"):
            expect((self.spare / ".sessions").exists()).to(equal(False))

        with it("should commit its work in the clone"):
            expect(self.clone.subject()).to(equal("From a moved chat"))
