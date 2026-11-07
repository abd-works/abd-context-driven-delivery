# harness/diagnostics
*AgentToolsProbe* checks the space, harness, and tools operations one install published, through the running MCP host; a person runs it as `agent-tools-diagnostics.agent_tools_diagnostics` (`/agent-tools-diagnostics`) and reads the result under `agent_tools` in `diagnostics.json`.
*GuidanceProbe* checks an install's practice and fidelity instructions and calls each guidance action with probe arguments; a person runs it as `guidance-diagnostics.guidance_diagnostics` (`/guidance-diagnostics`) and reads the result under `guidance` in `diagnostics.json`.

- **Purpose:** Check that what an install published answers through the live host, so a broken publication shows up in a report rather than in a failing chat.
- **Seam (terms):** AgentToolsProbe, ProbeRequiresServingHost, GuidanceProbe; the MCP operations `agent-tools-diagnostics.agent_tools_diagnostics` and `guidance-diagnostics.guidance_diagnostics`
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/installer, harness/mcp, harness/guidance, harness/name, space/session (a probe of a guidance action opens a session to call it in). Nothing in the framework imports it.

## Constraint

Run a probe through the MCP host serving the install (`serving_mcp_host()`); a probe that builds its own host checks code the chats do not run. Keep the probes here, above the modules they check, so a module never imports its own checker.
