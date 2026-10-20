# actions
*Actions* are the slash kits. You pass *Guidance* (or a string) and they run once per item — generate, document, scan, grill — so a practice keeps its words and does not reimplement the prelude.

- **Purpose:** Give every practice the same slash kits so the practice owns words, not session plumbing.
- **Seam (terms):** GuidanceAction, GuidanceArg
- **Dependencies (one-way):** `harness/guidance_actions`

## Constraint

Slash names match the operation (`/grill`, not `/grill-context`). Echo and handoff live under `tools/`.

---

## actions/scan
*Scan* runs a Guidance’s scanners over paths so a rule fires on disk, not only in chat. *Scanner* and *ScannerCollection* are the checks that Guidance names.

- **Purpose:** Run a Guidance’s scanners over paths so rules fire on disk.
- **Seam (terms):** Scan, Scanner, ScannerCollection
- **Dependencies (one-way):** `harness/guidance_actions`

---

## actions/document
*Document* records what already exists for the Guidance you list. It writes the finding and leaves the artifact as it is.

- **Purpose:** Record what already exists for listed Guidance without correcting it.
- **Seam (terms):** Document
- **Dependencies (one-way):** `harness/guidance_actions`, `actions/scan`

---

## actions/generate
*Generate* writes each listed Guidance’s artifact at the fidelity that Guidance is on now.

- **Purpose:** Write each listed Guidance’s artifact at its current fidelity.
- **Seam (terms):** Generate
- **Dependencies (one-way):** `harness/guidance_actions`

---

## actions/validate
*Validate* checks an artifact against the rules for that Guidance, or adds a named *Rule* from a failed example. *RulesCollection* and *AppliesTo* say which rules run and where.

- **Purpose:** Check artifacts against rules, or add a named rule from a failed example.
- **Seam (terms):** Validate, Rule, RulesCollection, AppliesTo
- **Dependencies (one-way):** `harness/guidance_actions`, `actions/scan`

---

## actions/satisfy
*Satisfy* validates, applies the implied fixes, and validates again on the same Guidance.

- **Purpose:** Validate, apply the implied fixes, validate again.
- **Seam (terms):** Satisfy
- **Dependencies (one-way):** `actions/validate`, `harness/guidance_actions`

---

## actions/render
*Render* turns content that is already generated into another format on that Guidance.

- **Purpose:** Turn already-generated content into another format on that Guidance.
- **Seam (terms):** Render
- **Dependencies (one-way):** `harness/guidance_actions`

---

## actions/partition
*Partition* splits a corpus into a *PartitionIndex* plus verbatim *Segment* chunks, and fails a chunk that drops a named *SegmentEntry*.

- **Purpose:** Split source into an index plus verbatim segments, and fail a chunk that drops a named entry.
- **Seam (terms):** Partition, PartitionIndex, Segment, SegmentEntry
- **Dependencies (one-way):** `harness/guidance_actions`

---

## actions/grill_context
*GrillContext* interviews the plan against files you have actually read, and writes each answer down so the next turn can cite it.

- **Purpose:** Interview the plan against files you have actually read, and persist each answer.
- **Seam (terms):** GrillContext
- **Dependencies (one-way):** `harness/agent_tools`

## Constraint

Do not offer options until the cited context files are read. Answers go to `{path}/.context/grill-answers.md`.

---

## actions/sketch
*Sketch* keeps a rough draft as a file through the grill, so the working record is on disk before anyone generates. *SketchOutline* reads one practice’s section of that sketch and hands back its tree as indented lines; *SketchLens* names which practice section you asked for.

- **Purpose:** Persist a rough draft through grill before generate; read one practice’s sketch section as indented lines for transforms and practice models.
- **Seam (terms):** Sketch, SketchOutline, SketchLens
- **Dependencies (one-way):** `actions/grill_context`

---

## actions/sketch_render
*SketchRender* takes an approved sketch and renders it with the calls *build_render_calls* already named.

- **Purpose:** On approval, render the sketch with explicit render calls.
- **Seam (terms):** SketchRender, build_render_calls
- **Dependencies (one-way):** `actions/sketch`, `actions/render`, `actions/grill_context`

---

## actions/iterate
*Iterate* grills, then generates one small validated slice, then stops. The next tick starts from that slice.

- **Purpose:** Grill, then generate one small validated slice per tick.
- **Seam (terms):** Iterate
- **Dependencies (one-way):** `actions/grill_context`, `actions/generate`, `actions/validate`

---

## actions/improvement
*Improvement* opens a repair on a Guidance and checks the same scanner theme again after the fix. `/repair` and `verify_fix` are the two calls.

- **Purpose:** Open a repair on a Guidance and re-check the same scanner theme after the fix.
- **Seam (terms):** Improvement, repair, verify_fix
- **Dependencies (one-way):** `harness/guidance_actions`, `actions/scan`

---

# builders
*Builders* scaffold a new `@agent_toolset` or *PracticeGuidance* package from templates and a worked example, so you do not copy a peer folder by hand.

- **Purpose:** Generate a new `@agent_toolset` or *PracticeGuidance* package from templates and a worked example.
- **Seam (terms):** CreateAgentToolset, CreatePracticeGuidance
- **Dependencies (one-way):** `harness/guidance`

## Constraint

Scaffolding stays in this tree. Do not invent new practices inside `harness/`.

---

## builders/create_agent_toolset
*CreateAgentToolset* scaffolds a decorated *AgentToolSet* — `@agent_tool` operations and `@agent_instructions` recipes — matching `harness/agent_tools`.

- **Purpose:** Scaffold a decorated *AgentToolSet* — `@agent_tool` operations and `@agent_instructions` recipes — matching `harness/agent_tools`.
- **Seam (terms):** CreateAgentToolset
- **Dependencies (one-way):** `harness/agent_tools`

---

## builders/create_practice_guidance
*CreatePracticeGuidance* scaffolds a new practice package under `practices/` from templates.

- **Purpose:** Scaffold a new practice package under `practices/` from templates.
- **Seam (terms):** CreatePracticeGuidance
- **Dependencies (one-way):** `harness/guidance`

---

# harness
*Harness* is the in-process home for agent-callable classes, co-located markdown, guidance, and the explorer *Graph*. Callers import a child package; this folder does not add a second seam. *Session* holds that graph for one process.

- **Purpose:** Give practices and kits one in-process home for agent-callable classes, co-located markdown, guidance, and the explorer graph.
- **Seam (terms):** AgentToolSet, Markdown, Guidance, GuidanceAction, Graph, Session
- **Dependencies (one-way):** *(children declare their own)*

## Constraint

Callers import child packages (`harness.markdown`, `harness.agent_tools`, `harness.graph`, …). This folder does not add a second seam.

---

## harness/markdown
*Markdown* keeps a practice’s words next to its class. `@markdown` loads one match and `@markdownCollection` loads several, as a file named after the property or a section titled after the property.

- **Purpose:** Keep a practice’s words next to its class and read them as HTML or a collection.
- **Seam (terms):** Markdown, MarkdownCollection, HTML, `@markdown`, `@markdownCollection`
- **Dependencies (one-way):** *(none)*

## Constraint

Property name is the match. **File:** `{name}.md` beside the class. **Section:** `## Name` in `{slug}.md`.

---

## harness/agent_tools
*AgentToolSet* publishes an ordinary class so an agent can list its operations, run some as Python, and follow others as instructions. Stamp `@agent_toolset` on the class, `@agent_tool` or `@agent_instructions` on each member, and name deferred work with `tools(...)` and nested recipes with `instructions(...)`.

- **Purpose:** Publish an ordinary class as operations an agent can list, run as Python, or follow as instructions.
- **Seam (terms):** AgentToolSet, AgentTool, AgentOperation, AgentInstructions, `@agent_toolset`, `@agent_tool`, `@agent_instructions`, `tools(...)`, `instructions(...)`
- **Dependencies (one-way):** `harness/markdown`

---

## harness/guidance
*Guidance* is one class plus the co-located markdown the agent follows. *PracticeGuidance* adds fidelities and format render. *FidelityGuidance* is one named stage of that practice.

- **Purpose:** Let a practice be one class plus co-located markdown, including fidelities and format render.
- **Seam (terms):** Guidance, GuidanceCollection, PracticeGuidance, FidelityGuidance
- **Dependencies (one-way):** `harness/agent_tools`, `harness/markdown`

---

## harness/guidance_actions
*GuidanceAction* is the shared prelude: bind a *GuidanceArg* — a list, one Guidance, or a string — and run the operation.

- **Purpose:** Share one prelude across generate, document, scan, and the other kits: bind the guidance list and run the operation.
- **Seam (terms):** GuidanceAction, GuidanceArg
- **Dependencies (one-way):** `harness/agent_tools`, `harness/hooks`, `harness/mcp`

---

## harness/graph
*Graph* holds the practice graphs — nodes, edges, and rules — and serves the explorer.

- **Purpose:** Hold practice graphs — nodes, edges, and rules — and serve the explorer.
- **Seam (terms):** Graph
- **Dependencies (one-way):** `harness/agent_tools`, `practices/clean_engineering`, `practices/stories`, `practices/ddd`, `practices/bdd`, `practices/ux`

---

## space/session
*Session* holds the host session for hooks and MCP: the in-memory graph and the active practice guidance. Name, work path, repo path, and session path belong on this session.

- **Purpose:** Keep one host session for hooks and MCP.
- **Seam (terms):** Session
- **Dependencies (one-way):** `harness/graph`, `harness/guidance`, `harness/hooks`, `space/repo`

---

## space/repo
*Repo* models a local clone and GitHub workflow; *Repo* agent toolset exposes branch switch/create/close (optional worktrees).

- **Purpose:** Domain types (*Repo*, *Branch*, *Commit*, …) plus slash/MCP ``branch`` / ``worktree`` / ``push`` on ``space.repo.repo:Repo`` (agent composes commit messages from diffs and CDD tool usage).
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState, RepoConnectError
- **Dependencies (one-way):** `harness/agent_tools`, `harness/mcp`, `harness/installation`

---

## harness/transformers
*Transformers* loads each practice *Transformer* a sketch names and renders that practice’s logical templates.

- **Purpose:** Load each practice transformer named by a sketch and render that practice’s logical templates.
- **Seam (terms):** Transformers, Transformer
- **Dependencies (one-way):** `actions/sketch`, `harness/agent_tools`, `practices/bdd`, `practices/clean_engineering`, `practices/ddd`, `practices/stories`

---

## harness/mcp
*Mcp* marks a member `@mcp` and runs a stdio host so Cursor can call it. *McpInstallation* writes the config; *McpServer* and *McpHost* run the process.

- **Purpose:** Mark a member `@mcp` and run a stdio host so Cursor can call it.
- **Seam (terms):** Mcp, McpInstallation, McpServer, McpHost
- **Dependencies (one-way):** `installation`, `harness/agent_tools`

## Constraint

Cursor starts `python -m harness.mcp`. `cdd.ping` is always listed. Only members marked `@mcp` enroll.

---

## harness/hooks
*Hook* marks a member `@Hook("event")` so a Cursor stdin event runs that Python. *Hooks* can disable every hook on a toolset. *HookInstallation* and *HookServer* publish and serve them.

- **Purpose:** Mark a member `@Hook("event")` so Cursor stdin events run that Python and return one merged result.
- **Seam (terms):** Hook, Hooks, HookInstallation, HookServer
- **Dependencies (one-way):** `installation`, `harness/agent_tools`

## Constraint

The event name is the Cursor event (`sessionStart`, `preToolUse`, …). `@Hooks(disabled=True)` on a toolset skips every hook on it.

---

# harness/installation
*Installation* publishes a toolset’s marked members into Cursor, VS Code, or Kilo. *Installer* walks the marks. *Destination* is the channel — `@skill`, `@command`, `@rules`, `@mcp`, `@Hook`. *FileInstallation* writes the skill, command, and rules files.

- **Purpose:** Publish a toolset’s marked members into Cursor (or VS Code / Kilo) as skills, MCP, hooks, commands, or rules.
- **Seam (terms):** Installer, Destination, Installation, FileInstallation, Skill, Command, Rules
- **Dependencies (one-way):** `harness/agent_tools`, `harness/mcp`, `harness/hooks`

## Constraint

Marks live on members; *Installer* walks them, including `harness/`. If `.install-state.json` points at a missing directory, install to `{repo}/.cursor`. Import this package as `harness.installation`. Leave `harness/` off `PYTHONPATH` so `import mcp` stays the MCP SDK.

---

# practices
*Practices* are fields of expertise — Clean Engineering, BDD, Stories, UX, DDD, agent BDD, CDD, Kanban — each a *PracticeGuidance* plus co-located markdown. *Stage* names the deepen step: discovery, specification, or implementation. Generate and validate stay on *Actions*.

- **Purpose:** Hold one *PracticeGuidance* per field so the same kits generate and check work against that field’s words.
- **Seam (terms):** PracticeGuidance, Stage
- **Dependencies (one-way):** `harness/guidance`

## Constraint

Do not put `/generate` on the practice. Pass the practice into the kit.

---

## practices/cdd
*Cdd* is the stage menu across Stories, DDD, UX, Clean Engineering, and BDD.

- **Purpose:** Offer the stage menu across Stories, DDD, UX, Clean Engineering, and BDD.
- **Seam (terms):** Cdd
- **Dependencies (one-way):** `harness/guidance`, `practices/stories`, `practices/ddd`, `practices/ux`, `practices/clean_engineering`, `practices/bdd`

---

## practices/clean_engineering
*CleanEngineering* partitions, types, and implements objects — modules, then model, then code — in the caller’s language.

- **Purpose:** Partition, type, and implement objects — modules, then model, then code — in the caller’s language.
- **Seam (terms):** CleanEngineering
- **Dependencies (one-way):** `harness/guidance`

---

### practices/clean_engineering/model
*CleanEngineeringModel* is the one OOAD model. *Module* and *OoadClass* are what the channels parse and render across markdown, JSON, languages, and draw.io.

- **Purpose:** Keep one OOAD model and parse or render it across markdown, JSON, languages, and draw.io.
- **Seam (terms):** CleanEngineeringModel, Module, OoadClass
- **Dependencies (one-way):** `practices/clean_engineering`
- **Packages:** `diagram`, `java`, `javascript`, `json`, `markdown`, `miro`, `python`, `sketch`, `transformation`, `typescript`

---

#### practices/clean_engineering/model/drawio
*Drawio* creates, scans, and repairs Clean Engineering draw.io diagrams. *DrawIOCleanEngineeringModel* is the draw.io channel for that same model.

- **Purpose:** Create, scan, and repair Clean Engineering draw.io diagrams, and host the draw.io channel.
- **Seam (terms):** Drawio, DrawIOCleanEngineeringModel
- **Dependencies (one-way):** `practices/clean_engineering/model`, `harness/agent_tools`

---

## practices/bdd
*Bdd* locks describe/it observations first, fills the tests red then green, and hands class code to Clean Engineering.

- **Purpose:** Lock describe/it observations first, then fill tests red-green, then hand class code to Clean Engineering.
- **Seam (terms):** Bdd
- **Dependencies (one-way):** `harness/guidance`, `practices/clean_engineering`
- **Packages:** `practices/bdd/model`, `practices/bdd/model/sketch`, `practices/bdd/model/transformation`

---

## practices/stories
*Stories* maps stakeholder behaviour as Epic then Story, so later fidelities share one hierarchy.

- **Purpose:** Map stakeholder behaviour as Epic → Story so later fidelities share one hierarchy.
- **Seam (terms):** Stories
- **Dependencies (one-way):** `harness/guidance`, `practices/clean_engineering`
- **Packages:** `practices/stories/model` (`drawio`, `java`, `javascript`, `json`, `markdown`, `miro`, `python`, `sketch`, `typescript`)

---

## practices/ux
*Ux* decides the screens, then the greybox, then the production UI, in the domain’s own words.

- **Purpose:** Decide screens, then greybox, then production UI, in domain words.
- **Seam (terms):** Ux
- **Dependencies (one-way):** `harness/guidance`, `practices/stories`, `practices/clean_engineering`

---

### practices/ux/model
*UxMap* is the one information architecture — *Screen*, *Region*, and *Control* — so a diagram, JSON, and HTML stay the same hierarchy.

- **Purpose:** Keep information architecture as one UX map so diagram, JSON, and HTML stay the same hierarchy.
- **Seam (terms):** UxMap, Screen, Region, Control
- **Dependencies (one-way):** *(none)*

---

#### practices/ux/model/drawio
*DrawioUxMap* reads and writes the default IA diagram as a *UxMap*.

- **Purpose:** Read and write the default IA diagram as a *UxMap*.
- **Seam (terms):** DrawioUxMap
- **Dependencies (one-way):** `practices/ux/model`

---

#### practices/ux/model/html
*HtmlUxMap* renders the mockup review shell and round-trips the *UxMap* embedded in it.

- **Purpose:** Render the mockup review shell and round-trip the embedded *UxMap*.
- **Seam (terms):** HtmlUxMap
- **Dependencies (one-way):** `practices/ux/model`, `practices/ux/model/json`

---

#### practices/ux/model/json
*JsonUxMap* round-trips *UxMap* fields as JSON for transform and scanners.

- **Purpose:** Round-trip *UxMap* fields as JSON for transform and scanners.
- **Seam (terms):** JsonUxMap
- **Dependencies (one-way):** `practices/ux/model`

---

#### practices/ux/model/markdown
*MarkdownUxMap* keeps optional UX notes and invariants beside the map.

- **Purpose:** Keep optional UX notes and invariants beside the map.
- **Seam (terms):** MarkdownUxMap
- **Dependencies (one-way):** `practices/ux/model`

---

### practices/ux/scripts
The UX scripts emit the story JavaScript the UX examples play.

- **Purpose:** Emit story JavaScript for UX examples.
- **Seam (terms):** emit_story_javascript
- **Dependencies (one-way):** `practices/stories`

---

### practices/ux/story-demo
*StoryDemoPage* plays a story in the UX shell — frames and controls. *StoryDemoControl* is the control that carries the story steps.

- **Purpose:** Play a story in the UX shell — frames, controls, and the dual runner.
- **Seam (terms):** StoryDemoPage, StoryDemoControl
- **Dependencies (one-way):** `practices/ux/model`

---

#### practices/ux/story-demo/play-dual-runner
*PlayDualRunner* collects and plays those story steps in the browser and under node.

- **Purpose:** Collect and play story steps in the browser and under node.
- **Seam (terms):** PlayDualRunner
- **Dependencies (one-way):** `practices/ux/story-demo`

---

## practices/ddd
*Ddd* draws where the language changes — bounded context, then building blocks, then tactics — and reuses Clean Engineering for the object ladder.

- **Purpose:** Draw where language changes — bounded context, then building blocks, then tactics — and reuse Clean Engineering for the OO ladder.
- **Seam (terms):** Ddd
- **Dependencies (one-way):** `harness/guidance`, `practices/clean_engineering`
- **Packages:** `practices/ddd/model` (`drawio`, `markdown`, `sketch`, `transformation`)

## Constraint

Do not restate Clean Engineering class analysis in DDD artifacts. Use the fidelity’s Clean Engineering companion.

---

## practices/agent_bdd
*AgentBdd* drives a real agent through `agent(...)` and asserts on the parsed run. `instruct`, `instruct_use_tool`, and `ai_judge` are the calls inside that block.

- **Purpose:** Drive a real agent through `agent(...)` and assert on the parsed run.
- **Seam (terms):** AgentBdd, agent, instruct, instruct_use_tool, ai_judge
- **Dependencies (one-way):** `practices/bdd`

## Constraint

Specs call the harness only inside `with agent(...)`.

---

## practices/kanban
*Kanban Lead* carves an ask into backlog items and passes each item to the practice agent that owns it.

- **Purpose:** Carve an ask into backlog items and pass each item to the practice agent that owns it.
- **Seam (terms):** Kanban Lead
- **Dependencies (one-way):** `practices/stories`, `practices/ux`, `practices/ddd`, `practices/clean_engineering`, `practices/bdd`

## Constraint

One agent role per session. Follow the prompt for how to carve the backlog.

---

# tools
*Tools* are the session, git, and workflow utilities the kits call.

## Constraint

Slash commands for the board live on `tools/workflow`. Do not deploy `/git`. Import repository types from ``space.repo`` only.

---

## tools/workflow
*Workflow* moves GitHub issues on Project columns and names the reusable workflows a plan is based on.

- **Purpose:** Move GitHub issues on Project columns and name the reusable workflows a plan is based on.
- **Seam (terms):** Workflow
- **Dependencies (one-way):** `space/repo`, `space/handoff`

---

## tools/plan
*Plan* runs a reusable or named workflow, including themed small-work issues, one ticket at a time. *PlanCommands*, *PlanExecution*, and *SmallWorkRunner* are how a caller starts and advances that run.

- **Purpose:** Run a reusable or named workflow, including themed small-work issues, one ticket at a time.
- **Seam (terms):** Plan, PlanCommands, PlanExecution, SmallWorkRunner
- **Dependencies (one-way):** `space/repo`, `tools/workflow`

---

## space/handoff
*Handoff* writes a resume document a fresh agent can continue from, under the current session folder ``handoffs/``.

- **Purpose:** Compact the current agent session into a handoff document a fresh agent can resume from.
- **Seam (terms):** Handoff
- **Dependencies (one-way):** `harness/agent_tools`

---

## tools/echo_instructions
*EchoInstructions* shows action instructions inside a labelled fence so you can read them and the agent does not follow them.

- **Purpose:** Show action instructions inside a labelled fence so the user can read them without the agent following them.
- **Seam (terms):** EchoInstructions
- **Dependencies (one-way):** `harness/agent_tools`

---

## tools/prompt_notify
*PromptNotify* toasts the invoked action, practice, fidelity, or guideline on `preToolUse`. Callers mark the member with `@echo`.

- **Purpose:** Toast the invoked action, practice, fidelity, or guideline on `preToolUse`.
- **Seam (terms):** Echo, PromptNotify
- **Dependencies (one-way):** `installation`, `harness/hooks`, `harness/agent_tools`

## Constraint

Callers mark members with `@echo`.

---

## tools/prompt_log
*PromptLog* appends a read-only audit of what Cursor sent the model on hook events.

- **Purpose:** Append a read-only audit of what Cursor sent the model on hook events.
- **Seam (terms):** PromptLog
- **Dependencies (one-way):** `harness/hooks`, `harness/agent_tools`

## Constraint

`@Hooks(disabled=True)` on *PromptLog* skips every audit handler.

---

## actions/diagnose
*Diagnose* runs a phase-sequenced bug hunt as a sub-agent when a host stays red. Pass practice guidance when the fix and the regression test should follow that practice.

- **Purpose:** Run a phase-sequenced bug-hunting loop as a sub-agent when a host stays red.
- **Seam (terms):** Diagnose
- **Dependencies (one-way):** `harness/guidance_actions`

---

## space/record_decisions
*RecordDecisions* writes a Context Decision Record when a choice is hard to reverse, surprising without context, and a real trade-off. Records go under the current session workpath ``.context/cdr/``.

- **Purpose:** Write a Context Decision Record when a choice is hard to reverse, surprising without context, and a real trade-off.
- **Seam (terms):** RecordDecisions
- **Dependencies (one-way):** `harness/agent_tools`

## Constraint

`/record-decisions-session` is the slash command. Do not deploy a `record_decisions` skill.

---

## cdd_guidance/context_setup
*ContextSetup* converts a folder of documents to markdown, partitions it through the practices you select, and embeds a *ContextIndex* you can ask.

- **Purpose:** Convert a folder of documents to markdown, partition through selected practices, and embed an index you can ask.
- **Seam (terms):** ContextSetup, ContextIndex
- **Dependencies (one-way):** `actions/partition`, `practices/clean_engineering`, `practices/ddd`, `practices/stories`, `practices/ux`

---

## harness/catalog_generator
*Catalog* discovers the registered toolsets and renders the self-contained CDD catalog pages. `@noCatalog` leaves a class, fidelity, or operation out of those pages.

- **Purpose:** Discover registered toolsets and render the self-contained CDD catalog pages.
- **Seam (terms):** Catalog, noCatalog
- **Dependencies (one-way):** `harness/agent_tools`, `harness/guidance`
