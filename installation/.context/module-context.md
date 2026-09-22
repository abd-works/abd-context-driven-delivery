## Language

*Installation* publishes marked toolset members into an IDE tree so an author does not write those files by hand. Cursor’s MCP host and hook process live under `harness/`.

### Installer

- Collects installable toolsets from the repo and writes each marked member to the current *Installation*.
- `/install` is this kit. Point it at an IDE path that exists.

### Destination

- Put `@skill`, `@command`, `@rules`, `@mcp`, or `@Hook` on a member when that channel should receive it. Unmarked members stay in-process.

### Installation

- One write channel per destination. Subclasses implement **write**; callers ask `install(tool)`.

### FileInstallation

- Writes skill, command, and rules markdown. Marks live on the member (`@skill`, `@command`, `@rules`).

Build order: `installation` → `harness/mcp` → `harness/hooks`

---

# installation
- **Purpose:** Publish a toolset’s marked members into Cursor (or VS Code / Kilo) so the agent can invoke them as skills, MCP, hooks, commands, or rules.
- **Seam (terms):** Installer, Destination, Installation, FileInstallation, Skill, Command, Rules
- **Dependencies (one-way):** `harness/agent_tools`, `harness/mcp`, `harness/hooks`

## Constraint

Do not subclass *AgentToolSet* here. Marks live on members; *Installer* walks them. If `.install-state.json` points at a missing directory, install to `{repo}/.cursor`. Do not put `installation/` or `harness/` on `PYTHONPATH` as a catalog root — `import mcp` must load the MCP SDK, not `harness.mcp`.
