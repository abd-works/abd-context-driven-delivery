"""BDD spec — Satisfy action, its recipe expanded as the MCP host expands it."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.bootstrap import ensure_import_path

ensure_import_path(_REPO_ROOT)

from expects import contain, expect
from mamba import after, before, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.actions.satisfy.satisfy import Satisfy
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from space.session.throwaway_project import ThrowawayProject


def _expanded(project: Path, guidance) -> str:
    action = Satisfy(session=ToolCall(project=project).session)
    return AgentInstructions.for_callable(Satisfy.satisfy, action).expand({"guidance": guidance}).instructions


with description("satisfy on practice guidance") as self:
    with before.each:
        self.throwaway = ThrowawayProject()

    with after.each:
        self.throwaway.close()

    with it("should tell the agent to call validate"):
        text = _expanded(self.throwaway.root, [CleanEngineering(fidelity="code", format="python")])
        expect(text).to(contain("Call **`validate`** with the same guidance"))

    with it("should give the rules of the fidelity it works at"):
        text = _expanded(self.throwaway.root, [CleanEngineering(fidelity="code", format="python")])
        expect(text).to(contain("vocabulary-traces-to-source"))

    with it("should ask for a Fixes list when validate is clean"):
        text = _expanded(self.throwaway.root, [CleanEngineering(fidelity="code", format="python")])
        expect(text).to(contain("**Fixes**"))

    # A fix in one format alone leaves the fidelity's other formats still breaking the rule.
    with it("should tell the agent to fix every format of the fidelity: documents, diagrams, and code"):
        text = _expanded(self.throwaway.root, [CleanEngineering(fidelity="model", format="markdown")])
        expect(text).to(contain("A violation is fixed only when every format of the fidelity agrees: its documents, its diagrams, and its code."))
