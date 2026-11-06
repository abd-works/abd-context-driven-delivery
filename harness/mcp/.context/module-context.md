# mcp — module context

**Layer:** MCP Invocation Layer  
**Location:** `harness/mcp`  
**Ticket theme:** `theme:mcp-invocation-layer` (see `.context/workflow-packages.yaml`)

## Purpose

Run the **one cdd server** every chat in every project talks to, and publish `@mcp` members as its tools. One MCP package: the `@mcp` annotation, `McpInstallation` (writes the IDE's `cdd` entry and records operations), the server (`McpServer` + `McpHost`), its process (`McpDaemon`), and its install folder (`CddHome`, `~/.cdd/`).

## Seam

`mcp`, `McpInstallation`, `McpServer`, `McpHost`, `McpDaemon`, `CddHome`, `ProjectNotNamed`

## Public API

- The server works from `AgentTool` directly: its `mcp_name`, `description`, `input_schema`, and `invoke`. An operation is published as a tool; instructions are published as a prompt whose call answers with them expanded.
- `McpInstallation.write` — record the `AgentTool` and write the `cdd` entry: the server's URL, and how each request names its project
- `McpInstallation.ensure_server` / `pin_server` / `serve_from_checkout` — start the server when none answers; change which code serves every chat
- `McpServer.start` / `bind_from` / `for_project` — enroll recorded `@mcp` ops only; one runtime per project
- `McpHost.from_refs` / `serve` / `dispatch` / `standup` — the server; `cdd.ping` and `cdd.restart` are always listed
- A tool's answer becomes JSON through `data_of` (`harness.installation.destination`), the one serializer, so a path reads with forward slashes in every answer.
- `McpDaemon.ensure` / `ping` / `stop` / `restart` — find, start, and stop the server process
- `CddHome.install` / `pin` / `serve_from` / `source` — `~/.cdd/runtime.json` and the pinned copy in `~/.cdd/runtime/`

## The one server

- **Transport:** MCP over Streamable HTTP at `http://127.0.0.1:47800/mcp` (`CDD_SERVER_PORT` changes the port; specs use a free one). `GET /ping` answers `{ok, pid, source, projects}`. Only this machine's clients get in: the Host header must name the port, and a browser page's Origin is refused.
- **Process:** `python -m harness.mcp [--port N] [--toolsets a:B,…]`, started from the checkout it serves. The exclusive bind on the port is the claim, so a second start exits quietly. It publishes `~/.cdd/server.json` and logs to `~/.cdd/server.log`.
- **Started on demand:** Claude Code's `cdd` entry runs `~/.cdd/connect.py` as its `headersHelper` before it connects; the script starts the server when none answers. Cursor and VS Code cannot run a helper, so the installer's `sessionStart` and `afterAgentResponse` hooks start it there, and `python scripts/install.py` starts it for every IDE.
- **One install location:** `~/.cdd/runtime.json` names the checkout the server runs and the Python it runs on. The first install pins it to a copy of the installing checkout's current commit in `~/.cdd/runtime/`. A later install from any worktree leaves it alone, so installing never repoints every open chat. `install.py --pin-runtime` re-pins to the current commit; `install.py --serve-from-checkout` serves a checkout as it is on disk, for working on CDD itself. Both restart the process.
- **Reload:** `cdd.restart` reloads the server's Python in place, for every chat, on the same connections. Each project's toolsets start again on the new code at its next call.

## The project on each request

- Every request names its chat's project in the `X-CDD-Project` header. Claude Code gets it from `connect.py`, which runs in the chat's own folder; Cursor and VS Code send `${workspaceFolder}`; a temp install tree names its own folder.
- The server runs each call inside `space.work_state.working_on(project)`, so `project_checkout()` and `project_folder()` answer that chat's project, and `Session` keeps one current session per project. Nothing reads the process's own folder or `CDD_PROJECT` while a call runs.
- Each project gets its own toolset objects (`McpServer.for_project`), so state a toolset keeps between calls never crosses between chats.
- A tool call with no header fails with `ProjectNotNamed`; only `cdd.ping` and `cdd.restart` answer without one.
- Code that runs outside a call — a script, a spec — names its project with `working_on`, or falls back to `CDD_PROJECT`, then the current folder.
