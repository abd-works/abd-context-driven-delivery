fidelity: discovery
scope: solution — plan + swarm utilities and git ticket-flow enhancement (ticket 23)
# Lenses in play: Stories + CE. DDD / UX / BDD omitted (operator confirmed).
# Contested forks detailed (ticks 1–4). Manage Ticket Flow remains scaffold. Remaining ? listed, not grilled.

flow:
  status: in-progress
  recommend: more-same-stage
  next: remaining ? only — no new grill this pass
  note: Story map and Increment 1 scenarios rewritten to PlannedTurn. Remaining ? is the PlannedTurn invocation bag only.
  open:
    - TODO PlannedTurn invocation bag (tool / action / fidelity / context)  #invocation-bag
  done:
    - pass #scaffold
    - pass #judge-shape
    - pass #swarm-slice
    - pass #hypothesis-own
    - pass #rubric-source

=========
theme: Compose Plan Sequence  (epic)
---------
stories:
    Compose Plan Sequence
        Practitioner --> Record Planned Turn
        Practitioner --> View Planned Turns
        Practitioner --> Add Judge Checkpoint
            // optional on PlannedTurn; not a distinct turn
        Practitioner --> Add Hip Checkpoint
            // optional on PlannedTurn; not a distinct turn; same attachment as judge
        Practitioner --> Start Plan
            // initiates WorkSession; no second session type
    ~> Increment 1: Compose a judged plan: Record Planned Turn, View Planned Turns, Add Judge Checkpoint, Add Hip Checkpoint, Start Plan
---
ce:
    utilities/plan/
      Plan
        workspace
        plannedTurns
        start
         -> Workspace.openWorkSession
         // start initiates WorkSession; never a second session type
      PlannedTurn
        ? contextTools actions fidelities context
        judgeCheckpoint
        hipCheckpoint
        // checkpoints optional; never distinct turns
        // after WorkSession.Turn.finish next PlannedTurn
      JudgeCheckpoint
      HipCheckpoint
      ----
      Workspace
        workSessions
        openWorkSession
      WorkSession
        turns
        openTurn
      Turn
        prompt
        result
        context
        toolCalls
        finish prompt result context
         // actual turn; Plan does not own Turn
=========

=========
theme: Manage Ticket Flow  (epic)
---------
stories:
    Manage Ticket Flow                        < scaffold
        Practitioner --> Record Research Tags < scaffold
        Practitioner --> Record Flow Notes    < scaffold
        Practitioner --> Update Ticket Status < scaffold
        Agent --> Resolve Ticket Number       < scaffold
    ~> Increment 2: Manage ticket flow on git: Record Research Tags, Record Flow Notes, Update Ticket Status, Resolve Ticket Number  < scaffold
---
ce:
    utilities/git/                            < scaffold
=========

=========
theme: Start Agent Swarm  (epic)
---------
stories:
    Start Agent Swarm                         < scaffold
        Supervisor --> Create Agent Swarm     < scaffold
        Supervisor --> Assign Agent Hypothesis
            // grill: Supervisor owns Outcome; Agent owns Hypothesis (approach)
            // not a single field on Agent, Supervisor map, or launch-time copy only
        Swarm agent --> Load Plan Context     < scaffold
        Swarm agent --> Run Planned Turns
            // grill: full Plan or selected PlannedTurns; issue “selected steps” maps here
    ~> Increment 3: Launch a plan swarm: Create Agent Swarm, Assign Agent Hypothesis, Load Plan Context, Run Planned Turns  < scaffold
---
ce:
    utilities/swarm/
      Swarm
        plan
        plannedTurns
        run
         -> Plan.plannedTurns
         // full Plan or slice of PlannedTurns; never a Step type
      Supervisor
        outcome
        rubric
        assignHypothesis agent
         -> Agent.hypothesis
         // Supervisor owns overarching Outcome; never the Agent approach
         // Supervisor rubric scores Outcome
      Agent
        hypothesis
        // “if we do this, we will achieve the Outcome”; unique first-order approach
      Hypothesis
=========

=========
theme: Compare Swarm Results  (epic)
---------
stories:
    Compare Swarm Results                     < scaffold
        Supervisor --> Collect Swarm Results  < scaffold
        Supervisor --> Compare Agent Outcomes < scaffold
        Supervisor --> Review Supervisor Rubric
            // grill: Supervisor rubric scores Outcome; not each Hypothesis
        Supervisor --> Review Plan Judges
            // grill: Plan JudgeCheckpoint rubrics score PlannedTurns; and/or Supervisor rubric
    ~> Increment 4: Compare swarm results: Collect Swarm Results, Compare Agent Outcomes, Review Supervisor Rubric, Review Plan Judges  < scaffold
---
ce:
    utilities/swarm/
      Supervisor
        rubric
        compare
         -> outcome
         // Supervisor rubric scores Outcome
         -> PlannedTurn.judgeCheckpoint
         // and/or Plan JudgeCheckpoint rubrics score PlannedTurns
         // never Supervisor rubric on each Hypothesis
=========

## log
- discovery / solution / whole-design / pass #scaffold
- discovery / Compose Plan Sequence / pass #judge-shape — Other: Plan↔Workspace; Plan holds PlannedTurns; start → WorkSession; actual Turn after close → next PlannedTurn; JudgeCheckpoint/HipCheckpoint optional on PlannedTurn, not distinct turns
- story map + Increment 1 scenarios rewritten to PlannedTurn; Start Plan added; session lives at utilities/swarm/.context/plan-and-swarm-utilities-23/
- discovery / Start Agent Swarm / pass #swarm-slice — Selected PlannedTurns: Swarm runs full Plan or a PlannedTurn slice; issue “selected steps” maps here; no Step type
- discovery / Start Agent Swarm / pass #hypothesis-own — Other: split — Supervisor.outcome (overarching); Agent.hypothesis (approach “if we do this we achieve Outcome”)
- discovery / Compare Swarm Results / pass #rubric-source — Either, different targets: Supervisor rubric → Outcome; Plan JudgeCheckpoint rubrics → PlannedTurns
