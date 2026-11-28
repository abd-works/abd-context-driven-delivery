# bolt-01: server-health.report says an app is running when another program holds its port

**Title** - `server-health.report` answers Kanban `running` on its port when the program listening there is not the board's server at all, only a socket that accepts and never answers, so the health panel draws a green Kanban icon and Open opens that other program's port without starting the board.

**Charter** - Bolt, theme 2 (chat bar reconnect, server health, ping and restart). **Tester** - Bolt.

**Story** - Move Work Forward From Chat Bar / Check CDD Server Health In Chat Bar / Open Server Health Panel, scenario "Show every part running on one line" ("hovering Kanban's icon shows ... Kanban: running :8778"), and Open App From Health Panel, scenario "Start the Kanban app, then open it, when it is not running" (with a stranger on the port, the board is never started). No scenario covers a port held by another program.

**Module and class** - `harness/apps/app.py` `App.status` / `AppServer.port` / `PortProbe.answers`: running means only that a TCP connect to 127.0.0.1:port succeeds (`connect_ex(...) == 0`). Drawn by `harness/chat-ui/pane/hooks/health/server-health-wording.ts` `appPartOf`.

**Severity** - wrong result.

**Steps**
1. Sandbox checkout copy (`git archive HEAD`) at `C:\dev\_et\after-1-2-1\bolt\checkout`; in it, `space/kanban/app/packages/session-board/ports.json` = `{"board": [8923]}` and empty folders `space/kanban/app/node_modules` and `space/kanban/app/dist` (so the package reads installed).
2. `CDD_HOME=C:\dev\_et\after-1-2-1\bolt\cdd_home CDD_SERVER_PORT=8921 PYTHONUTF8=1`, from the copy: `python -m harness.mcp`.
3. Start a listener that is no board server: `python dummy.py 8923 tcp` (binds 127.0.0.1:8923, accepts connections, never sends a byte).
4. Over MCP HTTP (`X-CDD-Project: C:\dev\_et\after-1-2-1\bolt\work\proj`): `tools/call server-health.report {}`.

**Expected** - Kanban reads `not running` (or a state that says the port is held by another program), because the board's server does not run; the panel then offers to start it, as "Start the Kanban app, then open it, when it is not running" says. The status is what the health panel and Open trust to decide whether to start the board.

**Actual** - `{"label": "Kanban", "status": "running", "port": 8923, ...}` (and Story UI, served by the same server, reports port 8923). `netstat` shows 8923 held by the dummy python process (pid 27620). The board page is never served, yet the bar would show Kanban green with tip `Kanban: running :8923`, and `App.open` answers that url without starting the board.

**Tier that should catch it** - unit for `App.status` with a probe double that sees a port held by something that is not the app's server (the current `PortProbe` double only says answers / does not answer), heavy for the real probe with a raw listener. No test puts a stranger on an app's port.
