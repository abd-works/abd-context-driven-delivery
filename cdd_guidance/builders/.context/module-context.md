# cdd_guidance/builders
*Builders* scaffold a new toolset or practice from templates and a worked example, so a new one starts in the shape the installer, the MCP host, and the actions already expect instead of being copied from a peer folder by hand. Each builder is itself a *PracticeGuidance*: its instructions carry its rules, templates, and examples.

*CreateAgentToolset* scaffolds an ordinary class as an agent toolset — `@agent_toolset` on the class, `@agent_tool` operations, and `@agent_instructions` recipes that call `tools(...)` and `instructions(...)` — matching the worked `car` example (`create-agent-toolset.instructions`).

*CreatePracticeGuidance* scaffolds a new practice under `cdd_guidance/practices/`: a thin *PracticeGuidance* subclass, its `{practice}.md` with Overview, shared rules, and a section per fidelity, its templates, and its examples (`create-practice-guidance.instructions`).

*CreateContextTool* scaffolds a practice that partitions and indexes source context, keeping the framework's defaults rather than overriding them (`create-context-tool.instructions`).

- **Purpose:** Start every new toolset and practice from the same templates, so it installs and runs with the existing actions on its first try.
- **Seam (terms):** CreateAgentToolset, CreatePracticeGuidance, CreateContextTool, `create-agent-toolset.instructions`, `create-practice-guidance.instructions`, `create-context-tool.instructions`
- **Dependencies (one-way):** `harness/guidance` (*PracticeGuidance*), `harness/agent_tools` (`@agent_toolset`)

## Constraint

Put a new practice in its own folder under `cdd_guidance/practices/` and a new toolset beside the domain it serves; never put a new practice inside `harness/`. Keep the framework's defaults: do not override `module_dir` or the instruction sections the framework already loads from the practice's markdown. Run lifecycle steps on the new practice through the actions (`generate.generate(guidance=[...])`), not as methods on the practice class.
