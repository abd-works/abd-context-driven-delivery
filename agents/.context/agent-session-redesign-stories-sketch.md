fidelity: story_map + behavior
source: agents/.context/agent-session-redesign-sketch.md
testing: agents/.context/bdd-testing-strategy.md
issue: 55
// Combined sketch: story-map headings (# epic · ## story) with nested BDD state trees
//   (with / that / it should) under each story — trees build on standing conditions.
//
// Spec file alignment: agents/agent_spec.py (vanilla) and agents/agent_agent_spec.py (agentic)
// MUST use the same top-level description names as ## stories, in this file's order.
//
// Same behavior on SubAgent / CliAgent / ChatAgent — sketch the route explicitly:
//   shared_context '{subject line}'     → shared it should once (Mamba: with shared_context)
//   with {Implementation}               → domain state (e.g. with a SubAgent (agentic))
//     -> included_context('{same subject line}')   → include shared examples on this branch
//     it should …                      → implementation-only; not in shared_context
// Do not copy the shared it-should tree under every implementation branch.
//
// (agentic) — story needs agent_bdd because the subject talks to AI chat
//   (SubAgent children, ChatAgent parent window). Flag every such branch.
// CliAgent is NOT (agentic): prove in agents/agent_spec.py (live CursorChatInstance
//   or jsonl stub). Do not put CliAgent live paths in agent_bdd.
//
// Four test layers — do not invert:
//   1. Run Agent Runtime — SAME Agent operations (_send / _await_accept / _await_done / verdict / continue / stop)
//   2. Time Agent Runtime — SAME FileSync clocks on CliAgent and SubAgent. ChatAgent has no file channel.
//   3. Vanilla stories below — Agent orchestration with those runtimes stubbed
//   4. End To End — SubAgent and ChatAgent (agentic); CliAgent in agent_spec.py

# Run Agent Runtime
// FIRST — Agent._send / _await_* / stop. One AIChatInstance per participant as the chat handle only
// (run, continue, stop, chatId, pid). Do not hang received / waiting / accepted / done / clocks / verdict
// parse on AIChatInstance.
// CliAgent and SubAgent wait through AgentRuntimeFileSync (same file protocol, different paths).
// ChatAgent has no file channel — parent window is the wait.
// No clocks here — Time Agent Runtime.

## Send Request To Agent Runtime
shared_context with an agent runtime with a prompt delivered
    it should record that the Agent has sent the request
    it should show FileSync is waiting on that request
    it should not yet be done
with an agent runtime
    with a prompt delivered
        with a SubAgent (agentic)
            -> included_context('with an agent runtime with a prompt delivered')
            it should write the request file and leave it until consumed
        with a CliAgent
            // not (agentic) — CliAgent
            -> included_context('with an agent runtime with a prompt delivered')
            it should spawn against workspacePath with that prompt
        with a ChatAgent (agentic)
            -> included_context('with an agent runtime with a prompt delivered')
            it should show the parent window is waiting on that request

## Accept Request On Agent Runtime
shared_context with an agent runtime that has received a request and is waiting on it
    it should show the request as accepted
    it should still be waiting for output
    with a SubAgent (agentic)
        -> included_context('with an agent runtime that has received a request and is waiting on it')
            // request file consumed
    with a CliAgent
        // not (agentic) — CliAgent
        -> included_context('with an agent runtime that has received a request and is waiting on it')
            // accept signal on the reply file (user line)
    with a ChatAgent (agentic)
        -> included_context('with an agent runtime that has received a request and is waiting on it')
            // parent chat continued the prompt

## Finish Request On Agent Runtime
shared_context with an agent runtime that has accepted a request
    it should show the runtime as done
    it should yield the reply
    with a SubAgent (agentic)
        -> included_context('with an agent runtime that has accepted a request')
            // reply file has output
        with drain restart while the request file still holds work
            it should keep waiting on that request
            it should not drop the unconsumed request
    with a CliAgent
        // not (agentic) — CliAgent
        -> included_context('with an agent runtime that has accepted a request')
            // reply file grew then went quiet
    with a ChatAgent (agentic)
        -> included_context('with an agent runtime that has accepted a request')
            // parent chat finished producing

## Read Verdict On Agent Runtime
shared_context with an agent runtime used as a judge
    with plain text PASS or FAIL
        it should return that verdict
    with no PASS or FAIL
        it should raise AIChatFault — never default PASS
    with a SubAgent (agentic)
        -> included_context('with an agent runtime used as a judge')
            // FileSync.read_verdict on the reply file
    with a CliAgent
        // not (agentic) — CliAgent
        -> included_context('with an agent runtime used as a judge')
            // same FileSync.read_verdict; tool_use-only is "no PASS or FAIL"
    with a ChatAgent (agentic)
        -> included_context('with an agent runtime used as a judge')
            // parent typed verdict; untyped keeps waiting

## Continue Agent Runtime
shared_context with an agent runtime that has stalled or been kicked
    it should continue the same runtime identity
    with a SubAgent (agentic)
        -> included_context('with an agent runtime that has stalled or been kicked')
            // same role files
    with a CliAgent
        // not (agentic) — CliAgent
        -> included_context('with an agent runtime that has stalled or been kicked')
            // same chatId
    with a ChatAgent (agentic)
        -> included_context('with an agent runtime that has stalled or been kicked')
            // same parent window

## Stop Agent Runtime
shared_context with an agent runtime that is alive
    it should no longer wait
    with a SubAgent (agentic)
        -> included_context('with an agent runtime that is alive')
            // FileSync.stop
    with a CliAgent
        // not (agentic) — CliAgent
        -> included_context('with an agent runtime that is alive')
            // FileSync.stop and terminate process
    with a ChatAgent (agentic)
        -> included_context('with an agent runtime that is alive')
            // clear the live parent binding

# Time Agent Runtime
// SECOND — same clocks, same file wait, CliAgent and SubAgent.
// AgentRuntimeFileSync: wait_accept (acceptSeconds) then wait_done (stallSeconds / quietSeconds).
// Paths differ (jsonl vs {role}.in/.out); operations do not. Request file still holding work is not stall.
// AIChatInstance does not clock or parse. ChatAgent has no file channel — no Time stories.

## Time Accept On Agent Runtime
shared_context with an Agent using AgentRuntimeFileSync
    with a request sent
        with an accept signal on the file channel before acceptSeconds
            it should treat the request as accepted in time
        with acceptSeconds run out and no accept signal
            it should raise AIChatFault not_accepted
    with a CliAgent
        // not (agentic) — CliAgent
        -> included_context('with an Agent using AgentRuntimeFileSync')
            // Await Accept On Transcript
    with a SubAgent (agentic)
        -> included_context('with an Agent using AgentRuntimeFileSync')

## Time Done On Agent Runtime
shared_context with an Agent using AgentRuntimeFileSync that has accepted
    with new output on the reply file before stallSeconds
        it should wait until quietSeconds with no further growth
        it should then treat the request as done
    with the request file still holding work
        it should keep waiting
        it should not raise stall
    with the request file empty and no reply before stallSeconds
        it should raise AIChatFault stall
    with a CliAgent
        // not (agentic) — CliAgent
        -> included_context('with an Agent using AgentRuntimeFileSync that has accepted')
            // Wait For Done On Transcript
    with a SubAgent (agentic)
        -> included_context('with an Agent using AgentRuntimeFileSync that has accepted')

# Run Agent Session
// Each ## story: `shared_context {## title}` wraps its it-should tree in the spec.
// Isolate-by-subtype routes use `-> included_context('{## title}')` to that story.

## Reject Multi Repo Session Span
with a Workspace that has multiple Repos
    it should attach the agent session to one primary repo only
    it should refuse a session that spans more than one repo

## Open Default Agent Session
shared_context Open Default Agent Session
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
shared_context Complete Agent Task
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

## Complete Agent Task Using Sub Agent (agentic)
    with an Agent that is a SubAgent
        -> included_context('Complete Agent Task')
        -> included_context('Complete Agent Task With Judge and Human')
        with a current task
            it should launch a non-blocking child for the doer
            with a judge and a human
                it should also launch a non-blocking child for the judge

## Close Agent Session Using Sub Agent (agentic)
        with someone closing the agent session
            -> included_context('Close Agent Session')
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

# Isolate Agent Session By Subtype
// Isolated session tests — SubAgent, CliAgent, and ChatAgent sessions do the SAME things
// including AgentSession.open (branch + worktree). Isolation is not CliAgent-only.
// Each ## story above defines shared_context '{## title}' with its it-should tree.
// Below: each implementation branch states domain state; route with included_context to those stories.
// SubAgent and ChatAgent live paths are (agentic); CliAgent is not (agentic).

with an Agent that is a SubAgent (agentic)
    -> included_context('Open Default Agent Session')
    -> included_context('Open Existing Agent Session')
    -> included_context('Open New Agent Session')
    -> included_context('Close Agent Session')
    -> included_context('Complete Agent Task')
    -> included_context('Complete Agent Task With Judge and Human')
    -> included_context('Add Agent Tasks To Backlog')
    -> included_context('Load Agent Tasks From Template')
    -> included_context('Launch Next Task As Current')
    -> included_context('Complete Task And Advance Queue')
    -> included_context('Finish Work Session')
with an Agent that is a CliAgent
    // not (agentic) — CliAgent
    -> included_context('Open Default Agent Session')
    -> included_context('Open Existing Agent Session')
    -> included_context('Open New Agent Session')
    -> included_context('Close Agent Session')
    -> included_context('Complete Agent Task')
    -> included_context('Complete Agent Task With Judge and Human')
    -> included_context('Add Agent Tasks To Backlog')
    -> included_context('Load Agent Tasks From Template')
    -> included_context('Launch Next Task As Current')
    -> included_context('Complete Task And Advance Queue')
    -> included_context('Finish Work Session')
with an Agent that is a ChatAgent (agentic)
    -> included_context('Open Default Agent Session')
    -> included_context('Open Existing Agent Session')
    -> included_context('Open New Agent Session')
    -> included_context('Close Agent Session')
    -> included_context('Complete Agent Task')
    -> included_context('Complete Agent Task With Judge and Human')
    -> included_context('Add Agent Tasks To Backlog')
    -> included_context('Load Agent Tasks From Template')
    -> included_context('Launch Next Task As Current')
    -> included_context('Complete Task And Advance Queue')
    -> included_context('Finish Work Session')

# Run Cli Agent Session
// not (agentic) — CliAgent; vanilla agents/agent_spec.py

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
                -> included_context('Complete Agent Task')

## Launch Judge On Agent Runtime
        with a judge prompt
            it should ensure a separate AI chat runtime for the judge
            it should set the same workspacePath and sessionName as the doer
            it should run the judge prompt on the judge agent runtime
            it should append a session log line that the judge prompt was sent
                // Await Accept On Transcript — same for doer and judge
            with context tools in the judge prompt
                -> included_context('Complete Agent Task') With Judge and Human

## Await Accept On Transcript
        // included_context('Time Accept On Agent Runtime') — FileSync.wait_accept; not a second clock model
        with a participant agent runtime that is running
            it should pick up the prompt before the accept timeout runs out
            it should append a session log line that the participant accepted the prompt
        with the accept timeout run out and the agent runtime process never ran
            it should raise AIChatFault not_accepted

## Wait For Done On Transcript
        // included_context('Time Done On Agent Runtime') — FileSync.wait_done; not a second clock model
        with a participant agent runtime that accepted the prompt
            with a doer participant
                it should wait up to the stall timeout for any new output on the transcript
                with new output appearing on the transcript
                    it should wait until the transcript stops changing for quietSeconds
                    with the transcript stopped changing for quietSeconds
                        it should append a session log line that the participant finished producing output
                            // may include task index, summary, and duration
                        it should complete the agent task
                            -> included_context('Complete Agent Task')
                with no new output before the stall timeout runs out
                    it should raise AIChatFault stall
            with a judge participant
                // continues under Read Verdict From Judge Transcript
            with dispatch-back from the runtime
                it should poll the chat transcript only


## Read Verdict From Judge Transcript
            // runtime verdict is under Read Verdict On Agent Runtime; this story is CliAgent wiring to the log
            with a readable PASS or FAIL on the judge transcript before the stall timeout runs out
                it should append a session log line with the verdict and result
                it should complete the agent task with judging and human
                    -> included_context('Complete Agent Task') With Judge and Human

## Complete Agent Task Using Cli Agent
    with a current task
        -> included_context('Complete Agent Task')
            // mechanics under Set Chat Context through Wait For Done On Transcript
        with max fails reached on the current task
            with a validation error
                it should stop this task and move on to the next item in the queue
            with a broken workflow fault
                it should stop the whole process
                    // invariant or parse fault — raised under Complete Agent Task
        with a judge prompt and a human participant
                -> included_context('Complete Agent Task With Judge and Human')
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
                            -> included_context('Complete Task And Advance Queue')

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
            -> included_context('Close Agent Session')

# Run Chat Agent Session (agentic)
// ChatAgent parent chat IS the runtime — tools run in this window.
// (agentic) — parent AI chat; mimic through agent_bdd, not CliAgent.

## Complete Agent Task Using Chat Agent (agentic)
with an Agent that is a ChatAgent
    with a current task
        -> included_context('Complete Agent Task')
        with a judge prompt
                -> included_context('Complete Agent Task With Judge and Human')
                // verdict is typed into the parent /agent tool — not read from a child transcript
        with a Human participant
            it should not invoke slash or ToolsCli for the human
            it should post a parent-chat message that the human should look at the work
            it should include a URL of what to look at (contextRoot)
            it should wait for typed feedback in this window
        with context tools, actions, or utilities in the doer prompt
            it should run those in the parent chat window
            it should not invoke ToolsCli from ChatAgent._run_tools_cli_for

## Persist Chat Agent Queue Across Kit Calls (agentic)
with ChatAgentKit tools agent and backlog
    it should bind the named AgentSession and forward to Agent
    it should persist queue state under session.folder
    with a later kit instance on the same session name
        it should resume the queue from what the session recorded

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

# End To End Agent Journeys
// LAST. SubAgent and ChatAgent journeys are (agentic) — AI chat via agent_bdd.
// CliAgent journeys are NOT (agentic) — agents/agent_spec.py. If e2e fails on code,
// add a vanilla repro under the matching runtime or timing story.

## One Judged Job Via Sub Agent (agentic)
with a live SubAgent drain
    with one judged task
        it should open the AgentSession
        it should run doer then judge through the mailbox
        it should record PASS or FAIL on the session log
        it should close the session when the backlog is empty

## One Judged Job Via Cli Agent
// not (agentic) — CliAgent
with a live CliAgent
    with one judged task
        it should bind workspacePath to the session worktree
        it should run doer then judge on cursor-agent
        it should record PASS or FAIL from the judge transcript
        it should close CliAgent session with no live processes

## Two Item Queue Via Sub Agent (agentic)
with a live SubAgent drain
    with two judged tasks on the backlog
        it should drain both in order
        it should record two verdicts and two complete_task lines

## Two Item Queue Via Chat Agent (agentic)
with ChatAgent in the parent window
    with two judged tasks on the backlog
        it should drain both in order through /agent and /agent-backlog

## Start Ticket To Finish
with a Workflow starting a ticket
    it should open an isolated session branch and sibling worktree
    it should run the ticket task
    it should finish the work session and close the issue
    with SubAgent or ChatAgent selected (agentic)
    with CliAgent selected
        // not (agentic) — CliAgent

~> Increment 0: Run Agent Runtime — shared_context + included_context per CliAgent, SubAgent, ChatAgent. Sub/Chat (agentic); CliAgent not (agentic)
~> Increment 0b: Time Agent Runtime — FileSync wait_accept / wait_done on CliAgent and SubAgent. ChatAgent has no file channel.
~> Increment 1: Run Agent Session + task queue (vanilla) — the ONE set of session examples
~> Increment 1b: Isolate Agent Session By Subtype — included_context to each ## story on CliAgent, SubAgent (agentic), ChatAgent (agentic)
~> Increment 2: Subtype extras — Sub/Chat (agentic); CliAgent in agent_spec.py
~> Increment 3: Ticket encapsulation (vanilla)
~> Increment 4: End To End — Sub/Chat (agentic); CliAgent in agent_spec.py
