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

from expects import be_empty, be_false, contain, expect
from mamba import after, before, context, description, it

from cdd_guidance.actions.document.document import Document
from cdd_guidance.actions.generate.generate import Generate
from cdd_guidance.actions.grill_context.grill_context import GrillContext
from cdd_guidance.actions.improvement.improvement import Improvement
from cdd_guidance.actions.iterate.iterate import Iterate
from cdd_guidance.actions.satisfy.satisfy import Satisfy
from cdd_guidance.actions.sketch.sketch import Sketch
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


def _expansion(project: Path | None, action_type, recipe, arguments: dict):
    """recipe of an action of action_type made for a call on project naming arguments, expanded for that call the way
    the MCP host expands it: from the call's arguments alone, with nothing run on the action first."""
    action = action_type().for_call(ToolCall(arguments, project))
    return AgentInstructions.for_callable(recipe, action).expand(arguments)


def _expanded(project: Path, action_type, recipe, arguments: dict) -> str:
    """The instructions of recipe expanded for a call on project naming arguments."""
    return _expansion(project, action_type, recipe, arguments).instructions


def _rule(fidelity) -> str:
    """How a prompt names the first rule of fidelity."""
    return f"`{list(fidelity.rules)[0].slug}`"


def _logged_verbs(session_folder: Path) -> list[str]:
    log = session_folder / "session.log"
    lines = log.read_text(encoding="utf-8").splitlines() if log.is_file() else []
    return [line.split(" ")[1] for line in lines if len(line.split(" ")) > 1]


with description("an action that writes a practice's artifacts") as self:
    with before.each:
        self.throwaway = ThrowawayProject()
        sessions = Sessions(self.throwaway.root)
        sessions.open(sessions.create("alpha", self.throwaway.root))
        self.session_folder = self.throwaway.root / ".sessions" / "alpha"
        self.story_map = _fidelity("story_map")
        self.scenarios = _fidelity("scenarios")

    with after.each:
        self.throwaway.close()

    with it("should have a template for the fidelity to show"):
        expect(self.story_map.templates.strip()).not_to(be_empty)

    with it("should have examples for the fidelity to show"):
        expect(str(self.story_map.examples).strip()).not_to(be_empty)

    with it("should have a sketch template for the practice to show"):
        expect(self.story_map.sketch_template.strip()).not_to(be_empty)

    with it("should have a Scaffold section for the fidelity to show"):
        expect(self.story_map.scaffold).not_to(be_empty)

    with context("that generates"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, Generate,Generate.generate, {"guidance": _STORY_MAP})

        with it("should give the fidelity's instructions"):
            expect(self.prose).to(contain(self.story_map.overview.strip()))

        with it("should give the fidelity's template"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

    # Each recipe below reaches its text through recipes it names; a recipe called as a Python method gives the prompt
    # nothing, so these expand from the call's arguments alone and look for the text that must arrive.
    with context("that sketches"):
        with before.each:
            self.expansion = _expansion(self.throwaway.root, Sketch, Sketch.sketch, {"guidance": _STORY_MAP})
            self.prose = self.expansion.instructions

        with it("should give the fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.story_map)))

        with it("should give the practice's sketch template"):
            expect(self.prose).to(contain(self.story_map.sketch_template.strip()))

        with it("should give the fidelity's Scaffold section, the shell's level of detail"):
            expect(self.prose).to(contain(self.story_map.scaffold))

        with it("should give the grill's interview"):
            expect(self.prose).to(contain("Conduct a relentless grilling interview"))

        with it("should give the generate the agreed sketch becomes, with the fidelity's template"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

        with it("should list save_sketch and review_sketch as tools"):
            expect(self.expansion.tools).to(contain("save_sketch", "review_sketch"))

        with it("should list validate as a tool, for after the artifact is generated"):
            expect(self.expansion.tools).to(contain("validate"))

    with context("that grills"):
        with before.each:
            self.expansion = _expansion(self.throwaway.root, GrillContext, GrillContext.grill, {"guidance": _STORY_MAP})
            self.prose = self.expansion.instructions

        with it("should give the grill's interview"):
            expect(self.prose).to(contain("Conduct a relentless grilling interview"))

        with it("should give the fidelity's instructions to generate from"):
            expect(self.prose).to(contain(self.story_map.overview.strip()))

        with it("should give the fidelity's template"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

        with it("should give the fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.story_map)))

        with it("should list the grill's tools and validate"):
            expect(self.expansion.tools).to(contain("explore_context_files", "write_grill_answer", "validate"))

    with context("that iterates"):
        with before.each:
            self.expansion = _expansion(self.throwaway.root, Iterate, Iterate.iterate, {"guidance": _STORY_MAP})
            self.prose = self.expansion.instructions

        with it("should give the grill's interview"):
            expect(self.prose).to(contain("Conduct a relentless grilling interview"))

        with it("should give the fidelity's template"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

        with it("should give the fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.story_map)))

        with it("should list mark_iterate_round and validate as tools"):
            expect(self.expansion.tools).to(contain("mark_iterate_round", "validate"))

    with context("that iterates in no session"):
        with it("should still give the grill's interview"):
            prose = _expanded(None, Iterate, Iterate.iterate, {"guidance": _STORY_MAP})
            expect(prose).to(contain("Conduct a relentless grilling interview"))

    with context("that satisfies"):
        with before.each:
            self.expansion = _expansion(self.throwaway.root, Satisfy, Satisfy.satisfy, {"guidance": _STORY_MAP})
            self.prose = self.expansion.instructions

        with it("should give the fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.story_map)))

        with it("should give the fixes to apply after validate"):
            expect(self.prose).to(contain("Apply the fixes the latest validate report names"))

        with it("should list validate as a tool to call"):
            expect(self.expansion.tools).to(contain("validate"))

        # The agent runs validate itself; checking nothing yet, the expansion must not tell the board the work was checked.
        with it("should save no validation report"):
            expect((self.session_folder / "validation-reports").exists()).to(be_false)

        with it("should log no validate line"):
            expect(_logged_verbs(self.session_folder)).not_to(contain("validate"))

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
