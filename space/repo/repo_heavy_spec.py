"""BDD spec for space/repo — clone, branch, worktree, and push."""

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

from expects import be_a, be_below, be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentToolSet
from space.repo import TicketNotFoundError
from space.repo.repo import (
    Branch,
    BranchInWorktreeError,
    BranchNameRequiredError,
    CliAgentBinding,
    Commit,
    DefaultBranchError,
    GH_PROJECT_SCOPES_HINT,
    GhConnectError,
    NoOpenWorktreeError,
    Project,
    Repo,
    Ticket,
    TicketState,
    issue_theme_label,
)
from space.work_state import WorkState


with description("a Ticket"):
    with it("should parse github issue references"):
        expect(Ticket.from_number("87")).to(equal(87))
        expect(Ticket.from_number("#87")).to(equal(87))
        expect(Ticket.from_number("demo-org/demo-repo#87")).to(equal(87))

    with it("should format its github ref"):
        expect(Ticket.github_ref("demo-org", "demo-repo", 87)).to(
            equal("demo-org/demo-repo#87")
        )


with description("a Commit"):
    with it("should format a message with trailers"):
        message = Commit.format(
            "start workflow-package-87",
            {
                "GitHub-Issue": "demo-org/demo-repo#87",
                "Workflow-State": "specification",
            },
        )
        expect(message).to(contain("Workflow-State: specification"))


with description("a Repo"):
    with context("opened in memory"):
        with before.each:
            self.repo = Repo.memory("/tmp/demo-clone")

        # (E) Open Work Session
        # (E) Work With Repo Branch
        # (S) Repo --> Commit Branch
        with it("should expose branches that can commit"):
            commit = self.repo.branch_named("session/demo").checkout().commit(
                ["README.md"], "demo turn"
            )
            expect(commit).to(be_a(Commit))
            expect(commit.message).to(equal("demo turn"))
            expect(self.repo.current_branch).to(equal("session/demo"))

        with it("should persist a cli-agent binding on the branch tag"):
            import os

            binding = CliAgentBinding(
                status="open",
                doer="doer-chat",
                doer_pid=os.getpid(),
                judge="judge-chat",
                judge_pid=0,
            )
            binding.write_tag(self.repo, "session/demo")
            loaded = self.repo.branch_named("session/demo").cli_agent()
            expect(loaded.doer).to(equal("doer-chat"))
            expect(loaded.judge).to(equal("judge-chat"))
            expect(loaded.open).to(be_true)

        with it("should store commit trailer data on the commit object"):
            message = self.repo.workflow_commit_message(
                "finish demo",
                87,
                "done",
                reviewed_by="human",
            )
            sha = self.repo.commit(["README.md"], message)
            commit = Commit.from_message(sha, message)
            expect(commit.data["GitHub-Issue"]).to(equal("demo-org/demo-repo#87"))
            expect(commit.data["Workflow-State"]).to(equal("done"))

        with it("should attach a project with ticket states"):
            project = self.repo.attach_project("demo-org", 3)
            expect(len(project.states)).to(equal(3))
            expect(project.state_named("Backlog").name).to(equal("Backlog"))

        with it("should link the project to the repository"):
            self.repo.attach_project("demo-org", 3)
            expect(self.repo._project_links).to(
                equal([("demo-org", 3, "demo-org/demo-repo")])
            )

        with it("should create tickets and track project state"):
            project = self.repo.attach_project("demo-org", 3)
            ticket = self.repo.create_ticket("Workflow package", "forward requirements")
            ticket.set_status("Backlog")
            expect(ticket.state.name).to(equal("Backlog"))
            expect(self.repo._ticket_project_state[ticket.number]).to(equal("Backlog"))
            ticket.set_status("In Progress")
            expect(self.repo._ticket_project_state[ticket.number]).to(equal("In Progress"))

        # (S) Repo --> Merge Branch
        with it("should merge branches through Branch objects"):
            self.repo.branch_named("session/demo").checkout()
            self.repo.commit(["a.py"], "work")
            main = self.repo.branch_named("main")
            merge = main.merge(self.repo.branch_named("session/demo"), message="finish demo")
            expect(merge.message).to(contain("finish demo"))
            expect(self.repo.current_branch).to(equal("main"))


with description("a Repo ticket lifecycle"):
    with before.each:
        self.repo = Repo.memory("/tmp/demo-clone")
        self.project = self.repo.attach_project("demo-org", 3)
        self.ticket = self.repo.create_ticket("Demo", "body")
        self.ticket.set_status("Backlog")

    with it("should close tickets"):
        self.ticket.close()
        expect(self.ticket.closed).to(be_true)

    with it("should refuse closing unknown tickets"):
        missing = Ticket(number=999, title="", body="", _repo=self.repo)
        expect(lambda: missing.close()).to(raise_error(TicketNotFoundError))

    with it("should put a theme label and project Theme on the ticket"):
        expect(issue_theme_label("CLI agent")).to(equal("theme:cli-agent"))
        expect(issue_theme_label("theme:cli-agent")).to(equal("theme:cli-agent"))
        self.ticket.add_theme("CLI agent")
        expect(self.ticket.labels).to(equal(["theme:cli-agent"]))
        expect(self.repo._ticket_project_theme[self.ticket.number]).to(
            equal("cli-agent")
        )

    with it("should apply an issue type name on the ticket"):
        self.ticket.write_type("Defect")
        expect(self.ticket.issue_type).to(equal("Defect"))

    with it("should create missing organization issue types"):
        expect(self.repo.list_issue_types()).to(equal([]))
        self.repo.ensure_issue_type(
            "Defect", description="An unexpected problem or behavior", color="red"
        )
        expect([item["name"] for item in self.repo.list_issue_types()]).to(
            equal(["Defect"])
        )
        self.repo.ensure_issue_type("Defect")
        expect(len(self.repo.list_issue_types())).to(equal(1))


with description("GitHub project status names"):
    with it("should append the project-scope refresh hint to gh auth errors"):
        original = GhConnectError(
            "gh project field-list failed: missing required scopes [read:project]"
        )
        project = Repo.memory("/tmp/demo-clone").attach_project("demo-org", 3)
        expect(str(project._project_scope_error(original))).to(contain(GH_PROJECT_SCOPES_HINT))

    with it("should refresh Project.states from the live Status field"):
        repo = Repo.memory("/tmp/demo-clone")
        project = repo.attach_project("demo-org", 3)

        def fake_gh(*args: str, stdin: str | None = None) -> str:
            if len(args) >= 2 and args[1] == "field-list":
                return (
                    '{"fields":[{"name":"Status","options":'
                    '[{"name":"Todo"},{"name":"In Progress"},{"name":"Review"},{"name":"Done"}]}]}'
                )
            return ""

        repo.run_gh = fake_gh  # type: ignore[method-assign]
        repo._memory = False
        names = project.refresh_states()
        expect(names).to(equal(["Todo", "In Progress", "Review", "Done"]))
        expect([state.name for state in project.states]).to(
            equal(["Todo", "In Progress", "Review", "Done"])
        )
        repo._memory = True

    with it("should map Backlog to Todo when the board has Todo"):
        expect(
            Project.github_status_option(
                "Backlog", ["Todo", "In Progress", "Done"]
            )
        ).to(equal("Todo"))

    with it("should keep Backlog when the board has Backlog"):
        expect(
            Project.github_status_option(
                "Backlog", ["Backlog", "In Progress", "Done"]
            )
        ).to(equal("Backlog"))

    with it("should map In Progress to In progress when the board uses lowercase"):
        expect(
            Project.github_status_option(
                "In Progress", ["Backlog", "In progress", "Done"]
            )
        ).to(equal("In progress"))

    with it("should send Todo to gh for Backlog while memory still records Backlog"):
        repo = Repo.memory("/tmp/demo-clone")
        repo.attach_project("demo-org", 3)
        ticket = repo.create_ticket("Demo", "body")
        calls: list[tuple[str, ...]] = []

        def fake_gh(*args: str, stdin: str | None = None) -> str:
            calls.append(args)
            if len(args) >= 2 and args[1] == "field-list":
                return (
                    '{"fields":[{"name":"Status","id":"FIELD_STATUS","options":'
                    '[{"id":"OPT_TODO","name":"Todo"},'
                    '{"id":"OPT_IP","name":"In Progress"},'
                    '{"id":"OPT_DONE","name":"Done"}]}]}'
                )
            if len(args) >= 2 and args[1] == "view":
                return '{"id":"PROJ_3"}'
            if len(args) >= 2 and args[1] == "item-add":
                return '{"id":"PVTI_1"}'
            return ""

        repo.run_gh = fake_gh  # type: ignore[method-assign]
        repo._memory = False
        ticket.set_status("Backlog")
        option_ids = []
        for call in calls:
            if "--single-select-option-id" in call:
                option_ids.append(call[call.index("--single-select-option-id") + 1])
        expect(option_ids).to(equal(["OPT_TODO"]))
        repo._memory = True
        ticket.set_status("Backlog")
        expect(repo._ticket_project_state[ticket.number]).to(equal("Backlog"))
        expect(ticket.state.name).to(equal("Backlog"))


with description("GitHub project theme names"):
    with it("should match Theme options case-insensitively"):
        expect(
            Project.github_theme_option(
                "CLI agent", ["cli-agent", "workspace"]
            )
        ).to(equal("cli-agent"))

    with it("should send cli-agent to gh while memory still records the slug"):
        repo = Repo.memory("/tmp/demo-clone")
        repo.attach_project("demo-org", 3)
        ticket = repo.create_ticket("Demo", "body")
        calls: list[tuple[str, ...]] = []

        def fake_gh(*args: str, stdin: str | None = None) -> str:
            calls.append(args)
            if len(args) >= 2 and args[1] == "field-list":
                return (
                    '{"fields":[{"name":"Theme","id":"FIELD_THEME","options":'
                    '[{"id":"OPT_CLI","name":"cli-agent"},'
                    '{"id":"OPT_WS","name":"workspace"}]}]}'
                )
            if len(args) >= 2 and args[1] == "view":
                return '{"id":"PROJ_3"}'
            if len(args) >= 2 and args[1] == "item-add":
                return '{"id":"PVTI_1"}'
            return ""

        repo.run_gh = fake_gh  # type: ignore[method-assign]
        repo._memory = False
        ticket.add_theme("CLI agent")
        theme_option_ids = []
        for call in calls:
            if "--single-select-option-id" in call:
                theme_option_ids.append(
                    call[call.index("--single-select-option-id") + 1]
                )
        expect(theme_option_ids).to(equal(["OPT_CLI"]))
        repo._memory = True
        ticket.add_theme("CLI agent")
        expect(repo._ticket_project_theme[ticket.number]).to(equal("cli-agent"))


# (E) Open Work Session
# (E) Work With Repo Worktree
with description("a Repo worktree"):
    with context("opened in memory"):
        with before.each:
            self.repo = Repo.memory("/tmp/demo-clone")

        # (S) Repo --> List Worktree
        with it("should list the primary checkout"):
            trees = self.repo.list_worktrees()
            expect(len(trees)).to(equal(1))
            expect(trees[0].branch).to(equal("main"))

        # (S) Repo --> Open Worktree
        with it("should add a worktree for a session branch"):
            path = self.repo.add_worktree("/tmp/wt-demo", "session/demo")
            expect(path).to(equal(Path("/tmp/wt-demo")))
            found = self.repo.worktree_for("session/demo")
            expect(found is not None).to(be_true)
            expect(found.branch).to(equal("session/demo"))

        # (S) Repo --> Reuse Worktree
        with it("should reuse an existing worktree for the same branch"):
            first = self.repo.add_worktree("/tmp/wt-demo", "session/demo")
            second = self.repo.add_worktree("/tmp/wt-demo-2", "session/demo")
            expect(second).to(equal(first))
            expect(len(self.repo.list_worktrees())).to(equal(2))

        # (S) Repo --> Remove Worktree
        with it("should remove a worktree"):
            path = self.repo.add_worktree("/tmp/wt-demo", "session/demo")
            self.repo.remove_worktree(path)
            expect(self.repo.worktree_for("session/demo")).to(equal(None))

        # (S) Repo --> Remove Worktree
        with it("should run Windows takeown icacls and Remove-Item as last resort"):
            import os
            from unittest.mock import patch

            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "locked-wt"
                target.mkdir()
                calls: list[tuple[str, ...]] = []

                def fake_run(args, **kwargs):
                    calls.append(tuple(args))
                    return subprocess.CompletedProcess(args, 0)

                with patch("space.repo.repo.os.name", "nt"):
                    with patch.dict(os.environ, {"USERNAME": "tester"}):
                        with patch("space.repo.repo.shutil.rmtree"):
                            with patch("space.repo.repo.subprocess.run", side_effect=fake_run):
                                self.repo._force_remove_directory_windows(target)
                expect(calls[0][0]).to(equal("takeown"))
                expect(calls[1][0]).to(equal("icacls"))
                expect(any("Remove-Item" in " ".join(c) for c in calls)).to(be_true)

        # (S) Repo --> Fetch Worktree
        with it("should fetch and pull in the current tree"):
            self.repo.fetch_pull()
            expect(self.repo._fetches).to(equal(["origin"]))
            expect(self.repo._pulls).to(equal(["main"]))

        # (E) Work With Repo Branch
        # (S) Repo --> Merge Branch
        with it("should merge another branch into the current branch"):
            sha = self.repo.merge_from("session/demo", message="merge with main")
            expect(sha).to(equal("merge-session/demo-into-main"))
            expect(self.repo.current_branch).to(equal("main"))

        # (S) Repo --> Push Branch
        with it("should push the current head to another branch name"):
            self.repo.push_to("main")
            expect(self.repo.pushes).to(equal(["main"]))


with description("an annotated tag"):
    with before.each:
        self.repo = Repo.memory("/tmp/demo-clone")
        self.repo.branch_named("session/demo").checkout()

    with context("that has been written on a commit"):
        with it("should return that message when read by name"):
            self.repo.write_annotated_tag("chat/session/demo", "C:/chats/one.jsonl")
            expect(self.repo.read_annotated_tag("chat/session/demo")).to(
                equal("C:/chats/one.jsonl")
            )

    with context("that has been written again under the same name"):
        with it("should keep the later message"):
            self.repo.write_annotated_tag("chat/session/demo", "first")
            self.repo.write_annotated_tag("chat/session/demo", "first\nsecond")
            expect(self.repo.read_annotated_tag("chat/session/demo")).to(
                equal("first\nsecond")
            )

    with context("that shares a name prefix with other annotated tags"):
        with it("should list every message for that prefix"):
            self.repo.write_annotated_tag("chat/session/a", "a.jsonl")
            self.repo.write_annotated_tag("chat/session/b", "b.jsonl")
            self.repo.write_annotated_tag("cli-agent/session/a", "other")
            expect(self.repo.list_annotated_tags("chat/session/")).to(
                equal(
                    {
                        "chat/session/a": "a.jsonl",
                        "chat/session/b": "b.jsonl",
                    }
                )
            )


with description("Repo dirty detection"):
    with it("should ignore events.log so session close is not blocked by the trail"):
        from space.repo.repo import Repo

        tmp = Path(tempfile.mkdtemp(prefix="git_events_log_"))
        Repo.git(tmp, "init")
        Repo.git(tmp, "config", "user.email", "test@example.com")
        Repo.git(tmp, "config", "user.name", "test")
        Repo.git(tmp, "commit", "--allow-empty", "-m", "init")
        log = tmp / ".context" / "sessions" / "demo" / "logs" / "events.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("trail\n", encoding="utf-8")
        Repo.git(tmp, "add", "-f", str(log))
        Repo.git(tmp, "commit", "-m", "track log")
        log.write_text("more trail\n", encoding="utf-8")
        repo = Repo(tmp)
        expect(repo.is_dirty()).to(equal(False))
        (tmp / "real.txt").write_text("keep", encoding="utf-8")
        expect(repo.is_dirty()).to(equal(True))


with description("Repo stash"):
    with it("should clear every stash entry"):
        from space.repo.repo import Repo

        repo = Repo.memory("/tmp/stash-clear")
        repo._stash = True
        expect(repo.has_stash()).to(equal(True))
        repo.clear_stash()
        expect(repo.has_stash()).to(equal(False))


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
            expect(WorkState(self.clone).branch).to(equal("feature/a"))

        with it("should switch to the saved branch when no name is given"):
            WorkState(self.clone).branch = "feature/saved"
            self.toolset.switch_branch()
            expect(_git(self.clone, "branch", "--show-current")).to(equal("feature/saved"))

        with it("should refuse to switch with no name and no saved branch"):
            expect(lambda: self.toolset.switch_branch()).to(raise_error(BranchNameRequiredError))

        with context("with uncommitted work on main"):
            with before.each:
                (self.clone / "main-work.txt").write_text("main work\n", encoding="utf-8")
                self.toolset.switch_branch("feature/a")

            with it("should commit that work on main before switching away"):
                expect(_git(self.clone, "ls-tree", "--name-only", "main")).to(contain("main-work.txt"))

            with it("should not push main to origin"):
                expect(_git(self.origin, "ls-tree", "--name-only", "main")).not_to(contain("main-work.txt"))

        with context("with uncommitted work on a feature branch"):
            with before.each:
                self.toolset.switch_branch("feature/a")
                (self.clone / "work.txt").write_text("feature work\n", encoding="utf-8")

            with it("should push that work to origin before switching away"):
                self.toolset.switch_branch("feature/b")
                expect(_git(self.origin, "ls-tree", "--name-only", "feature/a")).to(contain("work.txt"))

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
                expect(WorkState(self.clone).branch).to(equal("main"))

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

        with context("named by repo_path from a toolset started in another clone"):
            with before.each:
                (Path(self.tmp.name) / "host").mkdir()
                self.host_origin, self.host = _clone_with_origin(Path(self.tmp.name) / "host")
                self.toolset = Repo(self.host)
                self.toolset.switch_branch("feature/a", repo_path=str(self.clone))

            with it("should switch the named clone"):
                expect(_git(self.clone, "branch", "--show-current")).to(equal("feature/a"))

            with it("should leave the toolset's own clone on main"):
                expect(_git(self.host, "branch", "--show-current")).to(equal("main"))

            with it("should save the branch in the named clone's .sessions/session.json"):
                expect(WorkState(self.clone).branch).to(equal("feature/a"))

            with it("should commit and push in the named clone"):
                (self.clone / "work.txt").write_text("feature work\n", encoding="utf-8")
                self.toolset.push_commit("work", repo_path=str(self.clone))
                expect(_git(self.origin, "ls-tree", "--name-only", "feature/a")).to(contain("work.txt"))

            with it("should close the branch in the named clone"):
                self.toolset.close_branch(repo_path=str(self.clone))
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
                tree = Path(WorkState(self.clone).worktree)
                expect(_git(tree, "branch", "--show-current")).to(equal("feature/a"))

            with it("should move the clone back to main"):
                self.toolset.switch_worktree()
                expect(_git(self.clone, "branch", "--show-current")).to(equal("main"))

            with context("that has an open worktree with uncommitted work"):
                with before.each:
                    self.toolset.switch_worktree()
                    self.tree = Path(WorkState(self.clone).worktree)
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
                    expect(WorkState(self.clone).worktree).to(equal(""))

                with it("should keep the branch open when closed"):
                    self.toolset.close_worktree()
                    expect(WorkState(self.clone).branch).to(equal("feature/a"))

                with it("should refuse to close the branch while its worktree is open"):
                    expect(lambda: self.toolset.close_branch()).to(raise_error(BranchInWorktreeError))

        with it("should refuse to close a worktree when none is open"):
            expect(lambda: self.toolset.close_worktree()).to(raise_error(NoOpenWorktreeError))

        with context("named by repo_path from a toolset started in another clone"):
            with before.each:
                (Path(self.tmp.name) / "host").mkdir()
                self.host_origin, self.host = _clone_with_origin(Path(self.tmp.name) / "host")
                self.toolset = Repo(self.host)
                self.toolset.switch_worktree("feature/a", repo_path=str(self.clone))
                self.tree = Path(WorkState(self.clone).worktree)

            with it("should open the worktree beside the named clone"):
                expect(_git(self.tree, "branch", "--show-current")).to(equal("feature/a"))

            with it("should remove the named clone's worktree when closed"):
                self.toolset.close_worktree(repo_path=str(self.clone))
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
            expect(lambda: Repo._run_git_process(launcher, 1)).to(raise_error(subprocess.TimeoutExpired))
            expect(time.monotonic() - started).to(be_below(15))


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
            toolset = AgentToolSet.instantiate("space.repo.repo:Repo")
            commit = toolset.push_commit("push: checkpoint")
            expect(commit.sha).not_to(equal(""))
            expect(commit.subject).to(equal("push: checkpoint"))

        with it("should publish push_commit on MCP and keep /push as instructions only"):
            from harness.agent_tools.agent_tools import InstallDestination

            toolset = AgentToolSet.instantiate("space.repo.repo:Repo")
            mcp_names = [tool.name for tool in toolset.tools_for(InstallDestination.MCP)]
            expect("push_commit" in mcp_names).to(equal(True))
            expect("push" in mcp_names).to(equal(False))
            expect("push_commit" in toolset.instructions["push"].description).to(equal(True))
