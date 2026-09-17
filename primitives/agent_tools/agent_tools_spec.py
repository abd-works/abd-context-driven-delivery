"""Non-agentic BDD for agent_tools — domain, recipe walk, and ToolsetRunner integration."""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("actions", None)

import yaml
from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from primitives.harness.errors import RunError
from agent_tools.examples.car import Car
from primitives.agent_tools.agent_tools import (
    AgentInstructions,
    tools,
    instructions,
    AgentToolValidationError,
    AgentToolSet,
    agent_instructions,
    agent_toolset,
)
from primitives.agent_tools.agent_tools import AgentInstructions
from primitives.harness.runner import InstructionRunRequest, InstructionRunner, ToolsetRunner
from car_story.car_story import CarStory
from agent_tools.examples.super_delegation.super_delegation_demo import (
    EmptySuperChild,
    EmptyWithReturn,
    ExplicitSuperChild,
    SuperBase,
)
from agent_bdd.yaml_fence import load_fenced
from agent_tools.agent_tools import AgentToolSet, agent_tool as _tool, tools, instructions


def car_instance(*, running: bool = False) -> Car:
    car = Car("Toyota", "Camry", 2024, "cheerful companion named Sunny")
    if running:
        car.start()
    return car


_CAR_TOOLSET_PATH = "agent_tools.examples.car:Car"


@agent_toolset
class _ModeFixture:
    @_tool
    def ping(self) -> str:
        """ping tool"""
        return "pong"

    @agent_instructions
    def run(recipe) -> str:
        """Run by calling ping."""
        "Run by calling ping."
        tools(recipe.toolset.ping())


@agent_toolset
class _SelfCallAgent:
    """Toolset whose own action calls another action on itself (same instance)."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(recipe) -> str:
        """Prepare the work carefully."""
        "SELF_PREPARE_MARKER: prepare the work carefully."
        tools(recipe.toolset.polish())
        return "prepared"

    @agent_instructions
    def finish(recipe) -> str:
        """May invoke prepare()."""
        "SELF_FINISH_MARKER: may invoke prepare()."
        instructions(recipe.toolset.prepare())
        return "finished"


@agent_toolset
class _BodyModeFlipAgent:
    """Same-instance nesting that flips mode mid-body instead of cloning itself."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(recipe) -> str:
        """Prepare the work carefully."""
        "SELF_PREPARE_MARKER: prepare the work carefully."
        tools(recipe.toolset.polish())
        return "prepared"

    @agent_instructions
    def finish(recipe) -> str:
        """Defer prepare via mid-body mode flip."""
        "SELF_FINISH_MARKER: defer prepare via mid-body mode flip."
        recipe.toolset.mode = "tool"
        instructions(recipe.toolset.prepare())
        return "finished"


@agent_toolset
class _CalleeAgent:
    """Companion agentic toolset invoked across instances."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(recipe) -> str:
        """Prepare the work carefully."""
        "CALLEE_PREPARE_MARKER: prepare the work carefully."
        tools(recipe.toolset.polish())
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
    def orchestrate(recipe) -> str:
        """May invoke helper().prepare()."""
        "CALLER_ORCHESTRATE_MARKER: may invoke helper().prepare()."
        instructions(recipe.toolset.helper().prepare())
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
    def orchestrate(recipe) -> str:
        """May invoke helper.prepare()."""
        "CALLER_ORCHESTRATE_MARKER: may invoke helper.prepare()."
        instructions(recipe.toolset.helper.prepare())
        return "orchestrated"


_CAR_TOOLSET = "practices.car.car:Car"
_CAR_STORY_TOOLSET = "car_story.car_story:CarStory"


with description("a class"):
    with context("with a toolset that declares @agent_instructions recipes"):
        with context("the travelTo action"):
            with it("should expose travelTo as an instructions recipe"):
                entry = CarStory().instructions["travelTo"]
                expect(entry.kind).to(equal("instructions"))

            with it("should expand into instructions when invoked through the command-line interface"):
                request = yaml.safe_dump(
                    {
                        "toolset": _CAR_STORY_TOOLSET,
                        "action": "travelTo",
                        "arguments": {
                            "tools": [
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
                        },
                    }
                )
                completed = subprocess.run(
                    [sys.executable, "-m", "harness", "run", "-"],
                    input=request,
                    capture_output=True,
                    text=True,
                    cwd=_REPO_ROOT,
                    check=False,
                )
                expect(completed.returncode).to(equal(0))
                response = load_fenced(completed.stdout)
                expect(response["ok"]).to(be_true)
                expect(response["action"]).to(equal("travelTo"))
                expect(response["result"]).to(
                    equal("Instructions for traveling to Hazzard County courthouse")
                )
                expect("{destination}" in response["instructions"]).to(be_true)
                expect("{conditions}" in response["instructions"]).to(be_true)
                expect(response["tools"]).to(
                    equal(["start", "accelerate", "decelerate", "stop", "speak"])
                )
                expect(response["arguments"]["destination"]).to(equal("Hazzard County courthouse"))

        with context("when expand makes tools available to the chat"):
            with it("should tell the AI to display those tools by name and purpose in the user-visible reply"):
                request = yaml.safe_dump(
                    {
                        "toolset": "agent_tools.examples.logged_probe:LoggedProbe",
                        "action": "narrate",
                        "arguments": {"message": "hello"},
                    }
                )
                completed = subprocess.run(
                    [sys.executable, "-m", "harness", "run", "-"],
                    input=request,
                    capture_output=True,
                    text=True,
                    cwd=_REPO_ROOT,
                    check=False,
                )
                expect(completed.returncode).to(equal(0))
                response = load_fenced(completed.stdout)
                expect(response["ok"]).to(be_true)
                instructions = response["instructions"]
                expect(
                    "display the tools made available to this chat in your user-visible reply"
                    in instructions
                ).to(be_true)
                expect("Do not only follow them silently" in instructions).to(be_true)
                expect("Tools made available:" in instructions).to(be_true)
                expect("- ping — Echo a message." in instructions).to(be_true)
                expect(response["tools"]).to(equal(["ping"]))


with description("an action"):
    with context("that has instructions with templating"):
        with context("with templated placeholders for a parameter"):
            with it("should put argument values into those instructions where {{param}} appears"):
                rendered = AgentInstructions.substitute_template(
                    "Go to {{destination}}",
                    {"destination": "town"},
                    {"destination"},
                )
                expect(rendered).to(equal("Go to town"))

        with context("with templated placeholders for an instance value"):
            with it("should put instance values into those instructions where {{self.attr}} appears"):
                car = Car(make="Dodge", model="Charger", year=1969, personality="General Lee")
                rendered = AgentInstructions.substitute_template(
                    "Drive the {{self.make}}",
                    {},
                    set(),
                    instance=car,
                )
                expect(rendered).to(equal("Drive the Dodge"))

        with context("with {} single-brace placeholders"):
            with it("should leave single-brace {Placeholder} text unchanged"):
                rendered = AgentInstructions.substitute_template(
                    "Fill {Placeholder} then go {{destination}}",
                    {"destination": "town"},
                    {"destination"},
                )
                expect(rendered).to(equal("Fill {Placeholder} then go town"))

        with context("with a missing {{name}}"):
            with it("should fail expand/run"):
                def _missing():
                    AgentInstructions.substitute_template("Go to {{destination}}", {}, {"destination"})

                raised = False
                try:
                    _missing()
                except ValueError as error:
                    raised = True
                    expect("destination" in str(error)).to(be_true)
                expect(raised).to(be_true)

    with context("that has templated string literals in the recipe body"):
        with it("should put {{param}} / {{self.attr}} values into expanded instructions"):
            from agent_tools.examples.templated_md import TemplatedMdDemo

            request = yaml.safe_dump(
                {
                    "toolset": "agent_tools.examples.templated_md:TemplatedMdDemo",
                    "context": {"label": "Desk"},
                    "action": "greet",
                    "arguments": {"name": "Pat"},
                }
            )
            completed = subprocess.run(
                [sys.executable, "-m", "harness", "run", "-"],
                input=request,
                capture_output=True,
                text=True,
                cwd=_REPO_ROOT,
                check=False,
            )
            expect(completed.returncode).to(equal(0))
            response = load_fenced(completed.stdout)
            expect(response["ok"]).to(be_true)
            expect("Greet Pat on behalf of Desk" in response["instructions"]).to(be_true)
            expect("{Placeholder}" in response["instructions"]).to(be_true)


with description("super() delegation in action bodies"):
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

        with it("should inherit the parent's result template"):
            child = EmptySuperChild()
            body = AgentInstructions.for_callable(EmptySuperChild.generate, child)
            expect(body.result_template).to(equal("generate done"))

    with context("a child with Ellipsis plus a custom return"):
        with it("should use the child's result template"):
            child = EmptyWithReturn()
            body = AgentInstructions.for_callable(EmptyWithReturn.generate, child)
            expect(body.result_template).to(equal("child result only"))

        with it("should still inline parent tool steps"):
            child = EmptyWithReturn()
            body = AgentInstructions.for_callable(EmptyWithReturn.generate, child)
            expect("do_work" in body.tools).to(be_true)


with description("AgentToolSet"):
    with context("on a live Car example instance"):
        with context("with a class-level description"):
            with it("should expose description matching the class docstring"):
                car = car_instance()
                expect(car.description).to(
                    equal("Operate a car \u2014 start, stop, and read current state.")
                )

        with context("with methods marked as @agent_tool"):
            with before.each:
                self.car = car_instance()

            with it("should register every marked method in operations"):
                expect(set(self.car.operations.keys())).to(
                    equal({"start", "stop", "drive", "accelerate", "decelerate", "speak"})
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

        with context("with observable state on the example Car"):
            with it("should expose current values on the instance"):
                car = car_instance()
                expect(car.make).to(equal("Toyota"))
                expect(car.model).to(equal("Camry"))
                expect(car.year).to(equal(2024))
                expect(car.personality).to(equal("cheerful companion named Sunny"))
                expect(car.running).to(equal(False))

    with context("through ToolsetRunner"):
        with it("should invoke a marked @agent_tool"):
            response = ToolsetRunner.instance().run_request(
                {
                    "toolset": _CAR_TOOLSET_PATH,
                    "context": {
                        "make": "Toyota",
                        "model": "Camry",
                        "year": 2024,
                        "personality": "cheerful companion named Sunny",
                    },
                    "tool": "start",
                }
            )
            expect(response["ok"]).to(be_true)
            expect(response["tool"]).to(equal("start"))

        with it("should require tool arguments declared on the operation"):
            try:
                ToolsetRunner.instance().run_request(
                    {
                        "toolset": _CAR_TOOLSET_PATH,
                        "context": {
                            "make": "Toyota",
                            "model": "Camry",
                            "year": 2024,
                            "personality": "cheerful companion named Sunny",
                        },
                        "tool": "drive",
                    }
                )
                expect(False).to(be_true)
            except RunError as exc:
                response = exc.response
            expect(response["error"]).to(equal("missing required arguments"))
            expect("miles" in response["missing"]).to(be_true)

        with it("should refuse missing required constructor context with an AskQuestion hint"):
            try:
                ToolsetRunner.instance().run_request(
                    {
                        "toolset": _CAR_TOOLSET_PATH,
                        "tool": "start",
                    }
                )
                expect(False).to(be_true)
            except RunError as exc:
                response = exc.response
            expect(response["ok"]).to(equal(False))
            expect(response["error"]).to(equal("missing required context"))
            expect("make" in response["missing"]).to(be_true)
            expect("AskQuestion" in response["detail"]).to(be_true)

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
    def prepare(recipe) -> str:
        """Prepare carefully."""
        "FOREACH_CALLEE_MARKER: prepare carefully."
        tools(recipe.toolset.polish())
        return "prepared"


@agent_toolset
class _ForEachCaller:
    def companions(self) -> list:
        return [_ForEachCallee(), _ForEachCallee()]

    @agent_instructions
    def orchestrate(recipe) -> str:
        """Defer each companion."""
        "FOREACH_CALLER_MARKER: defer each companion."
        for companion in recipe.toolset.companions():
            companion.mode = "tool"
            instructions(companion.prepare())
        return "orchestrated"

    @agent_instructions
    def inline_all(recipe) -> str:
        """Inline each companion."""
        "FOREACH_INLINE_MARKER: inline each companion."
        for companion in recipe.toolset.companions():
            instructions(companion.prepare())
        return "inlined"

    @agent_instructions
    def inline_bare(recipe) -> str:
        """Inline each companion via bare attribute."""
        "FOREACH_BARE_MARKER: inline each companion via bare attribute."
        for companion in recipe.toolset.companions():
            instructions(companion.prepare())
        return "inlined"

    @agent_instructions
    def with_self_step(recipe) -> str:
        """Walk self tools inside the loop."""
        "FOREACH_SELF_MARKER: walk self tools inside the loop."
        for companion in recipe.toolset.companions():
            instructions(companion.prepare())
            tools(recipe.toolset.note())
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
    def guidance(recipe) -> str:
        """Contexts live here."""
        "FOREACH_GUIDANCE_MARKER: contexts live here."
        return ""


@agent_toolset
class _ScanCaller:
    def companions(self) -> list:
        return [_HostWithScanner()]

    @agent_instructions
    def check(recipe) -> str:
        """Guidance then scan."""
        "FOREACH_SCAN_MARKER: guidance then scan."
        for host in recipe.toolset.companions():
            instructions(host.guidance())
            tools(host.scanner.scan())
        return "checked"


@agent_toolset
class _BrokenProvider:
    def missing(self):
        raise RuntimeError("no session")

    @agent_instructions
    def wrap(recipe) -> str:
        """BROKEN_PROVIDER_MARKER: still list the named tool."""
        tools(recipe.toolset.missing().finish_turn())
        return ""


with description("a for-each action over companion toolsets"):
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


with description("a cross-instance call whose provider cannot resolve"):
    with it("should still list the named tool"):
        body = AgentInstructions.for_callable(
            _BrokenProvider.wrap, _BrokenProvider()
        )
        expect("finish_turn" in body.tools).to(be_true)


with description("AgentToolValidationError"):
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
    with context("the description property"):
        with it("should return the docstring text from the instruction callable"):
            story = CarStory()
            instruction = story.instructions["travelTo"]
            expect("Scripted trip" in instruction.description).to(be_true)

    with context("the tools property"):
        with it("should list deferred tool names from the recipe body"):
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

