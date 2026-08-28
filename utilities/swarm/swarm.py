# @toolset-manifest python -m tools manifest swarm.swarm:Swarm
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Swarm — Supervisor + Agents on a shared Plan turn slice."""
from __future__ import annotations

from dataclasses import dataclass
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

    def start_plan(self, workspace: Workspace, swarm_turns: list[Turn]) -> WorkSession:
        """Launch SubAgent.run at Plan.start on this Agent's own WorkSession."""
        if self.plan is None:
            raise RuntimeError("Agent.start_plan requires a Plan")
        session = workspace.open_work_session(
            name=f"agent-{self.hypothesis.name}",
            path=getattr(workspace, "path", ".") or ".",
        )
        self.work_session = session
        self._launched = True
        if swarm_turns:
            first = swarm_turns[0]
            session.open_turn = first
        self.run(tools=[], actions=[])
        return session


@agentic_toolset
class Supervisor:
    """Owns Outcome and rubric; compare streams; associate updates toward Outcome."""

    def __init__(self, outcome: Outcome, rubric: str = "") -> None:
        self.outcome = outcome
        self.rubric = rubric
        self.agents: list[Agent] = []
        self.compare_events: list[dict[str, Any]] = []
        self.associations: list[Agent] = []

    def add_agent(self, hypothesis: Hypothesis, plan: Plan | None = None) -> Agent:
        """Register the Agent; SubAgent.run has not launched yet."""
        agent = Agent(hypothesis=hypothesis, plan=plan)
        self.agents.append(agent)
        return agent

    def compare(self, event: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Stream after each Judge or HIL evaluation; does not wait for all agents."""
        if event is not None:
            self.compare_events.append(event)
            self.associate(event)
        return list(self.compare_events)

    def associate(self, event: dict[str, Any] | None = None) -> list[Agent]:
        """Update automatically after each streamed compare toward Outcome."""
        agent = None if event is None else event.get("agent")
        if isinstance(agent, Agent) and agent not in self.associations:
            self.associations.append(agent)
        return list(self.associations)


@agentic_toolset
class Swarm:
    """Plan plus shared turns slice, Supervisor, and Agents."""

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
