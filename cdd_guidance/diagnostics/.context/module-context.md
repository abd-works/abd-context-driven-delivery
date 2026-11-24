# cdd_guidance/diagnostics
Diagnostics that run the guidance actions. *SessionDiagnostics* (`session_diagnostics.py`, a *CallDiagnostics* of harness/diagnostics) is the toolset `session-diagnostics.session_diagnostics`, slash `/session-diagnostics`: it runs a *SessionProbe* (`session_probe.py`), which opens a throwaway repository, runs Generate and Validate in a session there through the live MCP host, and checks that each wrote its line to that session's log, then writes the result into the diagnostics file of the install its call names (*InstallDiagnostics*). It sits beside the actions it runs, so the session's core imports no action.

- **Purpose:** Check, through the live MCP host, that the guidance actions log their work in the session they run in.
- **Seam (terms):** SessionDiagnostics (`session-diagnostics.session_diagnostics`, `/session-diagnostics`), SessionProbe.
- **Dependencies (one-way):** `cdd_guidance/actions` (*Generate*, *Validate*), space/session (*Sessions*), `harness/agent_tools`, `harness/diagnostics` (*CallDiagnostics*, `raised_by_a_bug`), `harness/installation` (*RepositoryToolsets*, *InstallDiagnostics*), `harness/mcp`. Nothing imports it; the installer finds its toolset by reading the source.

## Constraint

Run the probe only through `/session-diagnostics` or `session-diagnostics.session_diagnostics` on the live MCP host: it checks what the host logs, so a call that does not go through the host proves nothing. The probe works in a throwaway repository it makes itself; never point it at a person's project, whose session log it would write into. Nothing imports this module, so keep it that way: the session's core and the actions must not import their own diagnostics.
