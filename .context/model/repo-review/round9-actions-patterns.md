# Round 9: actions, patterns, builders, agents, context setup, sketch document, judged across files

Area: `cdd_guidance/actions`, `cdd_guidance/patterns`, `cdd_guidance/builders`, `cdd_guidance/agents`, `cdd_guidance/context_setup` and `cdd_guidance/practices/sketch_document` (not `_examples`). Branch `ensure-domain-orientation-refactor` at 5f36e6a2, read on 2026-11-08. The CDD MCP host serves `~/.cdd/runtime` at the same commit (checked with `git log -1` there; `cdd.ping` answered `pong`).

## How each check ran

**Graph rules: run, for the first time in this area since round 5.** Two `validate.validate` calls, one after the other, each with `graph: true` and `paths` set to the six area folders (absolute, forward slashes):
- `clean-engineering-modules`: answered "still running" once, then returned. Report `C:\Users\jeffa\.cdd\runtime\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261109T014534.md`.
- `clean-engineering-code`: answered "still running" once, then returned. Report `…\clean-engineering-code-20261109T014640.md`.

Both reports hold the same 118 graph hits over 14 rules, so the round-8 Stories reader crash is gone. The hits by rule:

| rule | hits | counted | verdict |
|---|---|---|---|
| `use-typed-signatures` | 58 | 0 | Not counted, as in other areas: `Any` on `session` (harness and actions cannot name space's *Session*), and the pattern rule scanners' `(node, context)` signatures. Sketch and Validate still leave `session` and `call` untyped after round 8 removed `chat` from them; the base types `call: ToolCall \| None`. |
| `limit-operation-parameters` | 16 | 0 | Real, not counted (clean-code, single function). `ContextSetup._capture`, `smoke_test`, `scout_app` and `complete_capture` each take the same five capture arguments, because each is an MCP tool that makes a *LiveAppCapture* from them. |
| `keep-operations-small-focused` | 11 | 0 | Real, not counted. Most are recipe docstrings counted as lines (`diagnose` 107, `capture_from_live_app` 75). |
| `prefer-instance-operations` | 10 | 0 | `PartitionIndex` and `Segment` static helpers; small pure parsers. |
| `one-way-deps` | 4 | 1 | **Finding B1.** |
| `no-module-per-class` | 4 | 0 | `actions/diagnose`, `improvement`, `iterate`, `sketch`. Decided, by L8's reason: the installer and catalogue find one folder per action, which holds its recipe markdown and templates. |
| `use-intention-revealing-names`, `avoid-vague-parameter-names` | 3, 3 | 0 | `item` in the actions' `on` callbacks (the `each` contract), `config` in `Segment`. |
| `simplify-control-flow`, `keep-operations-single-responsibility` | 2, 2 | 0 | `_LernReading._context_mappings` (see B3), `tier_facts._braced_body`; `Validate.validate`, `ContextSetup._convert_source`. |
| `eliminate-duplication` | 2 | 1 | `SegmentNotFound.__init__` near-copies `ContextFileNotFound.__init__`: **finding B2**. `CddWebDomainAccess.__init__` duplicates `CddClaudeMod.__init__`: dismissed (last section). |
| `use-explicit-dependencies` | 1 | 0 | `OpenAIEmbeddingProvider` makes `OpenAI()`; dismissed as in round 5 (the provider is the adapter a caller swaps). |
| `provide-meaningful-context` | 1 | 0 | `validation_report.py:92`, the number 92. |
| `deep-module` | 1 | 0 | `sketch_document` exposes 2 of 3 classes. Dismissed (last section). |

No hits for `hide-inner-details`, `hold-state-on-the-object-not-in-parameters`, `low-coupling`, `put-logic-on-the-owning-resource` or missing module context.

**AI judgment: run, and checked by running the code.** I answered every `@agent_instructions` recipe of the eleven actions, `ContextSetup` and `ContextIndex` the way the MCP host does (`toolset.instruction(name).answer(ToolCall(arguments, project))`), with only the required arguments, at `stories-story-map` and `stories-acceptance-tests`, in a project with a session open (probe `…/a5c5bdbb8e4b6072/…/scratchpad/r9_ap_expand.py`, the round-8 probe with UTF-8 output; output `r9_probe_*.txt`, replies `r9_dump_*.txt`). A second probe (`r9_grill_fid.py`) asks Grill, Iterate, Sketch, Generate, Satisfy and Repair at five non-first fidelities (`stories-acceptance-tests`, `ddd-model`, `ux-mockup`, `clean-engineering-code`, `bdd-realization`), **twice each**, and counts the named fidelity's overview, template and first rule in the reply. A third (`r9_capture_flow.py`) reads the option words the capture recipe offers and sends each, and all of them together, through `partition` → `segment_files` → `embed`, with a session open and with none. A fourth (`r9_render.py`) sends Render through its served tool for a fidelity, a practice, two patterns and a list.

What the runs showed:
- No recipe raises. Reply sizes match round 8 within a few characters at `stories-story-map`.
- Grill, Iterate, Sketch and Generate at every non-first fidelity carry that fidelity's overview once, its template once where it has one, and no story-map rule. Two calls in a row give identical replies.
- The capture recipe offers `stories | ddd | ux | clean-engineering | bdd`. Every word, and all five together, partitions, lists its segment and embeds it, with and without a session.
- The live-app recipe names `out_path` on both `embed` steps.
- Render answers through the fidelity for a fidelity, a practice and a list.
- No reply holds a blank clause or a garbled f-string.
- An unknown slug now raises `UnknownGuidance: no practice or fidelity has the slug 'clean_engineering'; the slugs are …` (the round-8 harness-core note is fixed).

**Code metrics.** I ran `measure_revision.measure(Path('.'), 'r9', None)` and read the offenders in this area:
- Classes over 100 total complexity or 30 methods: only `_LernReading` (`patterns/lern_domain_driven/graph_overlay.py`, 104). Its misplaced job is B3.
- Next largest: `CheckedGraph` 70, `TierFile` 66, `Segment` 56, `SketchOutline` 55, `LiveAppCapture` 49 (23 methods), `Generate` 41. `CheckedGraph` holds the "named path must be there and under the session's root" job, which is part of B2. The others each hold one job (a file reader, a segment's completeness, a sketch reader, one live-app capture).
- Functions over 20 paths: none. Over 10: `_LernReading._link_tiers` 12, `_aggregate` 11, `_context_mappings` 11, `Generate._earlier_render` 11. The hardest to read is `_LernReading._context_mappings` (20).
- Duplicated helper names and body clones: none in this area.
- `classes_with_unrelated_jobs`: `PartitionIndex` 4 (its static config-key readers) and `Segment` 3. Small parsers on the object that owns the file; not counted.

## Findings, most severe first

| # | file:line | concern | found by | status | fix in one line | severity |
|---|---|---|---|---|---|---|
| B1 | patterns/__init__.py:9-14; patterns/domain_driven_stack.py:8; lern_domain_driven/lern_domain_driven.py:13; mern_domain_driven/mern_domain_driven.py:8 | 7 | graph (`one-way-deps`, 4 hits) | new scope | **The `patterns` package and its stack packages import each other.** `patterns/__init__.py` imports `LernDomainDriven` and `MernDomainDriven` to register them, and both import `DomainDrivenStack` from `patterns/domain_driven_stack.py`, a file of the `patterns` package itself. The package is both the composition root and the shared base, so importing either stack runs `patterns/__init__`, which imports the stack again. No run-time fault follows; it is a structural cycle of the same shape as round 8's board-page finding in space/tools. Round 5 kept `domain_driven_stack.py` at the package root as its shared base, before the cycle scanner read packages. Move `DomainDrivenStack` into a package of its own below the stacks (for example `patterns/domain_driven_stack/`), so `patterns/__init__` only registers | high |
| B2 | context_setup/context_index.py:117-123, :175; actions/grill_context/grill_context.py:18-23, :82; actions/validate/checked_graph.py:14-19, :132-144, :165-167 | 1 | graph (`eliminate-duplication`, 85%) + AI | new scope | **Three classes refuse a path the agent named that is not in the project, each with its own error.** `SegmentNotFound` ("no segment file at …; name it from the project's root, or absolute"), `ContextFileNotFound` (the same sentence with "context file") and `PathsNotFoundError` ("Name paths from the project's root, or absolute"). Each caller resolves the name through `session.path_named`, then tests `is_file()`/`exists()` itself, and `CheckedGraph._under_root` also tests "under the session's root" by hand. `SegmentNotFound` was added by the round-7 N4 fix beside the round-3 `ContextFileNotFound`; rule 2 ("grep for the job before you change anything") was missed. *Session* already owns naming a path in its project (`path_named`); give it the check too (one method that returns the existing path or raises one domain error carrying the name and the project), and have the three callers use it | medium |
| B3 | patterns/lern_domain_driven/graph_overlay.py:169-196 (`_context_mappings`, `_aggregate_named`); practices/ddd/model/schema.yaml:18-24 | 9 | AI, with metrics evidence | new | **The LERN overlay reads DDD's context mappings out of DDD's own markdown.** DDD's schema declares `boundedContext.mappedTo → contextMapping(local, remote, pattern)`, but no DDD reader makes a `ContextMapping`: only `_LernReading._context_mappings` does, by opening the bounded context's file and matching `Local → Remote` lines with its own regex. So the bounded context's file is read by DDD's reader and by the pattern's overlay, and a project without LERN never gets the mappings its DDD schema describes. `_aggregate_named` also resolves a `Context · Aggregate` label by hand beside DDD's own `·`-split target reading (`MarkdownIntegration`, `practices/ddd/model/markdown/nodes.py:118-128`). This job is the largest part of `_LernReading`, the only class over 100 total complexity in this area (104), and `_context_mappings` is its hardest-to-read function (20). Also concern 5 (logic not on its owner). Have DDD's graph reading make the mappings it declares, and let the overlay only link aggregates to its tier files. Owner: practices (DDD) for the reader, this area to delete the overlay's copy | medium |
| L7 | .context/repo-model.md:2737 | 11 | AI | decided | `partition/.context/cdr/0001-repository-model-lists-partition-as-it-was-read.md`. Agreed | — |
| M4 | validate/checked_graph.py:62-68 | 5 | AI | decided | `0001-violations-read-by-practice-key.md`. Agreed | — |
| M5 | generate/generate.py:52-62 | 2, 5 | AI | decided | `0001-formats-compared-through-format.md`. Agreed | — |
| N10 (part) | validate/checked_graph.py:100-113 | 1, 9 | AI | decided | Named graph files are read through `SavedGraph.from_file`. Agreed | — |
| M10 | lern_domain_driven/practices/stories/model/claude_design/fixtures.py:23 | 3 | AI | decided | `0001-canvas-fixtures-built-in-the-chat.md`. Agreed | — |
| L8 | builders/create_agent_toolset, builders/create_practice_guidance, patterns/mern_domain_driven, patterns/cdd_claude_mod; now also actions/diagnose, improvement, iterate, sketch (graph `no-module-per-class`) | 8 | AI + graph | decided | One folder per skill or action, which the installer finds and which holds its recipe and templates. Agreed | — |

## Fixed since round 8

- **A1 (high, regression).** `_inside` hands the inner action its outer action (`inner._outer = self`), and `fidelity_of` asks `_outer` for any practice it did not list itself, so the inner Generate works at the fidelity the grill names. Measured: Grill, Iterate, Sketch and Generate at five non-first fidelities each give that fidelity's overview, template and rules, and no story-map rule; two calls in a row are identical. Spec: `fidelity_text_spec.py` "an action that works at a fidelity past its practice's first" (generate, sketch, grill at `ddd-model` and at `stories-acceptance-tests`, iterate).
- **A2.** The capture recipe's options are `self.partition.practice_slugs`, the slugs of the practice set partition works with, so there is one list. `cdd` and `clean_engineering` are gone from the repository. Spec: `capture_documents_flow_spec.py` "the indexers a capture recipe offers" sends every offered word through partition.
- **A3.** Both live-app `embed` steps name `out_path` (`<overview folder>/rag`). `embed`'s docstring and the module card say it reads any markdown file, including the extraction overview. Spec: "a live-app capture recipe answered with only the application's folder" and "an index embedded from a capture's extraction overview".
- **A4.** Render calls `item.render_files(…)` / `item.render(…)` on the fidelity `each` hands it. `PracticeGuidance.render_at` is deleted, with no reference left in code, docs or cards.
- **A5.** Grill says "Grilling session started; the plan is the one the user describes." when no plan or paths are sent; the Iterate and Sketch replies carry the same line. `source_label` has no other caller that leaves a blank.
- **A6.** Document's docstring says "the session's root". `grep "session path"` finds nothing left in `harness`, `space`, `tools` or `cdd_guidance` but a constructor note in `space/session/.context/session-context.md` and the worktree rule, which mean other things.

## Did the fix agents follow the round-8 fix rules?

- **Rule 7, grep for the pattern before closing.** Followed for A2 (no option word left anywhere), A4 (`render_at` gone everywhere), A5 and A6. Missed one level up: the round-7 N4 fix that made `SegmentNotFound` did not look for the existing `ContextFileNotFound` (B2). That fix predates rule 7, so B2 is new scope rather than left.
- **Rule 8, action specs at a non-first fidelity and every option word.** Followed: `fidelity_text_spec.py` now asks Generate, Sketch, Grill (two fidelities) and Iterate past the first fidelity, and the capture flow spec sends every offered word.
- **Rule 9, two served calls give the same answer.** My probe answered every recipe twice at five fidelities: identical each time.
- **Metrics gate.** The round-8 changes here made the code smaller: Render's `on` lost a lookup and a parameter, Sketch and Validate lost the `chat` parameter. No metric got worse in this area.

## Outside this area (not counted)

- **Practices (DDD):** the reader half of B3. DDD's graph reading should make the `ContextMapping` nodes its schema declares.
- **Harness graph doc:** `harness/graph/.context/graph-populate-model.md:624` describes `ContextMapping`s as the LERN overlay's work; it needs updating when B3 moves the job.

## Counts

- **By concern** (a row counts once per concern; 3 counted rows; decided rows not counted):
  - 1: 1 (B2)
  - 7: 1 (B1)
  - 9: 1 (B3)
  - 2, 3, 4, 5, 6, 8, 10, 11, 12: 0
- **By severity:**
  - high 1 (B1)
  - medium 2 (B2, B3)
  - low 0
- **By status:**
  - fixed: 6 (A1, A2, A3, A4, A5, A6)
  - left: 0
  - regression: 0
  - new: 1 (B3)
  - new scope: 2 (B1, B2)
  - decided: 6 (L7, M4, M5, N10 part, M10, L8)

## Goal-class counts

| goal class | new | new scope | left | regression | total |
|---|---|---|---|---|---|
| Bad resource orientation (5, 9) | 1 (B3) | 0 | 0 | 0 | 1 |
| Shadow models (2) | 0 | 0 | 0 | 0 | 0 |
| Duplicated functions (1, 12) | 0 | 1 (B2) | 0 | 0 | 1 |
| **Total** | 1 | 1 | 0 | 0 | 2 |

Round 6 had 14 goal-class findings here, round 7 had 2, round 8 had 4, and round 9 has 2. All four round-8 goal findings are fixed (A1, A2, A3, A4), and **no high finding remains in the three goal classes**. The two now:
- **B2** was found by the graph check, which ran here for the first time since round 5.
- **B3** sits in code every round has read. The metrics pointed at it: `_LernReading` is this area's only class over 100 total complexity.

The one high finding, B1, is a package cycle (concern 7), outside the goal classes.

## What would make the next round cheaper

1. **When a pattern reads a practice's file, ask whether the practice should read it.** The LERN overlay builds DDD schema nodes from DDD's markdown (B3), and the practices' readers never learned to. Before a pattern overlay adds a node type that lives in a practice's own `schema.yaml`, the fix agent should grep that practice's graph reading for the type. If nothing makes it there, the job belongs in the practice.
2. **Grep for the error sentence, not only the function name.** B2's three refusals share almost the same message, so `grep "from the project's root, or absolute"` finds all three at once, and `grep "(FileNotFoundError)"` finds the classes. A fix that adds a new error class should run that grep first.

## Scanner false positives

- **`deep-module` on `practices/sketch_document`** (`cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py:20`, `_MIN_MEASURED_CLASSES = 3`, used at `:131`). The module holds three classes, and one is a private record (`_Section`). Its seam is the two classes its card names, *SketchOutline* and *DiscoveryDocument*, each used by Stories and DDD. With three classes, 40% allows one public class, so any three-class module with a two-class seam fails. The comment at `:19` already says one- and two-class modules cannot be measured. A module whose only hidden class is a private record is in the same position. Measure from four classes, or leave private records out of the count.
- **`eliminate-duplication` on `CddWebDomainAccess.__init__` and `CddClaudeMod.__init__`** (`cdd_guidance/practices/clean_engineering/rules/operation_checks.py:325-329`, the exact body fingerprint). Both bodies are one `super().__init__(format="typescript", default_workspace_folder="harness")` call with literal arguments. That is each pattern's configuration, not logic that could have one owner. The exact-copy branch should skip a body that is a single call with only literal arguments, as the near-copy branch's minimum size already does for small bodies.
