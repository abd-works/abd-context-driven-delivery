"""BDD spec — the actions that write a practice's artifacts tell the agent the fidelity they work at: its instructions,
its template, its examples and its rules, read from the fidelity the action holds rather than the practice's current one."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_empty, contain, expect
from mamba import after, before, context, description, it

from cdd_guidance.actions.document.document import Document
from cdd_guidance.actions.generate.generate import Generate
from cdd_guidance.actions.improvement.improvement import Improvement
from cdd_guidance.actions.validate.validate import Validate
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.practice_catalogue import PracticeCatalogue
from space.session import Sessions
from space.session.throwaway_project import ThrowawayProject

_STORY_MAP = "stories-story-map"
_SCENARIOS = "stories-scenarios"


def _fidelity(name: str):
    """A fidelity of Stories as a practice no session holds has it, to compare an action's text against."""
    return PracticeCatalogue.create("stories").fidelities[name]


def _expanded(project: Path, action_type, recipe, arguments: dict) -> str:
    """recipe of an action of action_type made for a call on project naming arguments, expanded for that call."""
    action = action_type().for_call(ToolCall(arguments, project))
    return AgentInstructions.for_callable(recipe, action).expand(arguments).instructions


with description("an action that writes a practice's artifacts") as self:
    with before.each:
        self.throwaway = ThrowawayProject()
        sessions = Sessions(self.throwaway.root)
        sessions.open(sessions.create("alpha", self.throwaway.root))
        self.story_map = _fidelity("story_map")
        self.scenarios = _fidelity("scenarios")

    with after.each:
        self.throwaway.close()

    with it("should have a template for the fidelity to show"):
        expect(self.story_map.templates.strip()).not_to(be_empty)

    with it("should have examples for the fidelity to show"):
        expect(str(self.story_map.examples).strip()).not_to(be_empty)

    with context("that generates"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, Generate,Generate.generate, {"guidance": _STORY_MAP})

        with it("should give the fidelity's instructions"):
            expect(self.prose).to(contain(self.story_map.overview.strip()))

        with it("should give the fidelity's template"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

    with context("that documents"):
        with it("should give the fidelity's template"):
            prose = _expanded(self.throwaway.root, Document,Document.document, {"guidance": _STORY_MAP, "paths": ["docs"]})
            expect(prose).to(contain(self.story_map.templates.strip()))

    with context("that repairs"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, Improvement,Improvement.repair, {"guidance": _STORY_MAP, "asset": "a.md", "violation": "rule"})

        with it("should give the fidelity's template"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

        with it("should give the fidelity's examples"):
            expect(self.prose).to(contain(str(self.story_map.examples).strip()))

    with context("that creates a rule"):
        with it("should give the fidelity's template"):
            prose = _expanded(self.throwaway.root, Validate,Validate.create_rule, {"guidance": _STORY_MAP, "failed": "a.md", "wanted": "b.md"})
            expect(prose).to(contain(self.story_map.templates.strip()))

    # Two calls in one session share its practice; the second must not change the fidelity the first one works at.
    with context("while another call works at another fidelity of the same practice"):
        with before.each:
            root = self.throwaway.root
            self.action = Generate().for_call(ToolCall({"guidance": _STORY_MAP}, root))
            self.action.listed()
            Generate().for_call(ToolCall({"guidance": _SCENARIOS}, root)).listed()
            self.prose = AgentInstructions.for_callable(Generate.generate, self.action).expand({"guidance": _STORY_MAP}).instructions

        with it("should give the template of the fidelity it works at"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

        with it("should not give the other fidelity's template"):
            expect(self.prose).not_to(contain(self.scenarios.templates.strip()))

        with it("should give the rules of the fidelity it works at"):
            expect(self.prose).to(contain(f"`{list(self.story_map.rules)[0].slug}`"))

        with it("should not give the other fidelity's rules"):
            expect(self.prose).not_to(contain(f"`{list(self.scenarios.rules)[0].slug}`"))
