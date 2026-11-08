"""An agent BDD practice writing its artifact: it composes vanilla BDD's guidance, the way a practice composes another
practice, without reaching for an action."""

import ast
import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, description, it

from cdd_guidance.practices.agent_bdd.agent_bdd import AgentBdd
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from space.session.throwaway_project import ThrowawayProject

with description("an agent BDD practice writing its artifact"):
    with before.all:
        self.project = ThrowawayProject()
        self.agent_bdd = AgentBdd()
        self.agent_bdd.session = ToolCall(project=self.project.root).session
        self.prose = AgentInstructions.for_callable(AgentBdd.generate_output, self.agent_bdd).expand({}).instructions

    with after.all:
        ThrowawayProject.close_all()

    with it("should carry vanilla BDD's guidance"):
        expect(self.prose).to(contain("Behavior-driven development turns domain vocabulary into passing tests"))

    with it("should import no action, as every practice composes another practice directly"):
        tree = ast.parse(Path(sys.modules[AgentBdd.__module__].__file__).read_text(encoding="utf-8"))
        imported = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        expect([module for module in imported if module.startswith("cdd_guidance.actions")]).to(equal([]))
