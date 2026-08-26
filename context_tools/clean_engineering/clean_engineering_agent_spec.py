# @agent-spec-manifest python -m tools agent-spec context_tools/clean_engineering/clean_engineering_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/clean_engineering/.context/.agent_bdd_sessions/clean-code-generate.json
"""BDD agent spec for CleanEngineering — manifest + generate/validate instruction surface."""

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    expect_instructions_contain_any,
    expect_ok_action,
    expect_tools_exclude,
    expect_tools_include,
    repo_root_from,
    run_manifest_from_header,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_CLEAN_CODE_PY = "context_tools/clean_engineering/clean_engineering.py"
_TOOLSET = "context_tools.clean_engineering.clean_engineering:CleanEngineering"
_CTX = {"format": "python"}

with description("a Clean Code generator"):
    with context("with agent"):
        with it("loads manifest and drives generate and validate"):
            with agent(_REPO_ROOT, _SESSIONS / "clean-code-generate.json"):
                manifest = run_manifest_from_header(_CLEAN_CODE_PY, timeout_seconds=300)
                text = manifest.text.lower()
                expect("generate" in text).to(be_true)
                expect("validate" in text).to(be_true)
                expect("satisfy" in text).to(be_true)
                expect("\n  scan:" in text or text.startswith("scan:")).to(be_true)
                expect("\n  scanners:" in text or text.startswith("scanners:")).not_to(
                    be_true
                )

                generate = run_toolset(
                    toolset="generate.generate:Generate",
                    action="generate",
                    arguments={"tools": [_TOOLSET]},
                    context=_CTX,
                    timeout_seconds=180,
                )
                expect_ok_action(generate, "generate")
                expect_tools_exclude(generate, ["scan"])
                expect_instructions_contain_any(
                    generate, "module", "class", "package", "packages"
                )

                validate = run_toolset(
                    toolset="validate.validate:Validate",
                    action="validate",
                    arguments={"tools": [_TOOLSET]},
                    context=_CTX,
                    timeout_seconds=180,
                )
                expect_ok_action(validate, "validate")
                expect_tools_include(validate, ["scan"])
