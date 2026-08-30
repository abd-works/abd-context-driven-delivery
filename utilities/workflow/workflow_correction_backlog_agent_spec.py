# @agent-spec-manifest python -m tools agent-spec utilities/workflow/workflow_correction_backlog_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/workflow/.context/.agent_bdd_sessions/correction-backlog-20.json
"""Agent BDD — correction-only /backlog guidance (#20).

Prompt/AI half: when an agent reads Turn + Workflow tool docs and module context,
it must see that (1) logging a mistake alone does **not** stage /backlog,
(2) logging a correction paired to that mistake **does** stage /backlog, and
(3) the staged issue body carries **both** the mistake and the correction.

Vanilla mamba coverage for the code path lives in ``workspace_spec`` /
``workflow_spec``. A red run here is usually prompt/guidance — fix those (and
this rubric if needed), not a vanilla BDD that only says "read the prompt."
"""
from pathlib import Path

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("auto backlog from logged mistake and correction (#20)"):
    with context(
        "when the agent reads Turn correction tools and Workflow module context"
    ):
        with it(
            "should require backlog only on correction with both mistake and correction in the body"
        ):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "correction-backlog-20.json",
            ):
                roots = [
                    _REPO_ROOT
                    / "utilities"
                    / "workspace"
                    / ".context"
                    / "module-context.md",
                    _REPO_ROOT
                    / "utilities"
                    / "workflow"
                    / ".context"
                    / "module-context.md",
                    _REPO_ROOT / "utilities" / "workspace" / "workspace.py",
                    _REPO_ROOT / "utilities" / "workflow" / "workflow.py",
                ]
                text = "\n".join(
                    p.read_text(encoding="utf-8").lower()
                    for p in roots
                    if p.is_file()
                )

                # Mistake alone must not stage /backlog (agent-facing contract).
                expect(
                    "does not invoke /backlog" in text
                    or (
                        "record_mistake" in text
                        and "does not invoke" in text
                        and "backlog" in text
                    )
                ).to(be_true)

                # Correction (paired) stages /backlog — never mistake alone.
                expect(
                    "correction only" in text
                    or "backlog starts on correction only" in text
                    or (
                        "backlog_from_correction" in text
                        and "never" in text
                        and "mistake alone" in text
                    )
                ).to(be_true)

                # Body must carry both so good vs bad is visible.
                expect("both the mistake and the correction" in text).to(be_true)
                expect("## mistake" in text or "mistake" in text).to(be_true)
                expect("## correction" in text or "correction" in text).to(be_true)
