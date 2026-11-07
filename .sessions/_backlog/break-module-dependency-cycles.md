# Break module dependency cycles

The Clean Engineering modules validation on `ensure-domain-orientation-refactor` (d6c41b23) found that module dependencies do not flow one way (`one-way-deps`, `extensions-live-with-the-domain`). Following every import, function-level ones included, the modules formed one strongly connected group. While that group exists, no module in it can be changed or tested without the others, and the framework cannot stay generic because it imports the practices.

To break a pair, move the shared concept down to a module both sides may depend on, or have the lower module accept the higher one's object through a seam it declares (registration) instead of importing it.

## Done: the framework's own modules depend one way
No two harness modules import each other any more. The order, lowest first:
- **harness/name** (*Name*, moved out of harness/agent_tools) and **harness/process** (*RunningProcess*, *StoppableProcess*, and the process helpers, moved out of harness/hooks) depend on nothing.
- **harness/marks** holds *Mark*, *OmissionMark*, *Destination*, and *NamedDestination*. Each publisher defines its *Destination* kind with a `channel` (`Skill`, `Command`, `Rules` in harness/installation, `Mcp` in harness/mcp, `Hook` in harness/hooks), and the kind registers here as it is defined, so harness/agent_tools lists a tool's destinations with `Destination.publishes(channel, operation)` and imports no publisher.
- **harness/markdown** depends on harness/name and harness/marks only; a property whose type reads itself with its parent, such as *RulesCollection*, is built through that type's `from_markdown(text, parent=...)`.
- **harness/agent_tools** depends on harness/name, harness/marks, and harness/markdown. A guidance action explains its `guidance` parameter through the toolset's `parameter_notes`, so agent_tools no longer imports harness/guidance_actions.
- **harness/installation** (the marks and data marks, *Installation*, *FileInstallation*, the language adapter, and *RepositoryToolsets*, which finds a repository's toolsets) depends on agent_tools, marks, markdown, and name.
- **harness/hooks** and **harness/mcp** depend on installation and process, never on each other or on the installer; both find toolsets through *RepositoryToolsets*.
- **harness/installer** (*Installer*, moved out of harness/installation) is the top of the publishing chain and the only module that imports hooks and mcp channels together.
- **harness/guidance** depends on the modules above; `load_document` moved into it (`harness/guidance/documents.py`), so it no longer imports harness/guidance_actions, and a fidelity's Clean Engineering companion comes from *PracticeCatalogue*.
- **harness/guidance_actions**, then **harness/diagnostics** (*AgentToolsProbe*, *GuidanceProbe*, and their toolsets, moved out of agent_tools and guidance) and **harness/sub_agent** (the *SubAgent* toolset, moved out of agent_tools), which nothing in the framework imports.

## Left: framework ↔ space
These keep harness in one dependency cycle with space, tools, and cdd_guidance. Each is a call reaching for its session, project, or chat outside the call it runs in.
- **harness/agent_tools ↔ space/session.** `tool_call.py:9` (type only) and `:32` open a call's session (`Sessions(project).saved`). *ToolCall* is the one seam the framework keeps for the session; to close the cycle, space/session should register how a project's session is opened with *ToolCall* (a class-level opener set when space/session is imported) instead of *ToolCall* importing it. The hook server now reads its session through *ToolCall* too (`hook_server.py`, `HookServer.session`), so this is the one place left to change. Owner: space/session.
- **harness/mcp → space/session and space/work_state.** `mcp_server.py:817` runs each call inside `working_on(project)` for space code that still reads its project from there, and `:823` takes the chat a call came from with *ChatPointer*. Both go once every space tool reads its project and chat from its *ToolCall*: `working_on` can then be deleted, and the chat can travel on *ToolCall* as the project does.
- **harness/guidance → space/session and tools/prompt_notify.** `rule.py:154` toasts with *PromptNotify*, and `rule.py` opens a session for the rule injection it logs.
- **harness/guidance_actions → space/session and tools/prompt_notify.** `guidance_actions.py:15` (*PromptNotify*, the `@Toast` mark), `:20`, `:21` (type only), `:126` (the session a `session=` word names). The `@Toast` mark could move to harness/marks as a *Destination* kind and *PromptNotify* subscribe to the hook result, so the action never names the notifier.
- **harness/hooks → space/context_config.** `hook_server.py:302`, `:310` read which guideline applies to an edited file.
- **harness/diagnostics → space/session.** `guidance_probe.py:158` opens a session to call a guidance action in. diagnostics is above every other framework module, so this edge closes no framework cycle on its own.
- **harness/design_canvas, harness/catalog_generator → space/work_state.** `design_canvas/versions.py:19` (*WorkState*, `DESIGN_CANVAS_FOLDER`), `catalog_generator/catalog_generator.py:46` (`project_checkout`), `generate_cdd_catalog.py:27` (`working_on`). These are applications on the framework; each should take its project from its call or its constructor.

## Left: framework → practices
The graph declares a seam, `harness/graph/graph_practice.py`: a practice registers a `GraphPractice` from its own `graph_practice.py`, and a pattern registers a `GraphOverlay` from its own `graph_overlay.py`, so `working_copy.py`, `rules.py`, `node_rules.py`, and `guidance_prose_index.py` name no practice.
- **The rule-example harnesses** in `harness/graph` (`ce_rule_eval_harness.py`, `ddd_rule_eval_harness.py`, `bdd_example_harness.py`, `stories_example_harness.py`, `ce_module_example_harness.py`, `stories_ts_folder_harness.py`, `ce_multi_language_fixtures.py`) import practice rules. They are spec support and belong in each practice's spec folder; their callers in the practices (and `clean_engineering/model/drawio/drawio.py`, `bdd/templates/bdd.py`) move with them.
- **UX** registers nothing yet: its explorer node types `UxMap` and `Screen` need `cdd_guidance/practices/ux/graph_practice.py`.
- **`cdd_guidance/practices/stages`.** `harness/graph/graph.py:21` and `harness/catalog_generator` read the stage names from `STAGES`. `stages.py` itself depends only on `harness.installation.destination`, so this edge joins the cycle only through the others; moving the stage names into harness (or the practices registering them) would remove it.
- **Not a cycle:** practices importing `harness.graph` (`practice_rule`, `bound_node`, `graph`) is the allowed direction.

## Left: practices that import each other
- **cdd_guidance/practices/stories ↔ cdd_guidance/practices/ux.**
  - stories/model/claude_design/nodes.py:21, :368 import ux nodes.
  - Back: ux/scripts/emit_story_javascript.py:15, :16.

## Left: space and tools
- **space/repo ↔ space/work_state.** repo.py:16 and latest_release.py:17; back: work_state.py:14, :15, :28, :93.
- **space/session ↔ tools/file_manager.** session.py:26, practice_session_output.py:18, session_files.py:8; back: file_manager.py:145. space/repo → tools/file_manager (repo.py:19, :155) also points upward.
- **space/session → cdd_guidance actions.** session_probe.py:44, :45 import Generate and Validate.

## The board (space/kanban)
The board is part of tracking the work, so it lives in `space/kanban`, beside the session and repo it reads, and each `@tool_subject` loader takes the call's project. What is left:
- **space/kanban → tools/file_manager:** ticket.py:28 (*FileEntry*, the type `fidelity-progress.files` answers with).
- **space/kanban → cdd_guidance:** board.py:18 and ticket.py:23 (the stage names), report.py:168 (`validate.graph_json_reader`, reading the graph saved beside a report), and `session_board_tiers.py` (Generate and Validate for the story tests).

The import graph is computed with a script that walks every `import` in the production `.py` files of harness, space, tools and cdd_guidance, type-only imports included. Specs, `_examples` and fixtures are excluded.
