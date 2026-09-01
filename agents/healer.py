"""Healer — eval prompt bundles log evidence; all guidance lives in-prompt."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal

TriggerKind = Literal["success", "exception", "manual"]
_LOG_TAIL = 20

_EVAL_PROMPT = """You are the Healer.

## Problem
{problem_signals}

## What to do

| Problem | Heal |
|---------|------|
| Judge FAIL | **Improve doer_prompt and/or judge_prompt** — clearer task, stricter acceptance, show the expected answer shape. Then retry. |
| Exception or Agent fault | Fix the code seam that threw. Spec → code → mamba. |
| Nothing wrong | Say **no heal needed** and stop. |

Do **not** audit logs for random infra issues. Do **not** fix agent machinery when the judge caught a bad doer answer — fix the **prompt**.

## Prompts in play
{task_prompts}

## Run context
- Phase: {phase}
- Trigger: {trigger}
- Backlog remaining: {backlog_remaining}
- Tasks completed: {completed_count}
- Error forwarded: {error}
- Last phase result: {last_phase_result}

## Run metadata
{run_metadata}

## Session log (last {log_tail} records — evidence only)
{log_records}

## Report back
1. Problem in one sentence.
2. **Heal:** improved prompt text, or code fix, or **no heal needed**.
3. If you changed a prompt, give the revised doer_prompt / judge_prompt ready to paste into /agent-backlog.
"""


@dataclass
class HealerRunContext:
    """Evidence bundle for eval — no grading logic."""

    agent_type: str = ""
    session_name: str = ""
    session_goal: str = ""
    workspace: str = ""
    context_root: str = ""
    session_folder: str = ""
    log_path: str = ""
    backlog_prompts: list[str] = field(default_factory=list)
    current_task: dict[str, Any] = field(default_factory=dict)
    completed_tasks: list[dict[str, Any]] = field(default_factory=list)

    def as_text(self) -> str:
        payload = {
            "agent_type": self.agent_type,
            "session_name": self.session_name,
            "session_goal": self.session_goal,
            "workspace": self.workspace,
            "context_root": self.context_root,
            "session_folder": self.session_folder,
            "log_path": self.log_path,
            "backlog_prompts": self.backlog_prompts,
            "current_task": self.current_task or None,
            "completed_tasks": self.completed_tasks,
        }
        return json.dumps(payload, indent=2)


def tail_log_records(records: list[dict[str, Any]], *, limit: int = _LOG_TAIL) -> list[dict[str, Any]]:
    if limit <= 0 or len(records) <= limit:
        return list(records)
    return list(records[-limit:])


def format_log_records(records: list[dict[str, Any]], *, limit: int = _LOG_TAIL) -> str:
    tail = tail_log_records(records, limit=limit)
    if not tail:
        return "(empty)"
    return json.dumps(tail, indent=2)


def _format_task_prompts(run_context: HealerRunContext | None) -> str:
    if run_context is None:
        return "(none)"
    current = run_context.current_task or {}
    lines: list[str] = []
    doer = str(current.get("doer_prompt") or "").strip()
    judge = str(current.get("judge_prompt") or "").strip()
    if doer:
        lines.append(f"- doer_prompt: {doer}")
    if judge:
        lines.append(f"- judge_prompt: {judge}")
    if not lines and run_context.backlog_prompts:
        lines.append("- backlog:")
        for prompt in run_context.backlog_prompts:
            lines.append(f"  - {prompt}")
    return "\n".join(lines) if lines else "(none)"


def summarize_problem_signals(
    *,
    trigger: str,
    error: str,
    log_records: list[dict[str, Any]],
    last_phase_result: str,
    run_context: HealerRunContext | None = None,
) -> str:
    """Name the failure — prompt problem, code problem, or nothing."""
    lines: list[str] = []

    if error and error != "(none)":
        lines.append(f"- **Exception:** {error}")

    phase_hint = (last_phase_result or "").strip()
    if phase_hint and phase_hint != "(none)":
        lowered = phase_hint.lower()
        if any(
            token in lowered
            for token in ("fail", "healer_fix", "healer_stop", "error", "exception", "fault")
        ):
            lines.append(f"- **Last phase result:** {phase_hint[:500]}")

    last_verdict_idx = -1
    last_verdict: dict[str, Any] | None = None
    for index, row in enumerate(log_records):
        if row.get("kind") == "verdict":
            last_verdict = row
            last_verdict_idx = index

    recovered_fail = False
    for index, row in enumerate(log_records):
        if row.get("kind") != "verdict" or str(row.get("result", "")).upper() != "FAIL":
            continue
        after = log_records[index + 1 :]
        kicked = any(item.get("kind") == "kick" for item in after)
        recovered = any(
            item.get("kind") == "verdict"
            and str(item.get("result", "")).upper() == "PASS"
            for item in after
        )
        if kicked and recovered:
            recovered_fail = True
            break

    if recovered_fail:
        lines.append(
            "- **Judge FAIL then retry PASS** — doer gave a bad answer once. "
            "If unintended, **improve doer_prompt and/or judge_prompt** so the task is clearer."
        )
    elif last_verdict is not None and str(last_verdict.get("result", "")).upper() == "FAIL":
        lines.append(
            "- **Judge FAIL** — doer output did not meet judge_prompt. "
            "**Improve doer_prompt and/or judge_prompt**, then retry."
        )

    for row in reversed(log_records):
        if row.get("kind") == "append_fault":
            detail = str(row.get("detail") or row.get("kind") or "agent fault")
            lines.append(f"- **Agent fault:** {detail}")
            break

    if trigger == "exception" and not any(line.startswith("- **Exception") for line in lines):
        lines.append("- **Exception** — fix the code seam that threw.")

    if not lines:
        if trigger == "success":
            return "**No problem.** Report **no heal needed**."
        return "(inspect run context below)"

    return "\n".join(lines)


@dataclass
class HealerReport:
    phase: str
    trigger: TriggerKind
    log_kinds: list[str]
    mistakes: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    error: str = ""
    stop_recommended: bool = False
    fix_recommended: bool = False
    healer_prompt: str = ""

    def has_issues(self) -> bool:
        return bool(self.mistakes or self.error)

    def to_json(self) -> str:
        return json.dumps(
            {
                "phase": self.phase,
                "trigger": self.trigger,
                "log_kinds": self.log_kinds,
                "mistakes": self.mistakes,
                "fixes": self.fixes,
                "error": self.error,
                "stop_recommended": self.stop_recommended,
                "fix_recommended": self.fix_recommended,
            },
            indent=2,
        )

    def summary(self) -> str:
        if not self.has_issues() and not self.fixes:
            return "healer eval: no problem — report no heal needed"
        parts = [f"healer eval: {self.trigger} @ {self.phase}"]
        if self.error:
            parts.append(f"error: {self.error}")
        if self.mistakes:
            parts.append(f"mistakes: {len(self.mistakes)}")
        if self.fixes:
            parts.append(f"fixes: {len(self.fixes)}")
        if self.fix_recommended:
            parts.append("fix_recommended: true")
        if self.stop_recommended:
            parts.append("stop_recommended: true")
        return " | ".join(parts)


@dataclass
class Healer:
    """Bundle log evidence into a self-contained eval prompt."""

    fixes: list[str] = field(default_factory=list)
    mistakes: list[str] = field(default_factory=list)

    def eval(
        self,
        log_kinds: list[str],
        *,
        phase: str,
        trigger: TriggerKind = "success",
        error: BaseException | None = None,
        backlog_remaining: int = 0,
        completed_count: int = 0,
        log_records: list[dict[str, Any]] | None = None,
        run_context: HealerRunContext | None = None,
        last_phase_result: str = "",
    ) -> HealerReport:
        mistakes = list(self.mistakes)
        if error is not None:
            mistakes.append(f"{type(error).__name__}: {error}")

        records = list(log_records or [])
        has_error = error is not None
        report = HealerReport(
            phase=phase,
            trigger=trigger,
            log_kinds=list(log_kinds),
            mistakes=mistakes,
            fixes=list(self.fixes),
            error=str(error) if error else "",
            stop_recommended=False,
            fix_recommended=has_error or bool(mistakes),
            healer_prompt=self._build_prompt(
                phase=phase,
                trigger=trigger,
                log_kinds=log_kinds,
                log_records=records,
                error=str(error) if error else "(none)",
                backlog_remaining=backlog_remaining,
                completed_count=completed_count,
                run_context=run_context,
                last_phase_result=last_phase_result,
            ),
        )
        return report

    def record_fixes(self, fixes: list[str], *, phase: str = "") -> None:
        del phase
        self.fixes.extend(line.strip() for line in fixes if line.strip())

    def record_mistakes(self, mistakes: list[str], *, phase: str = "") -> None:
        del phase
        self.mistakes.extend(line.strip() for line in mistakes if line.strip())

    def _build_prompt(
        self,
        *,
        phase: str,
        trigger: str,
        log_kinds: list[str],
        log_records: list[dict[str, Any]],
        error: str,
        backlog_remaining: int,
        completed_count: int,
        run_context: HealerRunContext | None,
        last_phase_result: str,
    ) -> str:
        problem_signals = summarize_problem_signals(
            trigger=trigger,
            error=error,
            log_records=log_records,
            last_phase_result=last_phase_result or "(none)",
            run_context=run_context,
        )
        return _EVAL_PROMPT.format(
            phase=phase,
            trigger=trigger,
            backlog_remaining=backlog_remaining,
            completed_count=completed_count,
            error=error,
            last_phase_result=last_phase_result or "(none)",
            problem_signals=problem_signals,
            task_prompts=_format_task_prompts(run_context),
            run_metadata=(run_context.as_text() if run_context else "(none)"),
            log_tail=_LOG_TAIL,
            log_records=format_log_records(log_records),
        )


class HealerStop(Exception):
    """Raised when eval recommends stopping the agent run."""

    def __init__(self, report: HealerReport) -> None:
        super().__init__(report.summary())
        self.report = report


class HealerFailure(RuntimeError):
    """Raised when healer machinery cannot run eval — hard stop, no fallback."""


def format_healer_fix_handoff(report: HealerReport) -> str:
    """Return healer_fix text — parent agent repairs and retries."""
    lines = [
        f"healer_fix: {report.summary()}",
        report.healer_prompt,
        "",
        "Judge FAIL → improve the prompts above. Exception → fix code. Otherwise → no heal needed.",
        f"Then retry phase {report.phase!r}.",
    ]
    return "\n".join(lines)


def log_healer_eval(log: Any, report: HealerReport) -> None:
    """Append healer eval audit rows to an AgentSessionLog."""
    log.healer_eval(
        phase=report.phase,
        trigger=report.trigger,
        journey="agent-pick",
        stop_recommended=report.stop_recommended,
        fix_recommended=report.fix_recommended,
    )
    for mistake in report.mistakes:
        log.healer_finding(finding_kind="mistake", detail=mistake, phase=report.phase)
    for fix in report.fixes:
        log.healer_finding(finding_kind="fix", detail=fix, phase=report.phase)
    log.healer_report(
        summary=report.summary(),
        stop_recommended=report.stop_recommended,
        fix_recommended=report.fix_recommended,
    )


log_healer_report = log_healer_eval
