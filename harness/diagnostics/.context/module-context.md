# harness/diagnostics
*AgentToolsProbe* checks the space, harness, and tools operations one install published, through the running MCP host; a person runs it as `agent-tools-diagnostics.agent_tools_diagnostics` (`/agent-tools-diagnostics`) and reads the result under `agent_tools` in `diagnostics.json`.
*GuidanceProbe* checks an install's practice and fidelity instructions and calls each guidance action with probe arguments; a person runs it as `guidance-diagnostics.guidance_diagnostics` (`/guidance-diagnostics`) and reads the result under `guidance` in `diagnostics.json`.

- **Purpose:** Check that what an install published answers through the live host, so a broken publication shows up in a report rather than in a failing chat.
- **Seam (terms):** the MCP operations `agent-tools-diagnostics.agent_tools_diagnostics` and `guidance-diagnostics.guidance_diagnostics`; each probe reports a section whose colour is red when any probe in it failed, so the reply and `diagnostics.json` agree.
- **Dependencies (one-way):** harness/agent_tools (*ToolCall*, which carries the call's project and the MCP host answering it), harness/installation, harness/installer (*Installer*, made for the call's project, writes the section), harness/mcp, harness/guidance. A probe of a guidance action calls it in the main session of a temp project, which *ToolCall* opens. Nothing in the framework imports it, and it imports nothing above the framework.

## Constraint

Run a probe through the MCP host answering the diagnostics call (`call.mcp_host`); a probe that builds its own host checks code the chats do not run. A tool that does not answer within the probe's time limit is reported red and left running, so one hung tool never hangs the report. Keep the probes here, above the modules they check, so a module never imports its own checker.
