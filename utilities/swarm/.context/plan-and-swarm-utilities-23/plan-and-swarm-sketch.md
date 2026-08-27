fidelity: exploration
scope: solution — plan + swarm utilities and git ticket-flow enhancement (ticket 23)
# Lenses: Stories + CE. Increment 1 BDDs absorbed from generated scenarios (files left in place). Increment 2 now sketched.

flow:
  status: in-progress
  recommend: more-same-stage
  next: grill Increment 2 only if notes-vs-tags surface forks; else Increment 3 swarm BDDs
  note: Generated Increment 1 scenario files remain under scenarios/…/compose-plan-sequence/. Sketch is the working BDD tree.
  open:
    - TODO PlannedTurn invocation bag (tool / action / fidelity / context)  #invocation-bag
    - TODO Increment 3 story BDDs  #inc3
    - TODO Increment 4 story BDDs  #inc4
  done:
    - pass #scaffold
    - pass #judge-shape
    - pass #swarm-slice
    - pass #hypothesis-own
    - pass #rubric-source
    - pass #inc1-bdd
    - pass #inc2-sketch

=========
theme: Compose Plan Sequence  (epic)
---------
stories:
    Compose Plan Sequence
        Practitioner --> Record Planned Turn
            planned turn is on the plan with context tool, action, fidelity, and context
                given a Plan compose-judged-plan associated with a Workspace
                when the operator records a PlannedTurn on that Plan
                    and context tool Stories
                    and action generate
                    and fidelity story_map
                    and context plan-and-swarm-utilities-23
                then that Plan shows the PlannedTurn in sequence
                    and that PlannedTurn names those four fields
                    and that PlannedTurn is not a JudgeCheckpoint
                    and that PlannedTurn is not a HipCheckpoint
            later planned turn follows the earlier planned turn
                given a Plan compose-judged-plan associated with a Workspace
                    and that Plan already has a PlannedTurn Stories generate story_map
                when the operator records a PlannedTurn CleanEngineering generate modules
                then that Plan shows the Stories PlannedTurn before the CleanEngineering PlannedTurn
        Practitioner --> View Planned Turns
            ordered planned turns show context tool, action, fidelity, and context
                given a Plan with a PlannedTurn Stories generate story_map
                    and a later PlannedTurn CleanEngineering generate modules
                when the operator views PlannedTurns on that Plan
                then that Plan shows Stories before CleanEngineering
                    and each PlannedTurn shows its four fields
            view shows checkpoints on the planned turn they belong to
                given a first PlannedTurn with a JudgeCheckpoint rubric stories-scenarios
                    and a later PlannedTurn with a HipCheckpoint
                when the operator views PlannedTurns on that Plan
                then the JudgeCheckpoint is on the first PlannedTurn
                    and the HipCheckpoint is on the later PlannedTurn
                    and neither checkpoint appears as its own PlannedTurn
        Practitioner --> Add Judge Checkpoint
            judge checkpoint hangs on the planned turn
                given a Plan with a PlannedTurn Stories generate story_map
                when the operator adds a JudgeCheckpoint to that PlannedTurn against rubric stories-scenarios
                then that PlannedTurn has the JudgeCheckpoint
                    and the Plan does not gain another PlannedTurn
                    and that JudgeCheckpoint is not a HipCheckpoint
            later planned turn can have its own judge checkpoint
                given a PlannedTurn that already has JudgeCheckpoint stories-scenarios
                    and a later PlannedTurn CleanEngineering generate modules
                when the operator adds a JudgeCheckpoint to the later PlannedTurn against rubric plan-modules
                then the first PlannedTurn still has stories-scenarios
                    and the later PlannedTurn has plan-modules
                    and neither JudgeCheckpoint is its own PlannedTurn
        Practitioner --> Add Hip Checkpoint
            hip checkpoint hangs on the planned turn
                given a Plan with a PlannedTurn Stories generate story_map
                when the operator adds a HipCheckpoint to that PlannedTurn
                then that PlannedTurn has the HipCheckpoint
                    and the Plan does not gain another PlannedTurn
                    and that HipCheckpoint is not a JudgeCheckpoint
            planned turn can hold both checkpoints
                given a PlannedTurn that already has a JudgeCheckpoint stories-scenarios
                when the operator adds a HipCheckpoint to that PlannedTurn
                then that PlannedTurn has the JudgeCheckpoint and the HipCheckpoint
                    and the Plan still has one PlannedTurn
                    and the HipCheckpoint is not an AI judge
        Practitioner --> Start Plan
            starting the plan opens a work session
                given a Plan compose-judged-plan associated with a Workspace
                    and that Plan has a PlannedTurn Stories generate story_map
                when the operator starts that Plan
                then that Workspace has a WorkSession for that Plan
                    and that WorkSession is not a second session type
                    and that Plan still holds the same PlannedTurns
            after the actual turn finishes the next planned turn is due
                given a Plan with Stories then CleanEngineering PlannedTurns
                    and the operator has started that Plan so a WorkSession is open
                when the WorkSession Turn for the first PlannedTurn finishes
                then the next PlannedTurn due is the CleanEngineering PlannedTurn
                    and the finished Turn remains an actual Turn on the WorkSession
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
    Manage Ticket Flow
        Practitioner --> Record Research Tags
            research tags live on the existing ticket
                given a Repo with a Ticket number 23
                when the operator records a ResearchTag thin-templates on that Ticket
                then that Ticket holds ResearchTag thin-templates
                    and that Ticket number is still 23
                    and there is no second ticket store
        Practitioner --> Record Flow Notes
            flow notes live on the existing ticket
                given a Repo with a Ticket number 23
                when the operator records a flow note swarm-slice-planned-turns on that Ticket
                then that Ticket shows the flow note swarm-slice-planned-turns
                    and identity remains GitHub issue 23
                    and eval-mistakes notes are not the flow-note surface
        Practitioner --> Update Ticket Status
            ticket status is an existing project state
                given a Repo with a Ticket number 23
                    and an attached Project
                    and that Ticket TicketState is Backlog
                when the operator sets that Ticket status to In Progress
                then that Ticket TicketState is In Progress
                    and the states remain Backlog, In Progress, Done
        Agent --> Resolve Ticket Number
            ticket number resolves from a github issue ref
                given a Repo
                when the agent resolves ticket ref #23
                then the Ticket number is 23
                    // same mechanic for owner/repo#23 and issues URL — examples, not extra stories
    ~> Increment 2: Manage ticket flow on git: Record Research Tags, Record Flow Notes, Update Ticket Status, Resolve Ticket Number
---
ce:
    utilities/git/
      Repo
        ticket
        note
        readNotes
      Ticket
        number
        researchTags
        notes
        state
        setStatus
        parseNumber
        // identity is GitHub issue #; no parallel yaml
      ResearchTag
        // git-primary notes + trailers — not Ticket.data as SoT
      TicketState
        // Backlog | In Progress | Done only
      Project
=========

=========
theme: Start Agent Swarm  (epic)
---------
stories:
    Start Agent Swarm                         < scaffold
        Supervisor --> Create Agent Swarm     < scaffold
        Supervisor --> Assign Agent Hypothesis
            // grill: Supervisor owns Outcome; Agent owns Hypothesis (approach)
        Swarm agent --> Load Plan Context     < scaffold
        Swarm agent --> Run Planned Turns
            // grill: full Plan or selected PlannedTurns
    ~> Increment 3: Launch a plan swarm: Create Agent Swarm, Assign Agent Hypothesis, Load Plan Context, Run Planned Turns  < scaffold
---
ce:
    utilities/swarm/
      Swarm
        plan
        plannedTurns
        run
         -> Plan.plannedTurns
      Supervisor
        outcome
        rubric
        assignHypothesis agent
         -> Agent.hypothesis
      Agent
        hypothesis
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
            // Supervisor rubric scores Outcome
        Supervisor --> Review Plan Judges
            // Plan JudgeCheckpoint rubrics score PlannedTurns; and/or Supervisor rubric
    ~> Increment 4: Compare swarm results: Collect Swarm Results, Compare Agent Outcomes, Review Supervisor Rubric, Review Plan Judges  < scaffold
---
ce:
    utilities/swarm/
      Supervisor
        rubric
        compare
         -> outcome
         -> PlannedTurn.judgeCheckpoint
=========

## log
- discovery / solution / whole-design / pass #scaffold
- discovery / Compose Plan Sequence / pass #judge-shape
- exploration / Compose Plan Sequence / pass #inc1-bdd — absorbed generated Increment 1 scenarios into stories notation; files left on disk
- exploration / Manage Ticket Flow / pass #inc2-sketch — main-flow BDDs; tags + notes on existing Ticket; status is existing TicketState; resolve is parse_number
- discovery / Start Agent Swarm / pass #swarm-slice
- discovery / Start Agent Swarm / pass #hypothesis-own
- discovery / Compare Swarm Results / pass #rubric-source
