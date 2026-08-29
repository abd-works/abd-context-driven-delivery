# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_backlog_hygiene_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/cli_agent/.context/.agent_bdd_sessions/backlog-hygiene-46.json
"""Agent BDD — CliAgent backlog hygiene prompts (#46).

Captures the prompt/AI half of BOTH: parent/defect-fix guidance must require
(1) up-front backlog triage to #N / capture_backlog,
(2) theme:cli-agent,
(3) finish-ticket before next_backlog_item.
"""
from pathlib import Path

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("CliAgent backlog hygiene guidance (#46)"):
    with context(
        "when the agent reads defect-fix, launch_sessions backlog docs, and module context"
    ):
        with it(
            "should require up-front triage, theme cli-agent, and finish-ticket before next_backlog_item"
        ):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "backlog-hygiene-46.json",
            ):
                roots = [
                    _REPO_ROOT
                    / "utilities"
                    / "cli_agent"
                    / "job-templates"
                    / "defect-fix.json",
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
                expect("theme:cli-agent" in text or "theme: cli-agent" in text).to(
                    be_true
                )
                expect("finish-ticket" in text or "finish_ticket" in text).to(be_true)
                expect(
                    "next_backlog_item" in text or "next_backlog_item" in text
                ).to(be_true)
                launch = (
                    _REPO_ROOT / "utilities" / "cli_agent" / "cli_agent.py"
                ).read_text(encoding="utf-8")
                backlog_doc = (
                    launch.split("## Backlog", 1)[-1].split("## ", 1)[0].lower()
                )
                expect(
                    "finish-ticket" in backlog_doc or "finish_ticket" in backlog_doc
                ).to(be_true)
                expect(
                    "triage" in backlog_doc
                    or "up front" in backlog_doc
                    or "up-front" in backlog_doc
                    or "entire backlog" in backlog_doc
                    or ("map" in backlog_doc and "ticket" in backlog_doc)
                ).to(be_true)
