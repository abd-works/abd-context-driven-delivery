# Session: context-tool-refactoring-71

## Start

- **date:** 2026-09-10
- **path:** .
- **goal:** Context-tool refactoring (#71) — parent ticket for structural refactors.
Child tickets: #22 standard fidelities on BaseContextTool; #68 dynamic content creation; #21 catalog/harness overlap; #19 domain transform/render on BaseContextTool.
- **fidelities:** (unset)
- **contexts:** #71 #22 #68 #21 #19

## Tickets

### #71 — Context-tool refactoring

https://github.com/abd-works/abd-context-driven-delivery/issues/71

Parent for context-tool structural refactors: standard fidelities on BaseContextTool, dynamic content creation, catalog/harness overlap, and invoke render on the base.

### #22 — Standard fidelities property on BaseContextTool that subclasses only override

https://github.com/abd-works/abd-context-driven-delivery/issues/22

# Standard fidelities property on BaseContextTool that subclasses only override

Guidance for this ticket came from `BaseContextTool` and the domain context tools (Stories, Clean Engineering, Bdd, Ddd, Ux, Cdd).

## Forward requirements (from prompt)

- Create a standard property for fidelities across context tools
- Declare it on the base
- Subclasses only overwrite it
- Right now it is a little all over the place

## Current recording (from source)

- Base already has `fidelities: ClassVar[dict[str, str] | None] = None`, `STAGE_ALIASES`, `resolve_fidelity`, and `_fidelity_format_defaults`
- Each domain still copies its own `fidelities = { SHAPING/DISCOVERY/SPEC/ENGINEER: name }` dict plus a parallel `_FIDELITY_FORMAT_DEFAULTS` / `_fidelity_format_defaults`
- Every subclass `__init__` still does `resolve_fidelity`, format default, and `self.fidelity = …` (Ddd uses `_fidelity` + a property instead)
- Session `WorkSession.fidelities` is a string on the sprint, not that ClassVar
- Cdd's `fidelities` map stages to stage names (`discovery`/`spec`/`engineer`); other tools map to domain names (`story_map`, `modules`, `ia`, …)
- Some tools omit SHAPING (Clean Engineering, Bdd, Ux)

## Handoff — base (2026-08-27)

## Resume

- **Stage:** (unset)
- **Last work:** (see session progress below)
- **Next action:** Standard fidelities property on BaseContextTool that subclasses only override
- **Next focus:** Standard fidelities property on BaseContextTool that subclasses only override

## Artifacts to read

- `context_tools/base/.context/module-context.md`
- `context_tools/base/base_context_tool.py`
- `context_tools/stories/stories.py`
- `context_tools/clean_engineering/clean_engineering.py`
- `context_tools/bdd/bdd.py`
- `context_tools/ddd/ddd.py`
- `context_tools/ux/ux.py`
- `context_tools/cdd/cdd.py`
- `.context/context-index.md`

### #68 — Easier dynamic content creation so that we can have base content be included without having to do hyperlinks for more than just context tools

https://github.com/abd-works/abd-context-driven-delivery/issues/68

*(Issue body empty on GitHub — title is the requirement.)*

### #21 — Catalog and harness likely overlap on classes, skills, actions, and render

https://github.com/abd-works/abd-context-driven-delivery/issues/21

# Catalog and harness likely overlap on classes, skills, actions, and render

Guidance for this ticket came from `utilities/catalog_generator` and `primitives/harness` (not a domain context tool such as Bdd or Stories).

## Forward requirements (from prompt)

- Catalog and harness likely have overlapping classes, render, skills, actions, and so on
- Look at that overlap

## Current recording (from module-context and source — do not conclude merge)

- Catalog discover-and-render wraps the real object model (`Toolset.tools`, `AgenticToolset.instructions` registry (`@agent_instructions`; was `actions`), `BaseContextTool.fidelities`) and renders HTML via `CatalogTool`, `CatalogAction`, `CatalogFidelity`, `CatalogContextTool`, `CatalogUtility`, `Catalog`
- Catalog already lists Harness in `UTILITY_REGISTRY` and comments that harness owns generate (replaces old deploy_agent_skills)
- Catalog `skill_slash_name` reads deployed `.cursor/skills/{name}/SKILL.md`; harness `Skill` / `Prompt` / `Command` *write* those IDE files
- Catalog `resolve_lifecycle_actions` AST-walks BaseContextTool actions; harness walks `context_tools` and `utilities` for `@agentic_toolset` / `@skill` / `@prompt` and generates skills, commands, hooks, agents, agent guidance
- Harness treats `catalog_generator` as a stale action-skill slug (`_STALE_ACTION_SKILL_SLUGS`)
- Same vocabulary (tool, action, skill, render, context tool) on both sides; whether the classes and walks should be one seam is the investigation

## Handoff — catalog_generator (2026-08-27)

## Resume

- **Stage:** (unset)
- **Last work:** (see session progress below)
- **Next action:** Catalog and harness likely overlap on classes, skills, actions, and render
- **Next focus:** Catalog and harness likely overlap on classes, skills, actions, and render

## Artifacts to read

- `utilities/catalog_generator/.context/module-context.md`
- `utilities/catalog_generator/catalog_generator.py`
- `primitives/harness/harness.py`
- `primitives/harness/.context/harness-sketch.md`
- `.context/context-index.md`

### #19 — Investigate whether domain transform and render can live on BaseContextTool

https://github.com/abd-works/abd-context-driven-delivery/issues/19

# Investigate whether domain transform and render can live on BaseContextTool

## Forward requirements (from prompt)

- Clean Engineering, Stories, and others have both `transform` and `render`
- Are these the exact same methods that can be put on `BaseContextTool`?
- Need to investigate

## Current recording (from source — do not conclude yet)

- `BaseContextTool` already has `render(format, content="")` that checks `supported_formats` then raises unless a subclass overrides; it has **no** `transform`
- `Render` lifecycle action (`context_tools/agent_toolset/render/render.py`) loops provided tools and calls `tool.render(format, content)`
- Clean Engineering, Stories, Ux each define `@agent_tool transform(source_format, target_format, content)` as channel parse → canonical → channel render, and `render` as transform from `self.format` to `format` (content required)
- Clean Engineering `render`/`transform` also take `previous` and `keep_positioning` (drawio); Stories/Ux/Bdd signatures do not
- Bdd and Ddd `transform`/`render` delegate to Clean Engineering rather than their own channels
- Same names and similar bodies appear on several domains; whether they are the **exact same** method that can lift to `BaseContextTool` is the investigation

## Handoff — guidance resource model implementation (2026-09-11)

## Resume

- **Stage:** layer 1 green; layer 2 next
- **Last work:** Layer 1 — `primitives/markdown`, `@markdown`, `context_tools/context_guidance/guidance_spec.py` + real fixtures; golden-reference workflow documented
- **Next action:** **Layer 2 turn** — minimal `Guidance` compound instructions and catalog (`generate` → migrate → real spec → `/turn`)
- **Next focus:** Layer 2 only — no deploy yet

## Golden deploy reference

- **Path:** `.cursor copy/` (repo root, local — successful `write_deploy(mcp=True)` snapshot)
- **Use:** compare deploy test output (skills, `mcp.json`, rules, MCP tails) to matching paths under `.cursor copy/`
- **Note:** fidelity commands appear as skills `{slug}-{fidelity}` in MCP golden, not only under `commands/`

## Handoff — base (2026-08-26)

## Resume (archived)

- **Next action:** Investigate whether domain transform and render can live on BaseContextTool
- **Next focus:** Investigate whether domain transform and render can live on BaseContextTool

## Artifacts to read

- `context_tools/base/.context/module-context.md`
- `context_tools/base/base_context_tool.py`
- `context_tools/agent_toolset/render/render.py`
- `context_tools/clean_engineering/clean_engineering.py`
- `context_tools/stories/stories.py`
- `context_tools/bdd/bdd.py`
- `context_tools/ddd/ddd.py`
- `context_tools/ux/ux.py`
- `.context/context-index.md`
