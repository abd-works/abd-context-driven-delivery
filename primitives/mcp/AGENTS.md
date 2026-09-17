# MCP — agent rules

1. **One package.** Annotation (`@mcp`), install (`McpInstallation`), runtime (`McpServer` / `McpHost`), and `python -m primitives.mcp` live in `primitives/mcp`. Do not add a second host under `utilities/` or `harness/`.

2. **Enroll recorded `@mcp` ops.** `McpServer.start` uses **`AgentToolSet.load_toolsets`** and **`tools_for(InstallDestination.MCP)`**. Do not rescan the class with `getmembers` or invent a `McpToolset` adapter.

3. **stdio + `mcp` SDK.** Local Cursor hosts use stdio. `McpHost` maps `tools/list`, `tools/call`, `prompts/list`, `prompts/get` to `McpServer`. Use `get_type_hints()` for JSON Schema.

4. **JSON Schema must match the Python parameter type.** After resolving hints, map `list`/`Sequence`/`tuple` to `array`, `dict`/`Mapping` to `object`, `bool` to `boolean`, `int` to `integer`, `float` to `number`, `str` to `string`, and `X | None` / unions to `anyOf`. Anything else advertised as `string` makes the host send a string.

5. **Three paths.** `McpServer.repo` is the CDD checkout, `venv` is `{repo}/.venv`, `project` is the other repo when work is not in the CDD checkout. Pass `--repo` / `--project` or `CDD_REPO` / `CDD_PROJECT`.

6. **Do not put `primitives/` on `PYTHONPATH`.** `import mcp` must resolve the MCP SDK, not this package. Import this host as `primitives.mcp` from the repo root.
