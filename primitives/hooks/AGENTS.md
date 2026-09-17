# hooks

- Declare Cursor handlers with **`@hook("afterAgentResponse")`** from **`primitives.hooks.hooks`**. That class and **`HookInstallation`** live in the same file. Use **`always=True`** for handlers that should run without an enable flag (prompt log, skill inject).
- Install is **`HookInstallation`** via **`Installer.install`**. It writes Cursor `hooks.json` (one `dispatch.py` command per event) and `hook-handlers.json`.
- **`dispatch.py` is the Cursor process only** — parse stdin, call marked operations, print the merged result. Do not put prompt-log or skill-inject logic in dispatch.
- Prompt log, skill inject, and prompt echo are **`@agent_toolset` hosts** (`PromptLog`, `SkillInject`, `PromptEcho`) with one `@hook` method per event. Do not add a second stdin `main()` on those modules.
- **`@hook` and `@mcp` are independent.** Stacking both writes both artifacts; dispatch does not call MCP.
