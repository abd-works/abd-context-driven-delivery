# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for context_tools/actions/workflow/workflow.py."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("workflow", None)

from expects import be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from git import TicketNotFoundError
from git.git import Commit, Repo, Ticket
from workflow.work_ticket import WorkTicket
from workflow.workflow import Workflow


def _seed_issue(repo: Repo, *, number: int = 87, title: str, body: str) -> Ticket:
    ticket = Ticket(
        number=number,
        title=title,
        body=body,
        url=f"https://github.com/demo-org/demo-repo/issues/{number}",
    )
    repo._tickets[number] = ticket
    return ticket


def _workflow_fixture(prefix: str) -> tuple[Path, Repo]:
    tmp = Path(tempfile.mkdtemp(prefix=prefix))
    (tmp / ".git").mkdir()
    config_dir = tmp / ".context"
    config_dir.mkdir()
    (config_dir / "workflow.yaml").write_text(
        "project_owner: demo-org\nproject_number: 3\n",
        encoding="utf-8",
    )
    return tmp, Repo.memory(tmp)


with description("Workflow helpers"):
    with it("should kebab-case focus labels"):
        w = Workflow()
        expect(w._kebab("Git Notes On Deploy")).to(equal("git-notes-on-deploy"))

    with it("should kebab-case issue titles for session slugs"):
        w = Workflow()
        expect(w._kebab("Add workflow package #87")).to(equal("add-workflow-package-87"))

    with it("should parse github issue references"):
        expect(Ticket.parse_number("87")).to(equal(87))
        expect(Ticket.parse_number("#87")).to(equal(87))
        expect(Ticket.parse_number("demo-org/demo-repo#87")).to(equal(87))
        expect(Ticket.parse_number("https://github.com/demo-org/demo-repo/issues/87")).to(
            equal(87)
        )

    with it("should format github issue trailers"):
        expect(Ticket.github_ref("demo-org", "demo-repo", 87)).to(
            equal("demo-org/demo-repo#87")
        )

    with it("should format commit messages with workflow trailers"):
        message = Commit.format(
            "start workflow-package-87",
            {
                "GitHub-Issue": "demo-org/demo-repo#87",
                "Workflow-State": "specification",
            },
        )
        expect(message).to(contain("GitHub-Issue: demo-org/demo-repo#87"))
        expect(message).to(contain("Workflow-State: specification"))

    with it("should derive session names from issue titles"):
        w = Workflow()
        expect(w.session_name_for_issue("Add workflow package", 87)).to(
            equal("add-workflow-package-87")
        )


with description("Workflow manifest"):
    with it("should expose backlog start finish as tools"):
        sig = Workflow.manifest.signature
        expect(sig["backlog"]["kind"]).to(equal("tool"))
        expect(sig["start"]["kind"]).to(equal("tool"))
        expect(sig["finish"]["kind"]).to(equal("tool"))
        expect(sig["capture_backlog"]["kind"]).to(equal("tool"))
        exposed = sorted(
            name
            for name, entry in sig.items()
            if isinstance(entry, dict) and entry.get("kind") == "tool"
        )
        expect(exposed).to(equal(["backlog", "capture_backlog", "finish", "start"]))


with description("a Workflow"):
    with context("that is asked to start an item"):
        with context("with a github issue reference given"):
            with context("with the issue not found"):
                with before.each:
                    self.tmp, self.repo = _workflow_fixture("wf-start-miss-")
                    self.workflow = Workflow(workspace=str(self.tmp), repo=self.repo)

                with it("should report that the ticket was not found"):
                    expect(lambda: self.workflow.start("87", workspace=str(self.tmp))).to(
                        raise_error(TicketNotFoundError)
                    )

                with it("should not open a work session"):
                    try:
                        self.workflow.start("87", workspace=str(self.tmp))
                    except TicketNotFoundError:
                        pass
                    ws = self.workflow.workspace_tool(path=str(self.tmp))
                    expect(ws.current_work_session is None).to(be_true)

    with context("that is asked to finish work"):
        with context("with no open work session"):
            with before.each:
                self.tmp, self.repo = _workflow_fixture("wf-finish-none-")
                self.workflow = Workflow(workspace=str(self.tmp), repo=self.repo)

            with it("should report that no work session is open"):
                expect(
                    lambda: self.workflow.finish(workspace=str(self.tmp))
                ).to(raise_error(RuntimeError, "no open work session"))


def _noop_launch(workflow, workspace, meta_path, focus):
    return {"launched": "yes", "staging": meta_path, "report": ""}


with description("a Workflow backlog path"):
    with context("with a memory Repo"):
        with before.each:
            self.tmp, self.repo = _workflow_fixture("wf-backlog-")
            self.workflow = Workflow(workspace=str(self.tmp), repo=self.repo)

        with it("should launch a sub-agent and return launched status"):
            with patch.object(Workflow, "_launch_backlog_agent", _noop_launch):
                result = self.workflow.backlog(
                    focus="Workflow package",
                    context="theme by package",
                    workspace=str(self.tmp),
                )
            expect(result["launched"]).to(equal("yes"))
            expect("staging" in result).to(be_true)

        with it("should write a staging metadata file with focus and workspace"):
            with patch.object(Workflow, "_launch_backlog_agent", _noop_launch):
                self.workflow.backlog(
                    focus="Workflow package",
                    context="need Todo mapping",
                    workspace=str(self.tmp),
                )
            staging_files = list((self.tmp / ".context").glob("backlog-*.json"))
            expect(len(staging_files)).to(equal(1))
            meta = json.loads(staging_files[0].read_text(encoding="utf-8"))
            expect(meta["focus"]).to(equal("Workflow package"))
            expect("workspace" in meta).to(be_true)

        with it("should write the handoff body and Turn Context into the staging body file"):
            with patch.object(Workflow, "_launch_backlog_agent", _noop_launch):
                self.workflow.backlog(
                    focus="Workflow package",
                    context="need Todo mapping",
                    workspace=str(self.tmp),
                )
            body_files = list((self.tmp / ".context").glob("backlog-*.md"))
            expect(len(body_files)).to(equal(1))
            body = body_files[0].read_text(encoding="utf-8")
            expect(body).to(contain("**Focus:** Workflow package"))
            expect(body).to(contain("## Turn Context"))

        with it("should include theme in staging metadata when given"):
            with patch.object(Workflow, "_launch_backlog_agent", _noop_launch):
                self.workflow.backlog(
                    focus="Queue for CLI agent",
                    context="same agent or another",
                    workspace=str(self.tmp),
                    theme="cli-agent",
                )
            staging_files = list((self.tmp / ".context").glob("backlog-*.json"))
            meta = json.loads(staging_files[0].read_text(encoding="utf-8"))
            expect(meta["theme"]).to(equal("cli-agent"))

        with it("should include category in staging metadata when given"):
            with patch.object(Workflow, "_launch_backlog_agent", _noop_launch):
                self.workflow.backlog(
                    focus="Sketch grill skips a turn",
                    workspace=str(self.tmp),
                    category="defect",
                )
            staging_files = list((self.tmp / ".context").glob("backlog-*.json"))
            meta = json.loads(staging_files[0].read_text(encoding="utf-8"))
            expect(meta["category"]).to(equal("defect"))

        with it("should create a github issue with the handoff body via capture_backlog"):
            created = self.workflow.capture_backlog(
                focus="Workflow package",
                body="forward requirements",
                workspace=str(self.tmp),
            )
            expect(created["number"]).to(equal(1))
            expect(created["body"]).to(equal("forward requirements"))
            expect(self.repo._ticket_project_state[1]).to(equal("Backlog"))

        with it("should put handoff file contents in the issue body not a path"):
            handoff = self.tmp / "handoff.md"
            handoff.write_text("# Handoff\n\nResume here.\n", encoding="utf-8")
            created = self.workflow.capture_backlog(
                focus="Workflow package",
                body=str(handoff),
                workspace=str(self.tmp),
            )
            expect(created["body"]).to(contain("# Handoff"))
            expect(created["body"]).to(contain("Resume here."))
            expect(created["body"]).not_to(contain(str(handoff)))

        with it("should not open a work session"):
            self.workflow.capture_backlog(
                focus="Workflow package",
                body="forward requirements",
                workspace=str(self.tmp),
            )
            ws = self.workflow.workspace_tool(path=str(self.tmp))
            expect(ws.current_work_session is None).to(be_true)

        with it("should infer type and theme for capture_backlog when the user does not override"):
            created = self.workflow.capture_backlog(
                focus="Sketch is stuffing prior grill answers",
                body="context: mistakes after the sketch refactor",
                workspace=str(self.tmp),
                infer_from="Sketch is stuffing prior grill answers\nmistakes after the sketch refactor",
            )
            expect(created["type"]).to(equal("Defect"))
            expect(created["theme"]).to(equal("theme:sketch"))
            expect([item["name"] for item in self.repo.list_issue_types()]).to(
                equal(["Defect", "Small change", "Refactor", "Feature"])
            )

        with it("should keep user type and theme for capture_backlog instead of inferred ones"):
            created = self.workflow.capture_backlog(
                focus="Sketch is stuffing prior grill answers",
                body="details",
                workspace=str(self.tmp),
                theme="workflow",
                category="feature",
            )
            expect(created["type"]).to(equal("Feature"))
            expect(created["theme"]).to(equal("theme:workflow"))


with description("a Workflow backlog helper"):
    with context("_format_turn_context"):
        with it("should render a Turn Context section with branch and commit"):
            w = Workflow()
            result = w._format_turn_context(
                {"branch": "main", "head_sha": "abc123def456", "log": "abc123 finish"},
                transcript_path="",
            )
            expect(result).to(contain("## Turn Context"))
            expect(result).to(contain("main"))
            expect(result).to(contain("abc123def456"))

        with it("should include transcript path when given"):
            w = Workflow()
            result = w._format_turn_context(
                {"branch": "main", "head_sha": "abc", "log": ""},
                transcript_path="/path/to/t.jsonl",
            )
            expect(result).to(contain("/path/to/t.jsonl"))

        with it("should omit empty fields"):
            w = Workflow()
            result = w._format_turn_context({"branch": "", "head_sha": "", "log": ""}, "")
            expect(result).to(contain("## Turn Context"))
            expect("Branch:" in result).to(equal(False))

    with context("_backlog_agent_task"):
        with it("should build a task prompt that names the metadata file and focus"):
            w = Workflow()
            task = w._backlog_agent_task("/path/meta.json", "Fix the scanner bug")
            expect(task).to(contain("/path/meta.json"))
            expect(task).to(contain("Fix the scanner bug"))
            expect(task).to(contain("capture_backlog"))

    with context("_write_backlog_staging"):
        with it("should write body and metadata files under .context/"):
            tmp = Path(tempfile.mkdtemp(prefix="wf-stage-"))
            w = Workflow()
            meta_path = w._write_backlog_staging(
                workspace=str(tmp),
                focus="Fix the scanner",
                body="## Body\n\nDetails.\n",
                metadata={"focus": "Fix the scanner", "workspace": str(tmp)},
            )
            expect(meta_path.is_file()).to(be_true)
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            expect(meta["focus"]).to(equal("Fix the scanner"))
            body_path = Path(meta["body_path"])
            expect(body_path.is_file()).to(be_true)
            expect(body_path.read_text(encoding="utf-8")).to(contain("## Body"))


with description("a WorkTicket"):
    with before.each:
        self.tmp, self.repo = _workflow_fixture("wf-ticket-")
        self.workflow = Workflow(workspace=str(self.tmp), repo=self.repo)
        self.workflow._ensure_project(self.repo, self.tmp)

    with it("should be constructed with the workflow repo"):
        work = WorkTicket(self.repo, self.workflow)
        expect(work.repo).to(equal(self.repo))
        expect(work.workflow).to(equal(self.workflow))

    with it("should expose type theme and a getter-only state"):
        work = WorkTicket(self.repo, self.workflow).create(
            "Sketch grill skips a turn",
            "mistakes",
            type="defect",
            theme="sketch",
        )
        expect(work.type).to(equal("Defect"))
        expect(work.theme).to(equal("sketch"))
        expect(work.state).to(equal("Backlog"))
        expect(lambda: setattr(work, "state", "Done")).to(raise_error(AttributeError))

    with it("should put missing types on the organization the repo is attached to"):
        expect(self.repo.list_issue_types()).to(equal([]))
        added = WorkTicket(self.repo, self.workflow).ensure_types()
        expect(added).to(equal(["Defect", "Small change", "Refactor", "Feature"]))
        expect([item["name"] for item in self.repo.list_issue_types()]).to(
            equal(["Defect", "Small change", "Refactor", "Feature"])
        )
        expect(WorkTicket(self.repo, self.workflow).ensure_types()).to(equal([]))

    with it("should map defect small change and feature to org types"):
        expect(WorkTicket.resolve_type("defect")).to(equal("Defect"))
        expect(WorkTicket.resolve_type("small change")).to(equal("Small change"))
        expect(WorkTicket.resolve_type("Feature")).to(equal("Feature"))
        expect(WorkTicket.resolve_type("refactor")).to(equal("Refactor"))
        expect(lambda: WorkTicket.resolve_type("epic")).to(raise_error(ValueError))

    with it("should infer type and theme from the request"):
        expect(WorkTicket.infer_type("list the mistakes")).to(equal("Defect"))
        expect(WorkTicket.infer_type("Rename Context Tool")).to(equal("Refactor"))
        expect(
            WorkTicket.infer_type("move transform to live on the base")
        ).to(equal("Refactor"))
        expect(WorkTicket.infer_type("Add ability to queue")).to(equal("Small change"))
        expect(
            WorkTicket.infer_type("small change to an existing feature")
        ).to(equal("Small change"))
        expect(
            WorkTicket.infer_type("creating the CLI agent as a new module")
        ).to(equal("Feature"))
        expect(WorkTicket.TYPE_DEFINITIONS["Small change"]).to(
            contain("existing feature")
        )
        expect(WorkTicket.TYPE_DEFINITIONS["Feature"]).to(contain("very large"))
        expect(WorkTicket.TYPE_GUIDE).to(contain("CLI agent"))
        expect(WorkTicket.infer_theme("Queue for CLI agent")).to(equal("cli-agent"))
        expect(WorkTicket.infer_theme("sketch is really rough")).to(equal("sketch"))


with description("a Workflow start path"):
    with context("with an issue available"):
        with before.each:
            self.tmp, self.repo = _workflow_fixture("wf-start-")
            _seed_issue(
                self.repo,
                title="Add workflow package",
                body="forward requirements from issue",
            )
            self.workflow = Workflow(workspace=str(self.tmp), repo=self.repo)

        with it("should open a work session named for that ticket"):
            opened = self.workflow.open_ticket_session(
                "87",
                instructions="resume from issue",
                workspace=str(self.tmp),
            )
            expect(opened["session_name"]).to(equal("add-workflow-package-87"))
            ws = self.workflow.workspace_tool(path=str(self.tmp))
            expect(ws.current_work_session.name).to(equal("add-workflow-package-87"))

        with it("should set the branch to the session branch for that work session"):
            self.workflow.open_ticket_session("87", workspace=str(self.tmp))
            ws = self.workflow.workspace_tool(path=str(self.tmp))
            expect(ws.current_work_session.session_branch).to(
                equal("session/add-workflow-package-87")
            )

        with it("should open a turn for the action run"):
            self.workflow.open_ticket_session("87", workspace=str(self.tmp))
            ws = self.workflow.workspace_tool(path=str(self.tmp))
            expect(ws.current_work_session.open_turn is not None).to(be_true)

        with it("should move the issue to In Progress on the project"):
            self.workflow.start("87", workspace=str(self.tmp))
            expect(self.repo._ticket_project_state[87]).to(equal("In Progress"))

        with it("should copy issue sections into the work session folder when needed"):
            path = self.workflow.copy_issue_body_to_session(
                "87",
                "add-workflow-package-87",
                workspace=str(self.tmp),
            )
            expect(Path(path).read_text(encoding="utf-8")).to(
                equal("forward requirements from issue")
            )


with description("a Workflow finish path"):
    with context("with an open work session from start"):
        with before.each:
            self.tmp, self.repo = _workflow_fixture("wf-finish-")
            _seed_issue(
                self.repo,
                title="Add workflow package",
                body="forward requirements",
            )
            self.workflow = Workflow(workspace=str(self.tmp), repo=self.repo)
            self.workflow.open_ticket_session("87", workspace=str(self.tmp))
            self.git = self.workflow.workspace_tool(path=str(self.tmp)).current_work_session.git
            self.git.create_branch("session/add-workflow-package-87")
            self.git.checkout_or_create("session/add-workflow-package-87")

        with it("should merge its session branch into main"):
            sha = self.workflow.merge_session_to_main(
                workspace=str(self.tmp),
                ticket="87",
                reviewed_by="human",
            )
            expect(self.git.current_branch).to(equal("main"))
            expect(sha).to(contain("merge-session/add-workflow-package-87-into-main"))

        with it("should carry github issue and workflow-state done trailers on the merge commit"):
            self.workflow.merge_session_to_main(
                workspace=str(self.tmp),
                ticket="87",
                reviewed_by="human",
            )
            _, message = self.git.commits[-1]
            expect(message).to(contain("GitHub-Issue: demo-org/demo-repo#87"))
            expect(message).to(contain("Workflow-State: done"))
            expect(message).to(contain("Reviewed-By: human"))

        with it("should close the github issue"):
            self.workflow.close_ticket("87", workspace=str(self.tmp))
            expect(87 in self.repo._closed_tickets).to(be_true)

        with it("should move the issue to Done on the project"):
            self.workflow.set_ticket_project_status(
                "87",
                "Done",
                workspace=str(self.tmp),
            )
            expect(self.repo._ticket_project_state[87]).to(equal("Done"))


with description("a Workflow finish tool"):
    with context("with a started session"):
        with before.each:
            self.tmp, self.repo = _workflow_fixture("wf-finish-tool-")
            _seed_issue(
                self.repo,
                title="Add workflow package",
                body="forward requirements",
            )
            self.workflow = Workflow(workspace=str(self.tmp), repo=self.repo)
            self.workflow.start("87", workspace=str(self.tmp))

        with it("should merge close and mark done"):
            result = self.workflow.finish(
                outcome="shipped",
                workspace=str(self.tmp),
                ticket="87",
                reviewed_by="human",
            )
            git = self.workflow.workspace_tool(path=str(self.tmp)).current_work_session.git
            expect(result["session_name"]).to(equal("add-workflow-package-87"))
            expect(git.current_branch).to(equal("main"))
            expect(87 in self.repo._closed_tickets).to(be_true)
            expect(self.repo._ticket_project_state[87]).to(equal("Done"))
