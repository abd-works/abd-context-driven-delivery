# @toolset-manifest python -m tools manifest plan.plan:Plan
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Plan — ordered workspace.Turns with optional JudgeCheckpoint / HILCheck."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from git.git import TicketState
from primitives.actions.action import agentic_toolset
from workspace.workspace import Turn, WorkSession, Workspace


@dataclass
class JudgeCheckpoint:
    """Judge hangs on a Turn; CliAgent doer-judge fills judge_result."""

    rubric: str
    judge_result: str | None = None


@dataclass
class HILCheck:
    """Human-in-the-loop check hanging on a Turn."""

    validation: str | None = None


@dataclass
class ProgressView:
    """Domain view of Plan progress for the open Turn."""

    state: Any
    result: Any
    hil_validation: str | None
    judge_result: str | None


class TurnAttachments:
    """HILCheck and JudgeCheckpoint hanging on Turns."""

    def add_hil(self, turn: Turn, hil: HILCheck | None = None) -> HILCheck:
        check = hil or HILCheck()
        turn.hil_check = check  # type: ignore[attr-defined]
        return check

    def edit_hil(self, turn: Turn, hil: HILCheck) -> HILCheck:
        turn.hil_check = hil  # type: ignore[attr-defined]
        return hil

    def delete_hil(self, turn: Turn) -> None:
        turn.hil_check = None  # type: ignore[attr-defined]

    def add_judge(
        self, turn: Turn, rubric: str, checkpoint: JudgeCheckpoint | None = None
    ) -> JudgeCheckpoint:
        check = checkpoint or JudgeCheckpoint(rubric=rubric)
        check.rubric = rubric
        turn.judge_checkpoint = check  # type: ignore[attr-defined]
        return check

    def edit_judge(self, turn: Turn, rubric: str) -> JudgeCheckpoint:
        check = getattr(turn, "judge_checkpoint", None)
        if check is None:
            check = JudgeCheckpoint(rubric=rubric)
        else:
            check.rubric = rubric
        turn.judge_checkpoint = check  # type: ignore[attr-defined]
        return check

    def delete_judge(self, turn: Turn) -> None:
        turn.judge_checkpoint = None  # type: ignore[attr-defined]


@agentic_toolset
class Plan:
    """Plan front-end to git: ordered Turns; TicketState maps to Project columns."""

    def __init__(
        self,
        attachments: TurnAttachments,
        name: str = "",
        workspace: Workspace | None = None,
    ) -> None:
        self._attachments = attachments
        self._name = name
        self._workspace = workspace
        self._turns: list[Turn] = []
        self._work_session: WorkSession | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> Workspace | None:
        return self._workspace

    @property
    def turns(self) -> list[Turn]:
        return list(self._turns)

    @property
    def work_session(self) -> WorkSession | None:
        return self._work_session

    @work_session.setter
    def work_session(self, session: WorkSession | None) -> None:
        self._work_session = session

    @property
    def attachments(self) -> TurnAttachments:
        return self._attachments

    @classmethod
    def create(
        cls,
        workspace: Workspace,
        attachments: TurnAttachments,
        name: str = "",
    ) -> Plan:
        plan = cls(attachments=attachments, name=name, workspace=workspace)
        plans = getattr(workspace, "plans", None)
        if plans is None:
            workspace.plans = []  # type: ignore[attr-defined]
            plans = workspace.plans
        plans.append(plan)
        return plan

    def add_turn(self, turn: Turn | None = None, **fields: Any) -> Turn:
        if turn is None:
            turn = Turn(work_session=None)
        for field_name, field_value in fields.items():
            setattr(turn, field_name, field_value)
        if not hasattr(turn, "state") or turn.state is None:  # type: ignore[attr-defined]
            turn.state = TicketState.backlog()  # type: ignore[attr-defined]
        if not hasattr(turn, "judge_checkpoint"):
            turn.judge_checkpoint = None  # type: ignore[attr-defined]
        if not hasattr(turn, "hil_check"):
            turn.hil_check = None  # type: ignore[attr-defined]
        self._turns.append(turn)
        return turn

    def edit_turn(self, turn: Turn, **fields: Any) -> Turn:
        for field_name, field_value in fields.items():
            setattr(turn, field_name, field_value)
        return turn

    def delete_turn(self, turn: Turn) -> None:
        if turn in self._turns:
            self._turns.remove(turn)


class PlanExecution:
    """Runs a Plan: start, execute, judge record, advance, fix."""

    def __init__(self, plan: Plan) -> None:
        self._plan = plan

    def start(self) -> WorkSession:
        workspace = self._plan.workspace
        if workspace is None:
            raise RuntimeError("Plan.start requires a Workspace")
        session = workspace.open_work_session(
            name=self._plan.name or "plan",
            path=getattr(workspace, "path", ".") or ".",
        )
        self._plan.work_session = session
        turns = self._plan.turns
        if turns:
            first = turns[0]
            first.state = TicketState.in_progress()  # type: ignore[attr-defined]
            session.open_turn = first
        return session

    def execute_turn(self) -> Turn | None:
        turn = self._open_turn()
        if turn is None:
            return None
        if hasattr(turn, "perform_turn"):
            turn.perform_turn()
        if not getattr(turn, "result", ""):
            turn.result = turn.action or "executed"
        return turn

    def validate_with_human(self, validation: str) -> HILCheck | None:
        turn = self._open_turn()
        if turn is None:
            return None
        return self._plan.attachments.add_hil(turn, HILCheck(validation=validation))

    def evaluate_results(self, judge_result: str) -> JudgeCheckpoint | None:
        turn = self._open_turn()
        if turn is None:
            return None
        check = getattr(turn, "judge_checkpoint", None)
        if check is None:
            return None
        check.judge_result = judge_result
        return check

    def review_progress(self) -> ProgressView | None:
        turn = self._open_turn()
        if turn is None:
            return None
        hil = getattr(turn, "hil_check", None)
        judge = getattr(turn, "judge_checkpoint", None)
        return ProgressView(
            state=getattr(turn, "state", None),
            result=getattr(turn, "result", None),
            hil_validation=getattr(hil, "validation", None) if hil else None,
            judge_result=getattr(judge, "judge_result", None) if judge else None,
        )

    def advance_turn(self) -> Turn | None:
        session = self._plan.work_session
        turn = self._open_turn()
        if session is None or turn is None:
            return None
        turn.state = TicketState.done()  # type: ignore[attr-defined]
        turn.finish(
            prompt=getattr(turn, "prompt", ""),
            result=getattr(turn, "result", ""),
            context=getattr(turn, "context", ""),
        )
        return self._promote_next(session, turn)

    def fix_and_rerun(self, mistake: str, correction: str) -> Turn | None:
        turn = self._open_turn()
        if turn is None:
            return None
        if hasattr(turn, "record_mistake"):
            turn.record_mistake(mistake)
        if hasattr(turn, "record_correction"):
            turn.record_correction(correction)
        return self.execute_turn()

    def _open_turn(self) -> Turn | None:
        session = self._plan.work_session
        if session is None:
            return None
        return session.open_turn

    def _promote_next(self, session: WorkSession, current: Turn) -> Turn | None:
        turns = self._plan.turns
        idx = turns.index(current) if current in turns else -1
        nxt = turns[idx + 1] if 0 <= idx < len(turns) - 1 else None
        if nxt is not None:
            nxt.state = TicketState.in_progress()  # type: ignore[attr-defined]
            session.open_turn = nxt
        else:
            session.open_turn = None
        return nxt
