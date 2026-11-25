# Round 8: harness-upper, after the round-7 fixes

Area: `harness/hooks`, `harness/mcp`, `harness/graph` (with its TypeScript app), `harness/diagnostics`, `harness/chat`, `harness/catalog_generator`, `harness/design_canvas`, and the TypeScript plugin `harness/chat-ui`. Code read at 4359b907 on `ensure-domain-orientation-refactor`. The CDD MCP host (pid 43352, `~/.cdd/runtime`, pinned to 2c30c2f7) served the same tree: `git diff 2c30c2f7 4359b907` is empty.

Checks run:

- **Graph rules:** one validate, `clean-engineering-code` with `graph: true` and the eight area folders as `paths`, started 11:39:36 local. The build ran in a worker process and the call answered "still running" eleven times. At about 11:47 it **failed**: `RecipeLineFailed` at `cdd_guidance/actions/validate/validate.py:57` (`self._graph.check_beside(self._reports)`), from `GraphBuildFailed: the graph build's worker process exited with 1`, ending in `AttributeError: 'Node' object has no attribute 'body'` at `cdd_guidance/practices/stories/model/graph_reading.py:147` (`StoryLinks._step_body`), reached from `Graph._read_working_copy` → `Stories.link_to_other_practices` (stories.py:129). `~/.cdd/server.log` holds this traceback 8 times (each failure logs it twice), so other validators hit it in the same window. Under `.claude/rules/mcp-fail-loud.md` no second graph validate was made. **This round again has no graph hits for this area.** The failure is R8-H1.
- **B10, measured directly:** while that validate ran, a loop started a `curl` to `http://127.0.0.1:47800/ping` every 2 seconds, from 11:39:35 to 11:47:08 (221 pings, 30 s timeout). Results under B10 below.
- **AI across files:** every finding in `round7-harness-upper.md` was checked against the code, with the decision records the fix agents wrote or changed in round 7 (`harness/graph/.context/cdr/0001`, `harness/catalog_generator/.context/cdr/0001`, `harness/chat-ui/.context/cdr/0002`). The round-7 fix code (c07e1a21, c0ab26cc, and the harness-core and space/tools/actions commits that touched this area: 802640f2, 1103aa1c, 82acd29e) was read beside the files it imports and the files that import it, including `cdd_guidance/practices/{ddd,stories,bdd}/model/graph_reading.py`, `cdd_guidance/actions/validate/checked_graph.py`, `space/kanban/board_app.py`, `space/kanban/report.py`, and `harness/markdown/format.py`.

Status words: **fixed**, **left**, **regression**, **new**, **new scope**, **decided**.

## B10: pings during one graph validate

| measure | round 6 | round 7 | round 8 |
|---|---|---|---|
| pings | 60 | 129 | 221 (one every 2 s, 7 min 33 s) |
| timed out or refused | 29 | 0 (30 s timeout) | **0** (30 s timeout) |
| slowest ping | over 10 s | 8.84 s | **12.26 s** (11:43:32), next 11.46 s, 10.77 s, 9.42 s |
| median | not recorded | 1.17 s | **4.06 s** |
| 90th percentile | not recorded | not recorded | 7.73 s |
| over 2 s | not recorded | 55 of 129 (43%) | **158 of 221 (71%)**; 3 over 10 s |
| ping just before the validate | about 0.1 s | 0.002 s | 4.80 s (other validators' builds already running) |

**B10 is worse than in round 7.** The server never refused a connection, but its event loop stopped answering for 4 s at the median and up to 12 s. Other validators were building in the same window (the ping before mine took 4.8 s), as in rounds 6 and 7, so this measures the live case: several validates refreshing one shared session graph. Round 7's fix serialises the server's part of each build behind `_SERVER_TURN` (graph_build.py:34), which stops two builds' server work from overlapping but does not shrink it: `Graph._order` still writes the whole held graph into each order (`SavedGraph.from_graph(self)`, graph.py:1465), `WorkerBuild.carry_out` still restores the worker's whole answer with `_hold`, and `Graph.refreshed` serialises the refreshed files again in the server (graph.py `refreshed`). Every validate in the session shares one `Graph` (`checked_graph.py:121`, "The session's graph holds every practice"), so each refresh carries every practice any validator loaded, and grows as they load more. See R8-M1.

## Findings, most severe first

### High

| # | file:line | concern | found by | status | finding | fix (one line) |
|---|---|---|---|---|---|---|
| R8-H1 | cdd_guidance/practices/stories/model/graph_reading.py:107-147 (`StoryLinks.link`, `_step_body`); harness/graph/graph.py:797 (`nodes_read_now`), graph.py `_hold` | 2 | both (the graph validate failed; AI traced it) | left (R7-H1, partly; the DDD half is fixed) | **A graph validate on this area still fails, from the same split object model in a sibling reader.** Round 7 fixed DDD's reading: it now takes `clean.in_graph.nodes_read_now("OoadClass")` (ddd graph_reading.py:188). Stories' linking was not changed. On a refresh in a worker, every Stories step not in the refreshed files is a plain restored `Node`, and `StoryLinks.link` walks every step (`self.stories.in_graph.nodes()`, :108) and asks each for `step.body.text` (:147), which a plain `Node` lacks. A Clean Engineering validate of harness folders reaches Stories at all only because the session's one graph holds every practice another validator loaded, so whether a validate fails depends on what other chats loaded before it. `graph_build_spec.py:134-175` checks a worker refresh of Clean Engineering + DDD only; no spec refreshes Stories (or BDD) beside Clean Engineering in a worker, and the brief's smoke check (`ddd`, `space/session`) did not load Stories. Rules missed: **each fix applied to every sibling reader**, and **specs take the live path**. Owner: the fix needs both `harness/graph` (what a restored node is) and the Stories reading. | Have `link_to_other_practices` link only `nodes_read_now` for the practice's own nodes, as DDD does, or give a restored node the facts a linker reads (`body` as a fact). Add Stories + Clean Engineering and BDD + Clean Engineering to the worker-refresh spec matrix, run on a graph that already holds every practice. |

### Medium

| # | file:line | concern | found by | status | finding | fix (one line) |
|---|---|---|---|---|---|---|
| R8-M1 | harness/graph/graph.py:1455-1466 (`_build`, `_order`), harness/graph/graph_build.py:34, :492-500, cdd_guidance/actions/validate/checked_graph.py:121 | behaviour (no concern number) | AI, measured live this round | left (R7-M1) | Measured above: median ping 4.06 s, slowest 12.26 s, 71% over 2 s, worse than round 7. `_SERVER_TURN` makes builds take turns at the server's part of the work, but each turn still serialises the whole shared session graph into the order and restores the whole answer. `graph_build_heavy_spec.py` now runs five builds at once on `cdd_guidance/practices` and passes its two-second bar, because each is a full load into an empty graph on a project of its own. The live case, refreshes of one session graph that already holds every practice, is not in it. Rule missed: **specs take the live path**. | Send the worker only the scope and the roots and have it read the held state from the saved graph, answer only the refreshed files' nodes, and make the heavy spec run several refreshes on one session graph that holds every practice. |

### Low

| # | file:line | concern | found by | status | finding | fix (one line) |
|---|---|---|---|---|---|---|
| R8-L1 | harness/catalog_generator/catalog_examples.py:24-26, :197; harness/catalog_generator/catalog_generator.py:170-175 | 1 | AI | left (R7-M5, partly) | `_SUFFIX_ORDER` and `_MONACO_LANGUAGES` are gone: the catalog orders files by `Format.file_order` and names an example's language through its practice's formats. The same file still decides which format a file is by tables of its own (`_MARKDOWN_SUFFIXES`, `_HTML_SUFFIXES`, `_DRAWIO_SUFFIXES`, used in `panel_html`, `stage_page_html`, `_figure_inner`), labels a code figure by its raw suffix (`self.suffix.lstrip(".")`, :197, so `py` where the panel says `python`), and `FidelityTemplate.language` names a template's language by `Format.from_extension` while examples use the practices' format adapters. Rule missed: **each fix applied to every sibling table**. | Ask `Format` (or the practice's formats) for every file kind the catalog shows, and label the code figure with `_language`. |
| R8-L2 | harness/graph/app/app.test.tsx:1015-1036 (`choicesFor`) | 12 | AI | left (R7-M3, spec half) | The explorer now asks `graph.filter_choices` for every change and its merge functions are gone (fixed in production). Its vitest stands in for Python with a TypeScript copy of `Filter.change_practices`: which node types stay chosen when practices change. A change to the Python rule leaves the explorer's tests passing against the old rule. `app_smoke_spec.py:114` covers the Python side. Rule missed: **specs take the live path**. | Have the explorer test read its choices from fixtures Python wrote (as the inventory fixture is), or drive one case through the live `graph.filter_choices`. |
| R8-L3 | harness/graph/saved_graph.py:181-195, :271-282 | 1 | AI | new (code added by the round-7 space/tools/actions fix, 1103aa1c) | Three parsers of the one saved-graph document: `SavedGraph.from_text` (empty text is an empty graph), `SavedGraph.from_file` (repeats the empty-text case, also takes a node list, raises `SavedGraphOutdated`), and `SavedGraphFile.read` (parses again, rejects a list, swallows an outdated shape). | `from_file` calls `from_text` for a document, and `SavedGraphFile.read` calls `from_file` and catches `SavedGraphOutdated`. |
| R8-L4 | space/kanban/board_app.py:8-16, harness/graph/graph_app.py:8-18, harness/diagnostics/server_health.py:16, :30-45 | 1 | AI | new (made by the round-7 R7-L2 fix, c0ab26cc) | `BoardAppPorts` is a near copy of `GraphAppPorts`: each reads one `ports.json` beside its server into tuples. `ServerHealth` then gets the two apps' ports two ways: the graph's as a default argument read at import, the board's through the class-level registration `reports_kanban_app_on`. | One ports-file class that both apps use, and have both apps register their ports with `ServerHealth` the same way. |

Concerns 3, 4, 5, 6, 7, 8, 9, 10, 11: none found this round. Nothing in the area's Python imports `space/`, `tools/` or `cdd_guidance/`; `harness/graph` still imports `harness/mcp` (`long_call`, `mcp`), which is downward.

## Fixed since round 7

- **R7-H1, DDD half:** DDD builds blocks from `nodes_read_now("OoadClass")` and keeps the blocks it built before; `graph_build_spec.py` refreshes a scoped Clean Engineering + DDD graph in a worker and in a reopened graph. The Stories half is R8-H1.
- **R7-M2:** the ambient `answering_a_chat` `ContextVar` is deleted. The host makes each chat's call with `ToolCall.answers_a_chat`, and every graph operation that builds takes the call it serves (`load_working_copy`, `load_files`, `refresh`, `refreshed`, `set_overlays`); `GuidanceAction` passes its call (guidance_actions.py:273), as does `CheckedGraph` (checked_graph.py:121).
- **R7-M3:** `App.tsx` asks `graphs.filterChoices(practices, node_types, practicesBefore)` on every practice and node-type change (`offerChoices`, :220); `practiceSelection`, `mergeKept`, `overlayFilterRefresh` and `mergeNewCatalogItems` are gone. The test copy is R8-L2.
- **R7-M4:** the chat-ui no longer reads `~/.cdd/runtime.json`. `CddHome` publishes `install.json` into the board mod (cdd_home.py:66, :181), and `installCommand` runs it (server-health-client.ts:139).
- **R7-M5, the tables round 7 named:** `_SUFFIX_ORDER` and `_MONACO_LANGUAGES` are deleted; the rest is R8-L1.
- **R7-L1, the active ticket:** `board.active` is sent whole and the chat bar reads it directly (chat-bar-client.ts:128). The switch list is decided (below).
- **R7-L2:** the board's port is written once, in `space/kanban/app/packages/session-board/ports.json`, read by its server (serve.ts:10) and registered with `ServerHealth` (board.py:595), whose `kanban_app_url` the chat-ui uses (board.ts `boardUrl`, board-server.ts). The near-copy reader is R8-L4.
- **R7-L4:** `CatalogFidelity` asks its `CatalogPractice` for the examples folder (catalog_examples.py:299).

## Decided (not counted)

- **R7-L3:** `harness/catalog_generator/.context/cdr/0001-utilities-are-the-work-and-tools-layers.md`. The catalog keeps sorting utilities by the layer their module is in (`_UTILITY_PACKAGES`). Agreed: the layer is the fact AGENTS.md defines, an annotation would repeat the folder and could disagree with it, no install destination tells the layers apart, and `@noCatalog` stays the one way out.
- **R7-L1, the switch list:** `harness/chat-ui/.context/cdr/0002-switch-list-names-tickets-its-columns-send.md`. `open_tickets` stays as names resolved against the columns of the same `board.show` answer. Agreed: Python decides which tickets are open, sending them whole would double the answer the chat bar reads on every turn, and the names point only into that one answer.
- **Graph CDR 0001, updated in round 7:** a chat's graph holds plain restored nodes, and a practice that builds on another's model objects must read them through `nodes_read_now`. Agreed as a design, but it puts the burden on every reading practice, and Stories did not take it up (R8-H1), so the record's consequence is not yet true of the code.

## Did the fix agents follow the round-7 fix rules?

- **Specs take the live path: missed three times.** The worker-refresh spec matrix covers Clean Engineering + DDD but not Stories or BDD, and never a graph that already holds every practice (R8-H1). The heavy spec builds five full loads into empty graphs, not refreshes of a shared session graph (R8-M1). The explorer's vitest answers filter choices with a TypeScript copy of the Python rule (R8-L2). Followed for R7-M2 (`tool_calls_spec.py`, the in-process case in `graph_build_spec.py:114`), R7-M4 (`cdd_home_spec.py`), and R7-L2 (`server_health_spec.py`, `board_app_spec.py`).
- **Each fix applied to every sibling format, reader and table: missed twice.** R7-H1 was fixed in the DDD reader only, not the Stories reader beside it (R8-H1). R7-M5 removed the two named tables but left the catalog's three file-kind tables and its raw-suffix label (R8-L1).
- **One owner for each finding: mostly followed.** Each round-7 row went to one commit. R7-H1 needs two owners, `harness/graph` for what a restored node is and each practice for its reading; round 7 assigned it to the graph fixes, which changed only DDD. R7-L2's fix created a second ports reader in another module (R8-L4).
- **Decision records:** written for R7-L3 and the switch-list half of R7-L1, both agreed.

## Rule-versus-schema gaps

Not applicable here: this area holds no practice and no `schema.yaml`. The Stories reading that fails in R8-H1 belongs to the Stories/UX/DDD area.

## Scanner false positives

None judged this round: the graph validate failed before it reported hits (R8-H1). This is the second round in a row with no graph hits for this area, so round 6's open scanner items (`python_class_model.py:184-188`, `operation_checks.py:111-124`, `class_rules.py:36`, `operation_semantics.py:63`, `eliminate-duplication` matching only identical bodies) remain unchecked here.

## Goal-class counts (this area's table)

Rows by concern: `{1: 3, 2: 1, 12: 1}` over 6 rows (1 high, 1 medium, 4 low), one row (R8-M1) with no concern number. By status: left 4 (R8-H1, M1, L1, L2), new 2 (R8-L3, L4), new scope 0, regression 0.

| Goal class | Concerns | left | new | new scope | regression | decided | total |
|---|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 0 | 0 | 0 | 0 | 2 (R7-L3, R7-L1 switch list) | 0 |
| Shadow models | 2 | 1 (R8-H1) | 0 | 0 | 0 | 0 | 1 |
| Duplicated functions | 1, 12 | 2 (R8-L1, L2) | 2 (R8-L3, L4) | 0 | 0 | 0 | 4 |

This area's goal total is **5, down from 12 in round 7** (counted once per concern, as `concern_counts.py` does; no row names both 1 and 12, so counting each row once per class also gives 5). One high finding remains in a goal class: R8-H1 (shadow models). Both new rows come from round-7 fix code.

## What would make this area's next round cheaper

1. **Fix a cross-practice reading bug in every reader, and spec the matrix.** R7-H1 was fixed where it crashed (DDD) and broke the next round's validate in the reader beside it (Stories). Before closing a finding of the shape "practice A reads practice B's model objects", list every `link_to_other_practices` and `read_working_copy` that reads another practice's or its own held nodes (DDD, Stories, BDD), and refresh each pair in a worker on a graph that already holds every practice.
2. **Make the heavy spec the live case.** B10 has now failed its live measurement in three rounds while its spec passed. The live case is several refreshes of one shared session graph that holds every practice; the spec builds fresh, separate graphs. Until the spec does what validators do, its two-second bar says nothing about the server agents use.
