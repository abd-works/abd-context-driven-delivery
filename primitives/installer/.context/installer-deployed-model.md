# Installer — installed object model (model fidelity)

Markdown channel for **`primitives/installer`** as it exists today. Describes install-time types and files under `Installer.path` (typically `.cursor/`). Runtime MCP lives in **`utilities/mcp_server`**; domain toolsets live in **`primitives/agent_tools`**.

**Not in this module:** YAML manifest CLI, `tools.ps1`, fenced `toolset:` invoke blocks in installed bodies, `AgentToolSet` member validation (that is `agent_tools`).

---

## Install moment vs runtime moment

| Moment | Owner | Does |
| ------ | ----- | ---- |
| **Install** | `Installer.install` → `Installation` | Walk each tool; write markdown skills/commands/rules; record `@mcp` ops; write `mcp.json` / `hooks.json` |
| **Runtime (MCP)** | `utilities.mcp_server.McpServer` | Read `mcp.json` toolset refs; enroll only `@mcp` ops recorded at install; invoke enrolled tools/prompts |
| **Runtime (agent)** | Cursor agent | Read installed skill/command bodies; follow `@agent_instructions` bodies; call MCP for `@mcp` tails |

Installed skill/command **bodies** are instruction prose from live `AgentInstructions` expansion, or context + `Use MCP tool: \`slug.op(...)\`` when the member is `@mcp`. No shell invoke tail.

**Not in installer:** YAML manifest CLI or a spec-only invoke runner. Specs expand ``instructions[name]`` and invoke ``operations[name]`` on the live toolset.

---

## Module map

```
primitives/installer/
  installer.py         Installer, Destination, Installation; channel write lives on packagers
```

Consumer: MCP start uses **`AgentToolSet.instantiate`**.

---

## Language companion

**Installer** holds `ide`, `path`, and **`collect_toolsets()`** — the only logic it owns internally. `collect_toolsets()` walks the repo, parses Python for install annotations, and returns toolset instances to install.

**`install(toolsets=…)`** walks each toolset’s **`tools`**, then **`tool.destinations`** to pick channel installments. **`Installation.install(tool)`** writes that channel from the `AgentTool`. Returns **`mcp`** for runtime bind.

**Installation** **`install(tool)`** calls subclass **`write`**. **`MarkdownInstallation.install`** skips unmarked tools and rules-only members, then writes. **`Installer`** owns the run-level **`McpInstallation`** and **`HookInstallation`**.

**`McpInstallation`** owns `mcp_operations`, `write_mcp_manifest`, and `bind`. **`HookInstallation`** owns `_events` and `write_hooks_manifest`. **`MarkdownInstallation`** owns skill, command, and rules files.

Members come from **`toolset.tools`** (including nested fidelity toolsets via **`toolset.nested_toolsets`**). Channel choice is **`Installer.get_installations(tool)`** from **`tool.destinations`**:

---

## Installer                                                         <!-- Md -->

Installer(ide: str | None = None, path: Path | None = None)
------
ide: str
	Invariant: defaults from .install-state.json or "Cursor"
path: Path
	Invariant: defaults from ide — Cursor ".cursor", VS Code ".github", Kilo ".kilo"
----
collect_toolsets(): list[Any]
	Interaction:
		walk the repo for ``.py`` files (skip cache, examples, venv, node_modules, git)
		AST-parse each ``.py`` for class/member install annotations
		instantiate each installable class; return tool instances
install(tools: Iterable | None = None) -> McpInstallation
	Interaction:
		run = InstallRun.for_ide(ide, path)
		for toolset in (toolsets or collect_toolsets()): install that toolset
		persist {ide, path} to primitives/installer/.install-state.json
		return run.mcp

---

## InstallRun                                                         <!-- Md -->

InstallRun(ide, path)
------
ide: str
path: Path
mcp: McpInstallation
hook: HookInstallation
----
(for_ide(ide, path): InstallRun)
(install(tool): None)
	Interaction: write from the AgentTool and its destinations

---

## Installation (channel template method)                             <!-- Md -->

Installation(ide, path, toolset_ref="")
------
ide: str
path: Path
----
(for_annotation(mark): type[Installation])
	Interaction: ``mcp`` → McpInstallation; ``hook`` → HookInstallation; ``skill`` / ``command`` → MarkdownInstallation
(install(tool): None)
	Interaction: write(tool)
(write(tool): None)
	Interaction: subclass implements channel write from the AgentTool

---

## MarkdownInstallation : Installation                               <!-- Md -->

MarkdownInstallation(ide, path)
------
(write(tool): None)
	Interaction: write skill/command/rules markdown under path/ from the AgentTool

---

## McpInstallation : Installation                                     <!-- Md -->

McpInstallation(ide, path, toolset_ref="")
------
mcp_operations: list[McpOp]
_bound: bool
----
(write(tool): None)
	Interaction: record_operation; write_mcp_manifest
(record_operation(tool): None)
	Interaction: when tool.install_to_mcp append McpOp(mcp_name=slug.op, kind=tool|prompt, toolset, name, callable)
(write_mcp_manifest(): None)
	Interaction:
		refs = sorted toolset_ref(op.tool) for all recorded ops
		write path/mcp.json → mcpServers.cdd.args = ["-m", "mcp_server", "--toolsets", refs…]
(bind(server: McpServer): None)
	Interaction: for each McpOp call server.enroll(op)

---

## HookInstallation : Installation                                    <!-- Md -->

HookInstallation(ide, path)
------
_handlers: list[dict]
----
(write(tool): None)
	Interaction:
		when tool.install_to_hook on an AgentToolSet member:
			write skills/hook-{name}/SKILL.md from tool.description
			append {event, operation, ref} to _handlers
			write Cursor hooks.json dispatch command for each event
			write hook-handlers.json

---

## McpOp                                                              <!-- Md -->

McpOp(mcp_name, kind, tool, operation, member)
------
mcp_name: str
	Invariant: "{tool_slug}.{operation}"
kind: str
	Invariant: "tool" if @agent_tool else "prompt" if @agent_instructions
tool: Any
operation: str
member: Callable

---

## Installed artifacts (under Installer.path)                        <!-- Mu -->

```
.cursor/                          (Cursor default)
  skills/
    {domain}/{name}/SKILL.md       context tools, actions, utilities, formats
    hook-{operation}/SKILL.md      @hook members
  commands/*.md                    Cursor command prompts (@command / @prompt)
  rules/*.mdc                      @rules collections
  mcp.json                         MCP server registration
  hooks.json                       hook event → command map
```

VS Code uses `prompts/` instead of `commands/`. Path comes from `Installer.path`, not necessarily repo root.

---

## External types (not defined here)                                  <!-- Mu -->

| Type | Module | Role in install walk |
| ---- | ------ | -------------------- |
| `AgentToolSet` | `agent_tools` | Tool with `@agent_tool` / `@agent_instructions` |
| `PracticeGuidance` | `guidance` | Context tool + fidelities |
| `Guidance` / `FidelityGuidance` | `guidance` | Skill/command/rules from @markdown marks |
| `AgentInstructions` | `agent_tools` | Supplies `.prompt` for installed action bodies |
| `McpServer` / `McpTool` / `McpPrompt` | `utilities/mcp_server` | Runtime enrollment from `McpOp` |

---

## Requirements trace (code → model)                                  <!-- Mu -->

| Requirement | Code | Model |
| ----------- | ---- | ----- |
| Install entry | `Installer.install` → `Installation.install` | `Installer` → channel `write(tool)` |
| Collect toolsets | `Installer.collect_toolsets` | AST walk the repo |
| Member walk | `toolset.tools` + `tool.destinations` | `AgentTool` |
| Markdown files | `MarkdownInstallation.write` | `skills/`, `commands/` or `prompts/`, `rules/` |
| MCP registration | `McpInstallation.write_mcp_manifest` | `mcp.json`, `McpOp` list |
| MCP runtime | `McpServer.bind_from` / `start` | enroll from install-recorded ops only |
| Hooks | `HookInstallation.write` | Cursor `hooks.json` dispatch + `hook-handlers.json` + `skills/hook-*/SKILL.md` |
| Toolset import | `AgentToolSet.instantiate` | MCP `start()` constructs `module:Class` refs from `mcp.json` |
