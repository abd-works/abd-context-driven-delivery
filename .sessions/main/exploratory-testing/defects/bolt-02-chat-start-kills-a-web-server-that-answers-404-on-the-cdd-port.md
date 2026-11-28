# bolt-02: a chat's start stops another program's web server on the cdd port when it answers anything but 200

**Title** - When another program's web server holds the cdd server's port and answers `/ping` with a 404 (or any status other than 200, or 200 JSON without `"ok": true`), `connect.py --start`, which the cdd plugin runs as every chat starts, reads it as "nothing answers", stops that program's process, and starts a cdd server on its port, all without a word; a server that answers 200 with text that is not JSON is instead refused loudly with *PingReplyUnreadable* and left running.

**Charter** - Bolt, theme 2 (chat bar reconnect, server health, ping and restart). **Tester** - Bolt.

**Story** - no scenario covers this. The promise is in `harness/mcp/mcp_address.py` *PingReplyUnreadable*: "the program answering on the port is no cdd server ... Read as nothing answering, the next start would try the port another program holds and fail for a reason nobody sees". `ServerDaemon._started` stops "a process still holding the port without answering, such as a hung server"; a server that answers 404 is answering.

**Module and class** - `harness/mcp/mcp_address.py` `McpAddress.ping_answer` (`text = ... if reply.status == 200 else ""`, then `answer if isinstance(answer, dict) and answer.get("ok") else None`), used by `harness/mcp/scripts/connect.py` `ensure_server` and `harness/mcp/mcp_daemon.py` `McpDaemon.running`; the stop is `harness/process/server_daemon.py` `ServerDaemon._started` (`holder.stop(...)`).

**Severity** - wrong result (another program the person runs is stopped without warning).

**Steps**
1. Sandbox cdd home `C:\dev\_et\after-1-2-1\bolt\cdd_home`, installed from the checkout copy (`CddHome().serve_from(copy)`, `connect.py` copied in). `PYTHONUTF8=1`, `CDD_HOME` set, `CLAUDE_CODE_SESSION_ID` unset, `CDD_SERVER_PORT=8923`.
2. Start a plain web server on 8923 that answers every request `HTTP/1.1 404 Not Found` with body `not found` (`python dummy.py 8923 http404`). `curl http://127.0.0.1:8923/ping` -> `not found 404`.
3. From `work/proj`: `python C:\dev\_et\after-1-2-1\bolt\cdd_home\connect.py --start`.
4. Repeat with the server answering `200` and body `hello from another program` (`python dummy.py 8923 httptext`).

**Expected** - The program on the port is left running and the start fails loudly naming the port and the program, exactly as it does for the 200 non-JSON case, since a reply of any kind means some program is answering there.

**Actual** - Step 3 exits 0 in 3.7 s with no output; the dummy web server (pid 5820) is gone, and 8923 is now held by a new cdd server (pid 61516, `/ping` -> `{"ok":true,...}`). Step 4 exits 1 with `PingReplyUnreadable: the program answering on port 8923 is no cdd server this code can read: its ping reply is not JSON: 'hello from another program'` and the dummy keeps the port. The same 404 reading makes `McpDaemon.running()`/`is_running()` answer "not running" and `McpDaemon.stop()` stop the foreign process.

**Tier that should catch it** - unit for `McpAddress.ping_answer` with a reply double of status 404 and of 200 JSON without `ok` (the spec covers only 200 JSON and 200 non-JSON), heavy for `connect.py --start` against a real foreign listener. No test puts a web server that is not cdd on the port.
