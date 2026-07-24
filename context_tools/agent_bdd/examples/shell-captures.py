"""
# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
"""
# @agent-spec-manifest python -m tools agent-spec context_tools/agent_bdd/examples/shell-captures.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: context_tools/agent_bdd/.agent_bdd_sessions/shell-captures-example.json
"""Example — session_shell_captures; assert tool invocations appeared then judge the story."""
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import context, description, it

from agent_bdd import agent, ai_judge, instruct, instruct_use_tool
from agent_bdd.agent_bdd_common import looks_like_tools_run_output

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SESSIONS = Path(__file__).resolve().parents[1] / ".agent_bdd_sessions"

_TRAVEL_YAML = """\
toolset: primitives.actions.examples.car:Car
context:
  make: Dodge
  model: Charger
  year: 1969
  personality: General Lee
action: travelTo
arguments:
  destination: Hazzard County courthouse
  conditions: muddy back roads, Sheriff Rosco in pursuit
"""

with description("a Car toolset"):
    with context("with agent following travelTo instructions"):
        with it("drives travelTo, checks shell captures, then judges the story"):
            with agent(_REPO_ROOT, _SESSIONS / "shell-captures-example.json") as a:
                instruct("Read actions/examples/car.py from the workspace.", timeout_seconds=60)

                response = instruct_use_tool(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"{_TRAVEL_YAML}\n"
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=90,
                )
                expect(response.ok).to(be_true)
                expect(response.action).to(equal("travelTo"))
                expect(str(response.instructions).lower()).to(contain("courthouse"))

                story = instruct(
                    "Follow the travelTo instructions — call start, then speak once in character.",
                    timeout_seconds=180,
                ).text

                tool_runs = [
                    c for c in a.session_shell_captures
                    if "tools run" in c.command.lower() or looks_like_tools_run_output(c.output)
                ]
                expect(len(tool_runs) >= 1).to(be_true)
                combined = "\n".join(f"{c.command}\n{c.output}" for c in tool_runs)
                expect(combined.lower()).to(contain("start"))

                ai_judge(
                    story,
                    "The story features General Lee traveling to a destination "
                    "with personality and at least one line of dialogue.",
                )
