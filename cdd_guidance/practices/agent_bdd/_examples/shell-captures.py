"""
"""
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: practices/agent_bdd/.agent_bdd_sessions/shell-captures-example.json
"""Example — helpers + session_shell_captures for action-following specs."""
from expects import be_true, expect
from mamba import context, description, it

from cdd_guidance.practices.agent_bdd.agent_block import agent
from cdd_guidance.practices.agent_bdd.spec_helpers import (
    expect_instructions_contain,
    expect_ok_action,
    repo_root_from,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)

with description("a Car toolset"):
    with context("with agent following travelTo instructions"):
        with it("drives travelTo, checks shell captures, then judges the story"):
            with agent(_REPO_ROOT, _SESSIONS / "shell-captures-example.json") as run:
                run.read_workspace("harness/agent_tools/_examples/car/car.py")

                response = run.run_toolset(
                    toolset="agent_tools._examples.car:Car",
                    action="travelTo",
                    context={
                        "make": "Dodge",
                        "model": "Charger",
                        "year": 1969,
                        "personality": "General Lee",
                    },
                    arguments={
                        "destination": "Hazzard County courthouse",
                        "conditions": "muddy back roads, Sheriff Rosco in pursuit",
                    },
                    timeout_seconds=90,
                )
                expect_ok_action(response, "travelTo")
                expect_instructions_contain(response, "courthouse")

                story = run.instruct(
                    "Follow the travelTo instructions - call start, then speak once in character.",
                    timeout_seconds=180,
                ).text

                captures = run.session_shell_captures
                expect(len(captures) >= 1).to(be_true)
                expect(any("start" in capture.command + capture.output for capture in captures)).to(be_true)

                run.ai_judge(
                    story,
                    "The story features General Lee traveling to a destination "
                    "with personality and at least one line of dialogue.",
                )
