"""BDD — repo toolset branch switch/create/close (memory clone)."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from space.repo import repo as clone
from space.repo.agent import Repo


with description("the repo toolset"):
    with context("on a memory repository"):
        with before.each:
            self.repo_tool = Repo()
            self.repository = clone.Repo.memory("/tmp/repo-branch-spec")
            self.repository.checkout_or_create("main")
            self.repo_tool._bind(self.repository)

        with it("should switch branch in place when work_tree is false"):
            self.repo_tool.branch_switch("feature/a", work_tree=False)
            expect(self.repo_tool.current_branch).to(equal("feature/a"))

        with it("should create and switch a new branch"):
            self.repo_tool.branch_create("feature/new", work_tree=False, switch=True)
            expect(self.repo_tool.current_branch).to(equal("feature/new"))

        with it("should close without error on memory repo"):
            self.repo_tool.branch_create("feature/done", work_tree=False)
            text = self.repo_tool.branch_close(merge_to_main=True)
            expect("feature/done" in text).to(equal(True))
