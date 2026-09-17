# Installer

`install(toolsets=…)` walks **toolsets**, then each **tool**:

```
for toolset in toolsets:
    for tool in toolset.tools.values():
        for installation in self.get_installations(tool):
            installation.install(tool)
    for child in toolset.nested_toolsets:
        for tool in child.tools.values():
            for installation in self.get_installations(tool):
                installation.install(tool)
```

`nested_toolsets` is a `ToolSetCollection` (empty by default). Practice `fidelities` is a `GuidanceCollection`, which is a `ToolSetCollection` of fidelity toolsets — same walk.

`Installation.install(tool)` writes the channel. Do not split it into `installAgentToolSet` / `installGuidance` — both kinds already sit on `toolset.tools` and use the same write. Markdown skips live in `MarkdownInstallation.install`.

Members come from **`toolset.tools`**. Each tool’s install channels come from **`tool.destinations`**. Do not walk class flags into a parallel install record.

- **MCP** — register the operation on the MCP server
- **skill / command / rule** — write `tool.docstring`. If the tool is also `@mcp`, append `Use MCP tool: …`. Do not assemble `toolset.instructions` or expand a prompt. `@rules` is the same write (`rules/{name}.mdc`). A `RulesCollection` is one tool per rule slug.
- **MCP** — register the operation on the MCP server. The slash file is still docstring plus that invoke line.
- **hook** — `@hook("sessionStart")` from `primitives.hooks.hooks` (`hook.EVENTS`). `@hooks(disabled=True)` on the toolset skips those operations. `HookInstallation` lives in that same file and writes Cursor `hooks.json` plus `hook-handlers.json`. Runtime is `primitives/hooks/hook_server.py`. **`@hook` and `@mcp` are independent.**
- Hook-only members belong in **`toolset.tools`** (same walk as `@agent_tool` / `@agent_instructions`). Install reads `tool.destinations`; do not add a leftover class inspect for `_hook`.
- Specs expand and invoke on the live toolset (`instructions[name].expand`, `operations[name].invoke`). Do not add a YAML request runner or `RunError` wrapper for tests.
- Installer specs stay in two files: `installer_spec.py` and `installer_agent_spec.py`. Car deploy/invoke setup lives in those spec files, not a separate installer helper module.
- There is no `ToolsetExtensions` / `extensions.py` on the installer. Sub-agent registration against that walk is disconnected (`utilities/sub_agent/register.py` is a no-op).
- There is no `marks.py` or `installation.py`. They are **annotations** (`Destination.annotate`), not marks or decorators. `Destination` and `Installation` live on `installer.py`. Each install destination is a packager: `skill` / `command` / `rules` / `agent` / `agent_guidance` + `MarkdownInstallation` in `primitives/harness_files`; `hook` + `HookInstallation` in `primitives/hooks/hooks.py`; `mcp` + `McpInstallation` / `McpServer` in `primitives/mcp/mcp_server.py`. Import the packager, not a barrel.
- There is no install `Registry`. `Installer.install()` with no toolsets uses `collect_toolsets()`, which walks the repo (skip `__pycache__`, `examples`, `.venv`, `node_modules`, `.git`) and returns `module:Class` refs. **`install`** constructs each one with **`AgentToolSet.instantiate`**. Pass live toolsets or refs. There is no `toolset_loader.py`.
- The class annotation for collect is `@agent_toolset` only. There is no `@agentic_toolset`.
- `Installer` is itself an `@agent_toolset`. `install` is `@mcp`, `@skill`, and `@agent_tool` so a run can install the installer. `collect_toolsets` and `get_installations` stay public; walk helpers stay private (`_`).
- Paths: `Installer.repo` is the CDD checkout. `McpServer` holds `repo` (CDD), `venv` (`{repo}/.venv`), and `project` (another repo when work is not in the CDD checkout). There is no `repo_paths.py` venv-forensics module.
