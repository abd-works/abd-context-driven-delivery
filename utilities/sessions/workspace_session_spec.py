"""BDD spec for WorkspaceSession - kit prose + tools on BaseContextTool hosts."""

import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_none, be_true, equal, expect
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
    with it("should resolve create_session from workspace_session.md section"):
        text = _section("create_session")
        expect(text.startswith("# Create Session")).to(be_true)
        expect("kebab-slug" in text).to(be_true)

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

        with it("should name open's session tools then CDR tools"):
            expect(self.response["tools"]).to(
                equal(
                    [
                        "ensure_session",
                        "read_context_index",
                        "record_context_root",
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                    ]
                )
            )

        with it("should inline Session Guidance from workspace_session.md"):
            expect("# Session Guidance" in self.response["instructions"]).to(be_true)
            expect(
                "session.folder" in self.response["instructions"]
                or "folder" in self.response["instructions"]
                or "active.path" in self.response["instructions"]
                or "path" in self.response["instructions"]
            ).to(be_true)

        with it("should expand session resource from the host instance"):
            expect(
                f"Resource `active` = {self.host.active!r}."
                in self.response["instructions"]
            ).to(be_true)

        with it("should expand kit tool instructions from workspace_session.md"):
            from sessions.workspace_session import Session

            tools = _discover_tools(self.host.workspace())
            expect(isinstance(self.host.workspace(), Session)).to(be_true)
            expect(tools["create_session"].instructions.startswith("# Create Session")).to(
                be_true
            )
            expect(
                tools["read_context_index"].instructions.startswith("# Read Context Index")
            ).to(be_true)
            expect(
                tools["ensure_session"].instructions.startswith("# Ensure Session")
            ).to(be_true)

    with context("ChronicleWithOutput generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_CHRONICLE_WITH_OUTPUT_TOOLSET
            )

        with it("should keep session tools ahead of nested generate_output tools"):
            expect(self.response["tools"]).to(
                equal(
                    [
                        "ensure_session",
                        "read_context_index",
                        "record_context_root",
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                        "add_epic",
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

        with it("should inline session guidance on the composer"):
            expect("# Session Guidance" in self.response["instructions"]).to(be_true)


with description("a Session with a name and path"):
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="session_props_"))
        from sessions.workspace_session import Session
        from sessions.session_log import SessionLog
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
        from sessions.workspace_session import Session
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
        from sessions.workspace_session import Session
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
            from sessions.workspace_session import Session
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
            from sessions.workspace_session import Session
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
        from sessions.workspace_session import Session
        tmp = Path(tempfile.mkdtemp(prefix="session_started_"))
        s = Session(path=str(tmp), name="start-test", goal="build feature")
        # Act
        md = s.ensure_started()
        # Assert
        expect(md.is_file()).to(be_true)
        content = md.read_text(encoding="utf-8")
        expect("build feature" in content).to(be_true)


with description("a Session that is closed"):
    with it("should write an End section with outcome into session.md"):
        import tempfile
        from sessions.workspace_session import Session
        tmp = Path(tempfile.mkdtemp(prefix="session_closed_"))
        s = Session(path=str(tmp), name="close-test")
        s.ensure_started()
        # Act
        md = s.close(outcome="all done", handoff="")
        # Assert
        content = md.read_text(encoding="utf-8")
        expect("all done" in content).to(be_true)
        expect("## End" in content).to(be_true)


with description("a Session tool"):
    with before.each:
        from sessions.workspace_session import Session
        from sessions.session_log import SessionLog
        SessionLog.set_instance(None)
        self.tmp = Path(tempfile.mkdtemp(prefix="session_tool_"))
        self.session = Session(path=str(self.tmp))

    with context("ensure_session"):
        with it("should create the session folder and return the session.md path"):
            # Act
            result = self.session.ensure_session(name="tool-sprint", goal="goal A",
                                                  path=str(self.tmp))
            # Assert
            expect(Path(result).is_file()).to(be_true)
            expect(Path(result).name).to(equal("session.md"))

    with context("create_session"):
        with it("should create the session and return the session.md path"):
            # Act
            result = self.session.create_session(name="create-sprint",
                                                  path=str(self.tmp))
            # Assert
            expect(Path(result).is_file()).to(be_true)

    with context("close_session"):
        with it("should write the End section and return the session.md path"):
            # Arrange
            self.session.ensure_session(name="close-sprint", path=str(self.tmp))
            # Act
            result = self.session.close_session(outcome="done")
            # Assert
            content = Path(result).read_text(encoding="utf-8")
            expect("done" in content).to(be_true)

    with context("read_context_index"):
        with it("should return a missing message when no context-index.md exists"):
            # Arrange: session with workspace pointing at an empty tmp dir
            from sessions.workspace_session import Session
            from sessions.session_log import SessionLog
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
                from sessions.workspace_session import Session
                from sessions.session_log import SessionLog
                from sessions.context_index import ContextIndex
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
        from sessions.session import SessionPaths
        sprint = Path("/work/.context/sessions/my-sprint")
        # Act / Assert
        expect(SessionPaths.docs_dir(sprint)).to(equal(sprint))

    with it("should return path/.context for a working area path"):
        from sessions.session import SessionPaths
        working = Path("/work/sandbox")
        # Act / Assert
        expect(SessionPaths.docs_dir(working)).to(equal(working / ".context"))
