# @agent-spec-manifest python -m tools agent-spec context_tools/bdd/bdd_grill_sketch_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/bdd/.context/.agent_bdd_sessions/bdd-grill-sketch-two-agent.json
"""Agent BDD ΓÇö Bdd grill/sketch uses runner + judge agents with eval turns per tick."""

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    follow_instructions,
    read_workspace,
    repo_root_from,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_WORKFLOW = "context_tools/bdd/.context/bdd-grill-sketch-workflow.md"
_RUNNER_SKILL = ".cursor/skills/bdd-grill-runner/SKILL.md"
_JUDGE_SKILL = ".cursor/skills/bdd-grill-judge/SKILL.md"
_COMMAND = ".cursor/commands/bdd-grill-sketch.md"


with description("Bdd grill-sketch two-agent workflow"):
    with context("that is documented for runner and judge"):
        with it("should require separate eval turns for grill, answer, sketch, and validate"):
            with agent(_REPO_ROOT, _SESSIONS / "bdd-grill-sketch-two-agent.json"):
                read_workspace(_WORKFLOW)
                read_workspace(_RUNNER_SKILL)
                read_workspace(_JUDGE_SKILL)
                read_workspace(_COMMAND)

                summary = follow_instructions(
                    "Using only the four files you read, summarize in plain text:\n"
                    "1. Which agent grills vs answers vs validates.\n"
                    "2. The four turn kinds and whether grill and sketch may share a turn.\n"
                    "3. What the judge does on FAIL (mistakes + corrections).\n"
                    "4. That each turn uses begin_eval_turn and finish_eval_turn with its own commit.\n"
                    "Do not invent steps not in those files.",
                    timeout_seconds=180,
                ).text

                ai_judge(
                    summary,
                    "PASS only if: (a) runner grills/sketches and judge answers/validates; "
                    "(b) grill and sketch are separate turns; (c) judge runs independent "
                    "validation plus runner alignment; (d) FAIL leads to log_mistake and "
                    "log_correction on the turn; (e) every turn uses begin_eval_turn and "
                    "finish_eval_turn. FAIL if one agent does both grill and self-answer, "
                    "or if sketch is allowed in the same turn as grill.",
                )

    with context("that runner skill forbids self-answer"):
        with it("should tell the runner not to answer its own grill questions"):
            text = (_REPO_ROOT / _RUNNER_SKILL).read_text(encoding="utf-8")
            expect("do not" in text.lower() or "never" in text.lower()).to(be_true)
            expect("answer" in text.lower()).to(be_true)
            expect("begin_eval_turn" in text).to(be_true)

    with context("that judge skill requires independent validation"):
        with it("should require a validation pass without relying on runner chat"):
            text = (_REPO_ROOT / _JUDGE_SKILL).read_text(encoding="utf-8")
            expect("independent" in text.lower()).to(be_true)
            expect("log_mistake" in text).to(be_true)
            expect("log_correction" in text).to(be_true)
