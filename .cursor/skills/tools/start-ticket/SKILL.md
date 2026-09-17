---
name: start-ticket
description: "Start work from a GitHub issue — In Progress, WorkSession, session branch."
disable-model-invocation: true
---

Start work from a GitHub issue — In Progress, WorkSession, session branch.

        ``kind: sub_agent`` / ``launch: non_blocking`` — the parent launches a sub-agent
        for this operation and does not wait. Inside that sub-agent, run start (In Progress,
        open WorkSession, session branch) then continue the ticket work.

Use MCP tool: `workflow.start(ticket: 'str', instructions: 'str' = '', workspace: 'str' = '', copy_body: 'bool' = False, workflow_state: 'str' = 'specification') -> 'dict[str, str | int]'`
