# @agent-spec-manifest python -m tools agent-spec primitives/actions/actions_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/actions/.context/.agent_bdd_sessions/travel-to.json
"""BDD agent spec for action.py — travelTo via shared helpers."""

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

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_CAR_TOOLSET = "primitives.actions.examples.car:Car"
_LEE = {
    "make": "Dodge",
    "model": "Charger",
    "year": 1969,
    "personality": "General Lee",
}

with description("a class"):
    with context("with a toolset that declares @agent_instructions recipes"):
        with context("with agent and travelTo action"):
            with it("drives travelTo, follows tools, judges the story"):
                with agent(_REPO_ROOT, _SESSIONS / "travel-to.json") as block:
                    read_workspace("primitives/actions/examples/car.py")

                    travel = run_toolset(
                        toolset=_CAR_TOOLSET,
                        action="travelTo",
                        context=_LEE,
                        arguments={
                            "destination": "Hazzard County courthouse",
                            "conditions": "muddy back roads, Sheriff Rosco in pursuit",
                        },
                        timeout_seconds=90,
                    )
                    expect_ok_action(travel, "travelTo")
                    expect_instructions_contain(travel, "Hazzard County courthouse")

                    story = follow_instructions(
                        "General Lee must reach the Hazzard County courthouse. "
                        "Use python -m tools run via shell: call start, then speak once in character. "
                        "Summarize the muddy-road adventure with Rosco in pursuit.",
                        timeout_seconds=180,
                    )
                    captures = tools_run_captures(block)
                    expect(len(captures) >= 1).to(be_true)
                    combined = combined_capture_text(captures, story.text)
                    expect_capture_mentions(combined, "start")
                    mentioned_speak = (
                        "speak" in combined.lower() or "says" in combined.lower()
                    )
                    expect(mentioned_speak).to(be_true)

                    ai_judge(
                        story.text,
                        "The story features General Lee traveling to Hazzard County "
                        "with personality, action, and at least one line of dialogue.",
                        timeout_seconds=180,
                    )
