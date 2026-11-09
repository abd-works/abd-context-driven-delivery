# Round 8: actions, patterns, builders, agents, context setup, sketch document, judged across files

Area: `cdd_guidance/actions`, `cdd_guidance/patterns`, `cdd_guidance/builders`, `cdd_guidance/agents`, `cdd_guidance/context_setup` and `cdd_guidance/practices/sketch_document` (not `_examples`). Branch `ensure-domain-orientation-refactor` at 4359b907, read on 2026-11-08. The CDD MCP host serves `~/.cdd/runtime` at 2c30c2f7, the parent of 4359b907; the merge between them changes nothing in this area.

## How each check ran

**Graph rules: failed, not run.** `cdd.ping` answered `pong` before and after. One `validate.validate` call was made: `clean-engineering-modules`, `graph: true`, `paths` set to the six area folders (absolute, forward slashes). It answered "still running" six times, then failed:

```
RecipeLineFailed: Validate.validate recipe line ...\cdd_guidance\actions\validate\validate.py:57
`graph_paths = self._graph.check_beside(self._reports)` failed: GraphBuildFailed: the graph build's worker process exited with 1:
  ...harness\graph\graph.py, line 1530, in _read_working_copy   practice.link_to_other_practices()
  ...cdd_guidance\practices\stories\stories.py, line 129, in link_to_other_practices   StoryLinks(self, self.object_model).link()
  ...cdd_guidance\practices\stories\model\graph_reading.py, line 118, in _link_step   body = self._step_body(step)
  ...cdd_guidance\practices\stories\model\graph_reading.py, line 147, in _step_body   return f"{step.name}\n{step.body.text}"
AttributeError: 'Node' object has no attribute 'body'
```

The session log recorded it: `tool validate.validate …cdd_guidance\actions, …` at 16:40:05Z, and an `error validate.validate …session.err <offset>` line. `session.err` holds the same `'Node' object has no attribute 'body'` eight times, so other areas met it too.

The cause is in the practices area, not this one. It is the round-7 DDD crash again, in a sibling reader:
- `StoryLinks.link` (`practices/stories/model/graph_reading.py:108`) takes every `Step`/`Given`/`When`/`Then` node from `stories.in_graph.nodes()`.
- `_step_body` (`:147`) reads `step.body.text`. In the worker process those are graph `Node`s, which have no `body`.
- The line dates from round 6 (7d3efb535). The round-7 smoke check over `ddd` and `space/session` read no story steps, so it passed. This area's folders do hold story steps: the pattern templates `patterns/lern_domain_driven/templates/tests/{epicSlug}/{subEpicSlug}_server.test.ts` and the MERN twin.
- The round-7 practices fix covered DDD (`TacticalClass`) but missed its Stories sibling. Two fix rules were missed there: rule 5 ("fix every sibling reader") and rule 4 ("a graph-reading spec builds through the worker on a restored graph that holds several practices").

Following `.claude/rules/mcp-fail-loud.md` and the brief, I made no further graph calls and did not run validate through Python. **No graph rule has yet run on this area in any round from 5 to 8.**

**AI judgment: run, and checked by running the code.** I answered every `@agent_instructions` recipe of the eleven actions, `ContextSetup` and `ContextIndex` the way the MCP host does: `toolset.instruction(name).answer(ToolCall(arguments, project))`. Each call carried only the arguments its parameter schema marks required. I ran it for six slugs (`stories-story-map`, `stories-acceptance-tests`, `ddd-model`, `clean-engineering-code`, `ux-mockup`, `bdd-behavior`), in a project with a session open, and again with none open. For each reply I measured:
- its length, tools and result line
- docstring and first-rule counts
- which fidelity's overview, template, Scaffold and sketch template reach it
- placeholders left in it
- the session-log lines and files written straight after `answer`

I compared each measure with round 7's probe output. Probe: `…/scratchpad/r8_ap_expand.py`, output `r8_probe_*.txt`, story-map replies `r8_dump_*.txt`. A second probe asks each writing action at four non-first fidelities and prints the headings that reach the agent: `r8_grill_fid.py`.

**Capture → partition → embed, end to end** (`…/scratchpad/r8_capture_flow.py`). Each step is answered as the MCP host answers it, with the arguments the step before tells the agent to pass. The steps are `capture_from_documents`, `convert`, `partition.partition` (paths = the converted files, out_root = the folder), writing a segment where the partition's reply places it, `partition.segment_files`, and `context_index.embed`. I ran it with a session open and with none, for five `guidance` values: `["stories"]`, `"stories clean-engineering"`, `["ux", "ddd"]`, and the two option words the recipe offers, `["clean_engineering"]` and `["cdd"]`.

What the run showed:
- For real slugs the chain now holds. `segment_files` lists exactly the segment the agent wrote, `embed` indexes 1 segment into `docs/rag`, and the log shows `tool context-setup.capture_from_documents`, `tool context-setup.convert`, `tool partition.partition`, a `partition` line, a `segment_files` line and `tool context-index.embed`.
- For two of the five option words the recipe tells the agent to offer, partition raises (A2).
- With no session open, every action runs and logs in the `main` session, and the reply's Session section names `.sessions/main/session.json`. Round 7's note "with no session, nothing is logged" read the wrong log file. The code behaves as designed: "With no named session the action runs in the main session".

## What reaches the agent (measured, required arguments only)

| Recipe | `stories-story-map` | r7 | `stories-acceptance-tests` | r7 | Session log after `answer` |
|---|---|---|---|---|---|
| `generate` | 21.3 K | 20.4 K | 42.5 K | — | `tool generate.generate`, one `generate` line |
| `sketch` | 33.4 K | 32.5 K | 54.0 K | — | `tool sketch.sketch` only |
| `grill` | 26.0 K | 25.1 K | **26.0 K (story map's text)** | 47.1 K | `tool grill-context.grill` only |
| `iterate` | 26.6 K | 25.7 K | 47.8 K | — | tool line, one `iterate` line |
| `satisfy` | 7.3 K | 6.9 K | 8.3 K | — | tool line, one `satisfy` line |
| `document` | 3.2 K | 3.2 K | — | — | tool line, one `document` line |
| `repair` | 11.8 K | 11.8 K | 25.6 K | — | tool line, one `repair` line |
| `partition` | 3.9 K | 3.8 K | 3.3 K | — | tool line, one `partition` line |
| `validate` | 9.5 K | 9.0 K | 10.7 K | — | tool line, one `validate` line, one report |
| `capture_from_documents` | 2.0 K | 1.8 K | — | — | tool line; tools convert, partition, segment_files, embed |
| `capture_from_live_app` | 4.1 K | 4.1 K | — | — | tool line; text unchanged since round 7 |
| `context_index.ask` | 0.7 K | 0.7 K | — | — | tool line |

The results across the six slugs:
- No recipe raises.
- Every docstring arrives once.
- Sketch, Grill and Iterate log no `generate` line.
- "Partition of  finished" and "failed for  (call" are gone.
- The capture recipe names `paths`, `out_root` and `segment_files`.

Two problems showed up in the measures:
- **Grill at any fidelity but a practice's first** gets the first fidelity's text (A1). With `ddd-model`, `ux-mockup`, `clean-engineering-code` and `stories-acceptance-tests`, the overview, template and first rule of the named fidelity are absent: 0, 0, 0 for each. `stories-acceptance-tests` gets the Story Map template and seven `story-map` rules. Round 7 measured 47.1 K with the named fidelity's overview and first rule.
- **BDD** carries four rules twice in every rules-bearing reply (outside this area; see below).

## Findings, most severe first

| # | file:line | concern | found by | status | fix in one line | severity |
|---|---|---|---|---|---|---|
| A1 | harness/guidance_actions/guidance_actions.py:443-446 (`_inside`), seen through actions/grill_context/grill_context.py:112-115 (`_generate`) | 5 | measured | regression (round 7 measured grill at the named fidelity for six slugs) | `_inside` copies the outer action's `_worked_at` (`inner._worked_at = dict(self._worked_at)`) *before* it evaluates `self.listed()`, which is what fills `_worked_at`. Grill calls nothing that lists before `_generate()`, unlike Iterate and Satisfy, which log first. So the inner Generate gets an empty map and works at the practice's first fidelity: grill at `stories-acceptance-tests` hands the agent the story map's template and rules, and grill at `ddd-model`, `ux-mockup` or `clean-engineering-code` gives that practice's first fidelity. This arrived with 802640f20 (round-7 harness core: "the fidelity a call works at off the shared practice"). Have the inner action ask its held `_outer` for `fidelity_of` instead of copying a map, or list before copying. Add a spec that grills at a non-first fidelity: `fidelity_text_spec.py` runs every action only at `stories-story-map`, the first fidelity, so it cannot see this. Owner: harness core (`_inside`) | high |
| A2 | context_setup/context_setup.py:268, :273 | 2, 10 | AI + measured | new | Step 2 tells the agent to offer the options stories, clean_engineering, ddd, ux and cdd, and Step 3 to pass the selection as `guidance`. `clean_engineering` and `cdd` are not guidance slugs, and partition raises `ValueError: expected <module>:<Class>, got 'clean_engineering'` (and the same for `cdd`). The recipe keeps its own list of practices, under its own names, beside the practice catalogue. Offer the slugs the catalogue lists (or the `partition` skill's guidance list), and drop the made-up `cdd` bundle or name it as the two slugs. The flow spec `capture_documents_flow_spec.py` passes only `["stories"]`, so it never tries an option the recipe offers | medium |
| A3 | context_setup/context_setup.py:231, :239 (`capture_from_live_app` Steps 5-6) | 1 | AI | left (sibling of R1; fix rule 5, "fix every sibling", missed) | The live-app recipe tells the agent to call `context_index.embed(segments_paths=[…overview_path])` with no `out_path`, which `embed` requires, so the MCP call fails schema validation or the agent guesses a folder. It also embeds the extraction overview, though `embed`'s docstring says `segments_paths` are "the *-segment.md files partition wrote". R1 fixed the same hand-over in `capture_from_documents` only. Name `out_path` (for example `{capture_repo}/rag`), and say in `embed` that it reads any markdown file, or partition the overview first | medium |
| A4 | actions/render/render.py:35-38 | 5 | AI | new | `each` hands `on` the fidelity this action works at. `on` turns it back into its practice (`practice_of`), then hands the same fidelity back in as a parameter: `practice.render_files(…, fidelity=self.fidelity_of(item))` and `practice.render_at(self.fidelity_of(item), …)`. The fidelity knows its practice, so it could answer render itself. The two practice methods also take the fidelity in different places (first positional, last keyword). Give `FidelityGuidance` `render`/`render_files` that use its practice, and have Render call `item.render…`. Owner: harness/guidance for the method, this area for the caller | medium |
| A5 | actions/grill_context/grill_context.py:136 | 11 | measured | left (R4, part; fix rule 5 missed) | R4 fixed the blank-argument lines in Partition and Improvement, but "Grilling session for: " still reaches the agent blank in the grill, iterate and sketch replies when no plan or paths are sent (`r8_dump_GrillContext.grill…:29`, `Iterate…:31`, `Sketch…:193`). Leave the clause out when the source is empty, as `Partition._corpus` does | low |
| A6 | actions/document/document.py:21 | 10 | AI | left (R5, part; fix rule 5 missed) | R5 fixed Partition's "session path" wording. Document's docstring still says "write the observed state under the session path", while its own result line, in the same reply, says "under the session's root". Use "the session's root" | low |
| L7 | .context/repo-model.md:2737 | 11 | AI | decided | `partition/.context/cdr/0001-repository-model-lists-partition-as-it-was-read.md`: the model is one reading of the whole repository at one commit, which fix agents may not edit; the lead drops `partition_corpus` and adds `segment_files` at the next reading. Agreed | — |
| M4 | validate/checked_graph.py:62-68 | 5 | AI | decided | `0001-violations-read-by-practice-key.md` (updated round 7). Agreed | — |
| M5 | generate/generate.py:52-62 | 2, 5 | AI | decided | `0001-formats-compared-through-format.md`, wording now current. Agreed | — |
| N10 (part) | validate/checked_graph.py:98-111 | 1, 9 | AI | decided | Named graph files are read through `SavedGraph.from_file` in harness/graph. Agreed | — |
| M10 | lern_domain_driven/practices/stories/model/claude_design/fixtures.py:23 | 3 | AI | decided | `0001-canvas-fixtures-built-in-the-chat.md`. Agreed | — |
| L8 | builders/create_agent_toolset, builders/create_practice_guidance, patterns/mern_domain_driven, patterns/cdd_claude_mod | 8 | AI | decided | One-class packages kept because the installer finds one folder per skill (round 5) | — |

## Fixed since round 7

- **R1.** Step 3 passes `paths = the markdown_files convert returned` and `out_root = {folder_path}`. Step 4 calls the new `partition.segment_files`, which lists `Segment.files_under(folder)`, and `Segment` now owns the segment place (`SEGMENT_FILE`). The partition's `segment` line names that same place. I followed the chain end to end with real slugs and it found the segment the agent wrote. Spec: `capture_documents_flow_spec.py`, answered through `toolset.tools[name].answer(ToolCall)`, the live path.
- **R2.** "call it with no guidance" is gone. The recipe now says to ask once more, then stop and say nothing was indexed.
- **R3.** `FidelityProgress._written_by_generate` is deleted. The board counts every `generate` line and points to `GuidanceAction.log_running`, the one owner of the rule.
- **R4 (Partition, Improvement).** "Partition finished", "Index the corpus the user names (ask which files or folder…)" and "failed (call the diagnose tool" no longer leave a blank. The sibling in Grill is still blank (A5).
- **R5.** The Generate record names `current.format.name`. The partition docstring and `partition.md` say "the session's root". The sibling in Document still says "session path" (A6).
- **L5.** `graph_json_reader.py` is deleted. `SavedGraph.from_file`, `from_nodes` and `from_violations`, and `Violation.by_rule`, in harness/graph, read every graph file. `space/kanban/report.py` imports `SavedGraph`, not an action module. Spec: `checked_graph_spec.py`.

## Did the fix agents follow the round-7 fix rules?

- **Specs take the live path.**
  - Yes for the capture chain: each step is answered as the MCP host answers it.
  - Partly elsewhere. `fidelity_text_spec.py` answers every action through `answer`, but only at `stories-story-map`, which is a practice's first fidelity. It therefore cannot catch an action that ignores the named fidelity, and A1 got through.
  - The flow spec sends only `["stories"]`, never the option words the recipe offers (A2).
  - Graph reading through the worker: missed for Stories' `StoryLinks` (the crash above).
- **Every sibling fixed.**
  - R1's fix reached `capture_from_documents` but not `capture_from_live_app` (A3).
  - R4's fix reached Partition and Improvement but not Grill (A5).
  - R5's fix reached Partition but not Document (A6).
  - The DDD graph-reader fix did not reach Stories (outside this area).
- **One owner per finding.**
  - Yes for R3: the board's twin is deleted.
  - Yes for L5: one reader, in harness/graph.
- **Decision records.**
  - L7 now has a record, and I agree with it.
  - The validate and generate records were brought up to date.

## Outside this area (not counted)

- **High, practices (Stories):** the graph worker crash above, at `practices/stories/model/graph_reading.py:147`. `StoryLinks._step_body` reads `step.body` from graph `Node`s, so every graph-backed validate whose paths hold story steps fails, including every graph check of this area. Fix rules 4 and 5 were missed: this is the sibling of the round-7 DDD reader.
- **Low, practices (BDD):** four BDD rules reach the agent twice, with two different texts, in every rules-bearing reply at `bdd-behavior`:
  - `shared-describe-subject`, `state-not-when`, `nest-by-enabling-events` and `context-setup-expresses-state`
  - for example `practices/bdd/bdd.md:115` and `:159` both define `state-not-when`
  - round 7's probe shows the same (its first-rule count was 2 at `bdd-behavior`), but round 7 did not report it
- **Low, harness core:** the static result line that `AgentInstructions.expand` builds (`harness/agent_tools/recipe.py:184-200`, `text_of`) garbles a nested f-string or a local name. It writes "Partitionf' of {source}' if source else '' finished", "failed{{under_repair}}" and "Validation report … self._reports.where()". `practices/agent_bdd/agent_bdd_common.py:599` reads that line as the recipe's result.
- **Low, harness core:** an unknown slug in a guidance list raises "expected <module>:<Class>, got 'clean_engineering'" (from the `ToolsetReference` path in `GuidanceArgument`), which tells the agent the wrong remedy. It should say that no practice or fidelity has that slug, and list the ones that do.
- **Generated, not counted:** the installed `actions-partition` skill and the MCP tool description still say "Omit it to use the session path". `.claude/` needs a reinstall.

## Counts

- **By concern** (a row counts once per concern; 6 counted rows; decided rows not counted):
  - 1: 1 (A3)
  - 2: 1 (A2)
  - 5: 2 (A1, A4)
  - 10: 2 (A2, A6)
  - 11: 1 (A5)
  - 3, 4, 6, 7, 8, 9, 12: 0
- **By severity:**
  - high 1 (A1)
  - medium 3 (A2, A3, A4)
  - low 2 (A5, A6)
- **By status:**
  - fixed: 6 (R1, R2, R3, R4, R5, L5)
  - left: 3 (A3, A5, A6), each a sibling a round-7 fix missed
  - regression: 1 (A1, against round 7)
  - new: 2 (A2, A4)
  - new scope: 0
  - decided: 6 (L7, M4, M5, M10, N10 part, L8)

## Goal-class counts

| goal class | new | new scope | left | regression | total |
|---|---|---|---|---|---|
| Bad resource orientation (5, 9) | 1 (A4) | 0 | 0 | 1 (A1) | 2 |
| Shadow models (2) | 1 (A2) | 0 | 0 | 0 | 1 |
| Duplicated functions (1, 12) | 0 | 0 | 1 (A3) | 0 | 1 |
| **Total** | 2 | 0 | 1 | 1 | 4 |

Round 6 had 14 goal-class findings here, round 7 had 2, and round 8 has 4. Both round-7 goal findings (R1, R3) are fixed. The four now are:
- **A1** is the one high. It is a regression caused by a fix in another area (harness core), and seen here.
- **A3** is R1's sibling.
- **A2 and A4** sit in code that round 7 read but did not flag.

As in round 7, these come from the AI check alone. The graph check has never run on this area, so near-copy duplication, hide-inner-details and the cycle rules may add findings.

## What would make the next round cheaper

1. **Specs at more than the first fidelity.** Every action spec in this area runs at `stories-story-map`. A fidelity-handling change in harness core (A1) broke grill for every other fidelity, and nothing failed. Run `fidelity_text_spec.py` over at least one non-first fidelity, `stories-acceptance-tests` for example, and check that the named fidelity's template heading reaches the reply. Do the same for the capture flow: run every option word the recipe offers through partition (A2).
2. **When a finding is fixed, grep for the same hand-over everywhere first.** All three left items are siblings of round-7 fixes:
   - The live-app recipe also calls `embed` (A3). `grep "context_index.embed("` finds it.
   - Grill also builds a line from `source_label` (A5). `grep "source_label("` finds it.
   - Document also says "session path" (A6). `grep "session path"` finds it.
   The fix brief's rule 5 says this; the fix agent's report should list the grep and its hits.
3. **(For the lead) smoke-test the graph check on the pattern folders.** The round-7 smoke check covered `ddd` and `space/session`, which hold no story steps, so the Stories crash only appeared on this area's templates. One `validate` with `graph: true` over `cdd_guidance/patterns` before the round would have shown it.

## Scanner false positives

None judged: the graph check did not run (see "How each check ran"). The crash is not a scanner false positive. It is a reader (`practices/stories/model/graph_reading.py:147`) that fails before any scanner runs.
