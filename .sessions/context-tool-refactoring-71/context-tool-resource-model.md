# Guidance resource model (proposed remodel)

**Sources / context:** `.sessions/context-tool-refactoring-71/session.md` (#71, #22, #68, #21); today `context_tools/base/base_context_tool.py` (`BaseContextTool`) → target `context_tools/context_guidance/` (*Guidance*, *ContextGuidance*, …); `primitives/harness/`; `utilities/catalog_generator/`. **Out of scope for this pass:** full `document` channel implementation (ticket #19 partial). **In scope in model:** where `render` / `iterate` live relative to *ContextGuidance* vs lifecycle action kits.

**Three roles — do not collapse them:**

| Role | Who | Job |
| ---- | --- | --- |
| **Reading** | *Guidance* / *ContextGuidance* / *AgenticToolset* | `@markdown`, `.instructions`, `.catalog`, `@agent_tool`, `@agent_instructions` — assemble and return content when asked |
| **Deploy** | **`Deployment.deploy(deployable)`** | dispatch: context tool → `deployContextTool`; toolset → `deployToolset` |
| **Mechanism** | **subtypes** | *MarkdownDeployment*, *McpDeployment*, *HookDeployment* extend *Deployment* and **implement** abstract `deployContextSection`, `deployContextSectionFidelity`, `deployAgentInstructions`, `deployAgentTool`, … |

Runtime invoke and deploy use the same read side: channel calls `.instructions` on the *ContextGuidance* / *FidelityGuidance* passed in; agent calls `guidance()` → same string.

**Layers (not alternatives):**

```
primitives/markdown          read — @markdown extract
context_tools/context_guidance   read — ContextSection.instructions + overrides
primitives/agent_toolset     read — @agent_instructions recipes, @agent_tool
primitives/harness           Deployment.deploy(deployable) — MarkdownDeployment, McpDeployment, HookDeployment, Harness
```

Also: MCP/CLI `context:` block = invoke args (fidelity, path, session) — not the `context` `@markdown` property on *ContextSection*. `**.guidance`** on *ContextSection* = `@markdown` property reading the `## Guidance` / `### Guidance` section — not informal "guidance" prose.

**Deploy:** rules live in the class intro that owns them — under **Modules** below (`AgenticToolset`, `ContextGuidance`, `Harness`, …). No separate deployment chapter.

---

## Modules

**Design stance:** `**Guidance` has `instructions` and `catalog`** — read seams. `deploy` and agents **read** them; Harness does not build them. `**catalog`** is for `catalog_generator` only.

Build order: `primitives/markdown` → `context_tools/context_guidance` → `primitives/agent_toolset` → `primitives/harness` → `catalog_generator`

**One read path:** runtime `guidance()`, deploy channels, and catalog all call `.instructions` / `.catalog` on the host — no `compound_guidance` subprocess in Harness.

**Three modules — do not merge them:**

```
primitives/markdown         Guidance (context_tools/context_guidance)        AgenticToolset (primitives/agent_toolset)
─────────────────────       ─────────────────────────────        ────────────────────────────────
@markdown per extract property       instructions @property → assemble    @agent_instructions → action recipe
Markdown.extract()       catalog @property → human page       @agent_tool → tools dict
@markdown on ContextSection  context, guidance, rules (`list[Rule]` for rules)   Deployment (@skill @prompt @instruction @hook @mcp …) on primitives/harness
```

Extract and assemble are sequential — `@markdown` does not compete with `instructions`. `primitives/markdown` does not import `primitives/agent_toolset`.

---

# primitives/markdown

*Markdown* (`primitives/markdown`) — `@markdown` decorator + `Markdown` value object. Extraction only — not assembly. Today: `primitives/instructions` + `@instruction` → rename on refactor.

- **Dependencies:** `primitives/assets` (`AssetLocator`). No `primitives/agent_toolset`.

## Markdown

**`@markdown`** decorates each host property that reads co-located md. Property name = label. `Markdown` always resolves from **`host.context_guidance.module_dir`** (the practice — self on *ContextGuidance*, parent on *FidelityGuidance*); `host.name` scopes fidelity sections:

1. `{label}/` folder — merge files
2. `{label}.md` file
3. `## {Label}` (or `###` under fidelity scope) in `{slug}.md`

Return type on the property selects coercion: `str` → extracted text; `list[Rule]` → parse rules-section bullets into `list[Rule]`; `dict[str, str]` → scan `templates/` into **format key → relative path** (same scan rules as today's `AssetLocator` for the `templates` label).

```python
@markdown
def context(self) -> str: ...

@markdown
def guidance(self) -> str: ...

@markdown
def rules(self) -> list[Rule]: ...

@markdown
def templates(self) -> dict[str, str]: ...   # format → path under module_dir

@markdown
def examples(self) -> str: ...                # ContextGuidance only — not in instructions
```

`templates[format]` subscripts the map and **reads file content** at that path (with fidelity line-filter on *FidelityGuidance* — today's `filter_template_lines`).

- @markdown
// decorator — getter → Markdown.from_label(owner, label).extract() → coerce to property return type
- from_label(host, label): Markdown
- extract(): str
- coerce(text: str, return_type): str | list[Rule] | dict[str, str]
// dict[str, str] — format key → relative path; subscript loads content

**Label paths:** `context` → `# Contexts` section for this host's scope; `guidance` / `rules` → practice `## …` before `## Fidelities`; fidelity `### …` under `## Fidelities` → `## {name}`; `examples` → `examples/` folder; `templates` → `templates/` folder scan → path map.

**Host requirement:** `context_guidance` on every *ContextSection* — `@markdown` uses `context_guidance.module_dir`. `name` scopes extract (`None` practice-wide; fidelity name under `## Fidelities` → `## {name}` in `{slug}.md`; #68 prior `##` stack in `context`). `fidelity: str | None` on the base — equals `name` on *FidelityGuidance*; active domain key on *ContextGuidance* at invoke.

---

+ host.{label}
<< triggered by >> any caller (`self.context`, `instructions` assembly, tests, …)
	-> Markdown.from_label(host, label)
	-> Markdown.extract()
	-> Markdown.coerce(return_type)   // str | list[Rule] | dict[str, str] (templates path map)
<< uses >> AssetLocator
	-> AssetLocator.locate(owner.module_dir, label)
	// folder → file → section in {slug}.md; templates/ → format → path map
	-> str | list[Rule] | dict[str, str]

---

# context_tools/context_guidance

- **Dependencies (one-way):** `primitives/markdown`, `primitives/assets`, `workspace`, `context_tools/agent_toolset/scan` (`Rule`)

## Guidance

*Guidance* — abstract base. **`instructions`** and **`catalog`** are the two public seams — each a **compound doc** assembled on read, not a registry.

### Compound doc

*AgenticToolset* extends *Guidance* because toolsets **return instructions** (and catalog pages): deploy, MCP, and `guidance()` read assembled documents from the host.

Same assembly shape for both seams:

1. **Own markdown properties** — subclass content first (*ContextSection*: `@markdown` joins; bare *AgenticToolset*: module/operation prose).
2. **Iterate members** — stable order over registered operations; append each slice.
   - **`instructions`** (`str`, markdown) — per `@agent_instructions` in the **instructions registry** (was `actions`).
   - **`catalog`** (`str`, HTML) — per `tools` entry and per instructions-registry entry that exposes catalog.

Replaces `compound_guidance` subprocess (deploy) and catalog AST scrape. Harness copies `.instructions`; `catalog_generator` copies `.catalog`.

**`catalog`** is not derived from `instructions` — parallel compound doc, same iteration pattern, different format.

### Type hierarchy

```
Toolset
└── AgenticToolset              extends Guidance — compound instructions + compound catalog from registry iteration

Guidance
└── ContextSection              @markdown properties → compound instructions doc
    ├── ContextGuidance         also AgenticToolset; instructions = ContextSection + fidelities compound docs
    └── FidelityGuidance        `context_guidance` = practice; `fidelity` = `name` — no instructions override
```

*ContextSection* is the common base for both *ContextGuidance* and *FidelityGuidance*. Each declares the same four `@markdown` extract properties (`context`, `guidance`, `rules`, `templates`), plus `format`, `default_format`, `name`, `context_guidance`, and `fidelity`; `instructions` on *ContextSection* joins them with the same logic on every host. `@markdown` always uses `context_guidance.module_dir`. `name` scopes section extract. `fidelity` equals `name` on *FidelityGuidance*; on *ContextGuidance* at invoke holds the active domain key (`None` practice-wide). Node lookup: `fidelities[practice.fidelity]` (default `"name"` key). *FidelityGuidance* does not override `instructions`. *ContextGuidance* overrides `instructions` to append `fidelities.instructions`.

**`rules`** are `list[Rule]` (`context_tools/agent_toolset/scan`) — `@markdown` coerces the rules section; each `Rule.slug` matches a `Scanner(rule)` — **and** `format_rules(rules)` inlines them into `instructions`. Same objects for scan, validate, deploy, and prose.

**Not in `instructions`:** `@markdown examples` on *ContextGuidance* only.

### What `instructions` and `catalog` are (and what they are not)


|                | `**instructions**`                                                                                                                                                                                                                                                                                                                             | `**catalog**`                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Audience**   | Agent (IDE skill, command body, `action: guidance`, MCP expand)                                                                                                                                                                                                                                                                                | Human (CDD catalog site)                                                                               |
| **Shape**      | `@property` → `str` (markdown)                                                                                                                                                                                                                                                                                                                 | `@property` → `str` (HTML or page markdown)                                                            |
| **Built from** | **Compound instructions doc:** own markdown properties + iterate members. *ContextSection*: `@markdown` joins. *AgenticToolset*: instructions registry. *ContextGuidance*: super + `fidelities.instructions`. **`examples` excluded** | **Compound catalog doc:** own catalog properties + iterate `tools` and instructions registry → HTML; **not** from `instructions` markdown |
| **Consumers**  | Harness deploy, runtime `guidance()` → `return self.instructions`                                                                                                                                                                                                                                                                              | `catalog_generator` only                                                                               |
| **Not**        | Catalog pages, `examples/` folder                                                                                                                                                                                                                                                                                                                    | Agent skills, generate/validate recipes                                                                |


Override `**instructions**` on *ContextGuidance* only — *FidelityGuidance* uses *ContextSection* assembly unchanged. Do not put assembly on `@markdown` extract labels. Runtime-only orchestration (e.g. a practice calling a companion's `guidance()` with `mode=tool`) stays on `**@agent_instructions guidance()**` and is **not** part of deploy `instructions`.

- Guidance()
// Abstract base — instructions @property; catalog @property; does not subclass Toolset

---

- instructions: str
// @property — abstract; subclasses override
- catalog: str
// @property — subclass override; never from instructions

### Instructions assembly (today → target)


| Path        | When                            | Mechanism                                                                |
| ----------- | ------------------------------- | ------------------------------------------------------------------------ |
| **Runtime** | `action: guidance` / `generate` | `guidance()` → `self.instructions`; action recipes that mention `self.examples` hit the `@markdown` getter like any other caller |
| **Deploy**  | Harness writes skills/commands  | today: `compound_guidance` subprocess — **target:** read `.instructions` |


**Today `guidance()` on `BaseContextTool`** — method body is a recipe; `primitives/agent_toolset/action.py` walks the AST (`self.contexts`, `super().guidance()`, companion deferrals). **Target:** `return self.instructions`.


| Today                                         | Moves to                                              |
| --------------------------------------------- | ----------------------------------------------------- |
| Assembly in `BaseContextTool.guidance()` body | `ContextGuidance.instructions` @property override     |
| Merged `templates/` + `filter_template_lines` | `@markdown templates` → `dict[str, str]` path map; `templates[format]` reads content + fidelity filter |
| Prior-depth stack (#68)                       | `FidelityGuidance.context` — prior `## {name}` blocks in declaration order |
| `compound_guidance` subprocess                | Harness reads `fidelity.instructions`                 |
| `ContextToolBody` assembly                    | *Deployment* on `instructions` / `rules` — `@skill`, `@prompt`, `@rules` |


**Practice vs fidelity `.instructions`:** *ContextGuidance* — `super.instructions` (practice-wide extract) + `fidelities.instructions` (each *FidelityGuidance* joined in declaration order). Each *FidelityGuidance* — same *ContextSection* `instructions` property; `name` scopes `@markdown` extract (`context` includes #68 prior `##` stack). **`examples`** — read via `.examples` when an action recipe asks; never merged into `.instructions`.

Assembly interactions — **Behavior sketch (BDD)** object flows.

## ContextSection

*ContextSection* extends *Guidance* — common base for *ContextGuidance* and *FidelityGuidance*. Four `@markdown` extract properties plus `format`; `instructions` joins them with the same logic on every host.

| Property | Role | `@markdown` return |
| -------- | ---- | ------------------ |
| `context` | Scoped `# Contexts` section — like today's `contexts` `@instruction` | `str` |
| `guidance` | `## Guidance` on *ContextGuidance*; `### Guidance` under `## Fidelities` → `## {name}` on *FidelityGuidance* | `str` |
| `rules` | `## Shared rules` on *ContextGuidance*; `### Rules` under each fidelity `## {name}` | `list[Rule]` |
| `templates` | Scan `templates/` for this host scope — practice-wide on *ContextGuidance*; fidelity subset on *FidelityGuidance* | `dict[str, str]` |
| `format` | Active format for `templates[format]` in `instructions` | — |
| `default_format` | Fallback when `format` unset; invoke copies to `format` on the active host | — |
| `name` | `None` on practice-wide *ContextGuidance*; fidelity domain name on *FidelityGuidance* — scopes `@markdown` extract | — |
| `context_guidance` | Practice host — `self` on *ContextGuidance*; parent on *FidelityGuidance*; `@markdown` `module_dir` always from here | — |
| `fidelity` | Domain fidelity key — equals `name` on *FidelityGuidance*; active key on *ContextGuidance* at invoke; `None` practice-wide | — |

`ContextSection.instructions` → `context` + `guidance` + `format_rules(rules)` + `templates[format]`.

**Contexts file layout** (`bdd.md`, `# Contexts` chapter):

```
# Contexts
preamble before first ##     → ContextGuidance.context
## Guidance                  → ContextGuidance.guidance
## Shared rules              → ContextGuidance.rules

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
- catalog: str
- context: str
// @markdown — # Contexts section for this host's scope
- guidance: str
// @markdown
- rules: list[Rule]
// @markdown — coerce bullets → list[Rule]
- templates: dict[str, str]
// @markdown — format key → relative path; templates[format] reads content
- format: str
// active format for templates[format] in instructions assembly
- default_format: str
// fallback when format unset; invoke copies to format on active host
- name: str | None
// scopes @markdown extract; None = practice-wide on ContextGuidance
- context_guidance: ContextGuidance
// @markdown module_dir always from here
- fidelity: str | None
// equals name on FidelityGuidance; active domain key on ContextGuidance at invoke
- format_rules(rules: list[Rule]): str

## ContextGuidance

*ContextGuidance* extends *ContextSection* + *AgenticToolset* at practice scope (Stories, Bdd, Clean Engineering, …). Practice-wide `context` / `guidance` / `rules` / `templates` come from the top of `# Contexts` and practice `templates/` scan. `**fidelities: GuidanceCollection`** — map of *FidelityGuidance* nodes (#22). Lookup: `**fidelities[name]`** (default `"name"` key) or `**fidelities.by(key_id, key)`** for other indexes (`"stage"`, …).

### `instructions` assembly (practice level)

*ContextGuidance* **overrides** `instructions`:

1. `super.instructions` — practice `context` + `guidance` + `format_rules(rules)` + practice `templates[format]`
2. `fidelities.instructions` — each *FidelityGuidance*.`instructions` in declaration order (sketch first)

**Rules as list:** `practice.rules` and each `fidelity.rules` are `list[Rule]` — passed to `Scan` / `ScannerCollection.get(rule.slug)`, validate, and `RuleSpec` deploy. **Same list** formatted into `instructions` via `format_rules`.

### Deploy

Harness does **not** build guidance prose. Deploy runs *Deployment* on declared members — same path for practice, fidelity, utilities, and lifecycle operations.

| Member | Host | Read | Deploy |
| ------ | ---- | ---- | ------ |
| `instructions` | *ContextGuidance* | `@markdown` assembly + `@property` | `@skill` `@agent_instructions` → router skill; `guidance()` → `self.instructions` |
| `rules` | *ContextGuidance* | `@markdown` → `list[Rule]` | `@rules` → one `.cursor/rules/{slug}.mdc` per `Rule` |
| `instructions` | *FidelityGuidance* | `@markdown` assembly + `@property` | `@prompt` `@agent_instructions` → fidelity command |
| `rules` | *FidelityGuidance* | `@markdown` → `list[Rule]` | `@rules` → one rule file per `Rule.slug` |

**Naming:** `@rules` on the `rules` property — not `@instruction` (that is a **named** rule file on an **operation**) and not `@instructions` (collides with `instructions`). `Deployment.deployContextTool` walks sections; *MarkdownDeployment* **implements** `deployContextSection` / `deployContextSectionFidelity` / `deployAgentInstructions` / `deployAgentTool`.

```
ContextGuidance                   # ContextSection + AgenticToolset
├── context / guidance / rules    # @markdown — practice-wide top of # Contexts
├── .instructions / .catalog
├── templates                     # @markdown on ContextSection — practice templates/ scan
├── .examples                     # @markdown — not in practice.instructions
└── fidelities: GuidanceCollection
    └── FidelityGuidance × n      # ContextSection per ## {name}
```

- ContextGuidance(format, path, session, workspace)

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
- catalog: str

### Slim-down (retire from `BaseContextTool`)

*ContextGuidance* holds `instructions`, `catalog`, `context`/`guidance`/`rules`, `fidelities`, `templates[format]`, workspace/scanner — not session prose, fidelity method synthesis, satisfy hooks, or render iteration loops.


| Today on CT                                            | Target                                                                |
| ------------------------------------------------------ | --------------------------------------------------------------------- |
| `session_guidance()`                                   | **Workspace** only                                                    |
| `fidelities` dict, `STAGE_ALIASES`, `resolve_fidelity` | `GuidanceCollection([...])` + `fidelities[name]` / `fidelities.by(key_id, key)` |
| `_generate_fidelity_methods()`                         | **Retire** — `Generate` / `Validate` / `Satisfy` stay independent `@agent_instructions` on *ContextGuidance* |
| `_set_fidelity`                                        | **Retire** — invoke sets `practice.fidelity` via `fidelities[...]` / `by("stage", ...)` and copies `fidelities[practice.fidelity].default_format` → `format` |
| `generate_fixes_from_validate()`                       | **Retire** — Satisfy action recipe                                    |
| # Open prelude on base md                              | Workspace + `LifecycleAction.begin`                                   |
| Render iterate loops on CT                             | `context_tools/agent_toolset/render/`                                       |


**Keep on domain practice:**


| Member                    | Role                                              |
| ------------------------- | ------------------------------------------------- |
| `generate_output()`       | Domain body for **Generate** action               |
| `render(format, content)` | Channel transform when supported                  |
| `@markdown` labels        | `context`, `guidance`, `rules`; `examples`; `scaffold` lifecycle-only |
| `templates`               | `@markdown` → `dict[str, str]` (format → path); `templates[format]` reads content |
| `load_template`           | `@agent_tool` — `fidelities[fidelity].templates[format]` |


### `templates` — `@markdown` on *ContextSection*

`templates` is declared on *ContextSection* — both *ContextGuidance* and *FidelityGuidance* inherit it. `@markdown` scans `templates/` (same rules as today's `AssetLocator` + `_path_for_templates`) and coerces to **`dict[str, str]`**: canonical **format key → relative path** under `module_dir`. Subscript `templates[format]` loads file content at that path.

**Format keys** — canonical names from `supported_formats` / host `format` (`markdown`, `python`, `typescript`, `java`, …). Folder aliases (`md`, `py`, `ts`) map to those keys when building the dict.

**Host scope:**

| Host | Map includes |
| ---- | ------------ |
| *ContextGuidance* | All produce files / format packs under `templates/` for this practice |
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

`@markdown examples` → `.examples` on *ContextGuidance* (`examples/` folder). **Not** in `practice.instructions` or any `instructions` assembly. Lifecycle `@agent_instructions` methods (`Generate`, `Validate`, …) pull `self.examples` in their `@agent_instructions` recipe when they need example prose.

## GuidanceCollection

*GuidanceCollection* — collection owned by *ContextGuidance*. Declared with `**GuidanceCollection([...])`** list syntax — **sketch `FidelityGuidance` first**. At construction builds per-`key_id` indexes over entries. **Default key:** `"name"` — `**fidelities[name]`** / `**getitem(name)**` use the name index. Other keys: `**fidelities.by(key_id, key)`**. Replaces today's `fidelities` dict + `STAGE_ALIASES` + `resolve_fidelity`.

| `key_id` | Index key | Access |
| -------- | --------- | ------ |
| `"name"` *(default)* | `FidelityGuidance.name` | `fidelities["behavior"]` |
| `"stage"` | `FidelityGuidance.stage` | `fidelities.by("stage", "specification")` — aliases normalized in stage index |

### CDD stage vs domain name

```python
# Bdd target
fidelities = GuidanceCollection([
    FidelityGuidance("sketch", stage="sketch", ...),   # templates["markdown"] → templates/bdd-sketch.md
    FidelityGuidance("modules", stage="discovery", ...),
    FidelityGuidance("behavior", stage="spec", ...),
    FidelityGuidance("development", stage="engineer", ...),
])
practice.fidelities.by("stage", "sketch")
practice.fidelities["behavior"]                      # default name key — same as by("stage", "specification")
```

**Sketch fidelity:** shallowest node — `stage="sketch"` (`ContextGuidance.SKETCH`); first in `GuidanceCollection([...])`. Not lifecycle `scaffold`. Deploy: `{slug}-{name}` (e.g. `bdd-sketch`).

- GuidanceCollection([...entries: FidelityGuidance])

---

- << association >> parent: ContextGuidance
- entries: tuple[FidelityGuidance, ...]
- indexes: dict[str, dict[str, FidelityGuidance]]
// key_id → key → entry — built at construction

---

- **getitem**(name: str): FidelityGuidance
// default key "name" — fidelities["behavior"]
- **by**(key_id: str, key: str): FidelityGuidance
// non-default keys — select index for key_id; lookup key in that index
- instructions: str
// @property — join each entry.instructions in declaration order
- names(): list[str]
- **iter**()

## FidelityGuidance

*FidelityGuidance* extends *ContextSection* for one `## {name}` block. Sets `name`, `fidelity` (= `name`), `default_format`, and `context_guidance` (practice) on the base; same `@markdown` properties and `instructions` assembly. No `instructions` override. **`instructions`** — `@prompt` `@agent_instructions` at deploy; **`rules`** — `@rules` at deploy (same as practice).

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

- catalog: str
// @property override — stacks prior fidelity catalog sections (#68)

*FidelityGuidance* has no lifecycle methods — `Generate`, `Validate`, `Satisfy`, and the rest live in `context_tools/agent_toolset/` as independent `@agent_instructions` on *ContextGuidance* (*AgenticToolset*).

---

# context_tools/agent_toolset

Lifecycle orchestration — not on *ContextGuidance* base class. Harness walk: `kind == instruction` (was `action`).

### Deploy

| Default | With mark |
| ------- | --------- |
| **Cursor command** (`ActionBody` + invoke tail) | `@skill` → skill file (rare) |
| | `@prompt(name="render")` → named command (e.g. `/render`) |
| | MCP mode (`write_deploy(mcp=True)`) → tail `Use MCP tool: {slug}.{action}` in skill/command body; `mcp.json` |

`generate` on a practice is usually **not** a separate deploy file — invoked via fidelity command or MCP tail in the command body when `mcp=True`. **Target:** per-method `@mcp` on agent-invokable entry points.

## Satisfy

**Today:** `Satisfy` calls `Validate` then `tool.generate_fixes_from_validate()`. **Target:** validate report → fix in Satisfy `@agent_instructions` body → re-validate until green. Remove `generate_fixes_from_validate` from practice class.

## Render

Convert generated content via `tool.render(format, content)` on practices that support channels. Channel iterate prose (e.g. Draw.io repair loop) lives in `context_tools/agent_toolset/render/` — not on practice base.

## Iterate

Grill → segment → generate → validate → fix per tick for large artifacts (`context_tools/agent_toolset/iterate/`).

```
context_tools/agent_toolset/
├── generate / validate / satisfy / document
├── render
└── iterate
```

*ContextGuidance* exposes `render()` only where a domain has programmatic channel code.

---

# context_tools/agent_toolset/scan

*Rule* — already in the scan kit. One rule slug, one `Scanner` subclass in the host's `scanners/` folder. Parsed from `## Shared rules` / `### Rules` bullets in `{domain}.md`; carried on *ContextSection* `.rules` as `list[Rule]` via `@markdown`.

## Rule

- Rule(slug: str, body: str, fidelity: str | None = None)

---

- slug: str
// same string passed to Scanner(slug) and ScannerCollection.get(slug)
- body: str
// prose from md bullet — validate rubric + consequence clause
- fidelity: str | None
// None = shared; else fidelity name when parsed under ## {name}

**Association:** `ContextGuidance._scanner_collection()` discovers `scanners/*_scanner.py`; each discovered slug must have a matching `Rule` in `practice.rules` or fidelity `rules` when declared in md. `createRule` adds both the bullet and the scanner script — one `Rule`, two surfaces (md + code).

## Scanner / ScannerCollection

- Scanner(rule: str) — runs one slug over files
- ScannerCollection.discover() → dict[slug, type[Scanner]]
- Scan.bound_to(host) — uses host._scanner_collection()

---

# primitives/agent_toolset

- **Purpose:** `Toolset`, `AgenticToolset(Toolset, Guidance)` — `tools`, `instructions_registry`, `mode`, manifest. Extends *Guidance* so `.instructions` / `.catalog` are **compound docs** (assemble own markdown or catalog properties, then iterate registry members). `instructions_registry` holds `@agent_instructions` (was `actions`). `.instructions` `str` @property is the compound markdown doc. Class name stays *AgenticToolset*.
- **Seam:** registration surface for MCP host and harness walk.
- **Dependencies:** `primitives/tools`, `context_tools/context_guidance` (Guidance)

## AgenticToolset

*AgenticToolset* — `Toolset` + `Guidance`. Registration plus compound-doc assembly: `.instructions` iterates `instructions_registry`; `.catalog` iterates `tools` and registry for HTML. `ContextGuidance` is *ContextSection* + *AgenticToolset* (today `BaseContextTool(AgenticToolset)`).

### What gets registered where

| Member kind | Decorator | Registry | In compound doc | Default IDE file | MCP (mcp mode) |
| ----------- | --------- | -------- | --------------- | ---------------- | --------------- |
| Host tool | `@agent_tool` | `tools` | catalog slice | **none** | `{slug}.{method}` |
| Lifecycle / orchestration | `@agent_instructions` | `instructions_registry` | instructions slice | **command** / prompt if unmarked | `{slug}.{method}` |
| Router guidance | `@skill` + `@agent_instructions` on `guidance()` | `instructions_registry` | instructions slice | **skill** | usually N/A |
| Utility entry | `@agent_instructions` only | `instructions_registry` | instructions slice | **command** (`UtilityBody`) | `{slug}.{method}` |
| Utility tool | `@agent_tool` only | `tools` | **none** | `{slug}.{method}` |

`@agent_tool` alone never writes a file — add `@skill` / `@prompt` or rely on MCP tail in a parent skill when `mcp=True`. **Invoke kind** (`operation_writes`): `@agent_tool` / `@sub_agent` → `invoke=tool`; `@agent_instructions` → `invoke=instruction`.

**Utilities** (`kind == utility`): `@agent_instructions` → command; `@agent_tool` only → MCP, no skill; `@prompt` overrides name (e.g. Catalog `generate-catalog`).

- `@agent_tool` / `@agent_instructions` → `tools` / `instructions_registry`; `.instructions` / `.catalog` are compound docs on *Guidance* (assemble + iterate)
- `mode`, `context_tool()` / `context_tools()` for lifecycle `@agent_instructions` methods
- Action body walk may reference `self.{label}` in recipes — resolves via normal `@markdown` property getters on *Guidance*, not a separate extract path in `primitives/agent_toolset`
- `guidance()` → `return self.instructions` (thin — deploy and runtime share one assembly)

Utilities that are not practices may mixin `Guidance` with `instructions` assembled from one `@markdown` label.

---

# primitives/harness

- **Role:** *Deployment* — one deploy seam; *Harness* loads registry and calls `deployment.deploy(deployable)`.
- **Purpose:** **Extract and name what `Harness.write_deploy` already does** — same artifacts, same walks, same decorator stacks. The refactor is not new behavior; it moves deploy logic out of the monolithic *Harness* / MCP server entry so each mechanism is self-contained and subtype-driven.
- **Seam:** `Deployment`, `MarkdownDeployment`, `McpDeployment`, `HookDeployment`, `Deployable`, `Harness`, `McpServer`, `McpTool`, `McpPrompt`
- **Dependencies:** registry; `transport` (invoke tails). Stdio entry: `utilities/mcp_server/__main__.py` imports *McpServer* from here.

## Maps to today (no behavior change)

| Target method | Today (`primitives/harness/`) | What it already does |
| ------------- | ----------------------------- | -------------------- |
| `Harness.write_deploy` | `Harness.write_deploy` | `registry.load()` → walk classes → `_generate_entry` per class → `_write_harness_files` / `_write_mcp_json` |
| `deploy(deployable)` | per-class `_generate_entry` | dispatch by registry kind — context tool vs bare toolset |
| `deployContextTool` | `_generate_entry` when `kind == "context_tool"` | router skill + fidelity prompts + decorated-method pass |
| `deployContextSection` | `_emit("skill")` for practice + `_write_context_tool_mdcs` / rules | router `.cursor/skills/{slug}/SKILL.md`; one `.mdc` per `Rule` |
| `deployContextSectionFidelity` | fidelity loop → `_emit("prompt")` | `.cursor/commands/{slug}-{fidelity}.md` per fidelity |
| `deployToolset` | `operation_writes(cls)` loop inside `_generate_entry` | AST scan of class methods — **not** a walk of `instructions_registry` |
| `deployAgentInstructions` | `operation_writes` row with `invoke == "action"` | method has `@agent_instructions`; file when `@skill` / `@prompt` / `@instruction` stacked |
| `deployAgentTool` | `operation_writes` row with `invoke == "tool"` | method has `@agent_tool`; usually invoke tail only |
| `MarkdownDeployment.render` | `ContextToolBody` / `ActionBody` + `transport` | skill/command body + CLI fence or `render_mcp_invoke` tail |
| `McpDeployment.deployToolset` | `_write_mcp_json` contribution | same `operation_writes` walk; records `@mcp` ops; writes manifest |
| `McpDeployment.bind` | `McpServer.start` → `McpToolset` getmembers rescan | server start only — enroll from ops already collected; **no second scan** |

**Read vs deploy:** `instructions_registry` assembles `.instructions` at **read** time. Deploy discovers operations by scanning the class (`operation_writes`) — same as today.

## Deployment

`deploy(deployable)` — pass the deployable **in**; write artifacts to disk; **no return** (product is on file). *Deployable* is anything in the registry.

| Deployable passed in | Calls |
| -------------------- | ----- |
| *ContextGuidance* | `deployContextTool(context_guidance)` |
| *AgenticToolset* | `deployToolset(toolset)` |

**`deployContextTool`** — concrete walk on *Deployment* base (mirrors `_generate_entry` for context tools):

1. `deployContextSection(context_guidance)` — abstract
2. `deployContextSectionFidelity(fidelity)` per `context_guidance.fidelities` — abstract
3. `deployToolset(context_guidance)` — context tools are also toolsets

**`deployToolset`** — concrete walk (mirrors `operation_writes`):

1. For each `operation_writes(toolset)` row:
   - `invoke == "action"` (`@agent_instructions`) → `deployAgentInstructions(toolset, operation)` — abstract
   - `invoke == "tool"` (`@agent_tool`) → `deployAgentTool(toolset, operation)` — abstract

*MarkdownDeployment*, *McpDeployment*, *HookDeployment* extend *Deployment* and **implement** the abstract methods — same walk, different mechanism. No decorator names hardcoded in `deployContextTool` itself.

## MarkdownDeployment : Deployment

Same `deploy*` API as base — **overrides** the abstract section methods. Finds `@skill` / `@prompt` / `@rules` / `@instruction` marks on the section or operation, writes markdown via `relative_path` + `render`. Replaces `_harness_writes` and today's `HarnessTool` subclasses.

- `deployContextSection(section)` / `deployContextSectionFidelity(fidelity)` / `deployAgentInstructions(toolset, op)` / `deployAgentTool(toolset, op)` — implementations write files; no separate `deployMember`
- `transport` — `"cli"` \| `"mcp"`; when `"mcp"`, `render` appends the same `render_mcp_invoke` tail
- `relative_path(mark, section, member)` → Path
- `render(mark, section, member)` → str
- `mark(member)` → member — `@skill`, `@prompt`, `@rules`, `@instruction`

| Kind | Decorator | Writes (Cursor) |
| ---- | --------- | --------------- |
| skill | `@skill` | `.cursor/skills/{name}/SKILL.md` |
| prompt | `@prompt` | `.cursor/commands/{name}.md` (VS Code: `.github/prompts/…`) |
| rules | `@rules` | `.cursor/rules/{slug}.mdc` per `Rule` on `rules` property |
| instruction | `@instruction(name)` | named rule file on an operation |

## MCP mode (today)

**No `@mcp` decorator today.** MCP is a **Harness deploy flag**:

- `Harness.write_deploy(mcp: bool = False, …)`
  - `self._transport = "mcp"` when `mcp=True` else `"cli"`
  - transport passed into Skill / Prompt body generation (`ContextToolBody`, `ActionBody`, …)
  - when `transport == "mcp"`: body ends with `render_mcp_invoke` tail — `Use MCP tool: \`{slug}.{member}(…)\``
  - when `mcp=True` and Cursor: `_write_mcp_json` → `.cursor/mcp.json` stdio server
  - `@skill` still deploys `SKILL.md` — MCP tail is at the bottom of that markdown, not a separate file

| `mcp=False` (CLI) | `mcp=True` (MCP) |
| ----------------- | ---------------- |
| every `@skill` / `@prompt` / `@rules` / `@instruction` body ends with YAML fence + `.\tools.ps1 run -` | same files; body ends with `Use MCP tool: \`{slug}.{member}(…)\`` |
| no `mcp.json` | `.cursor/mcp.json` — stdio server → `utilities/mcp_server` |

**Example** — router skill `@stories` body (mcp mode):

```
# stories
…assembled instructions / guidance prose…
Determine which stories skill to run from context…
Use MCP tool: `stories.generate(format='', path='', session='')`
```

CLI mode (`mcp=False`) — same skill, bottom is YAML fence + `.\tools.ps1 run -` instead.

- `render_mcp_invoke(toolset_ref, member)` → str — `primitives/harness/transport.py`; used by `bodies._invoke_tail` when `transport=mcp`

**Today:** `utilities/mcp_server/McpToolset` loads an instance and **rescans** the class with `getmembers` — a second discovery pass unrelated to harness deploy.

## MCP in target

**One walk on *McpDeployment*; two moments:**

| Moment | Method | Job |
| ------ | ------ | --- |
| Deploy | `deployToolset` / `deployAgentInstructions` / `deployAgentTool` | same `operation_writes` iteration as markdown deploy; write `mcp.json` slices; **record** `@mcp` rows in `mcp_operations` |
| Server start | `bind(server)` | open the collection of *McpDeployment* (one per toolset ref); enroll `McpTool` / `McpPrompt` from `mcp_operations` — **not** called from deploy |

| Part | Owner | Applies to |
| ---- | ----- | ---------- |
| **Invoke tail** | *MarkdownDeployment* `render(…, transport="mcp")` | `@skill`, `@prompt`, `@rules`, `@instruction` — agent-facing strings in files |
| **Manifest** | *McpDeployment* `deploy*` | `mcp.json`, which toolset refs to load |
| **Enrollment** | *McpDeployment* `bind` | `McpServer.start` — protocol handlers for recorded `@mcp` ops only |

`@mcp` stacks on the **operation**. No separate *McpToolset* adapter that re-iterates annotations — that logic lives on *McpDeployment* and is shared between deploy and bind.

**Today → target:** retire *McpToolset* as a parallel discovery type; keep *McpTool* / *McpPrompt* as thin protocol wrappers created inside `bind`.

## McpDeployment : Deployment

One per toolset ref. Overrides `deployAgentInstructions` / `deployAgentTool` — during deploy, records `@mcp` operations and writes manifest; does not render markdown. **`bind(server)`** at server start enrolls from `mcp_operations` without rescanning the class. **Today** runtime enrolls all `@agent_tool` / `@agent_instructions` via *McpToolset*; **target** only `@mcp`-marked ops on *McpDeployment*.

## HookDeployment : Deployment

Overrides `deployContextSection` and/or `deployAgentInstructions` — hooks config + hook skill files (`operation_writes` where `vehicle == "hook"`).

`@instruction` named rule files (`primitives/instructions`) are **read-side** — co-located content injects at expand time; orthogonal to the invoke tail.

## Deployable

Protocol — host walked by `Harness.write_deploy()` for *Deployment*-marked members: *ContextGuidance*, *FidelityGuidance*, bare *Guidance*, operations with decorator stacks.

## Harness

```
Harness.write_deploy(mcp=False)
  → registry.load()
  → for each Deployable: deployment.deploy(deployable)
  → merge mcp.json
```

`write_deploy` loads the registry and calls `deployment.deploy(deployable)`. The active `Deployment` subtype (usually *MarkdownDeployment*, sometimes composite with *McpDeployment*) implements the abstract section methods.

### What stays on Harness vs moves off

| Stays on Harness | Moves to host |
| ---------------- | ------------- |
| `write_deploy` — registry load, `deployment.deploy(deployable)` loop, `mcp.json` merge | `.instructions` on *ContextGuidance* / *FidelityGuidance* |
| *McpServer* runtime — `start` calls `McpDeployment.bind` | `@markdown` extract + `instructions` @property assembly |
| | `ContextToolBody` / `compound_guidance` subprocess — **retire** |
| | `context_tool_rules` re-parse — **retire** (`deployContextSection` reads `.rules`) |

## McpServer

- start(toolset_refs: tuple[str, ...])
  → for each ref: *McpDeployment*(ref).bind(self) — **today:** `McpToolset(instance)` + getmembers rescan
- invoke_tool(mcp_name, arguments)
- invoke_prompt(mcp_name, arguments)

*McpTool* / *McpPrompt* — protocol wrappers created inside `McpDeployment.bind`; not a second annotation walk.

---

# utilities/catalog_generator

- **Purpose:** Write catalog pages from `.catalog` on each *Guidance* node.
- **Dependencies:** guidance registry — **not** `harness.bodies`, **not** heading scrape

## Catalog

- Catalog.from_registry()

---

- generate_catalog(out_root: Path)
-> for each ContextGuidance: write page from practice.catalog
-> for each FidelityGuidance: write page from fidelity.catalog

---

## Migration notes


| Ticket          | Today                                                   | Target                                                                                      |
| --------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| #22             | `fidelities` dict on class                              | `**GuidanceCollection**` of *FidelityGuidance* (`stage` + `name` per entry)                 |
| fidelity lookup | `resolve_fidelity`, `STAGE_ALIASES`, `fidelity()` on CT | `**fidelities[name]**` (default) / `**fidelities.by(key_id, key)**` — per-`key_id` indexes |
| fidelity ops    | `_generate_fidelity_methods`, `_set_fidelity` on CT     | **Retire** — fidelity lookup on `GuidanceCollection`; `@agent_instructions` stay on *ContextGuidance* |
| session         | `session_guidance` on CT                                | Workspace only                                                                              |
| satisfy hook    | `generate_fixes_from_validate` on CT                    | Satisfy action recipe + validate report                                                     |
| setup           | # Open prelude on `base_context_tool.md`                | Workspace + `LifecycleAction.begin`                                                         |
| render iterate  | implied on CT / base md                                 | `context_tools/agent_toolset/render/` + channel action md                                   |
| #68             | hyperlinks to other fidelities                          | prior `## {name}` blocks in `FidelityGuidance.context` per `GuidanceCollection` order       |
| #21             | catalog scrape + Harness overlap                        | `.instructions` / `.catalog` on *Guidance*; *Deployment* subtypes only write files |
| deploy          | `ContextToolBody`, `compound_guidance` in Harness       | `Deployment.deployContextTool` / `deployToolset` + `MarkdownDeployment` implements abstract section methods |
| harness prose   | scattered Deployment model section                      | deploy rules on each class intro under Modules                                              |
| contexts        | `@instruction contexts` on CT                           | `@markdown context` on *ContextSection*; `instructions` @property assembles (was `_expand_instructions`) |
| md extractor    | `primitives/instructions`, `@instruction`               | `primitives/markdown`, `@markdown` on extract properties                                    |
| md assembly     | `guidance()` AST + `compound_guidance` CLI              | `instructions` @property override on *Guidance* subclasses                                 |
| templates       | merged `templates/` + `filter_template_lines`           | `@markdown templates` → format → path map; subscript reads content (existing filenames) |
| rules parse     | `context_tool_rules.py` re-parses md at deploy          | `@markdown rules` → `list[Rule]` on *ContextSection*; slug ↔ `Scanner`; same list in `format_rules` |
| section objects | implicit everywhere                                     | *ContextSection* — `context`, `guidance`, `rules`; each `@markdown` (`str` or `list[Rule]`) |
| inheritance     | `BaseContextTool(AgenticToolset)`                       | `ContextGuidance(ContextSection, AgenticToolset)`, `FidelityGuidance(ContextSection)`       |
| #10             | `BaseContextTool` in `context_tools/base/`              | `ContextGuidance` in `context_tools/context_guidance/` (`context_guidance.py`, `guidance.py`, …) |
| #19             | render channels on base                                 | `render()` hook on domain CT; iterate prose on Render/Iterate `@agent_instructions`         |
| MCP transport   | `write_deploy(mcp=True)` → `transport=mcp` on bodies + `mcp.json`; *McpToolset* rescan at start | `@mcp` on *McpDeployment*; `bind` enrolls recorded ops — no *McpToolset* rescan |


**Remove:** `catalog_generator.scrape_fidelities`, `CatalogFidelity` prose assembly → read `.catalog`. `**compound_guidance`** subprocess for deploy → read `Guidance.instructions`. `**session_guidance`**, `**generate_fixes_from_validate`**, `**_generate_fidelity_methods**`, `**_set_fidelity**` from CT.

---

## Behavior sketch (BDD signatures)

**Canonical copy:** `context-tool-resource-model-om-bdd.md` — keep in sync when changing specs. Port to `context_tools/context_guidance/guidance_spec.py` on implementation.

**Notation:** `describe` / `that` / `with` / `it should` — never `when` for state. **Subject-first:** outer `describe` names the file, folder, or deploy tree under test — not internal class names. Object flows: `+` operation, `->` call, `<< triggered by >>` actor.

**Implementation order** (green each layer before the next; detail in `context-tool-resource-model-om-bdd.md`):

1. `Markdown`, `Rule` — extract, coerce str / list[Rule] / templates map
2. `Guidance` — standalone instructions + catalog compound doc
3. `AgenticToolset` — read then deploy bare operations (`@skill` / `@prompt`; `operation_writes`)
4. Base `Guidance` subclass — read then deploy on same fixture (compound instructions in skill bodies)
5. `ContextSection` — shared contexts format — read then deploy router skill and context guidance rules (+ mcp on router when green)
6. `FidelityGuidance` — fidelity instructions read → fidelity prompt deploy (+ mcp); then `GuidanceCollection` / `ContextGuidance` assembly read → full-tree deploy (+ mcp, CLI, VS Code, utility filter)
7. `McpDeployment`, `McpServer` — `mcp.json` manifest; then host invoke on layer 3–6 fixtures (operation annotated `@mcp` + `@agent_tool` or `@agent_instructions`, deployed, started, `tools/call` or `prompts/get`)
8. `Catalog` — pages from each host `.catalog` property (not validate/satisfy — those stay in `agent_toolset`)
9. `HookDeployment` — last; hook deploy not complete in harness today

Deploy outcomes shared across layers live in om-bdd **Deploy shared contexts** — each host layer adds delta `it_behaves_like` blocks only.

Full specs → `context-tool-resource-model-om-bdd.md` (canonical).

---

# Object flows

Interaction traces — same notation as `context-tool-resource-model-om-bdd.md`. Full detail lives there; summary below.

### 0 — Compound doc (read)

+ `Guidance.instructions` / `.catalog` — own markdown or catalog properties + iterate members
+ `AgenticToolset.instructions` — iterate `instructions_registry` (read-side; deploy uses `operation_writes`, not this walk)
+ `AgenticToolset.catalog` — catalog properties + tools + `instructions_registry`

### 1 — Instructions assembly (read)

+ `ContextSection.instructions` → context + guidance + format_rules(rules) + templates[format]
+ `GuidanceCollection.instructions` → join fidelities in declaration order
+ `ContextGuidance.instructions` → super + fidelities

<< triggered by >> Agent, `MarkdownDeployment` render at deploy, action: guidance — same `@property` string, no subprocess

### 1b — `@markdown` extract

+ `ContextSection.{context,guidance,rules,templates}` → `Markdown.from_label` → extract → coerce

<< triggered by >> Scan — `practice.rules` / `fidelity.rules`
<< triggered by >> `MarkdownDeployment.deployContextSection` / `deployContextSectionFidelity` with `@rules`
<< triggered by >> `.instructions` assembly — rules via `format_rules`

### 2 — Fidelity lookup

<< triggered by >> Agent or invoke context with fidelity
	-> `practice.fidelities[name]` / `practice.fidelities.by("stage", stage)` → `fidelity.instructions`

### 3 — Catalog

+ `Catalog.generate_catalog` → each `Guidance.catalog` — never reads `.instructions`

### 4 — Deploy

+ `Harness.write_deploy` → `registry.load()` → `deployment.deploy(deployable)` per entry
	-> `deployContextTool` — `deployContextSection` + `deployContextSectionFidelity` × n + `deployToolset` (`operation_writes`)
	-> `deployToolset` alone for bare `AgenticToolset`
	-> `MarkdownDeployment` — skills, commands, rules, invoke tails
	-> `McpDeployment` — record `@mcp` ops, merge `mcp.json` (no `bind` during deploy)

### 5 — MCP server start

+ `McpServer.start(refs)` → `McpDeployment(ref).bind(server)` per ref — enroll from `mcp_operations`, no class rescan

### 6 — MCP invoke

<< triggered by >> Agent reads invoke tail or `tools/call`
	-> `McpServer.invoke_tool` / `invoke_prompt`

### 7 — Runtime guidance

+ `AgenticToolset.guidance()` → `self.instructions`

---

## Open questions

1. `**catalog` format** — HTML fragment only, or markdown that `Catalog` wraps in a shell template?
2. **Utilities** — `Guidance` with `instructions` only and `catalog` empty until overridden?
3. **Fidelity artifact** — per-fidelity **command** (today) vs **skill** (extended mode) — policy on `FidelityGuidance` or deploy flag?
4. **operation_writes** — keep AST walk in Harness or move write-vehicle metadata onto `AgenticToolset` manifest?
5. **Cross-tool guidance** — a practice calling a companion's `guidance()` with `mode=tool`: stay in `@agent_instructions` recipe only, or split into deploy-time `.instructions` vs runtime companion defer?

