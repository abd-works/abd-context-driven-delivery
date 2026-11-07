# harness/sub_agent
*SubAgent* publishes `sub-agent.sub_agent`, the operation that hands a recipe to a background sub-agent and lets the current conversation go on without waiting. The `@subAgent` mark, which puts the same hand-off at the start of any member's description, stays in harness/agent_tools beside the toolsets that read it.

- **Purpose:** Let an agent delegate work to a sub-agent through one published operation.
- **Seam (terms):** SubAgent; the MCP operation and skill `sub-agent.sub_agent`
- **Dependencies (one-way):** harness/agent_tools (the toolset marks and `SUB_AGENT_CALLER_PREAMBLE`), harness/installation (`@skill`), harness/mcp (`@mcp`).

## Constraint

Do not call `sub-agent.sub_agent` from inside the sub-agent it launched; the hand-off would start another background agent for the same work.
