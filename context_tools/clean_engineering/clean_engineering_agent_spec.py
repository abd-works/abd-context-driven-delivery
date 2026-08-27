# @agent-spec-manifest python -m tools agent-spec context_tools/clean_engineering/clean_engineering_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/clean_engineering/.context/.agent_bdd_sessions/clean-code-generate.json
"""BDD agent spec for CleanEngineering — generate/validate instruction surface."""

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
_TOOLSET = "context_tools.clean_engineering.clean_engineering:CleanEngineering"
_HOST = {"toolset": _TOOLSET, "context": {"format": "python"}}


with description("a Clean Code generator"):
    with context("with agent"):
        with it("drives generate and validate"):
            with agent(_REPO_ROOT, _SESSIONS / "clean-code-generate.json"):
                generate = run_toolset(
                    toolset="generate.generate:Generate",
                    action="generate",
                    arguments={"tools": [_HOST]},
                    timeout_seconds=180,
                )
                expect_ok_action(generate, "generate")
                expect_tools_include(
                    generate,
                    [
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                        "create_diagram",
                        "scan",
                        "repair",
                        "finish_turn",
                    ],
                )
                expect_instructions_contain_any(
                    generate, "module", "class", "package", "packages"
                )

                validate = run_toolset(
                    toolset="validate.validate:Validate",
                    action="validate",
                    arguments={"tools": [_HOST]},
                    timeout_seconds=180,
                )
                expect_ok_action(validate, "validate")
                expect_tools_include(
                    validate,
                    [
                        "read_cdr_format",
                        "list_cdrs",
                        "write_cdr",
                        "scan",
                        "finish_turn",
                    ],
                )
