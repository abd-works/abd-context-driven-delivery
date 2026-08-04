---
fidelity: story_map + one-scenario-per-story
tool: stories
---

# Sketch — CDD Catalog

**Plan:** `[cdd-catalog-plan.md](./cdd-catalog-plan.md)` — this sketch is the story-hierarchy view of that plan's build order. Depth stops at story-map + a single main-flow scenario per story: no variations, no shared background, no example data. Actor is `Maintainer` throughout — this is an internal dev-tool project with one persona (whoever runs the generator / edits the config), so the actor carries no real branching weight here; it's kept only because the notation requires `{Actor} --> {Story}`.

Four epics, sibling to each other (no umbrella epic-of-epics, no sub-epic layer — each epic's own story count already sits inside the 4–9 range without one). **Not five.** A fifth "Align Code With Catalog Names" epic was drafted here and removed — see `mistakes.log` note below. Renaming `ddd`/`ux` fidelity keys and the `agent_skills`/`sub_agent` packages is real, necessary work, but it is not a *story*: it is a one-time thing the maintainer does to the codebase before generation, not a repeatable stakeholder/system interaction. It stays exactly where it already lived before this sketch existed — the plan's own `rename-fidelities` and `rename-utilities` todos (`[cdd-catalog-plan.md](./cdd-catalog-plan.md)`) — and is a hard prerequisite the other four epics assume is already done, not something the story map should re-describe as behavior. Same call, same reason, inside `Configure Illustrated Examples` (renamed from `Configure And Migrate Illustrated Examples`): the `.drawio` migration was also a one-time task drafted as a story and removed — once it's done (per the plan's own `illustrated-examples` todo), the migrated diagram is just an ordinary `Source` row that `Extract Whole-File Illustrated Example` picks up like any other example; there is no separate migration *behavior* to sketch.

---

```
Assemble Catalog Page Data
    Maintainer --> Load Context Tool And Utility Registry
        registry lists every card the catalog will need
            given the hardcoded CDD-header-plus-five-context-tool-toolset list and the deploy_agent_skills / diagnose / handoff / workspace / sub_agent utility list
            when the maintainer runs the generator's discover step
            then every context tool, CDD, and utility resolves to a class or module path with nothing missing
    Maintainer --> Scrape Fidelity Keys, Format Defaults, And Guidance Sections
        fidelity data comes from code and matching markdown, not a hand-typed table
            given a toolset's fidelities ClassVar, its format defaults, and its {tool}.md file
            when the maintainer runs the discover step for that toolset
            then each fidelity resolves to its key, default format, and matching ## {fidelity} guidance body
                and a fidelity with no matching ## heading resolves to a Guidance missing stub instead of failing
    Maintainer --> Resolve Lifecycle Action Source Dir And Calls Via AST Walk
        every action's home and neighbors are found by walking code, not a hand-maintained list
            given BaseContextTool's lifecycle-actions section with its public @action methods in source order
            when the maintainer runs the discover step over that section
            then each action resolves to its delegate kit dir under utilities/{name}/ or falls back to context_tools/base/
                and same-instance self.<other_action>() calls resolve as that action's tools-called list
    Maintainer --> Collect Skill Slash-Command Map From SKILL Frontmatter
        the Section 0 quick-invoke block needs a real skill name per tool
            given a .cursor/skills/*/SKILL.md file per context tool, including the hyphenated clean-engineering folder
            when the maintainer runs the discover step over the skills folder
            then each context tool resolves to its slash-invocable skill name exactly as spelled in that tool's own SKILL.md

    Render Self-Contained Catalog Pages
    Maintainer --> Render Hub Board With Actions And Utilities Rows
        the hub is the one page every other page links back to
            given the CDD header row, the five context-tool rows, and the assembled Actions and Utilities rows
            when the maintainer runs the generator's render step for the hub
            then index.html shows the CDD header row on top, the five context-tool rows beneath it, and the Actions and Utilities rows below the board
    Maintainer --> Render Context Tool Page
        a tool page is the front door to its fidelities
            given one toolset's Purpose/Overview prose and its resolved fidelity cards
            when the maintainer runs the render step for that tool
            then the tool page shows its badge, its Purpose prose, and a card per fidelity linking to that fidelity's page
    Maintainer --> Render Fidelity Page With Quick-Invoke And Illustrated Example
        a fidelity page carries the full guidance for one ticket, and must say exactly how to call it
            given a fidelity's skill name (e.g. stories), its own key (e.g. story_map), the ten lifecycle action names in source order, and each action's resolved page
            when the maintainer runs the render step for that fidelity
            then the page opens above the hero with the literal line /{skill} <action> {fidelity} — e.g. /stories <action> story_map — as the one prominent command on the page, followed by all ten lifecycle actions (partition, grill, sketch, generate, document, iterate, validate, satisfy, repair, improve) listed as the legal values for <action>, each one a hyperlink to that action's own page, and a single small "Raw manifest format →" link to the YAML request shape as a subsidiary reference — never an inline YAML block competing with the command line above it
                and below that comes the hero, the highlighted board, the Guidance body, and the Illustrated example panel
    Maintainer --> Render Action Page With Four Fixed Sections
        every action page reads the same shape no matter which action it is, and must say exactly how to call that one action
            given an action's own name, its tools-called list, resolved markdown guide, module overview, and main code file
            when the maintainer runs the render step for that action
            then the page's hero carries the Lifecycle action badge, a plain one-line "used as action: {this action's name} in the request" note, and the same small "Raw manifest format →" subsidiary link — no inline YAML block
                and below the hero the page shows Tools/actions called, Markdown instructions, Module overview, and Code in that fixed order, each collapsible
    Maintainer --> Render Utility Page
        a utility page carries the same shape as an action page minus the stage-ticket framing
            given a utility's Purpose/Seam prose and its optional {utility}.md guide
            when the maintainer runs the render step for that utility
            then the page shows its Purpose/Seam prose and a link to its guide when one exists
    Maintainer --> Render Flat Grid Pages
        every card is also reachable from a plain list, not only the board
            given every rendered tool, fidelity, action, and utility card
            when the maintainer runs the render step for the grid pages
            then context-tools.html, fidelities.html, actions.html, and utilities.html each list every card of that kind

    Make Catalog Output Portable
    Maintainer --> Embed Local Assets And Content Into Generated HTML
        the catalog has to work with no other folder present
            given the commons CSS/JS, migrated diagram images, and every panel's markdown/code content
            when the maintainer runs the generator's emit step
            then every asset and every panel's content is written literally into the generated HTML with no runtime fetch back into context_tools/ or utilities/
    Maintainer --> Build Git-URL Source Citation For Every Reference
        every view-source link has to survive the catalog leaving this machine
            given the repo's resolved remote URL and ref
            when the maintainer's emit step builds a citation for a code file, a markdown guide, or an illustrated-example source
            then the citation renders as {repo_url}/blob/{ref}/{path} and no local filesystem path appears anywhere in the output
    Maintainer --> Regenerate Catalog Via CLI With Default And Override Flags
        regenerating the whole site is one command with sane defaults
            given the bare command python -m utilities.catalog_generator.generate_cdd_catalog
            when the maintainer runs it with no flags
            then the catalog regenerates into catalog/ using the current HEAD and the origin remote, with --out, --repo-url, and --ref available to override any of those three

    Configure Illustrated Examples
    Maintainer --> Configure Illustrated Example Mapping Per Fidelity
        which file illustrates a fidelity is a decision, not a guess — and the decision names a real file, not the index itself
            given a tool's examples/ folder — its examples.md or README.md index, plus the tool's real illustration files, which typically sit in their own named subfolder under examples/ as markdown or Python (e.g. examples/md/story-map.md, examples/py/manage-customer-orders/story_runner.py) rather than inside the index file
            when the maintainer adds a ## Illustrated examples table row naming Fidelity, Source (the path to one of those subfolder files — or, for the few tools that keep content inline, an anchor inside examples.md itself), and Anchor
            then the generator's illustrated-example panel for that fidelity resolves to exactly that Source file or anchor and nothing else
    Maintainer --> Extract Whole-File Illustrated Example
        some illustrations are simplest as an entire file
            given an Illustrated examples row with Anchor whole-file
            when the maintainer's discover step resolves that row
            then the entire source file's content becomes that fidelity's illustrated-example body
    Maintainer --> Extract Heading-Anchored Illustrated Example Section
        some illustrations live inside a larger shared file under one heading
            given an Illustrated examples row whose Anchor names a ## or ### heading
            when the maintainer's discover step resolves that row
            then only the body under that heading, up to the next heading of the same or higher level, becomes that fidelity's illustrated-example body
    Maintainer --> Extract Comment-Tag-Anchored Illustrated Example Block
        some illustrations are marked inline inside a shared file with a comment tag rather than a heading
            given an Illustrated examples row whose Anchor names an HTML comment tag such as <!-- Mu -->
            when the maintainer's discover step resolves that row
            then only the lines carrying that comment tag become that fidelity's illustrated-example body
~> Increment 1 (prerequisite, not a story — see rename-fidelities / rename-utilities in the plan): code and guides already renamed (`ddd`/`ux` engineer fidelity → `tactics`/`front_end_code`; `sessions` → `workspace` — top-level package folder only, done; `agent_skills` → `deploy_agent_skills` still outstanding) before any story below starts.
~> Increment 2: The generator has everything it needs to know about every card before it renders a single page: Load Context Tool And Utility Registry, Scrape Fidelity Keys/Format Defaults/Guidance Sections, Resolve Lifecycle Action Source Dir And Calls Via AST Walk, Collect Skill Slash-Command Map From SKILL Frontmatter
~> Increment 3: The catalog is fully browsable end to end from the hub down to every fidelity, action, and utility page: Render Hub Board With Actions And Utilities Rows, Render Context Tool Page, Render Fidelity Page With Quick-Invoke And Illustrated Example, Render Action Page With Four Fixed Sections, Render Utility Page, Render Flat Grid Pages
~> Increment 4: The catalog is safe to zip and hand to someone with no other context: Embed Local Assets And Content Into Generated HTML, Build Git-URL Source Citation For Every Reference, Regenerate Catalog Via CLI With Default And Override Flags
~> Increment 5 (assumes the plan's own migration prerequisite is already done — the two abd-skills .drawio assets copied into context_tools/stories/examples/, not a story here): Every fidelity page's illustrated-example panel shows either a real current example or the existing "No illustrated example configured yet" fallback — never a fabricated example and never an invented stale/warning state: Configure Illustrated Example Mapping Per Fidelity, Extract Whole-File Illustrated Example, Extract Heading-Anchored Illustrated Example Section, Extract Comment-Tag-Anchored Illustrated Example Block
```

---

## Notes on mechanical-uniqueness calls made here

- **Illustrated-examples extraction is 3 stories, not 1.** `whole-file`, heading-anchor, and comment-tag-anchor are three different parsing algorithms (read everything / slice by heading level / filter by inline tag) — that's the `branch-on-mechanical-uniqueness` rule, not three rows of the same mechanic with different data.
- **Page rendering is 6 stories, not 1.** Hub, tool, fidelity, action, utility, and grid pages each assemble a genuinely different data shape and section structure (the fidelity page alone has 5 named panels no other page has). Same rule, other direction: these are not "one render story with different examples."
- **One-time tasks are not stories at all — fixed twice, logged twice.** An earlier draft had a fifth epic, "Align Code With Catalog Names," with 4 rename "stories," and a "Migrate Legacy Drawio Assets Into Stories Examples" story inside what was then "Configure And Migrate Illustrated Examples." Same wrong call both times: a one-time codebase change the maintainer performs once, by hand, before generation runs is not a stakeholder/system *behavior* — there's no repeatable interaction to specify Given/When/Then against, and once it's done the artifact it produces (a renamed key, a copied `.drawio` file) is indistinguishable from one that was always there. Both removed; both pieces of work stay exactly where they already lived — the plan's `rename-fidelities` / `rename-utilities` todos and its `illustrated-examples` todo, respectively. Logged as defects at `.context/sessions/cdd-catalog/mistakes.log` under this same `catalog/` root.
- **`Make Catalog Output Portable` has only 3 stories** — below the 4–9 default but only a *warn*, not an error, per `four-to-nine-children`. Embedding assets, building git-URL citations, and the CLI wrapper are three genuinely distinct mechanics; forcing a fourth would be padding, not real variation.
- **`Configure Illustrated Examples` has only 4 stories now, not 5 — fixed, logged.** Had a "Flag Stale Illustrated Example With Warning Badge" story: invented. There is no "stale" status, no warning badge, no maintenance-signal the generator renders — that was never part of the actual `## Illustrated examples` feature, just something drafted here that sounded plausible. The real behavior for CE `code` and CDD's example was already covered, for free, by the ordinary "no row configured" case: fix the content and add the row, or don't add the row yet. Removed the story; plan's `Status` column and every "stale" mention removed with it.
- **No sub-epic layer.** `SubEpic` is nestable, not mandatory. Each epic's story count already sits at a legible size on its own; inserting a sub-epic tier here would just be a relabeling, not a real grouping decision.
- **One command, not two competing ones — fixed, logged.** The Fidelity/Action page stories used to give a raw YAML "Invoke" block equal billing alongside Section 0's `/{skill} <action> {fidelity}` line — two different-looking things claiming to be "how you call this," with no indication which was primary. There is exactly one prominent command: the slash line. The YAML request shape is real (it's what every deployed `SKILL.md` documents internally) but it's secondary — a single small "Raw manifest format →" link, never inlined, never competing for attention.
- **No variations, no shared background, no example data**, per the ask — every story stops at one main-flow scenario. Deepening any one of these to `scenarios` fidelity (with variations / shared setup) or `acceptance_tests` fidelity (spec files + tier) is the next fidelity pass, not part of this sketch.

---

## Clean Engineering pass — `/clean-engineering sketch` on `utilities/catalog_generator/`

The story map above says *what* the generator must do; it says nothing about the classes that do it. Ran `/clean-engineering`'s `sketch` action (grill → generate) against that gap, at **model** fidelity, in markdown — per `clean_engineering.md`'s own progression (`modules → model → code`) and its markdown channel shape (`context_tools/clean_engineering/class_model/markdown_class_model.py`).

**Prove-read before asking** (`grill_context.md`'s gate): read `primitives/tools/tool.py` (`Toolset`, `@tool`, `@resource`, `_Tool`/`_Resource` dataclasses), `primitives/actions/action.py` (`AgenticToolset`, `@action`, `Action` dataclass, `_ActionExpander`), `primitives/assets/assets.py` + `markdown_extractor.py` (the framework's own module-relative markdown/section resolver), `context_tools/clean_engineering/class_model/` (canonical-model + render-channel precedent), `context_tools/base/base_context_tool.py` (`fidelities` ClassVar, lifecycle `@action`s), and `utilities/agent_skills/agent_skills.py` in full (closest sibling utility — same "scrape the repo, emit files" shape).

**Grilled two branches** (full framing + resolution in `catalog/.context/sessions/cdd-catalog/grill-answers.md`, written live during the grill, not reconstructed after):

1. *Does the top-level class need an `@action` orchestration recipe, or a plain `@tool`?* Resolved **`@tool`, no `@action` anywhere** — `@action` bodies are never executed; `_ActionExpander` AST-walks them into step-by-step instructions *because* the step needs agentic judgment between calls (a question, a branch on natural-language content — that's why `AgentSkills.deploy_tools_as_skills` and `BaseContextTool.grill`/`sketch` are `@action`s: they ask the user things mid-flow). Scrape → render → write is a fixed, deterministic pipeline with zero judgment points. It runs for real, called directly by `generate_cdd_catalog.py`.
2. *Does the generator need its own parallel data schema* (`CatalogModel` / `PracticeEntry` / `FidelityEntry` / …), *scraped once and then rendered?* Rejected outright, not just the interface question about it. The real object model already carries everything: `Toolset.tools`, `AgenticToolset.actions`, `BaseContextTool.fidelities`. **No scrape-then-model-then-render split.** Instead: a small family of thin renderer classes, each wrapping one real primitive one-for-one, each exposing exactly one operation — `generate_catalog(...)` — that renders that node and composes its children's `generate_catalog(...)` against the live objects directly.

**Sketch / generate** — the resulting model, one module, no `I{Class}` interfaces (following `agent_skills.py`'s own precedent — a closer analog than `class_model`'s multi-language channel classes; there is no second implementation of the same contract here to justify a formal seam).

Deepened one notch further than a first model pass usually goes: `clean_engineering.md`'s `## model` section now explicitly says Interactions and Invariants **may** be named at model fidelity — optional, not required (restored in the same session this catalog model was sketched; they used to be askable here and had quietly dropped to code-only). Reusing the exact notation from `templates/clean_engineering-sketch.md` rather than inventing a new one: each `generate_catalog` operation below nests `-> {field}.{operation}` for the call it makes (the order of the `->` lines **is** the sequencing — nothing more) and `// …` for any invariant or looping note, per that template's **Notation** / **Interaction rules**.

```
# catalog_generator

*catalog_generator* is the single module that renders the CDD catalog. It
wraps the real object model directly — Toolset.tools, AgenticToolset.actions,
BaseContextTool.fidelities — there is no separate scraped schema. Each class
below wraps one real primitive one-for-one and exposes exactly one operation,
generate_catalog, that renders that node and composes its children's
generate_catalog calls against the live objects.

## CatalogTool

*CatalogTool* is the one-line, hyperlinked rendering of a single real `_Tool`
wherever a "Tools/actions called" bullet needs one — inside an Action page's
own list, and inside a Utility page's tool list.

CatalogTool(repo_url: str, ref: str)
------
repo_url: str
ref: str
----
generate_catalog(tool, owner): str
  // never mutates tool or owner — read-only render of a live object

## CatalogAction

*CatalogAction* is the four-fixed-section rendering of one real `Action` —
Tools/actions called, Markdown instructions, Module overview, Code — used for
every lifecycle-action detail page and reused unchanged for a utility's own
actions.

CatalogAction(repo_url: str, ref: str, catalog_tool: CatalogTool)
------
repo_url: str
ref: str
catalog_tool: CatalogTool
----
generate_catalog(action, owner): str
  -> catalog_tool.generate_catalog
  // once per tool name in action.signature_entry()["tools"], in that list's order
  // never mutates action or owner — read-only render of a live object

## CatalogFidelity

*CatalogFidelity* is the Section-0-quick-invoke-plus-guidance rendering of one
fidelity name on one `BaseContextTool` instance — the `/{skill} <action>
{fidelity}` line, the ten lifecycle actions each linked through
CatalogAction, the matching `## {fidelity}` guidance section, and the
illustrated-example panel.

CatalogFidelity(repo_url: str, ref: str, catalog_action: CatalogAction)
------
repo_url: str
ref: str
catalog_action: CatalogAction
----
generate_catalog(fidelity_name, owner): str
  -> catalog_action.generate_catalog
  // once per lifecycle-action name, in BaseContextTool's declared source
  //   order (partition, grill, sketch, generate, document, iterate,
  //   validate, satisfy, repair, improve)
  // never mutates owner — read-only render of a live object

## CatalogContextTool

*CatalogContextTool* is the context-tool page for one `BaseContextTool`
instance — Stories, DDD, UX, Clean Engineering, BDD, or CDD's own header-row
page — composing CatalogFidelity for every value in owner.fidelities.

CatalogContextTool(repo_url: str, ref: str, catalog_fidelity: CatalogFidelity)
------
repo_url: str
ref: str
catalog_fidelity: CatalogFidelity
----
generate_catalog(owner): str
  -> catalog_fidelity.generate_catalog
  // once per value in owner.fidelities, in that dict's declared stage order
  //   (DISCOVERY, SPEC, ENGINEER)
  // never mutates owner — read-only render of a live object

## CatalogUtility

*CatalogUtility* is the utility-row detail page for one plain-utility
`Toolset` instance (deploy_agent_skills, diagnose, handoff, workspace,
sub_agent) — composing CatalogTool and, when the utility declares
any, CatalogAction.

CatalogUtility(repo_url: str, ref: str, catalog_tool: CatalogTool, catalog_action: CatalogAction)
------
repo_url: str
ref: str
catalog_tool: CatalogTool
catalog_action: CatalogAction
----
generate_catalog(owner): str
  -> catalog_tool.generate_catalog
  // once per entry in owner.tools, in manifest signature order
  -> catalog_action.generate_catalog
  // once per entry in owner.actions, in manifest signature order — only
  //   when owner is an AgenticToolset (declares any @action)
  // never mutates owner — read-only render of a live object

## Catalog

*Catalog* is the top-level entry point — the only class `generate_cdd_catalog.py`
calls. It owns the shared portability config (git repo URL, ref, output root)
and the fixed roster of live instances to render: the CDD instance as the
header row, the five context-tool instances, the shared lifecycle-action list
for the Actions row, and the utility instances for the Utilities row.

Catalog(repo_url: str, ref: str, out_root: str)
------
repo_url: str
ref: str
out_root: str
catalog_context_tool: CatalogContextTool
catalog_action: CatalogAction
catalog_utility: CatalogUtility
----
generate_catalog(): None
  -> catalog_context_tool.generate_catalog
  // for the CDD instance first (the header row), then once per context tool
  //   in roster order (Stories, DDD, UX, Clean Engineering, BDD)
  -> catalog_action.generate_catalog
  // once per lifecycle-action name, in source order — the Actions row,
  //   shared across every context tool
  -> catalog_utility.generate_catalog
  // once per utility instance, in roster order (deploy_agent_skills,
  //   diagnose, handoff, workspace, sub_agent)
  // every emitted page's source citation is a git URL
  //   ({repo_url}/blob/{ref}/{path}) — never a local filesystem path
  // no output is ever written outside out_root
```

One module, one file (`catalog_generator.py`) — matches `agent_skills.py`'s own shape: a single cohesive class family, no folder-per-class, no separate scrape/model/render modules. `generate_cdd_catalog.py` stays a thin CLI wrapper: build a `Catalog(...)`, call `.generate_catalog()`.
