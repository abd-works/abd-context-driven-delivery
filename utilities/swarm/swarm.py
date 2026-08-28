# @toolset-manifest python -m tools manifest swarm.swarm:Swarm
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Swarm — Supervisor + Agents on a shared Plan turn slice."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from plan.plan import Plan
from primitives.actions.action import agentic_toolset
from sub_agent.sub_agent import SubAgent
from workspace.workspace import Turn, WorkSession, Workspace


@dataclass
class Outcome:
    """Overarching result owned by Supervisor."""

    name: str


@dataclass
class Hypothesis:
    """Unique first-order approach toward the Supervisor Outcome."""

    name: str


class Agent(SubAgent):
    """SubAgent running the Plan under one Hypothesis.

    Registered at Add Agent; SubAgent.run launches at Plan.start on its WorkSession.
    Each Agent runs the shared Swarm.turns slice on its own WorkSession (Execute Plan).
    """

    def __init__(
        self,
        hypothesis: Hypothesis,
        plan: Plan | None = None,
        work_session: WorkSession | None = None,
    ) -> None:
        super().__init__()
        self.hypothesis = hypothesis
        self.plan = plan
        self.work_session = work_session
        self._launched = False

    @property
    def launched(self) -> bool:
        return self._launched

    def start_plan(
        self,
        workspace: Workspace,
        swarm_turns: list[Turn],
        *,
        plan_work_session: WorkSession | None = None,
    ) -> WorkSession:
        """Launch SubAgent.run at Plan.start on this Agent's own WorkSession."""
        if self.plan is None:
            raise RuntimeError("Agent.start_plan requires a Plan")
        session = workspace.open_work_session(
            name=f"agent-{self.hypothesis.name}",
            path=getattr(workspace, "path", ".") or ".",
        )
        if plan_work_session is not None and session is plan_work_session:
            raise RuntimeError("Agent WorkSession must not be the Plan Start Plan WorkSession")
        self.work_session = session
        self._launched = True
        if swarm_turns:
            first = swarm_turns[0]
            session.open_turn = first
        self.run(tools=[], actions=[])
        return session

    def execute_turn(self) -> Turn | None:
        """Run Execute Plan on this Agent WorkSession (same stories as Plan.execute_turn)."""
        if self.plan is None:
            raise RuntimeError("Agent.execute_turn requires a Plan")
        previous = self.plan.work_session
        self.plan.work_session = self.work_session
        try:
            return self.plan.execute_turn()
        finally:
            self.plan.work_session = previous


@agentic_toolset
class Supervisor:
    """Owns Outcome and rubric; compare streams; associate updates toward Outcome."""

    def __init__(self, outcome: Outcome, rubric: str = "") -> None:
        self.outcome = outcome
        self.rubric = rubric
        self.agents: list[Agent] = []
        self.compare_events: list[dict[str, Any]] = []
        self.associations: list[Agent] = []

    def set_rubric(self, rubric: str) -> str:
        self.rubric = rubric
        return self.rubric

    def add_agent(self, hypothesis: Hypothesis, plan: Plan | None = None) -> Agent:
        """Register the Agent; SubAgent.run has not launched yet."""
        agent = Agent(hypothesis=hypothesis, plan=plan)
        self.agents.append(agent)
        return agent

    def compare(self, event: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Stream after each Judge or HIL evaluation; does not wait for all agents.

        Automatic associate follows each streamed compare under the Supervisor rubric
        toward Outcome. May include Plan Turn JudgeCheckpoint rubric evaluations.
        """
        if event is not None:
            payload = dict(event)
            payload.setdefault("outcome", self.outcome.name)
            payload.setdefault("rubric", self.rubric)
            payload.setdefault(
                "agent_progress",
                [
                    {
                        "hypothesis": a.hypothesis.name,
                        "launched": a.launched,
                        "open_turn": getattr(
                            getattr(a.work_session, "open_turn", None), "action", None
                        ),
                    }
                    for a in self.agents
                ],
            )
            self.compare_events.append(payload)
            self.associate(payload)
        return list(self.compare_events)

    def associate(self, event: dict[str, Any] | None = None) -> list[Agent]:
        """Update automatically after each streamed compare toward Outcome."""
        agent = None if event is None else event.get("agent")
        if isinstance(agent, Agent) and agent not in self.associations:
            self.associations.append(agent)
        return list(self.associations)


@agentic_toolset
class Swarm:
    """Plan plus shared turns slice, Supervisor, and Agents.

    Shared Swarm.turns is selected once before any Agent runs. Each Agent runs
    that same slice on its own WorkSession. SubAgent.run launches at Plan.start.
    """

    def __init__(self, plan: Plan | None = None) -> None:
        self.plan = plan
        self.turns: list[Turn] = []
        self.supervisor: Supervisor | None = None
        self.agents: list[Agent] = []

    def create_supervisor(self, outcome: Outcome, rubric: str = "") -> Supervisor:
        self.supervisor = Supervisor(outcome=outcome, rubric=rubric)
        return self.supervisor

    def select_turns(self, turns: list[Turn]) -> list[Turn]:
        """Shared turn slice selected once before any Agent runs."""
        self.turns = list(turns)
        return self.turns

    def add_agent(self, hypothesis: Hypothesis) -> Agent:
        if self.supervisor is None:
            raise RuntimeError("Swarm.add_agent requires a Supervisor")
        agent = self.supervisor.add_agent(hypothesis=hypothesis, plan=self.plan)
        self.agents.append(agent)
        return agent
