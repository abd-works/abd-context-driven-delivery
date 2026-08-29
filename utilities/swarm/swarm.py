# @toolset-manifest python -m tools manifest swarm.swarm:Swarm
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Swarm — Supervisor + Agents on a shared flow/ticket slice; CliAgent is the worker."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cli_agent.cli_agent import CliAgent, IdeCli
from plan.plan import Plan, PlanExecution
from primitives.actions.action import agentic_toolset
from workspace.workspace import Turn, WorkSession, Workspace


@dataclass
class Outcome:
    """Overarching result owned by Supervisor."""

    name: str


@dataclass
class Hypothesis:
    """Unique first-order approach toward the Supervisor Outcome."""

    name: str


@dataclass
class AgentProgress:
    """Snapshot of one Agent for Supervisor.compare."""

    hypothesis: str
    launched: bool
    open_turn: str | None


class Agent(CliAgent):
    """CliAgent running the Plan under one Hypothesis."""

    def __init__(
        self,
        hypothesis: Hypothesis,
        ide: IdeCli,
        plan: Plan | None = None,
        work_session: WorkSession | None = None,
        workspace: str = "",
        session: str = "",
    ) -> None:
        super().__init__(ide=ide, workspace=workspace, session=session)
        self._hypothesis = hypothesis
        self._plan = plan
        self._agent_work_session = work_session
        self._launched = False

    @property
    def hypothesis(self) -> Hypothesis:
        return self._hypothesis

    @property
    def plan(self) -> Plan | None:
        return self._plan

    @property
    def launched(self) -> bool:
        return self._launched

    @property
    def agent_work_session(self) -> WorkSession | None:
        return self._agent_work_session

    def start_plan(
        self,
        workspace: Workspace,
        swarm_tickets: list[int] | None = None,
        *,
        plan_work_session: WorkSession | None = None,
        tools: list[object] | None = None,
        actions: list[object] | None = None,
        swarm_turns: list[Turn] | None = None,
    ) -> WorkSession:
        """Run the shared flow/ticket slice on this Agent WorkSession (no planned-turn list)."""
        session = self._open_agent_session(workspace, plan_work_session)
        tickets = list(swarm_tickets or [])
        if not tickets and swarm_turns:
            # legacy test shim — prefer swarm_tickets
            self._bind_first_turn(session, swarm_turns)
        elif self._plan is not None and tickets:
            self._plan.tickets = list(tickets)  # type: ignore[attr-defined]
        self.launch_sessions(tools=tools or [], actions=actions)
        return session

    def execute_turn(self) -> Turn | None:
        if self._plan is None:
            raise RuntimeError("Agent.execute_turn requires a Plan")
        execution = PlanExecution(self._plan)
        previous = self._plan.work_session
        self._plan.work_session = self._agent_work_session
        try:
            return execution.execute_turn()
        finally:
            self._plan.work_session = previous

    def _open_agent_session(
        self, workspace: Workspace, plan_work_session: WorkSession | None
    ) -> WorkSession:
        if self._plan is None:
            raise RuntimeError("Agent.start_plan requires a Plan")
        session = workspace.open_work_session(
            name=f"agent-{self._hypothesis.name}",
            path=getattr(workspace, "path", ".") or ".",
        )
        if plan_work_session is not None and session is plan_work_session:
            raise RuntimeError(
                "Agent WorkSession must not be the Plan Start Plan WorkSession"
            )
        self._agent_work_session = session
        self._launched = True
        return session

    def _bind_first_turn(self, session: WorkSession, swarm_turns: list[Turn]) -> None:
        if swarm_turns:
            session.open_turn = swarm_turns[0]


@agentic_toolset
class Supervisor:
    """Owns Outcome and rubric; compare reads Turn JudgeCheckpoint results — does not judge."""

    def __init__(self, outcome: Outcome, rubric: str = "") -> None:
        self._outcome = outcome
        self._rubric = rubric
        self._agents: list[Agent] = []
        self._compare_events: list[dict[str, Any]] = []
        self._associations: list[Agent] = []

    @property
    def outcome(self) -> Outcome:
        return self._outcome

    @property
    def rubric(self) -> str:
        return self._rubric

    @property
    def agents(self) -> list[Agent]:
        return self._agents

    @property
    def compare_events(self) -> list[dict[str, Any]]:
        return list(self._compare_events)

    @property
    def associations(self) -> list[Agent]:
        return list(self._associations)

    def set_rubric(self, rubric: str) -> str:
        self._rubric = rubric
        return str(self._rubric)

    def add_agent(
        self, hypothesis: Hypothesis, plan: Plan | None, ide: IdeCli
    ) -> Agent:
        """Register the Agent; CliAgent has not launched yet."""
        workspace = ""
        if plan is not None and plan.workspace is not None:
            workspace = getattr(plan.workspace, "path", "") or ""
        agent = Agent(
            hypothesis=hypothesis, ide=ide, plan=plan, workspace=workspace
        )
        self._agents.append(agent)
        return agent

    def compare(self, event: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Stream after each Turn JudgeCheckpoint or HIL result; does not judge."""
        if event is not None:
            payload = self._payload_from_event(event)
            self._compare_events.append(payload)
            self.associate(payload)
        return list(self._compare_events)

    def associate(self, event: dict[str, Any] | None = None) -> list[Agent]:
        if event is None:
            return list(self._associations)
        agent = self._agent_from_event(event)
        if agent is not None and agent not in self._associations:
            self._associations.append(agent)
        return list(self._associations)

    def _agent_from_event(self, event: dict[str, Any]) -> Agent | None:
        agent = event.get("agent")
        return agent if isinstance(agent, Agent) else None

    def _payload_from_event(self, event: dict[str, Any]) -> dict[str, Any]:
        compare_event = dict(event)
        compare_event.setdefault("outcome", self._outcome.name)
        compare_event.setdefault("rubric", self._rubric)
        self._copy_turn_results(event, compare_event)
        compare_event.setdefault(
            "agent_progress",
            [self._progress_for(agent) for agent in self._agents],
        )
        return compare_event

    def _copy_turn_results(
        self, event: dict[str, Any], compare_event: dict[str, Any]
    ) -> None:
        turn = event.get("turn")
        if turn is None:
            return
        judge = getattr(turn, "judge_checkpoint", None)
        hil = getattr(turn, "hil_check", None)
        compare_event.setdefault(
            "judge_result",
            getattr(judge, "judge_result", None) if judge else None,
        )
        compare_event.setdefault(
            "hil_validation",
            getattr(hil, "validation", None) if hil else None,
        )

    def _progress_for(self, agent: Agent) -> dict[str, Any]:
        open_turn = getattr(agent.agent_work_session, "open_turn", None)
        view = AgentProgress(
            hypothesis=agent.hypothesis.name,
            launched=agent.launched,
            open_turn=getattr(open_turn, "action", None),
        )
        return {
            "hypothesis": view.hypothesis,
            "launched": view.launched,
            "open_turn": view.open_turn,
        }


@agentic_toolset
class Swarm:
    """Plan plus shared flow/ticket slice, Supervisor, and Agents. Front-end to git."""

    def __init__(self, plan: Plan | None = None) -> None:
        self._plan = plan
        self._tickets: list[int] = []
        self._turns: list[Turn] = []  # runtime Turns created by state entry — not planned
        self._supervisor: Supervisor | None = None
        self._agents: list[Agent] = []

    @property
    def plan(self) -> Plan | None:
        return self._plan

    @property
    def tickets(self) -> list[int]:
        return list(self._tickets)

    @property
    def turns(self) -> list[Turn]:
        """Runtime turns only; prefer tickets for the shared slice."""
        return self._turns

    @property
    def supervisor(self) -> Supervisor | None:
        return self._supervisor

    @property
    def agents(self) -> list[Agent]:
        return self._agents

    def create_supervisor(self, outcome: Outcome, rubric: str = "") -> Supervisor:
        supervisor = Supervisor(outcome=outcome, rubric=rubric)
        self._supervisor = supervisor
        return supervisor

    def select_tickets(self, tickets: list[int]) -> list[int]:
        """Select the shared flow/ticket slice once (no planned-turn list)."""
        self._tickets = list(tickets)
        if self._plan is not None:
            self._plan.tickets = list(tickets)  # type: ignore[attr-defined]
        return list(self._tickets)

    def select_turns(self, turns: list[Turn]) -> list[Turn]:
        """Deprecated — use select_tickets. Kept as empty runtime list setter for old callers."""
        self._turns = list(turns)
        return list(self._turns)

    def add_agent(self, hypothesis: Hypothesis, ide: IdeCli) -> Agent:
        if self._supervisor is None:
            raise RuntimeError("Swarm.add_agent requires a Supervisor")
        agent = self._supervisor.add_agent(
            hypothesis=hypothesis, plan=self._plan, ide=ide
        )
        self._agents.append(agent)
        return agent
