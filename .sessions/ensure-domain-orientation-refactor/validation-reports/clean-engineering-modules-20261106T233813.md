# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `harness/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (markdown: C:/Users/jeffa/.cdd/runtime-ensure-domain-orientatio/{module}/.context/module-context.md). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-06 23:38:13 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 77
**Rules with graph hits:** 14
**AI rules in scope:** 20

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story_map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `domain-nouns-only`

Name modules after domain concepts or paths, never action verbs or generic `*Model` and `*Runtime` suffixes. A technical container name does not tell callers which business knowledge it owns.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders/create_agent_toolset](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders\create_agent_toolset#L1): Module `create_agent_toolset`: Module 'create_agent_toolset' reads like an action verb path, not a domain noun.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders/create_practice_guidance](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders\create_practice_guidance#L1): Module `create_practice_guidance`: Module 'create_practice_guidance' reads like an action verb path, not a domain noun.

Evaluate the current context against this rule (domain-nouns-only):

### `named-seam-and-constraint`

Name **Seam (terms)** and **Constraint** (what callers must or must not do). At modules do not require a Public API heading — that member dump is **model**.

Evaluate the current context against this rule (named-seam-and-constraint):

### `high-cohesion`

Group classes that share one purpose and the same domain concept, or else unrelated work will keep landing in the same module and every feature ends up editing it.

Evaluate the current context against this rule (high-cohesion):

### `no-module-per-class`

A module groups multiple cohesive classes. One folder or package per class is an anti-pattern unless each class is a genuinely independent subsystem. When sketching with DDD, a small bounded context is usually **one module** with several entities inside — not one module per aggregate root.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders/create_agent_toolset](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders\create_agent_toolset#L1): Module `create_agent_toolset`: Module 'create_agent_toolset' exposes a single class in one file; group cohesive classes or merge into an existing module.

Evaluate the current context against this rule (no-module-per-class):

### `single-boundary`

Do not let another module hold, mutate, or duplicate this module’s concept. The two modules will drift, and every rule change has to be found and made in both.

Evaluate the current context against this rule (single-boundary):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions#L1): Module `actions`: Module 'actions' splits into many tiny classes (33); prefer a deep module with a small public surface.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders#L1): Module `builders`: Module 'builders' splits into many tiny classes (7); prefer a deep module with a small public surface.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup#L1): Module `context_setup`: Module 'context_setup' splits into many tiny classes (18); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `abstraction-focus`

Name *what* the module does for callers, not internal steps or storage. A seam named after its implementation has to be renamed, with every caller updated, whenever the implementation changes.

Evaluate the current context against this rule (abstraction-focus):

### `language-opens-the-card`

Language is the first lines under `# {path}`. Do not add `## Language` or `## Modules`. A section above the cards splits the words from the module they name.

Evaluate the current context against this rule (language-opens-the-card):

### `purpose-before-mechanism`

Open each concept, Purpose, and seam term with the job a caller hires it for. A decorator, merge, mark, or storage choice is how — it never leads. Either say what the caller uses each concept for, or omit them.

Evaluate the current context against this rule (purpose-before-mechanism):

### `public-seam-only`

Document only the public seam and dependencies on other modules. The seam is what a caller types (`@agent_instructions`, `tools(...)`). A runtime name nobody writes (`expand`, `invoke`, `install_to`) is an internal — leave it out. Do not document tests, scan reports, or session dumps. Do not put **Sources / context** that only lists files inside the module folder — those are the subject, not a source. Documented internals are misunderstood as public promises, and callers start writing code against them.

Evaluate the current context against this rule (public-seam-only):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders/create_agent_toolset/_examples/car/car.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders\create_agent_toolset\_examples\car\car.py#L46): Parameter `recipe`: Parameter 'recipe' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

### `general-purpose-surface`

Do not shape the seam for one caller’s UI or workflow. The second caller then either needs a near-duplicate operation or has to reshape its data to look like the first caller’s.

Evaluate the current context against this rule (general-purpose-surface):

### `temporal-independence`

Leave the module valid after every public operation. Do not require a call order unless you document it, because an undocumented order fails on the first untested path.

Evaluate the current context against this rule (temporal-independence):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

Evaluate the current context against this rule (one-way-deps):

### `extensions-live-with-the-domain`

Domain extensions of a framework belong in the domain module — a nested package under that domain is fine. Do not host them in the base framework package. `GraphEpic` lives with Stories, not in Knowledge Graph; otherwise the framework depends on every practice and cannot stay generic.

Evaluate the current context against this rule (extensions-live-with-the-domain):

### `low-coupling`

Depend only through other modules’ seams. Keep sibling imports few. Reaching past a seam freezes that module’s internals — it can no longer change them without breaking you.

Evaluate the current context against this rule (low-coupling):

### `layer-separation`

keep dependent modules at different levels of abstractions. Collapse pass-through modules — a module that only forwards turns every signature change into an edit in three files instead of one.

Evaluate the current context against this rule (layer-separation):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/segment.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\segment.py#L92): Operation `from_text`: Parameter 'config' in 'from_text' is vague.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 15

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/diagnose/diagnose.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\diagnose\diagnose.py#L24): Operation `diagnose`: Operation 'diagnose' is 107 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/grill_context/grill_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\grill_context\grill_context.py#L41): Operation `explore_context_files`: Operation 'explore_context_files' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L145): Operation `partition`: Operation 'partition' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\render\render.py#L17): Operation `render`: Operation 'render' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/satisfy/satisfy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\satisfy\satisfy.py#L22): Operation `satisfy`: Operation 'satisfy' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/graph_json_reader.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\graph_json_reader.py#L83): Operation `refresh_stale_limit_operation_parameter_messages`: Operation 'refresh_stale_limit_operation_parameter_messages' is 58 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L37): Operation `validate`: Operation 'validate' is 49 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L22): Operation `of_graph_and_ai_rules`: Operation 'of_graph_and_ai_rules' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report_formatter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report_formatter.py#L21): Operation `format_violation_line`: Operation 'format_violation_line' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L12): Operation `verify_report`: Operation 'verify_report' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L90): Operation `embed`: Operation 'embed' is 40 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L134): Operation `search`: Operation 'search' is 32 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L159): Operation `convert`: Operation 'convert' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L293): Operation `capture_from_live_app`: Operation 'capture_from_live_app' is 72 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L369): Operation `capture_from_documents`: Operation 'capture_from_documents' is 35 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `language-modules-one-section`

**Graph violations:** 18

- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L23): OoadClass `RankedChunk`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L32): OoadClass `EmbedResult`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L40): OoadClass `SearchResult`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L47): OoadClass `EmbeddingProvider`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L54): OoadClass `OpenAIEmbeddingProvider`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L74): OoadClass `ContextIndex`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index_spec.py#L41): OoadClass `FakeEmbeddingProvider`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index_spec.py#L63): OoadClass `SpecFixture`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L27): OoadClass `StructureNote`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L36): OoadClass `ConversionResult`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L43): OoadClass `ScreenResult`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L52): OoadClass `SmokeTestResult`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L60): OoadClass `PageCapture`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L69): OoadClass `ScoutResult`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L85): OoadClass `CaptureResult`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup.py#L101): OoadClass `ContextSetup`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup_heavy_spec.py#L80): OoadClass `_AppHandler`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup_heavy_spec.py#L92): OoadClass `SpecFixture`: Module 'context_setup' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.

Evaluate the current context against this rule (language-modules-one-section):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L32): Operation `verify_segment_completeness`: Operation 'verify_segment_completeness' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L145): Operation `partition`: Operation 'partition' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\render\render.py#L17): Operation `render`: Operation 'render' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L37): Operation `validate`: Operation 'validate' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L22): Operation `of_graph_and_ai_rules`: Operation 'of_graph_and_ai_rules' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 19

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/_examples/car_story/car_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\_examples\car_story\car_story.py#L12): OoadClass `CarStory`: Module folder 'car_story' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/diagnose/_examples/memory_leak_hunt/memory_leak_hunt.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\diagnose\_examples\memory_leak_hunt\memory_leak_hunt.py#L7): OoadClass `MemoryLeakHunt`: Module folder 'memory_leak_hunt' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/document/document.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\document\document.py#L11): OoadClass `Document`: Module folder 'document' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\generate\generate.py#L13): OoadClass `Generate`: Module folder 'generate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\generate\generate_spec.py#L1): OoadClass `_module`: Module folder 'generate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/iterate/_examples/story_generator/story_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\iterate\_examples\story_generator\story_generator.py#L7): OoadClass `StoryGenerator`: Module folder 'story_generator' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\render\render.py#L11): OoadClass `Render`: Module folder 'render' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/satisfy/satisfy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\satisfy\satisfy.py#L16): OoadClass `Satisfy`: Module folder 'satisfy' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/_examples/module_sketch/module_sketch.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\_examples\module_sketch\module_sketch.py#L8): OoadClass `ModuleSketch`: Module folder 'module_sketch' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/graph_json_reader.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\graph_json_reader.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L19): OoadClass `PathsNotFoundError`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L28): OoadClass `Validate`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate_spec.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L15): OoadClass `ValidationReport`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report_formatter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report_formatter.py#L9): OoadClass `ValidationReportFormatter`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders/create_agent_toolset/_examples/car/car.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders\create_agent_toolset\_examples\car\car.py#L8): OoadClass `Car`: Module folder 'car' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders/create_agent_toolset/templates/agent-toolset.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders\create_agent_toolset\templates\agent-toolset.py#L3): OoadClass `name`: Module folder 'templates' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/builders/create_context_tool/create_context_tool.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\builders\create_context_tool\create_context_tool.py#L10): OoadClass `CreateContextTool`: Module folder 'create_context_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition_index.py#L37): Operation `resolve_near`: Operation 'resolve_near' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/sketch_outline.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\sketch_outline.py#L13): Operation `of`: Operation 'of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/sketch_outline.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\sketch_outline.py#L20): Operation `every`: Operation 'every' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L32): Operation `verify_segment_completeness`: Operation 'verify_segment_completeness' uses the unnamed number 120.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L12): Operation `verify_report`: Operation 'verify_report' uses the unnamed number 80.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup_heavy_spec.py#L101): Operation `start_test_server`: Operation 'start_test_server' uses the unnamed number 0.1.

Evaluate the current context against this rule (provide-meaningful-context):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/sketch.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\sketch.py#L53): Operation `find_template`: Operation 'find_template' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/_examples/car_story/car_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\_examples\car_story\car_story.py#L12): OoadClass `CarStory`: Operation 'travelTo' uses camelCase while other operations on 'CarStory' use the other convention.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L28): OoadClass `Validate`: Operation 'createRule' uses camelCase while other operations on 'Validate' use the other convention.

Evaluate the current context against this rule (use-consistent-naming):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index.py#L54): OoadClass `OpenAIEmbeddingProvider`: Class 'OpenAIEmbeddingProvider' constructs 'OpenAI' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_index_spec.py#L63): OoadClass `SpecFixture`: Class 'SpecFixture' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\context_setup\context_setup_heavy_spec.py#L92): OoadClass `SpecFixture`: Class 'SpecFixture' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):


---

# Judgment (modules fidelity) — cdd_guidance/actions, builders, context_setup

Judged: every `module-context.md` under these three folders (the `_examples/car_chronicle` card excluded).

Graph hits: `domain-nouns-only` on create_agent_toolset / create_practice_guidance confirmed (verb-led folder names; the domain nouns are the builders' products). `no-module-per-class` on create_agent_toolset confirmed (one class, 100% public). `deep-module` class counts dismissed as worded; ratios judged per card. `language-modules-one-section` on context_setup confirmed. `missing-module-context` confirmed for actions/document, generate, render, satisfy and validate (none has a card; they rely on the stale `actions` umbrella card) and builders/create_context_tool; `_examples`, `templates` and spec `_module` entries dismissed. Code-level hits (`keep-operations-small-focused`, `limit-operation-parameters`, `prefer-instance-operations`, ...) are outside this fidelity; note that `refresh_stale_limit_operation_parameter_messages` (graph_json_reader.py:83, 58 lines, a free function) confirms P-19 is still open.

## Judgment — `cdd_guidance/actions/.context/module-context.md`

### `language-opens-the-card` — Fail
- module-context.md:1 `## Language` section above the cards.

### `public-seam-only` — Fail
- module-context.md:28 `actions/scan` card (`Scan`, `Scanner`, `ScannerCollection`) names a module and classes that no longer exist.
- module-context.md:107 `actions/sketch_render` card (`SketchRender`, `build_render_calls`, `render_approved_sketch`) names a removed module.
- module-context.md:13 Build order cites both removed modules.

### `single-boundary` — Fail
- module-context.md:59 `actions/validate` seam claims `Rule`, `RulesCollection`, `AppliesTo`, which now live in harness/guidance/rule.py (P-17); two cards claim the same concept.

### `one-way-deps` — Fail
- module-context.md:42 `actions/document` depends on `actions/scan`, and module-context.md:60 `actions/validate` and module-context.md:128 `actions/improvement` likewise — a dependency on a removed module; the real dependencies (harness/guidance, harness/graph, harness/installation, harness/mcp) are missing.

### `use-consistent-naming` — Fail
- module-context.md:59 seam term `createRule` is camelCase among snake_case operations (validate.py:348; graph hit confirmed).

## Judgment — `cdd_guidance/actions/diagnose/.context/module-context.md`

### `named-seam-and-constraint` — Fail
- module-context.md:1 "diagnose — module context" with section headings, not a `# cdd_guidance/actions/diagnose` card.

## Judgment — `cdd_guidance/actions/grill_context/.context/module-context.md`

### `one-way-deps` — Fail
- module-context.md:10 depends on `tools.tool` and `sessions`, neither of which exists.

### `public-seam-only` — Fail
- module-context.md:4 cites `AgenticToolset.context_tools`, a removed base class; module-context.md:12 Public API and module-context.md:18 Mechanism describe internals.

### `do-not-invent-terms` — Fail
- module-context.md:4 "prove-read gate" is the pseudo-precise phrase writing-guidelines.md bans; "read gate" or "read the cited files first" says it.

## Judgment — `cdd_guidance/actions/improvement/.context/module-context.md`

### `public-seam-only` — Fail
- module-context.md:4 cites `BaseContextTool`, module-context.md:11 `WorkSession.repairs` ("workspace package") and module-context.md:13 `@instruction(label=...)` — all removed.

### `named-seam-and-constraint` — Fail
- module-context.md:1 no Seam (terms), no Constraint, no Dependencies; "Manual loop until the kit is real" is a session note.

## Judgment — `cdd_guidance/actions/iterate/.context/module-context.md`

### `one-way-deps` — Fail
- module-context.md:10 depends on `tools.tool`, which does not exist.

### `public-seam-only` — Fail
- module-context.md:4 cites `AgenticToolset.context_tools` (removed) and describes the internal gate; module-context.md:12 Public API includes `mark_iterate_tick`.

### `do-not-invent-terms` — Fail
- module-context.md:4 "per tick" / "prove-read" — `ticks` is a banned word in writing-guidelines.md; the action's own word is cycle.

## Judgment — `cdd_guidance/actions/partition/.context/module-context.md`

### `vocabulary-traces-to-source` — Fail
- module-context.md:1 and module-context.md:9 name the seam `PartitionPipeline`; the class is `Partition` (partition.py:18), so the card and the code use different words for one thing.

### `one-way-deps` — Fail
- module-context.md:21 "Dependencies: (none)" while partition imports harness/guidance_actions, agent_tools, mcp and installation.

### `public-seam-only` — Fail
- module-context.md:13 Public API dumps `SegmentCompletenessConfig` fields and `from_text`/`resolve_near`.

## Judgment — `cdd_guidance/actions/sketch/.context/module-context.md`

### `public-seam-only` — Fail
- module-context.md:4 sends callers to `/sketch_render` and `actions/sketch_render`, which no longer exist; module-context.md:16 Public API.

### `one-way-deps` — Fail
- module-context.md:14 depends on `tools.tool` and `sessions`, neither of which exists.

## Judgment — `cdd_guidance/builders/.context/module-context.md`

### `language-opens-the-card` — Fail
- module-context.md:1 `## Language` above the cards.

## Judgment — `cdd_guidance/builders/create_agent_toolset/.context/module-context.md`

### `public-seam-only` — Fail
- module-context.md:13 documents `CreateAgentToolset(format=None, path=None, session=None, workspace=None)`; no constructor in the repository takes `workspace` any more.

### `domain-nouns-only` — Fail
- module-context.md:1 the module is named for an action (create); the builders card already groups both builders, so the nested folders add a module per class.

## Judgment — `cdd_guidance/builders/create_practice_guidance/.context/module-context.md`

### `public-seam-only` — Fail
- module-context.md:15 the same removed `workspace=None` constructor; module-context.md:11 sends callers to `harness/guidance/AGENTS.md`, which the repository rules forbid authoring.

### `domain-nouns-only` — Fail
- module-context.md:1 verb-led module name (graph hit confirmed).

## Judgment — `cdd_guidance/context_setup/.context/module-context.md`

### `language-opens-the-card` — Fail
- module-context.md:1 `# Modules` heading with a `### Public Seam` outline instead of a path card (graph hit confirmed).

### `deep-module` — Fail
- module-context.md:5 fourteen public seam classes, including result records (`EmbedResult`, `SearchResult`, `ScoutResult`, ...), out of about 18 classes — far above 40%.

### `named-seam-and-constraint` — Fail
- module-context.md:30 "*(none named in this file yet)*" — no Constraint.
