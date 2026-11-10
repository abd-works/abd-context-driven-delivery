"""BDD spec for space/repo — clone, branch, worktree, and push."""

import json
import os
import shutil
import sys
import subprocess
import tempfile
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_below, be_false, be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentToolSet
from harness.mcp.mcp_server import McpHost
from harness.process.git import Git, RepoConnectError
from space.repo.repo import (
    BranchInWorktreeError,
    BranchNameRequiredError,
    DefaultBranchError,
    NoOpenWorktreeError,
    Repo,
)
from space.work_state import WorkState


# (E) Open Work Session
# (E) Work With Repo Branch
with description("a Repo"):
    with context("on a clone whose origin has a main branch"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.origin, self.clone = _clone_with_origin(Path(self.tmp.name))
            self.repo = Repo(self.clone)

        with after.each:
            _remove_tree(self.tmp)

        # (S) Repo --> Commit Branch
        with it("should commit work on the branch checked out"):
            self.repo.branch_named("session/demo").check_out()
            (self.clone / "a.py").write_text("work\n", encoding="utf-8")
            self.repo.commit([str(self.clone / "a.py")], "demo turn", untracked=True)
            expect(_git(self.clone, "log", "-1", "--pretty=%s", "session/demo")).to(equal("demo turn"))

        # (S) Repo --> Merge Branch
        with it("should merge another branch into the branch checked out"):
            self.repo.branch_named("session/demo").check_out()
            (self.clone / "a.py").write_text("work\n", encoding="utf-8")
            self.repo.commit([str(self.clone / "a.py")], "demo turn", untracked=True)
            self.repo.branch_named("main").check_out()
            self.repo.merge_from(self.repo.branch_named("session/demo"), message="merge demo")
            expect(_git(self.clone, "ls-tree", "--name-only", "main")).to(contain("a.py"))

        with it("should name the files a branch changed since it left main"):
            self.repo.branch_named("session/demo").check_out()
            (self.clone / "a.py").write_text("work\n", encoding="utf-8")
            expect(self.repo.branch_named("session/demo").changed_files()).to(equal(["a.py"]))

        # (S) Repo --> Push Branch
        with context("with a commit pushed to its branch from elsewhere"):
            with before.each:
                self.repo.branch_named("session/demo").check_out()
                (self.clone / "a.py").write_text("work\n", encoding="utf-8")
                self.repo.commit([str(self.clone)], "first turn", untracked=True)
                self.repo.push_upstream()
                self.elsewhere = _clone_of(self.origin, Path(self.tmp.name) / "elsewhere", "session/demo")
                (self.elsewhere / "b.py").write_text("from elsewhere\n", encoding="utf-8")
                _git(self.elsewhere, "add", "-A")
                _git(self.elsewhere, "commit", "-m", "elsewhere turn")
                _git(self.elsewhere, "push", "origin", "session/demo")
                (self.clone / "a.py").write_text("more work\n", encoding="utf-8")
                self.repo.commit([str(self.clone)], "second turn", untracked=True)

            with it("should take that commit in when it pushes"):
                self.repo.push_upstream()
                expect((self.clone / "b.py").is_file()).to(be_true)

            with it("should push its own commit after it"):
                self.repo.push_upstream()
                expect(_git(self.origin, "log", "--format=%s", "session/demo")).to(contain("second turn"))

            with context("that changed the same lines of the same file"):
                with before.each:
                    (self.elsewhere / "a.py").write_text("theirs\n", encoding="utf-8")
                    _git(self.elsewhere, "commit", "-am", "conflicting turn")
                    _git(self.elsewhere, "push", "origin", "session/demo")

                with it("should refuse the push, naming the conflict"):
                    expect(lambda: self.repo.push_upstream()).to(raise_error(RepoConnectError))

                with it("should leave no merge half done"):
                    try:
                        self.repo.push_upstream()
                    except RepoConnectError:
                        pass
                    expect((self.clone / ".git" / "MERGE_HEAD").exists()).to(be_false)

        # Every branch appends to the same session logs, so landing one never stops on them.
        with context("with a session log both main and a branch appended to"):
            with before.each:
                log = self.clone / ".sessions" / "main" / "session.log"
                log.parent.mkdir(parents=True)
                log.write_text("start\n", encoding="utf-8")
                self.repo.commit([str(self.clone)], "log start", untracked=True)
                self.repo.push_upstream()
                self.repo.branch_named("session/demo").check_out()
                log.write_text("start\non the branch\n", encoding="utf-8")
                self.repo.commit([str(self.clone)], "branch line", untracked=True)
                self.repo.branch_named("main").check_out()
                log.write_text("start\non main\n", encoding="utf-8")
                self.repo.commit([str(self.clone)], "main line", untracked=True)
                self.repo.merge_from(self.repo.branch_named("session/demo"), message="merge demo")
                self.merged = log.read_text(encoding="utf-8")

            with it("should keep the lines main wrote"):
                expect(self.merged).to(contain("on main"))

            with it("should keep the lines the branch wrote"):
                expect(self.merged).to(contain("on the branch"))

        # Every tool call appends a line to the session log, so a switch never stops on it.
        with context("with a line not yet committed in a session log the next branch changed too"):
            with before.each:
                log = self.clone / ".sessions" / "main" / "session.log"
                log.parent.mkdir(parents=True)
                log.write_text("start\n", encoding="utf-8")
                self.repo.commit([str(self.clone)], "log start", untracked=True)
                self.repo.push_upstream()
                self.repo.branch_named("session/demo").check_out()
                log.write_text("start\non the branch\n", encoding="utf-8")
                self.repo.commit([str(self.clone)], "branch line", untracked=True)
                self.repo.branch_named("main").check_out()
                log.write_text("start\nnot committed\n", encoding="utf-8")
                self.repo.branch_named("session/demo").switch_to()
                self.switched = log.read_text(encoding="utf-8")

            with it("should switch to that branch"):
                expect(self.repo.current_branch.name).to(equal("session/demo"))

            with it("should carry the line not yet committed along"):
                expect(self.switched).to(contain("not committed"))

            with it("should keep the branch's own line"):
                expect(self.switched).to(contain("on the branch"))


# (E) Open Work Session
# (E) Work With Repo Worktree
with description("a Repo's worktrees"):
    with context("on a clone whose origin has a main branch"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.origin, self.clone = _clone_with_origin(Path(self.tmp.name))
            self.repo = Repo(self.clone)
            self.folder = Path(self.tmp.name) / "wt-demo"

        with after.each:
            _remove_tree(self.tmp)

        # (S) Repo --> List Worktree
        with it("should list the main clone with the branch it has checked out"):
            expect([tree.branch.name for tree in self.repo.worktrees]).to(equal(["main"]))

        # (S) Repo --> Open Worktree
        with it("should add a worktree for a session branch"):
            self.repo.worktrees.add(self.folder, self.repo.branch_named("session/demo"))
            expect(self.repo.branch_named("session/demo").worktree.path.resolve()).to(equal(self.folder.resolve()))

        # (S) Repo --> Reuse Worktree
        with it("should reuse the worktree a branch already has"):
            first = self.repo.worktrees.add(self.folder, self.repo.branch_named("session/demo"))
            second = self.repo.worktrees.add(Path(self.tmp.name) / "wt-demo-2", self.repo.branch_named("session/demo"))
            expect(second.path.resolve()).to(equal(first.path.resolve()))

        # (S) Repo --> Remove Worktree
        with it("should remove a worktree"):
            added = self.repo.worktrees.add(self.folder, self.repo.branch_named("session/demo"))
            self.repo.worktrees.remove(added)
            expect(self.repo.branch_named("session/demo").worktree).to(equal(None))

        # (S) Repo --> Remove Worktree
        with it("should run Windows takeown icacls and Remove-Item as last resort"):
            from unittest.mock import patch

            target = Path(self.tmp.name) / "locked-wt"
            target.mkdir()
            calls: list[tuple[str, ...]] = []

            def fake_run(args, **kwargs):
                calls.append(tuple(args))
                return subprocess.CompletedProcess(args, 0)

            with patch("space.repo.worktree.os.name", "nt"):
                with patch.dict(os.environ, {"USERNAME": "tester"}):
                    with patch("space.repo.worktree.shutil.rmtree"):
                        with patch("space.repo.worktree.subprocess.run", side_effect=fake_run):
                            self.repo.worktrees._force_remove_directory_windows(target)
            expect([calls[0][0], calls[1][0], any("Remove-Item" in " ".join(call) for call in calls)]).to(equal(["takeown", "icacls", True]))

        with it("should name a branch's sibling folder by the clone and the branch"):
            expect(self.repo.worktrees.sibling_folder(self.repo.branch_named("feature/a")).name).to(equal("clone-feature-a"))

        with it("should name a ticket branch's sibling folder by its ticket number"):
            expect(self.repo.worktrees.sibling_folder(self.repo.branch_named("checkout-flow-87")).name).to(equal("clone-87"))


with description("Repo dirty detection"):
    with it("should ignore events.log so session close is not blocked by the trail"):
        tmp = Path(tempfile.mkdtemp(prefix="git_events_log_"))
        git = Git(tmp)
        git.run("init")
        git.run("config", "user.email", "test@example.com")
        git.run("config", "user.name", "test")
        git.run("commit", "--allow-empty", "-m", "init")
        log = tmp / ".context" / "sessions" / "demo" / "logs" / "events.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("trail\n", encoding="utf-8")
        git.run("add", "-f", str(log))
        git.run("commit", "-m", "track log")
        log.write_text("more trail\n", encoding="utf-8")
        repo = Repo(tmp)
        expect(repo.is_dirty()).to(equal(False))
        (tmp / "real.txt").write_text("keep", encoding="utf-8")
        expect(repo.is_dirty()).to(equal(True))


# (E) Open Work Session
# (E) Work With Repo Branch
with description("a branch opened through the repo toolset"):
    with context("on a clone whose origin has a main branch"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.origin, self.clone = _clone_with_origin(Path(self.tmp.name))
            self.toolset = Repo(self.clone)

        with after.each:
            _remove_tree(self.tmp)

        # (S) Repo --> Switch Branch
        with it("should check out a new branch started from main"):
            self.toolset.switch_branch("feature/a")
            expect(_git(self.clone, "branch", "--show-current")).to(equal("feature/a"))

        with it("should save the branch in .sessions/session.json"):
            self.toolset.switch_branch("feature/a")
            expect(WorkState(self.clone).branch_name).to(equal("feature/a"))

        with it("should switch to the saved branch when no name is given"):
            WorkState(self.clone).branch_name = "feature/saved"
            self.toolset.switch_branch()
            expect(_git(self.clone, "branch", "--show-current")).to(equal("feature/saved"))

        with it("should refuse to switch with no name and no saved branch"):
            expect(lambda: self.toolset.switch_branch()).to(raise_error(BranchNameRequiredError))

        with context("with uncommitted work on main"):
            with before.each:
                (self.clone / "main-work.txt").write_text("main work\n", encoding="utf-8")
                self.toolset.switch_branch("feature/a")

            # A switch commits nothing: git carries uncommitted work to the branch switched to.
            with it("should carry that work, uncommitted, onto the branch switched to"):
                expect(_git(self.clone, "status", "--porcelain")).to(contain("main-work.txt"))

            with it("should not push main to origin"):
                expect(_git(self.origin, "ls-tree", "--name-only", "main")).not_to(contain("main-work.txt"))

        with context("with uncommitted work on a feature branch"):
            with before.each:
                self.toolset.switch_branch("feature/a")
                (self.clone / "work.txt").write_text("feature work\n", encoding="utf-8")

            with it("should carry that work, uncommitted, onto the branch switched to"):
                self.toolset.switch_branch("feature/b")
                expect(_git(self.clone, "status", "--porcelain")).to(contain("work.txt"))

            # (S) Repo --> Close Branch
            with it("should merge the branch into main on origin when closed"):
                self.toolset.close_branch()
                expect(_git(self.origin, "ls-tree", "--name-only", "main")).to(contain("work.txt"))

            with it("should delete the closed branch from origin"):
                self.toolset.close_branch()
                expect(_git(self.origin, "branch", "--list", "feature/a")).to(equal(""))

            with it("should delete the closed branch from the clone"):
                self.toolset.close_branch()
                expect(_git(self.clone, "branch", "--list", "feature/a")).to(equal(""))

            with it("should leave the clone on main after close"):
                self.toolset.close_branch()
                expect(_git(self.clone, "branch", "--show-current")).to(equal("main"))

            with it("should save main as the branch after close"):
                self.toolset.close_branch()
                expect(WorkState(self.clone).branch_name).to(equal("main"))

        with it("should refuse to close main"):
            expect(lambda: self.toolset.close_branch("main")).to(raise_error(DefaultBranchError))

        with context("with end-to-end results from the release that lands and from older ones"):
            with before.each:
                self.toolset.switch_branch("feature/a")
                WorkState(self.clone).session = "new-release"
                (self.clone / ".gitignore").write_text(
                    ".sessions/session.json\n.sessions/*/e2e-test-results/**/*.png\n", encoding="utf-8"
                )
                self.latest = _release_screenshot(self.clone, "new-release", finished=True)
                self.older = _release_screenshot(self.clone, "old-release", finished=True)
                self.recording = _release_screenshot(self.clone, "pml-my", finished=False)
                self.toolset.close_branch()

            with it("should push the landed release's screenshots to e2e-latest"):
                expect(_git(self.origin, "ls-tree", "-r", "--name-only", "e2e-latest")).to(
                    equal(".sessions/new-release/e2e-test-results/run/pml-web/step.png")
                )

            with it("should keep the landed release's screenshots in the clone"):
                expect(self.latest.exists()).to(equal(True))

            with it("should remove an older release's results from the clone"):
                expect(self.older.parent.parent.parent.exists()).to(equal(False))

            with it("should remove an older release's results from main on origin"):
                expect(_git(self.origin, "ls-tree", "-r", "--name-only", "main")).not_to(contain(".sessions/old-release/"))

            with it("should keep the landed release's results on main on origin"):
                expect(_git(self.origin, "ls-tree", "-r", "--name-only", "main")).to(
                    contain(".sessions/new-release/e2e-test-results/run/pml-web/step.json")
                )

            with it("should keep the results of a release that never finished a run"):
                expect(_git(self.origin, "ls-tree", "-r", "--name-only", "main")).to(
                    contain(".sessions/pml-my/e2e-test-results/run/pml-web/step.json")
                )

            with it("should leave screenshots out of main"):
                expect(_git(self.origin, "ls-tree", "-r", "--name-only", "main")).not_to(contain(".png"))

        with context("loaded for the project a call names"):
            with before.each:
                (Path(self.tmp.name) / "host").mkdir()
                self.host_origin, self.host = _clone_with_origin(Path(self.tmp.name) / "host")
                Repo.of_project(self.clone).switch_branch("feature/a")

            with it("should switch that project's clone"):
                expect(_git(self.clone, "branch", "--show-current")).to(equal("feature/a"))

            with it("should leave another project's clone on main"):
                expect(_git(self.host, "branch", "--show-current")).to(equal("main"))

            with it("should save the branch in that project's .sessions/session.json"):
                expect(WorkState(self.clone).branch_name).to(equal("feature/a"))

            with it("should commit and push in that project's clone"):
                (self.clone / "work.txt").write_text("feature work\n", encoding="utf-8")
                Repo.of_project(self.clone).push_commit("work")
                expect(_git(self.origin, "ls-tree", "--name-only", "feature/a")).to(contain("work.txt"))

            with it("should close the branch in that project's clone"):
                Repo.of_project(self.clone).close_branch()
                expect(_git(self.clone, "branch", "--list", "feature/a")).to(equal(""))


# (E) Open Work Session
# (E) Work With Repo Worktree
with description("a worktree opened through the repo toolset"):
    with context("on a clone whose origin has a main branch"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.origin, self.clone = _clone_with_origin(Path(self.tmp.name))
            self.toolset = Repo(self.clone)

        with after.each:
            _remove_tree(self.tmp)

        with it("should refuse a worktree for main"):
            expect(lambda: self.toolset.switch_worktree("main")).to(raise_error(DefaultBranchError))

        with context("with a feature branch open in the clone"):
            with before.each:
                self.toolset.switch_branch("feature/a")

            # (S) Repo --> Open Worktree
            with it("should check the branch out in a sibling folder"):
                self.toolset.switch_worktree()
                tree = WorkState(self.clone).worktree_folder
                expect(_git(tree, "branch", "--show-current")).to(equal("feature/a"))

            with it("should move the clone back to main"):
                self.toolset.switch_worktree()
                expect(_git(self.clone, "branch", "--show-current")).to(equal("main"))

            with context("that has an open worktree with uncommitted work"):
                with before.each:
                    self.toolset.switch_worktree()
                    self.tree = WorkState(self.clone).worktree_folder
                    (self.tree / "tree.txt").write_text("worktree work\n", encoding="utf-8")

                # (S) Repo --> Close Worktree
                with it("should push the work to the branch on origin when closed"):
                    self.toolset.close_worktree()
                    expect(_git(self.origin, "ls-tree", "--name-only", "feature/a")).to(contain("tree.txt"))

                with it("should remove the worktree folder when closed"):
                    self.toolset.close_worktree()
                    expect(self.tree.exists()).to(equal(False))

                with it("should clear the worktree from .sessions/session.json when closed"):
                    self.toolset.close_worktree()
                    expect(WorkState(self.clone).worktree_folder).to(equal(None))

                with it("should keep the branch open when closed"):
                    self.toolset.close_worktree()
                    expect(WorkState(self.clone).branch_name).to(equal("feature/a"))

                with it("should refuse to close the branch while its worktree is open"):
                    expect(lambda: self.toolset.close_branch()).to(raise_error(BranchInWorktreeError))

                with it("should commit in the worktree when pushed from the main clone"):
                    Repo(self.clone).push_commit("worktree work")
                    expect(_git(self.origin, "ls-tree", "--name-only", "feature/a")).to(contain("tree.txt"))

                with it("should commit in the worktree when pushed from a new toolset after a restart"):
                    fresh = Repo(self.clone)
                    fresh.push_commit("worktree work", sync_remote=False)
                    expect(_git(self.tree, "status", "--porcelain")).to(equal(""))

        with it("should refuse to close a worktree when none is open"):
            expect(lambda: self.toolset.close_worktree()).to(raise_error(NoOpenWorktreeError))

        with context("loaded for the project a call names"):
            with before.each:
                Repo.of_project(self.clone).switch_worktree("feature/a")
                self.tree = WorkState(self.clone).worktree_folder

            with it("should open the worktree beside that project's clone"):
                expect(_git(self.tree, "branch", "--show-current")).to(equal("feature/a"))

            with it("should remove that project's worktree when closed"):
                Repo.of_project(self.clone).close_worktree()
                expect(self.tree.exists()).to(equal(False))


# (E) Open Work Session
# (S) Repo --> Run Git
with description("a git command that outlives its timeout"):
    with context("run through a launcher that leaves a child holding the output pipes"):
        with it("should give up within seconds of the timeout"):
            launcher = [
                sys.executable,
                "-c",
                "import subprocess, sys; subprocess.run([sys.executable, '-c', 'import time; time.sleep(60)'])",
            ]
            started = time.monotonic()
            expect(lambda: Git(".")._run_process(launcher, 1)).to(raise_error(subprocess.TimeoutExpired))
            expect(time.monotonic() - started).to(be_below(15))

    with context("that rewrites the working tree"):
        with it("should get the long limit so a slow checkout is not stopped partway"):
            from unittest.mock import patch

            with patch.object(Git, "_run_process", return_value=(0, "", "")) as run:
                Git(".").run("checkout", "main")
            expect(run.call_args.args[1]).to(equal(180))

    with context("that only reads the repository"):
        with it("should keep the short limit so a hung git fails fast"):
            from unittest.mock import patch

            with patch.object(Git, "_run_process", return_value=(0, "", "")) as run:
                Git(".").run("status")
            expect(run.call_args.args[1]).to(equal(10))


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _release_screenshot(clone: Path, release: str, *, finished: bool) -> Path:
    """One step's recording and screenshot in the release's end-to-end results; a finished run also writes the release's
    story map."""
    results = clone / ".sessions" / release / "e2e-test-results"
    shot = results / "run" / "pml-web" / "step.png"
    shot.parent.mkdir(parents=True)
    shot.write_bytes(b"png")
    (shot.parent / "step.json").write_text("{}", encoding="utf-8")
    if finished:
        (results / "story-map.html").write_text("<html></html>", encoding="utf-8")
    return shot


def _clone_with_origin(root: Path) -> tuple[Path, Path]:
    origin = root / "origin.git"
    seed = root / "seed"
    clone = root / "clone"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)
    subprocess.run(["git", "init", "-b", "main", str(seed)], check=True, capture_output=True)
    _init_repository(seed)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _git(seed, "add", "README.md")
    _git(seed, "commit", "-m", "seed")
    _git(seed, "push", str(origin), "main")
    subprocess.run(["git", "clone", str(origin), str(clone)], check=True, capture_output=True)
    _init_repository(clone)
    (clone / ".gitignore").write_text(".sessions/session.json\n", encoding="utf-8")
    _git(clone, "add", ".gitignore")
    _git(clone, "commit", "-m", "ignore session state")
    _git(clone, "push", "origin", "main")
    return origin, clone


def _clone_of(origin: Path, folder: Path, branch: str) -> Path:
    """Another clone of origin with branch checked out, standing for a person pushing from elsewhere."""
    subprocess.run(["git", "clone", "-b", branch, str(origin), str(folder)], check=True, capture_output=True)
    _init_repository(folder)
    return folder


def _remove_tree(tmp: tempfile.TemporaryDirectory) -> None:
    shutil.rmtree(tmp.name, ignore_errors=True)


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


# (E) Open Work Session
# (E) Work With Repo Branch
# (S) Repo --> Commit Branch
with description("the repo push toolset"):
    with context("that is in a git repository"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self._cwd = Path.cwd()
            root = Path(self.tmp.name)
            origin = root / "origin.git"
            subprocess.run(
                ["git", "init", "--bare", str(origin)],
                check=True,
                capture_output=True,
            )
            self.repo_root = root / "work"
            self.repo_root.mkdir()
            _init_repository(self.repo_root)
            subprocess.run(
                ["git", "remote", "add", "origin", str(origin)],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
            )
            os.chdir(self.repo_root)

        with after.each:
            os.chdir(self._cwd)
            self.tmp.cleanup()

        with it("should commit when push_commit is called"):
            (self.repo_root / "note.txt").write_text("checkpoint\n", encoding="utf-8")
            commit = Repo.of_project(self.repo_root).push_commit("push: checkpoint")
            expect(commit.sha).not_to(equal(""))
            expect(commit.subject).to(equal("push: checkpoint"))

        with it("should return the new commit as JSON through the MCP host"):
            (self.repo_root / "note.txt").write_text("checkpoint\n", encoding="utf-8")
            host = McpHost.from_refs(
                ("space.repo.repo:Repo",),
                repo=str(self.repo_root),
                project=str(self.repo_root),
            )
            commit = host.dispatch(
                "repo.push_commit", {"message": "push: checkpoint", "sync_remote": False}
            )
            payload = json.loads(host._content_blocks(commit)[0].text)
            expect(payload["sha"]).to(equal(_git(self.repo_root, "rev-parse", "HEAD")))

        with it("should publish push_commit on MCP and keep /push as instructions only"):
            from harness.agent_tools.agent_tools import InstallDestination

            toolset = AgentToolSet.instantiate("space.repo.repo:Repo")
            mcp_names = [tool.name for tool in toolset.tools_for(InstallDestination.MCP)]
            expect("push_commit" in mcp_names).to(equal(True))
            expect("push" in mcp_names).to(equal(False))
            expect("push_commit" in toolset.instructions["push"].description).to(equal(True))
