# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""BDD — /plan /small-work themed run with Grill + HIL Grill (judge replies)."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_true, contain, equal, expect
from mamba import context, description, it

from plan.plan import PlanCommands, SmallWorkRunner, ThemedIssue

_THEME = "dummy-job2"
_RICH = """## Context
Saving empty sketch fails.

## Root cause
Null strokes list.

## Acceptance
Empty list saves cleanly.
"""
_FIXTURES = [
    ThemedIssue(1, "Defect: rich sketch null", _RICH, [f"theme:{_THEME}", "bug"]),
    ThemedIssue(2, "Defect: thin backlog", "fix it", [f"theme:{_THEME}", "bug"]),
    ThemedIssue(3, "Small change: thin color", "make greener", [f"theme:{_THEME}", "enhancement"]),
]


with description("SmallWorkRunner themed execution"):
    with context("when issues mix enough and thin context under one theme"):
        with it("should interrupt on thin context with Grill + HIL Grill for the judge"):
            with tempfile.TemporaryDirectory() as tmp:
                runner = SmallWorkRunner(
                    workspace=tmp,
                    issues=_FIXTURES,
                    state_path=Path(tmp) / "small-work-run.json",
                )
                first = runner.run(_THEME)
                expect(first["status"]).to(equal("hil_interrupt"))
                expect(first["themed_source"]).to(equal(f"theme:{_THEME}"))
                expect(first["grill"]).to(be_true)
                expect(first["hil_grill"]).to(be_true)
                expect(first["hil_replier"]).to(equal("judge"))
                expect(first["current_issue"]).to(equal(2))
                expect(first["grill_questions"]).not_to(equal([]))
                expect(first["report"][0]["number"]).to(equal(1))
                expect(first["report"][0]["outcome"]).to(equal("done"))

        with it("should accept judge hil_reply, continue next issues, and report Done"):
            with tempfile.TemporaryDirectory() as tmp:
                runner = SmallWorkRunner(
                    workspace=tmp,
                    issues=_FIXTURES,
                    state_path=Path(tmp) / "small-work-run.json",
                )
                runner.run(_THEME)
                after_hil = runner.run(
                    _THEME,
                    hil_reply=(
                        "## Root cause\nMissing handler.\n\n"
                        "## Acceptance\nButton opens backlog.\n"
                    ),
                )
                # Issue 3 is also thin — expect another HIL or done after second reply.
                if after_hil["status"] == "hil_interrupt":
                    expect(after_hil["current_issue"]).to(equal(3))
                    expect(after_hil["hil_replier"]).to(equal("judge"))
                    done = runner.run(
                        _THEME,
                        hil_reply="## Root cause\nPalette.\n\n## Acceptance\nGreener Done.\n",
                    )
                else:
                    done = after_hil
                expect(done["status"]).to(equal("done"))
                expect(done["themed_source"]).to(equal(f"theme:{_THEME}"))
                expect(done["mixed_context"]).to(be_true)
                expect(done["issues_done"]).to(equal(3))
                expect(done["hil_interrupts"]).to(equal(2))
                outcomes = [row["outcome"] for row in done["report"]]
                expect("hil_filled" in outcomes).to(be_true)
                expect(outcomes.count("done")).to(equal(3))


with description("PlanCommands /plan /small-work"):
    with context("when context carries a theme and fixture issues"):
        with it("should load the small-work Plan and run the themed source"):
            with tempfile.TemporaryDirectory() as tmp:
                state = Path(tmp) / ".context" / "small-work-run.json"
                # Point runner state under tmp by using workspace=tmp and fixtures.
                cmds = PlanCommands()
                result = cmds.small_work(
                    context=f"theme:{_THEME}",
                    workspace=tmp,
                    issues=[
                        {
                            "number": 10,
                            "title": "thin only",
                            "body": "broken",
                            "labels": [f"theme:{_THEME}"],
                        }
                    ],
                )
                expect(result["plan"]).to(equal("small-work"))
                expect(result["workflow"]).to(equal("small-work"))
                expect(result["status"]).to(equal("hil_interrupt"))
                expect(result["hil_grill"]).to(be_true)
                expect(result["hil_replier"]).to(equal("judge"))
                expect(state.is_file()).to(be_true)

                finished = cmds.small_work(
                    context=f"theme:{_THEME}",
                    workspace=tmp,
                    hil_reply="## Root cause\nx\n\n## Acceptance\ny\n",
                    issues=[
                        {
                            "number": 10,
                            "title": "thin only",
                            "body": "broken",
                            "labels": [f"theme:{_THEME}"],
                        }
                    ],
                )
                expect(finished["status"]).to(equal("done"))
                expect(finished["report"]).not_to(equal([]))


with description("SmallWorkRunner.enough_context"):
    with it("should treat short bodies as not enough"):
        expect(SmallWorkRunner.enough_context("fix it")).to(be_false)

    with it("should treat root-cause sections as enough"):
        expect(SmallWorkRunner.enough_context(_RICH)).to(be_true)
        expect("theme:dummy" in f"theme:{SmallWorkRunner.parse_theme('theme:dummy')}").to(
            be_true
        )
        expect(SmallWorkRunner.parse_theme("theme:dummy-job2")).to(equal("dummy-job2"))
