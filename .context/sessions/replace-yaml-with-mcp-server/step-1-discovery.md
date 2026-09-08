# Step 1 — Discover with real conditions (mcp_server)

Manual verification per [testing-approach.md](../../../context_tools/clean_engineering/rules/testing-approach.md). No automated tests in this pass — call exactly as a host would.

## Real toolset: Echo

**Ref:** `echo.echo:Echo`

| Step | Action | Observed |
|------|--------|----------|
| Start | `McpServer.start(("echo.echo:Echo",))` | `started=True` |
| Discover tools | `list_tools()` | `("echo.fence",)` |
| Discover instructions | `list_instructions()` | `()` — `echo_session` is `@agent_instructions`, not `@mcp_instruction` |
| Parameters | `invocable_parameters_for("echo.fence")` | `("body",)` |
| Invoke | `invoke_tool("echo.fence", {"body": "verify real tool path"})` | Fenced `str` with DO-NOT-FOLLOW header/footer and body verbatim |
| Missing tool | `invoke_tool("echo.missing", {})` | `KeyError: 'echo.missing'` |

**Dotted name:** `echo.fence` (module slug `echo`, not `echo_echo`).

## Fixture toolset: HostingDemo (examples only)

**Ref:** `mcp_server.examples.hosting_demo.hosting_demo:HostingDemo`

| Step | Action | Observed |
|------|--------|----------|
| Discover tools | `list_tools()` | `hosting_demo.increment`, `hosting_demo.read_count` |
| Discover instructions | `list_instructions()` | `plan_work`, `guidance_only`, `orchestrate_with_plain` |
| Invoke tool | `invoke_tool("hosting_demo.increment", {"step": 2})` | `2` |
| State | `invoke_tool("hosting_demo.read_count", {})` | `2` |
| Invoke instruction | `invoke_instruction("hosting_demo.plan_work", {"concept": "widgets"})` | `{"concept": "widgets", "count": 2}` — `tool(self.increment, step=2)` ran inside orchestration |

## Signatures for step 2 (failures / edges to lock)

No happy-path failures. Candidate regression signatures from discovery:

- `it should reject invocation when the MCP tool name is unknown` — `KeyError`
- `it should expose only @agent_tool members as MCP tools on a real toolset` — Echo has one tool
- `it should not expose @agent_instructions as MCP instructions` — Echo `echo_session` absent from `list_instructions()`

## Next (step 2)

Lock fast suite in `mcp_server_spec.py` matching observed shapes above; stubs only at architecture boundaries, never on `McpServer`.
