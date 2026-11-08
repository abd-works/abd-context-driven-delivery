# Round 7: practices-ce-bdd (Clean Engineering, BDD, agent BDD, and the graph rule scanners)

Area: `cdd_guidance/practices/clean_engineering`, `cdd_guidance/practices/bdd` and `cdd_guidance/practices/agent_bdd`, without `_examples`, plus the graph rule scanners (`clean_engineering/rules`, `clean_engineering/model/production_code.py`, `harness/graph/skipped_folders.py`, `harness/graph/schema_rules.py` as it pairs rules with node types). Worktree `ensure-domain-orientation-refactor` at c8921451; the CDD MCP host runs `~/.cdd/runtime`, also at c8921451. Judged against `validate-brief.md`, `validate-brief-round5.md`, `validate-brief-round6.md` and `validate-brief-round7.md`. No code was edited.

Each finding of `round6-practices-ce-bdd.md` (N1–N15, M3, M4, M10, M17, L8, S1–S6) was checked against the code. The fix commits for this area are cd699291 (CE/BDD), a6e02056 and 39df16f8 (scanners), and e562aa96 (agent BDD). The decision records read: `clean_engineering/.context/cdr/0001-test-code-known-by-name.md`, `0002-near-copies-compare-operation-bodies.md`, `clean_engineering/model/.context/cdr/0001-format-render-follows-the-harness-render-call.md`, and `harness/graph/.context/cdr/0001-graph-builds-run-apart-from-the-server.md`.

## The graph check failed, so this round is AI only

**The one call failed.** `validate(guidance="clean-engineering-modules", graph=true, paths=[.../clean_engineering, .../bdd, .../agent_bdd])` answered "still running" ten times, then failed with:

```
RecipeLineFailed: Validate.validate recipe line ...\cdd_guidance\actions\validate\validate.py:57
`graph_paths = self._graph.check_beside(self._reports)` failed: GraphBuildFailed: the graph build's worker process exited with 1:
  File "...\harness\graph\graph_worker.py", line 30, in main          built = Graph().carry_out(order)
  File "...\harness\graph\graph.py", line 1469, in _read_working_copy  practice.read_working_copy()
  File "...\cdd_guidance\practices\ddd\ddd.py", line 81                DddReading(self).read()
  File "...\cdd_guidance\practices\ddd\model\graph_reading.py", line 203, in _members_by_folder   kind = tactical.inferred_kind(names)
  File "...\cdd_guidance\practices\ddd\model\stereotypes.py", line 98, in kind   return kind_named_by(self.oclass.stereotypes)
AttributeError: 'Node' object has no attribute 'stereotypes'
```

`cdd_ping` answered `pong` straight after, so the host is up; the build's worker process is what failed. Following `.claude/rules/mcp-fail-loud.md`, I made no further graph call and did not run validate any other way. **No graph hit was judged this round**, so no scanner hit is confirmed or dismissed, and S3 could not be rechecked.

**Cause, as far as the code shows (for harness upper and DDD, not counted here).** Since 7f24bdac a refresh sends the graph it holds to `graph_worker`, which rebuilds it from the saved shape (`harness/graph/.context/cdr/0001-…`: "plain nodes with their facts, edges, and violations"), then reads only the edited files again. Clean Engineering's `OoadClass` nodes outside the refreshed paths are therefore plain `Node`s, but `DddReading._members_by_folder` (`ddd/model/graph_reading.py:197-203`) wraps every `OoadClass` node in `TacticalClass` and reads `.stereotypes`, which only a parsed `OoadClass` has. So every graph validate whose session graph already holds a load fails once DDD is among the practices read, whatever paths it names. Severity high (wrong behaviour; it blocks the graph half of every area's round). The fix belongs to whoever owns the DDD reading and the worker: DDD reads the class's stereotypes through the node's facts, or the worker re-parses the classes DDD reads.

## The BDD rule-versus-schema gaps

A rule runs on a node only when the practice's `model/schema.yaml` lists the rule on that node type **and** the rule's `node_types` include it (`harness/graph/graph_rules_collection.py:120-123`). I compared both for every BDD rule with a scratch script (`PracticeSchema(Bdd()).applicable` against each rule's `node_types`); the facts each rule reads come from `bdd/model/bdd_model.py:22, 55-61` (the Spec) and `bdd/model/nodes.py:66, 76-81` (every describe, context and observation).

| rule | judges (`node_types`) | schema lists it on | the fact it reads is on | real? |
|---|---|---|---|---|
| `layer-isolation` | Spec | observation | Spec (`patches_infrastructure`) | **Real, and the rule never runs.** It is listed only where it does not apply, and applies only where it is not listed. A spec that patches infrastructure at import time is never reported. |
| `describe-is-plain-english` | Spec | description | Spec (`code_like_describe_lines`) | **Real, and the rule never runs**, for the same reason. |
| `observable-behavior` | Spec, Description, Context, Observation | spec, observation | every node (`private_probe`) | **Real, partly.** It runs on the Spec and on each Observation, never on a Description or Context. The Spec's fact holds only the file's first probe, so a probe in a describe's or context's setup is reported only when it is the first in the file; a probe inside an `it` is reported twice (Spec and Observation). |
| `describe-is-subject-not-internal` | Description, Context | description | node name | **Real, partly.** A context named for an internal type (`with a SessionLog`) is never reported. |
| `no-implementation` | Observation, Context | observation | every node (`has_implementation`) | **Real, partly**, but listing Context in the schema alone would be wrong: a context's `has_implementation` is measured over its whole span, children included, so every observation's hit would repeat on each enclosing context. Either measure a context's own setup only, or drop Context from the rule. |
| `framework-syntax`, `shared-describe-subject`, `state-not-when`, `one-assertion-per-test` | — | — | — | aligned |

The round-6 fix wrote the check that catches this (`clean_engineering/rules/production_code_rules_spec.py:138-143`, "should carry every rule on each node type the rule judges") for Clean Engineering only. The same comparison run for the other practices finds 13 misaligned Stories rules (for example `kebab-case-paths`, `domain-operation-in-the-step` and `originating-sub-epic-examples` are listed on no type at all, so they never run) and 2 DDD rules (`domain-concepts-not-technical-names` on Aggregate, `screen-interface-not-a-domain-object` on DomainService). Those belong to the Stories/UX/DDD area; I list them so its validator can confirm them.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|---|---|
| N4 | `clean_engineering/model/production_code.py:96-108` `ProductionCodeRule`; `model/.context/module-context.md` (Dependencies line) | 6 | AI | left (partly) | `rules_shared` moved into the practice's `rules` package (only an ignored `__pycache__` folder is left on disk). One rule class stayed: `ProductionCodeRule`, the base every Clean Engineering rule derives from, still lives in the model module, which is why the model imports `harness.graph.practice_rule`. Only the practice's rules use it; BDD and DDD import `is_spec_file`/`is_test_code` only. The model's own card now says 34 of its 83 classes are named outside it (41%), over the 40% that `deep-module` allows, so the module still fails the rule by its own count. | Move `ProductionCodeRule` to `clean_engineering/rules`; the model keeps `TestFileName` and its two questions. | low |
| N13 | `agent_bdd/spec_helpers.py:47` `car_tool_argument`, `:51` `invoke_request_for_path`, `:91` `stage_invoke_commands`, `:108` `ensure_invoke_staged`, `:122` `invoke_toolset`, `:155` `expect_tools_include`; `agent_bdd/.context/module-context.md:4` | 3 | AI | left (partly) | The five named helpers, `violations_for_spec_source`, `CallGraph.of_callees` and the committed agent-run logs in this area are gone, and `.gitignore` now ignores `.agent_bdd_sessions/`. Deleting `run_skill` left the chain it called with no caller but `spec_helpers_spec.py` and `.retired/` specs: the car-skill invoke mapping, its staging, `invoke_toolset`, and `expect_tools_include`. The module card still offers `invoke_toolset` and `expect_tools_include` as the helpers specs repeat. The no-use rule was applied to the names listed, not to what those names called. | Delete the chain and its spec examples; name only the helpers the template and examples use in the card. | low |

Decided, not counted:
- **M17** (`render` signatures differ across formats). `clean_engineering/model/.context/cdr/0001-format-render-follows-the-harness-render-call.md` gives the work to harness core's render call, with the steps that close it. I agree: the signature is set by `PracticeGuidance._call_render`, which drives every practice's formats, and changing two practices alone would make them disagree with it.

### Scanner findings

| # | scanner file:line | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|
| S8 | `bdd/model/schema.yaml:37, 93` against `bdd/rules/layer_isolation.py:16`, `bdd/rules/spec_rules.py:26` | new scope | `layer-isolation` and `describe-is-plain-english` never run in any load: each is listed on a node type its check does not judge, and its check judges a type the schema does not list it on (table above). | List both on `spec` and take them off `observation` and `description`; add the BDD twin of the schema-alignment spec. | medium |
| S7 | `clean_engineering/rules/coupling_rules.py:33`, `:44`; `model/operation_metrics.py:220` `SourceText.reaches_peer_private`, `:280` `SourceText.private_reach`, `:405` `PythonFunctionBody.reaches_peer_private`; `model/operation.py:281` | new scope | Two measures answer "does this body read another object's `_` member", and `hide-inner-details` reports either. `private_reach` (any receiver but `self`, `this`, `cls`) flags what `reaches_peer_private` deliberately lets through: copying a parameter's `_x` into this object's `_x`, and the wired peer fields. So the exception the measure states never holds for the rule. `put-logic-on-the-owning-resource` reads `peer_private_access` too, so one reach is reported by two rules. These rules were switched on in round 6, so their hits are new to the check. | One measure on `SourceText`/`PythonFunctionBody` with the copy and wired-field exceptions; each rule says which part of it it reports. | low |
| S9 | `bdd/model/schema.yaml` (`description`, `context`) against `bdd/rules/observable_behavior.py:24`, `bdd/rules/tree_rules.py:24`, `:57` | new scope | `observable-behavior` never runs on a describe or context, `describe-is-subject-not-internal` and `no-implementation` never on a context (table above). | List each rule on the types it judges, after making a context's `has_implementation` measure its own setup only. | low |
| S3 | `clean_engineering/rules/operation_checks.py`, `class_graph.py` (`use-explicit-dependencies`) | not rechecked | The graph build failed. a6e02056 says parts built from the owner's own state are now left out, and `SourceText.built_collaborators` / `PythonFunctionBody.built_collaborators` read that way; whether the 10 round-6 hits are gone needs the graph. | Recheck next round. | low |

## Fixed since round 6

- **N1:** a getter's property node takes its type from `value_type` (the getter's `return_type`, a field's `type_hint`), so `hasType` and `dependsOn` follow what it returns (`graph_reading.py:248-264`); spec in `graph_reading_spec.py`.
- **M10:** `Operation.is_property` is a property whose setter makes the getter's kind `Property`; the `parameters` fact is gone and the rules and BDD read parameters through `hasParameter` (`parameters_of`); spec says no copy is kept.
- **N2:** one `TestFileName` in `production_code.py` answers `is_spec_file` and `is_test_code`; BDD's `is_spec_file` and `_is_test_support` are deleted, and `.feature.`, `.e2e.`, `page-driver`, `test-utils` and `fixtures` are all known. Decided in `cdr/0001-test-code-known-by-name.md`.
- **N3, L8:** model documents are read with the practice's `model_document_format`; `graph_reading.py` no longer imports the markdown format and no format is reached by a name string.
- **N5, M4:** `DescribeCalls` nests a script spec's calls and `DescribeCall.adopt` holds them; both code readers add blocks through `add_description`/`add_child`; `_behavior_node` is deleted; spec `describe_calls_spec.py`.
- **N6:** `ModuleContext` reads its card once and answers every card question; a folder's documentation comes from the modules its files were already parsed into (`take_public_sources`).
- **M3:** `_FILE_LANGUAGES` and `SOURCE_SUFFIXES` are gone; a node's `file_language` asks its practice's formats.
- **N7:** `drawio_page.py` moved to `drawio/page/`, so the scanners depend on it one way.
- **N8, N9:** the duplicate `OoadNode` import is gone; the model's card describes the current imports.
- **N10:** `SourceText.top_level_index(es)`; `split_top_level` and `_brace_body` call `top_level_indexes` and `braced`.
- **N11:** `SketchProperty`/`SketchOperation.sketch_lines()`.
- **N12:** `CleanEngineering.members_named(name)` is the one member index; `ObservationLinks` and `GraphBddModel` both ask it; `_returned` is replaced by `value_type`.
- **N14:** practices set `sketch_lens` only.
- **N15:** `_model_documents` is set in `GraphReading.__init__`.
- **S1, S2:** `catalog-examples` and `templates` are skipped folders; `.feature.py` is a spec; `repository_scan_heavy_spec.py` loads this repository and asserts no hit lands in a spec, template, example or `.feature.py` file.
- **S4, S5, S6:** `no-module-per-class` counts child packages; `deep-module` names the allowed count; every per-node Clean Engineering rule derives from `ProductionCodeRule`, so production rules no longer judge specs.
- Also gone: agent BDD's `generate_output` no longer imports the Generate action (e562aa96); it composes the session's own BDD practice.

## The round-6 fix rules

- **A concern-5 fix has a spec on its effect:** followed for N1, M10, N5, N6 (new examples in `graph_reading_spec.py`, `describe_calls_spec.py`, `module_context_files_spec.py`).
- **One owner for a duplicated job, twins gone:** followed for N2, N10, N12, M4, and the dependency-line reader (markdown's `_DEPENDENCY` regex was folded into `Relationship.read_line`). Missed twice, both reported as left above: N4 (one rule class left behind in the model) and N13 (the helpers' callees left behind). Missed a third time across practices: the schema-alignment spec written for Clean Engineering's rules has no BDD, Stories or DDD twin (S8, S9).
- **A skip has a decision record:** followed for M17.

## Other observations (not counted)

- The markdown format reads and writes a dependency's line only (`markdown_class_model.py:139, 212`), while the code formats' doc comment now writes each dependency's `details` too (`class_stereotypes.py:114-120`, from a7b49c63). A class read from code and rendered to markdown loses its dependencies' details, which the model card's purpose ("converting between formats never changes the classes") rules out. Worth a round-trip spec.
- Outside this area, `cdd_guidance/practices/stories/.context/.agent_bdd_sessions/` (13 files) is still tracked in git although `.gitignore` now ignores the folder.

## Counts

This summary table is headed "by concern" so `concern_counts.py` counts only the finding rows above.

| by concern | high | medium | low |
|---|---|---|---|
| 3 no use | – | – | N13 |
| 6 seams that leak | – | – | N4 |

**2 finding rows** (round 6: 20): 0 high, 0 medium, 2 low. **By status:** 2 left (N4, N13, both partly), 0 new, 0 new scope, 0 regressions; 1 decided (M17). 20 round-6 finding rows are fixed (all but N4, N13 and the decided M17). **By check:** both AI. Plus 4 scanner findings: S8 (medium), S7 and S9 (low), all new scope; S3 not rechecked. The graph check did not run (build failure above), so a graph-only finding on old code may be missing from these counts.

Nothing was found for concerns 1, 2, 4, 5, 7, 8, 9, 10, 11 or 12 in the area's code.

## Goal-class counts

| goal class | round 5 | round 6 | round 7 left | round 7 new | round 7 new scope | round 7 total |
|---|---|---|---|---|---|---|
| bad resource orientation (5 + 9) | 12 | 10 | 0 | 0 | 0 | 0 |
| shadow models (2) | 8 | 2 | 0 | 0 | 0 | 0 |
| duplicated functions (1 + 12) | 9 | 4 | 0 | 0 | 0 | 0 |

From 16 class entries to 0 (M17, the only class entry not fixed, is decided). The scanner finding S7 is a duplicated measure inside the rules (concern 1 in kind); scanner rows were not counted in the goal classes in round 6, so it is not counted here either. With the graph check missing, treat the zero as "nothing the AI check found", not as confirmed by the scanners.

## What would make this area's next round cheaper

1. **Write a fix's check for every practice that has the same shape, not only the one named.** The schema-alignment spec caught Clean Engineering's dropped rules; the same three lines over `Bdd`, `Stories` and `Ddd` would have found two BDD rules and three Stories rules that never run. One spec in `harness/graph` that walks `PracticeCatalogue` and compares each practice's `RULES` with its `PracticeSchema.applicable` would keep every practice aligned.
2. **When deleting no-use code, follow its callees.** Removing `run_skill` left the invoke chain it was the only caller of; removing a rule package left its base class behind. A fix brief should say: after a delete, grep each name the deleted code called and delete what now has no caller but its own spec.
