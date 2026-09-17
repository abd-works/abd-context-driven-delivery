# Harness deploy

## Module layout

- **`extensions.py`** — `ToolsetExtensions` registry for sub-agents, action run handlers, and peer discoverers.
- **`register.py`** — import on CLI startup to wire `@agent_instructions` into `ToolsetExtensions`.
- **`types.py`** — `RunRequestDocument`, `RunResponseDocument`, `YamlValue` wire aliases.
- **`repo_paths.py`** — checkout venv and `sys.path` helpers for `python -m harness`.
- **`runner.py`** — `ToolsetRunner` / `InstructionRunner` YAML invoke path.

Domain toolset types and recipe validation stay in **`primitives/agent_tools`**.

## MCP deploy vs MCP runtime

**Deploy writes registration and invoke tails only — never Python server scaffolding.**

| Moment | Owner | Writes / does |
| ------ | ----- | ------------- |
| **Deploy** | `McpDeployment` + `MarkdownDeployment` | `mcp.json` registration (`python -m mcp_server --toolsets module:Class,…`); skill/command bodies with MCP invoke tail |
| **Runtime** | `utilities/mcp_server` | One stdio host for the repo; `McpServer.start(refs)` or `bind_from(deployment.mcp)` enrolls only `@mcp` ops recorded by the deploy walk |

Do not generate `mcp_server` Python files during deploy. Do not rescan the whole registry at server start — load the listed toolset refs and enroll their recorded `@mcp` ops via `operation_writes`, same walk as deploy.

## Other deploy rules

- **`Skill.relative_path()`** must include `self.folder` when set — e.g. `skills/actions/grill/SKILL.md`, `skills/practices/stories/SKILL.md`. Flat `skills/{name}/` is only when `folder` is empty (harness prompts, formats). Cursor and Kilo use nested folders; do not flatten all skills to the skills root.
- **Format skills** have no fixed toolset. In MCP mode, tell the agent to call the in-scope tool's `generate` MCP tool with the format in arguments — do not render a placeholder toolset slug like `the in-scope context tool.generate`.
- Write `.cursor/mcp.json` under the actual deploy path (`Harness.path`), not the repo root unless that is the deploy path.
- Never write `~/.cursor/mcp.json`. Harness deploy is project-scoped.
- On Windows, readonly `.cursor/skills/` folders block `shutil.rmtree` during deploy. Clear attributes before `write_deploy` if drop steps fail with `PermissionError`.
