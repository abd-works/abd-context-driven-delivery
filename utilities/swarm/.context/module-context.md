# utilities/swarm — module context

## Purpose

Runs a Plan (or a shared slice of Turns held on Swarm.turns, selected once before any Agent runs) with several SubAgents at once. An Agent is a SubAgent executing that Plan under one Hypothesis. Add Agent registers the Agent; SubAgent.run launches at Plan.start on the Agent’s own WorkSession. A Hypothesis is the first-order approach — which existing context tool, action, and fidelity that Agent believes will achieve the Supervisor’s Outcome. Supervisor.compare streams after each Judge or HIL evaluation; Supervisor.associate updates automatically under the Supervisor rubric toward Outcome. Launch uses the existing `sub_agent` non-blocking seam.

## Primary use case

Create Supervisor with Outcome and rubric, select shared Swarm.turns once, Add Agent with Hypothesis (register only), start each Agent Plan so SubAgent.run launches on that Agent WorkSession, stream Compare after Judge/HIL, associate automatically toward Outcome.

## Rationale

Swarm reuses Execute Plan stories on each Agent WorkSession. Shared turn slice is one selection for the whole Swarm. Mid-run Add Agent registers without launch until that Agent starts the Plan.

## Seam

Swarm, Supervisor, Agent, Hypothesis, Outcome

## Public API

- `Swarm` — `plan`, `turns` (shared slice), `supervisor`, `agents`; `create_supervisor`, `select_turns`, `add_agent`
- `Supervisor` — `outcome`, `rubric`, `agents`, `compare_events`, `associations`; `set_rubric`, `add_agent(hypothesis)`, `compare(event)`, `associate(event)`
- `Agent` — `plan`, `hypothesis`, `work_session`, `launched` (SubAgent; register at add; `start_plan` launches `SubAgent.run`; `execute_turn` runs Execute Plan on that WorkSession)
- `Hypothesis` — unique first-order approach toward Outcome
- `Outcome` — overarching result owned by Supervisor

## Dependencies

- `plan`, `sub_agent` (one-way)
