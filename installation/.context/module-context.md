## Language

*Installation* publishes marked toolset members into an IDE tree (skills, commands, rules, MCP, hooks) so an author does not write those files by hand.

### Installer

- Collects installable toolsets from the repo and writes each marked member to the current *Installation*.
- `/install` is this kit. Point it at an IDE path that exists.

### Destination

- Put `@skill`, `@command`, `@rules`, `@mcp`, or `@hook` on a member when that channel should receive it. Unmarked members stay in-process.

### Installation

- One write channel per destination. Subclasses implement **write**; callers ask `install(tool)`.

Build order: `installation` → `installation/harness_files` → `installation/mcp` → `installation/hooks`

---

# installation
- **Purpose:** Publish a toolset’s marked members into Cursor (or VS Code / Kilo) so the agent can invoke them as skills, MCP, hooks, commands, or rules.
- **Seam (terms):** Installer, Destination, Installation
- **Dependencies (one-way):** `harness/agent_tools`

## Constraint

Do not subclass *AgentToolSet* here. Marks live on members; *Installer* walks them. If `.install-state.json` points at a missing directory, install to `{repo}/.cursor`.

---

# installation/harness_files
- **Purpose:** Marks and writes for markdown channels — skill, slash command, rules, agent files.
- **Seam (terms):** Skill, Command, Rules, MarkdownInstallation, `@skill`, `@command`, `@rules`
- **Dependencies (one-way):** `installation` (*Destination*, *Installation*)

## Constraint

Put `@skill` / `@command` / `@rules` on the member. This package writes the files; it does not enroll MCP or hooks.

---

# installation/mcp
- **Purpose:** Marks a member `@mcp` and runs a stdio host so Cursor can call it as an MCP tool or prompt.
- **Seam (terms):** `@mcp`, McpInstallation, McpServer, McpHost
- **Dependencies (one-way):** `installation`, `harness/agent_tools`

## Constraint

Cursor starts `python -m installation.mcp`. `cdd.ping` is always listed. Only members marked `@mcp` enroll.

---

# installation/hooks
- **Purpose:** Marks a member `@hook("event")` so Cursor stdin events run that Python.
- **Seam (terms):** `@hook`, Hook, HookInstallation, HookServer
- **Dependencies (one-way):** `installation`, `harness/agent_tools`

## Constraint

The event name is the Cursor event (`sessionStart`, `preToolUse`, …). `@hooks(disabled=True)` on a toolset skips every hook on it.
