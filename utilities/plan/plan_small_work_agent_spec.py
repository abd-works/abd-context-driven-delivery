# @agent-spec-manifest python -m tools agent-spec utilities/plan/plan_small_work_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: utilities/plan/.context/.agent_bdd_sessions/small-work-themed-hil.json
"""Agent BDD — /plan /small-work themed source, HIL Grill (judge replies), Done report."""
import json
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_ok_tool,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_TOOLSET = "plan.plan:PlanCommands"
_THEME = "dummy-job2-agent"
_ISSUES = [
    {
        "number": 101,
        "title": "Defect: rich enough",
        "body": (
            "## Context\nCrash on empty save.\n\n"
            "## Root cause\nNull list.\n\n"
            "## Acceptance\nEmpty saves OK.\n"
        ),
        "labels": [f"theme:{_THEME}", "bug"],
    },
    {
        "number": 102,
        "title": "Defect: thin context",
        "body": "fix it",
        "labels": [f"theme:{_THEME}", "bug"],
    },
    {
        "number": 103,
        "title": "Small change: thin tweak",
        "body": "make greener",
        "labels": [f"theme:{_THEME}", "enhancement"],
    },
]


with description("a PlanCommands small-work run"):
    with context("against one dummy theme with mixed context"):
        with it("should HIL-interrupt for the judge, then finish Done after judge replies"):
            with agent(_REPO_ROOT, _SESSIONS / "small-work-themed-hil.json"):
                read_workspace("utilities/plan/plan.py")
                read_workspace("utilities/plan/.context/module-context.md")

                first = run_toolset(
                    toolset=_TOOLSET,
                    tool="small_work",
                    arguments={
                        "context": f"theme:{_THEME}",
                        "workspace": str(_REPO_ROOT / "utilities" / "plan"),
                        "issues": _ISSUES,
                    },
                    timeout_seconds=180,
                )
                expect_ok_tool(first, "small_work")
                result = first.result if isinstance(first.result, dict) else {}
                if isinstance(first.result, str):
                    result = json.loads(first.result)
                expect(result.get("status")).to(equal("hil_interrupt"))
                expect(str(result.get("themed_source"))).to(contain(_THEME))
                expect(result.get("grill")).to(equal(True))
                expect(result.get("hil_grill")).to(equal(True))
                expect(result.get("hil_replier")).to(equal("judge"))
                expect(result.get("current_issue")).to(equal(102))

                # Judge (not parent) replies to HIL Grill.
                after_first_hil = run_toolset(
                    toolset=_TOOLSET,
                    tool="small_work",
                    arguments={
                        "context": f"theme:{_THEME}",
                        "workspace": str(_REPO_ROOT / "utilities" / "plan"),
                        "hil_reply": (
                            "## Root cause\nMissing click handler.\n\n"
                            "## Acceptance\nBacklog opens.\n"
                        ),
                        "issues": _ISSUES,
                    },
                    timeout_seconds=180,
                )
                expect_ok_tool(after_first_hil, "small_work")
                mid = after_first_hil.result if isinstance(after_first_hil.result, dict) else {}
                if isinstance(after_first_hil.result, str):
                    mid = json.loads(after_first_hil.result)

                if mid.get("status") == "hil_interrupt":
                    expect(mid.get("current_issue")).to(equal(103))
                    expect(mid.get("hil_replier")).to(equal("judge"))
                    done_resp = run_toolset(
                        toolset=_TOOLSET,
                        tool="small_work",
                        arguments={
                            "context": f"theme:{_THEME}",
                            "workspace": str(_REPO_ROOT / "utilities" / "plan"),
                            "hil_reply": (
                                "## Root cause\nPalette token.\n\n"
                                "## Acceptance\nDone is greener.\n"
                            ),
                            "issues": _ISSUES,
                        },
                        timeout_seconds=180,
                    )
                    expect_ok_tool(done_resp, "small_work")
                    done = done_resp.result if isinstance(done_resp.result, dict) else {}
                    if isinstance(done_resp.result, str):
                        done = json.loads(done_resp.result)
                else:
                    done = mid

                expect(done.get("status")).to(equal("done"))
                expect(done.get("mixed_context")).to(equal(True))
                expect(int(done.get("issues_done") or 0)).to(equal(3))

                narrative = follow_instructions(
                    "In one short paragraph, summarize the small-work run. You MUST "
                    "explicitly mention: (1) themed source, (2) mixed context, "
                    "(3) HIL Grill interrupt, (4) judge (not parent) replies, "
                    "(5) continuing to the next issue after each reply, and "
                    f"(6) Done report. Result JSON: {json.dumps(done)[:1200]}",
                    timeout_seconds=120,
                ).text
                ai_judge(
                    narrative,
                    "PASS if the summary covers themed source, HIL or judge reply, "
                    "next issue (or continuing after reply), and Done. FAIL only if "
                    "one of those four ideas is clearly missing.",
                )
