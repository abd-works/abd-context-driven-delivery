# @toolset-manifest python -m tools manifest plan.plan:Plan
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Plan — front-end to git; based on a reusable or named Workflow."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from git.git import TicketState
from harness.harness_tool import prompt
from primitives.actions.action import agentic_toolset
from tools.tool import agent_tool
from workspace.workspace import Turn, WorkSession, Workspace
from workflow.workflow import Workflow


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


@dataclass
class TurnTemplate:
    """One prebaked Turn shape loaded from a named Workflow."""

    action: str
    fidelity: str = ""
    format: str = ""
    context: str = ""
    tool_keys: list[str] = field(default_factory=list)


# Prebaked Workflow recipes — /plan /small-work loads this; does not run against issues.
# BDD owns CE companions; Plan does not inject CleanEngineering onto Turns.
_PREBAKED_WORKFLOWS: dict[str, list[TurnTemplate]] = {
    "small-work": [
        TurnTemplate(
            action="Generate",
            fidelity="story_map",
            format="markdown",
            context="",
            tool_keys=["context_tools.stories.stories:Stories"],
        ),
        TurnTemplate(
            action="Generate",
            fidelity="behavior",
            format="markdown",
            context="",
            tool_keys=["context_tools.bdd.bdd:Bdd"],
        ),
    ],
}


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
    """Plan front-end to git, based on a reusable or newly named Workflow."""

    def __init__(
        self,
        attachments: TurnAttachments | None = None,
        name: str = "",
        workspace: Workspace | None = None,
        workflow: Workflow | None = None,
        workflow_name: str = "",
    ) -> None:
        self._attachments = attachments if attachments is not None else TurnAttachments()
        self._name = name
        self._workspace = workspace
        self._workflow = workflow
        self._workflow_name = workflow_name
        self._turns: list[Turn] = []
        self._work_session: WorkSession | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> Workspace | None:
        return self._workspace

    @property
    def workflow(self) -> Workflow | None:
        return self._workflow

    @property
    def workflow_name(self) -> str:
        return self._workflow_name

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
        attachments: TurnAttachments | None = None,
        name: str = "",
        workflow: Workflow | None = None,
        workflow_name: str = "",
    ) -> Plan:
        plan = cls(
            attachments=attachments,
            name=name,
            workspace=workspace,
            workflow=workflow,
            workflow_name=workflow_name,
        )
        plans = getattr(workspace, "plans", None)
        if plans is None:
            workspace.plans = []  # type: ignore[attr-defined]
            plans = workspace.plans
        plans.append(plan)
        return plan

    @classmethod
    def from_workflow(
        cls,
        workspace: Workspace,
        attachments: TurnAttachments,
        workflow: Workflow,
        workflow_name: str,
        name: str = "",
    ) -> Plan:
        """Build a Plan on a reusable Workflow; load prebaked Turns when named."""
        plan = cls.create(
            workspace=workspace,
            attachments=attachments,
            name=name or workflow_name,
            workflow=workflow,
            workflow_name=workflow_name,
        )
        plan._load_prebaked_turns(workflow_name)
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

    def _load_prebaked_turns(self, workflow_name: str) -> None:
        for template in _PREBAKED_WORKFLOWS.get(workflow_name, []):
            self.add_turn(
                action=template.action,
                fidelity=template.fidelity,
                format=template.format,
                context=template.context,
                tool_keys=list(template.tool_keys),
            )

    @prompt(name="plan")
    @agent_tool
    def plan(
        self,
        workflow: str = "",
        context: str = "",
        workspace: str = "",
    ) -> dict[str, str | int]:
        """Create a Plan based on a reusable Workflow name, or a new Workflow named here."""
        workflow_name = (workflow or "").strip() or "plan"
        return self._open_named_workflow(
            workflow_name=workflow_name,
            context=context,
            workspace_path=workspace,
        )

    @prompt(name="small-work")
    @agent_tool
    def small_work(self, context: str = "", workspace: str = "") -> dict[str, str | int]:
        """/plan /small-work {context} — load the prebaked small-work Workflow into a Plan.

        Does not execute against GitHub issues — only opens the Plan on that Workflow.
        """
        return self._open_named_workflow(
            workflow_name="small-work",
            context=context,
            workspace_path=workspace,
        )

    def _open_named_workflow(
        self,
        workflow_name: str,
        context: str,
        workspace_path: str,
    ) -> dict[str, str | int]:
        folder = (workspace_path or "").strip() or "."
        ws = Workspace(folder)
        ws.load()
        flow = Workflow(workspace=folder)
        attachments = TurnAttachments()
        built = Plan.from_workflow(
            workspace=ws,
            attachments=attachments,
            workflow=flow,
            workflow_name=workflow_name,
            name=workflow_name,
        )
        if context.strip():
            for turn in built.turns:
                existing = getattr(turn, "context", "") or ""
                turn.context = f"{existing} {context}".strip() if existing else context
        return {
            "plan": built.name,
            "workflow": workflow_name,
            "turns": len(built.turns),
            "workspace": folder,
            "context": context,
        }


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
