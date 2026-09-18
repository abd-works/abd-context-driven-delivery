# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: practices/engineering_specification/mern_domain_driven/.context/.agent_bdd_sessions/mern-domain-driven-generate.json
"""BDD agent spec for MernDomainDriven - manifest + generate instruction surface.

Proves a real agent, reading only the manifest (never this Python source),
discovers that generate composes the stories companion (which brings ce /
production TypeScript) and is told to apply the MERN-specific rules on top."""

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

_REPO_ROOT = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)
_MERN_PY = "practices/engineering_specification/mern_domain_driven/mern_domain_driven.py"
_TOOLSET = "practices.engineering_specification.mern_domain_driven.mern_domain_driven:MernDomainDriven"

with description("a MernDomainDriven generator"):
    with context("with agent"):
        with it("loads manifest and drives generate"):
            with agent(_REPO_ROOT, _SESSIONS / "mern-domain-driven-generate.json"):
                response = run_toolset(
                    toolset="generate.generate:Generate",
                    action="generate",
                    arguments={"guidance": [_TOOLSET]},
                    context={},
                    timeout_seconds=180,
                )
                expect_ok_action(response, "generate")
                expect_tools_include(response, ["open"])
                expect_instructions_contain_any(
                    response,
                    "clean_engineering",
                    "stories",
                    "session_guidance",
                    "sources",
                    "templates",
                )
