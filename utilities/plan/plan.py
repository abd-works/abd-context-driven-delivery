# @toolset-manifest python -m tools manifest plan.plan:Plan
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Plan — ordered workspace.Turns with optional JudgeCheckpoint / HILCheck."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from git.git import TicketState
from primitives.actions.action import agentic_toolset
from workspace.workspace import Turn, WorkSession, Workspace


@dataclass
class JudgeCheckpoint:
    """AI judge against a rubric on a Turn — same rubric argument as ai_judge."""

    rubric: str
    judge_result: str | None = None


@dataclass
class HILCheck:
    """Human-in-the-loop check hanging on a Turn."""

    validation: str | None = None


@agentic_toolset
class Plan:
    """Plan associated with a Workspace; holds ordered Turns.

    Start opens a WorkSession and moves the first Backlog Turn to In Progress.
    Execute Turn runs that Turn (performTurn). Advance finishes it (Done) and
    the next Backlog Turn becomes In Progress. HILCheck / JudgeCheckpoint hang
    on Turns; Fix and Rerun uses Turn.recordMistake / recordCorrection plus
    WorkSession.repairs.
    """

    def __init__(self, name: str = "", workspace: Workspace | None = None) -> None:
        self.name = name
        self.workspace = workspace
        self.turns: list[Turn] = []
        self.work_session: WorkSession | None = None

    @classmethod
    def create(cls, workspace: Workspace, name: str = "") -> Plan:
        plan = cls(name=name, workspace=workspace)
        plans = getattr(workspace, "plans", None)
        if plans is None:
            workspace.plans = []  # type: ignore[attr-defined]
            plans = workspace.plans
        plans.append(plan)
        return plan

    _BDD_KEY = "context_tools.bdd.bdd:Bdd"
    _CE_KEY = "context_tools.clean_engineering.clean_engineering:CleanEngineering"

    def add_turn(self, turn: Turn | None = None, **fields: Any) -> Turn:
        if turn is None:
            turn = Turn(work_session=None)
        for key, value in fields.items():
            setattr(turn, key, value)
        if not hasattr(turn, "state") or turn.state is None:  # type: ignore[attr-defined]
            turn.state = TicketState.backlog()  # type: ignore[attr-defined]
        if not hasattr(turn, "judge_checkpoint"):
            turn.judge_checkpoint = None  # type: ignore[attr-defined]
        if not hasattr(turn, "hil_check"):
            turn.hil_check = None  # type: ignore[attr-defined]
        self._ensure_bdd_includes_ce(turn)
        self.turns.append(turn)
        return turn

    def _ensure_bdd_includes_ce(self, turn: Turn) -> None:
        """/bdd must run Clean Engineering under the hood — companion on the same Turn."""
        keys = list(getattr(turn, "tool_keys", None) or [])
        if self._BDD_KEY in keys and self._CE_KEY not in keys:
            keys.append(self._CE_KEY)
            turn.tool_keys = keys
        calls = list(getattr(turn, "tool_calls", None) or [])
        has_bdd = any(getattr(c, "toolset", "") == self._BDD_KEY for c in calls)
        has_ce = any(getattr(c, "toolset", "") == self._CE_KEY for c in calls)
        if has_bdd and not has_ce:
            from workspace.workspace import ToolCall

            action = getattr(turn, "action", "") or "Generate"
            calls.append(
                ToolCall(
                    toolset=self._CE_KEY,
                    name=action,
                    summary="CleanEngineering companion under /bdd",
                )
            )
            turn.tool_calls = calls

    def edit_turn(self, turn: Turn, **fields: Any) -> Turn:
        for key, value in fields.items():
            setattr(turn, key, value)
        return turn

    def delete_turn(self, turn: Turn) -> None:
        if turn in self.turns:
            self.turns.remove(turn)

    def add_hil_check(self, turn: Turn, hil: HILCheck | None = None) -> HILCheck:
        check = hil or HILCheck()
        turn.hil_check = check  # type: ignore[attr-defined]
        return check

    def edit_hil_check(self, turn: Turn, hil: HILCheck) -> HILCheck:
        turn.hil_check = hil  # type: ignore[attr-defined]
        return hil

    def delete_hil_check(self, turn: Turn) -> None:
        turn.hil_check = None  # type: ignore[attr-defined]

    def add_judge_checkpoint(
        self, turn: Turn, rubric: str, checkpoint: JudgeCheckpoint | None = None
    ) -> JudgeCheckpoint:
        check = checkpoint or JudgeCheckpoint(rubric=rubric)
        check.rubric = rubric
        turn.judge_checkpoint = check  # type: ignore[attr-defined]
        return check

    def edit_judge_checkpoint(self, turn: Turn, rubric: str) -> JudgeCheckpoint:
        check = getattr(turn, "judge_checkpoint", None)
        if check is None:
            check = JudgeCheckpoint(rubric=rubric)
        else:
            check.rubric = rubric
        turn.judge_checkpoint = check  # type: ignore[attr-defined]
        return check

    def delete_judge_checkpoint(self, turn: Turn) -> None:
        turn.judge_checkpoint = None  # type: ignore[attr-defined]

    def start(self) -> WorkSession:
        """Open WorkSession; first Backlog Turn becomes In Progress."""
        if self.workspace is None:
            raise RuntimeError("Plan.start requires a Workspace")
        session = self.workspace.open_work_session(
            name=self.name or "plan",
            path=getattr(self.workspace, "path", ".") or ".",
        )
        self.work_session = session
        if self.turns:
            first = self.turns[0]
            first.state = TicketState.in_progress()  # type: ignore[attr-defined]
            session.open_turn = first
        return session

    def execute_turn(self) -> Turn | None:
        """Run the In Progress Turn (performTurn); TicketState stays In Progress."""
        session = self.work_session
        if session is None or session.open_turn is None:
            return None
        turn = session.open_turn
        if hasattr(turn, "perform_turn"):
            turn.perform_turn()
        if not getattr(turn, "result", ""):
            turn.result = turn.action or "executed"
        return turn

    def validate_with_human(self, validation: str) -> HILCheck | None:
        """Present Turn result to human; HILCheck holds the validation."""
        turn = self.work_session.open_turn if self.work_session else None
        if turn is None:
            return None
        check = getattr(turn, "hil_check", None) or HILCheck()
        check.validation = validation
        turn.hil_check = check  # type: ignore[attr-defined]
        return check

    def evaluate_results(self, judge_result: str) -> JudgeCheckpoint | None:
        """ai_judge against JudgeCheckpoint.rubric; holds JudgeResult."""
        turn = self.work_session.open_turn if self.work_session else None
        if turn is None:
            return None
        check = getattr(turn, "judge_checkpoint", None)
        if check is None:
            return None
        check.judge_result = judge_result
        return check

    def review_progress(self) -> dict[str, Any]:
        """Progress and results on the Plan for the open Turn."""
        turn = self.work_session.open_turn if self.work_session else None
        if turn is None:
            return {}
        hil = getattr(turn, "hil_check", None)
        judge = getattr(turn, "judge_checkpoint", None)
        return {
            "state": getattr(turn, "state", None),
            "result": getattr(turn, "result", None),
            "hil_validation": getattr(hil, "validation", None) if hil else None,
            "judge_result": getattr(judge, "judge_result", None) if judge else None,
        }

    def advance_turn(self) -> Turn | None:
        """Finish current Turn (Done); next Backlog becomes In Progress."""
        session = self.work_session
        if session is None or session.open_turn is None:
            return None
        current = session.open_turn
        current.state = TicketState.done()  # type: ignore[attr-defined]
        current.finish(
            prompt=getattr(current, "prompt", ""),
            result=getattr(current, "result", ""),
            context=getattr(current, "context", ""),
        )
        idx = self.turns.index(current) if current in self.turns else -1
        nxt = self.turns[idx + 1] if 0 <= idx < len(self.turns) - 1 else None
        if nxt is not None:
            nxt.state = TicketState.in_progress()  # type: ignore[attr-defined]
            session.open_turn = nxt
        else:
            session.open_turn = None
        return nxt

    def fix_and_rerun(self, mistake: str, correction: str) -> Turn | None:
        """recordMistake / recordCorrection; Repair on WorkSession; execute again."""
        session = self.work_session
        if session is None or session.open_turn is None:
            return None
        turn = session.open_turn
        if hasattr(turn, "record_mistake"):
            turn.record_mistake(mistake)
        if hasattr(turn, "record_correction"):
            turn.record_correction(correction)
        return self.execute_turn()
