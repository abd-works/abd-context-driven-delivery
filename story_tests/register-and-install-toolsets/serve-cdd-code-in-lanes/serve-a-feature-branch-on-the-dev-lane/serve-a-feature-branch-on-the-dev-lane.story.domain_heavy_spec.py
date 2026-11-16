"""Serve CDD Code In Lanes with real git: a ticket's worktree pinned or served from disk on the dev lane, naming its
branch, while the stable lane keeps serving main. No server is started; the lanes' homes are throwaway folders."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.examples import server_lanes_examples as examples
from harness.mcp.cdd_home import SERVER_MODULE, CddHome


def _git(folder: Path, *arguments: str) -> str:
    return subprocess.run(["git", "-C", str(folder), *arguments], check=True, capture_output=True, text=True).stdout.strip()


def _commit(checkout: Path, file: str, text: str) -> str:
    path = checkout / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git(checkout, "add", "-A")
    _git(checkout, "-c", "user.name=spec", "-c", "user.email=spec@example.invalid", "commit", "--quiet", "-m", f"change {file}")
    return _git(checkout, "rev-parse", "HEAD")


def _seed_main_with_ticket_worktree(root: Path) -> tuple[Path, Path]:
    """A main checkout on main that holds the server module, and checkout-flow's worktree with a commit main does not."""
    main = root / "abd-context-driven-delivery"
    main.mkdir()
    _git(main, "init", "--quiet", "--initial-branch", examples.MAIN_BRANCH)
    _commit(main, SERVER_MODULE, "# the server\n")
    worktree = root / "worktrees" / examples.CHECKOUT_FLOW
    _git(main, "worktree", "add", "--quiet", "-b", examples.CHECKOUT_FLOW, str(worktree))
    return main, worktree


with description("Serve A Feature Branch On The Dev Lane") as self:
    with before.all:
        self.root = Path(tempfile.mkdtemp())
        self.main, self.worktree = _seed_main_with_ticket_worktree(self.root)
        self.feature_commit = _commit(self.worktree, "harness/feature.py", "# checkout-flow's change\n")
        self.lanes = examples.seed_lanes(self.root)
        self.main_commit = self.lanes.stable.home.pin(self.main)

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("Pin the feature's branch straight from its worktree"):
        with before.all:
            self.dev_home = self.lanes.for_project(self.worktree).home
            self.dev_home.pin(self.worktree)

        with it("should serve the feature's commit on the dev lane"):
            expect(self.dev_home.is_pinned_to(self.worktree)).to(equal(True))

        with it("should name the branch checkout-flow"):
            expect(self.dev_home.served_branch).to(equal(examples.CHECKOUT_FLOW))

        with it("should name the worktree it was pinned from"):
            expect(self.dev_home.served_worktree).to(equal(self.worktree.resolve()))

        with it("should leave the stable lane serving main"):
            expect(self.lanes.stable.home.served_branch).to(equal(examples.MAIN_BRANCH))

    with context("Serve the feature's worktree as it is on disk"):
        with before.all:
            self.disk_home = CddHome(self.root / ".cdd-disk")
            self.disk_home.serve_from(self.worktree)

        with it("should serve the worktree on disk and name the branch checkout-flow"):
            expect((self.disk_home.source, self.disk_home.served_branch)).to(equal((self.worktree.resolve(), examples.CHECKOUT_FLOW)))
