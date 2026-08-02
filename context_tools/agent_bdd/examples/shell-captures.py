"""
# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
"""
# @agent-spec-manifest python -m tools agent-spec context_tools/agent_bdd/examples/shell-captures.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: context_tools/agent_bdd/.agent_bdd_sessions/shell-captures-example.json
"""Example — helpers + session_shell_captures for action-following specs."""
from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    combined_capture_text,
    expect_capture_mentions,
    expect_instructions_contain,
    expect_ok_action,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
    tools_run_captures,
)

_REPO_ROOT = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)

with description("a Car toolset"):
    with context("with agent following travelTo instructions"):
        with it("drives travelTo, checks shell captures, then judges the story"):
            with agent(_REPO_ROOT, _SESSIONS / "shell-captures-example.json") as block:
                read_workspace("primitives/actions/examples/car.py")

                response = run_toolset(
                    toolset="primitives.actions.examples.car:Car",
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

                story = follow_instructions(
                    "Follow the travelTo instructions - call start, then speak once in character.",
                    timeout_seconds=180,
                ).text

                captures = tools_run_captures(block)
                expect(len(captures) >= 1).to(be_true)
                expect_capture_mentions(combined_capture_text(captures), "start")

                ai_judge(
                    story,
                    "The story features General Lee traveling to a destination "
                    "with personality and at least one line of dialogue.",
                )
