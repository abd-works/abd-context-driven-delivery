# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_human_check_docs_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/cli_agent/.context/.agent_bdd_sessions/human-check-53-docs.json
"""Agent BDD — CliAgent human-check parent contract (#53).

Prompt/docs half: module-context + parent checkin + launch_sessions must describe
human_check_needed / human_notified / IDE or OS notification / resolve_human_check /
looks_good vs needs_fixing.
"""
from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("CliAgent human check guidance (#53)"):
    with context("when the agent reads module context and cli_agent parent contract"):
        with it(
            "should document human job flag, notification, human_check_needed, and resolve"
        ):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "human-check-53-docs.json",
            ):
                roots = [
                    _REPO_ROOT
                    / "utilities"
                    / "cli_agent"
                    / ".context"
                    / "module-context.md",
                    _REPO_ROOT / "utilities" / "cli_agent" / "cli_agent.py",
                ]
                text = "\n".join(
                    p.read_text(encoding="utf-8").lower()
                    for p in roots
                    if p.is_file()
                )
                expect("human" in text).to(be_true)
                expect("human_check_needed" in text).to(be_true)
                expect("human_notified" in text).to(be_true)
                expect(
                    "os notification" in text
                    or "ide/os" in text
                    or "show_os_notification" in text
                    or "ide/os notification" in text
                ).to(be_true)
                expect("resolve_human_check" in text).to(be_true)
                expect("looks_good" in text or "looks good" in text).to(be_true)
                expect("needs_fixing" in text or "needs fixing" in text).to(be_true)
                expect("run_backlog" in text).to(be_true)
