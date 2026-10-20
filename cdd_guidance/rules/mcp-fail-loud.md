---
description: "When a slash command or workflow names an MCP tool, call MCP only; if MCP fails, stop and report — no shell workaround"
alwaysApply: true
---

# MCP fail loud

Slash commands, skills, and `@agent_instructions` that say **Use MCP tool:** or name a tool such as `repo.new_branch`, `session.session`, or `repo.push` require the **CDD MCP host**. Run that MCP call from the agent integration.

When the MCP call errors, times out, returns invalid parameters, or the tool is missing from the catalog, **stop**. Tell the user what failed (tool name, error text, and whether the MCP host looks running). Ask them to fix MCP — reload Cursor, restart the **cdd** server, re-run `python scripts/install.py`, check `.cursor/diagnostics.json` — before retrying.

**Do not** substitute Shell, `python -c`, `AgentToolSet.instantiate(...)`, or `scripts/*.py` to complete the same step unless the deployed instructions explicitly say that path is the only entry (for example **`/install`** and **`/clean`**, which are `@agent_tool` without MCP).

Shell invoke tails on deployed markdown apply only to operations that are **not** on MCP. They are not a backup when MCP breaks.

Matching a problem by hiding it behind a shell path leaves MCP broken for the next turn and trains the wrong habit. Fail loud so the integration gets fixed.
