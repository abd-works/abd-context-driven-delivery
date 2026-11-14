"""BDD spec for agent_bdd run requests and in-process toolset runs."""

import time
from contextvars import ContextVar
from pathlib import Path

from expects import be_true, equal, expect, raise_error
from mamba import after, before, context, description, it

from cdd_guidance.practices.agent_bdd.agent import agent
from cdd_guidance.practices.agent_bdd.agent_bdd_common import (
    AgentHarnessError,
    ToolRunDeadline,
    ToolsetInvoke,
    ToolRunTimedOut,
    ToolsRunYaml,
)
from space.session.sessions import Sessions
from space.session.throwaway_project import ThrowawayProject
import cdd_guidance.actions.sketch.sketch  # noqa: F401 - imported once here, not by the first run request that names it

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CALLING_PROJECT: ContextVar[str] = ContextVar("calling_project", default="")


def _slow_run() -> str:
    time.sleep(2)
    return "finished"


def _failing_run() -> str:
    raise KeyError("unknown tool")


with description("an agent spec file"):
    with context("with agent context manager"):
        with it("should enter and exit via __enter__ for in-chat harness"):
            session_file = _REPO_ROOT / "cdd_guidance" / "practices" / "agent_bdd" / ".agent_bdd_sessions" / "context-manager-spec.json"
            cm = agent(_REPO_ROOT, session_file, in_chat=True)
            block = cm.__enter__()
            try:
                expect(hasattr(block, "instruct")).to(be_true)
                expect(hasattr(block, "instruct_use_tool")).to(be_true)
            finally:
                cm.__exit__(None, None, None)

        with it("should strip prose after embedded run-request YAML in instruct_use_tool prompts"):
            prompt = (
                "Invoke this request:\n"
                "toolset: cdd_guidance.builders.create_practice_guidance._examples.car_chronicle.car_chronicle:CarChronicle\n"
                "action: repair\n"
                "Return the complete response.\n"
            )
            body = ToolsRunYaml().yaml_from_prompt(prompt)
            expect(body).to(equal("toolset: cdd_guidance.builders.create_practice_guidance._examples.car_chronicle.car_chronicle:CarChronicle\naction: repair"))

        with it("should not mistake python source for run output"):
            garbage = "lines = [f\"toolset: {invoke['toolset']}\", f\"action: {invoke['action']}\"]"
            expect(ToolsRunYaml().looks_like_tools_run_output(garbage)).to(equal(False))


with description("an in-process toolset run with a timeout"):
    with context("that finishes in time"):
        with it("should return what the run returned"):
            expect(ToolRunDeadline(5).run(lambda: "finished", "car")).to(equal("finished"))

        with it("should see the calling spec's context"):
            _CALLING_PROJECT.set("shop")
            expect(ToolRunDeadline(5).run(_CALLING_PROJECT.get, "car")).to(equal("shop"))

    with context("that fails"):
        with it("should raise the run's own error"):
            expect(lambda: ToolRunDeadline(5).run(_failing_run, "car")).to(raise_error(KeyError))

    with context("that outlives its timeout"):
        with it("should fail naming the timeout"):
            expect(lambda: ToolRunDeadline(0.01).run(_slow_run, "car")).to(raise_error(ToolRunTimedOut))


with description("a toolset run request") as self:
    with before.each:
        self.project = ThrowawayProject()
        Sessions(self.project.root).switch("checkout-flow")
        Sessions(self.project.root).switch("main")

    with after.each:
        self.project.close()

    with context("that names a session the project has"):
        with it("should make the toolset for that session, not the one the project has open"):
            invoke = ToolsetInvoke.create(
                {"toolset": "cdd_guidance.actions.sketch.sketch:Sketch", "action": "sketch", "session": "checkout-flow"},
                self.project.root,
            )
            expect(invoke.toolset.session.name).to(equal("checkout-flow"))

    with context("that names neither a tool nor an action"):
        with it("should be refused"):
            expect(lambda: ToolsetInvoke.for_toolset("pkg:Tool", self.project.root)).to(raise_error(ValueError))

    with context("that names both a tool and an action"):
        with it("should be refused"):
            expect(lambda: ToolsetInvoke.for_toolset("pkg:Tool", self.project.root, tool="scan", action="generate")).to(raise_error(ValueError))

    with context("that names an action the toolset does not have"):
        with it("should be refused when the run is made, naming the action"):
            request = {"toolset": "cdd_guidance.actions.sketch.sketch:Sketch", "action": "draw", "session": "checkout-flow"}
            expect(lambda: ToolsetInvoke.create(request, self.project.root)).to(raise_error(AgentHarnessError, "unknown action 'draw'"))

    with context("that names a session the project does not have"):
        with it("should fail naming that session"):
            request = {"toolset": "cdd_guidance.actions.sketch.sketch:Sketch", "action": "sketch", "session": "billing"}
            expect(lambda: ToolsetInvoke.create(request, self.project.root)).to(raise_error(AgentHarnessError, "request names session 'billing', which the project does not have"))

    with context("that names no project, while CDD_PROJECT names another"):
        with before.each:
            self.elsewhere = ThrowawayProject()

        with after.each:
            self.elsewhere.close()

        with it("should run in the project the spec gives it"):
            invoke = ToolsetInvoke.create(
                {"toolset": "cdd_guidance.actions.sketch.sketch:Sketch", "action": "sketch", "session": "checkout-flow"},
                self.project.root,
            )
            expect(invoke.toolset.session.name).to(equal("checkout-flow"))
