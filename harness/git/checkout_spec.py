"""A checkout is the folder git marks as one: which checkout holds a folder, whether it is the main clone or a linked
worktree, and where its facts are read from."""
import shutil
import tempfile
from pathlib import Path

from expects import be_a, equal, expect
from mamba import after, before, context, description, it

from harness.git.checkout import Checkout
from harness.git.git_facts import AskedOfGit, GitFolder, NoGitFacts


def _main_clone(top: Path) -> Path:
    """A main clone on main, its .git a folder holding a HEAD and one branch."""
    clone = top / "clone"
    (clone / ".git" / "refs" / "heads").mkdir(parents=True)
    (clone / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (clone / ".git" / "refs" / "heads" / "main").write_text("a" * 40 + "\n", encoding="utf-8")
    (clone / "src").mkdir()
    return clone


with description("a checkout") as self:
    with before.each:
        self.top = Path(tempfile.mkdtemp(prefix="cdd-checkout-")).resolve()

    with after.each:
        shutil.rmtree(self.top, ignore_errors=True)

    with context("that is a main clone"):
        with before.each:
            self.clone = _main_clone(self.top)

        with it("should be the checkout holding a folder inside it"):
            expect(Checkout.holding(self.clone / "src")).to(equal(Checkout(self.clone)))

        with it("should be the main clone and no linked worktree"):
            checkout = Checkout(self.clone)
            expect([checkout.is_main, checkout.is_linked_worktree]).to(equal([True, False]))

        with it("should name the branch its HEAD names"):
            expect(Checkout(self.clone).branch).to(equal("main"))

        with it("should read its facts from its files"):
            expect(Checkout(self.clone).facts).to(be_a(GitFolder))

        with it("should be its own main checkout"):
            expect(Checkout(self.clone).main_folder).to(equal(self.clone))

    with context("that is a linked worktree"):
        with before.each:
            self.clone = _main_clone(self.top)
            own = self.clone / ".git" / "worktrees" / "pets"
            own.mkdir(parents=True)
            (own / "HEAD").write_text("ref: refs/heads/pets\n", encoding="utf-8")
            (own / "commondir").write_text("../..\n", encoding="utf-8")
            self.linked = self.top / "pets"
            self.linked.mkdir()
            (self.linked / ".git").write_text(f"gitdir: {own}\n", encoding="utf-8")

        with it("should be a linked worktree and not the main clone"):
            checkout = Checkout(self.linked)
            expect([checkout.is_main, checkout.is_linked_worktree]).to(equal([False, True]))

        with it("should name its own branch"):
            expect(Checkout(self.linked).branch).to(equal("pets"))

        with it("should lead back to the main clone"):
            expect(Checkout(self.linked).main_folder).to(equal(self.clone))

        with it("should see no merge going on"):
            expect(Checkout(self.linked).facts.is_merging()).to(equal(False))

        with context("with a merge going on in it"):
            with before.each:
                (self.clone / ".git" / "worktrees" / "pets" / "MERGE_HEAD").write_text("b" * 40 + "\n", encoding="utf-8")

            with it("should see the merge, kept in its own git folder"):
                expect(Checkout(self.linked).facts.is_merging()).to(equal(True))

            with it("should leave the main clone with no merge going on"):
                expect(Checkout(self.clone).facts.is_merging()).to(equal(False))

    with context("that is a folder in no repository"):
        with it("should be the folder itself"):
            expect(Checkout.holding(self.top).folder).to(equal(self.top))

        with it("should be no clone and name no branch"):
            checkout = Checkout(self.top)
            expect([checkout.is_clone, checkout.branch]).to(equal([False, ""]))

        with it("should have no facts to read"):
            expect(Checkout(self.top).facts).to(be_a(NoGitFacts))

        with it("should read its files once git has made it a repository"):
            checkout = Checkout(self.top)
            checkout.facts
            (self.top / ".git" / "refs" / "heads").mkdir(parents=True)
            (self.top / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            expect(checkout.facts).to(be_a(GitFolder))

    with context("whose refs git keeps in a reftable"):
        with before.each:
            self.clone = _main_clone(self.top)
            (self.clone / ".git" / "config").write_text("[extensions]\n\trefstorage = reftable\n", encoding="utf-8")

        with it("should ask git for its facts"):
            expect(Checkout(self.clone).facts).to(be_a(AskedOfGit))
