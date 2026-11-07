"""The session a tool call opens, which one cdd server keeps for every project its chats work on."""

import shutil
import sys
import tempfile
import threading
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.agent_tools.tool_call import ToolCall
from space.session import Sessions


def _project() -> Path:
    root = Path(tempfile.mkdtemp(prefix="cdd-current-session-"))
    (root / ".git").mkdir()
    return root.resolve()


with description("the session a tool call opens"):
    with before.each:
        self.first = _project()
        self.second = _project()
        Sessions(self.first).switch("alpha")
        Sessions(self.second).switch("beta")

    with after.each:
        shutil.rmtree(self.first, ignore_errors=True)
        shutil.rmtree(self.second, ignore_errors=True)

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

    with context("that a call names a folder inside a project"):
        with before.each:
            (self.first / "docs").mkdir()

        with it("should be the session of the checkout holding that folder"):
            expect(ToolCall({}, self.first / "docs").session.repo_path).to(equal(self.first))

    with context("that a call names a folder in a linked worktree of a project"):
        with before.each:
            self.worktree = Path(tempfile.mkdtemp()).resolve()
            worktree_git = self.first / ".git" / "worktrees" / "pet-visits"
            worktree_git.mkdir(parents=True)
            (worktree_git / "commondir").write_text("../..\n", encoding="utf-8")
            (self.worktree / ".git").write_text(f"gitdir: {worktree_git}\n", encoding="utf-8")
            (self.worktree / "docs").mkdir()

        with after.each:
            shutil.rmtree(self.worktree, ignore_errors=True)

        with it("should be the session of the worktree holding that folder"):
            expect(ToolCall({}, self.worktree / "docs").session.repo_path).to(equal(self.worktree))
