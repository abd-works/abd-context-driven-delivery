# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: harness/agent_tools/.context/.agent_bdd_sessions/travel-to.json
# session: harness/agent_tools/.context/.agent_bdd_sessions/display-agenda-tools.json
"""Agent BDD for actions — travelTo, display agenda tools, deployed prompts."""

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    combined_capture_text,
    expect_capture_mentions,
    expect_instructions_contain,
    expect_ok_action,
    expect_tools_include,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_skill,
    run_toolset,
    sessions_dir,
    tools_run_captures,
)
from agent_bdd.spec_helpers import (
    CAR_SKILL,
    TRAVEL_TO,
    car_tool_argument,
    stage_invoke_commands,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("a class"):
    with context("with a toolset that declares @agent_instructions members"):
        with context("with agent and travelTo action"):
            with it("drives travelTo from deployed prompts, follows tools, judges the story"):
                stage_invoke_commands(_REPO_ROOT)
                with agent(_REPO_ROOT, _SESSIONS / "travel-to.json") as block:
                    read_workspace(CAR_SKILL)
                    read_workspace(TRAVEL_TO)

                    travel = run_skill(
                        TRAVEL_TO,
                        repo_root=_REPO_ROOT,
                        arguments={
                            "tools": [car_tool_argument()],
                            "destination": "Hazzard County courthouse",
                            "conditions": "muddy back roads, Sheriff Rosco in pursuit",
                        },
                        timeout_seconds=90,
                    )
                    expect_ok_action(travel, "travelTo")
                    expect_instructions_contain(travel, "Hazzard County courthouse")

                    story = follow_instructions(
                        "General Lee must reach the Hazzard County courthouse. "
                        "Invoke the car start tool, then speak once in character. "
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


with description("agenda construction"):
    with context("when expand makes tools available to the chat"):
        with it("should tell the agent to display those tools and the agent should surface them"):
            with agent(_REPO_ROOT, _SESSIONS / "display-agenda-tools.json") as block:
                expanded = run_toolset(
                    toolset="agent_tools.examples.logged_probe:LoggedProbe",
                    action="narrate",
                    arguments={"message": "hello"},
                    timeout_seconds=90,
                    require_agent_shell=True,
                )
                expect_ok_action(expanded, "narrate")
                expect_tools_include(expanded, ["ping"])
                expect_instructions_contain(
                    expanded,
                    "display the tools made available to this chat in your user-visible reply",
                    "Tools made available:",
                    "ping",
                    "Echo a message",
                )

                reply = follow_instructions(
                    "Follow response.instructions. Before calling any tool, "
                    "display the tools made available to this chat — each name and what it is for — "
                    "in your reply. Then stop; do not invoke tools yet.",
                    timeout_seconds=120,
                )
                text = (reply.text or "").lower()
                expect("ping" in text).to(be_true)
                expect("echo" in text).to(be_true)
                expect(len(tools_run_captures(block)) >= 1).to(be_true)
