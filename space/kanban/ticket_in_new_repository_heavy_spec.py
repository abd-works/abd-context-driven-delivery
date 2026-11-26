"""Heavy spec: a ticket opened through a real cdd server in a folder that was made a git repository with ``git init``
and has no commit yet, as a person makes one from a plain folder before its first ticket.

Git names the new branch after ``init.defaultBranch`` (master here, as many people have it set), the branch has no
commit, and the repository has no origin. The examples run in order: each context acts once, then its examples look at
the result."""
import os
import shutil
import subprocess
import sys
import tempfile
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
    "space.session.session:Session",
    "space.session.sessions:Sessions",
    "space.repo.repo:Repo",
    # The board lists every practice's fidelities; importing one practice registers them all.
    "cdd_guidance.practices.stories.stories:Stories",
    # A stage's steps are the actions registered for it; importing one action registers them all.
    "cdd_guidance.actions.generate.generate:Generate",
)
# The branch git init makes when the person's git names no other: not main, so nothing may assume main.
INIT_BRANCH = "master"


def git(folder: Path, *arguments: str) -> str:
    return subprocess.run(["git", *arguments], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()


def worktree_of(folder: Path, branch: str) -> Path | None:
    for block in git(folder, "worktree", "list", "--porcelain").split("\n\n"):
        lines = block.splitlines()
        if f"branch refs/heads/{branch}" in lines:
            return Path(lines[0].removeprefix("worktree "))
    return None


# (E) Open Work Session
# (S) Person --> Activate Ticket
with description("a ticket in a folder just made a git repository") as self:
    with before.all:
        self.config = Path(tempfile.mkdtemp(prefix="cdd-claude-config-"))
        self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
        self.server = SpecServer(TOOLSETS)
        self.server.start()
        self.top = Path(tempfile.mkdtemp(prefix="cdd-new-repository-"))
        self.folder = self.top / "demo"
        self.folder.mkdir()
        self.chat = SpecChat(self.server, self.folder)

    with after.all:
        self.server.stop()
        shutil.rmtree(self.top, ignore_errors=True)
        shutil.rmtree(self.config, ignore_errors=True)
        if self.prior_config is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

    with context("while the folder is a plain folder"):
        with it("should read as no git repository"):
            expect(self.chat.answer("board.overview")["is_clone"]).to(equal(False))

    with context("that git init made it a repository with no commit"):
        with before.all:
            git(self.folder, "init", "-q", "-b", INIT_BRANCH)
            git(self.folder, "config", "user.name", "person")
            git(self.folder, "config", "user.email", "person@example.test")
            self.created = self.chat.answer("ticket.create", title="Feature X")

        with it("should read as a git repository"):
            expect(self.chat.answer("board.overview")["is_clone"]).to(equal(True))

        with it("should make the ticket's session folder"):
            expect((self.folder / ".sessions" / "feature-x" / "session.json").is_file()).to(be_true)

    with context("that the ticket is opened in its own worktree"):
        with before.all:
            self.opened, self.error = self.chat.call("ticket.activate", ticket="feature-x")
            self.worktree = worktree_of(self.folder, "feature-x")

        with it("should open without an error"):
            expect(self.error).to(equal(""))

        with it("should make a worktree on its branch"):
            expect(self.worktree is not None and self.worktree.is_dir()).to(be_true)

        with it("should give the branch git init made its first commit, holding the session folders"):
            expect(git(self.folder, "ls-tree", "-r", "--name-only", INIT_BRANCH, ".sessions").splitlines()).to(contain(".sessions/feature-x/session.json"))

        # The record of the branch and worktree found is committed on that branch after the worktree is made.
        with it("should start the ticket's branch from that first commit"):
            expect(git(self.folder, "merge-base", INIT_BRANCH, "feature-x")).to(equal(git(self.folder, "rev-list", "--max-parents=0", INIT_BRANCH)))

        with it("should leave the folder itself on the branch git init made"):
            expect(git(self.folder, "branch", "--show-current")).to(equal(INIT_BRANCH))
