# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for LifecycleAction — AgentSession prelude for action kits."""

import inspect
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_agents = str(_REPO_ROOT / "agents")
for _cat in ("utilities", "primitives", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
if _agents not in sys.path:
    sys.path.insert(0, _agents)

from expects import be_false, be_none, be_true, contain, equal, expect
from mamba import before, context, description, it

from agents.agent import AgentSession, InMemoryRepo, Repo, Workspace
from lifecycle import LifecycleAction
from record_decisions.record_decisions import RecordDecisions


def _log_kinds(session: AgentSession) -> list[str]:
    return [record["kind"] for record in session.log._records]


with description("a lifecycle action"):
    with context("whose module source is inspected"):
        with it("should open via agents.agent.Workspace and AgentSession"):
            source = Path(inspect.getfile(LifecycleAction)).read_text(encoding="utf-8")
            expect("from agents.agent import" in source).to(be_true)
            expect("workspace.open" in source).to(be_true)
            expect("WorkSession" in source).to(be_false)
            expect("workspace.workspace" in source).to(be_false)

    with context("that is constructed on a temp workspace"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            (self.root / ".context").mkdir()
            self.action = LifecycleAction(path=str(self.root))

        with it("should build an agents.agent.Workspace with a primary repo"):
            expect(isinstance(self.action.workspace, Workspace)).to(be_true)
            expect(self.action.workspace.primary_repo).not_to(be_none)
            expect(isinstance(self.action.workspace.primary_repo, InMemoryRepo)).to(be_true)

        with it("should leave no agent session open until begin or open_workspace"):
            expect(self.action._session()).to(be_none)

    with context("that is constructed with a session name"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            (self.root / ".context").mkdir()
            self.action = LifecycleAction(path=str(self.root), session="u2-open")

        with it("should open an AgentSession under .agent_sessions"):
            session = self.action._session()
            expect(session).not_to(be_none)
            expect(session.name).to(equal("u2-open"))
            expect(session.folder).to(equal(self.root / ".agent_sessions" / "u2-open"))

        with it("should resolve context_root to .context when present"):
            session = self.action._session()
            expect(session.context_root).to(equal(self.root / ".context"))

    with context("that begins a wrapped action"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            (self.root / ".context").mkdir()
            self.action = LifecycleAction(path=str(self.root), session="u2-begin")

        with it("should hang a turn on the agent session"):
            with patch.object(RecordDecisions, "record_decisions_session", return_value=""):
                self.action.begin(action="generate")
            session = self.action._session()
            turn = session.turn
            expect(turn.hanging).to(be_true)
            expect(session.open_turn).to(equal(turn))
            expect(_log_kinds(session)).to(contain("open_turn"))

        with it("should record the action on the hanging turn"):
            with patch.object(RecordDecisions, "record_decisions_session", return_value=""):
                self.action.begin(action="validate")
            turn = self.action._session().open_turn
            expect(turn._action).to(equal("validate"))

        with it("should use session.decisions for decision records"):
            session = self.action._session()
            expect(isinstance(session.decisions, RecordDecisions)).to(be_true)

    with context("that ends a wrapped action"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            (self.root / ".context").mkdir()
            self.action = LifecycleAction(path=str(self.root), session="u2-end")
            with patch.object(RecordDecisions, "record_decisions_session", return_value=""):
                self.action.begin(action="generate")

        with it("should finish the hanging turn via finish_turn"):
            session = self.action._session()
            self.action.end()
            expect(session.open_turn).to(be_none)
            expect(_log_kinds(session)).to(contain("finish_turn"))

    with context("whose open_workspace tool is invoked"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            (self.root / ".context").mkdir()
            self.action = LifecycleAction(path=str(self.root))

        with it("should return the opened agent session name"):
            name = self.action.open_workspace(name="u2-tool")
            expect(name).to(equal("u2-tool"))
            expect(self.action._session().name).to(equal("u2-tool"))

    with context("that loads path overrides from context-index.md"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            index = self.root / ".context" / "context-index.md"
            index.parent.mkdir(parents=True)
            index.write_text(
                "| tool | fidelity | path |\n"
                "| --- | --- | --- |\n"
                "| agent | contextRoot | custom-context |\n",
                encoding="utf-8",
            )
            self.action = LifecycleAction(path=str(self.root), session="u2-override")

        with it("should resolve context_root from the workspace override"):
            session = self.action._session()
            expect(session.context_root).to(equal(Path("custom-context")))
