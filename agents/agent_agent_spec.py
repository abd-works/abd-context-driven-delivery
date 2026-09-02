"""SKELETON TO START FROM — (agentic) stories only, from agent-session-redesign-stories-sketch.md.
Empty it bodies. Fill later via agent_bdd; no CliAgent live here.
# @agent-spec-manifest python -m tools agent-spec agents/agent_agent_spec.py
"""
from mamba import description, context, it, shared_context, included_context
from expects import expect, equal


# --- shared contexts (subset copied from agent_spec.py by repair_shared_context_specs.py) ---
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

# --- end shared contexts ---

# SKELETON TO START FROM

# # Run Agent Session

# ## Complete Agent Task Using Sub Agent (agentic)
with description("Complete Agent Task Using Sub Agent (agentic)"):
    with context("with an Agent that is a SubAgent"):
        with included_context("Complete Agent Task"):
            pass
        with included_context("Complete Agent Task With Judge and Human"):
            pass
        with context("with a current task"):
            pass
            with it("should launch a non-blocking child for the doer"):
                # BDD: SIGNATURE
                pass
            with context("with a judge and a human"):
                pass
                with it("should also launch a non-blocking child for the judge"):
                    # BDD: SIGNATURE
                    pass

# ## Close Agent Session Using Sub Agent (agentic)
with description("Close Agent Session Using Sub Agent (agentic)"):
    with context("with someone closing the agent session"):
        pass
        with included_context("Close Agent Session"):
            pass
        with it("should tear down non-blocking doer and judge children"):
            # BDD: SIGNATURE
            pass

# # Run Chat Agent Session (agentic)

# ## Complete Agent Task Using Chat Agent (agentic)
with description("Complete Agent Task Using Chat Agent (agentic)"):
    with context("with an Agent that is a ChatAgent"):
        with context("with a current task"):
            pass
            with included_context("Complete Agent Task"):
                pass
            with context("with a judge prompt"):
                pass
                with included_context("Complete Agent Task With Judge and Human"):
                    pass
                    # verdict is typed into the parent /agent tool — not read from a child transcript
            with context("with a Human participant"):
                pass
                with it("should not invoke slash or ToolsCli for the human"):
                    # BDD: SIGNATURE
                    pass
                with it("should post a parent-chat message that the human should look at the work"):
                    # BDD: SIGNATURE
                    pass
                with it("should include a URL of what to look at (contextRoot)"):
                    # BDD: SIGNATURE
                    pass
                with it("should wait for typed feedback in this window"):
                    # BDD: SIGNATURE
                    pass
            with context("with context tools, actions, or utilities in the doer prompt"):
                pass
                with it("should run those in the parent chat window"):
                    # BDD: SIGNATURE
                    pass
                with it("should not invoke ToolsCli from ChatAgent._run_tools_cli_for"):
                    # BDD: SIGNATURE
                    pass

# ## Persist Chat Agent Queue Across Kit Calls (agentic)
with description("Persist Chat Agent Queue Across Kit Calls (agentic)"):
    with context("with ChatAgentKit tools agent and backlog"):
        pass
        with it("should bind the named AgentSession and forward to Agent"):
            # BDD: SIGNATURE
            pass
        with it("should persist queue state under session.folder"):
            # BDD: SIGNATURE
            pass
        with context("with a later kit instance on the same session name"):
            pass
            with it("should resume the queue from what the session recorded"):
                # BDD: SIGNATURE
                pass

# # End To End Agent Journeys

# ## One Judged Job Via Sub Agent (agentic)
with description("One Judged Job Via Sub Agent (agentic)"):
    with context("with a live SubAgent drain"):
        pass
        with context("with one judged task"):
            pass
            with it("should open the AgentSession"):
                # BDD: SIGNATURE
                pass
            with it("should run doer then judge through the mailbox"):
                # BDD: SIGNATURE
                pass
            with it("should record PASS or FAIL on the session log"):
                # BDD: SIGNATURE
                pass
            with it("should close the session when the backlog is empty"):
                # BDD: SIGNATURE
                pass

# ## Two Item Queue Via Sub Agent (agentic)
with description("Two Item Queue Via Sub Agent (agentic)"):
    with context("with a live SubAgent drain"):
        pass
        with context("with two judged tasks on the backlog"):
            pass
            with it("should drain both in order"):
                # BDD: SIGNATURE
                pass
            with it("should record two verdicts and two complete_task lines"):
                # BDD: SIGNATURE
                pass

# ## Two Item Queue Via Chat Agent (agentic)
with description("Two Item Queue Via Chat Agent (agentic)"):
    with context("with ChatAgent in the parent window"):
        pass
        with context("with two judged tasks on the backlog"):
            pass
            with it("should drain both in order through /agent and /agent-backlog"):
                # BDD: SIGNATURE
                pass
