# @agent-spec-manifest python -m tools agent-spec context_tools/bdd/bdd_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/bdd/.context/.agent_bdd_sessions/bdd-generate.json
"""BDD agent spec for Bdd — manifest + generate instruction surface."""

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    expect_instructions_contain_any,
    expect_ok_action,
    expect_tools_include,
    repo_root_from,
    run_manifest_from_header,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_BDD_PY = "context_tools/bdd/bdd.py"
_TOOLSET = "context_tools.bdd.bdd:Bdd"

with description("a Bdd generator"):
    with context("with agent"):
        with it("loads manifest and drives generate"):
            with agent(_REPO_ROOT, _SESSIONS / "bdd-generate.json"):
                manifest = run_manifest_from_header(_BDD_PY, timeout_seconds=300)
                text = manifest.text.lower()
                expect("generate" in text).to(be_true)
                expect("validate" in text).to(be_true)

                response = run_toolset(
                    toolset="generate.generate:Generate",
                    action="generate",
                    arguments={"tools": [_TOOLSET]},
                    context={"fidelity": "behavior", "format": "python"},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "generate")
                expect_tools_include(response, ["open"])
                expect_instructions_contain_any(
                    response, "describe", "behavior", "session_guidance", "subject"
                )
