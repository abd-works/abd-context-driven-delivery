fidelity: exploration
scope: solution — plan + swarm utilities and git ticket-flow enhancement (ticket 23)
# Lenses: Stories + CE. Increments 1–3 story BDDs in this sketch. Increment 4 still names only.

flow:
  status: in-progress
  recommend: more-same-stage
  next: Increment 4 compare BDDs
  note: Generated Increment 1 scenario files remain under scenarios/…/compose-plan-sequence/. Sketch is the working BDD tree.
  open:
    - TODO PlannedTurn invocation bag (tool / action / fidelity / context)  #invocation-bag
    - TODO Increment 4 story BDDs  #inc4
  done:
    - pass #scaffold
    - pass #judge-shape
    - pass #swarm-slice
    - pass #hypothesis-own
    - pass #rubric-source
    - pass #inc1-bdd
    - pass #inc2-sketch
    - pass #inc3-sketch

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
    Start Agent Swarm
        Supervisor --> Create Agent Swarm
            swarm is a collection of agents on a plan
                given a Plan compose-judged-plan with PlannedTurns
                    and a Supervisor with Outcome fewer-cli-handoffs
                when the Supervisor creates a Swarm for that Plan
                then that Swarm holds that Plan
                    and that Swarm is a collection of Agents
                    and launch uses existing sub_agent
                    and there is not a second decorator kit
        Supervisor --> Assign Agent Hypothesis
            supervisor assigns approach; agent owns it
                given a Swarm on Plan compose-judged-plan
                    and a Supervisor with Outcome fewer-cli-handoffs
                when the Supervisor assigns Agent thin-templates the Hypothesis thin-templates-first
                then that Agent owns Hypothesis thin-templates-first
                    and the Supervisor still owns Outcome fewer-cli-handoffs
            second agent owns a different hypothesis toward the same outcome
                given a Swarm with Agent thin-templates owning Hypothesis thin-templates-first
                    and Supervisor Outcome fewer-cli-handoffs
                when the Supervisor assigns Agent channel-write the Hypothesis channel-owns-the-file
                then Agent channel-write owns Hypothesis channel-owns-the-file
                    and Agent thin-templates still owns Hypothesis thin-templates-first
                    and Outcome remains on the Supervisor
        Swarm agent --> Load Plan Context
            agent holds the plan plus its unique hypothesis
                given a Swarm on Plan compose-judged-plan
                    and Agent thin-templates owns Hypothesis thin-templates-first
                when that Agent loads Plan context
                then that Agent holds the Plan
                    and that Agent still owns Hypothesis thin-templates-first
                    and that Hypothesis is not the Supervisor Outcome
        Swarm agent --> Run Planned Turns
            swarm runs the full plan
                given a Swarm on Plan compose-judged-plan with Stories then CleanEngineering PlannedTurns
                    and two Agents each with a unique Hypothesis
                    and that Plan already has a WorkSession from Start Plan
                when the Swarm runs that Plan
                then each Agent runs both PlannedTurns
                    and each Agent has its own WorkSession
                    and those WorkSessions are not the Plan Start Plan WorkSession
                    and launch is non-blocking sub_agent
            swarm runs a selected planned-turn slice
                given the same Swarm and Plan
                when the Swarm runs the Stories PlannedTurn only
                then each Agent runs that PlannedTurn
                    and each Agent still has its own WorkSession
                    and the CleanEngineering PlannedTurn is not run
                    // issue “selected steps” maps to this PlannedTurn slice
    ~> Increment 3: Launch a plan swarm: Create Agent Swarm, Assign Agent Hypothesis, Load Plan Context, Run Planned Turns
---
ce:
    utilities/swarm/
      Swarm
        plan
        plannedTurns
        agents
        run
         -> Plan.plannedTurns
         // full Plan or slice of PlannedTurns; never a Step type
         -> sub_agent.run
         // existing non-blocking launch; never a second decorator
      Supervisor
        outcome
        rubric
        assignHypothesis agent
         -> Agent.hypothesis
      Agent
        plan
        hypothesis
        workSession
         -> Workspace.openWorkSession
         // each Agent opens its own WorkSession on run; never the Plan Start Plan session
         // “if we do this, we will achieve the Outcome”
      Hypothesis
      Outcome
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
- exploration / Start Agent Swarm / pass #inc3-sketch — create Swarm; split Outcome/Hypothesis; load Plan+Hypothesis; run full Plan or PlannedTurn slice via existing sub_agent
- exploration / Start Agent Swarm / pass #swarm-session — tick 5: each Agent opens its own WorkSession; not the Plan Start Plan session; not sessionless run
