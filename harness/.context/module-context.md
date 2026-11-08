# harness

*harness* is the framework every CDD toolset is built on: the annotations an author types, the toolsets and the tool call, the markdown beside a class, the installer, the hook server, the MCP host, the knowledge graph, the practices' and actions' base classes, and the tools above them (diagnostics, chat, the catalog generator, the design canvas, the chat UI plugin). Each module has its own card in its `.context/`; this card says how they stack.

- **Purpose:** Give `cdd_guidance/`, `space/` and `tools/` one framework to build on, which can change and be tested without the code built on it.
- **Seam (terms):** each module's own seam, named in its card.
- **Dependencies (one-way):** none outside `harness/`. `harness/` imports nothing from `space/`, `tools/`, or `cdd_guidance/`, neither directly nor through `importlib` strings; they register with the framework instead (`ToolCall.open_sessions_with`, `HookServer.show_toasts_with`, `PracticeCatalogue.register`, `ActionCatalogue.register` and `run_actions_with`).

## The layers, from the bottom up

The order follows the modules' top-level imports; a module imports only the modules below it.

1. `annotations`: the decorator annotations, *Name*, and `class_folder`. Imports nothing.
2. `process`: starting, naming, and stopping processes, and git. Imports nothing.
3. `markdown`: a class's prose kept in markdown beside it. Imports annotations.
4. `agent_tools`: toolsets, their tools, and the per-call *ToolCall*. Imports annotations and markdown.
5. `installation`: the *Installer* and what it publishes with, and the JSON files CDD keeps in a project. Imports annotations, markdown, and agent_tools.
6. `hooks`: the hook annotations, the hook server, and the hook files. Imports annotations, process, agent_tools, and installation.
7. `mcp`: the MCP host. Imports annotations, process, agent_tools, installation, and hooks.
8. `guidance`: practices, fidelities, rules, stages, and the practice and action catalogues. Imports annotations, markdown, agent_tools, installation, hooks, and mcp.
9. `guidance_actions`: the base of every action, made for the session its call works in. Imports annotations, agent_tools, hooks, and guidance.
10. `graph`: the knowledge graph. Imports annotations, agent_tools, installation, mcp, and guidance.
11. `diagnostics`, `chat`, `catalog_generator`, `design_canvas`, and the `chat-ui` plugin sit on top.

An import placed inside a function to reach a module above is still an upward dependency; move the code to its owner or add a registration instead.

## Constraint

Keep the order above when adding an import: a module that needs something from a module above it takes it through a registration that module makes, so each layer can be tested without the ones on top of it. The layer order is kept here, not in `AGENTS.md`, which agents do not edit (`.claude/rules/learning-from-corrections.md`).
