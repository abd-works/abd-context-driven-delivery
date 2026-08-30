# @agent-spec-manifest python -m tools agent-spec context_tools/clean_engineering/clean_engineering_module_context_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/clean_engineering/.context/.agent_bdd_sessions/module-context-public-seam.json
"""Agent BDD — module-context stays public-seam-only (use / extend / dependencies)."""

import re

from expects import be_true, contain, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    expect_instructions_contain,
    expect_ok_action,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_TOOLSET = "context_tools.clean_engineering.clean_engineering:CleanEngineering"
_HOST = {
    "toolset": _TOOLSET,
    "context": {"fidelity": "modules", "format": "markdown"},
}

_BANNED_HEADINGS = re.compile(
    r"(?im)^\s*#{1,6}\s+(Internal design|Internals?|Participants|Domain separation|"
    r"Pickup|Known scan notes|Tests|Scanners|Layout)\b"
)
_PRIVATE_NAME = re.compile(r"(?<![A-Za-z0-9*])(_(?!is_)[A-Za-z][A-Za-z0-9_]*)\b")


with description("CleanEngineering module-context"):
    with context("when generating at modules fidelity"):
        with it("should keep module-context to use, extend, and dependencies only"):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "module-context-public-seam.json",
            ):
                read_workspace(
                    "context_tools/clean_engineering/clean_engineering.md"
                )

                generate = run_toolset(
                    toolset="generate.generate:Generate",
                    action="generate",
                    arguments={"tools": [_HOST]},
                    timeout_seconds=300,
                )
                expect_ok_action(generate, "generate")
                expect_instructions_contain(
                    generate,
                    "module-context",
                    "public seam",
                )
                instructions = (generate.instructions or "").lower()
                expect("public-seam-only" in instructions).to(be_true)
                expect("internal design" in instructions).to(be_true)
                expect("never" in instructions).to(be_true)

                draft = follow_instructions(
                    "Using Clean Engineering module-context rules you just received, "
                    "write a complete `.context/module-context.md` for a toy `cart` "
                    "module. Public types: Cart only. Dependencies: catalog (one-way). "
                    "Include how to use and how to extend. Do not invent private helpers, "
                    "underscore types, Internal design, Participants, Pickup, or doer/judge "
                    "internals. Return only the markdown file body.",
                    timeout_seconds=300,
                ).text
                lowered = draft.lower()
                expect(lowered).to(contain("cart"))
                expect(lowered).to(contain("catalog"))
                expect(
                    "purpose" in lowered
                    or "seam" in lowered
                    or "dependenc" in lowered
                ).to(be_true)
                expect(
                    "extend" in lowered
                    or "mechanism" in lowered
                    or "how to extend" in lowered
                ).to(be_true)
                expect(_BANNED_HEADINGS.search(draft) is None).to(be_true)
                expect(_PRIVATE_NAME.search(draft) is None).to(be_true)
