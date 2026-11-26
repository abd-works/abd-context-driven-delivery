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

from harness.agent_tools.agent_tools import AgentToolSet, ToolsetReference
from harness.mcp.mcp_server import ChatProtocol, McpHost
from harness.git.git import Git, RepoConnectError
from space.repo.built_once import BuiltOnce
from space.repo.folder_deletion import FolderDeletion
from space.repo.latest_release import LatestRelease
from space.repo.repo import NothingToCommitError, Repo
from space.repo.origin import MergeRefusedError


# Seed: a file whose name git writes in quotes with octal escapes unless it is asked for NUL-ended entries.
QUOTED_BY_GIT = "ünïcödé_日本.py"
NOT_COMMITTED = "café.md"

# (E) Open Work Session
# (E) Work With Repo Branch
with description("a Repo"):
    with context("on a clone whose origin has a main branch"):
        with before.each:
            self.top = _CLONES.copy()
            self.origin, self.clone = self.top / "origin.git", self.top / "clone"
            self.repo = Repo(self.clone)

        with after.each:
            shutil.rmtree(self.top, ignore_errors=True)

        # (S) Repo --> Commit Branch
        with it("should commit work on the branch checked out"):
            self.repo.branch_named("session/demo").check_out()
            (self.clone / "a.py").write_text("work\n", encoding="utf-8")
            self.repo.working_tree.commit([str(self.clone / "a.py")], "demo turn", untracked=True)
            expect(_git(self.clone, "log", "-1", "--pretty=%s", "session/demo")).to(equal("demo turn"))

        # (S) Repo --> Merge Branch
        with it("should merge another branch into the branch checked out"):
            self.repo.branch_named("session/demo").check_out()
            (self.clone / "a.py").write_text("work\n", encoding="utf-8")
            self.repo.working_tree.commit([str(self.clone / "a.py")], "demo turn", untracked=True)
            self.repo.branch_named("main").check_out()
            self.repo.merges.merge_from(self.repo.branch_named("session/demo"), message="merge demo")
            expect(_git(self.clone, "ls-tree", "--name-only", "main")).to(contain("a.py"))

        with it("should name the files a branch changed since it left main"):
            self.repo.branch_named("session/demo").check_out()
            (self.clone / "a.py").write_text("work\n", encoding="utf-8")
            expect(self.repo.branch_named("session/demo").changed_files()).to(equal(["a.py"]))

        with context("with a branch that committed a file whose name git quotes, and changed a tracked file without staging it"):
            with before.each:
                self.repo.branch_named("session/demo").check_out()
                (self.clone / QUOTED_BY_GIT).write_text("uni = 1" + chr(10), encoding="utf-8")
                _git(self.clone, "add", "-A")
                _git(self.clone, "commit", "-m", "demo turn")
                (self.clone / "README.md").write_text("changed" + chr(10), encoding="utf-8")
                (self.clone / NOT_COMMITTED).write_text("# café" + chr(10), encoding="utf-8")

            with it("should name each file as it is on disk"):
                expect(sorted(self.repo.branch_named("session/demo").changed_files())).to(equal(sorted(["README.md", QUOTED_BY_GIT, NOT_COMMITTED])))

        with context("with a branch checked out in a worktree of its own, a file committed there and one not yet"):
            with before.each:
                self.tree = self.top / "ticket-tree"
                _git(self.clone, "worktree", "add", "-b", "session/ticket", str(self.tree), "main")
                (self.tree / "done.py").write_text("work", encoding="utf-8")
                _git(self.tree, "add", "done.py")
                _git(self.tree, "commit", "-m", "ticket turn")
                (self.tree / "doing.py").write_text("work", encoding="utf-8")

            with it("should find the branch checked out in that worktree"):
                expect(self.repo.branch_named("session/ticket").checkout.root).to(equal(self.tree.resolve()))

            with it("should name both files, read from the clone"):
                expect(sorted(self.repo.branch_named("session/ticket").changed_files())).to(equal(["doing.py", "done.py"]))

        # A linked worktree's .git is a file naming its own git folder, which holds the merge going on there.
        with context("with a ticket's branch in a worktree of its own, stopped part way through merging main"):
            with before.each:
                self.tree = self.top / "ticket-tree"
                _git(self.clone, "worktree", "add", "-b", "session/ticket", str(self.tree), "main")
                (self.tree / "a.py").write_text("ticket\n", encoding="utf-8")
                _git(self.tree, "add", "a.py")
                _git(self.tree, "commit", "-m", "ticket turn")
                (self.clone / "a.py").write_text("main\n", encoding="utf-8")
                _git(self.clone, "add", "a.py")
                _git(self.clone, "commit", "-m", "main turn")
                subprocess.run(["git", "-C", str(self.tree), "merge", "main"], capture_output=True)
                (self.tree / "a.py").write_text("both\n", encoding="utf-8")
                self.ticket = Repo(self.tree)

            with it("should see the merge going on in that worktree"):
                expect(self.ticket.working_tree.is_merging).to(be_true)

            with it("should conclude the merge when it commits, rather than commit the paths it was named alone"):
                self.ticket.working_tree.commit([str(self.tree / "a.py")], "merge main into the ticket")
                expect(len(_git(self.tree, "log", "-1", "--format=%P").split())).to(equal(2))

        # (S) Repo --> Push Branch
        with context("with a commit pushed to its branch from elsewhere"):
            with before.each:
                self.repo.branch_named("session/demo").check_out()
                (self.clone / "a.py").write_text("work\n", encoding="utf-8")
                self.repo.working_tree.commit([str(self.clone)], "first turn", untracked=True)
                self.repo.origin.push_upstream()
                self.elsewhere = _clone_of(self.origin, self.top / "elsewhere", "session/demo")
                (self.elsewhere / "b.py").write_text("from elsewhere\n", encoding="utf-8")
                _git(self.elsewhere, "add", "-A")
                _git(self.elsewhere, "commit", "-m", "elsewhere turn")
                _git(self.elsewhere, "push", "origin", "session/demo")
                (self.clone / "a.py").write_text("more work\n", encoding="utf-8")
                self.repo.working_tree.commit([str(self.clone)], "second turn", untracked=True)

            with it("should take that commit in when it pushes"):
                self.repo.origin.push_upstream()
                expect((self.clone / "b.py").is_file()).to(be_true)

            with it("should push its own commit after it"):
                self.repo.origin.push_upstream()
                expect(_git(self.origin, "log", "--format=%s", "session/demo")).to(contain("second turn"))

            with context("that changed the same lines of the same file"):
                with before.each:
                    (self.elsewhere / "a.py").write_text("theirs\n", encoding="utf-8")
                    _git(self.elsewhere, "commit", "-am", "conflicting turn")
                    _git(self.elsewhere, "push", "origin", "session/demo")

                with it("should refuse the push, naming the branch that does not merge and the one it would merge into"):
                    expect(lambda: self.repo.origin.push_upstream()).to(raise_error(MergeRefusedError, contain("origin/session/demo does not merge into session/demo")))

                with it("should leave no merge half done"):
                    try:
                        self.repo.origin.push_upstream()
                    except RepoConnectError:
                        pass
                    expect((self.clone / ".git" / "MERGE_HEAD").exists()).to(be_false)

        # Every branch appends to the same session logs, so landing one never stops on them.
        with context("with a session log both main and a branch appended to"):
            with before.each:
                log = self.clone / ".sessions" / "main" / "session.log"
                log.parent.mkdir(parents=True)
                log.write_text("start\n", encoding="utf-8")
                self.repo.working_tree.commit([str(self.clone)], "log start", untracked=True)
                self.repo.origin.push_upstream()
                self.repo.branch_named("session/demo").check_out()
                log.write_text("start\non the branch\n", encoding="utf-8")
                self.repo.working_tree.commit([str(self.clone)], "branch line", untracked=True)
                self.repo.branch_named("main").check_out()
                log.write_text("start\non main\n", encoding="utf-8")
                self.repo.working_tree.commit([str(self.clone)], "main line", untracked=True)
                self.repo.merges.merge_from(self.repo.branch_named("session/demo"), message="merge demo")
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
                self.repo.working_tree.commit([str(self.clone)], "log start", untracked=True)
                self.repo.origin.push_upstream()
                self.repo.branch_named("session/demo").check_out()
                log.write_text("start\non the branch\n", encoding="utf-8")
                self.repo.working_tree.commit([str(self.clone)], "branch line", untracked=True)
                self.repo.branch_named("main").check_out()
                log.write_text("start\nnot committed\n", encoding="utf-8")
                self.repo.branch_named("session/demo").check_out()
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
            self.top = _CLONES.copy()
            self.origin, self.clone = self.top / "origin.git", self.top / "clone"
            self.repo = Repo(self.clone)
            self.folder = self.top / "wt-demo"

        with after.each:
            shutil.rmtree(self.top, ignore_errors=True)

        # (S) Repo --> List Worktree
        with it("should list the main clone with the branch it has checked out"):
            expect([tree.current_branch.name for tree in self.repo.worktrees]).to(equal(["main"]))

        # (S) Repo --> Open Worktree
        with it("should add a worktree for a session branch"):
            self.repo.worktrees.add(self.folder, self.repo.branch_named("session/demo"))
            expect(self.repo.branch_named("session/demo").checkout.root).to(equal(self.folder.resolve()))

        # (S) Repo --> Reuse Worktree
        with it("should reuse the worktree a branch already has"):
            first = self.repo.worktrees.add(self.folder, self.repo.branch_named("session/demo"))
            second = self.repo.worktrees.add(self.top / "wt-demo-2", self.repo.branch_named("session/demo"))
            expect(second.root).to(equal(first.root))

        # (S) Repo --> Remove Worktree
        with it("should remove a worktree"):
            added = self.repo.worktrees.add(self.folder, self.repo.branch_named("session/demo"))
            self.repo.worktrees.remove(added)
            expect(self.repo.branch_named("session/demo").checkout).to(equal(None))

        # (S) Repo --> Remove Worktree
        with it("should run Windows takeown icacls and Remove-Item as last resort"):
            from unittest.mock import patch

            target = self.top / "locked-wt"
            target.mkdir()
            calls: list[tuple[str, ...]] = []

            def fake_run(args, **kwargs):
                calls.append(tuple(args))
                return subprocess.CompletedProcess(args, 0)

            with patch("space.repo.folder_deletion.os.name", "nt"):
                with patch.dict(os.environ, {"USERNAME": "tester"}):
                    with patch("space.repo.folder_deletion.shutil.rmtree"):
                        with patch("space.repo.folder_deletion.subprocess.run", side_effect=fake_run):
                            FolderDeletion(target).delete()
            taken_over = [call[0] for call in calls if call[0] in ("takeown", "icacls")]
            expect([taken_over, any("Remove-Item" in " ".join(call) for call in calls)]).to(equal([["takeown", "icacls"], True]))

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
        expect(repo.working_tree.is_dirty()).to(equal(False))
        (tmp / "real.txt").write_text("keep", encoding="utf-8")
        expect(repo.working_tree.is_dirty()).to(equal(True))


# (E) Open Work Session
# (S) Repo --> Keep Latest Release
# A ticket that closes with its branch merged lands its release; its end-to-end results are the only ones kept.
with description("a release that lands on the default branch"):
    # Keeping the release changes the clone and origin once; every example only reads what it left.
    with context("with end-to-end results from it and from older releases"):
        with before.all:
            self.top = _CLONES.copy()
            self.origin, self.clone = self.top / "origin.git", self.top / "clone"
            (self.clone / ".gitignore").write_text(".sessions/*/e2e-test-results/**/*.png\n", encoding="utf-8")
            self.latest = _release_screenshot(self.clone, "new-release", finished=True)
            self.older = _release_screenshot(self.clone, "old-release", finished=True)
            self.recording = _release_screenshot(self.clone, "pml-my", finished=False)
            _git(self.clone, "add", "-A")
            _git(self.clone, "commit", "-m", "results")
            _git(self.clone, "push", "origin", "main")
            LatestRelease(Repo(self.clone), "new-release").keep()

        with after.all:
            shutil.rmtree(self.top, ignore_errors=True)

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


# (E) Open Work Session
# (S) Repo --> Push Commit
# A chat's calls name its own folder, so a commit lands in the checkout that chat works in.
with description("a commit pushed through the repo toolset"):
    with context("on a clone whose origin has a main branch"):
        with before.each:
            self.top = _CLONES.copy()
            self.origin, self.clone = self.top / "origin.git", self.top / "clone"

        with after.each:
            shutil.rmtree(self.top, ignore_errors=True)

        with context("for the project a call names, beside another project"):
            with before.each:
                self.other_top = _CLONES.copy()
                self.other_origin, self.other = self.other_top / "origin.git", self.other_top / "clone"
                (self.clone / "work.txt").write_text("work\n", encoding="utf-8")
                Repo.of_project(self.clone).push_commit("work")

            with after.each:
                shutil.rmtree(self.other_top, ignore_errors=True)

            with it("should commit and push in that project's clone"):
                expect(_git(self.origin, "ls-tree", "--name-only", "main")).to(contain("work.txt"))

            with it("should leave the other project's clone as it was"):
                expect(_git(self.other_origin, "ls-tree", "--name-only", "main")).not_to(contain("work.txt"))

        with context("from a linked worktree of the clone"):
            with before.each:
                self.tree = self.top / "clone-feature"
                _git(self.clone, "worktree", "add", "-q", "-b", "feature/a", str(self.tree))
                (self.tree / "tree.txt").write_text("worktree work\n", encoding="utf-8")
                Repo.of_project(self.tree).push_commit("worktree work")

            with it("should commit on the worktree's branch"):
                expect(_git(self.tree, "log", "-1", "--format=%s")).to(equal("worktree work"))

            with it("should push the worktree's branch to origin"):
                expect(_git(self.origin, "ls-tree", "--name-only", "feature/a")).to(contain("tree.txt"))

            with it("should leave main without that commit"):
                expect(_git(self.clone, "log", "-1", "--format=%s", "main")).not_to(equal("worktree work"))


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


def _clone_with_origin(root: Path) -> None:
    """A bare origin with main, and a clone of it whose main carries one commit more, pushed."""
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


def _clone_of(origin: Path, folder: Path, branch: str) -> Path:
    """Another clone of origin with branch checked out, standing for a person pushing from elsewhere."""
    subprocess.run(["git", "clone", "-b", branch, str(origin), str(folder)], check=True, capture_output=True)
    _init_repository(folder)
    return folder


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


def _work_with_empty_origin(root: Path) -> None:
    """A repository with no commit yet whose origin is a bare repository with none either."""
    origin = root / "origin.git"
    subprocess.run(["git", "init", "--bare", str(origin)], check=True, capture_output=True)
    work = root / "work"
    work.mkdir()
    _init_repository(work)
    subprocess.run(["git", "remote", "add", "origin", str(origin)], cwd=work, check=True, capture_output=True)


# Each example gets a copy of repositories built once for the run, rather than starting git a dozen times to build them.
_CLONES = BuiltOnce("repo-spec-clone-", _clone_with_origin)
_EMPTY_WORK = BuiltOnce("repo-spec-work-", _work_with_empty_origin)


# (E) Open Work Session
# (E) Work With Repo Branch
# (S) Repo --> Commit Branch
with description("the repo push toolset"):
    with context("that is in a git repository"):
        with before.each:
            self.top = _EMPTY_WORK.copy()
            self._cwd = Path.cwd()
            self.repo_root = self.top / "work"
            os.chdir(self.repo_root)

        with after.each:
            os.chdir(self._cwd)
            shutil.rmtree(self.top, ignore_errors=True)

        with it("should commit when push_commit is called"):
            (self.repo_root / "note.txt").write_text("checkpoint\n", encoding="utf-8")
            commit = Repo.of_project(self.repo_root).push_commit("push: checkpoint")
            expect(commit.sha).not_to(equal(""))
            expect(commit.subject).to(equal("push: checkpoint"))

        with it("should name the checkout it committed in"):
            (self.repo_root / "note.txt").write_text("checkpoint\n", encoding="utf-8")
            commit = Repo.of_project(self.repo_root).push_commit("push: checkpoint", sync_remote=False)
            expect(Path(commit.checkout)).to(equal(self.repo_root.resolve()))

        with it("should refuse when the checkout has no changes"):
            expect(
                lambda: Repo.of_project(self.repo_root).push_commit("push: checkpoint", sync_remote=False)
            ).to(raise_error(NothingToCommitError))

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
            payload = json.loads(ChatProtocol(host).content_blocks(commit)[0].text)
            expect(payload["sha"]).to(equal(_git(self.repo_root, "rev-parse", "HEAD")))

        with it("should publish push_commit on MCP and keep /push as instructions only"):
            from harness.mcp.mcp_annotations import Mcp

            toolset = ToolsetReference.parsed("space.repo.repo:Repo").made()
            mcp_names = [tool.name for tool in toolset.tools_published_to(Mcp)]
            expect("push_commit" in mcp_names).to(equal(True))
            expect("push" in mcp_names).to(equal(False))
            expect("push_commit" in toolset.instructions["push"].description).to(equal(True))
