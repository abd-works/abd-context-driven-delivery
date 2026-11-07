# Break module dependency cycles

The Clean Engineering modules validation on `ensure-domain-orientation-refactor` (d6c41b23) found that module dependencies do not flow one way (`one-way-deps`, `extensions-live-with-the-domain`). Following every import, function-level ones included, 25 modules form one strongly connected group. While that group exists, no module in it can be changed or tested without the others, and the framework cannot stay generic because it imports the practices.

Break each pair below. To break one, move the shared concept down to a module both sides may depend on, or have the lower module accept the higher one's object through a seam it declares (registration) instead of importing it.

## Framework modules that import each other (harness)
- **harness/agent_tools ↔ harness/installation.**
  - agent_tools.py:17, :330, :910, :937 import `installation.destination` and `installation.files`.
  - Back: files.py:9, installer.py:17, and language_adapter.py:19–20 import `agent_tools`.
- **harness/agent_tools ↔ harness/hooks.**
  - agent_tools.py:324, :379, :922, :931 import `hooks.hooks`.
  - Back: hooks.py:9 and hook_server.py:35.
- **harness/agent_tools ↔ harness/mcp.**
  - agent_tools.py:916, agent_tools_diagnostics.py:7, and agent_tools_probe.py:104, :335 import `mcp.mcp_server`.
  - Back: mcp_server.py:22, :768 and mcp/__main__.py:19.
- **harness/agent_tools ↔ harness/markdown.**
  - agent_tools.py:114, :1103 import `markdown.markdown`.
  - Back: markdown.py:11 imports `agent_tools.name`.
- **harness/agent_tools ↔ harness/guidance.**
  - agent_tools_probe.py:19 imports `guidance.guidance_probe`.
  - Back: guidance.py:10, :12, guidance_diagnostics.py:5, and guidance_probe.py:189.
- **harness/agent_tools ↔ harness/guidance_actions.**
  - agent_tools.py:1082 imports `guidance_actions`.
  - Back: guidance_actions.py:12, :13, :186, :506.
- **harness/guidance ↔ harness/guidance_actions.**
  - guidance.py:481 and guidance_probe.py:178.
  - Back: guidance_actions.py:297, :298.
- **harness/guidance ↔ harness/installation.**
  - guidance.py:21, :22 and guidance_diagnostics.py:6, :25.
  - Back: installation/files.py:289 imports `guidance.rule`.
- **harness/guidance ↔ harness/markdown.**
  - guidance.py:24, :32 and rule.py:17, :50.
  - Back: markdown.py:918 imports `guidance.rule`.
- **harness/hooks ↔ harness/installation.**
  - hooks.py:10 and hook_server.py:36, :360.
  - Back: installer.py:26, :508, :559, :560.
- **harness/installation ↔ harness/markdown.**
  - installer.py:27.
  - Back: markdown.py:12 imports `installation.destination`.
- **harness/installation ↔ harness/mcp.**
  - files.py:240 and installer.py:113, :509, :569.
  - Back: mcp_server.py:23, :401, :926 and mcp/__main__.py:20.

## Framework ↔ space
- **harness/agent_tools ↔ space/session.**
  - agent_tools.py:1047.
  - Back: session.py:15, :16 and session_diagnostics.py:7.
- **harness/guidance ↔ space/session.**
  - guidance_probe.py:158 and rule.py:157.
  - Back: session.py:18, :34, :35.
- **harness/hooks ↔ space/session.**
  - hook_server.py:439.
  - Back: session.py:938 imports `hooks.session_logs`. `SessionLogs` repeats `Repo.current_session`, so moving that behaviour onto Repo removes this edge.
- **harness/mcp ↔ space/session.**
  - mcp_server.py:396, :799, :800 (`ChatPointer`).
  - Back: session.py:20 and session_diagnostics.py:9.
- **harness/guidance_actions and harness/guidance → tools/prompt_notify.**
  - guidance_actions.py:14 and rule.py:138 import `prompt_notify` (on the `tools` path).
  - prompt_notify.py:26–29, :337, :338 import `harness.agent_tools`, `harness.installation`, and `harness.hooks` back, so the cycle closes through those modules.
- **Other harness → space imports:**
  - guidance_actions.py:158 (`space.session`) and :388 (`space.work_state`).
  - mcp_server.py:769, :801 (`work_state`).
  - hook_server.py:270, :278 (`context_config`).
  - design_canvas/versions.py:19 and health/server_health.py:42 (`work_state`).

## Framework → practices (the framework depends on every practice)
Broken on `ensure-domain-orientation-refactor` (wave 3). The graph declares a seam, `harness/graph/graph_practice.py`: a practice registers a `GraphPractice` (its reader, its cross-practice links, its rules) from its own `graph_practice.py`, and a pattern registers a `GraphOverlay` (its nodes, its guidance) from its own `graph_overlay.py`. `GraphPractices` imports those modules by the practice's package from `PracticeCatalogue` or the pattern's folder name, so `working_copy.py`, `rules.py`, `node_rules.py`, and `guidance_prose_index.py` name no practice. `practice_rules_registry.py` is deleted; rules are found through each practice's `GraphPractice`.
- **Done:** working_copy.py's Stories, DDD, BDD, Clean Engineering, LERN, and CDD web domain access imports moved into `cdd_guidance/practices/{stories,ddd,bdd,clean_engineering}/graph_practice.py` and `cdd_guidance/patterns/{lern_domain_driven,cdd_web_domain_access,cdd_claude_mod}/graph_overlay.py`.
- **Left:** UX registers nothing yet (its explorer node types `UxMap` and `Screen` need `cdd_guidance/practices/ux/graph_practice.py`). The rule-example harnesses in `harness/graph` (`ce_rule_eval_harness.py`, `ddd_rule_eval_harness.py`, `bdd_example_harness.py`, `stories_example_harness.py`, `ce_module_example_harness.py`, `stories_ts_folder_harness.py`, `ce_multi_language_fixtures.py`) and the specs that use them still import practice rules; they are spec support, but they belong in each practice's spec folder, and their callers in the practices (and `clean_engineering/model/drawio/drawio.py`, `bdd/templates/bdd.py`) move with them.
- **Not a cycle:** practices importing `harness.graph` (`practice_rule`, `bound_node`, `graph`) is the allowed direction.

## Practices that import each other
- **cdd_guidance/practices/clean_engineering ↔ cdd_guidance/practices/ddd.**
  - base_class_model.py:618 imports `ddd.model.stereotypes`.
  - Back: ddd.py:73, :82, clean_engineering_bridge.py:13, and ddd_channel.feature.py:15.
- **cdd_guidance/practices/stories ↔ cdd_guidance/practices/ux.**
  - stories/model/claude_design/nodes.py:21, :368 import ux nodes.
  - Back: ux.py:53 and scripts/emit_story_javascript.py:14, :15.

## space and tools
- **space/repo ↔ space/session.**
  - repo.py:27, :1105, :1113, :1122.
  - Back: session.py:22.
- **space/repo ↔ space/work_state.**
  - repo.py:21 and latest_release.py:17.
  - Back: work_state.py:14, :29, :100.
- **space/session ↔ tools/file_manager.**
  - session.py:21.
  - Back: file_manager.py:145. space/repo → tools/file_manager (repo.py:28, :1168) also points upward.
- **space/session → cdd_guidance actions.**
  - session_probe.py:45, :46 import Generate and Validate.

## The board (space/kanban)
Decided: the board is part of tracking the work, so it moved from `harness/kanban` to `space/kanban`, beside the session and repo it reads. Its imports of space are now within space, and it no longer reads `space.work_state`: each `@tool_subject` loader takes the call's project, which `harness/agent_tools` hands it (`agent_tools.py:835`, a function-level import of `space.work_state.project_folder`, the same upward edge `agent_tools.py:1101` already makes to `space.session`). What is left:
- **space/kanban → harness, as all of space does.** board.py:11–17, ticket.py:8–12, backlog_item.py:8–10 and :13, report.py:10 import `harness.agent_tools`, `harness.guidance`, `harness.installation`, and `harness.mcp`; report.py:231–232 import `harness.graph`. These close once the shared marks move below agent_tools, installation, hooks, and mcp (above) and the graph's rules are reached through a seam space may depend on.
- **space/kanban → tools/file_manager:** ticket.py:30 (*FileEntry*, the type `fidelity-progress.files` answers with).
- **space/kanban → cdd_guidance/practices/stages:** board.py:18 (the stage names).
- **space/kanban → validate.graph_json_reader:** report.py:220 (reading the graph saved beside a report).

The import graph was computed with a script that walks every `import` in the production `.py` files of harness, space, tools and cdd_guidance. Specs, `_examples` and fixtures are excluded.
