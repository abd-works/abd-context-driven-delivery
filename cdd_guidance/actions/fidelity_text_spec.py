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

from expects import be_empty, be_false, contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.actions.document.document import Document
from cdd_guidance.actions.generate.generate import Generate
from cdd_guidance.actions.grill_context.grill_context import GrillContext
from cdd_guidance.actions.improvement.improvement import Improvement
from cdd_guidance.actions.iterate.iterate import Iterate
from cdd_guidance.actions.partition.partition import Partition
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


def _fidelity(name: str, practice: str = "stories"):
    """A fidelity of practice as a practice no session holds has it, to compare an action's text against."""
    return PracticeCatalogue.create(practice).fidelities[name]


def _expansion(project: Path | None, action_type, recipe, arguments: dict):
    """recipe of an action of action_type made for a call on project naming arguments, expanded for that call the way
    the MCP host expands it: from the call's arguments alone, with nothing run on the action first."""
    action = action_type().for_call(ToolCall(arguments, project))
    return AgentInstructions.for_callable(recipe, action).expand(arguments)


def _expanded(project: Path, action_type, recipe, arguments: dict) -> str:
    """The instructions of recipe expanded for a call on project naming arguments."""
    return _expansion(project, action_type, recipe, arguments).instructions


def _answered(project: Path, action_type, recipe, arguments: dict) -> str:
    """The reply the MCP host gives a call on project naming only arguments, the way a client sends it: the recipe
    answered for that call, which logs the call as the host does."""
    return AgentInstructions.for_callable(recipe, action_type()).answer(ToolCall(arguments, project))


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

        with it("should give the fidelity's rules once"):
            expect(self.prose.count(f"### {_rule(self.story_map)}")).to(equal(1))

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

        # A call that names no plan leaves the clause naming it out rather than handing the agent a blank.
        with it("should name no blank plan"):
            expect(self.prose).not_to(contain("Grilling session for:"))

    with context("that grills a plan the call names by its path"):
        with it("should name the plan's path"):
            prose = _expanded(self.throwaway.root, GrillContext, GrillContext.grill_with_context, {"paths": "plan.md"})
            expect(prose).to(contain("Grilling session for: plan.md"))

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

    # Building a prompt runs the recipes it names, such as the generate a sketch ends with. Only the action the call asked
    # for may say it ran: a generate line tells the session board that generate is done before anything is written.
    with context("that an MCP client calls with only its required arguments"):
        with context("to sketch"):
            with before.each:
                self.reply = _answered(self.throwaway.root, Sketch, Sketch.sketch, {"guidance": _STORY_MAP})

            with it("should give the sketch instructions"):
                expect(self.reply).to(contain("save_sketch the shell"))

            with it("should log no generate line"):
                expect(_logged_verbs(self.session_folder)).not_to(contain("generate"))

        with context("to grill"):
            with before.each:
                self.reply = _answered(self.throwaway.root, GrillContext, GrillContext.grill, {"guidance": _STORY_MAP})

            with it("should give the grill's interview"):
                expect(self.reply).to(contain("Conduct a relentless grilling interview"))

            with it("should log no generate line"):
                expect(_logged_verbs(self.session_folder)).not_to(contain("generate"))

        with context("to iterate"):
            with before.each:
                self.reply = _answered(self.throwaway.root, Iterate, Iterate.iterate, {"guidance": _STORY_MAP})

            with it("should give the grill's interview"):
                expect(self.reply).to(contain("Conduct a relentless grilling interview"))

            with it("should log that it iterates"):
                expect(_logged_verbs(self.session_folder)).to(contain("iterate"))

            with it("should log no generate line"):
                expect(_logged_verbs(self.session_folder)).not_to(contain("generate"))

        with context("to generate"):
            with it("should log its own generate line"):
                _answered(self.throwaway.root, Generate, Generate.generate, {"guidance": _STORY_MAP})
                expect(_logged_verbs(self.session_folder)).to(contain("generate"))

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

    # The index and the segments a partition asks for are one set for the corpus the call names, whatever it lists.
    with context("that partitions one corpus for two practices"):
        with before.each:
            arguments = {"guidance": "stories-story-map ddd-bounded-context", "paths": ["docs"], "mode": "one_go"}
            self.prose = _expanded(self.throwaway.root, Partition, Partition.partition, arguments)

        with it("should ask for the corpus's index once"):
            expect(self.prose.count("Index the corpus at docs")).to(equal(1))

        with it("should ask for its segments once"):
            expect(self.prose.count("Verbatim source chunks written as")).to(equal(1))

        with it("should give the Scaffold section of each practice's fidelity"):
            expect(self.prose).to(contain(self.story_map.scaffold))

    with context("that documents"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, Document, Document.document, {"guidance": _STORY_MAP, "paths": ["docs"]})

        with it("should give the fidelity's template"):
            expect(self.prose).to(contain(self.story_map.templates.strip()))

        # The session section names the session's root; a "session path" would be a folder the agent cannot find.
        with it("should name the session's root as where the observed state goes"):
            expect(self.prose).not_to(contain("session path"))

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


def _rules_given_twice() -> list[str]:
    """Each fidelity of every practice with the rule slugs its checked rules hold more than once."""
    found = []
    for key in PracticeCatalogue.keys():
        for fidelity in PracticeCatalogue.create(key).fidelities:
            slugs = [rule.slug for collection in fidelity.checked_rule_collections() for rule in collection]
            found.extend(f"{fidelity.slug}: {slug}" for slug in dict.fromkeys(slugs) if slugs.count(slug) > 1)
    return found


# Two texts for one rule leave the agent to guess which one holds; a fidelity restates no shared rule.
with description("the rules an action gives at any fidelity of any practice"):
    with it("should give each rule once"):
        expect(_rules_given_twice()).to(equal([]))


# A practice's first fidelity is the one it is made at, so an action that loses the fidelity a call names still gives
# the first one's text. Each action is asked here at a later fidelity: its text must be that fidelity's, not the first's.
_DDD_MODEL = "ddd-model"
_ACCEPTANCE_TESTS = "stories-acceptance-tests"
_UX_MOCKUP = "ux-mockup"


with description("an action that works at a fidelity past its practice's first") as self:
    with before.each:
        self.throwaway = ThrowawayProject()
        sessions = Sessions(self.throwaway.root)
        sessions.open(sessions.create("alpha", self.throwaway.root))
        self.model = _fidelity("model", "ddd")
        self.bounded_context = _fidelity("bounded_context", "ddd")

    with after.each:
        self.throwaway.close()

    with it("should have a template that differs from the first fidelity's, to tell them apart"):
        expect(self.model.templates.strip()).not_to(equal(self.bounded_context.templates.strip()))

    with context("that generates"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, Generate, Generate.generate, {"guidance": _DDD_MODEL})

        with it("should give the named fidelity's instructions"):
            expect(self.prose).to(contain(self.model.overview.strip()))

        with it("should give the named fidelity's template"):
            expect(self.prose).to(contain(self.model.templates.strip()))

        with it("should give the named fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.model)))

        with it("should not give the first fidelity's template"):
            expect(self.prose).not_to(contain(self.bounded_context.templates.strip()))

    with context("that sketches"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, Sketch, Sketch.sketch, {"guidance": _DDD_MODEL})

        with it("should give the named fidelity's template"):
            expect(self.prose).to(contain(self.model.templates.strip()))

        with it("should give the named fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.model)))

        with it("should not give the first fidelity's Scaffold section"):
            expect(self.prose).not_to(contain(self.bounded_context.scaffold))

    with context("that grills at the model"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, GrillContext, GrillContext.grill, {"guidance": _DDD_MODEL})

        with it("should give the named fidelity's instructions to generate from"):
            expect(self.prose).to(contain(self.model.overview.strip()))

        with it("should give the named fidelity's template"):
            expect(self.prose).to(contain(self.model.templates.strip()))

        with it("should give the named fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.model)))

        with it("should not give the first fidelity's template"):
            expect(self.prose).not_to(contain(self.bounded_context.templates.strip()))

    with context("that grills at the acceptance tests"):
        with before.each:
            self.acceptance_tests = _fidelity("acceptance_tests")
            self.prose = _expanded(self.throwaway.root, GrillContext, GrillContext.grill, {"guidance": _ACCEPTANCE_TESTS})

        with it("should give the named fidelity's instructions to generate from"):
            expect(self.prose).to(contain(self.acceptance_tests.overview.strip()))

        with it("should give the named fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.acceptance_tests)))

        with it("should not give the story map's template"):
            expect(self.prose).not_to(contain(_fidelity("story_map").templates.strip()))

    with context("that grills at the mockup"):
        with before.each:
            self.mockup = _fidelity("mockup", "ux")
            self.prose = _expanded(self.throwaway.root, GrillContext, GrillContext.grill, {"guidance": _UX_MOCKUP})

        with it("should give the named fidelity's instructions to generate from"):
            expect(self.prose).to(contain(self.mockup.overview.strip()))

        with it("should give the named fidelity's template"):
            expect(self.prose).to(contain(self.mockup.templates.strip()))

        with it("should give the named fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.mockup)))

    with context("that an MCP client asks to grill with only its required arguments"):
        with it("should give the named fidelity's template"):
            reply = _answered(self.throwaway.root, GrillContext, GrillContext.grill, {"guidance": _DDD_MODEL})
            expect(reply).to(contain(self.model.templates.strip()))

    with context("that iterates"):
        with before.each:
            self.prose = _expanded(self.throwaway.root, Iterate, Iterate.iterate, {"guidance": _DDD_MODEL})

        with it("should give the named fidelity's template"):
            expect(self.prose).to(contain(self.model.templates.strip()))

        with it("should give the named fidelity's rules"):
            expect(self.prose).to(contain(_rule(self.model)))

    with context("that satisfies"):
        with it("should give the named fidelity's rules"):
            prose = _expanded(self.throwaway.root, Satisfy, Satisfy.satisfy, {"guidance": _DDD_MODEL})
            expect(prose).to(contain(_rule(self.model)))

    with context("that documents"):
        with it("should give the named fidelity's template"):
            prose = _expanded(self.throwaway.root, Document, Document.document, {"guidance": _DDD_MODEL, "paths": ["docs"]})
            expect(prose).to(contain(self.model.templates.strip()))

    with context("that repairs"):
        with it("should give the named fidelity's template"):
            arguments = {"guidance": _DDD_MODEL, "asset": "a.md", "violation": "rule"}
            prose = _expanded(self.throwaway.root, Improvement, Improvement.repair, arguments)
            expect(prose).to(contain(self.model.templates.strip()))

    with context("that creates a rule"):
        with it("should give the named fidelity's template"):
            arguments = {"guidance": _DDD_MODEL, "failed": "a.md", "wanted": "b.md"}
            prose = _expanded(self.throwaway.root, Validate, Validate.create_rule, arguments)
            expect(prose).to(contain(self.model.templates.strip()))

    with context("that partitions"):
        with it("should not give the first fidelity's Scaffold section"):
            arguments = {"guidance": _DDD_MODEL, "paths": ["docs"], "mode": "one_go"}
            prose = _expanded(self.throwaway.root, Partition, Partition.partition, arguments)
            expect(prose).not_to(contain(self.bounded_context.scaffold))
