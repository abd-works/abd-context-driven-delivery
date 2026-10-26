---
name: tools-workflow-backlog
description: >-
  Capture an idea on the backlog — GitHub issue + Project Backlog.
  
  With no ``body``, commits the current turn, builds the handoff, and returns
  a ``sub_agent_task``. Launch a non-blocking sub-agent with that prompt; it
  calls this same tool again with the enriched ``body`` to file the issue.
  
  Infer `category` and `theme` unless the user sets them. Types:
  
  - Defect: unexpected or wrong current behavior (the kit should already do this).
  - Small change: a change to an existing feature, utility, or tool. Those are all Small changes unless the addition is very large.
  - Refactor: changing code and where things are without changing functionality.
  - Feature: standing up a new module (a new folder). Example: creating the CLI agent. A small change to an existing feature is not a Feature.
---

Capture an idea on the backlog — GitHub issue + Project Backlog.

With no ``body``, commits the current turn, builds the handoff, and returns
a ``sub_agent_task``. Launch a non-blocking sub-agent with that prompt; it
calls this same tool again with the enriched ``body`` to file the issue.

Infer `category` and `theme` unless the user sets them. Types:

- Defect: unexpected or wrong current behavior (the kit should already do this).
- Small change: a change to an existing feature, utility, or tool. Those are all Small changes unless the addition is very large.
- Refactor: changing code and where things are without changing functionality.
- Feature: standing up a new module (a new folder). Example: creating the CLI agent. A small change to an existing feature is not a Feature.

Use MCP tool: `workflow.backlog(focus: 'str', context: 'str' = '', workspace: 'str' = '', theme: 'str' = '', category: 'str' = '', body: 'str' = '')`
