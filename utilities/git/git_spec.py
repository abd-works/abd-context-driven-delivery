# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for utilities/git/git.py."""

import sys
import subprocess
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from git import TicketNotFoundError
from git.git import (
    Branch,
    CliAgentBinding,
    Commit,
    GH_PROJECT_SCOPES_HINT,
    GhConnectError,
    Project,
    Repo,
    Ticket,
    TicketState,
    _gh_project_scope_error,
    issue_theme_label,
    resolve_github_status_option,
    resolve_github_theme_option,
)


with description("a Ticket"):
    with it("should parse github issue references"):
        expect(Ticket.parse_number("87")).to(equal(87))
        expect(Ticket.parse_number("#87")).to(equal(87))
        expect(Ticket.parse_number("demo-org/demo-repo#87")).to(equal(87))

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
            self.repo.branch_named("session/demo").assign_cli_agent(binding)
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
        self.ticket.set_type("Defect")
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
        expect(str(_gh_project_scope_error(original))).to(contain(GH_PROJECT_SCOPES_HINT))

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

        repo._gh = fake_gh  # type: ignore[method-assign]
        repo._memory = False
        names = project.refresh_states()
        expect(names).to(equal(["Todo", "In Progress", "Review", "Done"]))
        expect([state.name for state in project.states]).to(
            equal(["Todo", "In Progress", "Review", "Done"])
        )
        repo._memory = True

    with it("should map Backlog to Todo when the board has Todo"):
        expect(
            resolve_github_status_option(
                "Backlog", ["Todo", "In Progress", "Done"]
            )
        ).to(equal("Todo"))

    with it("should keep Backlog when the board has Backlog"):
        expect(
            resolve_github_status_option(
                "Backlog", ["Backlog", "In Progress", "Done"]
            )
        ).to(equal("Backlog"))

    with it("should map In Progress to In progress when the board uses lowercase"):
        expect(
            resolve_github_status_option(
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

        repo._gh = fake_gh  # type: ignore[method-assign]
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
            resolve_github_theme_option(
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

        repo._gh = fake_gh  # type: ignore[method-assign]
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


with description("a Repo worktree"):
    with context("opened in memory"):
        with before.each:
            self.repo = Repo.memory("/tmp/demo-clone")

        with it("should list the primary checkout"):
            trees = self.repo.list_worktrees()
            expect(len(trees)).to(equal(1))
            expect(trees[0].branch).to(equal("main"))

        with it("should add a worktree for a session branch"):
            path = self.repo.add_worktree("/tmp/wt-demo", "session/demo")
            expect(path).to(equal(Path("/tmp/wt-demo")))
            found = self.repo.worktree_for("session/demo")
            expect(found is not None).to(be_true)
            expect(found.branch).to(equal("session/demo"))

        with it("should reuse an existing worktree for the same branch"):
            first = self.repo.add_worktree("/tmp/wt-demo", "session/demo")
            second = self.repo.add_worktree("/tmp/wt-demo-2", "session/demo")
            expect(second).to(equal(first))
            expect(len(self.repo.list_worktrees())).to(equal(2))

        with it("should remove a worktree"):
            path = self.repo.add_worktree("/tmp/wt-demo", "session/demo")
            self.repo.remove_worktree(path)
            expect(self.repo.worktree_for("session/demo")).to(equal(None))

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

                with patch("git.git.os.name", "nt"):
                    with patch.dict(os.environ, {"USERNAME": "tester"}):
                        with patch("git.git.shutil.rmtree"):
                            with patch("git.git.subprocess.run", side_effect=fake_run):
                                Repo._force_remove_directory_windows(target)
                expect(calls[0][0]).to(equal("takeown"))
                expect(calls[1][0]).to(equal("icacls"))
                expect(any("Remove-Item" in " ".join(c) for c in calls)).to(be_true)

        with it("should fetch and pull in the current tree"):
            self.repo.fetch_pull()
            expect(self.repo._fetches).to(equal(["origin"]))
            expect(self.repo._pulls).to(equal(["main"]))

        with it("should merge another branch into the current branch"):
            sha = self.repo.merge_from("session/demo", message="merge with main")
            expect(sha).to(equal("merge-session/demo-into-main"))
            expect(self.repo.current_branch).to(equal("main"))

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
        from git.git import GitRepo, Repo

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
        repo = GitRepo(tmp)
        expect(repo.is_dirty()).to(equal(False))
        (tmp / "real.txt").write_text("keep", encoding="utf-8")
        expect(repo.is_dirty()).to(equal(True))


with description("Repo stash"):
    with it("should clear every stash entry"):
        from git.git import Repo

        repo = Repo.memory("/tmp/stash-clear")
        repo._stash = True
        expect(repo.has_stash()).to(equal(True))
        repo.clear_stash()
        expect(repo.has_stash()).to(equal(False))
