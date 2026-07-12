"""
# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
"""
# @agent-spec-manifest python -m tools agent-spec agent_bdd/examples/generate-action.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: agent_bdd/.sessions/generate-action-example.json
"""Example — act → assert → act → assert inline; no self.* accumulation."""
from pathlib import Path

from expects import be_true, equal, expect
from mamba import context, description, it

from agent_bdd import agent, ai_judge, instruct, instruct_use_tool

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SESSIONS = Path(__file__).resolve().parent.parent / ".sessions"

_GENERATE_YAML = """\
toolset: generator.examples.car_chronicle.car_chronicle:CarChronicle
action: generate
"""

with description("a CarChronicle generator"):
    with context("with agent and generate action"):
        with it("drives generate then judges the log"):
            with agent(_REPO_ROOT, _SESSIONS / "generate-action-example.json"):
                instruct(
                    "Read generator/examples/car_chronicle/car_chronicle.py from the workspace.",
                    timeout_seconds=60,
                )

                response = instruct_use_tool(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"{_GENERATE_YAML}\n"
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=120,
                )
                expect(response.ok).to(be_true)
                expect(response.action).to(equal("generate"))
                expect(response.tools or []).to(equal([]))
                expect("use-driving-voice" in str(response.instructions).lower()).to(be_true)

                chronicle = instruct(
                    "Follow the generate instructions and write a driving chronicle entry "
                    "for one trip from the Hazzard County garage to the courthouse.",
                    timeout_seconds=300,
                ).text
                ai_judge(
                    chronicle,
                    "The chronicle is a first-person driving log with a named route, "
                    "mileage or odometer numbers, and the car's personality.",
                )
