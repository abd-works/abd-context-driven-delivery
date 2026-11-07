# harness
*Harness* is the framework every other part of CDD is built on: it writes one name in every case (harness/name), starts and stops long-running processes (harness/process), holds the marks an author types and the channels they publish to (harness/marks), keeps a class's words in markdown beside it (harness/markdown), turns an ordinary class into operations an agent can use (harness/agent_tools), gives each channel its writer and finds a repository's toolsets (harness/installation), publishes to every chat through the one `cdd` MCP server (harness/mcp) and the hook server (harness/hooks), installs all of it into each IDE (harness/installer), makes a practice one class plus its markdown (harness/guidance), gives every guidance action the same start (harness/guidance_actions), and reads a working copy into graphs that rules check (harness/graph). The modules are listed lowest first: each depends only on modules before it. Above them, harness/diagnostics probes an install and harness/sub_agent publishes the sub-agent hand-off.
On top of the framework sit its applications: the chat's board plugin and server health band (harness/chat-ui/pane, harness/health), the generated catalog (harness/catalog_generator), and Claude Design canvases (harness/design_canvas). Each of these folders owns its own card in `{folder}/.context/module-context.md`.

- **Purpose:** Give practices, actions, and tools one framework for publishing classes to agents and IDEs, and the applications that show the work.
- **Seam (terms):** the marks `@agent_toolset`, `@agent_tool`, `@agent_instructions`, `@markdown`, `@mcp`, `@skill`, `@command`, `@rules`, `@Hook`; *PracticeGuidance*; *GuidanceAction*; *Graph*; `python scripts/install.py --ide {IDE}`
- **Dependencies (one-way):** inside harness the modules depend one way, lowest first as listed above. Nothing in harness imports space, tools, or cdd_guidance: where the framework needs what they keep, it declares a seam and they register with it — space/session registers how a *ToolCall* opens its session, tools/prompt_notify registers the notifier that shows a hook's toast, each practice registers its *GraphPractice*, and *PracticeCatalogue* and *ActionCatalogue* name the practices and actions by reference. The stage names every fidelity is in are framework vocabulary (`harness/guidance/stages.py`).

## Constraint

Import a child package (`harness.agent_tools`, `harness.guidance`, ...); this folder adds no seam of its own. Keep practice-specific parsing and rules in the practice that owns them, not in the framework, so the framework does not have to change for every practice. Leave `harness/` off `PYTHONPATH`, so `import mcp` loads the MCP SDK.

---

# tools
*Tools* are standalone toolsets an agent or an application calls beside the practices: *Chat* (`tools/chat`) sends a prompt or a command to a live Claude Code chat; *FileManager* (`tools/file_manager`) lists and reads the files under a session's roots; *Echo* (`tools/echo`) shows an action's instructions inside a do-not-follow fence; *Granola* (`tools/granola`) files meeting notes and brings them into a folder's `.context`; *PromptLog* (`tools/prompt_log`) and *PromptNotify* (`tools/prompt_notify`) are hooks that log what the IDE sends the model and show which action, practice, or fidelity was used. Each child folder that has a card keeps it in `{folder}/.context/module-context.md`.

- **Purpose:** Hold the toolsets that are useful on their own, outside any one practice or action.
- **Seam (terms):** Chat, FileManager, Echo, Granola, PromptLog, PromptNotify; the MCP operations `chat.*`, `file-manager.*`, `echo.*`, `granola.*`
- **Dependencies (one-way):** harness (agent_tools, installation, mcp, hooks, marks), space/session (*PromptLog* writes in the open session's log folder). space/session, space/repo, and space/kanban import tools/file_manager, which imports nothing of space: it opens its session through *ToolCall*.

## Constraint

Import repository and session types from `space`, never from a tool, so a tool stays something other modules may use rather than something they depend on for state.

---

# cdd_guidance
*CDD guidance* is what an agent follows: the practices (`cdd_guidance/practices` — Stories, DDD, UX, Clean Engineering, BDD, and agent BDD), each a *PracticeGuidance* with its fidelities, rules, templates, and examples; the actions that run on them (`cdd_guidance/actions` — generate, validate, document, sketch, grill, partition, render, satisfy, iterate, repair, diagnose), each a *GuidanceAction*; the stack patterns that add rules for one kind of solution (`cdd_guidance/patterns` — LERN, MERN, CDD web domain access, Claude Code mods); the builders that start a new toolset or practice (`cdd_guidance/builders`); and context setup, which turns documents or a live app into indexed context (`cdd_guidance/context_setup`). `cdd_guidance/rules` and `cdd_guidance/references` are installed into every IDE, and `cdd_guidance/agents` are the role prompts. `cdd_guidance/practices`, `cdd_guidance/actions`, `cdd_guidance/builders`, and `cdd_guidance/context_setup` keep their own cards in `{folder}/.context/module-context.md`; `cdd_guidance/patterns`, `rules`, `references`, `agents`, and `catalog` have no card of their own and are covered by this one.

- **Purpose:** Hold the practices, actions, and patterns an agent follows to deliver work, as classes plus markdown the installer publishes.
- **Seam (terms):** each practice's and fidelity's instructions, published under its slug (`stories`, `clean-engineering-model`); each action's MCP operations (`generate.generate`, `validate.validate`, ...); each pattern's instructions
- **Dependencies (one-way):** harness (agent_tools, graph, guidance, guidance_actions, installation, markdown, mcp, design_canvas). Nothing in harness imports the practices, patterns, or actions; each practice keeps the spec support that runs its rules on examples in its own `rules/` folder. space imports some of them (the session diagnostics probe runs generate and validate, and the board reads the saved graph through validate's reader), and nothing here imports space back.

## Constraint

Run an action on a practice by passing the practice to the action (`generate` with `guidance: stories`), never by putting the action on the practice, so every practice gets every action the same way. Keep a practice's words in its `{practice}.md` and its format adapters under `{practice}/model/{format}/`.
