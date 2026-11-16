# scripts
The scripts are the command lines a person, a slash command, or a cloud session runs from a terminal. Each one puts the checkout on the import path and calls into the framework, so the work itself lives in `harness/` and `space/` and stays tested there; a script only reads its arguments, calls one entry, prints the result, and returns an exit code.

*Install* (`install.py`, with `install.ps1` and `install-latest.py`) installs CDD into an IDE's folder through the *Installer* and decides which code the shared cdd server serves: pinned to a commit in `~/.cdd/runtime`, or this checkout as it is on disk. `--from-latest` pulls origin main first and reports each step as it starts and ends, so the `/install-latest` command can show progress in the chat.

*Test* (`test.ps1`, `test-with-agent-bdd.ps1`) runs one tier of the suite: unit, heavy, or e2e. The unit tier puts `unit_guard/` on the Python path and runs every spec with its output format `budget_formatter.BudgetDocumentation`, so every spec process times its examples against the unit budget.

*ServiceStart* (`start.py`, with `start_hook.py`, `start_graph_app.py`, `start_graph_web.py`) stops every running copy of a service started from this checkout, starts one, and waits until it answers its ping. *HookPing* and *HttpPing* (`instances.py`, with `ping_hook.py` and `ping_graph_web.py`) ping a service and stop the extra copies, keeping the one that answers. *RepoProcesses* lists the processes started from this checkout and the ports they listen on; *HttpService* names a service by its command line, its ports, and the name its `/ping` gives; *PingAnswers* asks a port for that pong. Each prints one JSON report, so an agent can read the result.

*McpSanity* (`sanity_mcp.py`) stands up the MCP host in this process and pings every enrolled tool without running its body, so a broken registration shows before a chat calls it. *HookExercise* (`exercise_hooks.py`) touches one example file per fidelity and checks that the hook injected that fidelity's rules into the chat. `guidance-diagnostics.py`, `agent_tools_probe_off_host.py`, and `agent-tools-diagnostics-heavy.py` run the diagnostics probes outside the MCP server, and `clean-engineering-validate.py` runs the validate action with the same import path the MCP host uses.

`cloud-setup.sh` builds the virtual environment and installs CDD for a cloud session.

- **Purpose:** Give each job a person or a command runs from a terminal one entry point: install, test, start or ping a service, and probe the installed tools.
- **Seam (terms):** the command lines themselves (`python scripts/install.py`, `scripts/test.ps1 -Suite unit|heavy|e2e`, `scripts/start_*.py`, `scripts/ping_*.py`, `scripts/sanity_mcp.py`, `scripts/exercise_hooks.py`, the diagnostics scripts), their JSON or text reports, and their exit codes: 0 when everything answered or passed, 1 when anything did not.
- **Dependencies (one-way):** harness/installation (*Installer*, *RepositoryToolsets*), harness/mcp (*McpInstallation*, *McpHost*), harness/hooks (*HookDaemon*, *HookServer*, *HookInstallation*), harness/diagnostics (the probes, *App*), harness/process (*RunningProcess*, which also lists the ports a process listens on, *BackgroundStart*), harness/graph (`GRAPH_APP_PORTS`), harness/guidance (*PracticeGuidance*), space/repo (*Repo*, for `--update`), space/session and space/kanban (imported so their apps register before a restart), and cdd_guidance (the validate action, for `clean-engineering-validate.py`). Nothing imports a script except the other scripts here.

## Constraint

Keep the work in the framework and the script thin: a script that grows its own logic is code no spec runs. Start and stop servers only through these scripts or the framework classes they call, so every server is found by its command line in this checkout and the extras are stopped the same way. Run the unit tier through `test.ps1`, so the unit budget applies; running `mamba` directly skips it.
