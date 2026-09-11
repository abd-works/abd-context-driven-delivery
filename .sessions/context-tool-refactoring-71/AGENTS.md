# Guidance resource model (#71)



- Do not use **slice** in this design — not for a `# Contexts` region, a `ContextSection` scope, or iterate workflow steps. Name the thing: **section** (md heading scope), **segment** (iterate tick), or the property name (`context`, `guidance`, `rules`).

- Fidelity content lives under `## Fidelities`, then one `## {name}` per `FidelityGuidance` — not as a top-level `## behavior` sibling of `## Guidance`.

- Fidelity collection type is `GuidanceCollection` (not `Fidelities`). Default key is `"name"` — `fidelities["behavior"]` / `getitem`. Other keys via `by(key_id, key)` (e.g. `by("stage", "specification")`; stage aliases in stage index).

- `name`, `format`, `default_format`, `context_guidance`, `fidelity`, and `templates` live on `ContextSection`. `@markdown` always uses `context_guidance.module_dir`. `fidelity: str | None` equals `name` on `FidelityGuidance`; on `ContextGuidance` at invoke holds the active domain key (`format` from `fidelities[context_guidance.fidelity].default_format`).
- **BDD vocabulary — context guidance, fidelity guidance.** Never **practice host**, **practice-wide**, or **on the practice** in om-bdd or `guidance_spec.py`. Scope before `## Fidelities` is **context guidance**; each `## {name}` under Fidelities is **fidelity guidance**.

- Module paths: `primitives/agent_toolset/` and `context_tools/agent_toolset/` (not `actions/`). `AgenticToolset` extends `Guidance` — `.instructions` / `.catalog` are **compound docs** (own markdown or catalog properties + iterate registry members). Registry: `instructions_registry` (was `actions`); `.instructions` is the assembled markdown `str`.
- Do not use **slots** in this design or BDD — name the thing: markdown property, catalog property, registry member, `context` / `guidance` / `rules` property. Same ban as vague MDC-style shorthand.

- `FidelityGuidance` is read-side only — no `generate` / `validate` / `satisfy` / `apply_to`. Lifecycle entry points live in `context_tools/agent_toolset/`.

- **Deploy — one seam: `Deployment`.** Names trace today's harness: `deployAgentInstructions` / `deployAgentTool` map to `operation_writes` rows for `@agent_instructions` and `@agent_tool` — not invented "toolset operation" terms. `deployToolset` mirrors the `operation_writes` loop in `_generate_entry`; deploy does **not** walk `instructions_registry`. Subtypes **override** `deployContextSection`, `deployContextSectionFidelity`, `deployAgentInstructions`, `deployAgentTool`. No parallel API (`deployMember`, …). Refactor extracts existing behavior from Harness/MCP — no new deploy semantics.
- **MCP — one walker, two moments.** `McpDeployment` owns the same `operation_writes` iteration as deploy. `deploy*` records `@mcp` ops and writes `mcp.json`; `bind(server)` enrolls them at server start only. Do not add a separate `McpToolset` that rescans annotations — that duplicates the deploy walk. Retire today's `McpToolset` getmembers loop in favor of `McpDeployment.bind`.
- **Shared contexts format** — the `# Contexts` chapter template (`context-tool-resource-model.md` § Contexts file layout; seed `create_context_tool/templates/domain-md.md`). Not a vague label for "common tests."
- **Markdown layout — folder, then file, then section in `{domain-slug}.md`.** Layer 4–5 BDD uses Mamba **`shared_context` / `included_context`**: define read outcomes once under a shared keyword string, each layout `description` sets fixtures in `before.each` then `included_context(...)`. Not RSpec `shared_examples` / `it_behaves_like`. Same resolution as today's `@instruction` / `AssetLocator`.
- **Object flows and BDD — canonical in `context-tool-resource-model-om-bdd.md`.** Validate sketches against **bdd-behavior** shared rules before porting to `guidance_spec.py`. **BDD subjects:** observable file, folder, or deploy tree — not internal classes. **`it should`** = stakeholder-visible outcome only — never assert two internal code paths agree, and never phrase implementation bans as behavior (`should not depend on deploy walk`, `should not use getmembers`, …); put read vs deploy wiring in design notes or `->` hints, not as tests. Put implementation hints on `->` port lines only. No type syntax or braces in describe/that/with/it labels. Use `that has been deployed` not "after write_deploy". **`with` is structure, not the test** — do not describe assembly/compound wiring in setup; nest `with the instructions property read` then state the outcome. **Do not test non-existence** — no `it should not expose …` for properties or hooks the new design never adds, and no “legacy API must be gone” negatives after a refactor; test what context guidance does, not what it doesn’t fly. Read: `instructions_registry`; deploy: `operation_writes`.

