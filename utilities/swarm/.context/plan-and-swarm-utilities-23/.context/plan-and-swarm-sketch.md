fidelity: exploration
scope: solution ? plan + swarm utilities and git ticket-flow enhancement (ticket 23)
# Lenses: Stories + CE. Story map is Compose / Manage Ticket / Execute / Swarm.

flow:
  status: in-progress
  recommend: more-same-stage
  next: Increment 4 Swarm Plan
  note: Increment 3 Execute Plan deepened. Next working slice is Create Supervisor / Add Agent.
  open: []
  done:
    - pass #scaffold
    - pass #turn-ticket-state
    - pass #map-execute-swarm
    - pass #execute-session

=========
theme: Compose Plan  (epic)
---------
stories:
    Compose Plan
        Practitioner --> Create Plan
            plan is on the workspace
                given a Workspace
                when the operator creates a Plan compose-judged-plan
                then that Plan is associated with that Workspace
                    and that Plan holds no Turns yet
            second plan is its own plan
                given a Workspace that already has a Plan compose-judged-plan
                when the operator creates a Plan ticket-flow-plan
                then that Workspace has both Plans
                    and each Plan holds its own Turns
        Practitioner --> Manage Turns
            add a turn in backlog
                given a Plan compose-judged-plan associated with a Workspace
                when the operator adds a Turn
                    and that Turn has action generate fidelity story_map context plan-and-swarm-utilities-23
                    and a ToolCall toolset Stories name generate
                then that Plan shows the Turn in sequence
                    and that Turn TicketState is Backlog
                    and that Turn holds action generate fidelity story_map context plan-and-swarm-utilities-23
                    and that Turn holds that ToolCall
            turn holds multiple tools and one action
                given a Plan compose-judged-plan associated with a Workspace
                when the operator adds a Turn
                    and that Turn has action Sketch
                    and that Turn tool_keys are Stories and CleanEngineering
                    and ToolCall toolset Stories name Sketch
                    and ToolCall toolset CleanEngineering name Sketch
                then that Turn action is Sketch
                    and that Turn holds both ToolCalls
                    and that Turn TicketState is Backlog
            cli agent describes the turn shape
                given a hanging workspace.Turn with action Sketch
                    and tool_keys Stories and CleanEngineering
                    and toolCalls for Stories Sketch and CleanEngineering Sketch
                when CliAgent describes that Turn
                then CliAgent shows action Sketch
                    and CliAgent shows those tool_keys
                    and CliAgent shows those toolCalls
                    and CliAgent does not open that Turn
                    and CliAgent holds no Plan
            cli opens and finishes the hanging turn
                given that hanging workspace.Turn with action Sketch
                when the CLI opens that Turn
                    and runs Sketch with Stories and CleanEngineering
                    and finishes that Turn
                then that Turn holds result
                    and that Turn TicketState stays with TicketState
                    and that Turn still may hold HILCheck and JudgeCheckpoint
            later turn follows the earlier turn
                given a Plan that already has a Turn Stories generate story_map
                when the operator adds a Turn CleanEngineering generate modules
                then that Plan shows the Stories Turn before the CleanEngineering Turn
                    and both Turns TicketState is Backlog
            edit a turn
                given a Plan with a Turn Stories generate story_map
                when the operator edits that Turn fidelity to scenarios
                then that Turn fidelity is scenarios
                    and that Turn TicketState is still Backlog
                    and that Turn still holds ToolCall toolset Stories name generate
            delete a turn
                given a Plan with a Stories Turn and a CleanEngineering Turn
                when the operator deletes the CleanEngineering Turn
                then that Plan holds the Stories Turn
                    and that Stories Turn TicketState is still Backlog
        Practitioner --> Manage HIL Checks
            add a hil check
                given a Plan with a Turn Stories generate story_map
                when the operator adds a HILCheck to that Turn
                then that Turn has the HILCheck
                    and the Plan still has that one Turn
            edit a hil check
                given a Turn that already has a HILCheck
                when the operator edits that HILCheck
                then that Turn still has one HILCheck
            delete a hil check
                given a Turn that already has a HILCheck
                when the operator deletes that HILCheck
                then that Turn has no HILCheck
            hil check stays when a judge checkpoint is added
                given a Turn that already has a HILCheck
                when the operator adds a JudgeCheckpoint to that Turn against rubric stories-scenarios
                then that Turn has the HILCheck
                    and that Turn has the JudgeCheckpoint
        Practitioner --> Manage Judge Checkpoints
            add a judge checkpoint
                given a Plan with a Turn Stories generate story_map
                when the operator adds a JudgeCheckpoint to that Turn against rubric stories-scenarios
                then that Turn has the JudgeCheckpoint
                    and that JudgeCheckpoint rubric is stories-scenarios
                    and the Plan still has that one Turn
                    // rubric is the same argument ai_judge already takes
            later turn can have its own judge checkpoint
                given a Turn that already has JudgeCheckpoint stories-scenarios
                    and a later Turn CleanEngineering generate modules
                when the operator adds a JudgeCheckpoint to the later Turn against rubric plan-modules
                then the first Turn still has stories-scenarios
                    and the later Turn has plan-modules
            edit a judge checkpoint
                given a Turn with JudgeCheckpoint stories-scenarios
                when the operator edits that JudgeCheckpoint rubric to stories-validate
                then that Turn JudgeCheckpoint rubric is stories-validate
            delete a judge checkpoint
                given a Turn with a JudgeCheckpoint
                when the operator deletes that JudgeCheckpoint
                then that Turn has no JudgeCheckpoint
            judge checkpoint stays when a hil check is added
                given a Turn that already has a JudgeCheckpoint
                when the operator adds a HILCheck to that Turn
                then that Turn has the JudgeCheckpoint
                    and that Turn has the HILCheck
    ~> Increment 1: Compose Plan: Create Plan, Manage Turns, Manage HIL Checks, Manage Judge Checkpoints
---
ce:
    utilities/plan/
      Plan
        workspace
        turns
        create
      JudgeCheckpoint
        rubric
      HILCheck
      ----
      Workspace
        workSessions
        openWorkSession
      WorkSession
        turns
        openTurn
        repairs
      Turn
        prompt
        result
        context
        action
        fidelity
        format
        tool_keys
        toolCalls
        state
        judgeCheckpoint
        hilCheck
        mistakes
        correction
        finish prompt result context
        recordMistake
        recordCorrection
         // existing workspace.Turn; one action; multiple tools via tool_keys and toolCalls
         // state is TicketState Backlog | In Progress | Done
      CliAgent
        action
        tool_keys
        toolCalls
         -> Turn.action
         -> Turn.tool_keys
         -> Turn.toolCalls
         // describes hanging workspace.Turn shape; does not open the Turn
         // CLI opens the hanging Turn and finishes after the action
         // no Plan; no PlannedTurn
      ToolCall
        toolset
        name
      Mistake
      Correction
      Repair
      TicketState
        // Backlog | In Progress | Done ? same work states as Ticket
=========

=========
theme: Manage Ticket Flow  (epic)
---------
stories:
    Manage Ticket Flow
        Practitioner --> Record Research Tags
            research tags live on the existing ticket
                given a Repo with a Ticket number 23
                when the operator records a ResearchTag specification on that Ticket
                then that Ticket holds ResearchTag specification
                    and that Ticket number is still 23
            a second research tag stays on the same ticket
                given that Ticket already holds ResearchTag specification
                when the operator records a ResearchTag workflow on that Ticket
                then that Ticket holds ResearchTag specification
                    and that Ticket holds ResearchTag workflow
                    and that Ticket number is still 23
        Practitioner --> Record Flow Notes
            flow notes live on the existing ticket
                given a Repo with a Ticket number 23
                when the operator records a flow note that Start Plan opened a WorkSession
                then Repo.readNotes for that Ticket show that Start Plan opened a WorkSession
                    and that Ticket number is still 23
            a later flow note stays with the earlier note
                given that Ticket already has the Start Plan note
                when the operator records a flow note that Execute Turn holds result
                then Repo.readNotes show both notes
                    and that Ticket number is still 23
        Practitioner --> Update Ticket Status
            ticket status is an existing project state
                given a Repo with a Ticket number 23
                    and an attached Project
                    and that Ticket TicketState is Backlog
                when the operator sets that Ticket status to In Progress
                then that Ticket TicketState is In Progress
                    and Project.state_named In Progress is that TicketState
            ticket can move to done
                given that Ticket TicketState is In Progress
                when the operator sets that Ticket status to Done
                then that Ticket TicketState is Done
                    and Turn on a Plan uses that same TicketState type
        Agent --> Resolve Ticket Number
            ticket number resolves from a github issue ref
                given a Repo
                when the agent resolves ticket ref #23
                then Ticket.parseNumber is 23
            issue url resolves the same number
                given a Repo
                when the agent resolves an issues URL for 23
                then Ticket.parseNumber is 23
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
      ResearchTag
      TicketState
        // Backlog | In Progress | Done ? same type on Ticket and on Turn
      Project
        stateNamed
=========

=========
theme: Execute Plan  (epic)
---------
stories:
    Execute Plan
        Practitioner --> Start Plan
            start opens a work session and moves the first backlog turn to in progress
                given a Plan compose-judged-plan associated with a Workspace
                    and that Plan has a Turn Stories generate story_map
                    and that Turn TicketState is Backlog
                when the operator starts that Plan
                then Workspace.openWorkSession has a WorkSession for that Plan
                    and that WorkSession openTurn is that Turn
                    and that Turn TicketState is In Progress
            later backlog turn stays backlog
                given that Plan also has a later Turn CleanEngineering generate modules
                when the operator starts that Plan
                then the Stories Turn TicketState is In Progress
                    and the CleanEngineering Turn TicketState is Backlog
        Practitioner --> Execute Turn
            execute runs the in-progress turn
                given a Plan with a WorkSession already open
                    and the Stories Turn TicketState is In Progress
                when the operator executes that Turn
                then that WorkSession openTurn is that Turn
                    and that Turn runs performTurn
                    and that Turn action is generate
                    and that Turn fidelity is story_map
                    and that Turn holds result
                    and that Turn holds toolCalls
            execute leaves ticketstate in progress
                given that Turn already holds result
                when the operator reviews that Turn TicketState
                then that Turn TicketState is In Progress
        Practitioner --> Validate with Human
            hil check presents results to the human
                given a Turn In Progress with a HILCheck
                    and that Turn holds result
                when the human validates that Turn
                then that HILCheck holds the human validation
                    and that Turn still holds result
                    and that Turn TicketState is In Progress
        Judge --> Evaluate Results
            judge checkpoint evaluates the turn result
                given a Turn In Progress with a JudgeCheckpoint rubric stories-scenarios
                    and that Turn holds result
                when the Judge evaluates that Turn
                then ai_judge runs on that Turn result against rubric stories-scenarios
                    and that JudgeCheckpoint holds the JudgeResult
                    and that Turn TicketState is In Progress
        Practitioner --> Review Progress
            progress and results are on the plan
                given a Turn In Progress with result
                    and a HILCheck validation
                    and a JudgeCheckpoint JudgeResult
                when the operator reviews progress
                then that Plan shows that Turn TicketState
                    and that Plan shows that Turn result
                    and that Plan shows the HILCheck validation
                    and that Plan shows the JudgeResult
            review after hil only
                given a Turn In Progress with result
                    and a HILCheck validation
                when the operator reviews progress
                then that Plan shows that Turn result
                    and that Plan shows the HILCheck validation
            review after judge only
                given a Turn In Progress with result
                    and a JudgeCheckpoint JudgeResult
                when the operator reviews progress
                then that Plan shows that Turn result
                    and that Plan shows the JudgeResult
        Practitioner --> Advance Turn
            finished turn is done and the next backlog turn is in progress
                given a Plan with Stories then CleanEngineering Turns
                    and the Stories Turn TicketState is In Progress
                    and a WorkSession is open
                when the operator advances
                    and the Stories Turn finish runs
                then the Stories Turn TicketState is Done
                    and the CleanEngineering Turn TicketState is In Progress
                    and that WorkSession openTurn is the CleanEngineering Turn
            last turn advance leaves the plan on done
                given a Plan whose only In Progress Turn is the last Turn
                when the operator advances
                    and that Turn finish runs
                then that Turn TicketState is Done
                    and that WorkSession openTurn is empty
        Practitioner --> Fix and Rerun
            human asks to fix now
                given a Turn with a HILCheck validation that calls for a fix
                    and that Turn holds result
                    and that Turn TicketState is In Progress
                when the operator recordMistake on that Turn
                    and recordCorrection on that Turn
                    and WorkSession.repairs holds the Repair
                    and the operator executes that Turn again
                then that Turn holds the Mistake
                    and that Turn holds the Correction
                    and that Turn holds a new result
                    and that Turn TicketState is In Progress
            judge evaluation can also drive fix and rerun
                given a Turn with a JudgeResult that calls for a fix
                when the operator recordMistake on that Turn
                    and recordCorrection on that Turn
                    and WorkSession.repairs holds the Repair
                    and the operator executes that Turn again
                then that Turn holds the Mistake and the Correction
                    and that Turn holds a new result
                    and that Turn TicketState is In Progress
    ~> Increment 3: Execute Plan: Start Plan, Execute Turn, Validate with Human, Evaluate Results, Review Progress, Advance Turn, Fix and Rerun
---
ce:
    utilities/plan/
      Plan
        start
         -> Workspace.openWorkSession
        executeTurn
         -> Turn.performTurn
        advanceTurn
         -> Turn.finish
      ----
      Turn
        performTurn
        finish
        recordMistake
        recordCorrection
         -> WorkSession.repairs
      JudgeCheckpoint
        rubric
        judgeResult
         -> ai_judge
=========

=========
theme: Swarm Plan  (epic)
---------
stories:
    Swarm Plan
        Supervisor --> Create Supervisor
            supervisor holds the outcome
                given a Plan compose-judged-plan with Turns
                when the operator creates a Supervisor with Outcome Plan-started
                then that Supervisor owns Outcome Plan-started
                    and that Supervisor is on that Plan
                    and that Supervisor holds no Agents yet
            supervisor rubric hangs on the supervisor
                given a Supervisor with Outcome Plan-started
                when the operator sets that Supervisor rubric to plan-started
                then that Supervisor rubric is plan-started
                    and that Supervisor still owns Outcome Plan-started
            shared turn slice is selected once
                given a Plan with a Stories Turn and a later CleanEngineering Turn
                    and a Supervisor with Outcome Plan-started
                    and no Agent has run yet
                when the operator selects Turns the Stories Turn only for the Swarm
                then Swarm turns are the Stories Turn only
        Supervisor --> Add Agent
            agent holds the hypothesis
                given a Supervisor with Outcome Plan-started
                when the Supervisor adds an Agent with Hypothesis Stories generate story_map
                then that Agent owns Hypothesis Stories generate story_map
                    and that Agent is a SubAgent
                    and SubAgent.run has not launched yet
                    and the Supervisor still owns Outcome Plan-started
            second agent holds a different hypothesis
                given a Supervisor with an Agent that owns Hypothesis Stories generate story_map
                when the Supervisor adds an Agent with Hypothesis CleanEngineering generate modules
                then that Agent owns Hypothesis CleanEngineering generate modules
                    and the first Agent still owns Hypothesis Stories generate story_map
            agent opens its own work session
                given an Agent that owns Hypothesis Stories generate story_map
                    and Swarm turns are the Stories Turn only
                when that Agent starts the Plan
                then SubAgent.run launches on that Agent WorkSession
                    and Workspace.openWorkSession has a WorkSession for that Agent
                    and that WorkSession is not the Plan Start Plan WorkSession
            agent runs execute plan on its work session
                given an Agent that owns Hypothesis Stories generate story_map
                    and that Agent WorkSession is open
                when that Agent executes its In Progress Turn
                then that Agent WorkSession runs Execute Plan
                    and Validate with Human, Evaluate Results, Review Progress, Advance Turn, and Fix and Rerun are those same stories
            agent runs selected turns from the plan
                given Swarm turns are the Stories Turn only
                    and a Supervisor with an Agent that owns Hypothesis Stories generate story_map
                when that Agent starts the Plan on its WorkSession
                then that Agent WorkSession openTurn is the Stories Turn
                    and that WorkSession does not run the CleanEngineering Turn
            second agent runs the same shared turn slice
                given Swarm turns are the Stories Turn only
                    and a Supervisor with two Agents with different Hypotheses
                when each Agent starts the Plan on its WorkSession
                then each Agent WorkSession openTurn is the Stories Turn
            supervisor may add an agent while the swarm is running
                given a Supervisor with an Agent that is still running Execute Plan
                when the Supervisor adds an Agent with Hypothesis CleanEngineering generate modules
                then that new Agent owns Hypothesis CleanEngineering generate modules
                    and SubAgent.run has not launched for that new Agent yet
                    and the first Agent is still running
                    and the Supervisor still owns Outcome Plan-started
            mid-run add launches when that agent starts plan
                given a Supervisor with an Agent still running Execute Plan
                    and a new Agent with Hypothesis CleanEngineering generate modules
                    and SubAgent.run has not launched for that new Agent yet
                when that new Agent starts the Plan on its WorkSession
                then SubAgent.run launches on that new Agent WorkSession
                    and the first Agent is still running
        Supervisor --> Compare Swarm Results
            compare streams after a judge checkpoint
                given an Agent that owns Hypothesis Stories generate story_map
                    and that Agent WorkSession Turn just finished a JudgeCheckpoint
                    and another Agent is still running
                when the Supervisor compares swarm results
                then Supervisor.compare includes that JudgeCheckpoint evaluation
                    and Supervisor.compare shows progress for every Agent
                    and Supervisor.associate updates under the Supervisor rubric toward Outcome Plan-started
                    and the other Agent is still running
                    // stream after each Judge evaluation; associate follows automatically
            compare streams after a hil check
                given an Agent WorkSession Turn just finished a HILCheck
                    and another Agent is still running
                when the Supervisor compares swarm results
                then Supervisor.compare includes that HILCheck validation
                    and Supervisor.compare shows progress for every Agent
                    and Supervisor.associate updates under the Supervisor rubric toward Outcome Plan-started
            compare does not wait for all agents
                given two Agents still running Execute Plan
                    and the Stories Agent Turn just finished a JudgeCheckpoint
                when the Supervisor compares swarm results
                then Supervisor.compare includes that JudgeCheckpoint evaluation
                    and the CleanEngineering Agent is still running
            compare can use a plan judge checkpoint rubric
                given a Plan Turn with JudgeCheckpoint rubric stories-scenarios
                    and an Agent WorkSession Turn just finished that JudgeCheckpoint
                when the Supervisor compares swarm results
                then Supervisor.compare includes that JudgeCheckpoint rubric evaluation
        Supervisor --> Comparative Association
            association follows streamed judge compare
                given Supervisor.compare just streamed a JudgeCheckpoint evaluation
                    and a Supervisor rubric for Outcome Plan-started
                when that compare event completes
                then Supervisor.associate updates under that rubric toward Outcome Plan-started
                    and each Agent still owns its Hypothesis
            association follows streamed hil compare
                given Supervisor.compare just streamed a HILCheck validation
                    and a Supervisor rubric for Outcome Plan-started
                when that compare event completes
                then Supervisor.associate updates under that rubric toward Outcome Plan-started
            association can include a second agent as it arrives
                given Supervisor.associate already holds the Stories Agent under the Supervisor rubric
                    and the CleanEngineering Agent JudgeCheckpoint has just finished
                when Supervisor.compare streams that JudgeCheckpoint evaluation
                then Supervisor.associate includes both Agents under the Supervisor rubric toward Outcome Plan-started
            association updates when a mid-run agent arrives
                given Supervisor.associate already holds the Stories Agent
                    and the Supervisor just added an Agent with Hypothesis CleanEngineering generate modules
                when the CleanEngineering Agent JudgeCheckpoint finishes
                    and Supervisor.compare streams that evaluation
                then Supervisor.associate includes both Agents under the Supervisor rubric toward Outcome Plan-started
    ~> Increment 4: Swarm Plan: Create Supervisor, Add Agent, Compare Swarm Results, Comparative Association
---
ce:
    utilities/swarm/
      Swarm
        plan
        turns
        supervisor
        agents
         -> SubAgent.run
      Supervisor
        outcome
        rubric
        agents
        addAgent
        compare
        associate
         -> compare
         -> Agent.workSession
         -> Turn.judgeCheckpoint
         -> Turn.hilCheck
         -> JudgeResult
         -> Outcome
      Agent
        plan
        hypothesis
        workSession
         -> Swarm.turns
         -> Plan.start
         -> SubAgent.run
         -> Workspace.openWorkSession
         -> Plan.executeTurn
         // Add Agent registers; SubAgent.run launches at Plan.start on this WorkSession
      Hypothesis
      Outcome
=========

## log
- discovery / solution / whole-design / pass #scaffold
- exploration / Compose Plan Sequence / pass #turn-ticket-state ? Plan holds workspace.Turn; Turn.state is TicketState
- discovery / Run Planned Work / pass #map-execute-swarm ? Compose, Execute Plan, Swarm Plan; HIL and Judge stay two Manage stories; Comparative Association is Supervisor rubric across Agents
- exploration / Compose Plan / pass #inc1-bdd ? Create Plan; Manage Turns add/edit/delete; Manage HIL Checks; Manage Judge Checkpoints
- exploration / Execute Plan / pass #inc3-sketch ? Execute Turn; HIL validate; Judge evaluate; Review Progress; Advance Turn; Fix and Rerun on existing Mistake/Correction/Repair
- exploration / Swarm Plan / pass #inc4-sketch ? Create Supervisor then Add Agent; Compare Swarm Results is Execute judgment; Comparative Association is Supervisor rubric
- exploration / Compose Plan / pass #inc1-deepen ? second Plan; edit keeps ToolCall; HIL and Judge each stay when the other is added; JudgeCheckpoint.rubric is ai_judge rubric
- exploration / Manage Ticket Flow / pass #inc2-deepen ? ResearchTag and notes on Ticket 23; setStatus is TicketState; parseNumber on # and issues URL; same TicketState type as Turn
- exploration / Execute Plan / pass #inc3-deepen ? Start Plan openWorkSession; Execute Turn performTurn; ai_judge JudgeResult; Advance Turn finish; last turn Done; Fix and Rerun stays In Progress
- exploration / Swarm Plan / pass #inc4-deepen ? Agent opens own WorkSession; compare streams after Judge and HIL; mid-run addAgent; Comparative Association as results arrive
- exploration / Swarm Plan / pass #inc4-slice ? Agent runs selected Plan Turns; Agent.turns in CE
- exploration / Swarm Plan / pass #inc4-slice-lock ? Swarm.turns shared slice once before agents; associate automatic after streamed compare
- exploration / Swarm Plan / pass #inc4-subagent-launch ? register at Add Agent; SubAgent.run at Plan.start on Agent WorkSession
- exploration / Compose Plan / pass #turn-multi-tool ? Turn has one action and multiple tool_keys/toolCalls; CliAgent describes shape; CLI opens and finishes hanging Turn (no Plan, no PlannedTurn)
