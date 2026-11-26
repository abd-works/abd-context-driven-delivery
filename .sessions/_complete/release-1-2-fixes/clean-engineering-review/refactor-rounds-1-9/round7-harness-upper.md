# Round 7: harness-upper, after the round-6 fixes

Area: `harness/hooks`, `harness/mcp`, `harness/graph` (with its TypeScript app), `harness/diagnostics`, `harness/chat`, `harness/catalog_generator`, `harness/design_canvas`, and the TypeScript plugin `harness/chat-ui`. Code read at c8921451 on `ensure-domain-orientation-refactor`. The CDD MCP host (pid 30700, `~/.cdd/runtime`, pinned to c8921451) served the same commit.

Checks run:

- **Graph rules:** one validate, `clean-engineering-code` with `graph: true` and the eight area folders as `paths`, started 06:31:55 local (11:31 UTC). The build ran in a worker process, and the call answered "still running" ten times. At about 06:36:30 it **failed**: `RecipeLineFailed` at `cdd_guidance/actions/validate/validate.py:57` (`self._graph.check_beside(self._reports)`), from `GraphBuildFailed: the graph build's worker process exited with 1`, ending in `AttributeError: 'Node' object has no attribute 'stereotypes'` at `cdd_guidance/practices/ddd/model/stereotypes.py:98`. The server log (`~/.cdd/server.log`) shows the same traceback six times in this window, so other validators hit it too. Under `.claude/rules/mcp-fail-loud.md` no second graph validate was made. **This round has no graph hits for this area.** The failure itself is R7-H1.
- **B10, checked directly:** while that validate ran, a loop started a `curl` to `http://127.0.0.1:47800/ping` every 2 seconds (06:32:05 to 06:36:46, 129 pings). Results are under B10 below.
- **AI across files:** every finding in `round6-harness-upper.md` was checked against the code, along with the decision records the fix agents wrote (`harness/graph/.context/cdr/0001`, `harness/diagnostics/.context/cdr/0001`, `harness/design_canvas/.context/cdr/0001`, `harness/mcp/.context/cdr/0001-0002`, `harness/chat-ui/.context/cdr/0001`). The round-6 fix code (commits 636d8df8 and 7f24bdac, and the merges after them) was read beside the files it imports and the files that import it, including `cdd_guidance/practices/ddd/model/graph_reading.py`, `space/kanban/report.py`, `space/kanban/ticket.py`, `space/repo/worktree.py`, and `harness/markdown/format.py`.

Status words: **fixed**, **left**, **regression**, **new**, **new scope**, **decided**.

## B10: pings during one graph validate

| measure | round 6 | round 7 |
|---|---|---|
| pings | 60 | 129 (one every 2 s, 4 min 41 s) |
| timed out or refused | 29 (10 s timeout, then ECONNREFUSED) | **0** (30 s timeout) |
| slowest ping | over 10 s (timed out) | **8.84 s** (06:36:31), next 6.74 s, 5.65 s, 5.56 s |
| median | not recorded | 1.17 s |
| over 2 s | not recorded | 55 of 129 (43%) |
| idle ping | about 0.1 s | 0.002 s |

Five other validators' reports were written in the same window (`clean-engineering-*-20261108T1131..1136`), so several builds overlapped, as in round 6. **B10 is much better and still not done.** The server never refused a connection and no ping timed out, but its event loop still stopped answering for 5 to 9 seconds at a time. The likely cause is the work the build still does in the server's interpreter: `Graph._build` serialises the whole graph it holds into the order (`SavedGraph.from_graph(self)`, graph.py:1418), and then restores the worker's whole answer into the server's graph (`self._hold(...)`, graph.py:1420; `_hold` re-populates every practice's tree, graph.py:1268-1281). `graph_build_heavy_spec.py:113` asks for every call to answer "within two seconds while the build runs", but it builds one small folder, so the live case with several large builds fails that bar 43% of the time. See R7-M1.

## Findings, most severe first

### High

| # | file:line | concern | found by | status | finding | fix (one line) |
|---|---|---|---|---|---|---|
| R7-H1 | harness/graph/graph.py:1433 (`carry_out` → `_hold(order.state)`), cdd_guidance/practices/ddd/model/stereotypes.py:98 | 2 | both (the graph validate failed; AI traced it) | new (made by the round-6 B10 fix together with DDD reading Clean Engineering's class model, f02b6485) | **A graph validate on this area fails, and the graph holds two object models depending on which process built it.** In a chat's call the graph sends what it holds to a worker as a `SavedGraph`. The worker first restores that state, as plain `Node` objects, then reads the working copy. With `paths` set, Clean Engineering reads only the scoped files, so its other `OoadClass` nodes stay plain restored `Node`s. `DddReading._members_by_folder` (graph_reading.py:193-207) takes every `OoadClass` of the Clean Engineering practice and asks each for `stereotypes`, which a plain `Node` lacks, so the worker exits with 1 and validate fails. The same split reaches the server: after a chat's build its graph holds restored plain nodes, while a spec or a script holds parsed model objects (the graph CDR says so). Any practice or rule that reads another practice's model objects then behaves differently in a chat. `graph_build_spec.py` checks node and violation counts for one practice, but has no case where one practice reads another's model objects. | Have the worker read every chosen practice fresh from the working copy, and keep restored state only for checks that need no model objects. Otherwise give the reading practices an operation on the extended practice that answers parsed class models and raises a named error for a restored node. Add a spec that refreshes a scoped DDD + Clean Engineering graph in a worker. |

### Medium

| # | file:line | concern | found by | status | finding | fix (one line) |
|---|---|---|---|---|---|---|
| R7-M1 | harness/graph/graph.py:1418-1420, harness/graph/saved_graph.py:167 | behaviour (no concern number) | AI, measured live this round | left (R6-H2, partly; lowered from high, because the server now keeps answering) | Graph builds run in a worker process (graph CDR 0001), progress is throttled to four reports a second, and `cdd.ping` answers on the event loop. While one validate ran beside others, no ping failed, but the slowest took 8.84 s and 55 of 129 took over 2 s (idle: 2 ms). The server's interpreter still serialises the whole held graph into each `BuildOrder` and restores the whole answer with `_hold`, which rebuilds every practice's tree. The heavy spec's two-second bar is met only for a small folder. | Send the worker only the scope and the roots, not the whole held graph, and restore the answer off the request path or in parts. Make the heavy spec build a Stories/UX/DDD-sized folder with a second build running. |
| R7-M2 | harness/mcp/tool_calls.py:28, :41; harness/graph/graph.py:1417 | 5 | AI | new (code added by the round-6 B10 fix) | Where a graph build runs is decided by an ambient flag. `answering_a_chat()` sets a module-level `ContextVar` around each chat's call (mcp_server.py:709), and `Graph._build` reads it through `is_answering_a_chat()`. This is the same pattern that mcp CDR 0002 removed for the current project and chat: a call started on another thread, or a script that runs a host call in-process, reads whatever the flag says. The `ToolCall` the server makes for each request already exists to carry this. | Put "answers a chat" on the `ToolCall`, and have the graph read it from the call that loads it, or be made with a build runner that the host hands it. |
| R7-M3 | harness/graph/app/App.tsx:395-478 | 12, 1 | AI | left (R6-M6, partly) | The LERN tables in `overlay-labels.ts` are gone, the three-argument call is gone, and `npm test` runs `tsc --noEmit`. The explorer still decides filter choices in TypeScript on a practice change (`practiceSelection`, `mergeKept`, :445-478) and on an overlay change (`overlayFilterRefresh`, `mergeNewCatalogItems`, :395-443). It asks Python's `graphs.filterChoices` (:246) only on a node-type change. No decision record covers it. | Call `graph.filter_choices` for every selection change and delete the three merge functions. |
| R7-M4 | harness/chat-ui/pane/hooks/health/server-health-client.ts:134 | 12, 9 | AI | left (R6-M7) | Unchanged. `installTarget` still reads `~/.cdd/runtime.json` itself, works out the `CDD_HOME` default, and picks the checkout to install from. `CddHome` (harness/mcp/cdd_home.py) owns that file and those rules. No decision record covers it. | Run one Python entry point (for example `scripts/install.py --from-runtime`) that reads the file through `CddHome`. |
| R7-M5 | harness/catalog_generator/catalog_examples.py:24, :42 | 1 | AI | left (R6-M8 and R6-M9, catalog half) | The graph now asks each practice's formats for a file's language (`Node.file_language`, graph.py:577), and `Format.FILE_ORDER` (harness/markdown/format.py) is the one file order, which `FidelityProgress.files` applies; the chat bar dropped its own. The catalog still keeps its own suffix tables: `_SUFFIX_ORDER` (a second file order) and `_MONACO_LANGUAGES` (a second suffix-to-language table). The fix kept one owner but did not delete the twins. | Have the catalog order example files by `Format.FILE_ORDER` and name each file's language through the practice's format. |

### Low

| # | file:line | concern | found by | status | finding | fix (one line) |
|---|---|---|---|---|---|---|
| R7-L1 | harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:128 | 5, 12 | AI | left (R6-L2; K-F21 known) | The chat bar still finds the active ticket by the name in `board.active` and searches every column for it (`ticketNamed`, :134). No decision record covers it. | `board.show` sends the active ticket whole. |
| R7-L2 | harness/diagnostics/server_health.py:17 | 1 | AI | left (R6-L6) | The session board's port 8778 is still written in three places: `KANBAN_APP_PORTS` here, `DEFAULT_PORT` in `space/kanban/app/packages/session-board/serve.ts`, and `BOARD_URL` in `harness/chat-ui/pane/hooks/board-chat/board.ts:4`. The graph app's ports were moved into one file (`harness/graph/app/ports.json`, read through `GraphAppPorts`), but the board's were not. | Do the same for the board: one `ports.json` beside its server, read by the server, `ServerHealth`, and the chat-ui. |
| R7-L3 | harness/catalog_generator/catalog_generator.py:58, :74, :77 | 5 | AI | left (R6-M11, catalog half) | `CatalogGenerator` now takes toolset classes, but it still sorts them by matching each class's `__module__` (and each failed load's reference) against `_UTILITY_PACKAGES = ("space.", "tools.")`. The diagnostics half of R6-M11 is decided (see below). The catalog half has no decision record. | Ask each toolset class where it belongs (its install destination or catalog annotation). |
| R7-L4 | harness/catalog_generator/catalog_examples.py:311, harness/catalog_generator/catalog_practice.py:170 | 1 | AI | new (made by the round-6 move of `CatalogPractice` into its own file) | Two `examples_folder` properties work out the same folder: `CatalogFidelity` from `fidelity.practice_guidance.module_dir`, and `CatalogPractice` from `practice.module_dir`, each joined with `EXAMPLES_FOLDER`. | `CatalogFidelity` asks its `CatalogPractice` for the folder. |

Concerns 3, 4, 6, 7, 8, 10, 11: none found this round. R6-H3's two cycles are gone. `harness/graph` imports `harness/mcp` (`is_answering_a_chat`, `ThrottledReporter`), which is downward in the layer order in `AGENTS.md`, and nothing in `harness/mcp` or `harness/hooks` imports `harness/graph`.

## Fixed since round 6

- **R6-H1:** a hook daemon finds a daemon of the older layout on its port (through `.cursor/hook-server.json`, or else the port's holder), stops it, takes the port, and logs it (`HookDaemon.claim_port`, hook_daemon.py:410). `serve` no longer returns silently. Closing a worktree stops its daemon (`space/repo/worktree.py:188`). `hook_daemon_spec.py` covers three cases with an older-layout fixture daemon.
- **R6-H3:** both runtime cycles are gone. `saved_graph.py` imports `graph` only under `TYPE_CHECKING`, and `CatalogPractice` and `GitCitation` have files of their own, which `project_approach.py` imports.
- **R6-H4:** `server_health.py` reads the graph app's ports through `harness/graph/graph_app.py` (`GraphAppPorts`), and `scripts/instances.py` reads them from there too.
- **R6-H5:** a model object with no practice raises `ModelDetached` when asked for its graph (model_node.py:206); no private `Graph()` is made.
- **R6-H6:** `SavedGraph.restored_graph` is gone; `space/kanban/report.py:263` asks `saved.checks_of(self._practice)`.
- **R6-M1:** the catalog asks each practice for its examples folder (`module_dir`), and the guidance probe asks the action catalogue and each practice for its folder; no `cdd_guidance` path or module string is left in the area's code.
- **R6-M3:** `CallDiagnostics` makes no stand-in `ToolCall`; probing without a call raises `DiagnosticsNeedACall`.
- **R6-M4:** each practice's part of the graph keeps its own schemas (`schema_with`, graph.py:968); nothing writes into the practice's `__dict__`.
- **R6-M5, all but the parts the graph CDR decides:** `SchemaFields.of(practices, overlays)` reads the graph's own practices and finds pattern schemas through `GraphOverlay.practice_file`; no `lru_cache`; each graph makes its own pattern objects.
- **R6-M8, graph half:** `_FILE_LANGUAGES` and `Source.language`'s if-chain are gone; `Node.file_language` asks the practices' formats. The catalog half is R7-M5.
- **R6-M9, TypeScript half:** the chat bar's `fileOrder` is gone; `Format.FILE_ORDER` orders files in Python. The catalog half is R7-M5.
- **R6-M10:** examples are kept by `CatalogFidelity`; practice keys and stage names are turned into a fidelity only where a saved or typed mapping is read (`ProjectFiles._fidelity_at`). `SkillSlashName` is gone; the slash command comes from the skill install.
- **R6-L1:** the graph holds one `SchemaEdges` (graph.py:1102).
- **R6-L4:** `CddHome` and the hook daemon both take `PYTHONPYCACHEPREFIX` from `RepositoryToolsets.pycache_prefix()`.
- **R6-L5:** `"mcpServers"` is asked of `IdeLayout.mcp_servers_key` at both levels.
- **R6-L7:** `Node` has `forget_rules()` and `leave_tree()`; `PracticeNodes` no longer resets another class's private fields.
- **R6-L8:** both diagnostics descriptions name every skipped operation and point at the IDE folder the install wrote; `agent_tools_diagnostics_spec.py` fails when the description and the tables disagree.

## Decided (not counted)

- **R6-M2 and R6-M11, diagnostics half:** `harness/diagnostics/.context/cdr/0001-probe-arguments-by-published-name.md`. The probe keeps its arguments and skips by published MCP name, and reads the install record's `module:Class` references. Agreed: a published name is a public contract the probe checks, putting probe fixtures on every annotation would have each checked module carry its checker, and the install record is file data.
- **R6-L3:** `harness/design_canvas/.context/cdr/0001-recipe-called-canvas-api.md`. `CanvasVersions`, `FixtureScreen`, and `ScenarioSource` are the API that the Claude Design recipe calls. Agreed: the version choice needs the person, so it stays a recipe step.
- **R6-M12:** `harness/graph/.context/cdr/0001`, "Kept as they are". `_held_practice` is gone. `practice(key)` is the one key lookup, `practice_of(kind)` opens a practice, and `loaded(kind)` answers without opening one. Agreed.
- **R6-M5, registry parts:** the same CDR keeps `PatternOverlays._registered` as a process-wide registry of classes, as `PracticeCatalogue` does, and `GraphOverlay.rules_for` names its rules package from the pattern's own module. Agreed: the pattern objects are now per graph.

## Did the fix agents follow the round-6 fix rules?

- **A spec on the effect of a concern-5 fix:** followed for R6-H1 (`hook_daemon_spec.py`), R6-M3 (`agent_tools_diagnostics_spec.py`), R6-M4 (`schema_rules_spec.py`) and B10 (`graph_build_spec.py`, `graph_build_heavy_spec.py`). **Missed for B10's reach:** the specs build one practice, or one small folder, so they miss R7-H1, where one practice reads another's model objects, and R7-M1, a real-sized build next to others.
- **One owner for a duplicate, with the twins gone:** **missed** for R6-M8/M9. `Format.FILE_ORDER` and the formats' languages are the owners, but the catalog's `_SUFFIX_ORDER` and `_MONACO_LANGUAGES` remain (R7-M5). R6-M1's move of `CatalogPractice` also made a twin `examples_folder` (R7-L4).
- **A decision record for each skip:** followed for R6-M2, M11 (diagnostics), M12, L3, and M5's registry. **Missed** for R6-M6, M7, L2, and L6: they are still in the code with no fix and no record (R7-M3, M4, L1, L2). All four are on the TypeScript side or touch it.

## Rule-versus-schema gaps

Not applicable here: this area holds no practice and no `schema.yaml`. The DDD reading that fails in R7-H1 belongs to the Stories/UX/DDD area.

## Scanner false positives

None judged this round: the graph validate failed before it reported hits (R7-H1). Round 6's scanner items 1-5 (`python_class_model.py:184-188` type-only imports; `operation_checks.py:111-124` values and injectable defaults; `class_rules.py:36` judging specs; `operation_semantics.py:63` named lookups; `eliminate-duplication` matching only identical bodies) could not be rechecked from hits. Commit 39df16f8 and a6e02056 changed the scanners; the CE scanners area owns them.

## Goal-class counts (this area's table)

Rows by concern: `{1: 4, 2: 1, 5: 3, 9: 1, 12: 3}` over 10 rows (1 high, 5 medium, 4 low). By status: left 7, new 3, new scope 0, regression 0. Each row counted once per goal class:

| Goal class | Concerns | left | new | new scope | regression | decided | total |
|---|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 3 (R7-M4, L1, L3) | 1 (R7-M2) | 0 | 0 | 2 (R6-M11 diagnostics half, R6-M5 registry) | 4 |
| Shadow models | 2 | 0 | 1 (R7-H1) | 0 | 0 | 0 | 1 |
| Duplicated functions | 1, 12 | 5 (R7-M3, M4, M5, L1, L2) | 1 (R7-L4) | 0 | 0 | 1 (R6-M12) | 6 |

`python concern_counts.py round7-harness-upper.md` counts once per concern, as round 6's total of 26 did. It gives bad resource orientation 4 (left 3, new 1), shadow models 1 (new 1), and duplicated functions 7 (left 6, new 1), because R7-M3 counts under both 1 and 12. So this area's goal total is **12, down from 26 in round 6**, or 11 counting each row once per class. Both new goal rows (R7-H1, R7-M2) and R7-L4 come from round-6 fix code, not from code that round 6 missed.

## What would make this area's next round cheaper

1. **Give each TypeScript finding a fix or a decision record in the round it is raised.** R6-M6, M7, L2, and L6 (R7-M3, M4, L1, L2) have now been carried for a round with neither. They are half of this round's goal rows. Each needs one of two things: a Python operation that sends what the TypeScript works out (filter choices, the install target, the active ticket, the board's port), or a record that says why it stays.
2. **When a fix moves where work runs, test it against a practice that reads another practice's model objects.** The worker build was specced on one practice and passed. It broke DDD's reading of Clean Engineering classes in the first real validate. A spec matrix of "practice A reads practice B's model objects" × "built in a worker, scoped refresh" would have caught R7-H1 before the merge. A ping check with a real-sized build next to a second one would have caught R7-M1.
