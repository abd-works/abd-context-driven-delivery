# Guidance resource model — object model & BDD

Extract from `context-tool-resource-model.md`. **Canonical for object flows and BDD** — update here first; full doc summarizes and must stay aligned. **CE notation** per `clean_engineering` model fidelity. **BDD notation** per `bdd` behavior fidelity (`describe` / `that` / `with` / `it should` — never `when` for state). Tables, narrative, and rationale → full doc only.

---

# harness/markdown

- **Purpose:** Extract co-located markdown — not assembly. Convert that extract to HTML.
- **Seam (terms):** `@markdown`, `Markdown`, `HTML`, `AssetLocator`
- **Dependencies (one-way):** none — `AssetLocator` lives in this package

## HTML

+ HTML.from_markdown(text: str)
	// renamed from catalog — conversion of one markdown extract
------
----

## Markdown

+ Markdown.from_label(host, label: str)
------
----
+ extract(): str
	// this property is on a class — use that class’s file directory; no module_dir on the host
	-> AssetLocator.locate(class file directory, label, host.name)
+ html(): HTML
	// any @markdown property can convert its extract to HTML
	-> HTML.from_markdown(extract())
+ coerce(text: str, return_type): str | RulesCollection | dict[str, str] | HTML
	// return_type selects str, RulesCollection, templates path map, or HTML

## @markdown

+ @markdown(getter) -> property
	// property name = label; coerce to annotated return type
	// annotated property reads as markdown (extract) or HTML (html)
	-> Markdown.from_label(owner, label)
	-> Markdown.extract()
	-> Markdown.html() when the read is HTML
	-> Markdown.coerce(return_type)

---

# context_guidance/guidance

- **Purpose:** Assemble agent instructions from `@markdown` properties; fidelity-scoped guidance nodes.
- **Seam (terms):** `Guidance`, `PracticeGuidance`, `FidelityGuidance`, `GuidanceCollection`, `RulesCollection`
- **Dependencies (one-way):** `harness/markdown`, `workspace`, `actions/scan`

## Guidance
+ Guidance()
	// base — shared context / guidance / rules; no fidelity; instructions live here
------
+ context: str
	// @markdown — # Contexts  for this host scope
+ guidance: str
	// @markdown
+ rules: RulesCollection
	// @markdown — coerce bullets to RulesCollection
	// @rules — deploy writes one .mdc per rule because of this mark
+ templates: dict[str, str]
	// @markdown — format key → relative path under templates/; subscript reads content
+ format: str
	// active format for templates[format] in instructions assembly
+ default_format: str
	// fallback when format unset; invoke copies to format on active host
+ name: str | None
	// scopes @markdown extract; None on practice guidance
----
+ instructions: str
	// @property — context + guidance + format_rules(rules) + templates[format]; same logic on every host
+ guidance(): str
	// @agent_instructions @skill — same operation deploy as any other recipe; file kind is the skill mark
	-> self.instructions

## PracticeGuidance : Guidance
	// not an AgenticToolset — generate / satisfy / validate / scan are their own hosts
	// guidance() and rules still deploy through the same leaves as any marked member

+ PracticeGuidance(format, path, session, workspace)
------
+ << composition >> fidelities: GuidanceCollection
+ fidelity: str | None
	// active domain key at invoke; format from the matching child in fidelities
+ examples: str
	// @markdown — not in instructions
+ << association >> workspace: Workspace
+ << association >> scanner: Scan
----
+ rules: RulesCollection
	// inherited — still @rules from Guidance
+ instructions: str
	// @property override — super.instructions + fidelities.instructions
	-> Guidance.instructions
	-> GuidanceCollection.instructions

## GuidanceCollection : Guidance
	// Composite — every Guidance read iterates children

+ GuidanceCollection(entries: dict[str, Guidance])
	// keyed children — key is the child's name; FidelityGuidance, nested practice, another collection, …
------
+ entries: dict[str, Guidance]
----
+ context: str
	-> join each child's context
+ guidance: str
	-> join each child's guidance
+ rules: RulesCollection
	// Composite — keyed like entries; each value is that child's RulesCollection
	-> each key → that child's rules
+ templates: dict[str, str]
	-> merge each child's templates
+ instructions: str
	-> join each child's instructions
+ html() on any of those reads
	-> each child read as HTML, then join
+ iter()

## FidelityGuidance : Guidance

+ FidelityGuidance(name, stage, default_format, practice_guidance)
------
+ << association >> practice_guidance: PracticeGuidance
	// parent practice — child points up; the base does not
+ fidelity: str
	// domain fidelity key — equals name; read-side only
+ stage: str
	// CDD stage key
----
+ context: str
	// inherited @markdown — this name’s scope plus prior ## {name} blocks in declaration order
+ instructions: str
	// @property — Guidance assembly scoped by name; context already holds the prior stack
+ guidance(): str
	// @agent_instructions @command — same operation deploy; this subclass marks the file a command
	-> self.instructions
+ rules: RulesCollection
	// inherited — still @rules from Guidance

---

# actions/scan

- **Purpose:** Honor each rule against the current context. Validate is agentic and lives on the rule; the checker lives on the rule too.
- **Seam (terms):** `Rule`, `RulesCollection`, `Scanner`, `Scan`
- **Dependencies (one-way):** host `rules`

## Rule

+ Rule(slug: str, body: str, fidelity: str | None = None)
------
+ slug: str
	// name of the scanner that implements this rule, when one exists
+ body: str
+ fidelity: str | None
+ scanner: Scanner | None
	// zero or one — go to the rule; scanners/{slug}_scanner.py beside the practice
	-> None when that script is absent
----
+ validate(): str
	// agentic — evaluate the current context against this rule's body
	// planned body always names the run kind — mark is only the default if a call is bare
	-> instructions(
		self.body
	)
	-> tools(
		self.scanner.scan
	)
	// tools(...) omitted when scanner is None

## RulesCollection
	// Composite of Rule — batch validate so rules are not invoked one at a time

+ RulesCollection(entries: dict[str, Rule | RulesCollection])
	// keyed children — leaf slug or child guidance name
------
+ entries: dict[str, Rule | RulesCollection]
----
+ validate(): str
	// planned body — every child explicit
	-> instructions(
		each child's validate()
	)
+ scan(paths)
	-> tools(
		each Rule.scanner.scan when present
	)

## Scanner

+ Scanner(rule: Rule)
----
+ scan(file_path: Path): list

## Scan

+ Scan.bound_to(host)
----
+ scan(paths)
	-> tools(
		host.rules.scan
	)

---

# actions/validate

- **Purpose:** Agentic validate against the current context. Default is every rule; pass one rule to narrow.
- **Seam (terms):** `Validate`
- **Dependencies (one-way):** `Rule`, `RulesCollection`

## Validate
	// LifecycleAction — changing: default all rules, optional one rule

+ Validate()
------
----
+ validate(tools, rule: Rule | None = None): str
	// planned body — always wrap; mark is default only when a call is bare
	-> instructions(
		host.rules.validate
	)
	// or, when one rule passed:
	-> instructions(
		rule.validate
	)

---

# harness/agent_tools

- **Purpose:** One type. Two author wrappers on methods: `@agent_tool` and `@agent_instructions`. Unmarked methods are plain operations. Do not split Toolset / InstructionSet.
- **Seam (terms):** `AgenticToolset`, `@agentic_toolset`, `@agent_tool`, `@agent_instructions`
- **Source:** `.sessions/closed/eval-consolidate-workspace/workspace-eval-oo-sketch.md` § Agent annotations

## AgenticToolset

+ AgenticToolset()
	// class decorator @agentic_toolset
	// PracticeGuidance deploys as guidance documents; this type deploys as operation files
------
+ tools: dict
	// @agent_tool registry
+ instructions_registry: Mapping
	// @agent_instructions members — class/extension discovery (was `actions`)
----
+ instructions: str
	// compound instructions — own markdown + iterate instructions_registry
+ guidance(): str
	-> self.instructions
+ tools(*calls)
	// any number of calls — same path as @agent_tool; agent invokes each
	-> each call as if that member were @agent_tool
+ instructions(*calls)
	// any number of calls — same path as @agent_instructions; expand each
	-> each call as if that member were @agent_instructions

// Method marks are the default when a call is bare: @agent_tool, @agent_instructions, unmarked = plain
// Planned recipe bodies always wrap — make every call explicit even when the mark would have implied it
// Precedent — one call per line:
//	tools(
//		self.some_method,
//		self.other_class.some_other
//	)
//	instructions(
//		self.dynamically_add_ins()
//	)

---

# installation

- **Purpose:** *Deployment* + *Harness* + MCP runtime. **Extract** what `Harness.install` / `operation_writes` already do — same artifacts; not new deploy behavior.
- **Seam (terms):** `Deployment`, `MarkdownInstallation`, `McpInstallation`, `HookInstallation`, `Harness`, `McpServer`, `McpTool`, `McpPrompt`
- **Dependencies:** registry. Stdio entry: `python -m installation.mcp` loads *McpServer* from `installation/mcp`.

## Deployment

+ Installation(ide, path)
-----
+ ide: str
+ path: Path
----
+ deploy(host)
	when host is PracticeGuidance: installPracticeGuidance(practice_guidance)
	when host is AgenticToolset: deployAgenticToolset(host)

+ installPracticeGuidance(practice_guidance: PracticeGuidance)
	-> deployGuidance(practice_guidance)
	-> installFidelityGuidance(fidelity) per practice_guidance.fidelities

+ deployGuidance(guidance: Guidance)
	// visit this host’s marked members — same leaves as a toolset, not a second writer
	-> installAgentInstructions(guidance, guidance.guidance) when guidance() is marked
	-> write rules files from guidance.rules when rules is @rules

+ installFidelityGuidance(fidelity: FidelityGuidance)
	// same visit on that fidelity — guidance() is @command there
	-> installAgentInstructions(fidelity, fidelity.guidance) when guidance() is marked
	-> write rules files from fidelity.rules when rules is @rules

+ deployAgenticToolset(host)
	-> for each operation_writes row on the host class:
		when invoke == action: installAgentInstructions(host, operation)
		when invoke == tool: installAgentTool(host, operation)

+ installAgentInstructions(host, operation)
	// one write for any @agent_instructions member — utility generate, context guidance(), fidelity guidance()
	// file kind from @skill / @command / @rules stacked on that member

+ installAgentTool(host, operation)
	// @agent_tool — file only if @skill/@command stacked

## MarkdownInstallation : Installation

+ MarkdownInstallation(ide, path)
	// every file is a skill, a command, or a rule — @skill / @command / @rules on the member
------
----
+ deployGuidance(guidance: Guidance)
	// visit only — calls installAgentInstructions / rules write; do not reimplement render
+ installFidelityGuidance(fidelity: FidelityGuidance)
	// visit only — same leaves
+ installAgentInstructions(host, operation)
	// write the skill, command, or rule for that member — relative_path + render
+ installAgentTool(host, operation)
	// write the skill or command for that member when those marks are stacked
+ relative_path(mark, guidance, member): Path
+ render(mark, section, member): str
	// iterate marked members — @skill / @command / @rules writes the slash file
	when member is not @mcp:
		-> that operation’s instructions + CLI fence
	when member is @mcp:
		-> host.context
		-> render_mcp_invoke(toolset_ref, member)
		// tail is that string — do not call the MCP server at deploy
+ mark(member) -> member

+ @skill(name: str | None = None) -> member
+ @command(name: str | None = None) -> member
+ @rules(member) -> member
+ render_mcp_invoke(toolset_ref, member): str
	// string from the member — slug.operation + signature; not a live MCP call
	-> Use MCP tool: `{slug}.{member}(...)`

## McpInstallation : Installation

+ McpInstallation(ide, path, toolset_ref: str)
	// leaf writes only — record @mcp and mcp.json; the toolset walk stays on Deployment
------
+ toolset_ref: str
+ mcp_operations: list  // filled by the leaf writes — bind reuses, no second scan
----
+ deployGuidance(guidance: Guidance)
	// visit only — record via the same installAgentInstructions leaf when guidance() is @mcp
+ installFidelityGuidance(fidelity: FidelityGuidance)
	// visit only — same leaf
+ installAgentInstructions(host, operation)
	// @mcp on an @agent_instructions member — record op; mcp.json slice
+ installAgentTool(host, operation)
	// @mcp on an @agent_tool member — record op; mcp.json slice
+ bind(server: McpServer)
	// server start only — enroll McpTool / McpPrompt from mcp_operations; NOT called from deploy

+ @mcp(method) -> method

## HookInstallation : Installation

+ HookInstallation(ide, path)
	// same deploy API as base — implement the leaf writes; the walk stays on Deployment
------
+ deployGuidance(guidance: Guidance)
	// write hook config for the practice router
+ installFidelityGuidance(fidelity: FidelityGuidance)
	// write hook config for that fidelity command
+ installAgentInstructions(toolset, operation)
	// @hook stacked on @agent_instructions — only when host is AgenticToolset

+ @hook(event: str | None = None) -> member
+ @agent(name: str | None = None) -> member
+ @agent_guidance(name: str | None = None) -> member

## Harness

+ Installer(ide=None, path=None)
	// new with ide + path, or load the harness file — same two properties either way
	// today: installation/.install-state.json
	// MCP is @mcp on the member, not a harness flag
------
+ ide: str
	// Cursor | VS Code | Kilo | …
+ path: Path
	// exact folder — Cursor → .cursor; VS Code → .github; Kilo → .kilo when not given
+ << composition >> deployment: Installation
	// constructed with this harness’s ide + path
----
+ install()
	-> registry.load()
	-> deployment.deploy(host) per registry entry
	-> write ide + path to the harness file
	// side effect — artifacts on disk; no aggregate return

## McpServer

+ McpServer()
+ mcp_installations: list[McpInstallation]  // one per toolset_ref from mcp.json
----
+ start(toolset_refs: tuple[str, ...])
	// today: load instance + McpToolset getmembers rescan — target: McpInstallation per ref, bind()
	-> for ref in toolset_refs: McpInstallation(ref).bind(self)
+ invoke_tool(mcp_name, arguments)
+ invoke_prompt(mcp_name, arguments)
	// stdio host — refs from mcp.json

---

# tools/catalog_generator

## Catalog : HTML

+ Catalog.from_registry()
+ generate_catalog(out_root: Path)
	-> each practice guidance @markdown property as HTML
	-> each fidelity guidance @markdown property as HTML

---

# Object flows

**Implementation order** matches BDD layers below: markdown → Guidance → AgenticToolset **+deploy** → Guidance **+deploy** → shared contexts **+deploy** → fidelities + assembly **+deploy** → MCP → Catalog : HTML → hooks last.

## Compound doc

+ Guidance.instructions
	-> own markdown properties → markdown compound doc
+ AgenticToolset.instructions
	-> iterate instructions_registry — assemble markdown per @agent_instructions operation
	// read-side registry walk — deploy uses operation_writes AST walk, not this collection

## Instructions assembly

+ Guidance.instructions
	-> self.context + self.guidance + format_rules(self.rules) + self.templates[format]
	// FidelityGuidance — same property; name scopes @markdown extract only
+ GuidanceCollection.{context,guidance,templates,instructions}
	-> iterate children; join each child's same read
+ GuidanceCollection.rules
	-> RulesCollection keyed by entries keys; each value is that child's RulesCollection
	// Composite — rules stay partitioned by child; validate() batches every child
+ PracticeGuidance.instructions
	-> super.instructions + fidelities.instructions

<< triggered by >> Agent, deploy, guidance action

## Validate

+ Validate.validate(tools, rule=None)
	-> instructions(
		host.rules.validate
	)
	-> or instructions(
		rule.validate
	)
+ Rule.validate()
	-> instructions(
		self.body
	)
	-> tools(
		self.scanner.scan
	)
+ RulesCollection.validate()
	-> instructions(
		each child's validate()
	)
<< triggered by >> Agent, Validate action

## @markdown extract

+ host.{label}
	-> Markdown.from_label(host, label)
	-> Markdown.extract()
		-> AssetLocator.locate(class file directory, label, host.name)
	-> Markdown.html() when the read is HTML
	-> Markdown.coerce(return_type)
<< uses >> AssetLocator

## HTML

+ Markdown.html()
	-> HTML.from_markdown(extract())
<< triggered by >> Catalog, any @markdown property read as HTML

## Deploy

+ Installer(ide, path) or load the harness file
	-> Installation(ide, path) — MarkdownInstallation + McpInstallation (+ HookInstallation when hooks)
+ Harness.install()
	-> registry.load()
	-> deployment.deploy(host) per registry entry
		-> installPracticeGuidance(practice_guidance)
			-> deployGuidance — visit marked members; guidance() → installAgentInstructions; rules → @rules write
			-> installFidelityGuidance per fidelity — same leaves
		-> deployAgenticToolset(bare AgenticToolset)
			-> installAgentInstructions / installAgentTool per operation_writes row
		-> McpInstallation leaf: if the member is @mcp, record it and write mcp.json
	-> write ide + path to the harness file
<< triggered by >> Harness.install
	-> render: member not @mcp → that operation’s instructions + CLI fence; member is @mcp → context section + MCP invoke tail

## MCP server start

+ McpServer.start(toolset_refs from mcp.json)
	-> for ref: McpInstallation(ide, path, ref).bind(self)
		-> enroll from mcp_operations recorded when that member was @mcp — not getmembers rescan
<< triggered by >> Cursor spawns stdio host — not during install

## MCP invoke

<< triggered by >> Agent reads deployed skill or command invoke tail or host tools/call / prompts/get
	-> fixture: member annotated @mcp and deployed
	-> McpServer.invoke_tool("{slug}.{member}", arguments)
	-> McpServer.invoke_prompt("{slug}.{member}", arguments)

## Runtime guidance

+ Guidance.guidance()
	-> self.instructions
+ FidelityGuidance.guidance()
	-> self.instructions
+ AgenticToolset.guidance()
	-> self.instructions
<< triggered by >> action: guidance, deployed skill or command body

## Recipe callee

+ @agent_instructions body walk
	when call is in tools(*calls): same as @agent_tool — agent invokes
	when call is in instructions(*calls): same as @agent_instructions — expand
	when call is bare: callee mark is the default (@agent_tool / @agent_instructions / unmarked = plain)
	// planned bodies wrap every call — do not leave the default implied
<< triggered by >> Agent follows a recipe

---

# Behavior sketch (BDD)

Port each layer into the package that owns the subject:

| Layer | Spec |
| ----- | ---- |
| 1 | `harness/markdown/markdown_spec.py` |
| 2, 5–6 read | `harness/guidance/guidance_spec.py` |
| 3 read | `harness/agent_tools/agent_tools_spec.py` |
| 3–6 deploy | `installation/installation_spec.py` |
| Rule / Validate | `actions/scan/rule_spec.py`, `actions/validate/validate_spec.py` |
| 7 | `installation/mcp_server_spec.py` |
| 8 | `tools/catalog_generator/catalog_spec.py` |
| 9 | `installation/hook_installation_spec.py` |

Read a host, then deploy that same host: skill, command, or rule from the mark. `@mcp` writes the context section plus the invoke tail. Layer 7 is manifest and host invoke.

| Layer | Test subject | Depends on |
| ----- | ------------ | ---------- |
| 1 | Markdown — co-located section as string or HTML; this class file directory only | — |
| 2 | Context guidance — compound `instructions` | layer 1 |
| 3 | Agentic toolset — read `instructions`, then deploy skill and command from the marks | layer 2 |
| 4 | Context guidance — same `instructions`, then deploy skill and rules from the marks | layer 2 |
| 5 | Practice guidance — shared contexts read, then deploy skill and rules (no fidelity guidance yet) | layer 1–2, 4 |
| 6 | Fidelity guidance read and command deploy, then practice guidance assembly and full tree | layer 5 |
| 7 | MCP manifest then host invoke — `@mcp` member deployed → start from manifest → tools/call or prompts/get | layer 3–6 fixtures |
| 8 | Catalog pages from each host `@markdown` property as HTML | layer 1+ |
| 9 | Hooks config and hook skill files — last; hooks deploy not complete in harness today | layer 8 |

---

## Implementation — one layer per turn

**0. Isolate first — before any layer.** Backup the remodeled production trees (`markdown_extractor`, `BaseContextTool`, Harness deploy, `McpToolset`, …), then move those trees to `legacy-no-longer-valid/` at the repo root, keeping their relative paths. That folder is detailed requirements only: what files were written, what strings came back, what a deploy tree looked like. It is not the design. Design is this document. Do not write a layer while those modules still sit on the live import path — the old types and the new names get mixed. If a behavior detail is missing later, read `legacy-no-longer-valid/`. Write new modules from this sketch into their target paths.

**Golden deploy reference:** `.cursor copy/` at the repo root (local snapshot of a successful deploy). Compare structure and bodies to that tree. File kind follows the mark on the member — `@skill` / `@command` / `@rules` — even when the snapshot wrote a fidelity as a skill. Practice skill `.cursor/skills/{slug}/SKILL.md`, fidelity command `.cursor/commands/{slug}-{fidelity}.md`, rules under `.cursor/rules/`. `mcp.json` shape and MCP invoke tails stay. Target markdown may add `## Fidelities` for mapping.

**No fake deploy tests.** Every deploy `it should` runs the real `Harness.install` (or the extracted `Deployment` once migrated) into a temp or fixture directory, then reads files from disk. Do not mock `Harness`, `Deployment`, or `operation_writes` for outcomes that stakeholders see on disk. Read-path tests use real co-located fixtures beside a real module directory. Temporary throwaway modules are fine; stubby mocks of the deploy pipeline are not.

**One layer = one `/turn`.** Do not stack layers in a single commit. Per turn:

1. **`generate`** — `@bdd-development` for the layer’s `guidance_spec.py` (or the module that owns that layer); `@clean-engineering-model` when the layer introduces or moves types.
2. **Write** — minimum production code for that layer only, from this sketch. Do not grow the types in `legacy-no-longer-valid/`.
3. **Real environment** — run `install` (mcp when the layer includes MCP); diff against `.cursor copy/` for the fixtures in scope; run mamba on the layer spec.
4. **Subagent spot-check** — for MCP invoke and skill bodies (layers 3–7), run a sub-agent against deployed `SKILL.md` or `McpServer.invoke_tool` / `invoke_prompt` instead of asserting only string contains in unit tests.
5. **`/turn`** — commit with `utility: turn`, message names the layer number and what was written.

**Isolate (done):** remodeled trees live under `legacy-no-longer-valid/` (requirements only).

**Layer 1 (done after isolate):** `harness/markdown/Markdown` + `@markdown` over `AssetLocator`; `harness/guidance/guidance_spec.py` layer 1 block with real fixtures under `fixtures/sample_tool` and `fixtures/other_tool`.

**Layer 2:** `Guidance` compound `instructions` — context + guidance + formatted rules + selected template.

---

## Layer 1 — markdown

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
      -> Markdown locates the host class directory; this module only
  with a markdown-backed string property
    with that property read as HTML
      it should return HTML formatted from that section body
      -> Markdown.html(); HTML.from_markdown
```

---

## Layer 2 — context guidance instructions

```
describe context guidance
  with the instructions property read
    it should join context, guidance, formatted rules, and the template for the active format
    it should expose instructions as one compound property not as a single markdown label
    -> Guidance.instructions; not a @markdown label
```

---

## Deploy shared contexts (define once)

Reuse in every layer’s deploy subsection via `it_behaves_like`. Each layer’s `describe` only runs `install` on **its** fixture in `before.each`.

```
shared context "deploy bare agentic toolset operations"
  with a Cursor deploy output tree
    it should write one skill file per agent-instructions operation marked for skill
    -> .cursor/skills/{operation}/SKILL.md or flat skill path per harness convention
    it should write one command file per agent-instructions operation marked for command
    -> .cursor/commands/{operation}.md
    it should write a skill or command for an agent-tool operation only when that operation is also marked skill or command
    it should not write a context guidance skill or fidelity commands
    -> deployAgenticToolset; PracticeGuidance is not this host
  with a deploy output tree
    it should render skill and command bodies from the same instructions strings the read path assembles
    -> operation_writes rows; not instructions_registry

shared context "deploy context guidance skill and rules"
  with a Cursor deploy output tree
    it should write a skill file whose body equals context guidance instructions
    -> guidance() is @skill; .cursor/skills/{slug}/SKILL.md
    it should write one rules file per rule slug
    -> rules is @rules; .cursor/rules/{slug}.mdc

shared context "deploy practice guidance skill and rules"
  with a Cursor deploy output tree
    it should write a skill file whose body equals practice guidance instructions
    -> inherited @skill; .cursor/skills/{slug}/SKILL.md
    it should write one practice guidance rules file per practice guidance rule slug
    -> .cursor/rules/{slug}.mdc

shared context "deploy fidelity sections on practice guidance"
  with a Cursor deploy output tree
    it should write one fidelity command file per fidelity whose body equals that fidelity instructions
    -> .cursor/commands/{slug}-{fidelity}.md
    it should write one fidelity rules file per fidelity rule slug

shared context "deploy cli transport on markdown bodies"
  with deployed skill command and rules bodies
    it should append the CLI invoke fence at the bottom of each body
    -> MarkdownInstallation.render when the member is not @mcp

shared context "deploy mcp invoke tail on markdown bodies"
  with a deployed skill file for an mcp-published agent-instructions operation
    it should still write the skill file so there is a slash command
    it should put the context section at the top of the file
    it should not put the full instructions in that file
    it should place one MCP invoke tail after the context section
    it should name the tool as {toolset-slug}.{operation} with the method parameter signature in backticks
    -> Use MCP tool: `bdd.generate(...)`; MarkdownInstallation.render_mcp_invoke
    it should not append the CLI tools.ps1 invoke fence
  with a deployed command file for an mcp-published command operation
    it should write the context section plus MCP invoke tail — not the full command body
  with a deployed practice skill when guidance is mcp-published
    it should write the context section plus MCP invoke tail — not practice guidance instructions
  with a deployed fidelity command when that fidelity guidance is mcp-published
    it should write the context section plus MCP invoke tail — not fidelity instructions
  with a deployed rules file when that rule is mcp-published
    it should write the context section plus MCP invoke tail — not the full rule body

shared context "deploy mcp enrollment without bind"
  with a deploy output tree for hosts whose members are annotated mcp
    it should record each mcp-published operation for server enrollment
    it should not bind tool handlers during deploy
    -> McpInstallation.mcp_operations; bind at server start only

shared context "deploy vscode command paths"
  with a VS Code deploy output tree
    it should write fidelity command files under github prompts not under cursor commands
    -> Installer(ide=VS Code); .github/prompts/{slug}-{fidelity}.md

shared context "deploy full context tool coverage"
  with a registered practice guidance host fully deployed
    it should emit the practice skill, practice rules, fidelity commands, and fidelity rules in one pass
    -> installPracticeGuidance → deployGuidance then installFidelityGuidance per fidelity
```

---

## Layer 3 — agentic toolset read and deploy

### Read

```
describe a toolset module with several agent-instructions operations
  with the instructions property read on a loaded instance
    it should assemble one compound instructions string from each registered operation
    -> instructions_registry
```

### Deploy

Fixture: small `AgenticToolset` with `@skill` / `@command` on some `@agent_instructions` operations, optional `@agent_tool`, co-located markdown for invoke tails.

```
describe a bare agentic toolset registered for deploy
  with before.each that runs install on that fixture
  it_behaves_like "deploy bare agentic toolset operations"

describe a bare agentic toolset with mcp-published operations registered for deploy
  with before.each that runs install on that fixture
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

---

## Layer 4 — context guidance skill and rules

### Read

Same compound `instructions` as layer 2. This layer deploys those marks through the same leaves as layer 3 — `guidance()` is `@agent_instructions` `@skill`, `rules` is `@rules`.

```
describe context guidance
  with the instructions property read
    it should join context, guidance, formatted rules, and the template for the active format
```

### Deploy

```
describe context guidance registered for deploy
  with before.each that runs install on that fixture
  it_behaves_like "deploy context guidance skill and rules"

describe context guidance with mcp-published guidance registered for deploy
  with before.each that runs install on that fixture
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

---

## Layer 5 — practice guidance shared contexts

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

Define once — all `it should` read **context guidance** properties on **practice guidance** (assigned in `before.each` below):

```
shared context "shared contexts format on practice guidance"
  with the context property read
    it should return the Contexts preamble
  with the guidance property read
    it should return the Guidance section body only
  with a Shared rules section containing scanner bullets
    with the rules property read
      it should parse bullets into a rules collection
      it should expose slug, body, optional fidelity, and zero or one scanner on each rule
    with validate read on one rule
      it should return instructions to evaluate the current context against that rule
      it should tell the agent to run the scanner when the rule has one
    with validate read on the rules collection
      it should return every child rule's validate instructions in one shot
  with the instructions property read
    it should join context, guidance, formatted rules, and the template for the active format
    -> PracticeGuidance inherits Guidance.instructions; fidelities are empty in this layer
  with a templates folder beside the module
    with template files such as slug-templates and slug-sketch inside the folder
      with the templates property read
        it should map each format key to a relative path under templates
      with one format key selected
        it should return the file content at the mapped path
```

Use in each layout — **assign practice guidance, then include shared context**:

```
describe a context tool module with one domain markdown file named for the context tool
  with before.each that assigns practice guidance from {domain-slug}.md beside the class
  it_behaves_like "shared contexts format on practice guidance"

describe a context tool module with section files and subsection folders named for the context tool
  with before.each that assigns practice guidance from contexts guidance and rules files or folders beside the module
  it_behaves_like "shared contexts format on practice guidance"
```

### Validate action

Same fixtures as Read. Default is every rule; pass one rule to narrow.

```
describe a validate action on practice guidance
  with no rule passed
    it should return validate instructions for every rule in one shot
    -> Validate.validate(tools); host.rules.validate()
  with one rule passed
    it should return validate instructions for that rule only
    -> Validate.validate(tools, rule)
```

### Deploy

Fixture: same layouts as Read — shared contexts on context guidance, no fidelity sections yet (or empty `## Fidelities`).

```
describe a context tool module with shared contexts format registered for deploy
  with before.each that runs install on the single-file or section-file fixture from Read
  it_behaves_like "deploy practice guidance skill and rules"

describe a context tool module with shared contexts format and mcp on the practice skill registered for deploy
  with before.each that runs install on the layer 5 read fixture
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

---

## Layer 6 — fidelity guidance and practice guidance assembly

Fidelity blocks under `## Fidelities` — `## {name}` with optional `### Guidance` and `### Rules`, or one file or folder per fidelity name when split on disk. `guidance()` on fidelity guidance is `@command`. **Deploy those commands as soon as fidelity instructions read is green** — before assembly read. Assembly read then full-tree deploy follow.

### Read — fidelity instructions from markdown

Define once — all `it should` read **fidelity guidance** (and the deeper fidelity in stacking cases) assigned in `before.each` below:

```
shared context "fidelity sections in shared contexts format"
  with the guidance property read on fidelity guidance
    it should return Guidance under that fidelity name only
  with the rules property read on fidelity guidance
    it should return a rules collection for that fidelity name only
    it should not include rules from sibling fidelity sections
  with two fidelities declared shallower before deeper in the collection
    with the instructions property read on the deeper fidelity guidance
      it should include prior fidelity sections in context in declaration order
      it should not include later fidelity sections or sibling templates
    with the templates property read on the deeper fidelity guidance
      it should return only that fidelity entries from the templates scan
    with one format key selected on the deeper fidelity guidance
      it should apply template line filtering when several fidelities share one templates file
    with a markdown-backed property read as HTML on the deeper fidelity guidance
      it should return HTML formatted from that fidelity section body
    with the rules property read on the deeper fidelity guidance
      it should match the same bullets already formatted into fidelity instructions
```

Use in each layout — **assign practice guidance and fidelity guidance from that layout, then include shared context**:

```
describe a context tool module with one domain markdown file named for the context tool
  with before.each that assigns practice guidance from {domain-slug}.md and fidelity guidance from a named ## heading under ## Fidelities
  it_behaves_like "fidelity sections in shared contexts format"

describe a context tool module with a fidelities folder beside the module
  with before.each that assigns practice guidance and fidelity guidance from files or subfolders under fidelities
  it_behaves_like "fidelity sections in shared contexts format"
```

### Deploy — fidelity commands and rules

Same fixtures as fidelity Read — prove command bodies equal each fidelity guidance `instructions` string before testing assembly.

```
describe a context tool module with fidelity sections registered for deploy
  with before.each that runs install on the single-file or fidelities-folder fixture from fidelity Read
  it_behaves_like "deploy fidelity sections on practice guidance"

describe a context tool module with fidelity sections and mcp on fidelity commands registered for deploy
  with before.each that runs install on that fixture
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"
```

### Read — collection and practice guidance assembly

```
describe a guidance collection of context guidance children
  with the instructions property read on the collection
    it should join each child instructions string in declaration order
  with the context property read on the collection
    it should join each child context string in declaration order
  with the guidance property read on the collection
    it should join each child guidance string in declaration order
  with the rules property read on the collection
    it should return a rules collection keyed by each child key
    it should keep each child's rules under that child's key
    -> RulesCollection; not a flattened list
  with validate read on that rules collection
    it should return every child rule's validate instructions in one shot
```

Practice guidance assembly — practice guidance reads context guidance from layer 5 plus fidelities from above; not a separate “named tool” layer. Use the same `before.each` fixtures as layer 5–6.

```
describe practice guidance with fidelities examples and templates beside the module
  with before.each that assigns practice guidance from the layer 5 and layer 6 fixtures
  with the instructions property read on practice guidance
    it should join context guidance instructions with each fidelity instructions in declaration order sketch first
    it should not inline examples into instructions
  with the examples property read on practice guidance
    it should return examples folder content as a separate property not inside instructions
  with a markdown-backed property read as HTML on practice guidance
    it should return HTML formatted from that property extract
  with format and default format set on practice guidance
    it should select the template for the active format in practice guidance instructions assembly
  with fidelity set at invoke on practice guidance
    it should resolve active format from the named fidelity default format
```

### Deploy — full practice guidance tree

One pass proves the practice skill, practice rules, fidelity commands, and fidelity rules together. Practice guidance is not an agentic toolset — operation files stay in layer 3.

```
describe a context tool module with fidelities and assembly registered for deploy
  with before.each that runs install on the layer 6 assembly fixture
  it_behaves_like "deploy practice guidance skill and rules"
  it_behaves_like "deploy fidelity sections on practice guidance"
  it_behaves_like "deploy full context tool coverage"

describe a context tool module with fidelities assembly and mcp-published members registered for deploy
  with before.each that runs install on the layer 6 assembly fixture
  it_behaves_like "deploy mcp invoke tail on markdown bodies"
  it_behaves_like "deploy mcp enrollment without bind"

describe practice guidance that has been deployed
  with members that are not annotated mcp
  it_behaves_like "deploy cli transport on markdown bodies"

describe practice guidance that has been deployed for VS Code
  with before.each that constructs Harness for VS Code and runs install on a layer 6 fixture
  it_behaves_like "deploy vscode command paths"
```

---

## Layer 7 — MCP manifest and host

MCP invoke tails on deployed skill, command, and rules files are proved incrementally in layers 3–6 via **deploy mcp invoke tail on markdown bodies**. Layer 7 proves **manifest → start → invoke** on the same fixtures. MCP is `@mcp` on the member — not a harness or `install` flag. The slash file is the context section plus the invoke tail; the running host returns the full instructions.

### Manifest

```
describe an MCP manifest file
  that has been written by a deploy whose walked members are annotated mcp
    it should list stdio server command and comma-separated toolset refs for walked classes
    -> .cursor/mcp.json
  that has been written by a deploy with no mcp-published members
    it should omit the MCP manifest file
```

### Host — invoke after deploy

Chain every runtime `it should` through: **member annotated mcp → deployed → server started from that deploy’s manifest → tools/call or prompts/get**. Reuse layer 3–6 fixtures; only the invoke kind changes.

```
describe a bare agentic toolset with an agent-tool operation annotated for mcp
  that has been deployed
    with an MCP server started from manifest toolset refs written during that deploy
      it should enroll that operation under the mcp name {slug}.{operation}
      it should enroll from mcp operations recorded at deploy not from a second annotation scan on the class
      -> McpInstallation.bind
      with a tools call for that enrolled mcp name and arguments matching the operation signature
        it should return the operation result

describe a bare agentic toolset with an agent-instructions operation annotated for mcp
  that has been deployed
    with an MCP server started from manifest toolset refs written during that deploy
      it should enroll that operation as a prompt under the mcp name {slug}.{operation}
      with a prompts call for that enrolled mcp name
        it should return the orchestration result from that operation

describe context guidance with guidance annotated for mcp
  that has been deployed
    with an MCP server started from manifest toolset refs written during that deploy
      with a prompts call for that enrolled mcp name
        it should return the same compound instructions string the read path assembles

describe practice guidance with guidance annotated for mcp
  that has been deployed
    with an MCP server started from manifest toolset refs written during that deploy
      with a prompts call for the practice skill enrolled mcp name
        it should return practice guidance instructions as the prompt source

describe fidelity guidance with guidance annotated for mcp
  that has been deployed
    with an MCP server started from manifest toolset refs written during that deploy
      with a prompts call for that fidelity enrolled mcp name
        it should return fidelity guidance instructions as the prompt source

describe a host with an mcp-published member
  that has been deployed and the server has not been started
    it should record the member for enrollment without binding handlers during deploy
```

---

## Layer 8 — catalog pages

`Catalog` extends `HTML`. It reads each host’s `@markdown` properties as HTML — same extract as layers 1–6, different consumer. Generate and satisfy stay in `actions/` and out of `guidance_spec.py`. Validate is layer 5.

```
describe generated catalog pages
  that have been built from the guidance registry
    it should write each practice guidance markdown property as HTML to its own page
    it should write each fidelity guidance markdown property as HTML to its own page
    it should not scrape deployed markdown files or heading structure from disk
    -> Catalog : HTML; Markdown.html()
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
