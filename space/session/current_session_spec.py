"""The session a tool call opens, which one cdd server keeps for every project its chats work on."""

import shutil
import sys
import tempfile
import threading
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.agent_tools.tool_call import ToolCall
from space.repo.mock_repo import MockGit
from space.session import Sessions
from space.session.open_sessions import UnknownSessionError
from space.session.spec_support.throwaway_project import ExampleHome


def _project() -> Path:
    root = Path(tempfile.mkdtemp(prefix="cdd-current-session-"))
    (root / ".git").mkdir()
    return root.resolve()


with description("the session a tool call opens"):
    with before.each:
        self.home = ExampleHome()
        self.first = _project()
        self.second = _project()
        Sessions(self.first).switch("alpha", create=True)
        Sessions(self.second).switch("beta", create=True)

    with after.each:
        shutil.rmtree(self.first, ignore_errors=True)
        shutil.rmtree(self.second, ignore_errors=True)
        self.home.close()

    with context("that two projects each have a session switched on"):
        with it("should be each project's own session for a call on that project"):
            expect((ToolCall({}, self.first).session.name, ToolCall({}, self.second).session.name)).to(equal(("alpha", "beta")))

        with context("with calls on both projects running at the same time"):
            with it("should give each call its own project's session"):
                seen: dict[str, str] = {}
                both_inside = threading.Barrier(2)

                def look(project: Path) -> None:
                    call = ToolCall({}, project)
                    both_inside.wait(timeout=5)
                    seen[project.name] = call.session.name

                calls = [threading.Thread(target=look, args=(project,)) for project in (self.first, self.second)]
                for call in calls:
                    call.start()
                for call in calls:
                    call.join()
                expect(seen).to(equal({self.first.name: "alpha", self.second.name: "beta"}))

    # (S) Person --> Switch Session
    # Exploratory testing, gizmo-10: a misspelt name made a session folder and a card on the board nobody asked for.
    with context("that a chat switches to a name no session has"):
        with it("should refuse the switch, naming the sessions there are"):
            expect(lambda: Sessions(self.first).switch("alpah")).to(raise_error(UnknownSessionError, contain("alpah", "main, alpha")))

        with it("should make no session folder for it"):
            try:
                Sessions(self.first).switch("alpah")
            except UnknownSessionError:
                pass
            expect((self.first / ".sessions" / "alpah").exists()).to(equal(False))

        with it("should keep the chat's open session"):
            try:
                Sessions(self.first).switch("alpah")
            except UnknownSessionError:
                pass
            expect(ToolCall({}, self.first).session.name).to(equal("alpha"))

        with context("that asks for it to be made"):
            with before.each:
                Sessions(self.first).switch("gamma", create=True)

            with it("should make the session and open it"):
                expect(ToolCall({}, self.first).session.name).to(equal("gamma"))

    with context("that the session a chat has open was closed since"):
        with before.each:
            # A close made from another chat moves the folder among the closed sessions and leaves this chat's choice.
            Sessions(self.first).named("alpha").folder.move_to_closed()

        with it("should be the main session"):
            expect(ToolCall({}, self.first).session.name).to(equal("main"))

        with it("should leave no folder for it among the open sessions once a call logs a failure"):
            ToolCall({}, self.first).session.log.by(None).failure(RuntimeError("the call failed"), tool="ticket.activate")
            expect((self.first / ".sessions" / "alpha").exists()).to(equal(False))

    with context("that a call names a folder inside a project"):
        with before.each:
            (self.first / "docs").mkdir()

        with it("should be the session of the checkout holding that folder"):
            expect(ToolCall({}, self.first / "docs").session.checkout.root).to(equal(self.first))

    with context("that a call names a folder in a linked worktree of a project"):
        with before.each:
            # The project and its worktree held in memory: which branch each checkout has out is all this asks git.
            held = MockGit(self.first)
            held.make_clone()
            self.worktree = Path(tempfile.mkdtemp()).resolve() / "pet-visits"
            held.add_worktree("pet-visits", self.worktree)
            (self.worktree / "docs").mkdir()

        with after.each:
            shutil.rmtree(self.worktree.parent, ignore_errors=True)

        with it("should be the session of the worktree holding that folder"):
            expect(ToolCall({}, self.worktree / "docs").session.checkout.root).to(equal(self.worktree))
