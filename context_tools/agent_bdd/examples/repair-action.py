"""
# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
"""
# @agent-spec-manifest python -m tools agent-spec context_tools/agent_bdd/examples/repair-action.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: context_tools/agent_bdd/.agent_bdd_sessions/repair-action-example.json
"""Example — repair action; assert on tools list and argument substitution inline."""
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import context, description, it

from agent_bdd import agent, instruct, instruct_use_tool

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SESSIONS = Path(__file__).resolve().parents[1] / ".agent_bdd_sessions"

_REPAIR_YAML = """\
toolset: context_tools.base.examples.car_chronicle.car_chronicle:CarChronicle
action: repair
arguments:
  asset: context_tools/base/examples/car_chronicle/output/driving-log.md
  violation: Scanner use-driving-voice — chronicle reads like a spec sheet
"""

with description("a CarChronicle generator"):
    with context("with agent and repair action"):
        with it("drives repair and asserts tools + argument substitution"):
            with agent(_REPO_ROOT, _SESSIONS / "repair-action-example.json"):
                instruct(
                    "Read context_tools/base/examples/car_chronicle/car_chronicle.py from the workspace.",
                    timeout_seconds=60,
                )

                response = instruct_use_tool(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"{_REPAIR_YAML}\n"
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=120,
                )
                expect(response.ok).to(be_true)
                expect(response.action).to(equal("repair"))
                expect(response.tools or []).to(contain("scan"))
                expect(str(response.instructions)).to(contain("driving-log.md"))
                expect(str(response.instructions)).to(contain("use-driving-voice"))
