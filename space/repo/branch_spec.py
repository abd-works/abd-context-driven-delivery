"""A branch answers where it is checked out, and saves the work of the checkout that has it."""
import shutil
import tempfile
from pathlib import Path

from expects import be, be_false, be_none, be_true, equal, expect
from mamba import after, before, context, description, it

from space.repo.mock_repo import MockGit


with description("a branch of a repository") as self:
    with before.each:
        self.top = Path(tempfile.mkdtemp(prefix="cdd-branch-")).resolve()
        self.clone = self.top / "clone"
        self.clone.mkdir()
        self.held = MockGit(self.clone)
        self.held.make_clone()
        self.repo = self.held.serve(self.clone)

    with after.each:
        shutil.rmtree(self.top, ignore_errors=True)

    with it("should be the default branch the repository names"):
        expect(self.repo.default_branch.is_default).to(be_true)

    with context("opened in a linked worktree beside the main clone"):
        with before.each:
            self.worktree = self.top / "clone-pets"
            self.held.add_worktree("pets", self.worktree)
            self.branch = self.repo.branch_named("pets")

        with it("should be checked out, though not in the main clone"):
            expect((self.branch.is_checked_out, self.branch.is_checked_out_here)).to(equal((True, False)))

        with it("should answer that worktree as its linked worktree"):
            expect(self.branch.linked_worktree.root).to(equal(self.worktree))

        with it("should answer that worktree as its checkout"):
            expect(self.branch.checkout).to(be(self.branch.linked_worktree))

        with context("whose work is changed and saved"):
            with before.each:
                self.held.origin.add()
                (self.worktree / "visits.md").write_text("visits\n", encoding="utf-8")
                self.branch.save("pets: visits")

            with it("should commit the work in that worktree, on its branch"):
                expect(self.held.branches.logs["pets"][-1]).to(equal("pets: visits"))

            with it("should push the branch"):
                expect(self.held.calls[-1]).to(equal(("push", "pets")))

        with context("whose work is saved without a push"):
            with before.each:
                self.held.origin.add()
                (self.worktree / "visits.md").write_text("visits\n", encoding="utf-8")
                self.branch.save("pets: visits", push=False)

            with it("should leave origin without the branch"):
                expect(self.held.origin.has("pets")).to(be_false)

        with context("whose worktree is closed"):
            with before.each:
                self.closed = self.branch.linked_worktree.close("pets: close")

            with it("should answer the branch it had out"):
                expect(self.closed).to(equal(self.branch))

            with it("should no longer be checked out anywhere"):
                expect(self.branch.checkout).to(be_none)

    with context("checked out in the main clone"):
        with before.each:
            self.branch = self.repo.default_branch

        with it("should be checked out here"):
            expect(self.branch.is_checked_out_here).to(be_true)

        with it("should have no linked worktree"):
            expect(self.branch.linked_worktree).to(be_none)
