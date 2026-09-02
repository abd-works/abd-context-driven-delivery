"""SKELETON TO START FROM — rendered from agent-session-redesign-stories-sketch.md.
Empty it bodies. Fill later; do not treat this as passing BDD.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
from mamba import description, context, it, shared_context, included_context
from expects import expect, equal









# --- shared contexts (canonical in agent_spec.py; repair_shared_context_specs.py copies a subset to agent_agent_spec.py) ---

with shared_context("with an agent runtime with a prompt delivered"):
    with it("should record that the Agent has sent the request"):
        # BDD: SIGNATURE
        pass
    with it("should show FileSync is waiting on that request"):
        # BDD: SIGNATURE
        pass
    with it("should not yet be done"):
        # BDD: SIGNATURE
        pass


with shared_context("with an agent runtime that has received a request and is waiting on it"):
    with it("should show the request as accepted"):
        # BDD: SIGNATURE
        pass
    with it("should still be waiting for output"):
        # BDD: SIGNATURE
        pass


with shared_context("with an agent runtime that has accepted a request"):
    with it("should show the runtime as done"):
        # BDD: SIGNATURE
        pass
    with it("should yield the reply"):
        # BDD: SIGNATURE
        pass


with shared_context("with an agent runtime used as a judge"):
    with context("with plain text PASS or FAIL"):
        with it("should return that verdict"):
            # BDD: SIGNATURE
            pass
    with context("with no PASS or FAIL"):
        with it("should raise AIChatFault — never default PASS"):
            # BDD: SIGNATURE
            pass


with shared_context("with an agent runtime that has stalled or been kicked"):
    with it("should continue the same runtime identity"):
        # BDD: SIGNATURE
        pass


with shared_context("with an agent runtime that is alive"):
    with it("should no longer wait"):
        # BDD: SIGNATURE
        pass


with shared_context("with an Agent using AgentRuntimeFileSync"):
    with context("with a request sent"):
        with context("with an accept signal on the file channel before acceptSeconds"):
            with it("should treat the request as accepted in time"):
                # BDD: SIGNATURE
                pass
        with context("with acceptSeconds run out and no accept signal"):
            with it("should raise AIChatFault not_accepted"):
                # BDD: SIGNATURE
                pass


with shared_context("with an Agent using AgentRuntimeFileSync that has accepted"):
    with context("with new output on the reply file before stallSeconds"):
        with it("should wait until quietSeconds with no further growth"):
            # BDD: SIGNATURE
            pass
        with it("should then treat the request as done"):
            # BDD: SIGNATURE
            pass
    with context("with the request file still holding work"):
        with it("should keep waiting"):
            # BDD: SIGNATURE
            pass
        with it("should not raise stall"):
            # BDD: SIGNATURE
            pass
    with context("with the request file empty and no reply before stallSeconds"):
        with it("should raise AIChatFault stall"):
            # BDD: SIGNATURE
            pass

with shared_context("Open Default Agent Session"):
    with context("with a Workspace that has a primary Repo"):
        pass
        with context("with no AgentSession name given"):
            pass
            with it('should create session.folder at {repo.root}/.agent_sessions/{defaultName}'):
                # BDD: SIGNATURE
                pass
            with it('should include that session in Repo.agentSessions'):
                # BDD: SIGNATURE
                pass
            with it('should record session.log line with kind "open"'):
                # BDD: SIGNATURE
                pass
        with context("with the current Branch checked out"):
            pass
            with it('should correlate AgentSession.branch to that Branch'):
                # BDD: SIGNATURE
                pass
        with context("with an explicit path or workspace path override"):
            pass
            with it('should set contextRoot to that resolved path anywhere in the repo'):
                # BDD: SIGNATURE
                pass
        with context("with no explicit path"):
            pass
            with it('should resolve contextRoot from workspace defaults'):
                # BDD: SIGNATURE
                pass
            # Workspace.lookupPath — not tied to session name or .agent_sessions folder

with shared_context("Open Existing Agent Session"):
    with context("with a Workspace that has a primary Repo"):
        pass
        with context("with a Branch that already has an AgentSession"):
            pass
            with context("with a worktree"):
                pass
                with context("with a clean worktree"):
                    pass
                    with context("with session data on disk"):
                        pass
                        with it('should resume the Agent from what the session recorded'):
                            # BDD: SIGNATURE
                            pass
                        with it('should restore contextRoot from what the session recorded'):
                            # BDD: SIGNATURE
                            pass
                        with it('should record session.log line with kind "open"'):
                            # BDD: SIGNATURE
                            pass
                    with context("with no session data on disk"):
                        pass
                        with it('should recreate session.folder scaffolding under the same name'):
                            # BDD: SIGNATURE
                            pass
                        with it('should record session.log line with kind "open"'):
                            # BDD: SIGNATURE
                            pass
                with context("with a dirty worktree"):
                    pass
                    with context("with session data on disk"):
                        pass
                        with it('should resume without clearing the dirty tree'):
                            # BDD: SIGNATURE
                            pass
                        with it('should record session.log line with kind "open"'):
                            # BDD: SIGNATURE
                            pass
                    with context("with no session data on disk"):
                        pass
                        with it('should recreate scaffolding and leave the dirty tree intact'):
                            # BDD: SIGNATURE
                            pass
                        with it('should record session.log line with kind "open"'):
                            # BDD: SIGNATURE
                            pass
            with context("with no worktree"):
                pass
                with it('should checkout_or_create the Branch worktree before resume'):
                    # BDD: SIGNATURE
                    pass
                with it('should bind AgentSession.branch.worktree to that path'):
                    # BDD: SIGNATURE
                    pass
                with it('should record session.log line with kind "open"'):
                    # BDD: SIGNATURE
                    pass

with shared_context("Open New Agent Session"):
    with context("with no agent session for the current branch yet"):
        pass
        with it('should create a new agent session under the primary repo'):
            # BDD: SIGNATURE
            pass
        with it('should place session.folder at {repo.root}/.agent_sessions/{name}/'):
            # BDD: SIGNATURE
            pass
        with it('should resolve contextRoot independently of session.folder'):
            # BDD: SIGNATURE
            pass
        with it('should check out or create the branch worktree and attach it to the session'):
            # BDD: SIGNATURE
            pass
        with it('should link the branch to that session'):
            # BDD: SIGNATURE
            pass
        with it('should append a session log line with kind "open", name, branch, worktree path, and started time'):
            # BDD: SIGNATURE
            pass
    with context("with a session name that has no folder under {repo.root}/.agent_sessions/ yet"):
        pass
        with it('should create a distinct session folder for that name'):
            # BDD: SIGNATURE
            pass
        with it('should append a session log line with kind "open", name, branch, worktree path, and started time'):
            # BDD: SIGNATURE
            pass

with shared_context("Close Agent Session"):
    with context("with someone closing the agent session"):
        pass
        with it('should stop live participants without finishing the session folder'):
            # BDD: SIGNATURE
            pass
        with it('should append a session log line with kind "close"'):
            # BDD: SIGNATURE
            pass
        with it('should clear the live agent link from the session'):
            # BDD: SIGNATURE
            pass
        with it('should not attach or persist chats'):
            # BDD: SIGNATURE
            pass
        # chats attach on finish work session, not turn close or agent close

with shared_context("Complete Agent Task"):
    with context("with an Agent bound to an open AgentSession"):
        pass
        with context("with a current task"):
            pass
            with context("with a doer prompt"):
                pass
                with it('should run the doer prompt on the doer agent runtime'):
                    # BDD: SIGNATURE
                    pass
                with context("with context tools, actions, or utilities in the prompt"):
                    pass
                    with it('should run those according to their manifest in the agent runtime'):
                        # BDD: SIGNATURE
                        pass
                    with context("with context guidance received from running a context tool through the manifest"):
                        pass
                        with it('should provide session name, context root, new turn id, and context tool guidance text to the AI chat runtime'):
                            # BDD: SIGNATURE
                            pass
                        with context("with an action run through the manifest in that context"):
                            pass
                            with it('should run within that open session and open turn'):
                                # BDD: SIGNATURE
                                pass
                            with it('should use the guidance from the context tool'):
                                # BDD: SIGNATURE
                                pass
                            with it('should read and write output relative to the context root'):
                                # BDD: SIGNATURE
                                pass
                        with context("with a utility run through the manifest in that context"):
                            pass
                            with it('should run within that open session and open turn'):
                                # BDD: SIGNATURE
                                pass
                            with it('should use the action and context tool guidance it was given'):
                                # BDD: SIGNATURE
                                pass
                        with it('should close the turn when any accompanying actions or utilities are completed'):
                            # BDD: SIGNATURE
                            pass

with shared_context("Complete Agent Task With Judge and Human"):
    with context("with a judge prompt"):
        pass
        with it('should run the judge prompt on the judge agent runtime'):
            # BDD: SIGNATURE
            pass
        with it('should work within the same session as the doer'):
            # BDD: SIGNATURE
            pass
        # one AgentSession — same branch worktree for git
        with it('should work within the same context root as the doer'):
            # BDD: SIGNATURE
            pass
        # contextRoot — where documentation and other artifacts are read and written
        with it('should write session log lines under session.folder'):
            # BDD: SIGNATURE
            pass
        # orchestration log — not contextRoot
        with context("with doer output from the current task"):
            pass
            with it('should validate the content the doer generated'):
                # BDD: SIGNATURE
                pass
            with it('should validate the outcome of the action the doer ran'):
                # BDD: SIGNATURE
                pass
        with context("with context tools in the judge prompt"):
            pass
            with it('should run those according to their manifest in the agent runtime'):
                # BDD: SIGNATURE
                pass
            with context("with context guidance received from running a context tool through the manifest"):
                pass
                with it('should provide session name, context root, open turn id, and context tool guidance text to the AI chat runtime'):
                    # BDD: SIGNATURE
                    pass
                # validate reads doer artifacts from the same context root the doer wrote to
                with context("with an action run through the manifest in that context"):
                    pass
                    with it('should run within that same open session and open turn'):
                        # BDD: SIGNATURE
                        pass
                    with it('should use the guidance from the context tool'):
                        # BDD: SIGNATURE
                        pass
                    with it('should read and write output relative to the same context root'):
                        # BDD: SIGNATURE
                        pass
        with context("with default validation instructions"):
            pass
            with it('should run the validate action through the manifest on the context guidance provided'):
                # BDD: SIGNATURE
                pass
            with it('should record the verdict on the session log'):
                # BDD: SIGNATURE
                pass
        with context("with an additional judge prompt"):
            pass
            with it('should also apply the judge extra rubric before verdict'):
                # BDD: SIGNATURE
                pass
        with context("with a passing verdict"):
            pass
            with it('should mark the agent task as complete'):
                # BDD: SIGNATURE
                pass
            with it('should record that the task completed on the session log'):
                # BDD: SIGNATURE
                pass
        with context("with a failing verdict"):
            pass
            with context("with fails still under the limit"):
                pass
                with it('should kick the doer agent or tell it to retry'):
                    # BDD: SIGNATURE
                    pass
                with it('should rerun the task according to the prompt as well as additional judge verdict and instructions'):
                    # BDD: SIGNATURE
                    pass
            with context("with fails at the limit"):
                pass
                with it('should stop and raise a judge fail limit fault'):
                    # BDD: SIGNATURE
                    pass
        with context("with a validation error from the validate action"):
            pass
            with it('should record the validation error on the session log'):
                # BDD: SIGNATURE
                pass
    with context("with no judge prompt"):
        pass
        with it('should automatically pass once the doer is done'):
            # BDD: SIGNATURE
            pass
        with it('should mark the agent task as complete'):
            # BDD: SIGNATURE
            pass
        with it('should record that the task completed on the session log'):
            # BDD: SIGNATURE
            pass
    with context("with a workflow fault on the current task"):
        pass
        with it('should stop and raise an invariant or parse fault'):
            # BDD: SIGNATURE
            pass
    with context("with a Human participant"):
        pass
        with it('should wait for the human to finish'):
            # BDD: SIGNATURE
            pass
        with context("with human feedback"):
            pass
            with it('should record the feedback on the session log'):
                # BDD: SIGNATURE
                pass
            with it('should kick the doer agent or tell it to retry'):
                # BDD: SIGNATURE
                pass
            with it('should rerun the task according to its prompt  as well as additional humanfeedback'):
                # BDD: SIGNATURE
                pass
            with context("with a judge prompt"):
                pass
                with it('should evaluate the doer again'):
                    # BDD: SIGNATURE
                    pass
    with context("with that is being rerun"):
        pass
        with it('should be providing a new turn ID'):
            # BDD: SIGNATURE
            pass
        with it('should be providing the same session name and context root as its first run'):
            # BDD: SIGNATURE
            pass

with shared_context("Add Agent Tasks To Backlog"):
    with context("with an Agent that has an open session"):
        pass
        with context("with one or more AgentTasks"):
            pass
            with it('should append AgentTasks with state Backlog'):
                # BDD: SIGNATURE
                pass
            with it('should log add_tasks'):
                # BDD: SIGNATURE
                pass

with shared_context("Load Agent Tasks From Template"):
    with context("with a template name provided to the agent"):
        pass
        with it('should load the template from the template store'):
            # BDD: SIGNATURE
            pass
        with it('should create an agent task for each task in the template'):
            # BDD: SIGNATURE
            pass
        with it('should add those agent tasks to the agent backlog'):
            # BDD: SIGNATURE
            pass
        with it('should append those agent tasks with state Backlog'):
            # BDD: SIGNATURE
            pass
        with it('should log add_tasks'):
            # BDD: SIGNATURE
            pass

with shared_context("Launch Next Task As Current"):
    with context("with no participant still in flight on the current task"):
        pass
        with it('should take the next agent task from the backlog and make it the current task for the agent'):
            # BDD: SIGNATURE
            pass
        with it('should mark that task In Progress'):
            # BDD: SIGNATURE
            pass
        with it('should record on the session log that the agent task is next to launch'):
            # BDD: SIGNATURE
            pass
        with it('should complete the current agent task using doer and judge runtimes'):
            # BDD: SIGNATURE
            pass
        # continues under Complete Agent Task
    with context("with a doer still in flight on the current task"):
        pass
        with it('should refuse to take another task from the backlog'):
            # BDD: SIGNATURE
            pass
    with context("with a judge prompt on the current task"):
        pass
        with context("with the judge still in flight"):
            pass
            with it('should refuse to take another task from the backlog'):
                # BDD: SIGNATURE
                pass
    with context("with a human participant on the current task"):
        pass
        with context("with the human still in flight"):
            pass
            with it('should refuse to take another task from the backlog'):
                # BDD: SIGNATURE
                pass

with shared_context("Complete Task And Advance Queue"):
    with context("with the current agent task complete"):
        pass
        with context("with more tasks on the backlog"):
            pass
            with it('should launch the next task'):
                # BDD: SIGNATURE
                pass
            # continues under Launch Next Task As Current
    with context("with no tasks on the backlog"):
        pass
        with it('should leave currentTask empty'):
            # BDD: SIGNATURE
            pass

with shared_context("Finish Work Session"):
    with context("with an AgentSession that is finishing its work"):
        pass
        with it('should finish any hanging turns first'):
            # BDD: SIGNATURE
            pass
        # turn close commits work only — never attaches chats
        with context("with one or more agent runtimes used during the session"):
            pass
            with it('should gather transcript paths from participants and the orchestrator chat'):
                # BDD: SIGNATURE
                pass
            with it('should commit session close paths on the branch'):
                # BDD: SIGNATURE
                pass
            with it('should attach each path to that close commit via refs/notes/chats'):
                # BDD: SIGNATURE
                pass
            with it('should append each path to branch.chats'):
                # BDD: SIGNATURE
                pass
            # long-lived branch — many finish cycles, many paths; same as WorkSession.save_chat today
            with it('should record on AnnotatedTag chat/{branch.name}'):
                # BDD: SIGNATURE
                pass

# --- end shared contexts ---

# SKELETON TO START FROM

# # Run Agent Runtime

# ## Send Request To Agent Runtime
with description("Send Request To Agent Runtime"):
    with context("with an agent runtime"):
        with context("with a prompt delivered"):
            pass
    with context("with a SubAgent (agentic)"):
        with included_context("with an agent runtime with a prompt delivered"):
            pass
        with it("should write the request file and leave it until consumed"):
            # BDD: SIGNATURE
            pass
    with context("with a CliAgent"):
        with included_context("with an agent runtime with a prompt delivered"):
            pass
        with it("should spawn against workspacePath with that prompt"):
            # BDD: SIGNATURE
            pass
    with context("with a ChatAgent (agentic)"):
        with included_context("with an agent runtime with a prompt delivered"):
            pass
        with it("should show the parent window is waiting on that request"):
            # BDD: SIGNATURE
            pass

# ## Accept Request On Agent Runtime
with description("Accept Request On Agent Runtime"):
    with context("with a SubAgent (agentic)"):
        with included_context("with an agent runtime that has received a request and is waiting on it"):
            pass
    with context("with a CliAgent"):
        with included_context("with an agent runtime that has received a request and is waiting on it"):
            pass
    with context("with a ChatAgent (agentic)"):
        with included_context("with an agent runtime that has received a request and is waiting on it"):
            pass

# ## Finish Request On Agent Runtime
with description("Finish Request On Agent Runtime"):
    with context("with a SubAgent (agentic)"):
        with included_context("with an agent runtime that has accepted a request"):
            pass
        with context("with drain restart while the request file still holds work"):
            with it("should keep waiting on that request"):
                # BDD: SIGNATURE
                pass
            with it("should not drop the unconsumed request"):
                # BDD: SIGNATURE
                pass
    with context("with a CliAgent"):
        with included_context("with an agent runtime that has accepted a request"):
            pass
    with context("with a ChatAgent (agentic)"):
        with included_context("with an agent runtime that has accepted a request"):
            pass

# ## Read Verdict On Agent Runtime
with description("Read Verdict On Agent Runtime"):
    with context("with a SubAgent (agentic)"):
        with included_context("with an agent runtime used as a judge"):
            pass
    with context("with a CliAgent"):
        with included_context("with an agent runtime used as a judge"):
            pass
    with context("with a ChatAgent (agentic)"):
        with included_context("with an agent runtime used as a judge"):
            pass

# ## Continue Agent Runtime
with description("Continue Agent Runtime"):
    with context("with a SubAgent (agentic)"):
        with included_context("with an agent runtime that has stalled or been kicked"):
            pass
    with context("with a CliAgent"):
        with included_context("with an agent runtime that has stalled or been kicked"):
            pass
    with context("with a ChatAgent (agentic)"):
        with included_context("with an agent runtime that has stalled or been kicked"):
            pass

# ## Stop Agent Runtime
with description("Stop Agent Runtime"):
    with context("with a SubAgent (agentic)"):
        with included_context("with an agent runtime that is alive"):
            pass
    with context("with a CliAgent"):
        with included_context("with an agent runtime that is alive"):
            pass
    with context("with a ChatAgent (agentic)"):
        with included_context("with an agent runtime that is alive"):
            pass

# # Time Agent Runtime

# ## Time Accept On Agent Runtime
with description("Time Accept On Agent Runtime"):
    with context("with a CliAgent"):
        with included_context("with an Agent using AgentRuntimeFileSync"):
            pass
    with context("with a SubAgent (agentic)"):
        with included_context("with an Agent using AgentRuntimeFileSync"):
            pass

# ## Time Done On Agent Runtime
with description("Time Done On Agent Runtime"):
    with context("with a CliAgent"):
        with included_context("with an Agent using AgentRuntimeFileSync that has accepted"):
            pass
    with context("with a SubAgent (agentic)"):
        with included_context("with an Agent using AgentRuntimeFileSync that has accepted"):
            pass

# # Run Agent Session

# ## Reject Multi Repo Session Span
with description("Reject Multi Repo Session Span"):
    with context("with a Workspace that has multiple Repos"):
        pass
        with it("should attach the agent session to one primary repo only"):
            # BDD: SIGNATURE
            pass
        with it("should refuse a session that spans more than one repo"):
            # BDD: SIGNATURE
            pass

# ## Open Default Agent Session
# ## Open Existing Agent Session
# ## Open New Agent Session
# ## Complete Agent Task
# ## Complete Agent Task With Judge and Human
# ## Close Agent Session
# ## Finish Work Session
# # Run Agent Task Queue

# ## Add Agent Tasks To Backlog
# ## Load Agent Tasks From Template
# ## Launch Next Task As Current
# ## Complete Task And Advance Queue
# # Run Cli Agent Session

# ## Set Chat Context From Session Worktree
with description("Set Chat Context From Session Worktree"):
    with context("with an open AgentSession that has a branch worktree"):
        pass
        with it("should bind workspace root to session.branch.worktree.path before running tasks"):
            # BDD: SIGNATURE
            pass
    with context("with no branch worktree yet"):
        pass
        with it("should not open a durable CliAgent session on main"):
            # BDD: SIGNATURE
            pass
    with context("with a current task"):
        pass
        with it("should ensure one AI chat runtime per CliAgentParticipant"):
            # BDD: SIGNATURE
            pass
        with it("should set chat.workspacePath to session.branch.worktree.path"):
            # BDD: SIGNATURE
            pass
        with it("should set chat.sessionName to session.name"):
            # BDD: SIGNATURE
            pass
        with it("should append a JSONL line to the session log under session.folder with the participant, chat id, process id, worktree path, and agent session name"):
            # BDD: SIGNATURE
            pass

# ## Launch Doer On Agent Runtime
with description("Launch Doer On Agent Runtime"):
    with context("with a doer prompt"):
        pass
        with it("should persist the prompt to a task file under session.contextRoot when argv would be too long"):
            # BDD: SIGNATURE
            pass
        with it("should run the doer prompt on the doer agent runtime"):
            # BDD: SIGNATURE
            pass
        with it("should append a session log line that the doer agent runtime was run and the prompt was sent"):
            # BDD: SIGNATURE
            pass
            # may include task index
            # Await Accept and Wait For Done On Transcript — same for doer and judge
        with context("with context tools, actions, or utilities in the prompt"):
            pass
            with included_context("Complete Agent Task"):
                pass
# ## Launch Judge On Agent Runtime
with description("Launch Judge On Agent Runtime"):
    with context("with a judge prompt"):
        pass
        with it("should ensure a separate AI chat runtime for the judge"):
            # BDD: SIGNATURE
            pass
        with it("should set the same workspacePath and sessionName as the doer"):
            # BDD: SIGNATURE
            pass
        with it("should run the judge prompt on the judge agent runtime"):
            # BDD: SIGNATURE
            pass
        with it("should append a session log line that the judge prompt was sent"):
            # BDD: SIGNATURE
            pass
            # Await Accept On Transcript — same for doer and judge
        with context("with context tools in the judge prompt"):
            pass
            with included_context("Complete Agent Task With Judge and Human"):
                pass
# ## Await Accept On Transcript
with description("Await Accept On Transcript"):
    # included_context("Time Accept On Agent Runtime") — FileSync.wait_accept
    with context("with a participant agent runtime that is running"):
        pass
        with it("should pick up the prompt before the accept timeout runs out"):
            # BDD: SIGNATURE
            pass
        with it("should append a session log line that the participant accepted the prompt"):
            # BDD: SIGNATURE
            pass
    with context("with the accept timeout run out and the agent runtime process never ran"):
        pass
        with it("should raise AIChatFault not_accepted"):
            # BDD: SIGNATURE
            pass

# ## Wait For Done On Transcript
with description("Wait For Done On Transcript"):
    # included_context("Time Done On Agent Runtime") — FileSync.wait_done
    with context("with a participant agent runtime that accepted the prompt"):
        pass
        with context("with a doer participant"):
            pass
            with it("should wait up to the stall timeout for any new output on the transcript"):
                # BDD: SIGNATURE
                pass
            with context("with new output appearing on the transcript"):
                pass
                with it("should wait until the transcript stops changing for quietSeconds"):
                    # BDD: SIGNATURE
                    pass
                with context("with the transcript stopped changing for quietSeconds"):
                    pass
                    with it("should append a session log line that the participant finished producing output"):
                        # BDD: SIGNATURE
                        pass
                        # may include task index, summary, and duration
                    with it("should complete the agent task"):
                        # BDD: SIGNATURE
                        pass
                    with included_context("Complete Agent Task"):
                        pass
            with context("with no new output before the stall timeout runs out"):
                pass
                with it("should raise AIChatFault stall"):
                    # BDD: SIGNATURE
                    pass
        with context("with a judge participant"):
            pass
            # continues under Read Verdict From Judge Transcript
        with context("with dispatch-back from the runtime"):
            pass
            with it("should poll the chat transcript only"):
                # BDD: SIGNATURE
                pass

# ## Read Verdict From Judge Transcript
with description("Read Verdict From Judge Transcript"):
    # runtime verdict is under Read Verdict On Agent Runtime; this story is CliAgent wiring to the log
    with context("with a readable PASS or FAIL on the judge transcript before the stall timeout runs out"):
        pass
        with it("should append a session log line with the verdict and result"):
            # BDD: SIGNATURE
            pass
        with it("should complete the agent task with judging and human"):
            # BDD: SIGNATURE
            pass
            with included_context("Complete Agent Task With Judge and Human"):
                pass
# ## Complete Agent Task Using Cli Agent
with description("Complete Agent Task Using Cli Agent"):
    with context("with a current task"):
        pass
        with included_context("Complete Agent Task"):
            pass
            # mechanics under Set Chat Context through Wait For Done On Transcript
        with context("with max fails reached on the current task"):
            pass
            with context("with a validation error"):
                pass
                with it("should stop this task and move on to the next item in the queue"):
                    # BDD: SIGNATURE
                    pass
            with context("with a broken workflow fault"):
                pass
                with it("should stop the whole process"):
                    # BDD: SIGNATURE
                    pass
                    # invariant or parse fault — raised under Complete Agent Task
        with context("with a judge prompt and a human participant"):
            pass
            with included_context("Complete Agent Task With Judge and Human"):
                pass
                # mechanics under Launch Judge On Agent Runtime through Read Verdict From Judge Transcript

# ## Run Agent Task Queue Using Cli Agent
with description("Run Agent Task Queue Using Cli Agent"):
    with context("with one or more agent tasks on the backlog"):
        pass
        with it("should take the next backlog item as the current task"):
            # BDD: SIGNATURE
            pass
        with context("with a current task"):
            pass
            with it("should run it on the doer agent runtime"):
                # BDD: SIGNATURE
                pass
                # Set Chat Context through Wait For Done On Transcript
            with context("with the doer done"):
                pass
                with context("with a judge configured on the task"):
                    pass
                    with it("should run it on the judge agent runtime"):
                        # BDD: SIGNATURE
                        pass
                        # Launch Judge On Agent Runtime through Read Verdict From Judge Transcript
                with context("with the current task complete"):
                    pass
                    with context("with more tasks on the backlog"):
                        pass
                        with it("should take the next backlog item as the current task"):
                            # BDD: SIGNATURE
                            pass
                            with included_context("Complete Task And Advance Queue"):
                                pass
# ## Kick Stalled Doer
with description("Kick Stalled Doer"):
    with context("with a doer that finished its job but the queue did not advance"):
        pass
        with it("should automatically kick the doer agent runtime without user intervention"):
            # BDD: SIGNATURE
            pass
        with it("should append a session log line that the participant was kicked"):
            # BDD: SIGNATURE
            pass

# ## Kick Stalled Participant
with description("Kick Stalled Participant"):
    with context("with a currentTask participant that has stalled"):
        pass
        with it("should raise AIChatFault stall after stallSeconds"):
            # BDD: SIGNATURE
            pass
        with it("should allow kick to resume the participant"):
            # BDD: SIGNATURE
            pass
        with it("should log kick"):
            # BDD: SIGNATURE
            pass

# ## Close Cli Agent Session
with description("Close Cli Agent Session"):
    with context("with someone closing the agent session"):
        pass
        with it("should stop live doer and judge agent runtime processes"):
            # BDD: SIGNATURE
            pass
        with it("should clear doer and judge chat bindings on the agent session"):
            # BDD: SIGNATURE
            pass
        with it("should remove orchestration temps without deleting durable session artifacts"):
            # BDD: SIGNATURE
            pass
        with context("with the agent session closed successfully"):
            pass
            with it("should leave no live CLI processes or stale chat bindings"):
                # BDD: SIGNATURE
                pass
        with it("should close the agent session"):
            # BDD: SIGNATURE
            pass
            with included_context("Close Agent Session"):
                pass
# # Work On Ticket

# ## Create Work Ticket On Project Backlog
with description("Create Work Ticket On Project Backlog"):
    with context("with a Workflow"):
        pass
        with context("with a title and body"):
            pass
            with it("should create an Issue via WorkTicket.create"):
                # BDD: SIGNATURE
                pass
                with it("should set_status Backlog"):
                    # BDD: SIGNATURE
                    pass
                with it("should expose number/title/body through the WorkTicket"):
                    # BDD: SIGNATURE
                    pass

# ## Start Ticket Moves Issue In Progress
with description("Start Ticket Moves Issue In Progress"):
    with context("with tickets on Backlog"):
        pass
        with context("with someone starting that ticket"):
            pass
            with it("should set_status In Progress on the Issue"):
                # BDD: SIGNATURE
                pass
            with it("should create one agent task for the work"):
                # BDD: SIGNATURE
                pass
            with it("should link that agent task to the WorkTicket"):
                # BDD: SIGNATURE
                pass
            with it("should pass ticket number, title, and body into that task doer prompt"):
                # BDD: SIGNATURE
                pass
                # from task.tickets → ticket.issue — not a separate reference field

# ## Start Ticket Opens Agent Session And Branch
with description("Start Ticket Opens Agent Session And Branch"):
    with context("with an agent type selection"):
        pass
        with it("should continue under SubAgent by default"):
            # BDD: SIGNATURE
            pass
            # or CliAgent / ChatAgent when /agent type says so
    with it("should open a session via WorkTicket.openSession"):
        # BDD: SIGNATURE
        pass
    with it("should set session.name from WorkTicket.sessionName"):
        # BDD: SIGNATURE
        pass
    with it("should check out or create session.branch"):
        # BDD: SIGNATURE
        pass
        # session/{session.name} — from session open, not a field on the ticket
    with it("should create a sibling worktree next to the primary clone, never inside it"):
        # BDD: SIGNATURE
        pass
        # path: {primary.parent}/{repo-abbrev}-{issue-number}
        # shared open mechanics continue under Open New Agent Session
    with context("with CliAgent selected"):
        pass
        with it("should bind workspace root to that worktree before running tasks"):
            # BDD: SIGNATURE
            pass
            # Set Chat Context From Session Worktree
    with it("should write the GitHub issue body to issue-body.md under contextRoot"):
        # BDD: SIGNATURE
        pass
    with it("should set the session goal from the ticket title or any start instructions provided"):
        # BDD: SIGNATURE
        pass

# ## Finish Ticket Closes Issue And Session
with description("Finish Ticket Closes Issue And Session"):
    with context("with a ticket that is being closed"):
        pass
        with it("should finish the work session"):
            # BDD: SIGNATURE
            pass
            # continues under Finish Work Session — chats attach to close commit
        with it("should set_status Done then close the Issue"):
            # BDD: SIGNATURE
            pass
        with it("should close the AgentSession"):
            # BDD: SIGNATURE
            pass
            # continues under Close Agent Session


# # Isolate Agent Session By Subtype

with description("Isolate Agent Session By Subtype"):
    with context("with an Agent that is a SubAgent (agentic)"):
        with included_context("Open Default Agent Session"):
            pass
        with included_context("Open Existing Agent Session"):
            pass
        with included_context("Open New Agent Session"):
            pass
        with included_context("Close Agent Session"):
            pass
        with included_context("Complete Agent Task"):
            pass
        with included_context("Complete Agent Task With Judge and Human"):
            pass
        with included_context("Add Agent Tasks To Backlog"):
            pass
        with included_context("Load Agent Tasks From Template"):
            pass
        with included_context("Launch Next Task As Current"):
            pass
        with included_context("Complete Task And Advance Queue"):
            pass
        with included_context("Finish Work Session"):
            pass
    with context("with an Agent that is a CliAgent"):
        with included_context("Open Default Agent Session"):
            pass
        with included_context("Open Existing Agent Session"):
            pass
        with included_context("Open New Agent Session"):
            pass
        with included_context("Close Agent Session"):
            pass
        with included_context("Complete Agent Task"):
            pass
        with included_context("Complete Agent Task With Judge and Human"):
            pass
        with included_context("Add Agent Tasks To Backlog"):
            pass
        with included_context("Load Agent Tasks From Template"):
            pass
        with included_context("Launch Next Task As Current"):
            pass
        with included_context("Complete Task And Advance Queue"):
            pass
        with included_context("Finish Work Session"):
            pass
    with context("with an Agent that is a ChatAgent (agentic)"):
        with included_context("Open Default Agent Session"):
            pass
        with included_context("Open Existing Agent Session"):
            pass
        with included_context("Open New Agent Session"):
            pass
        with included_context("Close Agent Session"):
            pass
        with included_context("Complete Agent Task"):
            pass
        with included_context("Complete Agent Task With Judge and Human"):
            pass
        with included_context("Add Agent Tasks To Backlog"):
            pass
        with included_context("Load Agent Tasks From Template"):
            pass
        with included_context("Launch Next Task As Current"):
            pass
        with included_context("Complete Task And Advance Queue"):
            pass
        with included_context("Finish Work Session"):
            pass

# # End To End Agent Journeys

# ## One Judged Job Via Cli Agent
with description("One Judged Job Via Cli Agent"):
    # not (agentic) — CliAgent
    with context("with a live CliAgent"):
        pass
        with context("with one judged task"):
            pass
            with it("should bind workspacePath to the session worktree"):
                # BDD: SIGNATURE
                pass
            with it("should run doer then judge on cursor-agent"):
                # BDD: SIGNATURE
                pass
            with it("should record PASS or FAIL from the judge transcript"):
                # BDD: SIGNATURE
                pass
            with it("should close CliAgent session with no live processes"):
                # BDD: SIGNATURE
                pass

# ## Start Ticket To Finish
with description("Start Ticket To Finish"):
    with context("with a Workflow starting a ticket"):
        pass
        with it("should open an isolated session branch and sibling worktree"):
            # BDD: SIGNATURE
            pass
        with it("should run the ticket task"):
            # BDD: SIGNATURE
            pass
        with it("should finish the work session and close the issue"):
            # BDD: SIGNATURE
            pass
        with context("with SubAgent or ChatAgent selected (agentic)"):
            pass
        with context("with CliAgent selected"):
            pass
            # not (agentic) — CliAgent
