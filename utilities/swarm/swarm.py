# @toolset-manifest python -m tools manifest swarm.swarm:Swarm
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Swarm — Supervisor + Agents on a shared Plan turn slice; CliAgent is the worker."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cli_agent.cli_agent import CliAgent, IdeCli
from plan.plan import Plan
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


class Agent(CliAgent):
    """CliAgent running the Plan under one Hypothesis.

    Registered at Add Agent; CliAgent.launch_sessions starts at Plan.start on its WorkSession.
    Judge hangs on the Turn (JudgeCheckpoint) via CliAgent doer-judge — not judge-as-agent on Agent.
    """

    def __init__(
        self,
        hypothesis: Hypothesis,
        plan: Plan | None = None,
        work_session: WorkSession | None = None,
        ide: IdeCli | None = None,
        workspace: str = "",
        session: str = "",
    ) -> None:
        super().__init__(
            ide=ide or IdeCli(judge=True),
            workspace=workspace,
            session=session,
        )
        self.hypothesis = hypothesis
        self.plan = plan
        self._agent_work_session = work_session
        self._launched = False

    @property
    def launched(self) -> bool:
        return self._launched

    @property
    def agent_work_session(self) -> WorkSession | None:
        return self._agent_work_session

    def start_plan(
        self,
        workspace: Workspace,
        swarm_turns: list[Turn],
        *,
        plan_work_session: WorkSession | None = None,
        tools: list[object] | None = None,
        actions: list[object] | None = None,
    ) -> WorkSession:
        """Launch via CliAgent at Plan.start on this Agent's own WorkSession."""
        if self.plan is None:
            raise RuntimeError("Agent.start_plan requires a Plan")
        session = workspace.open_work_session(
            name=f"agent-{self.hypothesis.name}",
            path=getattr(workspace, "path", ".") or ".",
        )
        if plan_work_session is not None and session is plan_work_session:
            raise RuntimeError(
                "Agent WorkSession must not be the Plan Start Plan WorkSession"
            )
        self._agent_work_session = session
        self._launched = True
        if swarm_turns:
            first = swarm_turns[0]
            session.open_turn = first
        self.launch_sessions(tools=tools or [], actions=actions)
        return session

    def execute_turn(self) -> Turn | None:
        """Run Execute Plan on this Agent WorkSession (same stories as Plan.execute_turn)."""
        if self.plan is None:
            raise RuntimeError("Agent.execute_turn requires a Plan")
        previous = self.plan.work_session
        self.plan.work_session = self._agent_work_session
        try:
            return self.plan.execute_turn()
        finally:
            self.plan.work_session = previous


@agentic_toolset
class Supervisor:
    """Owns Outcome and rubric; compare reads Turn JudgeCheckpoint results — does not judge."""

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
        """Register the Agent; CliAgent has not launched yet."""
        workspace = ""
        if plan is not None and plan.workspace is not None:
            workspace = getattr(plan.workspace, "path", "") or ""
        agent = Agent(hypothesis=hypothesis, plan=plan, workspace=workspace)
        self.agents.append(agent)
        return agent

    def compare(self, event: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Stream after each Turn JudgeCheckpoint or HIL result; does not judge.

        Reads judge_result / validation from the event (CliAgent doer-judge already ran).
        Does not wait for all agents. Automatic associate follows each streamed compare.
        """
        if event is not None:
            payload = dict(event)
            payload.setdefault("outcome", self.outcome.name)
            payload.setdefault("rubric", self.rubric)
            turn = event.get("turn")
            if turn is not None:
                judge = getattr(turn, "judge_checkpoint", None)
                hil = getattr(turn, "hil_check", None)
                payload.setdefault(
                    "judge_result",
                    getattr(judge, "judge_result", None) if judge else None,
                )
                payload.setdefault(
                    "hil_validation",
                    getattr(hil, "validation", None) if hil else None,
                )
            payload.setdefault(
                "agent_progress",
                [
                    {
                        "hypothesis": a.hypothesis.name,
                        "launched": a.launched,
                        "open_turn": getattr(
                            getattr(a.agent_work_session, "open_turn", None),
                            "action",
                            None,
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
    that same slice on its own WorkSession. CliAgent.launch_sessions starts at Plan.start.
    Git is the store; Swarm is a front-end. Supervisor.compare reads Turn judge results.
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
