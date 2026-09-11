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

**Implementation order** matches BDD layers below: markdown → Guidance → AgenticToolset → ContextSection → fidelities → ContextGuidance → deploy/IDE → MCP → hooks.

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
		-> enroll McpTool / McpPrompt from mcp_operations
<< triggered by >> Cursor spawns stdio host — not during write_deploy

## MCP invoke

<< triggered by >> Agent reads SKILL.md invoke tail or host tools/call
	-> McpServer.invoke_tool("{slug}.{member}")
	-> McpServer.invoke_prompt("{slug}.{member}")

## Runtime guidance

+ AgenticToolset.guidance()
	-> self.instructions
<< triggered by >> action: guidance, MCP prompt body assembly

---

# Behavior sketch (BDD)

Port to `context_tools/context_guidance/guidance_spec.py`. Every `it` body: `# BDD: SIGNATURE` until development fidelity.

**bdd-behavior shared rules** (validate every line against these):

- **observable-behavior** — `it should` states return value, file on disk, or agent-visible text — not private helpers or class names.
- **describe-is-subject-not-internal** — outer `describe` is a file, folder, deploy tree, or context tool module — never `Markdown`, `Deployment`, `Harness`, …
- **describe-is-plain-english** — no decorator symbols or type syntax in `describe` / `that` / `with` / `it should` labels; put exact paths and APIs on `->` port lines beneath the `it`.
- **state-not-when** — never `when`; use `that` for finalized events (`that has been deployed`), `with` for standing conditions.
- **nest-by-enabling-events** — each nested block must be a real precondition for the outcomes below it.
- **domain-vocabulary** — use model terms in outcomes: **context guidance**, **fidelity guidance**, `context_guidance.module_dir`, fidelity name, context guidance instructions. Never **practice host** or **practice-wide**.
- **usage-order-behaviors** — layers below follow co-located file → minimal guidance → toolset → shared contexts format → fidelities → context guidance → deploy → MCP → hooks.

**Implementation order** — green each layer before the next.

| Layer | Test subject | Depends on |
| ----- | ------------ | ---------- |
| 1 | Co-located markdown section as string — correct module file only | — |
| 2 | Minimal tool host with compound instructions and catalog only | layer 1 |
| 3 | Toolset module with agent-instructions operations | layer 2 |
| 4 | Shared contexts format on context guidance — single file or section files | layer 1–2 |
| 5 | Fidelity sections in shared contexts format — same file or fidelities folder | layer 4 |
| 6 | Context guidance for a context tool such as bdd or stories | layer 3–5 |
| 7 | Deploy output trees per IDE host | layer 6 |
| 8 | MCP manifest and running stdio host | layer 7 |
| 9 | Hooks config and hook skill files | layer 7 |
| 10 | Catalog pages and satisfy after validate | layer 2+ |

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

## Layer 3 — a toolset module with operations

```
describe a toolset module with several agent-instructions operations
  with the instructions property read on a loaded instance
    it should assemble one compound instructions string from each registered operation
    -> instructions_registry
  with the catalog property read on the same instance
    it should assemble catalog from its catalog properties then from tools and registered operations
```

---

## Layer 4 — shared contexts format on context guidance

**Shared contexts format** — the `# Contexts` chapter template (`context-tool-resource-model.md` § Contexts file layout; scaffold seed in `create_context_tool/templates/domain-md.md`). Context guidance body before `## Fidelities`:

```
# Contexts
{preamble before first ##}     → context property
## Guidance                     → guidance property
## Shared rules                 → rules property — scanner bullets

## Fidelities
  … fidelity sections — layer 5 …
```

**Share** — Mamba `shared_context` / `included_context`: define read outcomes once, each on-disk layout `describe` only sets up fixtures in `before.each` then pulls in the shared tree. Resolution order matches today's `@instruction` slots: `{label}/` folder merged, then `{label}.md`, then `## {Label}` in `{domain-slug}.md` beside the module.

```python
from mamba import description, context, it, before, shared_context, included_context

with shared_context('shared contexts format on context guidance'):
    with context('a Contexts chapter and Guidance and Shared rules before Fidelities'):
        with context('the context property read on context guidance'):
            with it('should return the Contexts preamble on context guidance only'):
                # BDD: SIGNATURE

        with context('the guidance property read on context guidance'):
            with it('should return the Guidance section body only'):
                # BDD: SIGNATURE

        with context('a Shared rules section containing scanner bullets'):
            with context('the rules property read on context guidance'):
                with it('should parse bullets into rules whose slugs match the scanner registry'):
                    # BDD: SIGNATURE
                with it('should expose slug body and optional fidelity on each rule for scan and later deploy'):
                    # BDD: SIGNATURE

        with context('the instructions property read on context guidance'):
            with it('should join context guidance formatted rules and templates selected by format in one string'):
                # BDD: SIGNATURE

    with context('a templates folder beside the module'):
        with context('template files such as slug-templates and slug-sketch inside the folder'):
            with context('the templates property read on context guidance'):
                with it('should map each format key to a relative path under templates'):
                    # BDD: SIGNATURE
                with it('should keep existing filenames without renaming to slug-fidelity-format'):
                    # BDD: SIGNATURE
            with context('one format key selected on that property'):
                with it('should return the file content at the mapped path'):
                    # BDD: SIGNATURE

with description('a context tool module with one domain markdown file named for the context tool'):
    with before.each:
        # {domain-slug}.md at module_dir following the shared contexts format
        ...

    with included_context('shared contexts format on context guidance'):
        pass

with description('a context tool module with section files and subsection folders named for the context tool'):
    with before.each:
        # contexts as contexts.md or contexts/; guidance as guidance.md or guidance/;
        # shared rules as rules.md or rules/ beside the module
        ...

    with included_context('shared contexts format on context guidance'):
        pass
```

---

## Layer 5 — fidelity sections in shared contexts format

Fidelity blocks under `## Fidelities` in the same template — `## {name}` with optional `### Guidance` and `### Rules`, or one file or folder per fidelity name when split on disk.

```python
with shared_context('fidelity sections in shared contexts format'):
    with context('fidelity guidance whose name matches one fidelity heading'):
        with context('the guidance property read on that fidelity guidance'):
            with it('should return Guidance under that fidelity name only'):
                # BDD: SIGNATURE
        with context('the rules property read on that fidelity guidance'):
            with it('should return Rules under that fidelity name as a rule list'):
                # BDD: SIGNATURE
            with it('should not include rules from sibling fidelity sections'):
                # BDD: SIGNATURE

    with context('two fidelities declared shallower before deeper in the collection'):
        with context('the instructions property read on the deeper fidelity guidance'):
            with it('should include prior fidelity sections in context in declaration order'):
                # BDD: SIGNATURE
            with it('should not include later fidelity sections or sibling templates'):
                # BDD: SIGNATURE
            with it('should not inline examples into fidelity instructions'):
                # BDD: SIGNATURE
        with context('the templates property read on the deeper fidelity guidance'):
            with it('should return only that fidelity entries from the templates scan'):
                # BDD: SIGNATURE
        with context('one format key selected on that fidelity guidance'):
            with it('should apply template line filtering when produce fidelities share one templates file'):
                # BDD: SIGNATURE
        with context('the catalog property read on the deeper fidelity guidance'):
            with it('should stack prior fidelity catalog sections like instructions'):
                # BDD: SIGNATURE
        with context('the rules property read on that fidelity guidance'):
            with it('should match the same bullets already formatted into fidelity instructions'):
                # BDD: SIGNATURE

with description('a guidance collection on context guidance'):
    with context('the instructions property read on the collection'):
        with it('should join each fidelity instructions string in declaration order'):
            # BDD: SIGNATURE
    with context('lookup by domain name'):
        with it('should return fidelity guidance for that name'):
            # BDD: SIGNATURE
    with context('lookup by stage key and sketch'):
        with it('should return the sketch fidelity from the stage index'):
            # BDD: SIGNATURE
    with context('lookup by stage alias'):
        with it('should return the same fidelity as lookup by domain name'):
            # BDD: SIGNATURE

with description('a context tool module with one domain markdown file named for the context tool'):
    with before.each:
        # Fidelities and named fidelity headings inside {domain-slug}.md
        ...

    with included_context('fidelity sections in shared contexts format'):
        pass

with description('a context tool module with a fidelities folder beside the module'):
    with before.each:
        # one file or subfolder per fidelity name; guidance/rules split under each when needed
        ...

    with included_context('fidelity sections in shared contexts format'):
        pass
```

---

## Layer 6 — context guidance for a context tool

```
describe context guidance for a context tool such as bdd or stories
  with co-located domain markdown examples folder and templates folder using the shared contexts format
    with the instructions property read on context guidance
      it should equal context guidance instructions plus joined fidelity instructions sketch first
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

---

## Layer 7 — deploy output trees (skills, prompts, rules)

Deploy renders the same instructions and rules strings as layers 1–6. Observe files on disk.

```
describe a Cursor deploy output tree
  that has been deployed for a context tool such as stories
    it should write a router skill file whose body equals context guidance instructions
    -> .cursor/skills/{slug}/SKILL.md
    it should write one fidelity command file per fidelity whose body equals that fidelity instructions
    -> .cursor/commands/{slug}-{fidelity}.md
    it should write one rules file per context guidance rule slug
    -> .cursor/rules/{slug}.mdc
    it should write one fidelity rules file per fidelity rule slug
  that has been deployed for a bare utility toolset such as git
    with an operation published as both skill and agent instructions
      it should write one skill file for that operation without a router skill or fidelity commands
    with an agent-tool operation only
      it should not write a standalone skill file unless skill or prompt is also published
  that has been deployed for a single source name filter
    it should emit only that tool router fidelity commands and operation files

describe a VS Code deploy output tree
  that has been deployed for a context tool such as stories
    it should write fidelity command files under github prompts not under cursor commands
    -> .github/prompts/{slug}-{fidelity}.md

describe deployed skill and command bodies
  that has been deployed with cli transport
    it should append the CLI invoke fence at the bottom of every skill command and rules body
  that has been deployed with mcp transport
    it should append the same MCP tool invoke tail on every deployed markdown body kind

describe deploy coverage for a registered context tool
  that has been fully deployed
    it should emit router skill fidelity commands and operation artifacts in one pass
    -> deployContextSection; deployContextSectionFidelity per fidelity; deployToolset

describe deploy coverage for a registered utility toolset
  that has been fully deployed
    it should emit operation artifacts only without router or fidelity commands
    -> deployToolset; operation_writes not instructions_registry
```

---

## Layer 8 — MCP manifest and host

```
describe an MCP manifest file
  that has been written by a deploy with mcp enabled
    it should list stdio server command and comma-separated toolset refs for walked classes
    -> .cursor/mcp.json
  that has been written by a deploy with mcp disabled
    it should omit the MCP manifest file

describe a router skill body
  that has been deployed with mcp transport and an MCP-published operation on context guidance
    it should end with an MCP tool invoke tail in the markdown file
    it should record that operation for server enrollment without binding during deploy
    -> McpDeployment.mcp_operations; bind at server start only

describe a running MCP stdio host
  that has been started from manifest toolset refs after deploy
    it should enroll tools and prompts from recorded MCP operations without rescanning the class
    -> McpDeployment.bind; not McpToolset getmembers
  with a tools call for an enrolled tool name
    it should return the result of the loaded toolset operation

describe MCP server enrollment timing
  that has been deployed but not started
    it should not bind tool handlers during deploy
```

---

## Layer 9 — hooks deploy output

```
describe a Cursor hooks config
  that has been deployed with hook sources in the walk
    it should write hooks manifest entries for each registered hook event
    -> .cursor/hooks.json
    it should write hook skill files for hook-published agent-instructions operations
  that has been partially deployed with no hook sources emitted
    it should leave hooks manifest unchanged from a prior full deploy
```

---

## Layer 10 — catalog pages and satisfy

```
describe generated catalog pages
  that have been built from the guidance registry
    it should write each context guidance catalog property to its own page
    it should write each fidelity catalog property to its own page
    it should not scrape deployed markdown files or heading structure from disk

describe a satisfy run on a context tool
  that has run after validate
    it should apply fixes from the validate report
```
