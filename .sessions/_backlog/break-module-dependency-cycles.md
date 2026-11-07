# Break module dependency cycles

**Status: done.** The import graph of the production `.py` files of harness, space, tools, and cdd_guidance (every `import`, function-level and type-only ones included; specs, `_examples`, and fixtures excluded) has no cycle left, and no two modules import each other. Nothing in harness imports space, tools, or cdd_guidance.

The Clean Engineering modules validation on `ensure-domain-orientation-refactor` (d6c41b23) found that module dependencies did not flow one way (`one-way-deps`, `extensions-live-with-the-domain`): following every import, the modules formed one strongly connected group, so no module in it could be changed or tested without the others, and the framework could not stay generic because it imported the practices. Each pair was broken by moving the shared concept down to a module both sides may depend on, or by having the lower module declare a seam the higher one registers with.

## How the framework stopped reaching up
- **The framework's own modules** depend one way, lowest first: harness/name and harness/process; harness/marks; harness/markdown; harness/agent_tools; harness/installation; harness/hooks and harness/mcp; harness/installer; harness/guidance; harness/guidance_actions; then harness/diagnostics and harness/sub_agent.
- **A call's session.** *ToolCall* (harness/agent_tools) declares a *SessionOpener* seam; space/session registers *CallSessions* with `ToolCall.open_sessions_with` when it is imported. `call.session` and `call.session_named(session_file)` are the only ways the framework reaches a session (hook server, guidance actions, rule injection, the MCP server's failure log, the guidance probe, `FileManager.load`). The hook daemon imports every toolset module of the repository at start (`RepositoryToolsets.import_modules`), so the registration holds there as it does in the MCP host.
- **A call's project and chat.** *ChatPointer* moved to harness/agent_tools; the MCP server makes each request `ToolCall.sent(arguments, project)`, which carries the project and the chat to the tool and to the session it logs in (`Session.chat`, read by `SessionLog`). `working_on`, `project_folder`, `project_checkout`, and `ChatPointer.serving`/`current` are deleted; every space object is handed its project. `Sessions` and `Session` require their project.
- **Toasts.** The `@Toast` mark moved to harness/marks. A hook gives its toast in its result (`HookResult.toast`); the hook server hands it to the notifier registered with `HookServer.show_toasts_with`, which tools/prompt_notify registers. `rules_toast` and `TOAST_ARROW` live with the hook result.
- **Project configuration.** *ContextConfig* (`.context/config.json`) moved from space to harness/installation; the hook server and space/session both read it there.
- **Stages.** `stages.py` moved from cdd_guidance/practices to harness/guidance: the stage each fidelity names is framework vocabulary the graph, the catalog, and the board read.
- **Applications.** The catalog takes its project from its call (`Catalog.load(project=...)`, a `@tool_subject` loader) or its constructor. *CanvasVersions* takes the release's folder (`CanvasVersions.in_release(folder)`) and owns `DESIGN_CANVAS_FOLDER`.
- **Rule examples.** The `*_example_harness.py`, `*_rule_eval_harness.py`, and fixture files left harness/graph for each practice's `rules/rule_examples.py` (Clean Engineering also `rules/multi_language_examples.py`), and the specs of practice rules that lived in harness/graph moved beside them.

## How the space and practice pairs were inverted
- **space/repo ↔ space/work_state.** *WorkState* saves names only (`branch_name`, `worktree_folder`); *Repo* turns them into its *Branch* and *Worktree*.
- **space/session ↔ tools/file_manager.** The session owns its file manager, so session → file_manager stays; `FileManager.load` opens the call's session through *ToolCall*.
- **stories ↔ ux.** UX screens show stories, so UX depends on Stories. The Claude Design story canvas (`ClaudeDesignStoryModel`, its explorer, its rules) moved to `ux/model/claude_design/story_canvas.*`; Stories no longer lists a `claude_design` format.

## Left: imports from space up into tools and cdd_guidance (no cycle)
These cross the folder layering harness < space < tools, cdd_guidance, but nothing imports them back, so they close no cycle.
- space/session, space/repo, space/kanban → tools/file_manager (*FileManager*, *FileEntry*). The session owns its file manager; moving tools/file_manager under space would also move its published TypeScript adapter path.
- space/session → cdd_guidance/actions (`session_probe.py` runs Generate and Validate for the session diagnostics).
- space/kanban → cdd_guidance/actions/validate (`report.py`, the saved graph reader; `session_board_tiers.py`) and → generate, and the `*.story.shared.py` story tests → the Stories, DDD, and UX practices.

The import graph is computed with `module_cycles.py` (the session scratchpad), which walks every `import` in the production `.py` files of harness, space, tools and cdd_guidance.
