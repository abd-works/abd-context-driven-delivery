# Round 7: actions, patterns, builders, agents, context setup, sketch document, judged across files

Area: `cdd_guidance/actions`, `cdd_guidance/patterns`, `cdd_guidance/builders`, `cdd_guidance/agents`, `cdd_guidance/context_setup` and `cdd_guidance/practices/sketch_document` (not `_examples`). Branch `ensure-domain-orientation-refactor` at c8921451, read on 2026-11-08. `practices/sketch_document` is new this round: the round-6 fixes moved `SketchOutline` and `DiscoveryDocument` there from `actions/sketch` (N3).

## How each check ran

**Graph rules: failed, not run.** `cdd.ping` answered `pong`. One `validate.validate` call was made: `clean-engineering-modules`, `graph: true`, `paths` set to the six area folders (absolute, forward slashes). It answered "still running" three times, as the brief says it may, then failed:

```
RecipeLineFailed: Validate.validate recipe line ...\cdd_guidance\actions\validate\validate.py:57
`graph_paths = self._graph.check_beside(self._reports)` failed: GraphBuildFailed: the graph build's worker process exited with 1:
  ...harness\graph\graph.py, line 1469, in _read_working_copy  practice.read_working_copy()
  ...cdd_guidance\practices\ddd\ddd.py, line 81, in read_working_copy  DddReading(self).read()
  ...cdd_guidance\practices\ddd\model\graph_reading.py, line 203, in _members_by_folder  kind = tactical.inferred_kind(names)
  ...cdd_guidance\practices\ddd\model\stereotypes.py, line 98, in kind  return kind_named_by(self.oclass.stereotypes)
AttributeError: 'Node' object has no attribute 'stereotypes'
```

The cause is in the practices area, not this one. `DddReading._members_by_folder` (`practices/ddd/model/graph_reading.py:195-200`) wraps every node `clean.in_graph.nodes("OoadClass")` returns in a `TacticalClass`, and `TacticalClass.kind` (`practices/ddd/model/stereotypes.py:98`) reads `self.oclass.stereotypes`. In the worker process those are graph `Node` objects (`harness/graph/graph.py:792`), which have no `stereotypes`. The code arrived with f02b6485 ("DDD reads a class model through the practice it extends"). Every graph build that reads Clean Engineering classes alongside DDD fails, so **no graph-backed validate can run at this commit, in any area.** Following `.claude/rules/mcp-fail-loud.md` and the brief, I made no further graph calls and did not run validate through Python. Owner: practices (DDD). It needs a fix and a spec that builds a graph in the worker process, and then this area's graph check has to run again.

**AI judgment: run, and checked by running the code.** I answered every `@agent_instructions` recipe of the eleven actions, `ContextSetup` and `ContextIndex` the way the MCP host does: `toolset.instruction(name).answer(ToolCall(arguments, project))`. That is `AgentInstructions.answer` → `log_session_invocation` → `_expanded_reply` (`harness/agent_tools/agent_tools.py:1051-1071`). The project was a throwaway one with an open session, and each call carried **only the arguments the recipe's parameter schema marks required**. Each recipe ran for `stories-story-map`, `stories-acceptance-tests`, `ddd-model`, `clean-engineering-code`, `ux-mockup` and `bdd-behavior`. The eight writing recipes ran again with no session. For each reply I measured:
- its length, the tools it lists and its result line
- how often the docstring and the first rule appear in it
- whether the fidelity's overview, template, Scaffold and sketch template, the grill interview and the fixes step reach it
- every placeholder left in it
- the session-log lines and files the call wrote, read straight after `answer` and before anything else runs

Probe: `C:/Users/jeffa/AppData/Local/Temp/claude/C--Users-jeffa--claude-spares-spare-GRHl26/1da33504-c4b4-4a29-9c7f-0741c828af02/scratchpad/r7_ap_expand.py`. The output is in `r7_probe_*.txt` beside it, and the story-map replies are dumped there as `r7_dump_*.txt`.

**Rule-versus-schema gaps (round-7 specifics).** No practice lives in this area, but three patterns add graph rules to DDD, BDD and Stories. I compared each rule scanner's `node_types` with the type it is listed on in the pattern's `rules.yaml`:
- `lern_domain_driven`: BDD 4 rules, DDD 5 rules, Stories 4 rules
- `cdd_web_domain_access`: DDD 4 rules

Every scanner's types match its listing, so there is **no gap**. Stories' `share`, `domain`, `server` and `playwright` keys reach `StoryShared`, `DomainSpec`, `ServerSpec` and `PlaywrightSpec` through `_NODE_TYPES` in `harness/graph/schema_edges.py:46-60`. That table is the framework holding one pattern's node names (also `node` → `NodeRoot`, `client` → `ClientRoot`); see "Outside this area" below.

## What reaches the agent (measured, required arguments only)

| Recipe | Required args | `stories-story-map` reply | Largest of the six slugs | Tools listed | Session log after `answer` |
|---|---|---|---|---|---|
| `generate` | guidance | 20.4 K | 68.9 K (`ddd-model`) | render, validate | `tool generate.generate`, one `generate` line |
| `sketch` | guidance | 32.5 K | 85.9 K (`ddd-model`) | explore_context_files, read_context_file, write_grill_answer, find_template, save_sketch, review_sketch, render, validate | `tool sketch.sketch` only |
| `grill` | guidance | 25.1 K | 73.5 K | grill tools, render, validate | `tool grill-context.grill` only |
| `iterate` | guidance | 25.7 K | 74.1 K | grill tools, render, validate, mark_iterate_round | `tool iterate.iterate`, one `iterate` line |
| `satisfy` | guidance | 6.9 K | 12.4 K | validate | `tool satisfy.satisfy`, one `satisfy` line |
| `document` | guidance, paths | 3.2 K | — | refresh | tool line, one `document` line |
| `repair` | guidance | 11.8 K | 25.7 K | refresh, diagnose | tool line, one `repair` line |
| `partition` | guidance | 3.8 K | — | refresh | tool line, one `partition` line |
| `validate` | guidance | 9.0 K | 14.6 K | — | tool line, one `validate` line, one report |
| `create_rule` | guidance | 5.2 K | — | — | one `create_rule` line (no tool line: not on MCP) |
| `capture_from_documents` | folder_path | 1.8 K | — | convert, partition, embed | tool line |
| `capture_from_live_app` | repo_path | 4.1 K | — | smoke_test, scout_app, complete_capture, embed | tool line |
| `context_index.ask` | question, index_path | 0.7 K | — | search | tool line |

The results across all six slugs and the no-session runs:
- No recipe raises, with any slug or with no session.
- Every docstring arrives once.
- The first rule arrives once in every rules-bearing reply.
- Sketch, Grill and Iterate log no `generate` line.
- Satisfy saves no report.
- `ask` names its question and index.
- The only single-brace placeholders left are path templates the reply asks the agent to fill (`{epic}`, `{story_snake}`, `{artifact}`, `{Actor}`).
- With no session, nothing is logged and no file is written.

(A first version of the probe also called `expand` after `answer`. That runs the recipe a second time, so it logged each action twice and saved two validate reports. This is the probe's doing, not the code's: `answer` alone logs once.)

## Findings, most severe first

| # | file:line | concern | found by | status | fix in one line | severity |
|---|---|---|---|---|---|---|
| R1 | context_setup/context_setup.py:271-284 (`capture_from_documents` Steps 3-4) with actions/partition/partition.py:72-79 and partition.md:16, :70 | 1 | AI + measured | new | The recipe restates where Partition writes segments, and gets it wrong. Step 4 embeds `glob(folder_path/.context/**/*-segment.md)`, but Partition writes segments under `{out_root}/{artifact}/.context/` (its own `segment` line and partition.md), so the glob finds none of them. `embed` then builds an empty index with no error. Step 3 also never passes `paths` (the converted `folder_path/markdown/`) to `partition`, so the agent is told "Index the corpus at  under …" with a blank corpus. Step 3 contradicts itself too: "call ONLY the tools … start with `first` … then the rest" against "call partition.partition once". Have Step 3 pass `paths=folder_path/markdown` and `out_root`, and have Step 4 embed the segment files the partition reports, not a glob restated here | medium |
| R2 | context_setup/context_setup.py:278-279 | 11 | AI | left (N1, part) | "If the user selected nothing, call it with no guidance" is still in the recipe, though `guidance` is a required parameter of `partition.partition`, so that MCP call fails schema validation. Say what to do when nothing is selected (ask again, or stop) | medium |
| R3 | harness/guidance_actions/guidance_actions.py:487-495 (`log_running` skips `_outer`) and space/kanban/ticket.py:498-510 (`_written_by_generate`) | 1 | AI | new | Round-6 N2 was fixed twice, by two agents. The action now logs nothing when started `_inside` another, and the board separately drops any `generate` line written during another tool's call. One rule, "only the generate tool's own generate counts as generate done", now has two owners, and they can drift. Keep the rule where the line is written (`log_running`, which has the spec in `fidelity_text_spec.py:179-221`) and delete the board's filter, or record why the board must also read older logs | medium |
| R4 | partition/partition.py:106-108, :71 (blank `source`); improvement/improvement.py:24, :41-46 (blank `asset`) | 11 | measured | new | Now that a left-out optional argument takes its default (the N1 fix), the lines built around it reach the agent blank: "Partition of  finished", "Index the corpus at  under …", "Diagnose why … failed for  (call the diagnose tool". When the argument is empty, leave the clause out (or ask for the file), so the agent is not told to work on nothing | low |
| R5 | actions/generate/.context/cdr/0001-formats-compared-through-format.md:7, :16; partition/partition.py:103 | 11 | AI | new | The Generate record says `_earlier_render` reads the fidelity's format through `Format(label).name`. Since f02b6485 it reads the held `current.format.name`, and only the declared outputs are still labels, so the record's Consequences are half met. The partition docstring says omitting `out_root` uses "the session path", while `_folder` and the reply use the session's root (the project). Update both texts | low |
| L5 | validate/graph_json_reader.py:14-47 (5 free functions); space/kanban/report.py:11 imports two of them | 8, 6 | AI | left | The pattern helpers are folded onto `AccessFile` and `LernDomainDriven` (fixed). The violation reader stays as free functions. The validate record (`0001-violations-read-by-practice-key.md`) says this reading "belongs with the graph's *Violation* in `harness/graph`" and leaves it there only because another owner holds that module. That defers the work; it does not decide it. Meanwhile the CDD Kanban imports an action's internal module to read node lists. Move them to `Violation` / `SavedGraph` in harness/graph | low |
| L7 | .context/repo-model.md:2737 | 11 | AI | left | The repository model still lists `Partition.partition_corpus`, with no record | low |
| M4 | validate/checked_graph.py:58-67 | 5 | AI | decided | `0001-violations-read-by-practice-key.md`: a violation's practice key is that practice's identity in the graph file, so comparing keys looks nothing up by name. Agreed | — |
| M5 | generate/generate.py:58-62 | 2, 5 | AI | decided | `0001-formats-compared-through-format.md`: the declared outputs are labels owned by `FidelityGuidance` (harness/guidance), and converting them in Generate would add a second model of a fidelity's formats. Agreed (its wording is stale, R5) | — |
| N10 (part) | validate/graph_json_reader.py:14-22 | 1, 9 | AI | decided | The saved-graph path half is fixed (`CheckedGraph._session_saved` reads `session.graph.saved_file`). Reading a graph file the call names stays in `graph_json_reader`, which uses `SavedGraph.from_document`, per the same record. Agreed | — |
| M10 | lern_domain_driven/practices/stories/model/claude_design/fixtures.py:23 | 3 | AI | decided | `0001-canvas-fixtures-built-in-the-chat.md`: the bundle is built with the user's Node in the chat, far over the 10-second action limit, and the canvas step names it. Agreed | — |
| L8 | builders/create_agent_toolset, builders/create_practice_guidance, patterns/mern_domain_driven, patterns/cdd_claude_mod | 8 | AI | decided | One-class packages kept because the installer finds one folder per skill (round 5) | — |

## Fixed since round 6

- **N1.** A left-out optional argument now takes the parameter's default (`ParameterSchema.with_defaults`, used by `expand` and `RecipeExpansion`). `partition` without `mode` and `repair` without `asset` answer for all six slugs. Spec: `harness/agent_tools/agent_tools_spec.py:291` ("a call sends only its required arguments").
- **N2.** Sketch, Grill and Iterate log no `generate` line; measured for six slugs. Spec: `fidelity_text_spec.py:179-221` reads the session log after `answer`. (Fixed twice: R3.)
- **N3.** `SketchOutline` and `DiscoveryDocument` moved to `cdd_guidance/practices/sketch_document`, which imports only `harness/guidance`. No practice production file imports `cdd_guidance.actions`. `python -X importtime -c "import cdd_guidance.practices.sketch_document.sketch_outline"` loads no `cdd_guidance.actions` module.
- **N4.** `ContextIndex.for_call` holds the call's session and reads every path through `session.path_named`. `ContextSetup.for_call` makes it. A missing segment raises `SegmentNotFound`. Spec: `context_index_spec.py`.
- **N5.** Each docstring arrives once in every reply.
- **N6, N7, N8, N17.** The Discoverer, Specification and Implementation agents name the `actions-sketch`, `actions-generate` and `actions-satisfy` skills. `sketcher.md` and `dont use yet/` are deleted. The Context agent names its skills and points to the capture recipes instead of restating them.
- **N9, L3.** `repair.md` names only the session log, `diagnose`, `verify_fix` and `repo.push_commit`. Spec: `improvement_spec.py` "should name no step that nothing defines".
- **N10 (path).** `.context/graph.json` is built in one place, `Graph.saved_file`.
- **N11.** `DiscoveryDocument` reads its title and sources from `SketchOutline`, so one rule finds the header and the practice sections. Its twin reader is gone.
- **N12.** Partition asks for one index and one segment set per call; the `on` / `_corpus_steps` hand-down is gone. Spec: "a partition of one corpus for two practices".
- **N13.** The Toast on the inherited `begin` covers every action's tools, and the prompt-notify card says so. Spec: `action_toast_spec.py`.
- **N14.** The sketch reply carries each rule once. Spec checks the count.
- **N15.** The document result line names "the session section", with no literal `{session.path}`.
- **N16.** Sketch's docstring, `sketch.md` and `generate.md` no longer name `sketch_session` or `finish_turn`. Both `log-action-requests.txt` files are deleted.
- **N18.** Generate imports `Render` at the top.
- **L1.** `ask` fills `{{question}}` and `{{index_path}}`. Spec: "should leave no placeholder for the agent to read literally".
- **L5 (part).** `access_facts` helpers and `test_setup_text` are on `AccessFile` and `LernDomainDriven`.

## Did the fix agents follow the round-6 fix rules?

- **Spec on each concern-5 effect:**
  - N1: yes (harness spec).
  - N2: yes (log read after `answer`).
  - N4: yes (paths read from the project, missing segment refused).
  - N12: yes.
- **One owner of a duplicated job, twins gone:**
  - N11: yes.
  - N10: yes, for the path.
  - N2: **no.** The rule now lives in the action and on the board (R3); the "one owner" rule was missed.
- **A decision record for each skip:**
  - M4, M5, M10 and part of N10: yes.
  - L5 (the violation reader): the record defers to another owner instead of deciding, so it stays left.
  - L7: no record and no change.

## Outside this area (not counted)

- **High, practices (DDD):** the graph worker crash above. `TacticalClass` reads `stereotypes` from graph `Node`s, so every graph-backed validate fails at c8921451.
- **Low, harness core:** `harness/graph/schema_edges.py:46-60` holds the LERN pattern's schema key names (`share`, `server`, `domain`, `playwright`, `node`, `client`). The pattern's `schema.yaml` should name its node types, or register them, rather than the framework knowing them.

## Counts

- **By concern** (a row counts once per concern; 7 counted rows, decided rows not counted):
  - 1: 2 (R1, R3)
  - 6: 1 (L5)
  - 8: 1 (L5)
  - 11: 4 (R2, R4, R5, L7)
  - 2, 3, 4, 5, 7, 9, 10, 12: 0
- **By severity:** high 0; medium 3 (R1, R2, R3); low 4 (R4, R5, L5, L7). The one high this round sits outside the area: the DDD graph crash.
- **By status:**
  - fixed: 20 (N1-N9, N11-N18, L1, L3, and N10's path)
  - left: 3 (R2, L5, L7)
  - new: 4 (R1, R3, R4, R5)
  - new scope: 0
  - regression: 0
  - decided: 5 (M4, M5, M10, N10 part, L8)

## Goal-class counts

| goal class | new | new scope | left | regression | total |
|---|---|---|---|---|---|
| Bad resource orientation (5, 9) | 0 | 0 | 0 | 0 | 0 |
| Shadow models (2) | 0 | 0 | 0 | 0 | 0 |
| Duplicated functions (1, 12) | 2 (R1, R3) | 0 | 0 | 0 | 2 |
| **Total** | 2 | 0 | 0 | 0 | 2 |

Round 6 had 14 goal-class counts in this area (concern 5: 6, concern 9: 2, concern 2: 1, concern 1: 5); round 7 has 2. Every round-6 concern-5 and concern-9 finding is fixed or decided by a record I agree with (M4, M5, N10). Both remaining findings are duplicated knowledge across two owners:
- R3 came from two agents fixing one finding.
- R1 is a recipe restating another action's output location.

These counts come from the AI check alone, because the graph check could not run. The graph rules (near-copy duplication, hide-inner-details, cycles) may add rows once the DDD crash is fixed.

## What would make the next round cheaper

1. **One fix agent per finding, even when the finding spans two areas.** N2 was fixed in the action (`log_running`) by the actions agent and on the CDD Kanban (`_written_by_generate`) by the space agent, so it now has two owners (R3). The lead's brief should name the one module that owns each cross-area fix, and the other agent should only check it.
2. **Follow a recipe chain end to end in one spec.** `capture_from_documents` hands work to `partition` and then to `embed`. Each recipe is now right on its own, but the folder Partition writes and the folder Step 4 globs disagree (R1). A spec that answers each step with the arguments the step before says to pass, then checks that the next step's input paths are the previous step's output paths, would have caught it. The same spec should check that the blank-argument lines (R4) never reach the agent.
3. **(For the lead) a graph smoke test before the round.** One `validate` with `graph: true` on a small code folder, after the last merge, would have shown the DDD crash before six validators met it.

## Scanner false positives

None judged: the graph check did not run (see "How each check ran"). The crash is not a scanner false positive. It is a reader (`practices/ddd/model/graph_reading.py:195-200`, `stereotypes.py:98`) that fails before any scanner runs.
