## Language

*Builders* scaffold a new toolset or practice from templates so you do not copy a peer folder by hand.

Build order: `builders/create_agent_toolset` → `builders/create_context_tool`

---

# builders
- **Purpose:** Generate a new `@agent_toolset` or *PracticeGuidance* package from templates and a worked example.
- **Seam (terms):** CreateAgentToolset, CreateContextTool
- **Dependencies (one-way):** `harness/guidance`

## Constraint

Scaffolding stays in this tree. Do not invent new practices inside `harness/`.

---

# builders/create_agent_toolset
- **Purpose:** Scaffold a decorated *AgentToolSet* — `@agent_tool` operations and `@agent_instructions` recipes — matching `harness/agent_tools`.
- **Seam (terms):** CreateAgentToolset
- **Dependencies (one-way):** `harness/agent_tools`

## Constraint

Recipes use `tools(...)` / `instructions(...)`. Do not emit `@resource`. This is not a practice domain (that is *CreateContextTool*).

---

# builders/create_context_tool
- **Purpose:** Scaffold a new practice package under `practices/` from templates.
- **Seam (terms):** CreateContextTool
- **Dependencies (one-way):** `harness/guidance`

## Constraint

Do not put new domains inside `harness/` except through this kit.
