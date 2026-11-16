"""BDD spec: a session's work taken to main, merged in the clone or pushed to origin, as the chat bar's Merge to main
and Push to main do. Git is the in-memory *MockGit*, so no example starts git; session_to_main_heavy_spec.py proves
the same examples against real git."""
import shutil
import tempfile
from pathlib import Path

from expects import equal, expect, have_key
from mamba import after, before, context, description, it

from space.repo.mock_repo import MockGit

SESSION_BRANCH = "session/demo"


# (E) Steer Sessions
# (S) Person --> Push Session To Main From Chat Bar
with description("a session's work taken to main") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="session-to-main-"))
        self.clone = self.tmp / "clone"
        self.clone.mkdir()
        (self.clone / "seed.txt").write_text("seed\n", encoding="utf-8")
        self.held = MockGit(self.clone)
        self.held.make_clone()
        self.held.origin.add()

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("from the session's own worktree, with work not committed"):
        with before.each:
            self.tree = self.tmp / "clone-demo"
            self.held.add_worktree(SESSION_BRANCH, self.tree)
            (self.tree / "work.txt").write_text("work\n", encoding="utf-8")

        with context("that is merged to main"):
            with before.each:
                self.landed = self.held.serve(self.tree).merge_to_main()

            with it("should commit the work on the session's branch"):
                expect(self.held.branches.trees[SESSION_BRANCH]).to(have_key("work.txt"))

            with it("should hold the work on main in the clone"):
                expect(self.held.branches.trees["main"]).to(have_key("work.txt"))

            with it("should leave main on origin without the work"):
                expect(self.held.origin.trees["main"]).not_to(have_key("work.txt"))

            with it("should leave the worktree on the session's branch"):
                expect(self.held.branch_of(self.tree.resolve())).to(equal(SESSION_BRANCH))

            with it("should answer the commit main is on"):
                expect(self.landed.subject).to(equal(f"merge {SESSION_BRANCH} into main"))

        with context("and the clone's own changes not committed, such as the session's log written in main"):
            with before.each:
                (self.clone / "session.log").write_text("tool repo.merge_to_main", encoding="utf-8")
                self.held.serve(self.tree).merge_to_main()

            with it("should hold the clone's changes on main beside the work"):
                expect(self.held.branches.trees["main"]).to(have_key("session.log"))

        with context("that is pushed to main"):
            with before.each:
                self.held.serve(self.tree).push_to_main()

            with it("should hold the work on main on origin"):
                expect(self.held.origin.trees["main"]).to(have_key("work.txt"))

            with it("should push the session's branch to origin"):
                expect(self.held.origin.trees[SESSION_BRANCH]).to(have_key("work.txt"))

    with context("from the clone itself, with the session's branch checked out"):
        with before.each:
            self.held.check_out(self.clone, SESSION_BRANCH)
            (self.clone / "work.txt").write_text("work\n", encoding="utf-8")

        with context("that is merged to main"):
            with before.each:
                self.held.serve(self.clone).merge_to_main()

            with it("should hold the work on main"):
                expect(self.held.branches.trees["main"]).to(have_key("work.txt"))

            with it("should leave the clone on the session's branch"):
                expect(self.held.branch_of(self.clone)).to(equal(SESSION_BRANCH))

    with context("from main itself, with work not committed"):
        with before.each:
            (self.clone / "work.txt").write_text("work\n", encoding="utf-8")

        with context("that is pushed to main"):
            with before.each:
                self.held.serve(self.clone).push_to_main()

            with it("should push the work to main on origin"):
                expect(self.held.origin.trees["main"]).to(have_key("work.txt"))

    with context("from a repository whose default branch is master"):
        with before.each:
            self.held.default_branch = "master"
            self.held.branches.trees["master"] = self.held.branches.trees.pop("main")
            self.held.branches.logs["master"] = self.held.branches.logs.pop("main")
            self.held.checked_out[self.clone] = "master"
            self.held.origin.add()
            self.tree = self.tmp / "clone-demo"
            self.held.add_worktree(SESSION_BRANCH, self.tree)
            (self.tree / "work.txt").write_text("work\n", encoding="utf-8")

        with context("that is pushed to main"):
            with before.each:
                self.held.serve(self.tree).push_to_main()

            with it("should push the work to master on origin"):
                expect(self.held.origin.trees["master"]).to(have_key("work.txt"))

# (E) Steer Sessions
# (S) Person --> Push Work From Chat Bar
with description("a session's work pushed on its own branch") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="session-push-"))
        self.clone = self.tmp / "clone"
        self.clone.mkdir()
        (self.clone / "seed.txt").write_text("seed\n", encoding="utf-8")
        self.held = MockGit(self.clone)
        self.held.make_clone()
        self.held.origin.add()
        self.tree = self.tmp / "clone-demo"
        self.held.add_worktree(SESSION_BRANCH, self.tree)
        (self.tree / "work.txt").write_text("work\n", encoding="utf-8")
        self.held.serve(self.tree).push_work()

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with it("should push the work on the session's branch to origin"):
        expect(self.held.origin.trees[SESSION_BRANCH]).to(have_key("work.txt"))

    with it("should leave main without the work"):
        expect(self.held.branches.trees["main"]).not_to(have_key("work.txt"))
