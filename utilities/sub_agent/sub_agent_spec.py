"""BDD spec for utilities/sub_agent/sub_agent.py — SubAgentTool + discover helpers.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, equal, expect
from mamba import before, context, description, it

from tools.tool import agent_tool as _tool
from utilities.sub_agent.sub_agent import (
    SubAgent,
    SubAgentTool,
    discover_sub_agent_tools,
    sub_agent,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _WithSubAgent:
    """Toolset fixture that has one @sub_agent-decorated method with instructions."""

    @sub_agent
    @_tool
    def diagnose(self) -> str:
        """Run a deep diagnostic sweep and return a summary."""


class _WithSubAgentAndParams:
    """Toolset fixture that has one @sub_agent method with parameters."""

    @sub_agent
    @_tool
    def analyse(self, target: str, depth: int) -> str:
        """Analyse the named target at the given depth."""


class _WithSubAgentNoDoc:
    """Toolset fixture whose @sub_agent method has no docstring."""

    @sub_agent
    @_tool
    def silent_task(self) -> None:
        pass


class _WithNoSubAgent:
    """Toolset fixture with no @sub_agent methods."""

    @_tool
    def ping(self) -> str:
        """Regular tool, not a sub-agent."""


# ---------------------------------------------------------------------------
# BDD hierarchy
# ---------------------------------------------------------------------------


with description("a sub_agent-decorated method"):
    with context("that is applied to a tool method"):
        with it("should mark the function with _is_sub_agent as True"):
            # Arrange / Act — marker set at class-definition time
            # Assert
            expect(getattr(_WithSubAgent.diagnose, "_is_sub_agent", False)).to(be_true)

        with it("should suppress the tool marker so standard tool discovery skips it"):
            # Arrange / Act
            # Assert
            expect(getattr(_WithSubAgent.diagnose, "_is_agent_tool", True)).to(equal(False))


with description("a SubAgentTool"):
    with context("that is created with a name and a callable with a docstring"):
        with before.each:
            self.tool = SubAgentTool(
                name="diagnose",
                callable=_WithSubAgent().diagnose,
            )

        with it("should store the name as given"):
            # Assert
            expect(self.tool.name).to(equal("diagnose"))

        with it("should return the docstring text as instructions"):
            # Assert
            expect("diagnostic sweep" in self.tool.instructions).to(be_true)

    with context("that is created with a callable without a docstring"):
        with before.each:
            self.tool = SubAgentTool(
                name="silent_task",
                callable=_WithSubAgentNoDoc().silent_task,
            )

        with it("should return an empty string as instructions"):
            # Assert
            expect(self.tool.instructions).to(equal(""))

    with context("that builds a signature entry"):
        with context("with a callable that has a docstring"):
            with before.each:
                self.entry = SubAgentTool(
                    name="diagnose",
                    callable=_WithSubAgent().diagnose,
                ).signature_entry

            with it("should set kind to sub_agent"):
                expect(self.entry["kind"]).to(equal("sub_agent"))

            with it("should set launch to non_blocking"):
                expect(self.entry["launch"]).to(equal("non_blocking"))

            with it("should include instructions in the entry"):
                expect("instructions" in self.entry).to(be_true)
                expect("diagnostic sweep" in self.entry["instructions"]).to(be_true)

        with context("with a callable without a docstring"):
            with before.each:
                self.entry = SubAgentTool(
                    name="silent_task",
                    callable=_WithSubAgentNoDoc().silent_task,
                ).signature_entry

            with it("should omit instructions from the entry"):
                expect("instructions" in self.entry).to(equal(False))

        with context("with a callable that has parameters"):
            with before.each:
                self.entry = SubAgentTool(
                    name="analyse",
                    callable=_WithSubAgentAndParams().analyse,
                ).signature_entry

            with it("should include parameters in the entry"):
                expect("parameters" in self.entry).to(be_true)
                expect("target" in self.entry["parameters"]).to(be_true)
                expect("depth" in self.entry["parameters"]).to(be_true)

            with it("should include returns in the entry"):
                expect("returns" in self.entry).to(be_true)
                expect(self.entry["returns"]).to(equal("str"))

        with context("with a callable that has no parameters"):
            with before.each:
                self.entry = SubAgentTool(
                    name="diagnose",
                    callable=_WithSubAgent().diagnose,
                ).signature_entry

            with it("should omit parameters from the entry when none are declared"):
                expect("parameters" in self.entry).to(equal(False))

    with context("that adds itself to a signature dict"):
        with it("should insert the entry under its own name"):
            # Arrange
            sig: dict = {}
            tool_obj = SubAgentTool(name="diagnose", callable=_WithSubAgent().diagnose)
            # Act
            tool_obj.add_to_signature(sig)
            # Assert
            expect("diagnose" in sig).to(be_true)
            expect(sig["diagnose"]["kind"]).to(equal("sub_agent"))


with description("discover_sub_agent_tools"):
    with context("called on an instance that has @sub_agent methods"):
        with before.each:
            self.instance = _WithSubAgent()
            self.result = discover_sub_agent_tools(self.instance)

        with it("should return a dict containing a SubAgentTool for each marked method"):
            expect(len(self.result)).to(equal(1))
            expect(self.result["diagnose"]).to(be_a(SubAgentTool))

        with it("should key each SubAgentTool by the method name"):
            expect("diagnose" in self.result).to(be_true)
            expect(self.result["diagnose"].name).to(equal("diagnose"))

    with context("called on an instance with no @sub_agent methods"):
        with it("should return an empty dict"):
            # Arrange
            instance = _WithNoSubAgent()
            # Act
            result = discover_sub_agent_tools(instance)
            # Assert
            expect(result).to(equal({}))


with description("SubAgent.run"):
    with context("that is stacked the same way as other @sub_agent tools"):
        with it("should mark run as a sub_agent"):
            expect(getattr(SubAgent.run, "_is_sub_agent", False)).to(be_true)

        with it("should mark run as an action"):
            expect(getattr(SubAgent.run, "_is_agent_instructions", False)).to(be_true)

        with it("should suppress the tool marker so standard tool discovery skips it"):
            expect(getattr(SubAgent.run, "_is_agent_tool", True)).to(equal(False))

        with it("should publish kind sub_agent and launch non_blocking"):
            entry = discover_sub_agent_tools(SubAgent())["run"].signature_entry
            expect(entry["kind"]).to(equal("sub_agent"))
            expect(entry["launch"]).to(equal("non_blocking"))

        with it("should take context tools, optional other actions, and an optional task prompt"):
            params = discover_sub_agent_tools(SubAgent())["run"].signature_entry["parameters"]
            expect("tools" in params).to(be_true)
            expect("actions" in params).to(be_true)
            expect("prompt" in params).to(be_true)

        with it("should not expose lifecycle begin or end"):
            sig = SubAgent.manifest.signature
            expect("begin" in sig).to(equal(False))
            expect("end" in sig).to(equal(False))
            expect("open_workspace" in sig).to(equal(False))

    with context("when actions are listed"):
        with it("should keep listed action kits unwrapped by performTurn"):
            text = discover_sub_agent_tools(SubAgent())["run"].instructions
            expect("Do not wrap those in performTurn" in text).to(be_true)

    with context("when actions are missing or empty"):
        with it("should name performTurn around the listed context-tool work"):
            text = discover_sub_agent_tools(SubAgent())["run"].instructions
            expect("action: performTurn" in text).to(be_true)
            expect("finish_turn" in text).to(be_true)
            expect("report branch" in text).to(be_true)


    with context("when a session model is configured"):
        with it("should instruct reading sessions model and passing it on launch"):
            text = discover_sub_agent_tools(SubAgent())["run"].instructions
            expect("sessions" in text and "model" in text).to(be_true)
            expect("disable-model-invocation" in text).to(be_true)
