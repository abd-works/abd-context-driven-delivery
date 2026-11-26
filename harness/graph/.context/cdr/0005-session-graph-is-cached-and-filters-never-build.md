# A session's graph is built once and kept; a filter only narrows the view, and a file change re-reads only that file

**Status: proposed, for approval before building.** This CDR changes no code yet (card b56779ab42c9).

Toggling a format chip (diagram, markdown, code, grid) on the chat bar or in the Files app takes seconds to minutes, because each toggle builds the knowledge graph again. The user wants three things. A filter change works on the graph already built. A file change re-reads only the files that changed. And the plan must show it "CAN'T introduce bugs".

## Where a filter change builds the graph today

1. **Format chip, node filter, or file list in the graph view → a fresh read of every listed file.** `ticket.choose_formats` or `session.toggle_guidance` (format) writes `session.json` and raises the guidance version (`GuidanceSelection.changed`). The Files app reads the listing again (`ticket.root_files` / `ticket.fidelity_files`, which set `is_listed`). `FilesGraph.read` (`harness/files_app/app/files/files-graph.ts`) sees a new read key (the listed paths and the node filter) and calls `session.graph_trees`. `SessionExplorer._read_listed` (`space/session/files/session_explorer.py`) calls `Graph.load_files(root, working, listed)`, which:
   - narrows the graph's scope to the listed files (`LoadScope.of_paths`, so `over_whole` is false);
   - forgets every node (`GraphPractices.open_chosen`);
   - runs `BuildStep.READ` in a worker, which parses every listed file, links them, and runs every rule;
   - reads the worker's whole answer back (`practices.hold(SavedGraph.from_file(answer))`).

   Nothing is reused, so even a toggle that leaves the file list unchanged reads every listed file again. `session.graph_fix_prompt` does the same.
2. **Practice chip → a new graph opened from the 125 MB `graph.json`.** `SessionGraph.graph` remakes the graph whenever `SessionPractices.held` changes (`_graph_of`). The new graph opens the session's saved graph (`GraphReads.open_saved` → `GraphPractices.reopen`). The profile of `harness/hooks/hook_spec.py` measured this at over 40 s.
3. **Ping-pong between the narrow graph and the whole one.** After `graph_trees` narrows the scope, the next file viewer (`SessionFile` → `SessionGraph.holding`) or validate calls `hold_whole`. That call reads the whole saved graph back (`GraphReads.load`) and runs every rule in a worker (`BuildStep.CHECK`). The next `graph_trees` throws it all away again.
4. **The saved graph is never checked against the files.** `SavedGraphFile.holding` says "It is not checked against the files' dates". `SessionGraph` and `DocumentGraph` decide freshness by modification time alone, and only for files a viewer showed. A git checkout made outside CDD is never seen. A saved graph that cannot be read, or is in an older shape, quietly gives `None`, and the graph is read again without saying so.

## Measured (this worktree, in process, throwaway CDD_HOME, no running server touched)

The graph held Stories and Clean Engineering, the two practices switched on in session `ui-fixes-as-i-use-it`. The script is a scratch file of this card's chat. A live toggle adds a worker's start and the reading back of its answer on top of these times.

| What | Today | Target |
|---|---|---|
| Format chip toggle, Files app listing one story folder (`load_files` of `story_tests/review-generated-work-in-file-viewer`) | **17.9 s** (16.7 s again with nothing changed) | **under 0.5 s**: filter 0.3 s (`explorer_trees`, measured) plus the change check about 0.2 s |
| Format chip toggle, listing `harness/graph` and `story_tests` | **46.6 s** | **under 0.5 s** |
| Practice chip toggle (new graph, `open_saved` of the 125 MB `graph.json`) | **7.3 s** in process: 2.0 s to parse, the rest to restore. Over 40 s in today's `hook_spec` profile | **under 0.5 s**: a filter, no new graph |
| One-file change, a Python file (`refresh harness/graph/load_scope.py`) | **25.4 s** | **under 3 s** |
| One-file change, a model document (`refresh harness/graph/.context/graph-model.md`) | **26.4 s** | **under 3 s** |
| Checking every file for changes (list and stat 2,207 files; hash all 27 MB) | not done | 0.16 s list and stat; 0.29 s to hash every file |
| Writing the whole graph out (`SavedGraph.from_graph`) | 2.9 s | done only by the worker, as today |

A one-file refresh parses one file, yet it costs 25 s. Almost all of that is outside the parse: every rule's findings are dropped and every rule runs again over the whole practice (`rule_run.renew`), and each practice's compared facts and tree are rebuilt. So the one-file target needs more than a partial read: build step 6 limits which rules run again, under the same differential proof.

## Decision

### 1. One whole graph per session, kept; every filter is a view

- The session's graph always covers the whole working copy of every practice the session has (`own_practices`), each on its roots. It is never narrowed. `SessionGraph.graph` no longer remakes the graph when practices are switched on or off. `SessionPractices.held` becomes every practice, and `take_up` goes away.
- `graph_trees`, `graph_branch`, and `graph_fix_prompt` call `SessionGraph.current()` (§3), then answer `explorer_trees` / `fix_prompt` with a filter. The filter holds the listed paths, the practices switched on, and the node filter. `load_files` is no longer called from the session. `_read_listed`, `SessionGraph.listed`, `as_it_is_now`, and `holding`'s modification-time records are deleted, because the manifest (§2) replaces them.
- A format chip, a practice chip, a stage, a node filter, or a new file list then costs only the filter and the tree serialisation. No parse, no rule, no worker.
- One visible change: the listed view now shows cross-file links and findings that a read of the listed files alone could not judge, the same ones validate reports. `FileViewFilter.shows` already hides nodes reached in unlisted files.

### 2. What is cached, and keyed how

- **The graph:** in memory in the server for the life of the session, and on disk as `graph.json` in the session's work folder, as today. Each saved node keeps its source file, so the nodes of a file can be dropped (`PracticeLoading.forget_files`).
- **The manifest** (`GraphManifest`, new, saved inside `graph.json` beside the practices so the two can never disagree):
  - *Graph key*: the saved shape version (`SAVED_SHAPE_VERSION`), a code fingerprint (a content hash of `harness/graph/`, each held practice's package, and each applied pattern's package), each practice's key and roots, and the overlays.
  - *File key*, for every file a full build would read: its path from the project, size, `mtime_ns`, and a content hash (blake2b-128 of its bytes). Each `PracticeReading` gains `candidate_files(root)`, the files a full read reads, including the `.context/*-model.md`, `story-map.md`, and bounded-context documents. `scanned_files` skips dot folders, and a refresh reads `.context` (`_REFRESH_SKIPPED_FOLDERS`), so the candidate list must name those files itself.
  - *Git key*: the content hashes of `.git/HEAD` and `.git/index`, and the commit HEAD names.

### 3. How a change, including one made outside CDD, is found

`SessionGraph.current()` runs before every graph read. It takes the graph's `reads.changing` lock, so no read ever sees a graph half refreshed. It:

1. lists the candidate files again (about 0.16 s here to list and stat all 2,207);
2. hashes:
   - **every** candidate file when the graph was just opened from disk, or when the git key changed (a checkout, pull, reset, stash, or merge, made inside CDD or not); hashing every file takes 0.29 s here;
   - otherwise each file whose size or `mtime_ns` changed, plus each file whose `mtime_ns` falls within 2 s of the last check. This is git's own guard against changes that land in the same tick as the check ("racy" timestamps);
3. compares the hashes with the manifest. *Changed* means the hash differs. *Added* means a candidate the manifest lacks. *Removed* means a manifest file no longer there. A rename is a remove and an add in one refresh. A file whose time changed but whose content did not is not read again; only its manifest entry is updated.

A time stamp alone never decides "unchanged" after a git operation or an open, and never decides "changed" without a hash.

### 4. Partial rebuild and re-linking across files

The changed, added, and removed files go to the existing `Graph.refresh` in one call. That refresh already runs in a worker that answers only what changed (CDR 0003). For those files it:

- widens the set with `read_with`: a story map and its story tests are read together;
- drops their nodes in every practice, and every edge into or out of those nodes, whichever practice holds it (`GraphBuild._forget`). A step's link to a class heading in `domain-model.md` goes when either end's file is read again;
- reads them again, then lets every practice link its nodes to other practices' nodes (`link_to_other_practices`). The linkers read only saved facts and edges (CDR 0002), so they link the nodes kept to the nodes read now in one pass;
- recomputes each practice's compared facts over the whole practice (CDR 0004) and runs every rule again (`rule_run.renew`), so a whole-practice rule's findings on unchanged files are right too;
- saves `graph.json` with the new manifest in the worker (`BuildTask.saves`), so the server never serialises the graph.

Unchanged files are never parsed again. **One gap to close first** (build step 1): a linker that walks only `nodes_read_now` from one side leaves no edge from a kept node to a node read now. For example, a step in an unchanged scenario file names a class whose heading was renamed in `domain-model.md`. Each practice's `link_to_other_practices` is checked against the differential spec (§6), and every linker that misses a direction links from every node of the side it starts from, or from an index of the names each node refers to.

### 5. Safety fallback: rebuild the whole graph, and say so

`current()` throws the graph away and runs a full `load_working_copy(force=True)` in a worker, never serving the old or a partial graph, when any of these holds:

- `graph.json` is missing, cannot be read, or is in another shape. Today `SavedGraphFile.read` gives `None` silently; it will give the reason instead;
- the manifest is missing or cannot be read, or its graph key differs: code fingerprint, roots, practices, or overlays;
- a refresh fails (`GraphBuildFailed`). Today the old graph is kept. The graph is now marked stale and rebuilt whole;
- the changed files are more than a quarter of the candidates. A full read is then as cheap and simpler;
- verification mode (below) finds a difference.

Each fallback:

- reports progress, for example "Rebuilding the whole graph: the saved graph was made by other code";
- writes a `graph` line to the session log;
- puts the reason in the answer (`GraphLoaded.message`, and a `rebuilt_because` field on what `graph_trees` answers), which the Files app shows as a notice.

While a rebuild or refresh runs, every reader waits on `reads.changing` and the Files app shows its reading progress. No call ever gets trees from a graph that was half refreshed or found stale.

**Verification mode** (`CDD_GRAPH_VERIFY=1`, on in the heavy specs and the dev lane): after each partial rebuild, a full build of the same working copy runs in a second worker. Its nodes, edges, and violations are compared with the refreshed graph's. On any difference, the full graph replaces the refreshed one, the difference is logged to `session.err` as a defect naming the files and edit, and the loud fallback above fires.

### 6. Test plan

Unit tier (fakes, each example under 100 ms):

| Spec | What it proves |
|---|---|
| `harness/graph/graph_manifest_spec.py` | A changed, added, removed, or renamed file is found by its hash. A file touched with no content change is not changed. A change of the same size within the 2 s window is found. Every file is hashed after the git key changes, and after an open. |
| `harness/graph/graph_manifest_spec.py` (graph key) | Each kind of key difference (shape, code fingerprint, roots, practices, overlays) gives a full rebuild with its reason. |
| `space/session/session_graph_spec.py` | With a counting fake `GraphBuild`, a format chip, practice chip, stage, node filter, or file-list change runs no build and opens no saved graph. `current()` with nothing changed runs no build. One changed file runs one refresh naming exactly that file (plus `read_with`). |
| `space/session/files/session_explorer_spec.py` | `graph_trees` for a file list holds exactly the nodes of those files from the whole graph, and never calls `load_files`. |
| `harness/graph/saved_graph_spec.py` | An unreadable or outdated `graph.json` gives a reason, never a silent `None`. A failed refresh leaves the graph marked stale, and the next read rebuilds it whole. |

Heavy tier (real parses, real workers, real git):

| Spec | What it proves |
|---|---|
| `harness/graph/graph_incremental_heavy_spec.py`, the **differential spec** | Run on a copy of `harness/graph/_examples/input` (every practice, the LERN overlay, Python and TypeScript, markdown story tests) and on a copied slice of this repository: `story_tests/review-generated-work-in-file-viewer`, `harness/graph` and its `.context/*-model.md`, and the root `.context/story-map.md`. That covers Stories, DDD, Clean Engineering, UX, and BDD, in markdown, Python, TypeScript and drawio, wherever a practice reads them. For each edit — change a file, add one, delete one, rename one, change a heading another file links to (a class heading in a `*-model.md`), change a class steps link to, change a story's scenario file — the refreshed graph equals a fresh `load_working_copy(force=True)`, practice by practice: nodes (id, type, name, source, facts), edges (kind, parent id, child id), and violations (rule, node, message, severity), each list sorted. The comparison helpers already in `graph_worker_heavy_spec.py` (`_practice_state`) move to `harness/graph/spec_support.py` to be shared. |
| Same file, a fixed-seed **sequence** of 30 random edits drawn from those kinds | Compared with a fresh build after every edit, so edits that build on earlier ones are covered too. |
| Same file, **same findings** | `validate` with `graph: true` on the refreshed graph and on a fresh build gives the same report (rules, nodes, messages) for each practice. |
| `space/session/session_graph_heavy_spec.py`, **never stale** | In a temp git repository, a session graph is built. Then `git checkout` of a branch that changes a scenario file and a model document, done in a subprocess outside CDD, is held by the next `graph_trees`. So are a file written with its old `mtime` restored (`os.utime`) and an edit of the same size within the same second. |
| Same file, **loud fallback** | A corrupt `graph.json`, an old shape, a changed code fingerprint, and a worker that fails each give a full rebuild with the reason in the answer and the session log. |
| Same file, **timing** | On this repository's whole session graph held in memory: a format toggle answers `graph_trees` under the target below, and a one-file refresh finishes under its target. |

E2E tier (one example): in the Files app, switching a format chip redraws the graph view without the reading progress, measured with Playwright against a server of the spec's own.

### 7. Steps to build it, in order

1. **Differential spec first (heavy), against today's refresh.** Write `graph_incremental_heavy_spec.py` with every edit kind, compared with a fresh build, and move `_practice_state` into `spec_support.py`. Fix each linker or fact that it finds wrong (§4's gap). Nothing is cached yet, so this makes `refresh` itself provably equal to a full build.
2. **`GraphManifest`, test-first (unit).** Candidate files per practice (`PracticeReading.candidate_files`), the file, graph, and git keys, the hash rules of §3, and saving and reading it inside `graph.json`. The saved shape goes to 8.
3. **Loud fallback, test-first (unit).** `SavedGraphFile.read` gives its reason. Add `GraphRebuilt` reasons, the progress, the log line, and the `rebuilt_because` field. A failed refresh marks the graph stale.
4. **`SessionGraph.current()`, test-first (unit, fake build).** Hash, compare, then one `refresh` of the changed, added, and removed files, or a full rebuild on a fallback. The worker writes the manifest with the graph.
5. **Whole graph always.** `held` becomes every practice, a practice chip becomes a filter, and `SessionGraph` stops remaking the graph. `graph_trees`, `graph_branch`, and `graph_fix_prompt` call `current()` and then filter. Delete `_read_listed`, `listed`, `as_it_is_now`, and `holding`'s time records, after checking every caller (`graph_node_ranges`, `SessionFile`).
6. **Run again only the rules a change can affect, proved by the differential spec.** Profile a one-file refresh (25 s today). Then:
   - run node rules again only on the nodes of the changed files, and on the nodes one edge away from them, before and after;
   - run whole-practice checks again only when a fact they read changed. Each `PracticeGraphRule` declares the facts it reads, and `GraphChanges` already lists the nodes and facts that changed;
   - recompute compared facts (CDR 0004) only for the folders and classes the changed files touch.

   Every shortcut is kept only if the differential, sequence, and same-findings specs stay green. Until then a refresh runs every rule, which is slow but right.
7. **Verification mode** (`CDD_GRAPH_VERIFY`), on in the heavy specs.
8. **Never-stale and fallback heavy specs**, then the timing spec and the e2e example. Record the measured times in this CDR.
9. Update `harness/graph/.context/graph-working-copy.md`, `module-context.md`, and `space/session/.context/module-context.md`. Run the unit tier, then the heavy and e2e tiers in the background.

## Considered options

- **Keep listing-driven `load_files`, and cache each file's parsed nodes by content hash.** Rejected: a graph read from the listed files alone cannot judge links across files and practices. And re-linking and running rules on every toggle still costs a worker and the rules.
- **Watch the file system (watchdog) instead of hashing on read.** Rejected as the only guard: a watcher misses changes made while the server was down, and some made by git on Windows. It may later trigger `current()` early, but the hash check stays the source of truth.
- **Modification times only.** Rejected by the request. A checkout can restore old times, and a change within one timestamp tick goes unseen.
- **Shrink `graph.json` or split it by practice so the first open is fast.** Worth doing, but separate. With this CDR the 125 MB file is opened once per server and session, not on every practice toggle. A follow-up card should measure where the 40 s goes.

## Consequences

- A filter change never builds. A file change re-reads only that file and the files read with it. After step 6, it runs again only the rules the change can affect.
- The session graph holds every practice, so the first build of a session reads DDD, UX, and BDD too. After that, it is kept.
- The saved shape goes to 8, so each session's `graph.json` is built again once, loudly, after the change ships.
- The graph view now shows cross-file findings in the listed files, the same ones validate reports.
