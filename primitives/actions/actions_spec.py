"""BDD spec for action.py - @agent_instructions expansion via CLI."""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("actions", None)

import yaml
from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import (
    Action,
    ActionValidationError,
    AgenticToolset,
    _ActionExpander,
    agent_instructions,
    agentic_toolset,
)
from primitives.actions.examples.car import Car
from primitives.actions.examples.super_delegation import (
    EmptySuperChild,
    EmptyWithReturn,
    ExplicitSuperChild,
    SuperBase,
)
from agent_bdd.yaml_fence import load_fenced
from tools.tool import agent_tool as _tool


@agentic_toolset
class _ModeFixture:
    @_tool
    def ping(self) -> str:
        """ping tool"""
        return "pong"

    @agent_instructions
    def run(self) -> str:
        """Run by calling ping."""
        self.ping()


@agentic_toolset
class _SelfCallAgent:
    """Toolset whose own action calls another action on itself (same instance)."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """SELF_PREPARE_MARKER: prepare the work carefully."""
        self.polish()
        return "prepared"

    @agent_instructions
    def finish(self) -> str:
        """SELF_FINISH_MARKER: may invoke prepare()."""
        self.prepare()
        return "finished"


@agentic_toolset
class _BodyModeFlipAgent:
    """Same-instance nesting that flips mode mid-body instead of cloning itself."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """SELF_PREPARE_MARKER: prepare the work carefully."""
        self.polish()
        return "prepared"

    @agent_instructions
    def finish(self) -> str:
        """SELF_FINISH_MARKER: defer prepare via mid-body mode flip."""
        self.mode = "tool"
        self.prepare()
        return "finished"


@agentic_toolset
class _CalleeAgent:
    """Companion agentic toolset invoked across instances."""

    @_tool
    def polish(self) -> str:
        """Polish the work product."""
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """CALLEE_PREPARE_MARKER: prepare the work carefully."""
        self.polish()
        return "prepared"


@agentic_toolset
class _CallerAgent:
    """Caller that expands a cross-instance action on a companion."""

    def __init__(self, helper: _CalleeAgent | None = None) -> None:
        self._helper = helper if helper is not None else _CalleeAgent()
        super().__init__()

    def helper(self) -> _CalleeAgent:
        return self._helper

    @agent_instructions
    def orchestrate(self) -> str:
        """CALLER_ORCHESTRATE_MARKER: may invoke helper().prepare()."""
        self.helper().prepare()
        return "orchestrated"


@agentic_toolset
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
        """CALLER_ORCHESTRATE_MARKER: may invoke helper.prepare()."""
        self.helper.prepare()
        return "orchestrated"


_CAR_TOOLSET = "primitives.actions.examples.car:Car"


with description("a class"):
    with context("with a toolset that declares @agent_instructions recipes"):
        with context("the travelTo action"):
            with it("should appear in the manifest with kind action and referenced tools"):
                entry = Car.manifest.signature["travelTo"]
                expect(entry["kind"]).to(equal("action"))
                expect(entry["tools"]).to(
                    equal(["start", "accelerate", "decelerate", "stop", "speak"])
                )

            with it("should expand into instructions when invoked through the command-line interface"):
                request = yaml.safe_dump(
                    {
                        "toolset": _CAR_TOOLSET,
                        "context": {
                            "make": "Dodge",
                            "model": "Charger",
                            "year": 1969,
                            "personality": "General Lee",
                        },
                        "action": "travelTo",
                        "arguments": {
                            "destination": "Hazzard County courthouse",
                            "conditions": "muddy back roads",
                        },
                    }
                )
                completed = subprocess.run(
                    [sys.executable, "-m", "tools", "run", "-"],
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
                expect("Hazzard County courthouse" in response["instructions"]).to(be_true)
                expect("muddy back roads" in response["instructions"]).to(be_true)
                expect("Dodge" in response["instructions"]).to(be_true)
                expect("Charger" in response["instructions"]).to(be_true)
                expect(response["tools"]).to(
                    equal(["start", "accelerate", "decelerate", "stop", "speak"])
                )
                expect(response["arguments"]["destination"]).to(equal("Hazzard County courthouse"))


with description("an action"):
    with context("that has instructions with templating"):
        with context("with templated placeholders for a parameter"):
            with it("should put argument values into those instructions where {{param}} appears"):
                expander = _ActionExpander.instance()
                rendered = expander._substitute(
                    "Go to {{destination}}",
                    {"destination": "town"},
                    {"destination"},
                )
                expect(rendered).to(equal("Go to town"))

        with context("with templated placeholders for an instance value"):
            with it("should put instance values into those instructions where {{self.attr}} appears"):
                car = Car("Dodge", "Charger", 1969, "General Lee")
                expander = _ActionExpander.instance()
                rendered = expander._substitute(
                    "Drive the {{self.make}}",
                    {},
                    set(),
                    instance=car,
                )
                expect(rendered).to(equal("Drive the Dodge"))

        with context("with {} single-brace placeholders"):
            with it("should leave single-brace {Placeholder} text unchanged"):
                expander = _ActionExpander.instance()
                rendered = expander._substitute(
                    "Fill {Placeholder} then go {{destination}}",
                    {"destination": "town"},
                    {"destination"},
                )
                expect(rendered).to(equal("Fill {Placeholder} then go town"))

        with context("with a missing {{name}}"):
            with it("should fail expand/run"):
                expander = _ActionExpander.instance()

                def _missing():
                    expander._substitute("Go to {{destination}}", {}, {"destination"})

                raised = False
                try:
                    _missing()
                except ValueError as error:
                    raised = True
                    expect("destination" in str(error)).to(be_true)
                expect(raised).to(be_true)

    with context("that has instructions loaded from an md file with templating"):
        with it("should put {{param}} / {{self.attr}} values into the loaded md instructions"):
            from primitives.actions.examples.templated_md import TemplatedMdDemo

            request = yaml.safe_dump(
                {
                    "toolset": "primitives.actions.examples.templated_md:TemplatedMdDemo",
                    "context": {"label": "Desk"},
                    "action": "greet",
                    "arguments": {"name": "Pat"},
                }
            )
            completed = subprocess.run(
                [sys.executable, "-m", "tools", "run", "-"],
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
            body = _ActionExpander.instance().parse_body(ExplicitSuperChild.generate, child)
            joined = "\n".join(body.prose_parts)
            expect("Base generate instructions" in joined).to(be_true)

        with it("should include tool steps from the parent action"):
            child = ExplicitSuperChild()
            body = _ActionExpander.instance().parse_body(ExplicitSuperChild.generate, child)
            expect("do_work" in body.tool_steps).to(be_true)


with description("empty-body auto-super in action bodies"):
    with context("a child whose generate body is only Ellipsis"):
        with it("should inline the parent's prose"):
            child = EmptySuperChild()
            body = _ActionExpander.instance().parse_body(EmptySuperChild.generate, child)
            joined = "\n".join(body.prose_parts)
            expect("Base generate instructions" in joined).to(be_true)

        with it("should include tool steps from the parent action"):
            child = EmptySuperChild()
            body = _ActionExpander.instance().parse_body(EmptySuperChild.generate, child)
            expect("do_work" in body.tool_steps).to(be_true)

        with it("should inherit the parent's result template"):
            child = EmptySuperChild()
            body = _ActionExpander.instance().parse_body(EmptySuperChild.generate, child)
            expect(body.result_template).to(equal("generate done"))

    with context("a child with Ellipsis plus a custom return"):
        with it("should use the child's result template"):
            child = EmptyWithReturn()
            body = _ActionExpander.instance().parse_body(EmptyWithReturn.generate, child)
            expect(body.result_template).to(equal("child result only"))

        with it("should still inline parent tool steps"):
            child = EmptyWithReturn()
            body = _ActionExpander.instance().parse_body(EmptyWithReturn.generate, child)
            expect("do_work" in body.tool_steps).to(be_true)


with description("AgenticToolset"):
    with context("the mode resource"):
        with it("should default to 'action'"):
            instance = _ModeFixture()
            expect(instance.mode).to(equal("action"))

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
        with context("and the companion mode is action"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "action"
                self.caller = _CallerAgent(self.callee)
                self.body = _ActionExpander.instance().parse_body(
                    _CallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prose_parts)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(be_true)

            with it("should include the companion's inner tools in the expansion"):
                expect("polish" in self.body.tool_steps).to(be_true)

            with it("should not list the companion action itself as a deferred tool"):
                expect("prepare" in self.body.tool_steps).to(equal(False))

        with context("and the companion mode is tool"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "tool"
                self.caller = _CallerAgent(self.callee)
                self.body = _ActionExpander.instance().parse_body(
                    _CallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prose_parts)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should not inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(equal(False))

            with it("should list the companion action in the expansion tools"):
                expect("prepare" in self.body.tool_steps).to(be_true)

            with it("should not expose the companion's inner tools until that action runs"):
                expect("polish" in self.body.tool_steps).to(equal(False))

    with context("when a caller reaches a companion via a plain property (not a method call)"):
        with context("and the companion mode is action"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "action"
                self.caller = _PropertyCallerAgent(self.callee)
                self.body = _ActionExpander.instance().parse_body(
                    _PropertyCallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prose_parts)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(be_true)

            with it("should include the companion's inner tools in the expansion"):
                expect("polish" in self.body.tool_steps).to(be_true)

            with it("should not list the companion action itself as a deferred tool"):
                expect("prepare" in self.body.tool_steps).to(equal(False))

        with context("and the companion mode is tool"):
            with before.each:
                self.callee = _CalleeAgent()
                self.callee.mode = "tool"
                self.caller = _PropertyCallerAgent(self.callee)
                self.body = _ActionExpander.instance().parse_body(
                    _PropertyCallerAgent.orchestrate, self.caller
                )
                self.joined = "\n".join(self.body.prose_parts)

            with it("should keep the caller's own instructions"):
                expect("CALLER_ORCHESTRATE_MARKER" in self.joined).to(be_true)

            with it("should not inline the companion action's instructions"):
                expect("CALLEE_PREPARE_MARKER" in self.joined).to(equal(False))

            with it("should list the companion action in the expansion tools"):
                expect("prepare" in self.body.tool_steps).to(be_true)

            with it("should not expose the companion's inner tools until that action runs"):
                expect("polish" in self.body.tool_steps).to(equal(False))

    with context("when a toolset instance's own action calls another action on itself"):
        with context("and its own mode is action"):
            with before.each:
                self.instance = _SelfCallAgent()
                self.instance.mode = "action"
                self.body = _ActionExpander.instance().parse_body(
                    _SelfCallAgent.finish, self.instance
                )
                self.joined = "\n".join(self.body.prose_parts)

            with it("should keep the caller's own instructions"):
                expect("SELF_FINISH_MARKER" in self.joined).to(be_true)

            with it("should inline the nested self-action's instructions"):
                expect("SELF_PREPARE_MARKER" in self.joined).to(be_true)

            with it("should include the nested action's inner tools in the expansion"):
                expect("polish" in self.body.tool_steps).to(be_true)

            with it("should not list the nested action itself as a deferred tool"):
                expect("prepare" in self.body.tool_steps).to(equal(False))

        with context("and its own mode is tool"):
            with before.each:
                self.instance = _SelfCallAgent()
                self.instance.mode = "tool"
                self.body = _ActionExpander.instance().parse_body(
                    _SelfCallAgent.finish, self.instance
                )
                self.joined = "\n".join(self.body.prose_parts)

            with it("should keep the caller's own instructions"):
                expect("SELF_FINISH_MARKER" in self.joined).to(be_true)

            with it("should not inline the nested self-action's instructions"):
                expect("SELF_PREPARE_MARKER" in self.joined).to(equal(False))

            with it("should list the nested action in the expansion tools"):
                expect("prepare" in self.body.tool_steps).to(be_true)

            with it("should not expose the nested action's inner tools until that action runs"):
                expect("polish" in self.body.tool_steps).to(equal(False))

    with context("when a toolset flips self.mode mid-body before a nested self-action"):
        with before.each:
            self.instance = _BodyModeFlipAgent()
            self.body = _ActionExpander.instance().parse_body(
                _BodyModeFlipAgent.finish, self.instance
            )
            self.joined = "\n".join(self.body.prose_parts)

        with it("should keep the caller's own instructions"):
            expect("SELF_FINISH_MARKER" in self.joined).to(be_true)

        with it("should not inline the nested self-action's instructions"):
            expect("SELF_PREPARE_MARKER" in self.joined).to(equal(False))

        with it("should list the nested action in the expansion tools"):
            expect("prepare" in self.body.tool_steps).to(be_true)

        with it("should restore mode to action after the walk"):
            expect(self.instance.mode).to(equal("action"))


@agentic_toolset
class _ForEachCallee:
    @_tool
    def polish(self) -> str:
        return "polished"

    @agent_instructions
    def prepare(self) -> str:
        """FOREACH_CALLEE_MARKER: prepare carefully."""
        self.polish()
        return "prepared"


@agentic_toolset
class _ForEachCaller:
    def companions(self) -> list:
        return [_ForEachCallee(), _ForEachCallee()]

    @agent_instructions
    def orchestrate(self) -> str:
        """FOREACH_CALLER_MARKER: defer each companion."""
        for companion in self.companions():
            companion.mode = "tool"
            companion.prepare()
        return "orchestrated"

    @agent_instructions
    def inline_all(self) -> str:
        """FOREACH_INLINE_MARKER: inline each companion."""
        for companion in self.companions():
            companion.prepare()
        return "inlined"


with description("a for-each action over companion toolsets"):
    with context("when each companion is flipped to tool mode in the loop"):
        with before.each:
            self.body = _ActionExpander.instance().parse_body(
                _ForEachCaller.orchestrate, _ForEachCaller()
            )
            self.joined = "\n".join(self.body.prose_parts)

        with it("should keep the caller marker"):
            expect("FOREACH_CALLER_MARKER" in self.joined).to(be_true)

        with it("should not inline companion action instructions"):
            expect("FOREACH_CALLEE_MARKER" in self.joined).to(equal(False))

        with it("should list prepare as a deferred tool"):
            expect("prepare" in self.body.tool_steps).to(be_true)

        with it("should emit a separate-tools-run hint for deferred companions"):
            # Identical toolset+action hints dedupe; still one deferred prepare step.
            expect(self.joined.count("Separate tools run")).to(equal(1))
            expect("prepare" in self.body.tool_steps).to(be_true)

    with context("when companions stay in action mode"):
        with before.each:
            self.body = _ActionExpander.instance().parse_body(
                _ForEachCaller.inline_all, _ForEachCaller()
            )
            self.joined = "\n".join(self.body.prose_parts)

        with it("should inline companion action instructions"):
            expect("FOREACH_CALLEE_MARKER" in self.joined).to(be_true)


with description("ActionValidationError"):
    with context("when constructed without a line number"):
        with it("should format the message as class.action - message"):
            err = ActionValidationError(
                "self.foo is not allowed",
                class_name="MyClass",
                action_name="my_action",
            )
            expect(str(err)).to(equal("MyClass.my_action - self.foo is not allowed"))

    with context("when constructed with a line number"):
        with it("should include the line number in the message"):
            err = ActionValidationError(
                "self.foo is not allowed",
                class_name="MyClass",
                action_name="my_action",
                lineno=42,
            )
            expect(str(err)).to(equal("MyClass.my_action:42 - self.foo is not allowed"))

        with it("should expose class_name, action_name, and lineno attributes"):
            err = ActionValidationError(
                "msg",
                class_name="Cls",
                action_name="act",
                lineno=10,
            )
            expect(err.class_name).to(equal("Cls"))
            expect(err.action_name).to(equal("act"))
            expect(err.lineno).to(equal(10))


with description("Action"):
    with context("the instructions property"):
        with it("should return the docstring text from the action callable"):
            car = Car("Ford", "Mustang", 1965, "Pony")
            action_obj = car.actions["travelTo"]
            expect("interesting story" in action_obj.instructions).to(be_true)

    with context("the signature_entry property"):
        with it("should return a dict with kind 'action' and the tool list"):
            car = Car("Ford", "Mustang", 1965, "Pony")
            action_obj = car.actions["travelTo"]
            entry = action_obj.signature_entry
            expect(entry["kind"]).to(equal("action"))
            expect(entry["tools"]).to(equal(["start", "accelerate", "decelerate", "stop", "speak"]))

    with context("the add_to_signature method"):
        with it("should insert the entry under the action name in the given signature dict"):
            car = Car("Ford", "Mustang", 1965, "Pony")
            action_obj = car.actions["travelTo"]
            sig = {}
            action_obj.add_to_signature(sig)
            expect("travelTo" in sig).to(be_true)
            expect(sig["travelTo"]["kind"]).to(equal("action"))


@agentic_toolset
class _ContextToolsKit:
    @agent_instructions
    def run(self) -> str:
        return "done"


with description("an AgenticToolset"):
    with context("that is given context tools"):
        with it("should return an already-loaded instance unchanged"):
            kit = _ContextToolsKit()
            host = object()
            expect(kit.context_tool(host)).to(equal(host))

        with it("should resolve a list of instances via context_tools"):
            kit = _ContextToolsKit()
            first, second = object(), object()
            expect(kit.context_tools([first, second])).to(equal([first, second]))

