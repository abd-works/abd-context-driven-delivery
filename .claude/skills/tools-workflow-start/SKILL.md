---
name: tools-workflow-start
description: >-
  Hand work to a background sub-agent and continue without waiting.
  
  Do not perform the delegated work in this conversation. Do not wait for the
  sub-agent to finish.
  
  Launch the Task tool with run_in_background true and subagent_type
  generalPurpose. Pass the instructions below as the task prompt.
  
  Tell the user you launched a non-blocking sub-agent and summarize what you delegated.
  
  Start work from a GitHub issue — In Progress, WorkSession, session branch.
  
  ``kind: sub_agent`` / ``launch: non_blocking`` — the parent launches a sub-agent
  for this operation and does not wait. Inside that sub-agent, run start (In Progress,
  open WorkSession, session branch) then continue the ticket work.
---

Hand work to a background sub-agent and continue without waiting.

Do not perform the delegated work in this conversation. Do not wait for the
sub-agent to finish.

Launch the Task tool with run_in_background true and subagent_type
generalPurpose. Pass the instructions below as the task prompt.

Tell the user you launched a non-blocking sub-agent and summarize what you delegated.

Start work from a GitHub issue — In Progress, WorkSession, session branch.

``kind: sub_agent`` / ``launch: non_blocking`` — the parent launches a sub-agent
for this operation and does not wait. Inside that sub-agent, run start (In Progress,
open WorkSession, session branch) then continue the ticket work.

Use MCP tool: `workflow.start(ticket: 'str', instructions: 'str' = '', workspace: 'str' = '', copy_body: 'bool' = False, workflow_state: 'str' = 'specification')`
