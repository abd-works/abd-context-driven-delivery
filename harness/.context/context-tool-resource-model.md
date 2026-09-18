# Guidance resource model (proposed remodel)

**Sources / context:** `.sessions/context-tool-refactoring-71/session.md` (#71, #22, #68, #21); today `practices/base/base_context_tool.py` (`BaseContextTool`) → target `harness/guidance/` (*Guidance*, *Guidance*, …); `installation/`; `tools/catalog_generator/`. **Out of scope for this pass:** full `document` channel implementation (ticket #19 partial). **In scope in model:** where `render` / `iterate` live relative to *Guidance* vs lifecycle action kits.

**Three roles — do not collapse them:**

| Role | Who | Job |
| ---- | --- | --- |
| **Reading** | *Guidance* / *PracticeGuidance* / *AgenticToolset* | `@markdown`, `.instructions`, `Markdown.html()`, `@agent_tool`, `@agent_instructions` — assemble and return content when asked |
| **Deploy** | **`Deployment.deploy(deployable)`** | dispatch: PracticeGuidance → `installPracticeGuidance`; AgenticToolset → `deployAgenticToolset` |
| **Mechanism** | **subtypes** | *MarkdownInstallation*, *McpInstallation*, *HookInstallation* extend *Deployment* and **implement** abstract `deployGuidance`, `installFidelityGuidance`, `installAgentInstructions`, `installAgentTool`, … |

Runtime invoke and deploy use the same read side: channel calls `.instructions` on the *Guidance* / *FidelityGuidance* passed in; agent calls `guidance()` → same string.

**Layers (not alternatives):**

```
harness/markdown          read — @markdown extract
harness/guidance   read — ContextSection.instructions + overrides
harness/agent_toolset     read — @agent_instructions recipes, @agent_tool
installation           Deployment.deploy(deployable) — MarkdownInstallation, McpInstallation, HookInstallation, Harness
```

Also: MCP/CLI `context:` block = invoke args (fidelity, path, session) — not the `context` `@markdown` property on *ContextSection*. `**.guidance`** on *ContextSection* = `@markdown` property reading the `## Guidance` / `### Guidance` section — not informal "guidance" prose.

**Deploy:** rules live in the class intro that owns them — under **Modules** below (`AgenticToolset`, `Guidance`, `Harness`, …). No separate deployment chapter.

---

## Modules

**Design stance:** `**Guidance` has `instructions`** — the agent read seam. No abstract `Guidance` type. `deploy` and agents **read** instructions; Harness does not build them. Human pages are `Markdown.html()`; `Catalog` extends `HTML`.

Build order: `harness/markdown` → `harness/guidance` → `harness/agent_toolset` → `installation` → `catalog_generator`

**One read path:** runtime `guidance()` and deploy channels call `.instructions` on the host — no `compound_guidance` subprocess in Harness. Catalog pages call `Markdown.html()` on `@markdown` properties.

**Three modules — do not merge them:**

```
harness/markdown         Guidance (harness/guidance)        AgenticToolset (harness/agent_toolset)
─────────────────────       ─────────────────────────────        ────────────────────────────────
@markdown per extract property       instructions @property → assemble    @agent_instructions → action recipe
Markdown.extract() / html()     HTML on Markdown; Catalog : HTML       @agent_tool → tools dict
@markdown on ContextSection  context, guidance, rules (`RulesCollection` for rules)   Deployment (@skill @command @instruction @hook @mcp …) on installation
```

Extract and assemble are sequential — `@markdown` does not compete with `instructions`. `harness/markdown` does not import `harness/agent_toolset`.

---

# harness/markdown

*Markdown* (`harness/markdown`) — `@markdown` decorator + `Markdown` value object + `HTML`. Extraction and HTML conversion — not instructions assembly.

- **Dependencies:** none. `AssetLocator` lives in this package. No `harness/agent_toolset`.

## Markdown

**`@markdown`** decorates each host property that reads co-located md. Property name = label. `Markdown.extract` uses the host class’s file directory — no `module_dir` on the host. `host.name` scopes fidelity sections:

1. `{label}/` folder — merge files
2. `{label}.md` file
3. `## {Label}` (or `###` under fidelity scope) in `{slug}.md`

Return type on the property selects coercion: `str` → extracted text; `RulesCollection` → parse rules-section bullets into a `RulesCollection`; `dict[str, str]` → scan `templates/` into **format key → relative path** (same scan rules as today's `AssetLocator` for the `templates` label); `HTML` → `Markdown.html()`. Any `@markdown` property can be read as HTML.

```python
@markdown
def context(self) -> str: ...

@markdown
def guidance(self) -> str: ...

@markdown
def rules(self) -> RulesCollection: ...

@markdown
def templates(self) -> dict[str, str]: ...   # format → path under module_dir

@markdown
def examples(self) -> str: ...                # Guidance only — not in instructions
```

`templates[format]` subscripts the map and **reads file content** at that path (with fidelity line-filter on *FidelityGuidance* — today's `filter_template_lines`).

- @markdown
// decorator — getter → Markdown.from_label(owner, label).extract() → coerce to property return type
- from_label(host, label): Markdown
- extract(): str
- html(): HTML
// HTML.from_markdown(extract()) — renamed from catalog
- coerce(text: str, return_type): str | RulesCollection | dict[str, str] | HTML
// dict[str, str] — format key → relative path; subscript loads content

**Label paths:** `context` → `# Contexts` section for this host's scope; `guidance` / `rules` → practice `## …` before `## Fidelities`; fidelity `### …` under `## Fidelities` → `## {name}`; `examples` → `examples/` folder; `templates` → `templates/` folder scan → path map.

**Host requirement:** `context_guidance` on every *ContextSection* — `@markdown` uses `context_guidance.module_dir`. `name` scopes extract (`None` practice-wide; fidelity name under `## Fidelities` → `## {name}` in `{slug}.md`; #68 prior `##` stack in `context`). `fidelity: str | None` on the base — equals `name` on *FidelityGuidance*; active domain key on *Guidance* at invoke.

---

+ host.{label}
<< triggered by >> any caller (`self.context`, `instructions` assembly, tests, …)
	-> Markdown.from_label(host, label)
	-> Markdown.extract()
	-> Markdown.html() when the read is HTML
	-> Markdown.coerce(return_type)   // str | RulesCollection | dict[str, str] | HTML
<< uses >> AssetLocator
	-> AssetLocator.locate(class file directory, label)
	// folder → file → section in {slug}.md; templates/ → format → path map
	-> str | RulesCollection | dict[str, str]

---

# harness/guidance

- **Dependencies (one-way):** `harness/markdown`, `workspace`, `actions/scan` (`Rule`)

## Guidance

*Guidance* — base. **`instructions`** is the public compound-doc seam assembled on read, not a registry. No abstract `Guidance`. Human pages are `Markdown.html()`; types that used to expose `catalog` extend `HTML`.

### Compound doc

One type: *AgenticToolset*. Method marks (`@agent_tool`, `@agent_instructions`, unmarked = plain) are the **default** when a call is bare. Planned recipe bodies always wrap — make every call explicit even when the mark would have implied it. Write one call per line:

```
tools(
    self.some_method,
    self.other_class.some_other
)
instructions(
    self.dynamically_add_ins()
)
```

No `@plain_operation`. Do not split Toolset / InstructionSet. `PracticeGuidance` is also `AgenticToolset`. deploy, MCP, and `guidance()` read assembled documents from the host.

Instructions assembly:

1. **Own markdown properties** — subclass content first (*ContextSection*: `@markdown` joins; bare *AgenticToolset*: module/operation prose).
2. **Iterate members** — stable order over registered operations; append each slice.
   - **`instructions`** (`str`, markdown) — per `@agent_instructions` in the **instructions registry** (was `actions`).

Replaces `compound_guidance` subprocess (deploy). Harness copies `.instructions`. `Catalog` extends `HTML` and writes pages from `@markdown` properties via `Markdown.html()`.

### Type hierarchy

```
Guidance                 @markdown properties → compound instructions; no fidelity
├── PracticeGuidance            not an AgenticToolset; fidelities collection; instructions = Guidance + fidelities
└── FidelityGuidance            `practice_guidance` = practice; `fidelity` = `name`

AgenticToolset                  Toolset — compound instructions from registry iteration
```

*Guidance* is the common base for both *PracticeGuidance* and *FidelityGuidance*. Each declares the same four `@markdown` extract properties (`context`, `guidance`, `rules`, `templates`), plus `format`, `default_format`, and `name`; `instructions` on *Guidance* joins them with the same logic on every host. No `module_dir` on the host — `Markdown.extract` uses the class file directory. The base does not hold a *PracticeGuidance*. *FidelityGuidance* points up with `practice_guidance`. `name` scopes section extract. `fidelity` lives on *FidelityGuidance* (equals `name`) and as the active key on *PracticeGuidance* at invoke (matching child in `fidelities`). *FidelityGuidance* does not override `instructions`. *PracticeGuidance* overrides `instructions` to append `fidelities.instructions`.

**`rules`** are a `RulesCollection` (`actions/scan`) — `@markdown` coerces the rules section; each `Rule` has **zero or one** `Scanner` named by `slug` — **and** `format_rules(rules)` inlines them into `instructions`. Same objects for scan, validate, deploy, and prose.

**Not in `instructions`:** `@markdown examples` on *PracticeGuidance* only.

### What `instructions` and `HTML` are (and what they are not)


|                | `**instructions**`                                                                                                                                                                                                                                                                                                                             | `**HTML**`                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Audience**   | Agent (IDE skill, command body, `action: guidance`, MCP expand)                                                                                                                                                                                                                                                                                | Human (CDD catalog site)                                                                                |
| **Shape**      | `@property` on *Guidance* / *AgenticToolset* → `str` (markdown)                                                                                                                                                                                                                                                                          | `Markdown.html()` → `HTML`; `Catalog` extends `HTML`                                                    |
| **Built from** | **Compound instructions doc:** own markdown properties. *Guidance*: `@markdown` joins. *AgenticToolset*: instructions registry. *PracticeGuidance*: super + `fidelities.instructions`. **`examples` excluded** | One `@markdown` extract converted to HTML.                                                              |
| **Consumers**  | Harness deploy, runtime `guidance()` → `return self.instructions`                                                                                                                                                                                                                                                                              | `Catalog` only                                                                                          |
| **Not**        | Catalog pages, `examples/` folder                                                                                                                                                                                                                                                                                                                    | Agent skills, generate/validate recipes                                                                |


Override `**instructions**` on *Guidance* only — *FidelityGuidance* uses *ContextSection* assembly unchanged. Do not put assembly on `@markdown` extract labels. Runtime-only orchestration (e.g. a practice calling a companion's `guidance()` with `mode=tool`) stays on `**@agent_instructions guidance()**` and is **not** part of deploy `instructions`.

- Guidance()
// Base — instructions @property from @markdown joins; no fidelity

### Instructions assembly (today → target)


| Path        | When                            | Mechanism                                                                |
| ----------- | ------------------------------- | ------------------------------------------------------------------------ |
| **Runtime** | `action: guidance` / `generate` | `guidance()` → `self.instructions`; action recipes that mention `self.examples` hit the `@markdown` getter like any other caller |
| **Deploy**  | Harness writes skills/commands  | today: `compound_guidance` subprocess — **target:** read `.instructions` |


**Today `guidance()` on `BaseContextTool`** — method body is a recipe; `harness/agent_toolset/action.py` walks the AST (`self.contexts`, `super().guidance()`, companion deferrals). **Target:** `return self.instructions`.


| Today                                         | Moves to                                              |
| --------------------------------------------- | ----------------------------------------------------- |
| Assembly in `BaseContextTool.guidance()` body | `Guidance.instructions` @property override     |
| Merged `templates/` + `filter_template_lines` | `@markdown templates` → `dict[str, str]` path map; `templates[format]` reads content + fidelity filter |
| Prior-depth stack (#68)                       | `FidelityGuidance.context` — prior `## {name}` blocks in declaration order |
| `compound_guidance` subprocess                | Harness reads `fidelity.instructions`                 |
| `ContextToolBody` assembly                    | *Deployment* on `instructions` / `rules` — `@skill`, `@command`, `@rules` |


**Practice vs fidelity `.instructions`:** *Guidance* — `super.instructions` (practice-wide extract) + `fidelities.instructions` (each *FidelityGuidance* joined in declaration order). Each *FidelityGuidance* — same *ContextSection* `instructions` property; `name` scopes `@markdown` extract (`context` includes #68 prior `##` stack). **`examples`** — read via `.examples` when an action recipe asks; never merged into `.instructions`.

Assembly interactions — **Behavior sketch (BDD)** object flows.

## ContextSection

*ContextSection* extends *Guidance* — common base for *Guidance* and *FidelityGuidance*. Four `@markdown` extract properties plus `format`; `instructions` joins them with the same logic on every host.

| Property | Role | `@markdown` return |
| -------- | ---- | ------------------ |
| `context` | Scoped `# Contexts` section — like today's `contexts` `@instruction` | `str` |
| `guidance` | `## Guidance` on *Guidance*; `### Guidance` under `## Fidelities` → `## {name}` on *FidelityGuidance* | `str` |
| `rules` | `## Shared rules` on *Guidance*; `### Rules` under each fidelity `## {name}` | `RulesCollection` |
| `templates` | Scan `templates/` for this host scope — practice-wide on *Guidance*; fidelity subset on *FidelityGuidance* | `dict[str, str]` |
| `format` | Active format for `templates[format]` in `instructions` | — |
| `default_format` | Fallback when `format` unset; invoke copies to `format` on the active host | — |
| `name` | `None` on practice-wide *Guidance*; fidelity domain name on *FidelityGuidance* — scopes `@markdown` extract | — |
| `context_guidance` | Practice host — `self` on *Guidance*; parent on *FidelityGuidance*; `@markdown` `module_dir` always from here | — |
| `fidelity` | Domain fidelity key — equals `name` on *FidelityGuidance*; active key on *Guidance* at invoke; `None` practice-wide | — |

`ContextSection.instructions` → `context` + `guidance` + `format_rules(rules)` + `templates[format]`.

**Contexts file layout** (`bdd.md`, `# Contexts` chapter):

```
# Contexts
preamble before first ##     → Guidance.context
## Guidance                  → Guidance.guidance
## Shared rules              → Guidance.rules

## Fidelities

## sketch                      → FidelityGuidance("sketch").context
  ### Guidance                 → FidelityGuidance("sketch").guidance
  ### Rules                    → FidelityGuidance("sketch").rules
## modules                     → FidelityGuidance("modules").context
  ### Guidance / ### Rules     → same pattern per name
## behavior                    → FidelityGuidance("behavior").context
  (body + prior ## stack #68)  → included in behavior.context
  ### Guidance                 → FidelityGuidance("behavior").guidance
  ### Rules                    → FidelityGuidance("behavior").rules
## development                 → FidelityGuidance("development") …
```

Practice-wide sections end at `## Shared rules`. Every fidelity is a `## {name}` heading under `## Fidelities`, not a sibling of `## Guidance`. Today some domains omit the `## Fidelities` wrapper — migrate by inserting it and nesting existing fidelity `##` headings underneath.

`Key rules:` one-liners and separate `rules/` folder files are out of scope.

- ContextSection()
// abstract — context, guidance, rules, templates are @markdown; instructions joins them

---

- instructions: str
// @property — context + guidance + format_rules(rules) + templates[format]
- context: str
// @markdown — # Contexts section for this host's scope
- guidance: str
// @markdown
- rules: RulesCollection
// @markdown — coerce bullets → RulesCollection
- templates: dict[str, str]
// @markdown — format key → relative path; templates[format] reads content
- format: str
// active format for templates[format] in instructions assembly
- default_format: str
// fallback when format unset; invoke copies to format on active host
- name: str | None
// scopes @markdown extract; None = practice-wide on Guidance
- context_guidance: Guidance
// @markdown module_dir always from here
- fidelity: str | None
// equals name on FidelityGuidance; active domain key on Guidance at invoke
- format_rules(rules: RulesCollection): str

## Guidance

*Guidance* extends *ContextSection* + *AgenticToolset* at practice scope (Stories, Bdd, Clean Engineering, …). Practice-wide `context` / `guidance` / `rules` / `templates` come from the top of `# Contexts` and practice `templates/` scan. `**fidelities: GuidanceCollection`** — *Guidance* children; `.instructions` joins them in declaration order.

### `instructions` assembly (practice level)

*Guidance* **overrides** `instructions`:

1. `super.instructions` — practice `context` + `guidance` + `format_rules(rules)` + practice `templates[format]`
2. `fidelities.instructions` — each *FidelityGuidance*.`instructions` in declaration order (sketch first)

**Rules as collection:** `practice.rules` and each `fidelity.rules` are a `RulesCollection` — `Scan` is `host.rules.scan`, `Validate` defaults to `host.rules.validate()` (or one `Rule`), and `RuleSpec` deploy. **Same collection** formatted into `instructions` via `format_rules`.

### Deploy

Harness does **not** build guidance prose. Deploy runs *Deployment* on declared members — same path for practice, fidelity, utilities, and lifecycle operations.

| Member | Host | Read | Deploy |
| ------ | ---- | ---- | ------ |
| `instructions` | *Guidance* | `@markdown` assembly + `@property` | `@skill` `@agent_instructions` → router skill; `guidance()` → `self.instructions` |
| `rules` | *Guidance* | `@markdown` → `RulesCollection` | `@rules` → one `.cursor/rules/{slug}.mdc` per `Rule` |
| `instructions` | *FidelityGuidance* | `@markdown` assembly + `@property` | `@command` `@agent_instructions` → fidelity command |
| `rules` | *FidelityGuidance* | `@markdown` → `RulesCollection` | `@rules` → one rule file per `Rule.slug` |

**Naming:** `@rules` on the `rules` property — not `@instruction` (that is a **named** rule file on an **operation**) and not `@instructions` (collides with `instructions`). `Deployment.installPracticeGuidance` walks sections; *MarkdownInstallation* **implements** `deployGuidance` / `installFidelityGuidance` / `installAgentInstructions` / `installAgentTool`.

```
Guidance                   # ContextSection + AgenticToolset
├── context / guidance / rules    # @markdown — practice-wide top of # Contexts
├── .instructions
├── templates                     # @markdown on ContextSection — practice templates/ scan
├── .examples                     # @markdown — not in practice.instructions
└── fidelities: GuidanceCollection
    └── FidelityGuidance × n      # ContextSection per ## {name}
```

- Guidance(format, path, session, workspace)

---

- << composition >> fidelities: GuidanceCollection   // sketch FidelityGuidance first — stage "sketch"
- << association >> workspace: Workspace
- << association >> scanner: Scan

---

- instructions: str
// @property override — super.instructions + fidelities.instructions
- context / guidance / rules / templates
// @markdown — inherited from ContextSection; practice-wide scope
- examples: str
// @markdown — not in instructions

### Slim-down (retire from `BaseContextTool`)

*Guidance* holds `instructions`, `context`/`guidance`/`rules`, `fidelities`, `templates[format]`, workspace/scanner — not session prose, fidelity method synthesis, satisfy hooks, or render iteration loops.


| Today on CT                                            | Target                                                                |
| ------------------------------------------------------ | --------------------------------------------------------------------- |
| `session_guidance()`                                   | **Workspace** only                                                    |
| `fidelities` dict, `STAGE_ALIASES`, `resolve_fidelity` | `GuidanceCollection` of *Guidance* children; join `.instructions` |
| `_generate_fidelity_methods()`                         | **Retire** — `Generate` / `Satisfy` stay independent `@agent_instructions`; `Validate` is on `Rule` / `RulesCollection` / the Validate action |
| `_set_fidelity`                                        | **Retire** — invoke sets `practice.fidelity`; format from the matching child in `fidelities` |
| `generate_fixes_from_validate()`                       | **Retire** — Satisfy action recipe                                    |
| # Open prelude on base md                              | Workspace + `GuidanceAction.begin`                                   |
| Render iterate loops on CT                             | `actions/render/`                                                       |


**Keep on domain practice:**


| Member                    | Role                                              |
| ------------------------- | ------------------------------------------------- |
| `generate_output()`       | Domain body for **Generate** action               |
| `render(format, content)` | Channel transform when supported                  |
| `@markdown` labels        | `context`, `guidance`, `rules`; `examples`; `scaffold` lifecycle-only |
| `templates`               | `@markdown` → `dict[str, str]` (format → path); `templates[format]` reads content |
| `load_template`           | `@agent_tool` — `fidelities[fidelity].templates[format]` |


### `templates` — `@markdown` on *ContextSection*

`templates` is declared on *ContextSection* — both *Guidance* and *FidelityGuidance* inherit it. `@markdown` scans `templates/` (same rules as today's `AssetLocator` + `_path_for_templates`) and coerces to **`dict[str, str]`**: canonical **format key → relative path** under `module_dir`. Subscript `templates[format]` loads file content at that path.

**Format keys** — canonical names from `supported_formats` / host `format` (`markdown`, `python`, `typescript`, `java`, …). Folder aliases (`md`, `py`, `ts`) map to those keys when building the dict.

**Host scope:**

| Host | Map includes |
| ---- | ------------ |
| *Guidance* | All produce files / format packs under `templates/` for this practice |
| *FidelityGuidance* | Entries this fidelity owns — sketch file on sketch node; `{slug}-templates.{ext}` on produce nodes; optional fidelity filter via `filter_template_lines` on read |

#### Naming standard (existing CTs — migrate as-is)

Do **not** invent `{domain}-{fidelity}-{format}.md` unless a domain already uses that shape. Keep today's filenames; the map keys are format, not fidelity.

| On disk (under `templates/`) | Format key | Typical fidelity | Domains today |
| ----------------------------- | ---------- | ---------------- | ------------- |
| `{slug}-sketch.md` | `markdown` | sketch | bdd, ddd, stories, clean_engineering, ux |
| `{slug}-templates.py` | `python` | produce | bdd, clean_engineering, agent_bdd |
| `{slug}-templates.ts` | `typescript` | produce | bdd |
| `{slug}-templates.md` | `markdown` | produce | clean_engineering |
| `{slug}/` or `{alias}/` format pack | `markdown` / `python` / `typescript` | per-file frontmatter / stem | stories (`md/`, `py/`, `ts/`) |
| `{artifact}-template.md` | `markdown` | named artifact | ddd (`bounded-context-template.md`), stories (`scenario-template.md`) |
| Other produce assets | extension → format | practice | clean_engineering (`modules.drawio` — channel-specific, not in format map unless declared) |

**Stem rule:** `{slug}` = `module_dir.name` with underscore/hyphen variants (`_slug_variants` today). Produce stem is always `{slug}-templates` or `{slug}-template` (both accepted). Sketch stem is `{slug}-sketch`.

**Fidelity in the filename:** only where it already appears — `{slug}-sketch.md` for the sketch *FidelityGuidance* node. Deeper fidelities share `{slug}-templates.{ext}` and rely on inline fidelity tags (`// Md`, frontmatter `artifact:`) until a domain splits files deliberately.

**Optional split (future):** `{slug}-{fidelity}-{format}.{ext}` when a domain outgrows one merged templates file — add map entries without renaming existing files.

### `templates` in instructions assembly


| Order | Practice `.instructions`                | Fidelity `.instructions`          | Not in `.instructions` |
| ----- | --------------------------------------- | --------------------------------- | ---------------------- |
| 1     | *ContextSection* assembly (context + guidance + rules + practice `templates[format]`) | *ContextSection* assembly for this fidelity scope | — |
| 2     | `fidelities.instructions` (each FG, sketch first) | — | — |
| —     | —                                       | —                                 | `examples` — `.examples` property only |


`load_template(format, fidelity)` → `fidelities[fidelity].templates[format]`.

### `examples` (separate from *ContextSection*)

`@markdown examples` → `.examples` on *Guidance* (`examples/` folder). **Not** in `practice.instructions` or any `instructions` assembly. Lifecycle `@agent_instructions` methods (`Generate`, `Validate`, …) pull `self.examples` in their `@agent_instructions` recipe when they need example prose.

## GuidanceCollection : Guidance

*GuidanceCollection* — Composite of *Guidance*. Keyed children. Content reads iterate and join except `rules`, which stays keyed by the same child keys.

- GuidanceCollection({key: Guidance, ...})

---

- entries: dict[str, Guidance]
// key = child name

---

- context / guidance / templates / instructions
// each iterates children and joins the same read
- rules: RulesCollection
// keyed like entries; each value is that child's RulesCollection — validate() batches every child
- **iter**()

## FidelityGuidance

*FidelityGuidance* extends *ContextSection* for one `## {name}` block. Sets `name`, `fidelity` (= `name`), `default_format`, and `context_guidance` (practice) on the base; same `@markdown` properties and `instructions` assembly. No `instructions` override. **`instructions`** — `@command` `@agent_instructions` at deploy; **`rules`** — `@rules` at deploy (same as practice).

| Property | Resolves to | In `fidelity.instructions` |
| -------- | ----------- | ------------------------------ |
| `context` | `## {name}` body + #68 prior `##` stack | yes — via `super.instructions` |
| `guidance` | `### Guidance` | yes |
| `rules` | `### Rules` | yes — `format_rules(rules)` |
| `templates[format]` | path map entry → file content (see naming table) | yes — active format at invoke; all declared formats at deploy per policy |

**RuleSpec** reads `practice.rules` then each `fidelity.rules` — same `@markdown` lists, not a second parse.

- FidelityGuidance(name, stage, default_format, context_guidance)

---

- stage: str
- context / guidance / rules / templates / format / default_format / name / context_guidance / fidelity
// inherited from ContextSection; fidelity = name; context_guidance = practice

---

*FidelityGuidance* has no lifecycle methods — `Generate` and `Satisfy` live in `actions/`. **Validate** lives on `Rule` / `RulesCollection`; the Validate action calls them.

---

# actions

Lifecycle orchestration — not on *Guidance* base class. Harness walk: `kind == instruction` (was `action`).

### Deploy

| Default | With mark |
| ------- | --------- |
| **Cursor command** (`ActionBody` + invoke tail) | `@skill` → skill file (rare) |
| | `@command(name="render")` → named command (e.g. `/render`) |
| | MCP mode (`install(mcp=True)`) → tail `Use MCP tool: {slug}.{action}` in skill/command body; `mcp.json` |

`generate` on a practice is usually **not** a separate deploy file — invoked via fidelity command or MCP tail in the command body when `mcp=True`. **Target:** per-method `@mcp` on agent-invokable entry points.

## Satisfy

**Today:** `Satisfy` calls `Validate` then `tool.generate_fixes_from_validate()`. **Target:** validate report → fix in Satisfy `@agent_instructions` body → re-validate until green. Remove `generate_fixes_from_validate` from practice class.

## Render

Convert generated content via `tool.render(format, content)` on practices that support channels. Channel iterate prose (e.g. Draw.io repair loop) lives in `actions/render/` — not on practice base.

## Iterate

Grill → segment → generate → validate → fix per tick for large artifacts (`actions/iterate/`).

```
actions/
├── generate / validate / satisfy / document
├── render
└── iterate
```

*Guidance* exposes `render()` only where a domain has programmatic channel code.

---

# actions/scan

*Rule* — parsed from `## Shared rules` / `### Rules` bullets in `{domain}.md`; carried on *Guidance* `.rules` as a `RulesCollection` via `@markdown`. `Rule.validate()` returns agentic instructions for the current context against that rule's body, and tells the agent to run the scanner when one exists. `RulesCollection` is the Composite: `validate()` walks every child and returns those instructions in one shot. The checker lives on the rule: `Rule.scanner` is **zero or one** `Scanner`, named by `slug`. `Scan` is `host.rules.scan`. `createRule` adds the bullet and, when wanted, the scanner script.

## Rule

- Rule(slug: str, body: str, fidelity: str | None = None)

---

- slug: str
// name of the scanner that implements this rule, when one exists
- body: str
// prose from md bullet — validate rubric + consequence clause
- fidelity: str | None
// None = shared; else fidelity name when parsed under ## {name}
- scanner: Scanner | None
// zero or one — go to the rule; None when `scanners/{slug}_scanner.py` is absent
- validate(): str
// agentic — evaluate the current context against this rule; run the scanner when one exists

## RulesCollection

- RulesCollection(entries: dict[str, Rule | RulesCollection])

---

- entries: dict[str, Rule | RulesCollection]
- validate(): str
// walk every child; ingest validate instructions in one shot
- scan(paths)
// each Rule.scanner.scan when present

## Scanner

- Scanner(rule: Rule) — runs that rule over files

## Scan

- Scan.bound_to(host)
- scan(paths) → host.rules.scan(paths)

# actions/validate

The **Validate** action is in this model because it is changing: default mode is every rule; you can pass one particular rule.

## Validate

- Validate()

---

- validate(tools, rule: Rule | None = None): str
// default — all rules: host.rules.validate(); pass one Rule for that rule only

---

# harness/agent_toolset

- **Purpose:** `Toolset`, `AgenticToolset(Toolset, Guidance)` — `tools`, `instructions_registry`, `mode`, manifest. Extends *Guidance* so `.instructions` is the **compound markdown doc** (assemble own markdown properties, then iterate registry members). `instructions_registry` holds `@agent_instructions` (was `actions`). Class name stays *AgenticToolset*.
- **Seam:** registration surface for MCP host and harness walk.
- **Dependencies:** `harness/agent_tools`, `harness/guidance` (Guidance)

## AgenticToolset

*AgenticToolset* — `Toolset` + `Guidance`. Registration plus compound-doc assembly: `.instructions` iterates `instructions_registry`. `Guidance` is *ContextSection* + *AgenticToolset* (today `BaseContextTool(AgenticToolset)`).

### What gets registered where

| Member kind | Decorator | Registry | In compound doc | Default IDE file | MCP (mcp mode) |
| ----------- | --------- | -------- | --------------- | ---------------- | --------------- |
| Host tool | `@agent_tool` | `tools` | **none** | **none** | `{slug}.{method}` |
| Lifecycle / orchestration | `@agent_instructions` | `instructions_registry` | instructions slice | **command** if unmarked | `{slug}.{method}` |
| Router guidance | `@skill` + `@agent_instructions` on `guidance()` | `instructions_registry` | instructions slice | **skill** | usually N/A |
| Utility entry | `@agent_instructions` only | `instructions_registry` | instructions slice | **command** (`UtilityBody`) | `{slug}.{method}` |
| Utility tool | `@agent_tool` only | `tools` | **none** | `{slug}.{method}` |

`@agent_tool` alone never writes a file — add `@skill` / `@command` or rely on MCP tail in a parent skill when `mcp=True`. **Invoke kind** (`operation_writes`): `@agent_tool` / `@sub_agent` → `invoke=tool`; `@agent_instructions` → `invoke=instruction`.

**Utilities** (`kind == utility`): `@agent_instructions` → command; `@agent_tool` only → MCP, no skill; `@command` overrides name (e.g. Catalog `generate-catalog`).

- `@agent_tool` / `@agent_instructions` → `tools` / `instructions_registry`; `.instructions` is the compound doc on *Guidance* (assemble + iterate)
- `mode`, `context_tool()` / `context_tools()` for lifecycle `@agent_instructions` methods
- Action body walk may reference `self.{label}` in recipes — resolves via normal `@markdown` property getters on *Guidance*, not a separate extract path in `harness/agent_toolset`
- `guidance()` → `return self.instructions` (thin — deploy and runtime share one assembly)

Utilities that are not practices may mixin `Guidance` with `instructions` assembled from one `@markdown` label.

---

# installation

- **Role:** *Deployment* — one deploy seam; *Harness* loads registry and calls `deployment.deploy(deployable)`.
- **Purpose:** **Extract and name what `Harness.install` already does** — same artifacts, same walks, same decorator stacks. The refactor is not new behavior; it moves deploy logic out of the monolithic *Harness* / MCP server entry so each mechanism is self-contained and subtype-driven.
- **Seam:** `Deployment`, `MarkdownInstallation`, `McpInstallation`, `HookInstallation`, `Deployable`, `Harness`, `McpServer`, `McpTool`, `McpPrompt`
- **Dependencies:** registry; `transport` (invoke tails). Stdio entry: `python -m installation.mcp` imports *McpServer* from `installation/mcp`.

## Maps to today (no behavior change)

| Target method | Today (`installation/`) | What it already does |
| ------------- | ----------------------------- | -------------------- |
| `Harness.install` | `Harness.install` | `registry.load()` → walk classes → `_generate_entry` per class → `_write_harness_files` / `_write_mcp_json` |
| `deploy(deployable)` | per-class `_generate_entry` | dispatch by registry kind — context tool vs bare toolset |
| `installPracticeGuidance` | `_generate_entry` when `kind == "context_tool"` | practice host then each fidelity — not the decorated-method pass |
| `deployGuidance` | marked members on the host | a skill, a command, or a rule per `@skill` / `@command` / `@rules` |
| `installFidelityGuidance` | marked members on the fidelity | a skill, a command, or a rule per `@skill` / `@command` / `@rules` |
| `deployAgenticToolset` | `operation_writes(cls)` loop inside `_generate_entry` | AST scan of class methods — **not** a walk of `instructions_registry` |
| `installAgentInstructions` | `operation_writes` row with `invoke == "action"` | method has `@agent_instructions`; file when `@skill` / `@command` / `@instruction` stacked |
| `installAgentTool` | `operation_writes` row with `invoke == "tool"` | method has `@agent_tool`; usually invoke tail only |
| `MarkdownInstallation.render` | `ContextToolBody` / `ActionBody` + `transport` | skill/command body + CLI fence or `render_mcp_invoke` tail |
| `McpInstallation.installAgentInstructions` / `installAgentTool` | `_write_mcp_json` contribution | record `@mcp` ops during the base walk; write manifest |
| `McpInstallation.bind` | `McpServer.start` → `McpToolset` getmembers rescan | server start only — enroll from ops already collected; **no second scan** |

**Read vs deploy:** `instructions_registry` assembles `.instructions` at **read** time. Deploy discovers operations by scanning the class (`operation_writes`) — same as today.

## Deployment

`deploy(deployable)` — pass the deployable **in**; write artifacts to disk; **no return** (product is on file). *Deployable* is anything in the registry.

| Deployable passed in | Calls |
| -------------------- | ----- |
| *PracticeGuidance* | `installPracticeGuidance(practice_guidance)` |
| *AgenticToolset* | `deployAgenticToolset(toolset)` |

**`installPracticeGuidance`** — guidance documents only (router + each fidelity). Action kits (`Generate`, `Satisfy`, `Validate`, `Scan`, utilities) are their own registry hosts and take `deployAgenticToolset` when `deploy` hits them.

1. `deployGuidance(practice_guidance)` — abstract
2. `installFidelityGuidance(fidelity)` per `practice_guidance.fidelities` — abstract

**`deployAgenticToolset`** — concrete walk (mirrors `operation_writes`):

1. For each `operation_writes(toolset)` row:
   - `invoke == "action"` (`@agent_instructions`) → `installAgentInstructions(toolset, operation)` — abstract
   - `invoke == "tool"` (`@agent_tool`) → `installAgentTool(toolset, operation)` — abstract

*MarkdownInstallation*, *McpInstallation*, *HookInstallation* implement the leaf writes. `installPracticeGuidance` / `deployAgenticToolset` stay on *Deployment* — subtypes do not re-walk the host.

## MarkdownInstallation : Installation

Same walk as base. Every markdown file is a skill, a command, or a rule — `@skill` / `@command` / `@rules` on the member. `relative_path` + `render` write that file. Replaces `_installer_writes` and today's `HarnessTool` subclasses.
- `transport` — `"cli"` \| `"mcp"`; when `"mcp"`, `render` appends the same `render_mcp_invoke` tail
- `relative_path(mark, section, member)` → Path
- `render(mark, section, member)` → str
- `mark(member)` → member — `@skill`, `@command`, `@rules`, `@instruction`

| Kind | Decorator | Writes (Cursor) |
| ---- | --------- | --------------- |
| skill | `@skill` | `.cursor/skills/{name}/SKILL.md` |
| command | `@command` | `.cursor/commands/{name}.md` (VS Code: `.github/prompts/…`) |
| rules | `@rules` | `.cursor/rules/{slug}.mdc` per `Rule` on `rules` property |
| instruction | `@instruction(name)` | named rule file on an operation |

## MCP mode (today)

**No `@mcp` decorator today.** MCP is a **Harness deploy flag**:

- `Harness.install(mcp: bool = False, …)`
  - `self._transport = "mcp"` when `mcp=True` else `"cli"`
  - transport passed into Skill / Command body generation (`ContextToolBody`, `ActionBody`, …)
  - when `transport == "mcp"`: body ends with `render_mcp_invoke` tail — `Use MCP tool: \`{slug}.{member}(…)\``
  - when `mcp=True` and Cursor: `_write_mcp_json` → `.cursor/mcp.json` stdio server
  - `@skill` still deploys `SKILL.md` — MCP tail is at the bottom of that markdown, not a separate file

| `mcp=False` (CLI) | `mcp=True` (MCP) |
| ----------------- | ---------------- |
| every `@skill` / `@command` / `@rules` / `@instruction` body ends with YAML fence + `.\tools.ps1 run -` | same files; body ends with `Use MCP tool: \`{slug}.{member}(…)\`` |
| no `mcp.json` | `.cursor/mcp.json` — stdio server → `python -m installation.mcp` |

**Example** — router skill `@stories` body (mcp mode):

```
# stories
…assembled instructions / guidance prose…
Determine which stories skill to run from context…
Use MCP tool: `stories.generate(format='', path='', session='')`
```

CLI mode (`mcp=False`) — same skill, bottom is YAML fence + `.\tools.ps1 run -` instead.

- `render_mcp_invoke(toolset_ref, member)` → str — `installation/transport.py`; used by `bodies._invoke_tail` when `transport=mcp`

**Today:** `McpServer.start` instantiates each toolset and enrolls members with `@mcp` — no second class rescan.

## MCP in target

**One walk on *McpInstallation*; two moments:**

| Moment | Method | Job |
| ------ | ------ | --- |
| Deploy | `deployAgenticToolset` / `installAgentInstructions` / `installAgentTool` | same `operation_writes` iteration as markdown deploy; write `mcp.json` slices; **record** `@mcp` rows in `mcp_operations` |
| Server start | `bind(server)` | open the collection of *McpInstallation* (one per toolset ref); enroll `McpTool` / `McpPrompt` from `mcp_operations` — **not** called from deploy |

| Part | Owner | Applies to |
| ---- | ----- | ---------- |
| **Invoke tail** | *MarkdownInstallation* `render(…, transport="mcp")` | `@skill`, `@command`, `@rules`, `@instruction` — agent-facing strings in files |
| **Manifest** | *McpInstallation* `deploy*` | `mcp.json`, which toolset refs to load |
| **Enrollment** | *McpInstallation* `bind` | `McpServer.start` — protocol handlers for recorded `@mcp` ops only |

`@mcp` stacks on the **operation**. No separate *McpToolset* adapter that re-iterates annotations — that logic lives on *McpInstallation* and is shared between deploy and bind.

**Today → target:** retire *McpToolset* as a parallel discovery type; keep *McpTool* / *McpPrompt* as thin protocol wrappers created inside `bind`.

## McpInstallation : Installation

Leaf writes only. `deployGuidance` / `installFidelityGuidance` / `installAgentInstructions` / `installAgentTool` record `@mcp` and write the manifest slice. Does not render markdown. **`bind(server)`** at server start enrolls from `mcp_operations` without rescanning the class. **Today** runtime enrolls all `@agent_tool` / `@agent_instructions` via *McpToolset*; **target** only `@mcp`-marked ops on *McpInstallation*.

## HookInstallation : Installation

Same walk as base. On *PracticeGuidance*: `deployGuidance` / `installFidelityGuidance` write hooks config. On *AgenticToolset*: `installAgentInstructions` writes hook skill files (`operation_writes` where `vehicle == "hook"`).

`@markdown` extract is **read-side** — co-located content injects at expand time; orthogonal to the invoke tail.

## Deployable

Protocol — host walked by `Harness.install()` for *Deployment*-marked members: *Guidance*, *FidelityGuidance*, bare *Guidance*, operations with decorator stacks.

## Harness

```
Harness.install(mcp=False)
  → registry.load()
  → for each Deployable: deployment.deploy(deployable)
  → merge mcp.json
```

`install` loads the registry and calls `deployment.deploy(deployable)`. The active `Deployment` subtype (usually *MarkdownInstallation*, sometimes composite with *McpInstallation*) implements the abstract section methods.

### What stays on Harness vs moves off

| Stays on Harness | Moves to host |
| ---------------- | ------------- |
| `install` — registry load, `deployment.deploy(deployable)` loop, `mcp.json` merge | `.instructions` on *Guidance* / *FidelityGuidance* |
| *McpServer* runtime — `start` calls `McpInstallation.bind` | `@markdown` extract + `instructions` @property assembly |
| | `ContextToolBody` / `compound_guidance` subprocess — **retire** |
| | `context_tool_rules` re-parse — **retire** (`deployGuidance` reads `.rules`) |

## McpServer

- start(toolset_refs: tuple[str, ...])
  → for each ref: *McpInstallation*(ref).bind(self) — **today:** `McpToolset(instance)` + getmembers rescan
- invoke_tool(mcp_name, arguments)
- invoke_prompt(mcp_name, arguments)

*McpTool* / *McpPrompt* — protocol wrappers created inside `McpInstallation.bind`; not a second annotation walk.

---

# tools/catalog_generator

- **Purpose:** Write catalog pages. `Catalog` extends `HTML` and reads each host’s `@markdown` properties via `Markdown.html()`.
- **Dependencies:** guidance registry — **not** `harness.bodies`, **not** heading scrape

## Catalog : HTML

- Catalog.from_registry()

---

- generate_catalog(out_root: Path)
-> for each Guidance: write page from @markdown properties as HTML
-> for each FidelityGuidance: write page from @markdown properties as HTML

---

## Migration notes


| Ticket          | Today                                                   | Target                                                                                      |
| --------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| #22             | `fidelities` dict on class                              | `**GuidanceCollection**` of *FidelityGuidance* (`stage` + `name` per entry)                 |
| fidelity lookup | `resolve_fidelity`, `STAGE_ALIASES`, `fidelity()` on CT | `**fidelities[name]**` (default) / `**fidelities.by(key_id, key)**` — per-`key_id` indexes |
| fidelity ops    | `_generate_fidelity_methods`, `_set_fidelity` on CT     | **Retire** — fidelity lookup on `GuidanceCollection`; `@agent_instructions` stay on *Guidance* |
| session         | `session_guidance` on CT                                | Workspace only                                                                              |
| satisfy hook    | `generate_fixes_from_validate` on CT                    | Satisfy action recipe + validate report                                                     |
| setup           | # Open prelude on `base_context_tool.md`                | Workspace + `GuidanceAction.begin`                                                         |
| render iterate  | implied on CT / base md                                 | `actions/render/` + channel action md                                                  |
| #68             | hyperlinks to other fidelities                          | prior `## {name}` blocks in `FidelityGuidance.context` per `GuidanceCollection` order       |
| #21             | catalog scrape + Harness overlap                        | `.instructions` on *Guidance*; `Catalog : HTML`; *Deployment* subtypes only write files |
| deploy          | `ContextToolBody`, `compound_guidance` in Harness       | `Deployment.installPracticeGuidance` / `deployAgenticToolset` + `MarkdownInstallation` implements abstract section methods |
| harness prose   | scattered Deployment model section                      | deploy rules on each class intro under Modules                                              |
| contexts        | `@instruction contexts` on CT                           | `@markdown context` on *ContextSection*; `instructions` @property assembles (was `_expand_instructions`) |
| md extractor    | `harness/markdown`, `@instruction`                   | `harness/markdown`, `@markdown` on extract properties                                    |
| md assembly     | `guidance()` AST + `compound_guidance` CLI              | `instructions` @property override on *Guidance* subclasses                                 |
| templates       | merged `templates/` + `filter_template_lines`           | `@markdown templates` → format → path map; subscript reads content (existing filenames) |
| rules parse     | `context_tool_rules.py` re-parses md at deploy          | `@markdown rules` → `RulesCollection` on *Guidance*; `Rule.scanner` zero or one; `Validate` defaults to all rules |
| section objects | implicit everywhere                                     | *ContextSection* — `context`, `guidance`, `rules`; each `@markdown` (`str` or `RulesCollection`) |
| inheritance     | `BaseContextTool(AgenticToolset)`                       | `Guidance(ContextSection, AgenticToolset)`, `FidelityGuidance(ContextSection)`       |
| #10             | `BaseContextTool` in `practices/base/`              | `Guidance` in `harness/guidance/` (`context_guidance.py`, `guidance.py`, …) |
| #19             | render channels on base                                 | `render()` hook on domain CT; iterate prose on Render/Iterate `@agent_instructions`         |
| MCP transport   | `install(mcp=True)` → `transport=mcp` on bodies + `mcp.json`; *McpToolset* rescan at start | `@mcp` on *McpInstallation*; `bind` enrolls recorded ops — no *McpToolset* rescan |


**Remove:** `catalog_generator.scrape_fidelities`, `CatalogFidelity` prose assembly → `Markdown.html()` / `Catalog : HTML`. `**compound_guidance`** subprocess for deploy → read `Guidance.instructions`. `**session_guidance`**, `**generate_fixes_from_validate`**, `**_generate_fidelity_methods**`, `**_set_fidelity**` from CT.

---

## Behavior sketch (BDD signatures)

**Canonical copy:** `context-tool-resource-model-om-bdd.md` — keep in sync when changing specs. Port each layer into the package that owns the subject (see the om-bdd port table).

**Notation:** `describe` / `that` / `with` / `it should` — never `when` for state. **Subject-first:** outer `describe` names the file, folder, or deploy tree under test — not internal class names. Object flows: `+` operation, `->` call, `<< triggered by >>` actor.

**Implementation order** (green each layer before the next; detail in `context-tool-resource-model-om-bdd.md`):

1. `Markdown` — extract as string or HTML; this class file directory only
2. `Guidance` — compound `instructions` (context + guidance + formatted rules + selected template)
3. `AgenticToolset` — read then deploy skill and command from the marks
4. `Guidance` — same `instructions`, then deploy skill and rules from the marks
5. `PracticeGuidance` — shared contexts read, then deploy skill and rules (no fidelity guidance yet)
6. `FidelityGuidance` — fidelity instructions read → `@command` deploy; then collection / practice assembly read → full tree (CLI fence when not `@mcp`; VS Code via `Harness` ide)
7. `McpInstallation`, `McpServer` — `mcp.json` when members are `@mcp`; then host invoke on layer 3–6 fixtures
8. `Catalog` — pages from each host `@markdown` property as HTML
9. `HookInstallation` — last; hook deploy not complete in harness today

Deploy outcomes shared across layers live in om-bdd **Deploy shared contexts** — each host layer adds delta `it_behaves_like` blocks only.

**Implementation:** isolate remodeled trees into `legacy-no-longer-valid/` first, then one om-bdd layer per `/turn`. Golden MCP deploy snapshot: `.cursor copy/` at repo root. Deploy tests use real `Harness.install` and compare output to that tree. See om-bdd § Implementation — one layer per turn.

Full specs → `context-tool-resource-model-om-bdd.md` (canonical).

---

# Object flows

Interaction traces — same notation as `context-tool-resource-model-om-bdd.md`. Full detail lives there; summary below.

### 0 — Compound doc (read)

+ `Guidance.instructions` — own markdown properties + iterate members
+ `AgenticToolset.instructions` — iterate `instructions_registry` (read-side; deploy uses `operation_writes`, not this walk)
+ `Markdown.html()` — `HTML.from_markdown(extract())`

### 1 — Instructions assembly (read)

+ `ContextSection.instructions` → context + guidance + format_rules(rules) + templates[format]
+ `GuidanceCollection.instructions` → join each child `.instructions` in declaration order
+ `Guidance.instructions` → super + fidelities

<< triggered by >> Agent, `MarkdownInstallation` render at deploy, action: guidance — same `@property` string, no subprocess

### 1b — `@markdown` extract

+ `ContextSection.{context,guidance,rules,templates}` → `Markdown.from_label` → extract → coerce

<< triggered by >> Scan — `practice.rules` / `fidelity.rules`
<< triggered by >> `MarkdownInstallation.deployGuidance` / `installFidelityGuidance` with `@rules`
<< triggered by >> `.instructions` assembly — rules via `format_rules`

### 2 — Fidelity lookup

<< triggered by >> Agent or invoke context with fidelity
	-> `practice.fidelities[name]` / `practice.fidelities.by("stage", stage)` → `fidelity.instructions`

### 3 — Catalog

+ `Catalog.generate_catalog` → each host `@markdown` property as HTML — never reads `.instructions`

### 4 — Deploy

+ `Harness.install` → `registry.load()` → `deployment.deploy(deployable)` per entry
	-> `installPracticeGuidance` — `deployGuidance` + `installFidelityGuidance` × n
	-> `deployAgenticToolset` for each action kit / utility `AgenticToolset`
	-> `MarkdownInstallation` — skills, commands, rules, invoke tails
	-> `McpInstallation` — record `@mcp` ops, merge `mcp.json` (no `bind` during deploy)

### 5 — MCP server start

+ `McpServer.start(refs)` → `McpInstallation(ref).bind(server)` per ref — enroll from `mcp_operations`, no class rescan

### 6 — MCP invoke

<< triggered by >> Agent reads invoke tail or `tools/call`
	-> `McpServer.invoke_tool` / `invoke_prompt`

### 7 — Runtime guidance

+ `AgenticToolset.guidance()` → `self.instructions`

---

## Open questions

1. **Catalog page shell** — does `Catalog` wrap each `Markdown.html()` fragment in a site template, or is the fragment the page?
2. **Utilities** — `Guidance` with `instructions` only; HTML only when a `@markdown` property is read as HTML?
3. **Fidelity artifact** — per-fidelity **command** (today) vs **skill** (extended mode) — policy on `FidelityGuidance` or deploy flag?
4. **operation_writes** — keep AST walk in Harness or move write-vehicle metadata onto `AgenticToolset` manifest?
5. **Cross-tool guidance** — a practice calling a companion's `guidance()` with `mode=tool`: stay in `@agent_instructions` recipe only, or split into deploy-time `.instructions` vs runtime companion defer?

