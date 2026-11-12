"""Non-agentic BDD for agent_tools — domain, @agent_instructions expand, and spec invoke."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("actions", None)

import yaml
from expects import be, be_true, contain, equal, expect, have_key, raise_error
from mamba import after, before, context, description, it
from space.session.throwaway_project import ThrowawayProject

from harness.agent_tools.agent_tools import (
    AgentInstructions,
    collect,
    tools,
    instructions,
    AgentToolValidationError,
    CallNamesNoProject,
    AgentToolSet,
    InstallDestination,
    ToolSetCollection,
    agent_instructions,
    agent_toolset,
    toolset_collection,
)
from harness.hooks.hooks import hook
from harness.mcp.mcp_annotations import mcp
from harness.agent_tools.agent_tools import AgentInstructions, ToolSetCollectionAnnotation
from harness.agent_tools.recipe import RecipeLineFailed, RecipePlaceholders
from harness.agent_tools.tool_call import ToolCall
from cdd_guidance.actions._examples.car_story.car_story import CarStory
from harness.agent_tools._examples.super_delegation.super_delegation_demo import (
    EmptySuperChild,
    EmptyWithReturn,
    ExplicitSuperChild,
    SuperBase,
)
from harness.agent_tools.agent_tools import AgentToolSet, ToolsetMembers, ToolsetReference, agent_tool as _tool, tool_subject, tools, instructions

Car = ToolsetReference("cdd_guidance.practices._examples.car.car:Car").toolset_class


class CarInstance:
    """Build a Car for agent_tools specs."""

    def __new__(cls, *, running: bool = False):
        car = Car("Toyota", "Camry", 2024, "cheerful companion named Sunny")
        if running:
            car.start()
        return car


_CAR_TOOLSET_PATH = "cdd_guidance.practices._examples.car.car:Car"


@agent_toolset
class _ModeFixture:
    @_tool
    def ping(self) -> str:
        """ping tool"""
        return "pong"

    @agent_instructions
    def run(self) -> str:
        """Run by calling ping."""
        "Run by calling ping."
        tools(self.ping())


@agent_toolset
class _SelfCallAgent:
    """Toolset whose own action calls another action on itself (same instance)."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """Prepare the work carefully."""
        "SELF_PREPARE_MARKER: prepare the work carefully."
        tools(self.polish())
        return "prepared"

    @agent_instructions
    def finish(self) -> str:
        """May invoke prepare()."""
        "SELF_FINISH_MARKER: may invoke prepare()."
        instructions(self.prepare())
        return "finished"


@agent_toolset
class _BodyModeFlipAgent:
    """Same-instance nesting that flips mode mid-body instead of cloning itself."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """Prepare the work carefully."""
        "SELF_PREPARE_MARKER: prepare the work carefully."
        tools(self.polish())
        return "prepared"

    @agent_instructions
    def finish(self) -> str:
        """Defer prepare via mid-body mode flip."""
        "SELF_FINISH_MARKER: defer prepare via mid-body mode flip."
        self.mode = "tool"
        instructions(self.prepare())
        return "finished"


@agent_toolset
class _CalleeAgent:
    """Companion agentic toolset invoked across instances."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """Prepare the work carefully."""
        "CALLEE_PREPARE_MARKER: prepare the work carefully."
        tools(self.polish())
        return "prepared"


@agent_toolset
class _CallerAgent:
    """Caller that expands a cross-instance action on a companion."""

    def __init__(self, helper: _CalleeAgent | None = None) -> None:
        self._helper = helper if helper is not None else _CalleeAgent()
        super().__init__()

    def helper(self) -> _CalleeAgent:
        return self._helper

    @agent_instructions
    def orchestrate(self) -> str:
        """May invoke helper().prepare()."""
        "CALLER_ORCHESTRATE_MARKER: may invoke helper().prepare()."
        instructions(self.helper().prepare())
        return "orchestrated"


@agent_toolset
class _PropertyCallerAgent:
    """Caller that reaches a companion via a plain property, not a zero-arg method.

    ``self.helper.prepare()`` — the provider reference (``self.helper``) is a
    bare attribute; the call boundary is ``.prepare()``, the actual action.
    """

    def __init__(self, helper: _CalleeAgent | None = None) -> None:
        self._helper = helper if helper is not None else _CalleeAgent()
        super().__init__()

    @property
    def helper(self) -> _CalleeAgent:
        return self._helper

    @agent_instructions
    def orchestrate(self) -> str:
        """May invoke helper.prepare()."""
        "CALLER_ORCHESTRATE_MARKER: may invoke helper.prepare()."
        instructions(self.helper.prepare())
        return "orchestrated"


_CAR_TOOLSET = "cdd_guidance.practices._examples.car.car:Car"
_CAR_STORY_TOOLSET = "cdd_guidance.actions._examples.car_story.car_story:CarStory"


with description("a class"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("with a toolset that declares @agent_instructions members"):
        with context("the travelTo action"):
            with it("should expose travelTo as an @agent_instructions member"):
                entry = CarStory().instructions["travelTo"]
                expect(entry.kind).to(equal("instructions"))

            with it("should expand into instructions"):
                arguments = {
                    "guidance": [
                        {
                            "toolset": _CAR_TOOLSET,
                            "context": {
                                "make": "Dodge",
                                "model": "Charger",
                                "year": 1969,
                                "personality": "General Lee",
                            },
                        }
                    ],
                    "destination": "Hazzard County courthouse",
                    "conditions": "muddy back roads",
                }
                response = CarStory().instructions["travelTo"].expand(arguments)
                expect(response.result).to(
                    equal("Instructions for traveling to Hazzard County courthouse")
                )
                expect("{destination}" in response.instructions).to(be_true)
                expect("{conditions}" in response.instructions).to(be_true)
                expect(response.tools).to(
                    equal(["start", "accelerate", "decelerate", "stop", "speak"])
                )

        with context("when expand makes tools available to the chat"):
            with it("should tell the AI to display those tools by name and purpose in the user-visible reply"):
                from harness.agent_tools._examples.logged_probe import LoggedProbe

                response = LoggedProbe().instructions["narrate"].expand(
                    {"message": "hello"},
                )
                expect(response.tools).to(equal(["ping"]))


@agent_toolset
class _SplitRecipe:
    """A recipe with an optional parameter and a docstring of several lines, as partition's is."""

    @agent_instructions
    def split(self, paths: str, mode: str = "one_go") -> str:
        """Split the source into segments.

        Name every segment after its heading."""
        "Write segments for {{paths}} in {{mode}}."
        return f"Split {paths} in {mode}"


@agent_toolset
class _ConditionalResultRecipe:
    """A recipe whose result names its source only when the call sends one, as Partition's does."""

    @agent_instructions
    def split(self, source: str = "") -> str:
        """Split the source into segments."""
        return f"Split{f' {source}' if source else ''} finished"


with description("an action"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("that has instructions with templating"):
        with context("with templated placeholders for a parameter"):
            with it("should put argument values into those instructions where {{param}} appears"):
                rendered = RecipePlaceholders({"destination": "town"}, {"destination"}).filled("Go to {{destination}}")
                expect(rendered).to(equal("Go to town"))

        with context("with templated placeholders for an instance value"):
            with it("should put instance values into those instructions where {{self.attr}} appears"):
                car = Car(make="Dodge", model="Charger", year=1969, personality="General Lee")
                rendered = RecipePlaceholders({}, set(), car).filled("Drive the {{self.make}}")
                expect(rendered).to(equal("Drive the Dodge"))

        with context("with {} single-brace placeholders"):
            with it("should leave single-brace {Placeholder} text unchanged"):
                rendered = RecipePlaceholders({"destination": "town"}, {"destination"}).filled(
                    "Fill {Placeholder} then go {{destination}}"
                )
                expect(rendered).to(equal("Fill {Placeholder} then go town"))

        with context("with a missing {{name}}"):
            with it("should fail expand/run"):
                raised = False
                try:
                    RecipePlaceholders({}, {"destination"}).filled("Go to {{destination}}")
                except ValueError as error:
                    raised = True
                    expect("destination" in str(error)).to(be_true)
                expect(raised).to(be_true)

    with context("that a call sends only its required arguments"):
        with it("should fill a placeholder of an optional parameter with that parameter's default"):
            expansion = _SplitRecipe().instructions["split"].expand({"paths": "notes.md"})
            expect(expansion.result).to(equal("Split notes.md in one_go"))

        with it("should fill the prompt's placeholder of an optional parameter with its default"):
            expansion = _SplitRecipe().instructions["split"].expand({"paths": "notes.md"})
            expect(expansion.instructions).to(contain("Write segments for notes.md in one_go"))

    # The result line is what the recipe returns for the call, so a clause the recipe adds only for some calls reads right.
    with context("whose result names a clause only some calls fill"):
        with it("should give the clause when the call fills it"):
            expansion = _ConditionalResultRecipe().instructions["split"].expand({"source": "notes.md"})
            expect(expansion.result).to(equal("Split notes.md finished"))

        with it("should leave the clause out when the call does not"):
            expansion = _ConditionalResultRecipe().instructions["split"].expand({})
            expect(expansion.result).to(equal("Split finished"))

    with context("whose recipe has a docstring of several lines"):
        with it("should send the docstring once"):
            reply = _SplitRecipe().instructions["split"].answer(ToolCall({"paths": "notes.md"}))
            expect(reply.count("Name every segment after its heading.")).to(equal(1))

    with context("that has templated string literals in the @agent_instructions body"):
        with it("should put {{param}} / {{self.attr}} values into expanded instructions"):
            from harness.agent_tools._examples.templated_md import TemplatedMdDemo

            from harness.agent_tools._examples.templated_md import TemplatedMdDemo

            response = TemplatedMdDemo(label="Desk").instructions["greet"].expand(
                {"name": "Pat"},
            )
            expect("Greet Pat on behalf of Desk" in response.instructions).to(be_true)
            expect("{Placeholder}" in response.instructions).to(be_true)


with description("super() delegation in action bodies"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("a child class that calls super().generate() explicitly"):
        with it("should inline the parent's prose in the child expansion"):
            child = ExplicitSuperChild()
            body = AgentInstructions.for_callable(ExplicitSuperChild.generate, child)
            joined = "\n".join(body.prompt)
            expect("Base generate instructions" in joined).to(be_true)

        with it("should include tool steps from the parent action"):
            child = ExplicitSuperChild()
            body = AgentInstructions.for_callable(ExplicitSuperChild.generate, child)
            expect("do_work" in body.tools).to(be_true)


with description("empty-body auto-super in action bodies"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("a child whose generate body is only Ellipsis"):
        with it("should inline the parent's prose"):
            child = EmptySuperChild()
            body = AgentInstructions.for_callable(EmptySuperChild.generate, child)
            joined = "\n".join(body.prompt)
            expect("Base generate instructions" in joined).to(be_true)

        with it("should include tool steps from the parent action"):
            child = EmptySuperChild()
            body = AgentInstructions.for_callable(EmptySuperChild.generate, child)
            expect("do_work" in body.tools).to(be_true)

        with it("should answer with the parent's result"):
            child = EmptySuperChild()
            body = AgentInstructions.for_callable(EmptySuperChild.generate, child)
            expect(body.expand({}).result).to(equal("generate done"))

    with context("a child with Ellipsis plus a custom return"):
        with it("should answer with the child's result"):
            child = EmptyWithReturn()
            body = AgentInstructions.for_callable(EmptyWithReturn.generate, child)
            expect(body.expand({}).result).to(equal("child result only"))

        with it("should still inline parent tool steps"):
            child = EmptyWithReturn()
            body = AgentInstructions.for_callable(EmptyWithReturn.generate, child)
            expect("do_work" in body.tools).to(be_true)


with description("AgentToolSet"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("on a live Car example instance"):
        with context("with a class-level description"):
            with it("should expose description matching the class docstring"):
                car = CarInstance()
                expect("Example context tool" in car.description).to(be_true)

        with context("with methods annotated as @agent_tool"):
            with before.each:
                self.car = CarInstance()

            with it("should register every annotated method in operations"):
                expect(set(self.car.operations.keys())).to(
                    equal(
                        {
                            "start",
                            "stop",
                            "drive",
                            "accelerate",
                            "decelerate",
                            "speak",
                            "wrap_story",
                            "render",
                            "rules",
                        }
                    )
                )

            with it("should expose operation descriptions from method docstrings"):
                expect(self.car.operations["start"].description).to(equal("Start the engine."))
                expect(self.car.operations["stop"].description).to(equal("Stop the engine."))
                expect(self.car.operations["drive"].description).to(
                    equal("Drive the given number of miles. Engine must be running.")
                )

            with it("should mark each operation kind as tool"):
                for entry in self.car.operations.values():
                    expect(entry.kind).to(equal("tool"))

            with it("should keep the tools it made the first time its tools are read"):
                expect(self.car.tools["start"]).to(be(self.car.tools["start"]))

            with it("should publish the same operation in its tools and its operations"):
                expect(self.car.tools["start"]).to(be(self.car.operations["start"]))

            with it("should keep each tool's parameter schema once it is read"):
                drive = self.car.tools["drive"]
                expect(drive.parameter_schema).to(be(drive.parameter_schema))

        with context("with the members its class holds"):
            with it("should hold one set of members for the class"):
                expect(ToolsetMembers.of(Car)).to(be(ToolsetMembers.of(Car)))

            with it("should give a subclass members of its own"):
                class FasterCar(Car):
                    pass

                expect(ToolsetMembers.of(FasterCar)).not_to(be(ToolsetMembers.of(Car)))

        with context("with observable state on the example Car"):
            with it("should expose current values on the instance"):
                car = CarInstance()
                expect(car.make).to(equal("Toyota"))
                expect(car.model).to(equal("Camry"))
                expect(car.year).to(equal(2024))
                expect(car.personality).to(equal("cheerful companion named Sunny"))
                expect(car.running).to(equal(False))

    with context("when an annotated @agent_tool is invoked"):
        with it("should invoke start on a constructed Car"):
            car = CarInstance()
            car.operations["start"].invoke({})
            expect(car.running).to(equal(True))

        with it("should require tool arguments declared on the operation"):
            car = CarInstance(running=True)
            raised = False
            try:
                car.operations["drive"].invoke({})
            except TypeError:
                raised = True
            expect(raised).to(be_true)

        with it("should construct Car with default make and model"):
            car = Car()
            expect(car.make).to(equal("Dodge"))
            expect(car.model).to(equal("Charger"))

    with context("the mode resource"):
        with it("should default to 'instructions'"):
            instance = _ModeFixture()
            expect(instance.mode).to(equal("instructions"))

        with it("should accept 'tool' as a valid mode"):
            instance = _ModeFixture()
            instance.mode = "tool"
            expect(instance.mode).to(equal("tool"))

        with it("should reject unknown mode values with a ValueError"):
            instance = _ModeFixture()
            raised = False
            try:
                instance.mode = "bogus"
            except ValueError:
                raised = True
            expect(raised).to(be_true)

    with context("when a caller expands a cross-instance action on a companion"):
        with context("and the companion mode is instructions"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "instructions"
                self.caller = _CallerAgent(self.callee)
                self.body = AgentInstructions.for_callable(
                    _CallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prompt)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(be_true)

            with it("should include the companion's inner tools in the expansion"):
                expect("polish" in self.body.tools).to(be_true)

            with it("should not list the companion action itself as a deferred tool"):
                expect("prepare" in self.body.tools).to(equal(False))

        with context("and the companion mode is tool"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "tool"
                self.caller = _CallerAgent(self.callee)
                self.body = AgentInstructions.for_callable(
                    _CallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prompt)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should not inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(equal(False))

            with it("should list the companion action in the expansion tools"):
                expect("prepare" in self.body.tools).to(be_true)

            with it("should not expose the companion's inner tools until that action runs"):
                expect("polish" in self.body.tools).to(equal(False))

    with context("when a caller reaches a companion via a plain property (not a method call)"):
        with context("and the companion mode is instructions"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "instructions"
                self.caller = _PropertyCallerAgent(self.callee)
                self.body = AgentInstructions.for_callable(
                    _PropertyCallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prompt)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(be_true)

            with it("should include the companion's inner tools in the expansion"):
                expect("polish" in self.body.tools).to(be_true)

            with it("should not list the companion action itself as a deferred tool"):
                expect("prepare" in self.body.tools).to(equal(False))

        with context("and the companion mode is tool"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "tool"
                self.caller = _PropertyCallerAgent(self.callee)
                self.body = AgentInstructions.for_callable(
                    _PropertyCallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prompt)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should not inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(equal(False))

            with it("should list the companion action in the expansion tools"):
                expect("prepare" in self.body.tools).to(be_true)

            with it("should not expose the companion's inner tools until that action runs"):
                expect("polish" in self.body.tools).to(equal(False))

    with context("when a toolset instance's own action calls another action on itself"):
        with context("and its own mode is instructions"):
            with before.each:
                self.instance = _SelfCallAgent()
                self.instance.mode = "instructions"
                self.body = AgentInstructions.for_callable(
                    _SelfCallAgent.finish, self.instance
                )
                self.joined = "\n".join(self.body.prompt)

            with it("should keep the caller's own instructions"):
                expect("SELF_FINISH_MARKER" in self.joined).to(be_true)

            with it("should inline the nested self-action's instructions"):
                expect("SELF_PREPARE_MARKER" in self.joined).to(be_true)

            with it("should include the nested action's inner tools in the expansion"):
                expect("polish" in self.body.tools).to(be_true)

            with it("should not list the nested action itself as a deferred tool"):
                expect("prepare" in self.body.tools).to(equal(False))

        with context("and its own mode is tool"):
            with before.each:
                self.instance = _SelfCallAgent()
                self.instance.mode = "tool"
                self.body = AgentInstructions.for_callable(
                    _SelfCallAgent.finish, self.instance
                )
                self.joined = "\n".join(self.body.prompt)

            with it("should keep the caller's own instructions"):
                expect("SELF_FINISH_MARKER" in self.joined).to(be_true)

            with it("should not inline the nested self-action's instructions"):
                expect("SELF_PREPARE_MARKER" in self.joined).to(equal(False))

            with it("should list the nested action in the expansion tools"):
                expect("prepare" in self.body.tools).to(be_true)

            with it("should not expose the nested action's inner tools until that action runs"):
                expect("polish" in self.body.tools).to(equal(False))

    with context("when a toolset flips self.mode mid-body before a nested self-action"):
        with before.each:
            self.instance = _BodyModeFlipAgent()
            self.body = AgentInstructions.for_callable(
                _BodyModeFlipAgent.finish, self.instance
            )
            self.joined = "\n".join(self.body.prompt)

        with it("should keep the caller's own instructions"):
            expect("SELF_FINISH_MARKER" in self.joined).to(be_true)

        with it("should not inline the nested self-action's instructions"):
            expect("SELF_PREPARE_MARKER" in self.joined).to(equal(False))

        with it("should list the nested action in the expansion tools"):
            expect("prepare" in self.body.tools).to(be_true)

        with it("should restore mode to instructions after the walk"):
            expect(self.instance.mode).to(equal("instructions"))


@agent_toolset
class _ForEachCallee:
    @_tool
    def polish(self) -> str:
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """Prepare carefully."""
        "FOREACH_CALLEE_MARKER: prepare carefully."
        tools(self.polish())
        return "prepared"


@agent_toolset
class _ForEachCaller:
    def companions(self) -> list:
        return [_ForEachCallee(), _ForEachCallee()]

    @agent_instructions
    def orchestrate(self) -> str:
        """Defer each companion."""
        "FOREACH_CALLER_MARKER: defer each companion."
        for companion in self.companions():
            companion.mode = "tool"
            instructions(companion.prepare())
        return "orchestrated"

    @agent_instructions
    def inline_all(self) -> str:
        """Inline each companion."""
        "FOREACH_INLINE_MARKER: inline each companion."
        for companion in self.companions():
            instructions(companion.prepare())
        return "inlined"

    @agent_instructions
    def inline_bare(self) -> str:
        """Inline each companion via bare attribute."""
        "FOREACH_BARE_MARKER: inline each companion via bare attribute."
        for companion in self.companions():
            instructions(companion.prepare())
        return "inlined"

    @agent_instructions
    def with_self_step(self) -> str:
        """Walk self tools inside the loop."""
        "FOREACH_SELF_MARKER: walk self tools inside the loop."
        for companion in self.companions():
            instructions(companion.prepare())
            tools(self.note())
        return "noted"

    @_tool
    def note(self) -> str:
        return "noted"


@agent_toolset
class _ScannerKit:
    @_tool
    def scan(self) -> str:
        return "scanned"


@agent_toolset
class _HostWithScanner:
    def __init__(self) -> None:
        self.scanner = _ScannerKit()

    @agent_instructions
    def guidance(self) -> str:
        """Contexts live here."""
        "FOREACH_GUIDANCE_MARKER: contexts live here."
        return ""


@agent_toolset
class _ScanCaller:
    def companions(self) -> list:
        return [_HostWithScanner()]

    @agent_instructions
    def check(self) -> str:
        """Guidance then scan."""
        "FOREACH_SCAN_MARKER: guidance then scan."
        for toolset in self.companions():
            instructions(toolset.guidance())
            tools(toolset.scanner.scan())
        return "checked"


@agent_toolset
class _BrokenProvider:
    def missing(self):
        raise RuntimeError("no session")

    @agent_instructions
    def wrap(self) -> str:
        """BROKEN_PROVIDER_MARKER: a provider that raises fails its line."""
        tools(self.missing().finish_turn())
        return ""


with description("a for-each action over companion toolsets"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("when each companion is flipped to tool mode in the loop"):
        with before.each:
            self.body = AgentInstructions.for_callable(
                _ForEachCaller.orchestrate, _ForEachCaller()
            )
            self.joined = "\n".join(self.body.prompt)

        with it("should keep the caller marker"):
            expect("FOREACH_CALLER_MARKER" in self.joined).to(be_true)

        with it("should not inline companion action instructions"):
            expect("FOREACH_CALLEE_MARKER" in self.joined).to(equal(False))

        with it("should list prepare as a deferred tool"):
            expect("prepare" in self.body.tools).to(be_true)

    with context("when companions stay in action mode"):
        with before.each:
            self.body = AgentInstructions.for_callable(
                _ForEachCaller.inline_all, _ForEachCaller()
            )
            self.joined = "\n".join(self.body.prompt)

        with it("should inline companion action instructions"):
            expect("FOREACH_CALLEE_MARKER" in self.joined).to(be_true)

    with context("when the loop names a bare companion action"):
        with before.each:
            self.body = AgentInstructions.for_callable(
                _ForEachCaller.inline_bare, _ForEachCaller()
            )
            self.joined = "\n".join(self.body.prompt)

        with it("should inline companion action instructions from a bare attribute"):
            expect("FOREACH_CALLEE_MARKER" in self.joined).to(be_true)

    with context("when the loop also calls a self tool"):
        with before.each:
            self.body = AgentInstructions.for_callable(
                _ForEachCaller.with_self_step, _ForEachCaller()
            )

        with it("should list the self tool from inside the loop"):
            expect("note" in self.body.tools).to(be_true)

    with context("when the loop calls a tool on a companion provider"):
        with before.each:
            self.body = AgentInstructions.for_callable(
                _ScanCaller.check, _ScanCaller()
            )
            self.joined = "\n".join(self.body.prompt)

        with it("should inline guidance on the companion"):
            expect("FOREACH_GUIDANCE_MARKER" in self.joined).to(be_true)

        with it("should list scan from var.scanner.scan"):
            expect("scan" in self.body.tools).to(be_true)


@agent_toolset
class _RulesPropertyHost:
    @property
    @agent_instructions
    def markdown_block(self) -> str:
        """NESTED_RULES_MARKER: original rules markdown."""
        return "NESTED_RULES_BODY"


@agent_toolset
class _PracticeWithRules:
    def __init__(self) -> None:
        super().__init__()
        self.rules = _RulesPropertyHost()


@agent_toolset
class _NestedRulesCaller:
    def listed(self) -> list:
        return [_PracticeWithRules()]

    @agent_instructions
    def sketchish(self) -> str:
        """Walk listed practices."""
        "NESTED_CALLER_MARKER: walk listed practices."
        for item in self.listed():
            instructions(item.rules.markdown_block)
        return "sketched"


@agent_toolset
class _EmptyListCaller:
    def listed(self) -> list:
        return []

    @agent_instructions
    def sketchish(self) -> str:
        """Walk listed practices."""
        "EMPTY_CALLER_MARKER: walk listed practices."
        for item in self.listed():
            instructions(item.rules.markdown_block)
        return "sketched"


with description("a for-each action over nested instruction properties"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("when the loop names item.rules.markdown_block"):
        with before.each:
            self.body = AgentInstructions.for_callable(
                _NestedRulesCaller.sketchish, _NestedRulesCaller()
            )
            self.joined = "\n".join(self.body.prompt)

        with it("should keep the caller marker"):
            expect("NESTED_CALLER_MARKER" in self.joined).to(be_true)

        with it("should inline the nested markdown_block"):
            expect("NESTED_RULES_MARKER" in self.joined).to(be_true)
            expect("NESTED_RULES_BODY" in self.joined).to(be_true)

    with context("with nothing listed"):
        with it("should expand the rest of the recipe without reading an item"):
            body = AgentInstructions.for_callable(_EmptyListCaller.sketchish, _EmptyListCaller())
            expect(" ".join(body.prompt)).to(contain("EMPTY_CALLER_MARKER"))


@agent_toolset
class _ExecBodyAgent:
    def __init__(self) -> None:
        super().__init__()
        self.include_extra = False
        self.ran = False

    @_tool
    def mark(self) -> str:
        self.ran = True
        return "marked"

    @agent_instructions
    def go(self) -> str:
        """Run control flow and bare calls during expand."""
        "ALWAYS_MARKER"
        if self.include_extra:
            "EXTRA_MARKER"
        else:
            "ELSE_MARKER"
        self.mark()
        if self.ran:
            "RAN_OK"
        return "done"


with description("an @agent_instructions body that runs unwrapped Python"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("when a conditional branch is taken"):
        with before.each:
            self.agent = _ExecBodyAgent()
            self.agent.include_extra = True
            self.body = AgentInstructions.for_callable(_ExecBodyAgent.go, self.agent)
            self.joined = "\n".join(self.body.prompt)

        with it("should include prose from the taken branch"):
            expect("EXTRA_MARKER" in self.joined).to(be_true)

        with it("should omit prose from the untaken branch"):
            expect("ELSE_MARKER" in self.joined).to(equal(False))

        with it("should run a bare @agent_tool call"):
            expect(self.agent.ran).to(be_true)
            expect("RAN_OK" in self.joined).to(be_true)

    with context("when the other branch is taken"):
        with before.each:
            self.agent = _ExecBodyAgent()
            self.body = AgentInstructions.for_callable(_ExecBodyAgent.go, self.agent)
            self.joined = "\n".join(self.body.prompt)

        with it("should include prose from the else branch"):
            expect("ELSE_MARKER" in self.joined).to(be_true)


@agent_toolset
class _BrokenLineAgent:
    """A recipe whose lines read an attribute the toolset does not have."""

    @agent_instructions
    def branch_on_missing(self) -> str:
        """Branch on a flag the toolset does not have."""
        if self.missing_flag:
            "TAKEN_MARKER"
        else:
            "ELSE_MARKER"
        return "done"

    @agent_instructions
    def return_missing(self) -> str:
        """Return text the toolset does not have."""
        return self.missing_text


with description("an @agent_instructions body with a line that fails"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("with an if test that fails"):
        with before.each:
            self.body = AgentInstructions.for_callable(_BrokenLineAgent.branch_on_missing, _BrokenLineAgent())

        with it("should stop the expansion with a failed recipe line instead of taking the else branch"):
            expect(lambda: self.body.prompt).to(raise_error(RecipeLineFailed))

        with it("should name the recipe and the failing line's source"):
            expect(lambda: self.body.prompt).to(
                raise_error(RecipeLineFailed, contain("_BrokenLineAgent.branch_on_missing", "self.missing_flag"))
            )

        with it("should name the file line the failing line is on"):
            source_line = next(
                number for number, text in enumerate(Path(__file__).read_text(encoding="utf-8").splitlines(), 1)
                if text.strip() == "if self.missing_flag:"
            )
            expect(lambda: self.body.prompt).to(raise_error(RecipeLineFailed, contain(f":{source_line} ")))

    with context("with a return that fails"):
        with it("should stop the expansion instead of sending the return's source as instructions"):
            body = AgentInstructions.for_callable(_BrokenLineAgent.return_missing, _BrokenLineAgent())
            expect(lambda: body.expand({})).to(raise_error(RecipeLineFailed, contain("self.missing_text")))


with description("a cross-instance call whose provider cannot resolve"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with it("should fail the recipe line, naming the provider and its failure"):
        body = AgentInstructions.for_callable(
            _BrokenProvider.wrap, _BrokenProvider()
        )
        expect(lambda: body.tools).to(raise_error(RecipeLineFailed, contain("self.missing().finish_turn()", "no session")))


with description("AgentToolValidationError"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("when constructed without a line number"):
        with it("should format the message as class.action - message"):
            err = AgentToolValidationError(
                "self.foo is not allowed",
                class_name="MyClass",
                action_name="my_action",
            )
            expect("MyClass.my_action" in str(err)).to(be_true)

    with context("when constructed with a line number"):
        with it("should include the line number in the message"):
            err = AgentToolValidationError(
                "self.foo is not allowed",
                class_name="MyClass",
                action_name="my_action",
                lineno=42,
            )
            expect("line 42" in str(err)).to(be_true)

        with it("should expose class_name, action_name, and lineno attributes"):
            err = AgentToolValidationError(
                "msg",
                class_name="Cls",
                action_name="act",
                lineno=10,
            )
            expect(err.class_name).to(equal("Cls"))
            expect(err.action_name).to(equal("act"))
            expect(err.lineno).to(equal(10))



with description("AgentInstructions"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("the description property"):
        with it("should return the docstring text from the instruction callable"):
            story = CarStory()
            instruction = story.instructions["travelTo"]
            expect("Scripted trip" in instruction.description).to(be_true)

    with context("the tools property"):
        with it("should list deferred tool names from the @agent_instructions body"):
            story = CarStory()
            instruction = story.instructions["travelTo"]
            expect(instruction.tools).to(
                equal(["start", "accelerate", "decelerate", "stop", "speak"])
            )

    with context("AgentOperation.invoke"):
        with it("should call the bound @agent_tool method with argument dict only"):
            toolset = _ModeFixture()
            operation = toolset.operations["ping"]
            expect(operation.invoke({})).to(equal("pong"))


@agent_toolset
class _DestinationFixture:
    @mcp
    @_tool
    def ping(self) -> str:
        return "pong"

    @hook("stop")
    def on_stop(self, payload: dict) -> dict:
        return {}


with description("AgentToolSet destination catalog"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()


    with context("tools_for a destination"):

        with it("should return only members annotated for that destination"):
            toolset = _DestinationFixture()
            expect([tool.name for tool in toolset.tools_for(InstallDestination.MCP)]).to(
                equal(["ping"])
            )
            expect([tool.name for tool in toolset.tools_for(InstallDestination.HOOK)]).to(
                equal(["on_stop"])
            )

    with context("from_items"):

        with it("should instantiate a class once per type"):
            loaded = AgentToolSet.from_items([_DestinationFixture, _DestinationFixture()])
            expect(len(loaded)).to(equal(1))
            expect(type(loaded[0])).to(equal(_DestinationFixture))


@agent_toolset
class _BundleTools:
    def ping(self) -> str:
        return "pong"

    ping._hook = True
    ping._hook_name = "stop"


@agent_toolset
class _PropertyHost:
    @property
    @agent_instructions
    def instructions(self) -> str:
        return "hello"

    @property
    def bundle(self) -> _BundleTools:
        return _BundleTools()


@agent_toolset
class _NestedChild:
    @property
    def bundle(self) -> _BundleTools:
        return _BundleTools()


@toolset_collection
class _AnnotatedBag:
    pass


@agent_toolset
class _NestedParent:
    def __init__(self) -> None:
        self._kids = _AnnotatedBag()
        self._kids.entries["code"] = _NestedChild()

    @toolset_collection
    @property
    def kids(self) -> _AnnotatedBag:
        return self._kids


@agent_toolset
class _TwoCollections:
    def __init__(self) -> None:
        self._alpha = _AnnotatedBag()
        self._alpha.entries["code"] = _NestedChild()
        self._beta = _AnnotatedBag()
        self._beta.entries["extra"] = _NestedChild()

    @toolset_collection
    @property
    def alpha(self) -> _AnnotatedBag:
        return self._alpha

    @toolset_collection
    @property
    def beta(self) -> _AnnotatedBag:
        return self._beta


class _CollectChild:
    def __init__(self, name: str, overview: str, bag: dict | None = None) -> None:
        self.name = name
        self.overview = overview
        self.bag = bag or {}


class _WrappedBag:
    def __init__(self, entries: dict, parent=None) -> None:
        self.entries = entries
        self.parent = parent


@toolset_collection
class _CollectBag:
    @collect
    @agent_instructions
    def overview(self) -> str: ...

    @collect
    def bag(self) -> _WrappedBag: ...


with description("a class annotated as a toolset collection"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with it("should be a ToolSetCollection without subclassing it"):
        bag = _AnnotatedBag()
        bag.entries["code"] = object()
        expect(isinstance(bag, ToolSetCollection)).to(equal(True))
        expect(ToolSetCollectionAnnotation.annotates(type(bag))).to(equal(True))

    with it("should attach the collection to the instance"):
        host = type("Host", (), {})()
        host.bag = _AnnotatedBag()
        replacement = _AnnotatedBag()
        replacement.attach(host)
        expect(host.bag is replacement).to(equal(True))
        expect(replacement.parent).to(equal(host))


with description("a toolset collection with collected child properties"):
    with after.each:
        ThrowawayProject.close_all()

    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()
        self.bag = _CollectBag()
        self.bag.entries["one"] = _CollectChild("one", "first overview", {"a": 1})
        self.bag.entries["two"] = _CollectChild("two", "second overview", {"b": 2})

    with it("should join each child's string property"):
        expect(self.bag.overview).to(equal("first overview\n\nsecond overview"))

    with it("should wrap each child's collection-typed property under the child key"):
        expect(self.bag.bag.entries["one"]).to(equal({"a": 1}))
        expect(self.bag.bag.parent).to(equal(self.bag))

    with it("should keep other annotations on the collected property"):
        expect("overview" in self.bag.tools).to(equal(True))


with description("a toolset that exposes annotated properties and child collections"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("with an @agent_instructions property"):
        with it("should enroll the property getter on tools"):
            expect("instructions" in _PropertyHost().tools).to(equal(True))

    with context("with a property whose type is a toolset"):
        with it("should re-host the collection tools on the parent"):
            host = _PropertyHost()
            expect("ping" in host.tools).to(equal(True))
            expect(host.tools["ping"].toolset).to(equal(host))

    with context("with a nested toolset that holds a collection"):
        with it("should prefix the nested collection tools with the nest key"):
            expect("code.ping" in _NestedParent().tools).to(equal(True))

    with context("with properties annotated as toolset collections"):
        with it("should treat each annotated property as its own collection"):
            host = _TwoCollections()
            expect(host.toolset_collections).to(equal([host.alpha, host.beta]))
            expect(list(host.child_toolsets())).to(
                equal([host.alpha.entries["code"], host.beta.entries["extra"]])
            )
            expect("code.ping" in host.tools).to(equal(True))
            expect("extra.ping" in host.tools).to(equal(True))



@agent_toolset
class Parcel:
    """A parcel in a depot."""

    def __init__(self, label: str, depot: str) -> None:
        self.label = label
        self.depot = depot

    @classmethod
    @tool_subject
    def load(cls, parcel: str) -> "Parcel":
        return cls(parcel, "north")

    @classmethod
    @_tool
    def receive(cls, label: str) -> str:
        return f"received {label}"

    @_tool
    def forward(self, destination: str = "south") -> str:
        return f"{self.label} from {self.depot} to {destination}"


@agent_toolset
class Crate:
    """A crate in the project a call works on."""

    def __init__(self, label: str, project: Path) -> None:
        self.label = label
        self.project = project

    @classmethod
    @tool_subject
    def load(cls, crate: str, *, project: Path) -> "Crate":
        return cls(crate, Path(project))

    @classmethod
    @_tool
    def pack(cls, label: str, *, project: Path) -> str:
        return f"{label} packed in {Path(project).name}"

    @_tool
    def ship(self) -> str:
        return f"{self.label} shipped from {self.project.name}"

    @_tool
    def stack_on(self, other: "Crate | None" = None) -> str:
        if other is None:
            return f"{self.label} on the floor of {self.project.name}"
        return f"{self.label} on {other.label} in {other.project.name}"


@agent_toolset
class Pallet:
    """A pallet loaded for the chat a call came from."""

    def __init__(self, label: str, chat: str) -> None:
        self.label = label
        self.chat = chat

    @classmethod
    @tool_subject
    def load(cls, pallet: str, *, call: ToolCall) -> "Pallet":
        return cls(pallet, call.chat.id if call.chat is not None else "no chat")

    @_tool
    def lift(self) -> str:
        return f"{self.label} lifted for {self.chat}"


with description("a domain class whose constructor takes collaborators"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("that annotates a @tool_subject loader"):
        with it("should build as a toolset with no arguments"):
            expect(AgentToolSet.instantiate(Parcel).tools).to(have_key("forward"))

        with it("should take the loader's argument before the operation's own"):
            forward = AgentToolSet.instantiate(Parcel).tools["forward"]
            expect(list(forward.parameter_schema.names)).to(equal(["parcel", "destination"]))

        with it("should run the operation on the object the call names"):
            forward = AgentToolSet.instantiate(Parcel).tools["forward"]
            expect(forward.callable(parcel="box-1", destination="west")).to(equal("box-1 from north to west"))

        with it("should leave a classmethod tool to take only its own arguments"):
            receive = AgentToolSet.instantiate(Parcel).tools["receive"]
            expect(list(receive.parameter_schema.names)).to(equal(["label"]))

    with context("whose loader takes the project the call works on"):
        with before.each:
            self.project = ThrowawayProject().root

        with it("should leave the project out of the tool's arguments, since no caller passes it"):
            ship = AgentToolSet.instantiate(Crate).tools["ship"]
            expect(list(ship.parameter_schema.names)).to(equal(["crate"]))

        with it("should load the object from the project the call works on"):
            ship = AgentToolSet.instantiate(Crate).tools["ship"]
            expect(ship.invoke({"crate": "crate-1"}, project=self.project)).to(equal(f"crate-1 shipped from {self.project.name}"))

        with context("with a call that names no project"):
            with it("should refuse to load the object"):
                ship = AgentToolSet.instantiate(Crate).tools["ship"]
                expect(lambda: ship.invoke({"crate": "crate-1"})).to(raise_error(CallNamesNoProject))

        with context("with a classmethod tool that takes the project too"):
            with it("should leave the project out of its arguments"):
                pack = AgentToolSet.instantiate(Crate).tools["pack"]
                expect(list(pack.parameter_schema.names)).to(equal(["label"]))

            with it("should hand it the project the call works on"):
                pack = AgentToolSet.instantiate(Crate).tools["pack"]
                expect(pack.invoke({"label": "crate-2"}, project=self.project)).to(equal(f"crate-2 packed in {self.project.name}"))

        with context("with a tool that takes another crate"):
            with it("should take the other crate by name"):
                stack_on = AgentToolSet.instantiate(Crate).tools["stack_on"]
                expect(list(stack_on.parameter_schema.names)).to(equal(["crate", "other"]))

            with it("should hand the operation the crate that name loads, from the same project"):
                stack_on = AgentToolSet.instantiate(Crate).tools["stack_on"]
                expect(stack_on.invoke({"crate": "crate-1", "other": "crate-2"}, project=self.project)).to(
                    equal(f"crate-1 on crate-2 in {self.project.name}")
                )

            with it("should hand it no crate when the name is left out"):
                stack_on = AgentToolSet.instantiate(Crate).tools["stack_on"]
                expect(stack_on.invoke({"crate": "crate-1"}, project=self.project)).to(
                    equal(f"crate-1 on the floor of {self.project.name}")
                )

    with context("whose loader takes the call it serves"):
        with before.each:
            self.call = ToolCall.sent({"pallet": "pallet-1", "conversation_id": "chat-7"}, ThrowawayProject().root)
            self.lift = AgentToolSet.instantiate(Pallet).tools["lift"]

        with it("should leave the call out of the tool's arguments, since no caller passes it"):
            expect(list(self.lift.parameter_schema.names)).to(equal(["pallet"]))

        with it("should load the object with the chat the call came from"):
            expect(self.lift.answer(self.call)).to(equal("pallet-1 lifted for chat-7"))


with description("a toolset reference"):
    with context("to a module in a hyphenated folder under a folder on the import path"):
        with before.all:
            import tempfile

            self.root = Path(tempfile.mkdtemp(prefix="toolset-reference-spec-"))
            folder = self.root / "hyphen-tools"
            folder.mkdir()
            (folder / "found_tool.py").write_text(
                "from harness.agent_tools.agent_tools import agent_toolset\n\n\n"
                "@agent_toolset\nclass FoundTool:\n    \"\"\"A toolset kept in a hyphenated folder.\"\"\"\n",
                encoding="utf-8",
            )
            sys.path.insert(0, str(self.root))

        with after.all:
            sys.path.remove(str(self.root))
            sys.modules.pop("hyphen_tools.found_tool", None)

        with it("should load the toolset class its underscored module name names"):
            from harness.agent_tools.agent_tools import ToolsetReference

            expect(ToolsetReference("hyphen_tools.found_tool:FoundTool").toolset_class.__name__).to(equal("FoundTool"))

    with context("made from a toolset class"):
        with it("should name the class by its module and its own name"):
            from harness.agent_tools.agent_tools import ToolsetReference

            expect(str(ToolsetReference.of(CarStory))).to(equal(f"{CarStory.__module__}:CarStory"))


with description("a tool's MCP invoke line"):
    with it("should name the tool the installer reads back from it"):
        from harness.agent_tools.agent_tools import AgentTool

        tool = next(iter(AgentToolSet.instantiate(CarStory).tools.values()))
        expect(AgentTool.invoked_names(tool.invoke_line())).to(equal([tool.mcp_name]))


@agent_toolset
class FidelityProgress:
    """A toolset whose slug holds a hyphen, as fidelity-progress does."""

    @mcp
    @_tool
    def files(self) -> str:
        """The files a fidelity declares."""
        return ""


with description("a published tool asked whether a client's spelling names it"):
    with before.each:
        self.tool = AgentToolSet.instantiate(FidelityProgress).tools["files"]

    with it("should be published under its toolset's slug and its own name"):
        expect(self.tool.mcp_name).to(equal("fidelity-progress.files"))

    with it("should answer to its MCP name"):
        expect(self.tool.is_called("fidelity-progress.files")).to(be_true)

    with it("should answer to the underscore spelling Cursor sends"):
        expect(self.tool.is_called("fidelity-progress_files")).to(be_true)

    with it("should answer to its name with the hyphen written as an underscore"):
        expect(self.tool.is_called("fidelity_progress_files")).to(be_true)

    with it("should answer to the name a Claude Code hook gives it"):
        expect(self.tool.is_called("mcp__cdd__fidelity-progress_files")).to(be_true)

    with it("should answer in any case"):
        expect(self.tool.is_called("Fidelity-Progress_Files")).to(be_true)

    with it("should not answer to another tool's name"):
        expect(self.tool.is_called("fidelity-progress.report")).to(equal(False))

    with context("that a server has enrolled"):
        with before.each:
            from harness.mcp.mcp_server import McpServer

            self.server = McpServer(repo=Path(__file__).resolve().parents[2])
            self.server.enroll(self.tool)

        with it("should be the tool a call spelled with the hyphen as an underscore reaches"):
            expect(self.server.resolve_call_name("fidelity_progress_files")).to(equal("fidelity-progress.files"))

        with it("should be the tool a call spelled in another case reaches"):
            expect(self.server.resolve_call_name("Fidelity-Progress_Files")).to(equal("fidelity-progress.files"))


with description("the members of a practice's class asked which of them hold collections of tools"):
    with before.each:
        from cdd_guidance.practices.stories.stories import Stories

        self.stories = Stories()
        self.members = ToolsetMembers.of(Stories)

    with it("should find its shared rules on a practice of that class"):
        expect([name for name, _held in self.members.collections_on(self.stories)]).to(equal(["rules"]))

    with it("should name its fidelities as the toolset collection it holds"):
        expect(self.members.toolset_collection_names).to(equal(["fidelities"]))

    with it("should read which members can hold them once for the class"):
        expect(self.members.collection_names).to(be(ToolsetMembers.of(type(self.stories)).collection_names))
