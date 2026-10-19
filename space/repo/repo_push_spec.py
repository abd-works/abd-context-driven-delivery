"""BDD for repo push (commit + sync)."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentToolSet
from space.repo.agent import Repo


def _init_repository(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "push@test"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "push"],
        cwd=root,
        check=True,
        capture_output=True,
    )


with description("the repo push toolset"):
    with context("that is in a git repository"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self._cwd = Path.cwd()
            self.repo_root = Path(self.tmp.name)
            _init_repository(self.repo_root)
            os.chdir(self.repo_root)

        with after.each:
            os.chdir(self._cwd)
            self.tmp.cleanup()

        with it("should commit when push_commit is called"):
            toolset = AgentToolSet.instantiate("space.repo.agent:Repo")
            commit = toolset.push_commit("push: checkpoint")
            expect(commit.sha).not_to(equal(""))
            expect(commit.subject).to(equal("push: checkpoint"))
