fidelity: story_map + behavior
source: agents/.context/agent-session-redesign-sketch.md
testing: agents/.context/bdd-testing-strategy.md
issue: 55
// Combined sketch: story-map headings (# epic · ## story) with nested BDD state trees
//   (with / that / it should) under each story — trees build on standing conditions.
// testing: vanilla BDD signatures for code seams; agent BDD GWT later for agent-facing journeys

# Run Agent Session

## Reject Multi Repo Session Span
with a Workspace that has multiple Repos
    it should attach the agent session to one primary repo only
    it should refuse a session that spans more than one repo

## Open Default Agent Session
with a Workspace that has a primary Repo
    with no AgentSession name given
        it should create session.folder at {repo.root}/.agent_sessions/{defaultName}
        it should include that session in Repo.agentSessions
        it should record session.log line with kind "open"
    with the current Branch checked out
        it should correlate AgentSession.branch to that Branch
    with an explicit path or workspace path override
        it should set contextRoot to that resolved path anywhere in the repo
    with no explicit path
        it should resolve contextRoot from workspace defaults
            // Workspace.lookupPath — not tied to session name or .agent_sessions folder

## Open Existing Agent Session
with a Workspace that has a primary Repo
    with a Branch that already has an AgentSession
        with a worktree
            with a clean worktree
                with session data on disk
                    it should resume the Agent from what the session recorded
                    it should restore contextRoot from what the session recorded
                    it should record session.log line with kind "open"
                with no session data on disk
                    it should recreate session.folder scaffolding under the same name
                    it should record session.log line with kind "open"
            with a dirty worktree
                with session data on disk
                    it should resume without clearing the dirty tree
                    it should record session.log line with kind "open"
                with no session data on disk
                    it should recreate scaffolding and leave the dirty tree intact
                    it should record session.log line with kind "open"
        with no worktree
            it should checkout_or_create the Branch worktree before resume
            it should bind AgentSession.branch.worktree to that path
            it should record session.log line with kind "open"

## Open New Agent Session
    with no agent session for the current branch yet
        it should create a new agent session under the primary repo
        it should place session.folder at {repo.root}/.agent_sessions/{name}/
        it should resolve contextRoot independently of session.folder
        it should check out or create the branch worktree and attach it to the session
        it should link the branch to that session
        it should append a session log line with kind "open", name, branch, worktree path, and started time
    with a session name that has no folder under {repo.root}/.agent_sessions/ yet
        it should create a distinct session folder for that name
        it should append a session log line with kind "open", name, branch, worktree path, and started time



## Complete Agent Task
    with an Agent bound to an open AgentSession
        with a current task
            with a doer prompt
                it should run the doer prompt on the doer agent runtime
                with context tools, actions, or utilities in the prompt
                    it should run those according to their manifest in the agent runtime
                    with context guidance received from running a context tool through the manifest
                        it should provide session name, context root, new turn id, and context tool guidance text to the AI chat runtime
                        with an action run through the manifest in that context
                            it should run within that open session and open turn
                            it should use the guidance from the context tool
                            it should read and write output relative to the context root
                        with a utility run through the manifest in that context
                            it should run within that open session and open turn
                            it should use the action and context tool guidance it was given
                        it should close the turn when any accompanying actions or utilities are completed

## Complete Agent Task With Judge and Human
                with a judge prompt
                    it should run the judge prompt on the judge agent runtime
                    it should work within the same session as the doer
                        // one AgentSession — same branch worktree for git
                    it should work within the same context root as the doer
                        // contextRoot — where documentation and other artifacts are read and written
                    it should write session log lines under session.folder
                        // orchestration log — not contextRoot
                    with doer output from the current task
                        it should validate the content the doer generated
                        it should validate the outcome of the action the doer ran
                    with context tools in the judge prompt
                        it should run those according to their manifest in the agent runtime
                        with context guidance received from running a context tool through the manifest
                            it should provide session name, context root, open turn id, and context tool guidance text to the AI chat runtime
                                // validate reads doer artifacts from the same context root the doer wrote to
                            with an action run through the manifest in that context
                                it should run within that same open session and open turn
                                it should use the guidance from the context tool
                                it should read and write output relative to the same context root
                    with default validation instructions
                        it should run the validate action through the manifest on the context guidance provided
                        it should record the verdict on the session log
                    with an additional judge prompt
                        it should also apply the judge extra rubric before verdict
                    with a passing verdict
                        it should mark the agent task as complete
                        it should record that the task completed on the session log
                    with a failing verdict
                        with fails still under the limit
                            it should kick the doer agent or tell it to retry
                            the doer runtime should rerun the task according to the prompt as well as additional judge verdict and instructions 
                        with fails at the limit
                            it should stop and raise a judge fail limit fault
                    with a validation error from the validate action
                        it should record the validation error on the session log
                with no judge prompt
                    it should automatically pass once the doer is done
                    it should mark the agent task as complete
                    it should record that the task completed on the session log
                with a workflow fault on the current task
                    it should stop and raise an invariant or parse fault
                with a Human participant
                    it should wait for the human to finish
                    with human feedback
                        it should record the feedback on the session log
                        it should kick the doer agent or tell it to retry
                        the doer runtime should rerun the task according to its prompt  as well as additional humanfeedback 
                        with a judge prompt
                            the judge run time should evaluate the doer again
                that is being rerun
                    the context guidance should be providing a new turn ID 
                    the context guidance should be providing the same session name and context root as its first run
                

## Close Agent Session
    with someone closing the agent session
        it should stop live participants without finishing the session folder
        it should append a session log line with kind "close"
        it should clear the live agent link from the session
        it should not attach or persist chats
            // chats attach on finish work session, not turn close or agent close

## Finish Work Session
    with an AgentSession that is finishing its work
        it should finish any hanging turns first
            // turn close commits work only — never attaches chats
        with one or more agent runtimes used during the session
            it should gather transcript paths from participants and the orchestrator chat
            it should commit session close paths on the branch
            it should attach each path to that close commit via refs/notes/chats
            it should append each path to branch.chats
                // long-lived branch — many finish cycles, many paths; same as WorkSession.save_chat today
            it should record on AnnotatedTag chat/{branch.name}

## Complete Agent Task Using Sub Agent
    with an Agent that is a SubAgent
        with a current task
             it should launch a non-blocking child for the doer
            it should complete the agent task
                // same as Complete Agent Task — tests pass in SubAgent
            with a judge and a human
                it should also launch a non-blocking child for the judge
                it should complete the agent task with judging and human
                    // same as Complete Agent Task With Judge and Human — tests pass in SubAgent

## Close Agent Session Using Sub Agent
        with someone closing the agent session
            it should close the agent session
            it should tear down non-blocking doer and judge children

# Run Agent Task Queue

## Add Agent Tasks To Backlog
with an Agent that has an open session
    with one or more AgentTasks
        it should append AgentTasks with state Backlog
        it should log add_tasks

## Load Agent Tasks From Template
    with a template name provided to the agent
        it should load the template from the template store
        it should create an agent task for each task in the template
        it should add those agent tasks to the agent backlog
        it should append those agent tasks with state Backlog
        it should log add_tasks

## Launch Next Task As Current
        with no participant still in flight on the current task
            it should take the next agent task from the backlog and make it the current task for the agent
            it should mark that task In Progress
            it should record on the session log that the agent task is next to launch
            it should complete the current agent task using doer and judge runtimes
                // continues under Complete Agent Task
        with a doer still in flight on the current task
            it should refuse to take another task from the backlog
        with a judge prompt on the current task
            with the judge still in flight
                it should refuse to take another task from the backlog
        with a human participant on the current task
            with the human still in flight
                it should refuse to take another task from the backlog

## Complete Task And Advance Queue
        with the current agent task complete
            with more tasks on the backlog
                it should launch the next task
                    // continues under Launch Next Task As Current

    with no tasks on the backlog
        it should leave currentTask empty

# Run Cli Agent Session

with an Agent that is a CliAgent

## Set Chat Context From Session Worktree
    with an open AgentSession that has a branch worktree
        it should bind workspace root to session.branch.worktree.path before running tasks
    with no branch worktree yet
        it should not open a durable CliAgent session on main
    with a current task
        it should ensure one AI chat runtime per CliAgentParticipant
        it should set chat.workspacePath to session.branch.worktree.path
        it should set chat.sessionName to session.name
        it should append a JSONL line to the session log under session.folder with the participant, chat id, process id, worktree path, and agent session name

## Launch Doer On Agent Runtime
        with a doer prompt
            it should persist the prompt to a task file under session.contextRoot when argv would be too long
            it should run the doer prompt on the doer agent runtime
            it should append a session log line that the doer agent runtime was run and the prompt was sent
                // may include task index
                // Await Accept and Wait For Done On Transcript — same for doer and judge
            with context tools, actions, or utilities in the prompt
                // same as Complete Agent Task — tests pass in CliAgent

## Launch Judge On Agent Runtime
        with a judge prompt
            it should ensure a separate AI chat runtime for the judge
            it should set the same workspacePath and sessionName as the doer
            it should run the judge prompt on the judge agent runtime
            it should append a session log line that the judge prompt was sent
                // Await Accept On Transcript — same for doer and judge
            with context tools in the judge prompt
                // same as Complete Agent Task With Judge and Human — tests pass in CliAgent

## Await Accept On Transcript
        with a participant agent runtime that is running
            it should pick up the prompt before the accept timeout runs out
            it should append a session log line that the participant accepted the prompt
        with the accept timeout run out and the agent runtime process never ran
            it should raise AIChatFault not_accepted

## Wait For Done On Transcript
        with a participant agent runtime that accepted the prompt
            with a doer participant
                it should wait up to the stall timeout for any new output on the transcript
                with new output appearing on the transcript
                    it should wait until the transcript stops changing for quietSeconds
                    with the transcript stopped changing for quietSeconds
                        it should append a session log line that the participant finished producing output
                            // may include task index, summary, and duration
                        it should complete the agent task
                            // same as Complete Agent Task — tests pass in CliAgent
                with no new output before the stall timeout runs out
                    it should raise AIChatFault stall
            with a judge participant
                // continues under Read Verdict From Judge Transcript
            with dispatch-back from the runtime
                it should poll the chat transcript only


## Read Verdict From Judge Transcript
            with a readable PASS or FAIL on the judge transcript before the stall timeout runs out
                it should append a session log line with the verdict and result
                it should complete the agent task with judging and human
                    // same as Complete Agent Task With Judge and Human — tests pass in CliAgent

## Complete Agent Task Using Cli Agent
    with a current task
        it should complete the agent task
            // same as Complete Agent Task — tests pass in CliAgent
            // mechanics under Set Chat Context through Wait For Done On Transcript
        with max fails reached on the current task
            with a validation error
                it should stop this task and move on to the next item in the queue
            with a broken workflow fault
                it should stop the whole process
                    // invariant or parse fault — raised under Complete Agent Task
        with a judge prompt and a human participant
            it should complete the agent task with judging and human
                // same as Complete Agent Task With Judge and Human — tests pass in CliAgent
                // mechanics under Launch Judge On Agent Runtime through Read Verdict From Judge Transcript

## Run Agent Task Queue Using Cli Agent
    with one or more agent tasks on the backlog
        it should take the next backlog item as the current task
        with a current task
            it should run it on the doer agent runtime
                // Set Chat Context through Wait For Done On Transcript
            with the doer done
                with a judge configured on the task
                    it should run it on the judge agent runtime
                        // Launch Judge On Agent Runtime through Read Verdict From Judge Transcript
                with the current task complete
                    with more tasks on the backlog
                        it should take the next backlog item as the current task
                            // Complete Task And Advance Queue — tests pass in CliAgent

## Kick Stalled Doer
        with a doer that finished its job but the queue did not advance
            it should automatically kick the doer agent runtime without user intervention
            it should append a session log line that the participant was kicked

## Kick Stalled Participant
        with a currentTask participant that has stalled
            it should raise AIChatFault stall after stallSeconds
            it should allow kick to resume the participant
            it should log kick

## Close Cli Agent Session
    with someone closing the agent session
        it should stop live doer and judge agent runtime processes
        it should clear doer and judge chat bindings on the agent session
        it should remove orchestration temps without deleting durable session artifacts
        with the agent session closed successfully
            it should leave no live CLI processes or stale chat bindings
        it should close the agent session
            // same as Close Agent Session — tests pass in CliAgent

# Work On Ticket

## Create Work Ticket On Project Backlog
with a Workflow
    with a title and body
        it should create an Issue via WorkTicket.create
            and set_status Backlog
            and expose number/title/body through the WorkTicket

## Start Ticket Moves Issue In Progress
    with tickets on Backlog
        with someone starting that ticket
            it should set_status In Progress on the Issue
            it should create one agent task for the work
            it should link that agent task to the WorkTicket
            it should pass ticket number, title, and body into that task doer prompt
                // from task.tickets → ticket.issue — not a separate reference field

## Start Ticket Opens Agent Session And Branch
            with an agent type selection
                it should continue under SubAgent by default
                    or CliAgent / ChatAgent when /agent type says so
            it should open a session via WorkTicket.openSession
            it should set session.name from WorkTicket.sessionName
            it should check out or create session.branch
                // session/{session.name} — from session open, not a field on the ticket
            it should create a sibling worktree next to the primary clone, never inside it
                // path: {primary.parent}/{repo-abbrev}-{issue-number}
                // shared open mechanics continue under Open New Agent Session
            with CliAgent selected
                it should bind workspace root to that worktree before running tasks
                    // Set Chat Context From Session Worktree
            it should write the GitHub issue body to issue-body.md under contextRoot
            it should set the session goal from the ticket title or any start instructions provided

## Finish Ticket Closes Issue And Session
            with a ticket that is being closed
                it should finish the work session
                    // continues under Finish Work Session — chats attach to close commit
                it should set_status Done then close the Issue
                it should close the AgentSession
                    // continues under Close Agent Session

~> Increment 1: Run Agent Session + task queue: Open Default, Open Existing, Enqueue, Launch Next, Complete Task
~> Increment 2: Agent kinds + CliAgent trail: Complete Agent Task Using Sub/Cli Agent, Run Cli Chat Instance, Await Accept And Done
~> Increment 3: Ticket encapsulation: Create Work Ticket, Start Opens Session, Finish Closes Issue
