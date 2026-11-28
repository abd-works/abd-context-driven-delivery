# sparky-05: a project whose config.json does not parse gets no tool list at all, not even ping and restart

**Title** - When a project's `.context/config.json` is not valid JSON, the cdd server answers that project's `tools/list` with an error, so a chat on it sees no tools at all, including the built-in `cdd.ping` and `cdd.restart`; before d58373b13 the list did not read the config and still answered.

**Charter** - Sparky, theme 1. **Tester** - Sparky.

**Story** - no scenario covers this. `ProjectToolsets.start` and `McpServer.enroll` promise "the tool list never fails"; `ProjectToolsets._with_guidelines` records a folder that cannot be imported rather than failing, but does not catch `MalformedContextConfigError`.

**Module and class** - `harness/mcp/mcp_server.py` `ProjectToolsets._with_guidelines` -> `ProjectGuidelines.own_classes` / `.folder` -> `ContextConfig.load` raises `MalformedContextConfigError` (a `JsonFileUnreadable`, not one of `AgentToolSet.LOAD_FAILURES`), out through `McpHost._server_for` and `tools_listed_for`.

**Severity** - blocks work (a person with a typo in the config has a chat with no CDD tools; an MCP client may mark the whole cdd server failed). The message itself is clear.

**Steps**
1. Server as in sparky-01 (`python -m harness.mcp --port 8911`).
2. Project `work/malformed` (git repo), `.context/config.json` = `{ "guidelines": ["stories",` (cut off).
3. MCP `initialize`, then `tools/list` with `X-CDD-Project: C:/dev/_et/after-1-2-1/sparky/work/malformed`.
4. Fix the file to `{"guidelines": ["stories"]}` and list again.

**Expected** - The tool list answers (at least the built-ins and the toolsets that do not depend on the config, with patterns left out and the reason recorded, as for an unimportable guidelines folder); calls that need the config fail with the clear message.

**Actual** - `{"jsonrpc":"2.0","id":2,"error":{"code":0,"message":"C:\\dev\\_et\\after-1-2-1\\sparky\\work\\malformed\\.context\\config.json is not a readable JSON object (Expecting value: line 2 column 1 (char 28)); repair it before CDD changes it"}}`. After step 4 the list answers (290 tools), so the failure is not cached.

**Tier that should catch it** - unit (`harness/mcp/project_guidelines_spec.py` with an unreadable config). No spec gives the per-project server a config that does not parse.
