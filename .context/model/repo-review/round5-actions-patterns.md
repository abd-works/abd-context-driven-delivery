# Round 5: actions, patterns, context setup, builders, judged across files

Area: `cdd_guidance/actions`, `cdd_guidance/patterns`, `cdd_guidance/context_setup`, `cdd_guidance/builders` (not `_examples`). Branch `ensure-domain-orientation-refactor` at d71e0b20, read on 2026-11-07.

## How each check ran

**Graph rules: not run.** Every `validate.validate` call to the CDD MCP host failed. The calls with `graph: true` for `clean-engineering-modules` and `clean-engineering-code` on the four area folders either closed the connection ("MCP server "plugin:cdd:cdd" connection closed before the tool call was answered") or, after one or more "still running … call again" replies, came back `ECONNREFUSED: Unable to connect` or "MCP server "plugin:cdd:cdd" is not connected". Each failed call left a 0-byte report under `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\` (`clean-engineering-modules-20261108T014517.md`, `clean-engineering-code-20261108T014446.md`, `-014644.md`, `-014710.md` are this agent's calls; the host restarted between them, apparently under load from the other five agents). Following `.claude/rules/mcp-fail-loud.md`, validate was not run through Python. No graph hit was confirmed or dismissed, and there is no scanner false-positive list below. The cross-file scanners (copies, cycles, one-way dependencies, coupling, the 40%-public measure, module context, module naming) must be re-run on these folders once the host is stable.

**AI judgment: run, and checked by running the code.** I read each area file beside the files it imports and the files that import it. Recipe expansion was then checked by expanding each action's `@agent_instructions` recipe the way the MCP host does (`AgentInstructions.for_callable(recipe, Action().for_call(ToolCall({}, project))).expand(arguments)`). Each expansion used a throwaway project with an open session, on `stories-story-map`, and I compared the prompt with the text the held fidelity gives (`fidelity.instructions`, `fidelity.templates`, `practice.rules.markdown_block`, `practice.sketch_template`, the rules Validate lists). The probe scripts are in the session scratchpad. They exercise the code but are not a validate run.

## The recipe question: does each recipe reach its text through `item.member` on the loop's item?

The expander (`harness/agent_tools/recipe.py`) handles three shapes:
- **A `for item in self.listed():` loop.** In the loop, `instructions(item.member)` and `instructions(item.a.b)` (`_loop_member`, `_loop_item_instructions`, :383-408) expand a member of the item only when that member is an `@agent_instructions` or tool member.
- **A call on `self` that is no recipe or tool**, such as `self.run(callback)`. The expander evaluates it and adds the strings it returns (`_walk_member_call` → `_add_evaluated`, :579-594). So a callback that **returns** its text reaches the prompt.
- **A recipe called as an ordinary Python method** inside a callback, such as `grill.grill_with_context()` or `Generate.generate(...)`. Its body just runs: string statements do nothing, and `tools(self.x)` **calls** `x` when `x` needs no arguments (`agent_tools.py:1150-1157`). Only its `return` value comes back. The expander never sees the text that body contributes.

| Recipe | How it reaches its text | Result (measured) |
|---|---|---|
| `Generate.generate` (generate.py:21) | `self.run(self._generate_item)`. The callback returns `item.instructions` and `item.generate_output()` of the held FidelityGuidance that `each` hands it | **Reaches it.** The fidelity's instructions, template and rules are all in the prompt. |
| `Document.document` (document.py:20) | `self.run(on)`, which returns `item.templates` and `item.generate_output()` | **Reaches it.** |
| `Improvement.repair` (improvement.py:23) | `self.run(on)`, which returns `item.examples` and `item.templates` | **Reaches it.** |
| `Partition.partition` (partition.py:91) | `self.run(on)`, which returns `_corpus_steps`, holding the fidelity's Scaffold | **Reaches it.** |
| `Validate.validate` / `create_rule` | `self.run(on)` returns the text; the rules come from `_rules_text(item)` | **Reaches it.** |
| `Sketch.sketch` (sketch.py:113) | `self.begin(guidance, …)` then `for item in self.listed(): instructions(item.rules.markdown_block)` / `instructions(item.sketch_template)` | **Dropped.** The loop has the right shape, but `listed()` is empty (see H1). No rules and no sketch template reach the prompt. |
| `GrillContext.grill` (grill_context.py:109) | `self.begin(guidance)`, `self.grill_with_context()`, `self.generate_each()` | **Dropped.** `generate_each` runs Generate as Python and its prompt is lost (H2), and `begin` never sets what to work on (H1). |
| `Iterate.iterate` (iterate.py:28) | `self.run(self._iterate_item)`. The callback calls `grill.grill_with_context()` and `grill.generate_each()` as Python and returns `None` | **Dropped.** The whole grill and generate text is lost. The prompt is 461 characters: the docstring and the return line. |
| `Satisfy.satisfy` (satisfy.py:22) | `self.run(on)`. The callback appends `Validate.validate(...)` (Python) and `Generate.fix_instructions()` to a list the recipe returns | Validate's report and rules **reach it**. The fix instructions are **empty** (H4). |
| `ContextSetup.capture_from_documents` (context_setup.py:259) | `tools(self.partition.partition())` | **Wrong shape.** Partition's recipe is pasted inline, with no arguments, instead of being listed as a tool (H5). |
| `ContextSetup.capture_from_live_app` | `tools(...)` on its own tools and `context_index.embed` | Reaches it. |

## Findings, most severe first

| # | file:line | concern | found by | status | fix in one line | severity |
|---|---|---|---|---|---|---|
| H1 | sketch.py:115, grill_context.py:111 (and `GuidanceAction.begin`, harness/guidance_actions/guidance_actions.py:417-421) | 5, wrong behaviour | AI + measured | new | Call `self._work_on(guidance)` in the recipe; `begin` is expanded as a nested recipe **with no arguments**, so its `self._work_on(guidance)` sees `guidance=None` and does nothing | **high** |
| H2 | grill_context.py:116-124 (`generate_each` → `_generate` → `Generate.generate(...)` called as Python) | 5, wrong behaviour | AI + measured | new | Make `generate_each` a recipe line the expander walks (e.g. `instructions(self._generate_recipe())`, or return Generate's expanded instructions from `AgentInstructions.for_callable(...).expand`) rather than calling the recipe as a method | **high** |
| H3 | iterate.py:34-38 | 5, wrong behaviour | AI + measured | new (the guidance agent named the recipe limitation, not this case) | `_iterate_item` returns nothing and calls two recipes as Python; return their expanded text, or walk `grill_with_context` / `generate_each` as recipe lines. With no session the expansion raises (`ActionWorksInNoSession` from `explore_context_files`, which the direct call actually runs) | **high** |
| H4 | generate.py:101-109 with satisfy.py:33 | 5, wrong behaviour | AI + measured | new | `generate_fixes_from_validate` holds only a docstring and `return ""`, so `RecipeSource.only_defers_to_parent` is true and the expansion is empty; Satisfy's "apply generate_fixes_from_validate" step therefore gives the agent nothing. Put the sentence in the body as a string statement, or have `fix_instructions` fall back to the docstring | **high** |
| H5 | context_setup.py:287 | 5, wrong behaviour | AI + measured | new | `tools(self.partition.partition())` expands Partition's recipe inline with no arguments ("Partition of  finished (mode one_go)") and does not list `partition` as a tool, though Step 3 tells the agent to call it. Set `self.partition.mode = "tool"` (as Generate does for Validate) or give the cross-call the tool mode | **high** |
| H6 | sketch_spec.py:208-218, grill_context_spec.py, iterate_spec.py | 5 (no spec caught H1-H5) | AI | new | The sketch spec calls `sketcher.begin([...])` in Python before expanding, so it hides H1. Iterate's specs never expand. Add specs that expand each recipe from MCP arguments alone and assert the fidelity's rules, template and generate text are present | high (it is how H1-H5 got through) |
| M1 | satisfy.py:30-36 | 5 | AI + measured | new | Expanding the satisfy prompt runs a real validate. It writes a report into `validation-reports/` and logs a `validate` line to the session (the board reads that line as "checked") before the agent has fixed anything. This is defensible as "satisfy starts with validate", but logging should say satisfy ran it | medium |
| M2 | grill_context.py:30-39 and sketch.py:31-34 | 1 duplicated functionality | AI | new | Two ways to find "the .context folder under the session's root": GrillContext walks the parents for `.context`/`.sessions`, Sketch joins `root/module/.context`. Give the session one `context_folder(module="")` and use it in both | medium |
| M3 | context_setup.py:54-77 | 1, 2 | AI | new | ContextSetup re-implements GuidanceAction's session handling (`_session`, a `session` property raising `ActionWorksInNoSession`, `for_call`). Move that onto a shared session-bound toolset base, or have ContextSetup hold its Partition's session | medium |
| M4 | checked_graph.py:59-60; graph_json_reader.py:24-36 | 5 (name lookup) | AI | known skip ("Violation.practice stored as a string") | Violations are filtered by practice key strings; hold the practice objects | medium |
| M5 | generate.py:62-66 (`Format(...)` from strings) | 2, 5 | AI | known skip (Format as an object) | `fidelity.format` and `outputs` should return Format objects | medium |
| M6 | graph_json_reader.py:39-48 (`save_checked_graph` re-reads graph files to merge violations) and report_files.py:39 | 5 | AI | left from review (#34) | ReportFiles should copy the graph CheckedGraph already holds, not rebuild violations from the files | medium |
| M7 | sketch_outline.py:33 | 5 (global objects) | AI | new | Every `SketchOutline` reads `PracticeCatalogue.practices()`, the process-wide shared practice instances, for its lenses. Since `sketch_lens` is a class attribute, read it from `PracticeCatalogue.practice_class(key)`, or have the caller hand in the session's practices | medium |
| M8 | lern_domain_driven.py:13 → graph_overlay.py:65/85/143/211 → tier_facts.py:173 → lern_domain_driven.py | 7 (import cycle) | AI | new | `test_setup_text` imports `LernDomainDriven` only to read `story_test_folder`. Pass the folder from the overlay's pattern (`self.overlay.pattern...`) and drop the lazy import that closes the cycle | medium |
| M9 | render.py:31-39 | 5 | AI | new | `document_named(content, paths)` reads the files even when `paths` is set, and `render_files` then reads them again. `practice.render(format, practice, …)` hands the practice back to itself. Read only when `paths` is empty | medium |
| M10 | fixtures.py:23-27 (`LernCanvasFixtures`) | 3 no use, 2 | AI | left from review (D), kept by README | The only "use" is prose in `practices/ux/model/claude_design/story_canvas.md:61` ("build the pattern's fixtures bundle"). No tool or code calls it, and it copies `LernDomainDriven.story_test_folder`. Publish it as a tool on the LERN pattern or delete it | medium |
| L1 | context_setup.py:189, :265 | 11 / docs | AI + measured | new | The docstrings use `{repo_path}` / `{folder_path}` single-brace placeholders, which `RecipePlaceholders` never fills (it fills `{{name}}`), so the skill text shows them literally | low |
| L2 | partition.py:52 | 1 | AI | new | `partition_guidance.replace("{{slug}}", …)` fills placeholders by hand, beside `RecipePlaceholders`. Use the one placeholder filler | low |
| L3 | improvement.py:41 | 5 / docs | AI | new | The repair text names Diagnose as the string `cdd_guidance.actions.diagnose.diagnose:Diagnose`. Name the `diagnose` tool, which the agent can call | low |
| L4 | generate.py:36-39 and diagnose.py:132-137 | 1 | AI | new | Both are `self._inside(Validate, …).listed_rules()`: two small copies of "the rules to follow". One public `rules_to_follow()` on GuidanceAction would serve both | low |
| L5 | graph_json_reader.py (6 module functions), validate.py:189 `_rules_text`, tier_facts.py:171-267, access_facts.py:79-92, lern graph_overlay.py:43-261 | 8 / module-level functions | AI | partly left | Fold them into their owners: violation reading onto `SavedGraph`/`Violation`, `_rules_text` onto FidelityGuidance (`checked_rule_collections` already lives there), the regex helpers onto `TierFile`/`AccessFile` | low |
| L6 | patterns/mern_domain_driven/.context/grill-answers.md:15; mern-domain-driven-sketch.md | 11 stale docs | AI | left (review #51, `_stories` deleted) | They still describe `self._stories().generate()` and ported scanners that do not exist. Mark them historical or delete them | low |
| L7 | .context/repo-model.md:2737 | 11 | AI | new | The model still lists `Partition.partition_corpus`, which was deleted | low |
| L8 | builders/create_agent_toolset, builders/create_practice_guidance, patterns/mern_domain_driven, patterns/cdd_claude_mod | 8 one-class packages | AI | new | Each `.py` is a 7-30 line class. They are kept because the installer discovers one folder per skill. That is acceptable, so no fold is needed; noted only for the graph scanner to confirm | low |
| L9 | actions/render/AGENTS.md | 11 | AI | new | An `AGENTS.md` inside an action folder contradicts `.claude/rules/learning-from-corrections.md` (agent notes go in the kit markdown). Move its three lines into `render`'s docstring or the actions card | low |

## Confirmed fixed since the review (not findings)

- **Partition reads its own files.** `PartitionIndex.at/near` and `Segment.at` (review #44-46).
- **Overlays.** Each pattern makes its overlay once as `graph_overlay` and reaches practices by class (`graph.loaded_practice(Ddd)`), not by name (#52-62). Each file is read once into `TierFile`/`AccessFile`, which holds one `SourceText` (#66-67). `patterns/source_text.py` is gone.
- **Validate.** `CheckedGraph` keeps its built graph (`self._built`). `ValidationReport` takes the guidance and uses its own Rules. `ValidationReportFormatter` and the `rule_bodies` dict are gone (#25, #27-29, #35-36).
- **Smaller deletions.** `DomainDrivenStack._stories`, `Partition.partition_corpus`, Document's `scanner` branch, and ContextSetup's four practice fields are deleted.
- **Sketch lenses.** `SketchLens.of/every` are gone; lenses are held on the practice class.
- **Context index.** `SegmentIndex`/`IndexedSegment` own `index.faiss`/`meta.json` and read the view with FrontMatter (#82).
- **Dependency direction.** No file in the area imports `space/` or `tools/`. Nothing in `harness/` imports this area.

## Counts

- By concern: 5 (wrong-shape or wrong behaviour) 13; 1 (duplicated functionality) 4; 2 (duplicated shapes) 2, shared with 5; 3 (no use) 1; 7 (cycle) 1; 8 (one-class or module functions) 2; 11 (legacy and docs) 5.
- By severity: high 6 (H1-H6), medium 10, low 9.
- By status: new 19, left from review 4, known skip 2.

## Scanner false positives

None recorded. The graph scanners did not run, because the CDD MCP host refused or dropped every validate call (see "How each check ran"). Re-run `validate.validate` with `graph: true` for `clean-engineering-modules`, `-model` and `-code` on the four folders when the host is up, then confirm or dismiss each hit here.

## Graph check (run after the round)

Run one call at a time after the round: `clean-engineering-modules` with `graph: true` on `cdd_guidance/actions`, `cdd_guidance/patterns`, `cdd_guidance/context_setup` and `cdd_guidance/builders`. Report: `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261108T021449.md` (with its `.json`), 195 graph hits.

`clean-engineering-model` and `clean-engineering-code` were not run. In the space-tools area, the modules and model runs returned the same 285 hits rule for rule, and earlier model and code runs both returned 637. The graph section covers the whole Clean Engineering practice whichever fidelity is named.

### Hit counts per cross-file rule

| Rule | Hits | Confirmed |
|---|---|---|
| `one-way-deps` | 32 | 0 |
| `low-coupling` | 0 | – |
| `deep-module` | 0 | – |
| `eliminate-duplication` | 0 | – |
| `missing-module-context` | 0 | – |
| `no-module-per-class` | 3 | 0 |
| `use-consistent-naming` | 1 | 0 |
| `do-not-invent-parallel-object-models` | 0 (AI-only rule) | – |
| `use-explicit-dependencies` | 7 | 1 |

### Findings now marked both

- **M3 (ContextSetup re-implements session handling): both.** `use-explicit-dependencies` hit `context_setup/context_setup.py:63-64`. `ContextSetup` falls back to `Partition()` and `ContextIndex()` built inside its constructor, not made for the call's session. That is the same missing session wiring M3 names. It also explains why H5's inline Partition recipe expands with no arguments.

### Confirmed new findings

None. The graph missed M8 (the lern overlay cycle `lern_domain_driven.py` → `graph_overlay.py` → `tier_facts.py` → `lern_domain_driven.py`) because that cycle is between files inside one module.

### Dismissed hits and scanner false positives

- **`one-way-deps`, 32 hits**, each "cycle of 48 modules" on `grill_context`, `improvement`, `iterate`, `partition` and `sketch` (through `agent_tools`, `guidance_actions`, `installation`, `mcp`, `markdown`, `session`, `bdd`, `clean_engineering`). These are false positives.
  - No production file in `harness/` imports `cdd_guidance/`.
  - No production file in `cdd_guidance/actions` imports `cdd_guidance/practices`. The practices import `actions/sketch/sketch_outline.py`, one way.
  - The edges back come from specs and `_examples`, for example `actions/sketch/_examples/module_sketch/module_sketch.py:5` and `actions/iterate/_examples/story_generator/story_generator.py:4`.
  - Scanner: `cdd_guidance/practices/clean_engineering/model/graph_reading.py:52` (spec and `_examples` edges) and `rules/practice_wide_rules.py:30`.
- **`no-module-per-class`, 3 hits on `cdd_guidance/actions`, `cdd_guidance/builders` and `cdd_guidance/patterns`.** These are false positives. Each folder sits above modules that each have their own `.context`. It holds only its shared base (`builder.py`, `domain_driven_stack.py`), or for `actions` only a spec (`fidelity_text_spec.py`). Scanner: `cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py:52` and `:63-64`. `_public_classes_in` skips files that start with `_` or `test_` but not `*_spec.py` files, so a spec class counts as the module's public class. The rule also never asks whether the folder only holds the modules nested inside it.
- **`use-consistent-naming`, 1 hit:** `actions/_examples/car_story/car_story.py` (`travelTo`). An `_examples` file. Scanner: `harness/graph/skipped_folders.py:11-34` does not skip `_examples`.
- **`use-explicit-dependencies`, 6 dismissed:**
  - `SpecFixture` building a `Path` (`context_index_spec.py`, `context_setup_heavy_spec.py`). The rule runs on specs and flags a `Path`.
  - `LernCanvasFixtures` building a `Path` (`fixtures.py`). A `Path` is a value. Its no-use problem is M10.
  - `AccessFile` and `TierFile` building a `SourceText` from their own file (`access_facts.py`, `tier_facts.py`). A held value made from the object's own text.
  - `OpenAIEmbeddingProvider` building `OpenAI()` (`context_index.py:133`). The provider is itself the adapter that a caller swaps.

  Scanner for the `Path` and value hits: `cdd_guidance/practices/clean_engineering/model/rules_shared/operation_checks.py:97-104`.
