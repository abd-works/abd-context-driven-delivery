# cdd_guidance/diagnostics

Diagnostics that run the guidance actions in a probe session.

- **Purpose:** Check, through the live MCP host, that the guidance actions log their work in the session they run in.
- **Seam (terms):** SessionDiagnostics, SessionProbe
- **Dependencies (one-way):** cdd_guidance/actions, space/session, harness/agent_tools, harness/diagnostics, harness/installation, harness/mcp

## SessionDiagnostics : CallDiagnostics

Probe session logging (generate, validate, loops, chat pointers). Made for one call, as every diagnostics toolset is, so it writes the report into the install of the project that call names.

------
----
+ session_diagnostics(): str
+ write_to(diagnostics: InstallDiagnostics): str
	-> SessionProbe.run
---<<writes a section of>>--> InstallDiagnostics
---<<runs>>--> Generate
---<<runs>>--> Validate
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill
---<<annotated with>>--> Command
