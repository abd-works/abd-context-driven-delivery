# bolt-03: while the cdd server restarts, the chat bar says "Tools missing" and tells the person to reinstall

**Title** - During a `cdd.restart`, which waits for running calls (the chat bar's own 25-second guidance long-poll among them), `server-health.report` answers after 10 seconds with the server's "still running" sentence, not an error; the chat bar reads any answer that is not JSON as missing tools, so the health mark turns amber `!` with the headline "Tools missing - 290 loaded, server-health.report is not one of them." and the fix "Press Run install, then open a new session.", while `/ping` and `cdd.ping` both answer OK the whole time.

**Charter** - Bolt, theme 2 (chat bar reconnect, server health, ping and restart). **Tester** - Bolt.

**Story** - Move Work Forward From Chat Bar / Check CDD Server Health In Chat Bar / Display Server Health Mark, scenario "Show the tools missing mark" (only when server-health.report "is not one of them"); no scenario covers a restarting server.

**Module and class** - `harness/chat-ui/pane/hooks/health/server-health-client.ts` `askServer` (every `CddToolFailed` becomes `tools-missing`) with `harness/chat-ui/pane/hooks/shared/cdd-tool.ts` `replyOf` (a reply that is not JSON is a `CddToolFailed`); the still-running answer comes from `harness/mcp/mcp_server.py` `_ToolCalls` (`structuredContent.still_running`), which the module card says is how a client should recognise it. The wait is `McpHost.restart` / `harness/mcp/restart_gate.py` `_RestartGate.restarting`.

**Severity** - misleading message (wrong mark and wrong fix; Reconnect is not offered in this state, only Run install).

**Steps**
1. Sandbox server: `CDD_HOME=C:\dev\_et\after-1-2-1\bolt\cdd_home CDD_SERVER_PORT=8921 PYTHONUTF8=1`, from the checkout copy `python -m harness.mcp`; project `work/proj` (a git repo with its main session).
2. Over MCP HTTP (`X-CDD-Project: ...\work\proj`), at t=0: `session.guidance_selection_after {"version": 999, "session": "main"}` (the waiting read the chat bar always holds open); t=1 s: `cdd.restart {}`; t=2.5 s: `server-health.report {}`; t=3 s: `GET /ping` and `cdd.ping`.
3. Feed that answer to the bar: in a sandbox copy of `harness/chat-ui/pane`, a plugin test (`claude plugin test pane`) whose `mcp.call` answers `server-health.report` with `{content: [{type: 'text', text: <the sentence>}], structuredContent: {still_running: {...}}}`, then `$.prompt.submit(...)` (which runs `refreshHealth`) and mount `AbovePrompt`. Test file: `C:\dev\_et\after-1-2-1\bolt\pane\hooks\health\bolt-health.test.ts`.

**Expected** - A server that is up but busy restarting reads as up (or as restarting / still answering), never as missing tools; `server-health.report` is in the tool list the whole time.

**Actual** - Step 2: `/ping` `{"ok":true,...}` and `cdd.ping` `pong` at once; `server-health.report` after 10.3 s, `isError=False`: "server-health.report is still running after 10 seconds; it was not started again. ..."; the long-poll ended at 25.3 s and the restart answered at 26.0 s. Step 3: the stored health is `{"connection":"tools-missing","problem":"server-health.report is still running after 10 seconds; ...","toolCount":290}` and the panel draws "Tools missing / 290 loaded, server-health.report is not one of them." with Details and Run install. The same misreading happens for any tool failure of the report (an `isError` such as ProjectNotNamed), each shown as "tools missing".

**Tier that should catch it** - unit, a plugin test beside `server-health-client.ts` with a still-running answer (the client's tests were removed in 8c56ab052, so nothing plays the health mark now); heavy for the server half, a restart held by a running long call. The chat bar's own waiting read makes every restart from a chat with the bar open take up to 25 s.
