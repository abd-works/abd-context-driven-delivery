# @agent-spec-manifest python -m tools agent-spec actions/actions_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: actions/.agent_bdd_sessions/travel-to.json
"""BDD agent spec for action.py - agent invokes @action via tools CLI."""

from pathlib import Path

from expects import be_true, equal, expect
from mamba import after, before, context, description, it

from agent_bdd import agent
from agent_bdd.agent_cli_bdd import looks_like_tools_run_output

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SESSIONS = Path(__file__).resolve().parent / ".agent_bdd_sessions"
_CAR_TOOLSET = "primitives.actions.examples.car:Car"


with description("a class"):
    with context("with a toolset that declares @action recipes"):
        with context("with agent and travelTo action"):
            with before.all:
                self._travel_agent = agent(_REPO_ROOT, _SESSIONS / "travel-to.json")
                self.travel_session = self._travel_agent.__enter__()
                self.travel_session.instruct("Read actions/examples/car.py from the workspace.")
                self.general_lee = self.travel_session.instruct_run(
                    "Create a car based on the general lee from the Dukes of Hazzard."
                )
                self.travel_response = self.travel_session.instruct_run(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"toolset: {_CAR_TOOLSET}\n"
                    "context:\n"
                    "  make: Dodge\n"
                    "  model: Charger\n"
                    "  year: 1969\n"
                    "  personality: General Lee\n"
                    "action: travelTo\n"
                    "arguments:\n"
                    '  destination: Hazzard County courthouse\n'
                    '  conditions: muddy back roads, Sheriff Rosco in pursuit\n'
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=90,
                )
                self.story_result = self.travel_session.instruct(
                    "General Lee must reach the Hazzard County courthouse. "
                    "Use python -m tools run via shell: call start, then speak once in character. "
                    "Summarize the muddy-road adventure with Rosco in pursuit.",
                    timeout_seconds=180,
                )

            with after.all:
                self._travel_agent.__exit__(None, None, None)

            with it("should parse travelTo action response with instructions"):
                expect(self.travel_response.ok).to(be_true)
                expect(self.travel_response.action).to(equal("travelTo"))
                expect(self.travel_response.instructions is not None).to(be_true)
                expect("Hazzard County courthouse" in str(self.travel_response.instructions)).to(be_true)

            with it("should invoke at least start and speak tools while following instructions"):
                tool_runs = [
                    capture
                    for capture in self.travel_session.session_shell_captures
                    if "tools run" in capture.command.lower() or looks_like_tools_run_output(capture.output)
                ]
                combined = "\n".join(
                    f"{capture.command}\n{capture.output}" for capture in tool_runs
                )
                combined = combined + "\n" + self.story_result.stdout
                expect(len(tool_runs) >= 1).to(be_true)
                expect("start" in combined.lower()).to(be_true)
                expect("speak" in combined.lower() or "says" in combined.lower()).to(be_true)

            with it("should judge the story as an entertaining General Lee adventure"):
                verdict = self.travel_session.ai_judge(
                    self.story_result.stdout,
                    "The story should feature General Lee traveling to Hazzard County "
                    "with personality, action, and at least one line of dialogue.",
                )
                expect(verdict.passed()).to(be_true)
