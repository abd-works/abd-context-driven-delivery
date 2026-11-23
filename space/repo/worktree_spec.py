"""BDD spec: the folder a branch's worktree gets beside the main clone. Git is the in-memory *MockGit*, so no example
starts git; worktree_heavy_spec.py proves the same rule against real git."""
import shutil
import tempfile
from pathlib import Path

from expects import be_none, equal, expect
from mamba import after, before, context, description, it

from space.repo.mock_repo import MockGit

MONTHLY = "customer-order-history-export-monthly"
WEEKLY = "customer-order-history-export-weekly"


with description("the folder a branch's worktree gets") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="worktree-folder-"))
        self.clone = self.tmp / "clone"
        self.clone.mkdir()
        self.held = MockGit(self.clone)
        self.held.make_clone()
        self.repo = self.held.serve(self.clone)
        self.worktrees = self.repo.worktrees

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with it("should be named for the clone and the branch's first 24 characters"):
        expect(self.worktrees.sibling_folder(self.repo.branch_named(MONTHLY)).name).to(equal("clone-customer-order-history-e"))

    with context("with another branch whose name starts with the same 24 characters open in its worktree"):
        with before.each:
            self.monthly = self.repo.branch_named(MONTHLY).open_in_worktree()

        with it("should be a folder of its own, numbered"):
            expect(self.worktrees.sibling_folder(self.repo.branch_named(WEEKLY)).name).to(equal("clone-customer-order-history-e-2"))

        with it("should stay the same folder for the branch that has it"):
            expect(self.worktrees.sibling_folder(self.repo.branch_named(MONTHLY))).to(equal(self.monthly.path))

        with context("and a third such branch open in the numbered folder"):
            with before.each:
                self.repo.branch_named(WEEKLY).open_in_worktree()

            with it("should be the next numbered folder"):
                expect(self.worktrees.sibling_folder(self.repo.branch_named("customer-order-history-export-daily")).name).to(equal("clone-customer-order-history-e-3"))

    with context("with a worktree whose folder was deleted outside CDD"):
        with before.each:
            self.opened = self.repo.branch_named(MONTHLY).open_in_worktree()
            shutil.rmtree(self.opened.path)

        with it("should no longer be the branch's worktree"):
            expect(self.repo.branch_named(MONTHLY).worktree).to(be_none)
