# @toolset-manifest python -m tools manifest plan.plan:Plan
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Plan — front-end to git; based on a reusable or named Workflow."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from git.git import Repo, TicketState
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


@dataclass
class PlanSeed:
    """Construction seed for Plan.create / from_workflow."""

    workspace: Workspace
    attachments: TurnAttachments
    name: str = ""
    workflow: Workflow | None = None
    workflow_name: str = ""


_PREBAKED_WORKFLOWS: dict[str, list[TurnTemplate]] = {
    "small-work": [
        TurnTemplate(
            action="Generate",
            fidelity="behavior",
            format="markdown",
            context="root-cause",
            tool_keys=["context_tools.bdd.bdd:Bdd"],
        ),
        TurnTemplate(
            action="Generate",
            fidelity="scenarios",
            format="markdown",
            context="fix-one-issue",
            tool_keys=["context_tools.bdd.bdd:Bdd"],
        ),
    ],
}


class Plan:
    """Plan front-end to git, based on a reusable or newly named Workflow."""

    def __init__(self, seed: PlanSeed) -> None:
        self._attachments = seed.attachments
        self._name = seed.name
        self._workspace = seed.workspace
        self._workflow = seed.workflow
        self._workflow_name = seed.workflow_name
        self._turns: list[Turn] = []
        self._work_session: WorkSession | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> Workspace | None:
        return self._workspace

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
    def create(cls, seed: PlanSeed) -> Plan:
        plan = cls(seed)
        cls._register_on_workspace(plan)
        return plan

    @classmethod
    def from_workflow(cls, seed: PlanSeed) -> Plan:
        """Build a Plan on a reusable Workflow; load prebaked Turns when named."""
        if not seed.name:
            seed = PlanSeed(
                workspace=seed.workspace,
                attachments=seed.attachments,
                name=seed.workflow_name,
                workflow=seed.workflow,
                workflow_name=seed.workflow_name,
            )
        plan = cls.create(seed)
        plan._load_prebaked_turns(seed.workflow_name)
        return plan

    @staticmethod
    def _register_on_workspace(plan: Plan) -> None:
        workspace = plan.workspace
        if workspace is None:
            return
        plans = getattr(workspace, "plans", None)
        if plans is None:
            workspace.plans = []  # type: ignore[attr-defined]
            plans = workspace.plans
        plans.append(plan)

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

    def _load_prebaked_turns(self, workflow_name: str) -> None:
        for template in _PREBAKED_WORKFLOWS.get(workflow_name, []):
            self.add_turn(
                action=template.action,
                fidelity=template.fidelity,
                format=template.format,
                context=template.context,
                tool_keys=list(template.tool_keys),
            )


class PlanTurns:
    """Edit and delete Turns on a Plan."""

    def __init__(self, plan: Plan) -> None:
        self._plan = plan

    def edit(self, turn: Turn, **fields: Any) -> Turn:
        for field_name, field_value in fields.items():
            setattr(turn, field_name, field_value)
        return turn

    def delete(self, turn: Turn) -> None:
        turns = self._plan._turns
        if turn in turns:
            turns.remove(turn)


_ENOUGH_MARKERS = (
    "## root cause",
    "## acceptance",
    "## context",
    "reproduction:",
    "expected:",
)
_MIN_ENOUGH_CHARS = 160
_THEME_RE = re.compile(
    r"(?:^|\s)(?:theme:|theme\s*=\s*)(?P<theme>[\w./-]+)",
    re.IGNORECASE,
)


@dataclass
class ThemedIssue:
    """One GitHub (or fixture) issue under a theme label."""

    number: int
    title: str
    body: str
    labels: list[str] = field(default_factory=list)

    @property
    def context_enough(self) -> bool:
        return SmallWorkRunner.enough_context(self.body)


@dataclass
class SmallWorkState:
    """Persisted small-work run across HIL Grill interrupts."""

    theme: str
    issues: list[dict[str, Any]]
    index: int = 0
    report: list[dict[str, Any]] = field(default_factory=list)
    pending_hil: dict[str, Any] | None = None
    grill_questions: list[str] = field(default_factory=list)
    status: str = "running"


class SmallWorkRunner:
    """Execute prebaked small-work Plan against themed issues one at a time.

    Thin context → Grill + HIL Grill interrupt (judge replies via hil_reply).
    Enough context → process issue, advance to next. Report when Done.
    """

    def __init__(
        self,
        workspace: str = ".",
        *,
        issues: list[ThemedIssue] | None = None,
        state_path: Path | None = None,
    ) -> None:
        self._workspace = (workspace or ".").strip() or "."
        self._fixture_issues = issues
        self._state_path = state_path or (
            Path(self._workspace) / ".context" / "small-work-run.json"
        )

    @staticmethod
    def parse_theme(context: str) -> str:
        text = (context or "").strip()
        if not text:
            return ""
        match = _THEME_RE.search(text)
        if match:
            return match.group("theme").strip()
        if text.startswith("theme:"):
            return text.split(":", 1)[1].strip()
        return text

    @staticmethod
    def enough_context(body: str) -> bool:
        text = (body or "").strip()
        if not text:
            return False
        lowered = text.lower()
        if any(marker in lowered for marker in _ENOUGH_MARKERS):
            return True
        return len(text) >= _MIN_ENOUGH_CHARS

    @staticmethod
    def grill_questions_for(issue: ThemedIssue) -> list[str]:
        return [
            f"What is the root cause for #{issue.number} ({issue.title})?",
            "What acceptance criteria prove the fix?",
            "Which module owns the change?",
        ]

    def state_path(self) -> Path:
        return self._state_path

    def load_state(self) -> SmallWorkState | None:
        path = self._state_path
        if not path.is_file():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        return SmallWorkState(**raw)

    def save_state(self, state: SmallWorkState) -> None:
        path = self._state_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")

    def clear_state(self) -> None:
        path = self._state_path
        if path.is_file():
            path.unlink()

    def list_themed_issues(self, theme: str) -> list[ThemedIssue]:
        if self._fixture_issues is not None:
            label = theme if theme.startswith("theme:") else f"theme:{theme}"
            bare = theme.removeprefix("theme:")
            return [
                issue
                for issue in self._fixture_issues
                if label in issue.labels
                or bare in issue.labels
                or f"theme:{bare}" in issue.labels
            ]
        return self._list_from_gh(theme)

    def _list_from_gh(self, theme: str) -> list[ThemedIssue]:
        label = theme if theme.startswith("theme:") else f"theme:{theme}"
        raw = Repo.gh(
            "issue",
            "list",
            "--label",
            label,
            "--state",
            "open",
            "--json",
            "number,title,body,labels",
            "--limit",
            "50",
            cwd=self._workspace,
        )
        rows = json.loads(raw or "[]")
        issues: list[ThemedIssue] = []
        for row in rows:
            labels = [
                str(item.get("name") or item)
                for item in (row.get("labels") or [])
            ]
            issues.append(
                ThemedIssue(
                    number=int(row["number"]),
                    title=str(row.get("title") or ""),
                    body=str(row.get("body") or ""),
                    labels=labels,
                )
            )
        return sorted(issues, key=lambda item: item.number)

    def run(
        self,
        theme: str,
        *,
        hil_reply: str = "",
        issue: str | int = "",
        plan_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        theme_name = theme.removeprefix("theme:")
        state = self.load_state()
        if hil_reply.strip():
            if state is None or state.pending_hil is None:
                raise RuntimeError(
                    "hil_reply requires a pending HIL Grill interrupt "
                    "(judge replies; parent does not)"
                )
            return self._continue_with_hil(state, hil_reply, plan_meta=plan_meta)

        if state is not None and state.status == "hil_interrupt" and not hil_reply:
            return self._interrupt_payload(state, plan_meta=plan_meta)

        issues = self.list_themed_issues(theme_name)
        wanted = str(issue or "").strip()
        if wanted:
            number = int("".join(ch for ch in wanted if ch.isdigit()) or "0")
            issues = [item for item in issues if item.number == number]
            if not issues:
                raise RuntimeError(
                    f"no themed issue #{number} under theme:{theme_name}"
                )
        state = SmallWorkState(
            theme=theme_name,
            issues=[asdict(item) for item in issues],
            index=0,
            report=[],
            pending_hil=None,
            grill_questions=[],
            status="running",
        )
        self.save_state(state)
        return self._advance(state, plan_meta=plan_meta)

    def _continue_with_hil(
        self,
        state: SmallWorkState,
        hil_reply: str,
        *,
        plan_meta: dict[str, Any] | None,
    ) -> dict[str, Any]:
        pending = state.pending_hil or {}
        number = int(pending["number"])
        issue_row = state.issues[state.index]
        enriched = (
            f"{issue_row.get('body') or ''}\n\n"
            f"## Grill answers (judge HIL reply)\n\n{hil_reply.strip()}\n"
        )
        issue_row["body"] = enriched
        state.issues[state.index] = issue_row
        state.report.append(
            {
                "number": number,
                "title": issue_row.get("title") or "",
                "outcome": "hil_filled",
                "context_enough": False,
                "hil_reply_by": "judge",
            }
        )
        state.pending_hil = None
        state.grill_questions = []
        # Process this issue now that context is filled, then advance.
        self._complete_issue(state, ThemedIssue(**issue_row))
        state.index += 1
        state.status = "running"
        self.save_state(state)
        return self._advance(state, plan_meta=plan_meta)

    def _advance(
        self,
        state: SmallWorkState,
        *,
        plan_meta: dict[str, Any] | None,
    ) -> dict[str, Any]:
        while state.index < len(state.issues):
            row = state.issues[state.index]
            issue = ThemedIssue(**row)
            if not issue.context_enough:
                questions = self.grill_questions_for(issue)
                hil = HILCheck(
                    validation=(
                        "HIL Grill — judge must reply with enough context "
                        f"for #{issue.number} before work continues"
                    )
                )
                state.pending_hil = {
                    "number": issue.number,
                    "title": issue.title,
                    "validation": hil.validation,
                    "replier": "judge",
                }
                state.grill_questions = questions
                state.status = "hil_interrupt"
                self.save_state(state)
                return self._interrupt_payload(state, plan_meta=plan_meta)

            self._complete_issue(state, issue)
            state.index += 1
            self.save_state(state)

        state.status = "done"
        self.save_state(state)
        return self._done_payload(state, plan_meta=plan_meta)

    def _complete_issue(self, state: SmallWorkState, issue: ThemedIssue) -> None:
        # Logical Workflow spine: Backlog → In Progress → Done (no live branch).
        state.report.append(
            {
                "number": issue.number,
                "title": issue.title,
                "outcome": "done",
                "context_enough": issue.context_enough,
                "ticket_flow": ["Backlog", "In Progress", "Done"],
            }
        )

    def _interrupt_payload(
        self,
        state: SmallWorkState,
        *,
        plan_meta: dict[str, Any] | None,
    ) -> dict[str, Any]:
        pending = state.pending_hil or {}
        payload: dict[str, Any] = {
            "status": "hil_interrupt",
            "theme": state.theme,
            "themed_source": f"theme:{state.theme}",
            "current_issue": pending.get("number"),
            "grill": True,
            "hil_grill": True,
            "hil_replier": "judge",
            "grill_questions": list(state.grill_questions),
            "hil_validation": pending.get("validation"),
            "mixed_context": True,
            "report": list(state.report),
            "remaining": len(state.issues) - state.index,
        }
        if plan_meta:
            payload.update(plan_meta)
        return payload

    def _done_payload(
        self,
        state: SmallWorkState,
        *,
        plan_meta: dict[str, Any] | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": "done",
            "theme": state.theme,
            "themed_source": f"theme:{state.theme}",
            "mixed_context": any(
                not item.get("context_enough", True)
                or item.get("outcome") == "hil_filled"
                for item in state.report
            )
            or any(
                not SmallWorkRunner.enough_context(str(row.get("body") or ""))
                for row in state.issues
            ),
            "report": list(state.report),
            "issues_done": sum(
                1 for item in state.report if item.get("outcome") == "done"
            ),
            "hil_interrupts": sum(
                1 for item in state.report if item.get("outcome") == "hil_filled"
            ),
        }
        if plan_meta:
            payload.update(plan_meta)
        self.clear_state()
        return payload


@agentic_toolset
class PlanCommands:
    """Slash `/plan` and `/plan /small-work {context}` — load Workflow into a Plan."""

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
        return self._open_named_workflow(workflow_name, context, workspace)

    @prompt(name="small-work")
    @agent_tool
    def small_work(
        self,
        context: str = "",
        workspace: str = "",
        hil_reply: str = "",
        issue: str = "",
        issues: list | None = None,
    ) -> dict[str, Any]:
        """/plan /small-work {context} — load small-work Workflow; run themed tickets when theme is set.

        With ``theme:…`` in context, processes that theme's issues. Pass ``issue`` to run
        one ticket only (one Turn). Thin context triggers Grill + HIL Grill; the judge
        (not the parent) replies via ``hil_reply``. Fixture ``issues`` may be passed for
        Agent BDD. Without a theme, only opens the Plan on the prebaked Workflow.
        """
        opened = self._open_named_workflow("small-work", context, workspace)
        theme = SmallWorkRunner.parse_theme(context)
        if not theme and not hil_reply.strip() and issues is None and not str(issue or "").strip():
            return opened

        fixture: list[ThemedIssue] | None = None
        if issues is not None:
            fixture = [
                ThemedIssue(
                    number=int(row["number"]),
                    title=str(row.get("title") or ""),
                    body=str(row.get("body") or ""),
                    labels=list(row.get("labels") or []),
                )
                for row in issues
            ]
        runner = SmallWorkRunner(workspace=workspace or ".", issues=fixture)
        if not theme and hil_reply.strip():
            state = runner.load_state()
            theme = state.theme if state else ""
        if not theme:
            return opened
        return runner.run(
            theme,
            hil_reply=hil_reply,
            issue=issue,
            plan_meta=dict(opened),
        )

    def _open_named_workflow(
        self,
        workflow_name: str,
        context: str,
        workspace_path: str,
    ) -> dict[str, str | int]:
        seed = self._seed_for(workflow_name, workspace_path)
        built = Plan.from_workflow(seed)
        self._apply_context(built, context)
        return {
            "plan": built.name,
            "workflow": workflow_name,
            "turns": len(built.turns),
            "workspace": seed.workspace.path if hasattr(seed.workspace, "path") else workspace_path or ".",
            "context": context,
        }

    def _seed_for(self, workflow_name: str, workspace_path: str) -> PlanSeed:
        folder = (workspace_path or "").strip() or "."
        working_folder = Workspace(folder)
        working_folder.load()
        return PlanSeed(
            workspace=working_folder,
            attachments=TurnAttachments(),
            name=workflow_name,
            workflow=Workflow(workspace=folder),
            workflow_name=workflow_name,
        )

    def _apply_context(self, built: Plan, context: str) -> None:
        if not context.strip():
            return
        for turn in built.turns:
            existing = getattr(turn, "context", "") or ""
            turn.context = f"{existing} {context}".strip() if existing else context


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
