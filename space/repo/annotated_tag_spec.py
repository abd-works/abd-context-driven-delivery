"""BDD spec — the CLI agents kept on a branch's tag, and the annotated tags written after them."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.repo import CliAgents, Repo  # noqa: E402


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _commit_of(root: Path, ref: str) -> str:
    return _git(root, "rev-parse", f"{ref}^{{commit}}")


with description("a branch's CLI agents") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="annotated-tag-spec-"))
        _git(self.root, "init", "-q", "-b", "main")
        _git(self.root, "config", "user.email", "tag@test")
        _git(self.root, "config", "user.name", "tag")
        _git(self.root, "commit", "-q", "--allow-empty", "-m", "first")
        _git(self.root, "branch", "session/demo")
        _git(self.root, "commit", "-q", "--allow-empty", "-m", "second")
        self.repo = Repo(self.root)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("that have been written on a branch behind HEAD"):
        with before.each:
            self.repo.branch_named("session/demo").write_cli_agents(CliAgents(status="open", doer="doer-chat"))

        with it("should be read back from the branch"):
            expect(self.repo.branch_named("session/demo").cli_agents().doer).to(equal("doer-chat"))

        with it("should tag the branch's commit"):
            expect(_commit_of(self.root, "cli-agent/session/demo")).to(equal(_commit_of(self.root, "session/demo")))

        with it("should leave the next annotated tag on HEAD"):
            self.repo.write_annotated_tag("chat/session/demo", "C:/chats/one.jsonl")
            expect(_commit_of(self.root, "chat/session/demo")).to(equal(_commit_of(self.root, "HEAD")))
