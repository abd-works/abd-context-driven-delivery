# Guidance resource model — object model & BDD

Extract from `context-tool-resource-model.md`. **Canonical for object flows and BDD** — update here first; full doc summarizes and must stay aligned. **CE notation** per `clean_engineering` model fidelity. **BDD notation** per `bdd` behavior fidelity (`describe` / `that` / `with` / `it should` — never `when` for state). Tables, narrative, and rationale → full doc only.

---

# primitives/markdown

- **Purpose:** Extract co-located markdown — not assembly.
- **Seam (terms):** `@markdown`, `Markdown`, `AssetLocator`
- **Dependencies (one-way):** `primitives/assets`

## Markdown

+ Markdown.from_label(host, label: str)
------
----
+ extract(): str
	-> AssetLocator.locate(host.context_guidance.module_dir, label, host.name)
+ coerce(text: str, return_type): str | list[Rule] | dict[str, str]
	// return_type selects str, list[Rule], or templates path map

## @markdown

+ @markdown(getter) -> property
	// property name = label; coerce to annotated return type
	-> Markdown.from_label(owner, label)
	-> Markdown.extract()
	-> Markdown.coerce(return_type)

---

# context_guidance/guidance

- **Purpose:** Assemble agent instructions and catalog from `@markdown` properties; fidelity-scoped guidance nodes.
- **Seam (terms):** `Guidance`, `ContextSection`, `ContextGuidance`, `FidelityGuidance`, `GuidanceCollection`
- **Dependencies (one-way):** `primitives/markdown`, `primitives/assets`, `workspace`, `context_tools/agent_toolset/scan`

## Guidance

+ Guidance()
	// abstract — reading seam for instructions and catalog
------
----
+ instructions: str
	// @property — compound doc: own markdown properties + iterate members
+ catalog: str
	// @property — compound doc: own markdown properties + iterate members (HTML)

## ContextSection : Guidance
+ ContextSection()
	// abstract — shared context / guidance / rules
------
+ context: str
	// @markdown — # Contexts  for this host scope
+ guidance: str
	// @markdown
+ rules: list[Rule]
	// @markdown — coerce bullets to Rules; slug matches Scanner; @rules at deploy
+ templates: dict[str, str]
	// @markdown — format key → relative path under templates/; subscript reads content
+ format: str
	// active format for templates[format] in instructions assembly
+ default_format: str
	// fallback when format unset; invoke copies to format on active host
+ name: str | None
	// scopes @markdown extract; None on context guidance
+ context_guidance: ContextGuidance
	// @markdown module_dir always from here — self on ContextGuidance, parent on FidelityGuidance
+ fidelity: str | None
	// domain fidelity key — equals name on fidelity guidance; active key on context guidance at invoke; None on context guidance
----
+ instructions: str
	// @property — context + guidance + format_rules(rules) + templates[format]; same logic on every host

## ContextGuidance : ContextSection
	// also AgenticToolset, Deployable — see primitives/agent_toolset, primitives/harness

+ ContextGuidance(format, path, session, workspace)
------
+ << composition >> fidelities: GuidanceCollection
+ examples: str
	// @markdown — not in instructions
+ << association >> workspace: Workspace
+ << association >> scanner: Scan
----
+ rules: list[Rule]
	// inherited; deployed when MarkdownDeployment implements deployContextSection / deployContextSectionFidelity
+ instructions: str
	// @property override — super.instructions + fidelities.instructions
	// @skill @agent_instructions — router skill body = this string at deploy; guidance() -> self.instructions
	-> ContextSection.instructions
	-> GuidanceCollection.instructions

## GuidanceCollection

+ GuidanceCollection(entries: tuple[FidelityGuidance, ...])
------
+ << association >> parent: ContextGuidance
+ entries: tuple[FidelityGuidance, ...]
+ indexes: dict[str, dict[str, FidelityGuidance]]
	// key_id → key → entry — built at construction ("name", "stage", …)
----
+ instructions: str
	// @property — join each entry.instructions in declaration order
+ getitem(name: str): FidelityGuidance
	// default key — same as by("name", name); fidelities["behavior"]
+ by(key_id: str, key: str): FidelityGuidance
	// non-default keys — select index for key_id; lookup key (stage aliases in "stage" index)
+ names(): list[str]
+ iter()

## FidelityGuidance : ContextSection, Deployable

+ FidelityGuidance(name, stage, default_format, context_guidance)
------
+ stage: str
	// CDD stage key — fidelity, name, context_guidance on ContextSection; read-side only
----
+ instructions: str
	// @property — ContextSection assembly scoped by name; @prompt @agent_instructions — fidelity command body = this string at deploy
+ rules: list[Rule]
	// @markdown; @rules at deploy — same list[Rule] as Scan / format_rules

---

# context_tools/agent_toolset/scan

## Rule

+ Rule(slug: str, body: str, fidelity: str | None = None)
------
+ slug: str
+ body: str
+ fidelity: str | None

## Scanner

+ Scanner(rule: str)
----
+ scan(file_path: Path): list

## ScannerCollection

+ ScannerCollection.discover(): dict[str, type[Scanner]]

---

# primitives/agentic_toolset

- **Purpose:** `AgenticToolset` — tool and action registration; runtime invoke.
- **Dependencies:** `primitives/tools`, `context_tools/context_guidance`

## AgenticToolset : Toolset, Guidance, Deployable

+ AgenticToolset()
	// ContextGuidance uses deployContextTool; bare toolset uses deployToolset
------
+ tools: dict
	// @agent_tool registry — from Toolset
+ instructions_registry: Mapping
	// @agent_instructions members — class/extension discovery (was `actions`)
----
+ instructions: str
	// @property — compound instructions doc: own markdown properties + iterate instructions_registry
+ catalog: str
	// @property — compound catalog doc: own catalog properties + iterate tools and instructions_registry
+ guidance(): str
	-> self.instructions

---

# primitives/harness

- **Purpose:** *Deployment* + *Harness* + MCP runtime. **Extract** what `Harness.write_deploy` / `operation_writes` already do — same artifacts; not new deploy behavior.
- **Seam (terms):** `Deployment`, `MarkdownDeployment`, `McpDeployment`, `HookDeployment`, `Deployable`, `Harness`, `McpServer`, `McpTool`, `McpPrompt`
- **Dependencies:** registry; `transport` (invoke tails). Stdio entry: `utilities/mcp_server/__main__.py` loads *McpServer* from here.

## Deployment

+ Deployment()
	// deploy(deployable) — pass deployable in, write artifacts to disk; no return (product is on file)
------
----
+ deploy(deployable: Deployable)
	when deployable is ContextGuidance: deployContextTool(context_guidance)
	when deployable is AgenticToolset: deployToolset(toolset)

+ deployContextTool(context_guidance: ContextGuidance)
	// today: Harness._generate_entry when kind == context_tool
	-> deployContextSection(context_guidance)
	-> deployContextSectionFidelity(fidelity) per context_guidance.fidelities
	-> deployToolset(context_guidance)

+ deployContextSection(section: ContextSection)
	// abstract — today: router skill _emit("skill") + rules; subtype implements

+ deployContextSectionFidelity(fidelity: FidelityGuidance)
	// abstract — today: per-fidelity _emit("prompt"); subtype implements

+ deployToolset(toolset: AgenticToolset)
	// today: operation_writes loop in Harness._generate_entry — NOT instructions_registry walk
	-> for each operation_writes row on toolset class:
		when invoke == action: deployAgentInstructions(toolset, operation)
		when invoke == tool: deployAgentTool(toolset, operation)

+ deployAgentInstructions(toolset, operation)
	// @agent_instructions method — today: _emit when @skill/@prompt stacked (invoke=action)

+ deployAgentTool(toolset, operation)
	// @agent_tool method — today: invoke tail; file only if @skill/@prompt stacked

## MarkdownDeployment : Deployment

+ MarkdownDeployment(transport: str = "cli")
	// same deploy API as base — overrides abstract section methods; writes .cursor markdown files
------
+ transport: str
----
+ deployContextSection(section: ContextSection)
+ deployContextSectionFidelity(fidelity: FidelityGuidance)
+ deployAgentInstructions(toolset, operation)
+ deployAgentTool(toolset, operation)
+ relative_path(mark, section, member): Path
+ render(mark, section, member): str
+ mark(member) -> member

+ @skill(name: str | None = None) -> member
+ @prompt(name: str | None = None) -> member
+ @rules(member) -> member
+ @instruction(name: str) -> member
+ render_mcp_invoke(toolset_ref, member) -> str

## McpDeployment : Deployment

+ McpDeployment(toolset_ref: str)
	// one per toolset — same operation_writes walk as deploy; bind() at server start only
------
+ toolset_ref: str
+ mcp_operations: list  // @mcp rows collected during deployToolset walk — bind reuses, no second scan
----
+ deployAgentInstructions(toolset, operation)
	// @mcp + invoke action — record op; manifest slice when mcp=True
+ deployAgentTool(toolset, operation)
	// @mcp + invoke tool — record op
+ deployToolset(toolset: AgenticToolset)
	// same walk as base deployToolset; writes mcp.json contribution; fills mcp_operations
+ bind(server: McpServer)
	// server start only — enroll McpTool / McpPrompt from mcp_operations; NOT called from deploy

+ @mcp(method) -> method

## HookDeployment : Deployment

+ HookDeployment()
	// same deploy API — overrides section and/or toolset methods for hooks config + hook skills
------
+ deployContextSection(section: ContextSection)
+ deployAgentInstructions(toolset, operation)
	// @hook stacked on @agent_instructions — today: operation_writes vehicle==hook

+ @hook(event: str | None = None) -> member
+ @agent(name: str | None = None) -> member
+ @agent_guidance(name: str | None = None) -> member

## Deployable

+ Deployable()
	// anything passed to Deployment.deploy — ContextGuidance, AgenticToolset, …

## Harness

+ Harness()
+ deployment: Deployment
----
+ write_deploy(extended: bool, mcp: bool = False, …)
	// today: walk + _generate_entry + _write_harness_files inline on Harness
	-> registry.load()
	-> deployment.deploy(deployable) per registry entry
	// side effect — artifacts on disk; no aggregate return

## McpServer

+ McpServer()
+ mcp_deployments: list[McpDeployment]  // one per toolset_ref from mcp.json
----
+ start(toolset_refs: tuple[str, ...])
	// today: load instance + McpToolset getmembers rescan — target: McpDeployment per ref, bind()
	-> for ref in toolset_refs: McpDeployment(ref).bind(self)
+ invoke_tool(mcp_name, arguments)
+ invoke_prompt(mcp_name, arguments)
	// stdio host — refs from mcp.json

---

# utilities/catalog_generator

## Catalog

+ Catalog.from_registry()
+ generate_catalog(out_root: Path)
	-> ContextGuidance.catalog
	-> FidelityGuidance.catalog

---

# Object flows

**Implementation order** matches BDD layers below: markdown → Guidance → AgenticToolset **+deploy** → base Guidance **+deploy** → shared contexts **+deploy** → fidelities + assembly **+deploy** → MCP → catalog → hooks last.

## Compound doc

+ Guidance.instructions
	-> own markdown properties + iterate members → markdown compound doc
+ Guidance.catalog
	-> own catalog properties + iterate members → HTML compound doc
+ AgenticToolset.instructions
	-> iterate instructions_registry — assemble markdown per @agent_instructions operation
	// read-side registry walk — deploy uses operation_writes AST walk, not this collection
+ AgenticToolset.catalog
	-> own catalog properties + iterate tools + instructions_registry for HTML fragments

## Instructions assembly

+ ContextSection.instructions
	-> self.context + self.guidance + format_rules(self.rules) + self.templates[format]
	// FidelityGuidance — same property; name scopes @markdown extract only
+ GuidanceCollection.instructions
	-> join each FidelityGuidance.instructions in declaration order
+ ContextGuidance.instructions
	-> super.instructions + fidelities.instructions

<< triggered by >> Agent, deploy, guidance action

## @markdown extract

+ host.{label}
	-> Markdown.from_label(host, label)
	-> Markdown.extract()
	-> Markdown.coerce(return_type)
<< uses >> AssetLocator

## Deploy

+ Harness.write_deploy(mcp=…)
	-> registry.load()
	-> deployment.deploy(deployable) per registry entry
		// deployment composite — MarkdownDeployment + McpDeployment (+ HookDeployment when hooks)
		-> deployContextTool(context_guidance)
			-> deployContextSection — MarkdownDeployment: router @skill + @rules on context guidance
			-> deployContextSectionFidelity per fidelity — MarkdownDeployment: @prompt fidelity command + @rules
			-> deployToolset(context_guidance) — operation_writes walk (context tool is also toolset)
		-> deployToolset(bare AgenticToolset) — operation_writes walk only
		-> deployAgentInstructions per row invoke action — markdown file when @skill/@prompt stacked; McpDeployment records @mcp op
		-> deployAgentTool per row invoke tool — invoke tail when stacked; McpDeployment records @mcp op
		-> McpDeployment.deployToolset merges mcp.json slice when mcp=True
<< triggered by >> Harness.write_deploy
	-> host.instructions / fidelity.instructions at render — read @property, not subprocess

## MCP server start

+ McpServer.start(toolset_refs from mcp.json)
	-> for ref: McpDeployment(ref).bind(self)
		-> enroll from mcp_operations recorded when that toolset was deployed — not getmembers rescan
<< triggered by >> Cursor spawns stdio host — not during write_deploy

## MCP invoke

<< triggered by >> Agent reads deployed SKILL.md invoke tail or host tools/call / prompts/get
	-> fixture: toolset with operation annotated @mcp (+ @agent_tool or @agent_instructions) and deployed mcp=True
	-> McpServer.invoke_tool("{slug}.{member}", arguments)
	-> McpServer.invoke_prompt("{slug}.{member}", arguments)

## Runtime guidance

+ AgenticToolset.guidance()
	-> self.instructions
<< triggered by >> action: guidance, MCP prompt body assembly

---

# Behavior sketch (BDD)

Port to `context_tools/context_guidance/guidance_spec.py`. Every `it` body: `# BDD: SIGNATURE` until development fidelity.

**Share notation** — same shape as `bdd` § Guidance for **read** and **deploy**:
1. **`shared context "…"`** — outcomes written once (read against a common subject, or deploy against a deploy output tree).
2. **Each layout `describe`** — **`before.each`** assigns the subject or runs **`write_deploy`** on that layer’s fixture.
3. **`it_behaves_like "…"`** — pulls in the shared block; no repeating the same deploy `describe` tree in every layer.

**Deploy rule:** green **read** for a host, then **deploy markdown artifacts** for that same host before moving on — skills, prompts, and rules first because they are the cheap check that deploy renders the same instructions strings the read path assembled. Split a layer when read has two milestones (fidelity instructions, then assembly): deploy after each milestone, not after all read blocks.

**MCP rule:** same rhythm — once a layer’s markdown deploy is green, add a sibling deploy `describe` with `mcp` transport on **that fixture**. MCP still writes skills, commands, and rules files; transport only changes the **invoke tail at the bottom** of each body (`it_behaves_like "deploy mcp invoke tail on markdown bodies"`). Layer 7 keeps **manifest + host enrollment** only — not first proof of signatures on disk.

Port: `before.each` → fixture; `write_deploy` → deploy setup; shared block → `shared_context`; `it_behaves_like` → `included_context`.

**bdd-behavior shared rules** (validate every line against these):

- **observable-behavior** — `it should` states return value, file on disk, or agent-visible text — not private helpers or class names.
- **describe-is-subject-not-internal** — outer `describe` is a file, folder, deploy tree, or context tool module — never `Markdown`, `Deployment`, `Harness`, …
- **describe-is-plain-english** — no decorator symbols or type syntax in `describe` / `that` / `with` / `it should` labels; put exact paths and APIs on `->` port lines beneath the `it`.
- **state-not-when** — never `when`; use `that` for finalized events (`that has been deployed`), `with` for standing conditions.
- **nest-by-enabling-events** — each nested block must be a real precondition for the outcomes below it.
- **domain-vocabulary** — use model terms in outcomes: **context guidance**, **fidelity guidance**, `context_guidance.module_dir`, fidelity name, context guidance instructions. Never **practice host** or **practice-wide**.
- **usage-order-behaviors** — co-located file → minimal guidance → toolset **read+markdown deploy+mcp** → base guidance **read+markdown deploy+mcp** → shared contexts **read+router/rules deploy+mcp** → fidelity instructions **read+fidelity prompt deploy+mcp** → assembly **read+full-tree deploy** → MCP manifest/host → catalog → hooks last.

**Implementation order** — green each layer before the next. Each host layer ends with deploy using **deploy shared contexts** (define once below).

| Layer | Test subject | Depends on |
| ----- | ------------ | ---------- |
| 1 | Co-located markdown section as string — correct module file only | — |
| 2 | Minimal tool host with compound instructions and catalog only | layer 1 |
| 3 | Agentic toolset — read then deploy bare operations | layer 2 |
| 4 | Base Guidance — read then deploy on same fixture | layer 2–3 |
| 5 | Shared contexts on context guidance — read then deploy router and rules | layer 1–2, 4 |
| 6 | Fidelity instructions read → prompt deploy → assembly read → full-tree deploy (+ mcp each deploy step) | layer 5 |
| 7 | MCP manifest then host invoke — annotated op deployed → start from manifest → tools/call or prompts/get | layer 3–6 fixtures |
| 8 | Catalog pages from guidance catalog property | layer 2+ |
| 9 | Hooks config and hook skill files — last; hooks deploy not complete in harness today | layer 6 |

---

## Layer 1 — co-located markdown and folders

```
describe a co-located markdown file beside a host module
  with a section heading that matches a property label
    with a string property on the host backed by that section
      it should return the section body when the property is read
  with known prose written in the module markdown file for that label
    with the property read on the host in that module
      it should return that prose
    with an identically named section in a different module folder
      it should not return prose from the other module file when the host belongs to this module
      -> resolves under context_guidance.module_dir for this host only
```

---

## Layer 2 — minimal tool host without a contexts file

```
describe a minimal tool class
  with several markdown-backed properties
    with the instructions property read
      it should assemble markdown from those properties in declared order
      it should expose instructions as one compound property not as a single markdown label
    with the catalog property read and no catalog content on the host
      it should return empty catalog not instructions
    with the catalog property read and markdown catalog content on the host
      it should return HTML formatted text from that markdown formatting
      it should not return instructions text
```

---

## Deploy shared contexts (define once)

Reuse in every layer’s deploy subsection via `it_behaves_like`. Each layer’s `describe` only runs `write_deploy` on **its** fixture in `before.each`.

```
shared context "deploy bare agentic toolset operations"
  with a Cursor deploy output tree
    it should write one skill file per agent-instructions operation marked for skill
    -> .cursor/skills/{operation}/SKILL.md or flat skill path per harness convention
    it should write one command file per agent-instructions operation marked for prompt
    -> .cursor/commands/{operation}.md
    it should not write a router skill or fidelity commands
    -> deployToolset only; no deployContextSection
  with a deploy run after write_deploy
    it should walk operation_writes not instructions_registry
    it should render skill and prompt bodies from the same instructions strings the read path assembles

shared context "deploy base guidance skill bodies"
  with deployed skill bodies for marked operations
    it should use the compound instructions string from the guidance instructions property

shared context "deploy context guidance router and rules"
  with a Cursor deploy output tree
    it should write a router skill file whose body equals context guidance instructions
    -> .cursor/skills/{slug}/SKILL.md
    it should write one context guidance rules file per context guidance rule slug
    -> .cursor/rules/{slug}.mdc

shared context "deploy fidelity sections on context guidance"
  with a Cursor deploy output tree
    it should write one fidelity command file per fidelity whose body equals that fidelity instructions
    -> .cursor/commands/{slug}-{fidelity}.md
    it should write one fidelity rules file per fidelity rule slug

shared context "deploy cli transport on markdown bodies"
  with deployed skill command and rules bodies
    it should append the CLI invoke fence at the bottom of each body
    -> MarkdownDeployment.render transport cli

shared context "deploy mcp invoke tail on markdown bodies"
  with a deployed skill file for an mcp-published agent-instructions operation
    it should keep the instruction prose at the top of the skill body unchanged from the non-mcp deploy
    it should place one MCP invoke line after that prose at the bottom of the file
    it should name the tool as {toolset-slug}.{operation} with the method parameter signature in backticks
    -> Use MCP tool: `bdd.generate(...)`; MarkdownDeployment.render_mcp_invoke / transport.render_mcp_tool_reference
    it should not append the CLI tools.ps1 invoke fence
  with a deployed command file for an mcp-published prompt operation
    it should place the same MCP invoke line after the command body at the bottom of the file
  with a deployed router skill for context guidance when the router operation is mcp-published
    it should place the MCP invoke line after context guidance instructions at the bottom of the skill file
  with a deployed fidelity command when that fidelity prompt is mcp-published
    it should place the MCP invoke line after fidelity instructions at the bottom of the command file
  with a deployed rules file when that rule slug is mcp-published in the deploy walk
    it should place the MCP invoke line after the rule body at the bottom of the rules file

shared context "deploy mcp enrollment without bind"
  with a deploy run after write_deploy with mcp transport
    it should record each mcp-published operation for server enrollment
    it should not bind tool handlers during deploy
    -> McpDeployment.mcp_operations; bind at server start only

shared context "deploy vscode prompt paths"
  with a VS Code deploy output tree
    it should write fidelity command files under github prompts not under cursor commands
    -> .github/prompts/{slug}-{fidelity}.md

shared context "deploy full context tool coverage"
  with a registered context guidance host fully deployed
    it should emit router skill fidelity commands and operation artifacts in one pass
    -> deployContextSection; deployContextSectionFidelity per fidelity; deployToolset

shared context "deploy bare utility toolset only"
  with a registered utility toolset fully deployed
    it should emit operation artifacts only without router or fidelity commands
    -> deployToolset; operation_writes not instructions_registry
```

---

## Layer 3 — agentic toolset read and deploy

### Read

```
describe a toolset module with several agent-instructions operations
  with the instructions property read on a loaded instance
    it should assemble one compound instructions string from each registered operation
    -> instructions_registry
  with the catalog property read on the same instance
    it should assemble catalog from its catalog properties then from tools and registered operations
```

### Deploy

Fixture: small `AgenticToolset` with `@skill` / `@prompt` on some `@agent_instructions` operations, optional `@agent_tool`, co-located markdown for invoke tails.

```
describe a bare agentic toolset registered for deploy
  with before.each that runs write_deploy on that fixture
  it_behaves_like "deploy bare agentic toolset operations"

describe a bare agentic toolset with mcp-published operations registered for deploy
  with before.each that runs write_deploy with mcp transport on that fixture
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

---

## Layer 4 — base Guidance read and deploy

### Read

```
describe a minimal guidance tool subclass
  with agent-instructions operations registered on the toolset
    with the instructions property read
      it should assemble compound instructions from markdown properties then from each operation
```

### Deploy

Same annotations as layer 3 on a `Guidance` subclass with layer 2 compound `instructions` / `catalog`.

```
describe a minimal guidance tool registered for deploy
  with before.each that runs write_deploy on that fixture
  it_behaves_like "deploy bare agentic toolset operations"
  it_behaves_like "deploy base guidance skill bodies"

describe a minimal guidance tool with mcp-published operations registered for deploy
  with before.each that runs write_deploy with mcp transport on that fixture
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

---

## Layer 5 — shared contexts on context guidance read and deploy

### Read

**Shared contexts format** — the `# Contexts` chapter template (`context-tool-resource-model.md` § Contexts file layout; scaffold seed in `create_context_tool/templates/domain-md.md`). Context guidance body before `## Fidelities`:

```
# Contexts
{preamble before first ##}     → context property
## Guidance                     → guidance property
## Shared rules                 → rules property — scanner bullets

## Fidelities
  … fidelity sections — layer 6 …
```

**Share** (`bdd` § Guidance) — same read outcomes for every on-disk layout; only fixture setup differs. Resolution order matches today's `@instruction` slots: `{label}/` folder merged, then `{label}.md`, then `## {Label}` in `{domain-slug}.md` beside the module.

Define once — all `it should` read **context guidance** (assigned in `before.each` below):

```
shared context "shared contexts format on context guidance"
  with the context property read
    it should return the Contexts preamble on context guidance only
  with the guidance property read
    it should return the Guidance section body only
  with a Shared rules section containing scanner bullets
    with the rules property read
      it should parse bullets into rules whose slugs match the scanner registry
      it should expose slug body and optional fidelity on each rule for scan and later deploy
  with the instructions property read
    it should join context guidance formatted rules and templates selected by format in one string
  with a templates folder beside the module
    with template files such as slug-templates and slug-sketch inside the folder
      with the templates property read
        it should map each format key to a relative path under templates
        it should keep existing filenames without renaming to slug-fidelity-format
      with one format key selected
        it should return the file content at the mapped path
```

Use in each layout — **assign context guidance, then include shared context**:

```
describe a context tool module with one domain markdown file named for the context tool
  with before.each that assigns context guidance from {domain-slug}.md at module_dir
  it_behaves_like "shared contexts format on context guidance"

describe a context tool module with section files and subsection folders named for the context tool
  with before.each that assigns context guidance from contexts guidance and rules files or folders beside the module
  it_behaves_like "shared contexts format on context guidance"
```

### Deploy

Fixture: same layouts as Read — shared contexts on context guidance, no fidelity sections yet (or empty `## Fidelities`).

```
describe a context tool module with shared contexts format registered for deploy
  with before.each that runs write_deploy on the single-file or section-file fixture from Read
  it_behaves_like "deploy context guidance router and rules"

describe a context tool module with shared contexts format and mcp on the router registered for deploy
  with before.each that runs write_deploy with mcp transport on the layer 5 read fixture
  it_behaves_like "deploy context guidance router and rules"
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

---

## Layer 6 — fidelity sections and context guidance assembly

Fidelity blocks under `## Fidelities` in the shared contexts template — `## {name}` with optional `### Guidance` and `### Rules`, or one file or folder per fidelity name when split on disk. **Deploy fidelity prompts as soon as fidelity instructions read is green** — before assembly read. Assembly read then full-tree deploy follow.

### Read — fidelity instructions from markdown

Define once — all `it should` read **fidelity guidance** (and the deeper fidelity in stacking cases) assigned in `before.each` below:

```
shared context "fidelity sections in shared contexts format"
  with the guidance property read on fidelity guidance
    it should return Guidance under that fidelity name only
  with the rules property read on fidelity guidance
    it should return Rules under that fidelity name as a rule list
    it should not include rules from sibling fidelity sections
  with two fidelities declared shallower before deeper in the collection
    with the instructions property read on the deeper fidelity guidance
      it should include prior fidelity sections in context in declaration order
      it should not include later fidelity sections or sibling templates
      it should not inline examples into fidelity instructions
    with the templates property read on the deeper fidelity guidance
      it should return only that fidelity entries from the templates scan
    with one format key selected on the deeper fidelity guidance
      it should apply template line filtering when produce fidelities share one templates file
    with the catalog property read on the deeper fidelity guidance
      it should stack prior fidelity catalog sections like instructions
    with the rules property read on the deeper fidelity guidance
      it should match the same bullets already formatted into fidelity instructions
```

Use in each layout — **assign context guidance and fidelity guidance from that layout, then include shared context**:

```
describe a context tool module with one domain markdown file named for the context tool
  with before.each that assigns context guidance from {domain-slug}.md and fidelity guidance from a named ## heading under ## Fidelities
  it_behaves_like "fidelity sections in shared contexts format"

describe a context tool module with a fidelities folder beside the module
  with before.each that assigns context guidance and fidelity guidance from files or subfolders under fidelities
  it_behaves_like "fidelity sections in shared contexts format"
```

### Deploy — fidelity skills and prompts

Same fixtures as fidelity Read — prove command bodies equal each fidelity guidance `instructions` string before testing assembly.

```
describe a context tool module with fidelity sections registered for deploy
  with before.each that runs write_deploy on the single-file or fidelities-folder fixture from fidelity Read
  it_behaves_like "deploy fidelity sections on context guidance"

describe a context tool module with fidelity sections and mcp on fidelity commands registered for deploy
  with before.each that runs write_deploy with mcp transport on that fixture
  it_behaves_like "deploy fidelity sections on context guidance"
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

### Read — collection and context guidance assembly

Collection lookup (not layout-specific):

```
describe a guidance collection on context guidance
  with the instructions property read on the collection
    it should join each fidelity instructions string in declaration order
  with lookup by domain name
    it should return fidelity guidance for that name
  with lookup by stage key and sketch
    it should return the sketch fidelity from the stage index
  with lookup by stage alias
    it should return the same fidelity as lookup by domain name
```

Context guidance assembly — context guidance reads from layer 5 plus fidelities from above; not a separate “named tool” layer. Use the same `before.each` fixtures as layer 5–6.

```
describe context guidance with fidelities examples and templates beside the module
  with before.each that assigns context guidance from the layer 5 and layer 6 fixtures
  with the instructions property read on context guidance
    it should join context guidance instructions with each fidelity instructions in declaration order sketch first
    it should not inline examples into instructions
    it should not include the scaffold label
  with the examples property read on context guidance
    it should return examples folder content as a separate property not inside instructions
  with the catalog property read on context guidance
    it should not derive catalog from instructions
  with format and default format set on context guidance
    it should select the template for the active format in context guidance instructions assembly
  with fidelity set at invoke on context guidance
    it should resolve active format from the named fidelity default format
```

### Deploy — full context tool tree and transports

Assembly fixtures — one pass proves router, fidelity commands, and operation artifacts together. Fidelity prompt deploy is already green above; this subsection adds coverage, filters, and non-Cursor paths.

```
describe a context tool module with fidelities and assembly registered for deploy
  with before.each that runs write_deploy on the layer 6 assembly fixture
  it_behaves_like "deploy context guidance router and rules"
  it_behaves_like "deploy fidelity sections on context guidance"
  it_behaves_like "deploy full context tool coverage"

describe a context tool module with fidelities assembly and mcp registered for deploy
  with before.each that runs write_deploy with mcp transport on the layer 6 assembly fixture
  it_behaves_like "deploy full context tool coverage"
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"

describe a bare utility toolset such as git registered for deploy
  with before.each that runs write_deploy on that utility fixture
  it_behaves_like "deploy bare utility toolset only"
  with an operation published as both skill and agent instructions
    it should write one skill file for that operation without a router skill or fidelity commands
  with an agent-tool operation only
    it should write a standalone skill file only when skill or prompt is also published

describe a deploy run with a single source name filter on a context tool
  that has been deployed for one named source only
    it should emit only that tool router fidelity commands and operation files

describe a context tool deployed with cli transport
  with before.each that runs write_deploy with cli transport on a layer 6 fixture
  it_behaves_like "deploy cli transport on markdown bodies"

describe a context tool deployed for VS Code
  with before.each that runs write_deploy with vscode transport on a layer 6 fixture
  it_behaves_like "deploy vscode prompt paths"
```

---

## Layer 7 — MCP manifest and host

MCP invoke tails on deployed skill, command, and rules files are proved incrementally in layers 3–6 via **deploy mcp invoke tail on markdown bodies**. Layer 7 proves **manifest → start → invoke** on the same fixtures: a toolset whose operation was annotated for mcp, deployed, then called through the running host.

### Manifest

```
describe an MCP manifest file
  that has been written by a deploy with mcp enabled
    it should list stdio server command and comma-separated toolset refs for walked classes
    -> .cursor/mcp.json
  that has been written by a deploy with mcp disabled
    it should omit the MCP manifest file
```

### Host — invoke after deploy

Chain every runtime `it should` through: **annotated operation → deployed with mcp → server started from that deploy’s manifest → tools/call or prompts/get**. Reuse layer 3–6 fixtures; only the invoke kind changes.

```
describe a bare agentic toolset with an agent-tool operation annotated for mcp
  that has been deployed with mcp enabled
    with an MCP server started from manifest toolset refs written during that deploy
      it should enroll that operation under the mcp name {slug}.{operation}
      it should enroll from mcp operations recorded at deploy not from a second annotation scan on the class
      -> McpDeployment.bind; not McpToolset getmembers
      with a tools call for that enrolled mcp name and arguments matching the operation signature
        it should return the operation result

describe a bare agentic toolset with an agent-instructions operation annotated for mcp
  that has been deployed with mcp enabled
    with an MCP server started from manifest toolset refs written during that deploy
      it should enroll that operation as a prompt under the mcp name {slug}.{operation}
      with a prompts call for that enrolled mcp name
        it should return the orchestration result from that operation

describe a minimal guidance tool with an agent-instructions operation annotated for mcp
  that has been deployed with mcp enabled
    with an MCP server started from manifest toolset refs written during that deploy
      with a prompts call for that enrolled mcp name
        it should return the same compound instructions string the read path assembles

describe a context tool module with router skill annotated for mcp
  that has been deployed with mcp enabled
    with an MCP server started from manifest toolset refs written during that deploy
      with a prompts call for the router enrolled mcp name
        it should return context guidance instructions as the prompt source

describe a context tool module with fidelity command annotated for mcp
  that has been deployed with mcp enabled
    with an MCP server started from manifest toolset refs written during that deploy
      with a prompts call for that fidelity enrolled mcp name
        it should return fidelity guidance instructions as the prompt source

describe a toolset with an mcp-published operation
  that has been deployed with mcp enabled but the server has not been started
    it should record the operation for enrollment without binding handlers during deploy
```

---

## Layer 8 — catalog pages

`catalog_generator` reads each host’s `.catalog` compound doc — same read seam as layers 2–6, different consumer. **Generate / validate / satisfy** live in `context_tools/agent_toolset/`; they are not part of this resource model or `guidance_spec.py`.

```
describe generated catalog pages
  that have been built from the guidance registry
    it should write each context guidance catalog property to its own page
    it should write each fidelity catalog property to its own page
    it should not scrape deployed markdown files or heading structure from disk
```

---

## Layer 9 — hooks deploy output

**Last layer** — hook deploy is not fully wired in harness today; spec the target here but implement after MCP and catalog are green.

```
describe a Cursor hooks config
  that has been deployed with hook sources in the walk
    it should write hooks manifest entries for each registered hook event
    -> .cursor/hooks.json
    it should write hook skill files for hook-published agent-instructions operations
  that has been partially deployed with no hook sources emitted
    it should leave hooks manifest unchanged from a prior full deploy
```
