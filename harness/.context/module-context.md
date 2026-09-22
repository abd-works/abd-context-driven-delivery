## Language

*Harness* is the in-process package that turns a plain Python class into an agent-callable *AgentToolSet*, extracts co-located *Markdown*, and binds that extract into *Guidance* and *GuidanceAction*.

### AgentToolSet

- You want an agent to treat your class as a toolkit: list its operations, run some as Python, follow others as recipes, and have install publish the same members as skills, MCP, hooks, or commands — without you writing those files by hand or subclassing a framework base.
- Put `@agent_toolset` on that class so *AgentToolSet* is mixed in and the members become that toolkit.
- Class docstring is the toolset **description** the agent reads; **name** is the slugified class name so install and MCP have one id.
- **Invariant:** Each callable member has exactly one mark — `@agent_tool` or `@agent_instructions`.

### AgentTool

- One named callable on a parent *AgentToolSet* so the agent (and install) can see what it is for without reading the body.
- Put `@mcp`, `@skill`, `@hook`, `@command`, or `@rules` on that member when you want install to publish it to that destination. Without those marks it is only an in-process tool.

### AgentOperation

- Put `@agent_tool` on a method when you want the agent to execute that Python now (add a car, scan a path). Without the mark it is an ordinary method and never appears in **tools**.

### AgentInstructions

- Put `@agent_instructions` on a method when you want the agent to follow a written recipe — the method *is* the **instructions** (prompt plus the tools the agent may use while following it), not a Python call. That is how generate, document, and scan teach the agent what to do.
- Inside the body, `tools(...)` names tools the agent may use; `instructions(...)` nests another recipe. Nested `instructions(...)` cycles are rejected.

### Markdown

-  `@markdown` on a property loads prose from a matching markdown document so you do not copy it into the code: **file** — `{property_name}.md` beside the class; **section** — `## Property Name` in the class’s `{slug}.md`. The property name is the match (file stem or heading title).
- `@markdownCollection` is the same match when there are several (a folder of files, or several bullets under that heading).

### Guidance

- A *AgentToolSet* whose words — **overview**, **guidance**, **rules**, **templates**, **instructions** — come from *Markdown* extracts, so a practice is one class plus co-located markdown the agent can follow.
- *PracticeGuidance* adds **fidelities**, **format**, and **render** so one practice can deepen (modules → model → code) and emit another channel.
- *FidelityGuidance* is one named stage of that practice.

### GuidanceAction

- Run a kit (**generate**, **document**, **scan**, …) once on a string or once per listed *Guidance*, so the same prelude opens the workspace and binds the list.

### ToolSetCollection

- Named child *AgentToolSet* instances, iterated in entry order, so one parent can publish nested toolsets without flattening them.

Build order: `harness/markdown` → `harness/agent_tools` → `harness/guidance` → `harness/guidance_actions` → `harness/mcp` → `harness/hooks`

---

# harness
- **Purpose:** Give practices and kits one in-process home for agent-callable classes, co-located markdown, and guidance actions.
- **Seam (terms):** AgentToolSet, Markdown, Guidance, GuidanceAction
- **Dependencies (one-way):** *(none — children declare their own)*

## Constraint

Callers import child packages (`harness.markdown`, `harness.agent_tools`, …). This folder does not add a second seam.

---

# harness/markdown
- **Purpose:** Let a practice keep its words next to its class and read them as HTML or a collection without assembling agent recipes here.
- **Seam (terms):** Markdown, MarkdownCollection, HTML, `@markdown`, `@markdownCollection`
- **Dependencies (one-way):** `actions.validate.rule.RulesCollection` (from coerce of rules extracts)

## Constraint

Property name is the match. **File:** `{name}.md` beside the class. **Section:** `## Name` in `{slug}.md`. `@markdown` / `@markdownCollection` load that; callers do not assemble recipes here.

---

# harness/agent_tools
- **Purpose:** Let an author publish an ordinary class as operations an agent can list, run as Python, or follow as **instructions** — without writing MCP or skill wiring in that class.
- **Seam (terms):** AgentToolSet, AgentTool, AgentOperation, AgentInstructions, `@agent_toolset`, `@agent_tool`, `@agent_instructions`, `tools(...)`, `instructions(...)`
- **Dependencies (one-way):** `harness/markdown`

## Constraint

Stamp `@agent_toolset` when you want the agent (and install) to see the class; do not subclass *AgentToolSet*. A member carries exactly one of `@agent_tool` (run Python) or `@agent_instructions` (the **instructions** the agent follows). Wrap deferred work in `tools(...)` and nested recipes in `instructions(...)`. Wire-out (MCP, hooks, skills) lives in `harness/mcp`, `harness/hooks`, and `installation`. Put `@mcp`, `@skill`, `@hook`, `@command`, or `@rules` on a member to publish it there.

---

# harness/guidance
- **Purpose:** Let a practice be one class plus co-located markdown the agent follows, including fidelities and format **render**.
- **Seam (terms):** Guidance, GuidanceCollection, PracticeGuidance, FidelityGuidance
- **Dependencies (one-way):** `harness/agent_tools`, `harness/markdown`, `actions.validate.rule.RulesCollection`, `installation` (`@rules`, `@skill`, `@echo`, `@mcp`)

## Constraint

`instructions` is **overview** plus joined extracts. Skill and MCP marks sit on `instructions`. `PracticeGuidance.render` is the format seam; practices that own formats keep adapters under `{practice}/model/{format}/`.

---

# harness/guidance_actions
- **Purpose:** Let generate, document, scan, and the other kits share one prelude: bind the guidance list (or a string) and run the operation, optionally on an open work session.
- **Seam (terms):** GuidanceAction, GuidanceArg
- **Dependencies (one-way):** `harness/agent_tools`, `harness/hooks`, `harness/mcp` (`@echo`, `@hook`, `@mcp`)

## Constraint

*GuidanceArg* is a guidance list, one Guidance (ref or `{toolset, …}`), or a string to act on directly.

---

# harness/tool_catalog
- **Purpose:** Name the catalog shape — ToolSets, NestedTools, Tools, Operations, Instructions — so install and introspection share one outline.
- **Seam (terms):** AgentToolCatalog
- **Dependencies (one-way):** *(none — markdown outline only; no Python package)*

---

# harness/mcp
- **Purpose:** Mark a member `@mcp` and run a stdio host so Cursor can call it as an MCP tool or prompt.
- **Seam (terms):** Mcp, McpInstallation, McpServer, McpHost
- **Dependencies (one-way):** `installation`, `harness/agent_tools`

## Constraint

Cursor starts `python -m harness.mcp` or `harness/mcp/scripts/start_host.py`. `cdd.ping` is always listed. Only members marked `@mcp` enroll. Do not put this folder on `PYTHONPATH` as top-level `mcp`.

---

# harness/hooks
- **Purpose:** Mark a member `@Hook("event")` so Cursor stdin events run that Python and return one merged result.
- **Seam (terms):** Hook, Hooks, HookInstallation, HookServer
- **Dependencies (one-way):** `installation`, `harness/agent_tools`

## Constraint

The event name is the Cursor event (`sessionStart`, `preToolUse`, …). `@Hooks(disabled=True)` on a toolset skips every hook on it.

