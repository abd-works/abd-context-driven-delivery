# Guidance resource model (#71)

## Implementation turns (one om-bdd layer each)

- **Isolate first:** before any layer, backup remodeled production trees then move them to `legacy-no-longer-valid/`. That folder is requirements only (files written, strings returned, deploy tree) — not the design. Design is `context-tool-resource-model-om-bdd.md`. Do not write a layer while those modules still sit on the live import path.
- **Golden deploy:** `.cursor copy/` at repo root — successful MCP deploy snapshot. Deploy tests call real `Harness.write_deploy` into a temp dir and compare structure and bodies to `.cursor copy/` (skills, `mcp.json`, rules, MCP tails). Not a mock of the deploy pipeline.
- **Per turn:** `generate` (bdd-development + clean-engineering-model when types move) → write production code for that layer from the sketch → real deploy + mamba → subagent spot-check for MCP/skills when the layer includes them → `/turn`. One layer per commit.
- **No stubby deploy tests** — no mocking `Harness` / `Deployment` for disk outcomes. Real fixtures, real write_deploy, read files back.

- Do not use **slice** in this design — not for a `# Contexts` region, a `ContextGuidance` scope, or iterate workflow steps. Name the thing: **section** (md heading scope), **segment** (iterate tick), or the property name (`context`, `guidance`, `rules`).
- **Markdown deploy is three file kinds:** `@skill` (skill), `@command` (command), `@rules` (rule). Marks live on the member (`ContextGuidance.guidance()` is `@skill`, `rules` is `@rules`, `FidelityGuidance.guidance()` is `@command`). Deploy writes whatever the mark says — it does not hardcode a skill. Today’s harness `@prompt` is `@command`. MCP `prompts/get` / `McpPrompt` keep the protocol names.

- Fidelity content lives under `## Fidelities`, then one `## {name}` per `FidelityGuidance` — not as a top-level `## behavior` sibling of `## Guidance`.

- `GuidanceCollection` **is** `ContextGuidance` (Composite). Children are keyed (`entries: dict[str, ContextGuidance]`). Content reads (`context`, `guidance`, `templates`, `instructions`) iterate and join. `rules` is a `RulesCollection` keyed by those same child keys — not a concatenated list. `PracticeGuidance.fidelities` is a `GuidanceCollection`.
- **`RulesCollection` is the Composite of `Rule`.** `Rule.validate()` returns agentic instructions for the current context against that rule (and run the scanner when one exists). `RulesCollection.validate()` walks every child and returns those instructions in one shot. No `ScannerCollection` — each `Rule` has zero or one `Scanner`; `Scan` is `host.rules.scan`.
- **`Validate` action** — `Validate.validate(tools, rule=None)`. Default is all rules (`host.rules.validate()`). Pass one `Rule` to get that rule only.

- `name`, `format`, `default_format`, and `templates` live on `ContextGuidance`. The base does **not** hold a `PracticeGuidance`. Do not add `module_dir` — every class already has a file directory. `Markdown.extract` uses that. `FidelityGuidance` has `practice_guidance` (parent). `fidelity` lives on `FidelityGuidance` (equals `name`) and as the active key on `PracticeGuidance` at invoke (matching child in `fidelities`).
- **BDD vocabulary — context guidance, practice guidance, fidelity guidance.** `ContextGuidance` is the base (context / guidance / rules). `PracticeGuidance` is the practice host with `fidelities`. Each `## {name}` under Fidelities is **fidelity guidance**. No `Deployable` type — `Deployment.deploy` takes whatever.

- Module paths: `primitives/agent_toolset/` and `context_tools/agent_toolset/` (not `actions/`). No abstract `Guidance` type. `ContextGuidance` owns `.instructions` from `@markdown` properties. One type: `AgenticToolset`. Method marks (`@agent_tool`, `@agent_instructions`, unmarked = plain) are the **default** when a call is bare. Planned recipe bodies always wrap with `tools(...)` / `instructions(...)` — one call per line — even when the mark would have implied the run kind. Do not split Toolset / InstructionSet. HTML conversion lives on `Markdown.html()`; `Catalog` extends `HTML`.
- Do not use **slots** in this design or BDD — name the thing: markdown property, HTML read, registry member, `context` / `guidance` / `rules` property. Same ban as vague MDC-style shorthand.

- `FidelityGuidance` is read-side only — no `generate` / `satisfy` / `apply_to`. **Validate** lives on `Rule` / `RulesCollection` and the `Validate` action. Do not add generate/satisfy scenarios to om-bdd or `guidance_spec.py` — Catalog pages yes (`Markdown.html()` / `Catalog : HTML`), satisfy no (action recipe + validate report, different module).

- **Deploy — one seam: `Deployment`.** **Same write, two walks.** `guidance()` on context / fidelity guidance is `@agent_instructions` plus `@skill` or `@command` — `deployAgentInstructions` + `render` writes that file, same as a utility recipe. `rules` is `@rules` on the same render. `deployContextGuidance` / `deployFidelityGuidance` only visit those members; they do not write files themselves. `deployAgenticToolset` visits `operation_writes` on a bare toolset. `deployPracticeGuidance` and `deployAgenticToolset` are **only on `Deployment`**. The first calls `deployContextGuidance` then `deployFidelityGuidance` per fidelity. Subtypes implement the leaf writes; they do **not** re-implement either walk. **ide** and **path** are first-class properties of `Harness` — what IDE, where it is deployed. Construct a new harness with those values, or load the harness file (`primitives/harness/.deploy-state.json` today) — same two properties, not a last-vs-this pair. `Harness` constructs `Deployment(ide, path)`. They do not appear on `deploy` or the leaf methods. Cursor defaults to `.cursor`, VS Code to `.github`, Kilo to `.kilo`. `write_deploy` writes the harness file so the next load has ide + path. **MCP is `@mcp` on the member** — not a harness or `write_deploy` flag. `@mcp` still needs `@skill` / `@command` / `@rules` if there is a slash command. That file is the context section plus the MCP invoke tail — not the full instructions. Full prose is assembled when the MCP call runs. `McpDeployment` records marked members and writes `mcp.json`. `PracticeGuidance` is not an `AgenticToolset`. Action recipes (`Generate`, `Satisfy`, `Validate`, `Scan`, utilities) deploy when they are the registry host. `deployAgentInstructions` / `deployAgentTool` map to `operation_writes` rows for `@agent_instructions` and `@agent_tool` — not invented "toolset operation" terms. `deployAgenticToolset` mirrors the `operation_writes` loop in `_generate_entry`; deploy does **not** walk `instructions_registry`. Subtypes **override** `deployContextGuidance`, `deployFidelityGuidance`, `deployAgentInstructions`, `deployAgentTool`. No parallel API (`deployMember`, …). Refactor extracts existing behavior from Harness/MCP — no new deploy semantics.
- **MCP — one walker, two moments.** `McpDeployment` owns the same `operation_writes` iteration as deploy. `deploy*` records `@mcp` ops and writes `mcp.json`; `bind(server)` enrolls them at server start only. Do not add a separate `McpToolset` that rescans annotations — that duplicates the deploy walk. Retire today's `McpToolset` getmembers loop in favor of `McpDeployment.bind`. **MCP transport still writes skill/command/rules files** — it swaps the bottom invoke tail for `Use MCP tool: \`{slug}.{member}(…)\`` (`render_mcp_invoke`), not a different deploy shape.
- **Implementation order — read then markdown deploy per host.** Each om-bdd layer 3–6 pairs read with skill / command / rules deploy on the same fixture before the next layer. Layer 5 is practice guidance shared contexts only — no fidelity guidance. Layer 6 splits: fidelity instructions read → fidelity command deploy → assembly read → full-tree deploy. **MCP iteratively** — after each layer’s markdown deploy is green, prove the mcp shared contexts on fixtures whose members are `@mcp`. Layer 7 is manifest + host invoke: `@mcp` member → deployed → server started from manifest → tools/call or prompts/get. Layers 8–9: catalog then **hooks last**. **Deploy shared contexts** define outcomes once; each `describe` runs `write_deploy` in `before.each` then `it_behaves_like`. A layer’s mcp `describe` includes only the mcp shared contexts — not the full-body skill/command shared context; `@mcp` files are context section plus tail.
- **Shared contexts format** — the `# Contexts` chapter template (`context-tool-resource-model.md` § Contexts file layout; seed `create_context_tool/templates/domain-md.md`). Not a vague label for "common tests."
- **Markdown layout — folder, then file, then section in `{domain-slug}.md`.** Layer 4–5 BDD uses **`bdd` § Share**: **`shared context "…"`** exercises a common subject (`context guidance` / `fidelity guidance`); each layout **`describe`** assigns it in **`before.each`**, then **`it_behaves_like "…"`**. Same resolution as today's `@instruction` / `AssetLocator`.
- **Object flows and BDD — canonical in `context-tool-resource-model-om-bdd.md`.** Validate sketches against **bdd-behavior** shared rules before porting to `guidance_spec.py`. **BDD subjects:** observable file, folder, or deploy tree — not internal classes. **`it should`** = stakeholder-visible outcome only — never assert two internal code paths agree, and never phrase implementation bans as behavior (`should not depend on deploy walk`, `should not use getmembers`, …); put read vs deploy wiring in design notes or `->` hints, not as tests. Put implementation hints on `->` port lines only. No type syntax or braces in describe/that/with/it labels. Use `that has been deployed` not "after write_deploy". **`with` is structure, not the test** — do not describe assembly/compound wiring in setup; nest `with the instructions property read` then state the outcome. **Do not test non-existence** — no `it should not expose …` for properties or hooks the new design never adds, and no “legacy API must be gone” negatives after a refactor; test what context guidance does, not what it doesn’t fly. Read: `instructions_registry`; deploy: `operation_writes`.

## Layer status (implementer)

Command that passed (78 examples):

`mamba context_tools/context_guidance/guidance_spec.py`

(venv `python -m mamba` is not available here; system `mamba` CLI was used.)

| Layer | Status | Commit |
| ----- | ------ | ------ |
| Isolate | green (prior) | `d7199c6e` |
| 1 Markdown | green | `28e33fd7` |
| 2 ContextGuidance.instructions | green | `82759f68` |
| 3 AgenticToolset read + deploy | green | `d8fdf06b` |
| 4 ContextGuidance deploy | green | `eb111038` |
| 5 PracticeGuidance shared contexts + Validate + deploy | green | `710b774b` (also holds later-layer production types) |
| 6 FidelityGuidance + assembly + full tree + VS Code | green | `ff540381` |
| 7 MCP manifest + host invoke | green | recorded below |
| 8 Catalog : HTML | green | recorded below |
| 9 HookDeployment | green | recorded below |

Turn `git add -A` did not pick up empty `__init__.py` files ignored by gitignore, and did not stage the huge untracked `.cursor/` tree. Production guidance/harness/MCP/catalog files landed in `710b774b`.


