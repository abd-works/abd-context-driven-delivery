"""BDD spec for WorkspaceSession - kit prose + tools on BaseContextTool hosts."""

import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_none, be_true, equal, expect, raise_error
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
from primitives.instructions import Instruction
from tools.tool import Toolset, _ToolsetLoader, _discover_tools

_KIT_DIR = Path(__file__).resolve().parent
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_CHRONICLE_WITH_OUTPUT_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
)
_BASE_TOOLSET = "context_tools.base.base_context_tool:BaseContextTool"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().invoke_action(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    heading = name.replace("_", " ").replace("-", " ").title()
    return Instruction(
        f"# {heading}", _KIT_DIR, domain_slug="workspace_session"
    ).expand()


with description("WorkspaceSession kit prose"):
    with it("should resolve open from workspace_session.md section"):
        text = _section("open")
        expect(text.startswith("# Open")).to(be_true)
        expect("Session Guidance" in text or "session" in text.lower()).to(be_true)

    with it("should resolve session guidance from workspace_session.md section"):
        text = _section("session_guidance")
        expect("# Session Guidance" in text).to(be_true)
        expect("session.path" in text or "active.path" in text or "path" in text).to(be_true)
        expect("context-index.md" in text).to(be_true)


with description("WorkspaceSession on a BaseContextTool host"):
    with context("CarChronicle generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_CAR_CHRONICLE_TOOLSET
            )

        with it("should name open then eval begin, CDR tools, eval finish"):
            expect(self.response["tools"]).to(
                equal(
                    [
                        "open",
                        "begin_eval_turn",
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                        "finish_eval_turn",
                    ]
                )
            )

        with it("should resolve open instructions from workspace_session.md"):
            from workspace.workspace_session import Session

            tools = _discover_tools(self.host.workspace)
            expect(tools["open"].instructions.startswith("# Open")).to(be_true)
            expect("Session Guidance" in tools["open"].instructions).to(be_true)
            expect("# Session Guidance" in self.response["instructions"]).to(be_false)

        with it("should not expand session active resource on the host generate composer"):
            expect(
                f"Resource `active` = {self.host.active!r}."
                in self.response["instructions"]
            ).to(be_false)

        with it("should expand kit open instructions from workspace_session.md"):
            from workspace.workspace_session import Session

            tools = _discover_tools(self.host.workspace)
            expect(isinstance(self.host.workspace, Session)).to(be_true)
            expect(tools["open"].instructions.startswith("# Open")).to(be_true)
            expect(tools["close_session"].instructions.startswith("# Close Session")).to(
                be_true
            )

    with context("ChronicleWithOutput generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_CHRONICLE_WITH_OUTPUT_TOOLSET
            )

        with it("should keep open ahead of nested generate_output tools"):
            expect(self.response["tools"]).to(
                equal(
                    [
                        "open",
                        "begin_eval_turn",
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                        "add_epic",
                        "finish_eval_turn",
                    ]
                )
            )

    with context("BaseContextTool generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_BASE_TOOLSET
            )

        with it("should not inline session guidance on the composer"):
            expect("# Session Guidance" in self.response["instructions"]).to(be_false)


with description("a Session with a name and path"):
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="session_props_"))
        from workspace.workspace_session import Session
        from workspace.session_log import SessionLog
        SessionLog.set_instance(None)
        self.session = Session(path=str(self.tmp), name="my-sprint")

    with it("should expose folder under .context/sessions/{name}"):
        # Act / Assert
        expect(self.session.folder).to(
            equal(self.tmp / ".context" / "sessions" / "my-sprint")
        )

    with it("should expose log dir under folder/logs"):
        # Act / Assert
        expect(self.session.log).to(equal(self.session.folder / "logs"))

    with it("should expose session_md under folder/session.md"):
        # Act / Assert
        expect(self.session.session_md).to(equal(self.session.folder / "session.md"))

    with it("should return empty string for context_index before it is loaded"):
        # Act / Assert
        expect(self.session.context_index).to(equal(""))

    with it("should return a dict with all fields via to_dict"):
        # Arrange
        from workspace.workspace_session import Session
        s = Session(path=str(self.tmp), name="sprint-1", goal="ship it",
                    fidelities="behavior", contexts="bdd")
        # Act
        d = s.to_dict()
        # Assert
        expect(d["path"]).to(equal(str(self.tmp)))
        expect(d["name"]).to(equal("sprint-1"))
        expect(d["goal"]).to(equal("ship it"))
        expect(d["fidelities"]).to(equal("behavior"))
        expect(d["contexts"]).to(equal("bdd"))


with description("a Session without a name"):
    with it("should raise ValueError when folder is accessed"):
        from workspace.workspace_session import Session
        s = Session(path=".")
        # Act / Assert
        raised = False
        try:
            _ = s.folder
        except ValueError:
            raised = True
        expect(raised).to(be_true)


with description("a Session that is loaded"):
    with context("with no existing session.md"):
        with it("should return a Session with path and name set and no goal"):
            import tempfile
            from workspace.workspace_session import Session
            tmp = Path(tempfile.mkdtemp(prefix="session_load_"))
            # Act
            s = Session.load(str(tmp), "no-file")
            # Assert
            expect(s.path).to(equal(str(tmp)))
            expect(s.name).to(equal("no-file"))
            expect(s.goal).to(equal(""))

    with context("with an existing session.md"):
        with it("should return a Session with fields parsed from the file"):
            import tempfile
            from workspace.workspace_session import Session
            tmp = Path(tempfile.mkdtemp(prefix="session_load_existing_"))
            s = Session(path=str(tmp), name="loaded-sprint", goal="test goal",
                        fidelities="development")
            s.ensure_started()
            # Act
            loaded = Session.load(str(tmp), "loaded-sprint")
            # Assert
            expect(loaded.goal).to(equal("test goal"))
            expect(loaded.fidelities).to(equal("development"))


with description("a Session that is started"):
    with it("should create the session.md file at the sprint folder path"):
        import tempfile
        from workspace.workspace_session import Session
        tmp = Path(tempfile.mkdtemp(prefix="session_started_"))
        s = Session(path=str(tmp), name="start-test", goal="build feature")
        # Act
        md = s.ensure_started()
        # Assert
        expect(md.is_file()).to(be_true)
        content = md.read_text(encoding="utf-8")
        expect("build feature" in content).to(be_true)


with description("a Session that is started in a git working area"):
    with it("should create a branch named for this session"):
        import shutil
        import tempfile
        from workspace.workspace_repo import WorkspaceRepo, _git, find_git_root
        from workspace.workspace_session import Session

        tmp = Path(tempfile.mkdtemp(prefix="session_git_started_"))
        _git(tmp, "init")
        _git(tmp, "config", "user.email", "test@example.com")
        _git(tmp, "config", "user.name", "test")
        _git(tmp, "commit", "--allow-empty", "-m", "init")
        session = Session(path=str(tmp), name="sprint")
        session.ensure_started()
        root = find_git_root(tmp)
        expect(root).to(equal(tmp.resolve()))
        expect(WorkspaceRepo(tmp).current_branch()).to(equal("session/sprint"))
        shutil.rmtree(tmp, ignore_errors=True)

    with context("that is started again while already on the session branch"):
        with it("should stay on that branch when the tree is dirty"):
            import shutil
            import tempfile
            from workspace.workspace_repo import WorkspaceRepo, _git
            from workspace.workspace_session import Session

            tmp = Path(tempfile.mkdtemp(prefix="session_git_already_on_"))
            _git(tmp, "init")
            _git(tmp, "config", "user.email", "test@example.com")
            _git(tmp, "config", "user.name", "test")
            _git(tmp, "commit", "--allow-empty", "-m", "init")
            session = Session(path=str(tmp), name="sprint")
            session.ensure_started()
            (tmp / "wip.txt").write_text("in progress", encoding="utf-8")
            session.ensure_started()
            expect(WorkspaceRepo(tmp).current_branch()).to(equal("session/sprint"))
            shutil.rmtree(tmp, ignore_errors=True)

    with context("that is an existing session whose branch we are not on"):
        with it("should not switch when the tree is dirty"):
            import shutil
            import tempfile
            from workspace.workspace_repo import (
                DirtyBranchSwitchError,
                WorkspaceRepo,
                _git,
            )
            from workspace.workspace_session import Session

            tmp = Path(tempfile.mkdtemp(prefix="session_git_resume_dirty_"))
            _git(tmp, "init")
            _git(tmp, "config", "user.email", "test@example.com")
            _git(tmp, "config", "user.name", "test")
            _git(tmp, "commit", "--allow-empty", "-m", "init")
            started_on = WorkspaceRepo(tmp).current_branch()
            session = Session(path=str(tmp), name="sprint")
            session.ensure_started()
            _git(tmp, "checkout", started_on)
            (tmp / "wip.txt").write_text("in progress", encoding="utf-8")
            expect(lambda: session.ensure_started()).to(
                raise_error(DirtyBranchSwitchError)
            )
            expect(WorkspaceRepo(tmp).current_branch()).to(equal(started_on))
            shutil.rmtree(tmp, ignore_errors=True)

        with it("should switch to the existing session branch from another branch"):
            import shutil
            import tempfile
            from workspace.workspace_repo import WorkspaceRepo, _git
            from workspace.workspace_session import Session

            tmp = Path(tempfile.mkdtemp(prefix="session_git_resume_clean_"))
            _git(tmp, "init")
            _git(tmp, "config", "user.email", "test@example.com")
            _git(tmp, "config", "user.name", "test")
            _git(tmp, "commit", "--allow-empty", "-m", "init")
            started_on = WorkspaceRepo(tmp).current_branch()
            session = Session(path=str(tmp), name="sprint")
            session.ensure_started()
            (tmp / "handoff-marker.txt").write_text("user-one-handoff", encoding="utf-8")
            _git(tmp, "add", "handoff-marker.txt")
            _git(tmp, "add", ".context")
            _git(tmp, "commit", "-m", "handoff")
            _git(tmp, "checkout", started_on)
            session.ensure_started()
            expect(WorkspaceRepo(tmp).current_branch()).to(equal("session/sprint"))
            expect((tmp / "handoff-marker.txt").read_text(encoding="utf-8")).to(
                equal("user-one-handoff")
            )
            shutil.rmtree(tmp, ignore_errors=True)

        with it("should return to the first session branch after a later session was created from main"):
            import shutil
            import tempfile
            from workspace.workspace_repo import WorkspaceRepo, _git
            from workspace.workspace_session import Session

            tmp = Path(tempfile.mkdtemp(prefix="session_git_two_sprints_"))
            _git(tmp, "init")
            _git(tmp, "config", "user.email", "test@example.com")
            _git(tmp, "config", "user.name", "test")
            _git(tmp, "commit", "--allow-empty", "-m", "init")
            main = WorkspaceRepo(tmp).current_branch()
            first = Session(path=str(tmp), name="first")
            first.ensure_started()
            (tmp / "first-handoff.txt").write_text("first-session-work", encoding="utf-8")
            _git(tmp, "add", "first-handoff.txt")
            _git(tmp, "add", ".context")
            _git(tmp, "commit", "-m", "first handoff")
            _git(tmp, "checkout", main)
            Session(path=str(tmp), name="second").ensure_started()
            expect(WorkspaceRepo(tmp).current_branch()).to(equal("session/second"))
            expect((tmp / "first-handoff.txt").exists()).to(be_false)
            _git(tmp, "add", ".context")
            _git(tmp, "commit", "-m", "second handoff")
            first.ensure_started()
            expect(WorkspaceRepo(tmp).current_branch()).to(equal("session/first"))
            expect((tmp / "first-handoff.txt").read_text(encoding="utf-8")).to(
                equal("first-session-work")
            )
            shutil.rmtree(tmp, ignore_errors=True)


with description("a Session that is closed"):
    with it("should write an End section with outcome into session.md"):
        import tempfile
        from workspace.workspace_session import Session
        tmp = Path(tempfile.mkdtemp(prefix="session_closed_"))
        s = Session(path=str(tmp), name="close-test")
        s.ensure_started()
        # Act
        md = s.close(outcome="all done", handoff="")
        # Assert
        content = md.read_text(encoding="utf-8")
        expect("all done" in content).to(be_true)
        expect("## End" in content).to(be_true)

    with it("should preserve hand-written prose between Start and End (regression: closing must not clobber it)"):
        import tempfile
        from workspace.workspace_session import Session
        tmp = Path(tempfile.mkdtemp(prefix="session_closed_body_"))
        s = Session(path=str(tmp), name="close-body-test")
        s.ensure_started()
        # Simulate an agent hand-writing progress notes directly into session.md
        # (outside the Session API), the way this session's Progress notes were added.
        md = s.session_md
        existing = md.read_text(encoding="utf-8")
        md.write_text(
            existing.rstrip("\n")
            + "\n\n## Progress\n\n- did the thing\n- did another thing\n",
            encoding="utf-8",
        )
        # Act: close via a fresh load, mirroring handoff.py's
        # Session.load(working, dest.name).close(...) call.
        closed_md = Session.load(str(tmp), "close-body-test").close(
            outcome="done", handoff=""
        )
        # Assert
        content = closed_md.read_text(encoding="utf-8")
        expect("## Progress" in content).to(be_true)
        expect("did the thing" in content).to(be_true)
        expect("did another thing" in content).to(be_true)
        expect("## End" in content).to(be_true)


with description("a Session tool"):
    with before.each:
        from workspace.workspace_session import Session
        from workspace.session_log import SessionLog
        SessionLog.set_instance(None)
        self.tmp = Path(tempfile.mkdtemp(prefix="session_tool_"))
        self.session = Session(path=str(self.tmp))

    with context("open"):
        with it("should ensure session, load index, and record root in one call"):
            from workspace.context_index import ContextIndex
            from workspace.workspace_session import Session

            keyed = Session(
                path=str(self.tmp),
                name="open-sprint",
                workspace=str(self.tmp),
                context_index_key="test-kit",
            )
            result = keyed.open()
            expect("Workspace open" in result).to(be_true)
            expect(keyed.session_md.is_file()).to(be_true)
            expect("missing:" not in keyed.read_context_index()).to(be_true)
            idx = ContextIndex.context_index_path(str(self.tmp))
            expect(idx.is_file()).to(be_true)
            expect("test-kit" in idx.read_text(encoding="utf-8")).to(be_true)

    with context("_ensure_sprint"):
        with it("should create the session folder and return the session.md path"):
            # Act
            result = self.session._ensure_sprint(
                name="tool-sprint", goal="goal A", path=str(self.tmp)
            )
            # Assert
            expect(Path(result).is_file()).to(be_true)
            expect(Path(result).name).to(equal("session.md"))

    with context("close_session"):
        with it("should write the End section and return the session.md path"):
            # Arrange
            self.session._ensure_sprint(name="close-sprint", path=str(self.tmp))
            # Act
            result = self.session.close_session(outcome="done")
            # Assert
            content = Path(result).read_text(encoding="utf-8")
            expect("done" in content).to(be_true)

    with context("read_context_index"):
        with it("should return a missing message when no context-index.md exists"):
            # Arrange: session with workspace pointing at an empty tmp dir
            from workspace.workspace_session import Session
            from workspace.session_log import SessionLog
            SessionLog.set_instance(None)
            fresh_tmp = Path(tempfile.mkdtemp(prefix="session_read_idx_"))
            session = Session(path=str(fresh_tmp), workspace=str(fresh_tmp))
            # Act
            result = session.read_context_index()
            # Assert
            expect("missing" in result).to(be_true)

        with context("when a context-index.md exists"):
            with it("should return the file contents"):
                # Arrange
                from workspace.workspace_session import Session
                from workspace.session_log import SessionLog
                from workspace.context_index import ContextIndex
                SessionLog.set_instance(None)
                idx_tmp = Path(tempfile.mkdtemp(prefix="session_read_idx_exist_"))
                ContextIndex.upsert_entry(str(idx_tmp), "mytool", "fixtures/my-tool")
                session = Session(path=str(idx_tmp), workspace=str(idx_tmp))
                # Act
                result = session.read_context_index()
                # Assert
                expect("mytool" in result).to(be_true)

    with context("record_context_root"):
        with it("should skip when the session has no context_index_key"):
            # Act
            result = self.session.record_context_root()
            # Assert
            expect("skipped" in result).to(be_true)


with description("docs_dir"):
    with it("should return a sprint folder unchanged when the parent is 'sessions'"):
        from workspace.session import SessionPaths
        sprint = Path("/work/.context/sessions/my-sprint")
        # Act / Assert
        expect(SessionPaths.docs_dir(sprint)).to(equal(sprint))

    with it("should return path/.context for a working area path"):
        from workspace.session import SessionPaths
        working = Path("/work/sandbox")
        # Act / Assert
        expect(SessionPaths.docs_dir(working)).to(equal(working / ".context"))
