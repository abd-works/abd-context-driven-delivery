# Round 8: practices-ce-bdd (Clean Engineering, BDD, agent BDD, and the graph rule scanners)

Area: `cdd_guidance/practices/clean_engineering`, `cdd_guidance/practices/bdd` and `cdd_guidance/practices/agent_bdd`, without `_examples`, plus the graph rule scanners (`clean_engineering/rules`, `clean_engineering/model/production_code.py`, `harness/graph/skipped_folders.py`, and `harness/graph/schema_rules.py` with `harness/graph/rule_fixture.py` as they pair rules with node types). Worktree `ensure-domain-orientation-refactor` at 4359b907; the CDD MCP host runs `~/.cdd/runtime` at 2c30c2f7, whose code is identical to 4359b907 (`git diff 2c30c2f7 4359b907` is empty). Judged against `validate-brief.md` and the round 5–8 briefs. No code was edited.

Every finding of `round7-practices-ce-bdd.md` (N4, N13, S3, S7, S8, S9, and the decided M17) was checked against the code. The round-7 fix for this area is 22d9d132 with its work-in-progress commits 58f068fa and b1bcc798; the graph fix is c07e1a21. No new decision record was written in this area since round 7; the four read were `clean_engineering/.context/cdr/0001-test-code-known-by-name.md`, `0002-near-copies-compare-operation-bodies.md`, `clean_engineering/model/.context/cdr/0001-format-render-follows-the-harness-render-call.md` and `harness/graph/.context/cdr/0001-graph-builds-run-apart-from-the-server.md`.

The area's 43 quick specs and `cdd_guidance/practices/practice_rules_spec.py` and `harness/graph/schema_rules_spec.py` all pass (`drawio_scanner_spec.py` passes with `PYTHONUTF8=1`, which `scripts/test.ps1` sets).

## The graph check failed again, so this round is AI only

**The one call failed.** `validate(guidance="clean-engineering-code", graph=true, paths=[.../clean_engineering, .../bdd, .../agent_bdd])` answered "still running" fourteen times, then failed with:

```
RecipeLineFailed: Validate.validate recipe line C:\Users\jeffa\.cdd\runtime\cdd_guidance\actions\validate\validate.py:57
`graph_paths = self._graph.check_beside(self._reports)` failed: GraphBuildFailed: the graph build's worker process exited with 1:
  File "...\harness\graph\graph_worker.py", line 30, in main                 built = Graph().carry_out(order)
  File "...\harness\graph\graph.py", line 1530, in _read_working_copy         practice.link_to_other_practices()
  File "...\cdd_guidance\practices\stories\stories.py", line 129             StoryLinks(self, self.object_model).link()
  File "...\cdd_guidance\practices\stories\model\graph_reading.py", line 111, in link       self._link_step(step)
  File "...\cdd_guidance\practices\stories\model\graph_reading.py", line 118, in _link_step  body = self._step_body(step)
  File "...\cdd_guidance\practices\stories\model\graph_reading.py", line 147, in _step_body  return f"{step.name}\n{step.body.text}"
AttributeError: 'Node' object has no attribute 'body'
```

`cdd_ping` answered `pong` straight after, so the host is up and the build's worker process is what failed. Following `.claude/rules/mcp-fail-loud.md`, I made no further graph call and did not run validate any other way. **No graph hit was judged this round**, so S3 could not be rechecked a second time.

**Cause (for harness upper and Stories; not counted here).** It is the round-7 crash again in a sibling reader. The session graph already holds Stories (the other validators share the session). A refresh rebuilds that graph in the worker from its saved shape, where every node outside the refreshed paths is a plain `Node` with its saved facts (`InGraph.restore`, `graph.py:1075`). c07e1a21 fixed only DDD (`PracticeNodes.nodes_read_now`, so DDD builds its blocks from the nodes this build read). `StoryLinks.link` (`stories/model/graph_reading.py:108-111`) still walks every Step, Given, When and Then in the graph, restored ones included, and `_step_body` (`:147`) reads `step.body.text`, which only a parsed step has. So every graph validate fails once Stories is in the session graph, whatever paths it names. Severity high (wrong behaviour; it blocks the graph half of every area's round for the second round running). Two round-7 fix rules were missed here: **fix every sibling** (the DDD fix was not applied to the other readers that link across practices: Stories' `StoryLinks`, and any UX reader of the same shape) and **specs take the live path** (`harness/graph/graph_build_spec.py:134-175` builds Clean Engineering and DDD through the worker on a restored graph, but no spec does it with Stories, UX or BDD loaded).

BDD's own linking is safe from this: `ObservationLinks` (`bdd/model/graph_reading.py:72-163`) reads only facts (`reach`, `setup_reach`, `owner`) and source lines, which a restored node keeps. I also checked whether a worker refresh loses Clean Engineering's cross-file near-copy hits, since `near_copies._runs_of` (`near_copies.py:67-74`) and `ClassGraph.fields` (`class_graph.py:97-108`) read typed attributes through `getattr` and would find nothing on a plain node. A scratch probe (two files with copied bodies, refreshed in the worker, then refreshed again on an unrelated file) kept the `eliminate-duplication` hit in every case, so that suspicion is dismissed.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|---|---|
| N4 | `clean_engineering/model/.context/module-context.md:8`; `rules/practice_wide_rules.py:144-146` `_allowed_public` | 6 | AI | left (partly) | `ProductionCodeRule` now lives in `rules/production_code_rule.py`, and the model no longer imports `harness.graph.practice_rule`. The rest of the finding stands by the model's own count: its card says 33 of its 82 classes are named outside it and calls that 40%, but `deep-module` allows `int(0.4 × 82)` = 32, so the module still fails the rule by one class, and the card states the rule's limit as if it passed. | Take one more class out of the seam (or out of the module), and have the card quote the count the rule allows. | low |
| R8-1 | `clean_engineering/model/.context/ooad-model.md:285`, `:292`; `bdd/model/.context/bdd-model.md:92` | 11 | AI | new | The class models still list names the round-7 fix deleted or changed: `SourceText.private_reach()` (gone), `reaches_peer_private(parameter_names)` (now takes no parameter), and the Spec's `code_like_describe_lines` fact (gone; each describe and context now judges its own name through `reads_like_code`). The fix updated the module cards but not these model documents. | Update both model documents with the round-7 shape. | low |
| R8-2 | `clean_engineering/model/python/_examples/put-logic-on-the-owning-resource/` (faulty and repaired) | 3 | AI | new | The round-7 fix deleted the `PutLogicOnOwningResource` scanner (the reach is now reported only by `hide-inner-details`; `put-logic-on-the-owning-resource` stays a prose rule in `schema.yaml:81, 148`) and the spec example that read this pair, but left the example pair. Nothing reads it now: it is the only one of the 31 python `_examples` folders no spec names, and `example_asset_paths` is reached only from specs. The no-use rule was again applied to the deleted names and not to what only they used. | Delete the folder, or move the pair under `hide-inner-details` if it adds a case that folder lacks. | low |

Decided, not counted:
- **M17** (`render` signatures differ across formats). Unchanged since round 7: `clean_engineering/model/.context/cdr/0001-format-render-follows-the-harness-render-call.md` gives the work to harness core's render call. I still agree, for the reason given in round 7.

### Scanner findings

| # | scanner file:line | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|
| S10 | `clean_engineering/rules/class_graph.py:117-127` `is_failure`/`_derives_failure` against `:134-142` `_derives_value` | new | The round-7 fix for `do-not-invent-parallel-object-models` (a failure keeps the name of what it failed on) added a second walk up a class's bases that copies `_derives_value`'s: the same suffix test (`_FAILURE_SUFFIXES`), the same `seen` guard, the same recursion through `bases_of`. `_derives_value` already answers "is a failure" as one of its cases, so the job is done twice and the two can drift. | One derivation walk that takes the test to apply; `is_value` asks `is_failure` for its failure case. | low |
| S11 | `harness/graph/rule_fixture.py:46-72` `SchemaRuleRun` against `harness/graph/graph.py:1032-1063` `InGraph.check`/`_check_each_node` | new | The spec support written so rule specs take the live path re-implements the live loop instead of calling it: it keeps a practice-wide hit only on a node that carries the slug (what `GraphRulesCollection.record_violation` does), and runs a node check only when the node's entry `runs`. It leaves out what the live loop also does: skipping the checks a covering class of another practice already ran (`_covering_classes`). A spec through it can pass where validate behaves differently. | Let `InGraph.check` run one named rule, and have the fixture call that. | low |
| S3 | `clean_engineering/rules/operation_checks.py`, `class_graph.py` (`use-explicit-dependencies`) | not rechecked | The graph build failed again (above), so whether the 10 round-6 hits are gone still needs the graph. | Recheck next round. | low |

## Fixed since round 7

- **N13:** `car_tool_argument`, `invoke_request_for_path`, `stage_invoke_commands`, `ensure_invoke_staged`, `invoke_toolset`, `expect_tools_include` and the `CAR*` constants are deleted from `agent_bdd/spec_helpers.py`. The two refusal examples moved to `agent_bdd_spec.py`, where they test `ToolsetInvoke.for_toolset` itself. Every helper left (`repo_root_from`, `sessions_dir`, `expect_ok_action`, `expect_instructions_contain`, `generate_similar_prompt`, `generate_similar_rubric`) is used by the template, the examples or `agent_block.py`, and the card names only those.
- **S7:** one private-reach measure. `SourceText.private_reach`, `_PRIVATE_REACH` and the `private_reach` fact are deleted. `SourceText.reaches_peer_private` and `PythonFunctionBody.reaches_peer_private` now apply the same exceptions: own receivers, `cls` and a classmethod's first parameter, dunders, wired repositories, and same-field copies. `PutLogicOnOwningResource` is deleted, so `hide-inner-details` is the one rule that reports the reach. Specs in `production_code_rules_spec.py:280-299` (local receiver, classmethod, dunder, same-field copy, "the one rule that reports the reach").
- **S8, S9:** BDD's schema lists `layer-isolation` on `spec`; `describe-is-plain-english`, `describe-is-subject-not-internal`, `observable-behavior` and `no-implementation` on `context`; `observable-behavior` on `description`. `PlainEnglishOnly` judges each Description and Context by its own name (`reads_like_code`). A block's facts are measured over its own lines (`BehaviorNode.own_lines`), so a context's setup is judged once and an observation's body is not repeated on its context; shared setup hooks count as implementation. The Spec's private probe reads only lines no describe holds. Specs reach each rule through the schema (`bdd_examples_spec.py:29-145`, via `SchemaRuleRun`).
- **The cross-practice schema-alignment spec** asked for in round 7 now exists: `cdd_guidance/practices/practice_rules_spec.py` compares every shipped practice's rules with its `PracticeSchema.applicable`; the Clean Engineering-only copy was removed from `production_code_rules_spec.py`.
- **Round-7 observation, markdown dependency details:** `MarkdownOoadClass` writes and reads each dependency's details (`Relationship.lines`/`read_lines`, `OoadClass._keep_dependency`); specs in `class_stereotypes_spec.py:131-141`.
- **N4, the part that names the class:** `ProductionCodeRule` moved to `rules/production_code_rule.py` and every rule imports it from there (the measure part is left, above).

## The round-7 fix rules

- **Specs take the live path, rules:** followed in this area. `RuleFixture.hits` and `RulePair` go through `SchemaRuleRun`, and the three Clean Engineering specs that called `rule.check` on a hand-picked node now call `node_hits` (`ce_rules_spec.py:192, 416, 447`). No rule spec in the area calls `check` directly. S11 records that the live path is a copy of the graph's loop rather than the loop itself.
- **Specs take the live path, graph reading:** missed outside this area (the Stories crash above). In this area no spec builds BDD's or Clean Engineering's reading through the worker on a restored graph that holds BDD; BDD's reading reads only facts, so it does not fail today, but nothing would catch it if it began reading a typed attribute.
- **Fix every sibling:** followed for the rule-to-schema alignment (one spec over all five practices) and for the reach measure (Python and brace languages). Missed for the model documents (R8-1), the rule's example pair (R8-2), and, outside the area, the restored-node fix (Stories).
- **One owner per finding:** followed; the Stories and DDD schema gaps listed in round 7 were fixed in the same commit by the practices agent, with no second copy of the fix.

## Other observations (not counted)

- 63 files under `.agent_bdd_sessions/` folders are still tracked in git across the repository (for example `harness/agent_tools/.context/.agent_bdd_sessions/`), although `.gitignore` ignores them.
- `production_code_rules_spec.py:148` still enumerates the rules whose `check` is their own, which is how the round-6 per-node rule fix is held; it passes.

## Counts

This summary table is headed "by concern" so `concern_counts.py` counts only the finding rows above.

| by concern | high | medium | low |
|---|---|---|---|
| 3 no use | – | – | R8-2 |
| 6 seams that leak | – | – | N4 |
| 11 legacy left | – | – | R8-1 |

**3 finding rows** (round 7: 2): 0 high, 0 medium, 3 low. **By status:** 1 left (N4, partly), 2 new (R8-1, R8-2), 0 new scope, 0 regressions; 1 decided (M17). 1 round-7 finding row fixed (N13), plus the scanner findings S7, S8 and S9. **By check:** all AI. Plus 2 new scanner findings (S10, S11), both low, and S3 still not rechecked. The graph check did not run (build failure above), so the new-scope hits this round was meant to measure for the first time are still unmeasured in this area.

Not counted in this area: the graph build failure (high, owner harness upper and Stories).

Nothing was found for concerns 1, 2, 4, 5, 7, 8, 9, 10 or 12 in the area's code outside the scanner tables.

## Goal-class counts

| goal class | round 5 | round 6 | round 7 | round 8 left | round 8 new | round 8 new scope | round 8 total |
|---|---|---|---|---|---|---|---|
| bad resource orientation (5 + 9) | 12 | 10 | 0 | 0 | 0 | 0 | 0 |
| shadow models (2) | 8 | 2 | 0 | 0 | 0 | 0 | 0 |
| duplicated functions (1 + 12) | 9 | 4 | 0 | 0 | 0 | 0 | 0 |

The two new scanner findings S10 and S11 are duplicated functions in kind (concern 1). Scanner rows have not been counted in the goal classes since round 6, so they are not counted here either; counting them would make this area's duplicated-functions total 2 (both new, both low). As in round 7, the zero is what the AI check found; the scanners have not confirmed it, because the graph check has not run for two rounds.

## What would make this area's next round cheaper

1. **When a fix deletes a rule or a name, delete its documents and fixtures in the same change.** Round 7 said to follow a deleted function's callees; this round the same miss shows up in documents and examples: the model documents that list the deleted measure and fact (R8-1) and the example pair only the deleted rule's spec read (R8-2). A grep of the deleted slug and names over `.context/` and `_examples/` before committing catches both.
2. **Write a spec support by calling the code it stands for.** `SchemaRuleRun` and `_derives_failure` each repeat a loop that already exists one file away. A fix that needs "the same as X but for one rule" or "the same walk with another test" should give X that parameter, not copy it.
