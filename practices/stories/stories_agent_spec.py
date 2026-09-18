# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: practices/stories/.context/.agent_bdd_sessions/stories-generate.json
"""BDD agent spec for Stories — manifest + generate instruction surface."""

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    expect_instructions_contain_any,
    expect_ok_action,
    expect_tools_include,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_STORIES_PY = "practices/stories/stories.py"
_TOOLSET = "practices.stories.stories:Stories"

with description("a Stories generator"):
    with context("with agent"):
        with it("loads manifest and drives generate"):
            with agent(_REPO_ROOT, _SESSIONS / "stories-generate.json"):
                response = run_toolset(
                    toolset="generate.generate:Generate",
                    action="generate",
                    arguments={"guidance": [_TOOLSET]},
                    context={"fidelity": "discovery", "format": "markdown"},
                    timeout_seconds=180,
                )
                expect_ok_action(response, "generate")
                expect_tools_include(response, ["open"])
                expect_instructions_contain_any(
                    response, "story", "epic", "session_guidance", "sources"
                )
