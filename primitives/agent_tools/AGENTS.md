# agent_tools

- **`toolset.tools`** is the member inventory: `@agent_tool`, `@agent_instructions`, and `@hook` members. Hook-only methods belong here so install can use `tool.destinations` without a second class walk.
- **`toolset.tools_for(destination)`** is the catalog filter MCP and hooks share (`InstallDestination.MCP` / `HOOK`). Do not walk `tools` again in those servers to decide membership.
- **`AgentTool.docstring`** is the install prose for that member — the callable’s docstring (or the rule text when the tool is one slug from a `RulesCollection`). Write that. Do not expand `prompt` or reassemble `toolset.instructions` at install.
- Specs call **`instructions[name].expand`** and **`operations[name].invoke`** on the live toolset. Do not add a YAML request runner for tests.
- **`AgentToolSet.instantiate`** / **`instantiate_all`** construct a toolset from a `module:Class` ref, a class, a `{toolset, context}` dict, a constructor dict on this class, or an already-live object. **`load_toolsets`** is the shared catalog load (one instance per type). Import (`_load`) and `@agent_toolset` checking stay private. There is no `ToolsetLoader`.
