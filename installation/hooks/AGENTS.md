# hooks

- Declare Cursor handlers with **`@hook("afterAgentResponse")`** from **`installation.hooks.hooks`**. Disable every hook on a toolset with **`@hooks(disabled=True)`** on the class, above `@agent_toolset`, so the mark stays on the registered type. Do not add `.enabled` / `.disabled` flag files.
- Install is **`HookInstallation`** via **`Installer.install`**. It writes Cursor `hooks.json` (one `hook_server.py` command per event) and `hook-handlers.json`.
- **`HookServer(repo_root, toolsets=None)`** owns catalog, invoke, and merge. Cursor runs `hook_server.py` (`HookServer.run`). **`HandlerCatalog`** loads toolsets in `__init__` (`_refs_from_file`, `_collect_refs`, then `AgentToolSet.load_toolsets`). Public catalog surface is the constructor, `toolsets`, and `for_event`. A **`HookHandler`** is one **`tools_for(InstallDestination.HOOK)`** member whose event matches. A toolset annotated **`@hooks(disabled=True)`** is skipped.
- Prompt log and prompt echo are **`@agent_toolset`** classes with `@hook` operations, same as any other hook toolset. The catalog finds them; do not list them in `HookServer`. Do not add a second stdin `main()` on those modules.
- **`@hook` and `@mcp` are independent.** Stacking both writes both artifacts; dispatch does not call MCP.
