# UI fixes as I use it: queued work and decisions

Context for the session that picks up the work queued in chat 82179ef0-da0c-4b49-a11d-f0d46aafce7e. Branch `ui-fixes-as-i-use-it`, worktree `C:\dev\abd-cdd-ui-fixes-as-i-use-it`, CDD session `ui-fixes-as-i-use-it` (45 commits ahead of main on 2026-11-26). Handoff: `.sessions/ui-fixes-as-i-use-it/handoff-20261126T183908.md`. Defect log: `.sessions/_backlog/chat-ui-defects.md`.

## Cards

- 8aa0fef227db (Sparky, done): story explorer class card, divider, realization toggle (9a3cd7d28, 200f27bf6).
- 1a89989913e3 (Bolt, done): whiteboard class diagram arrows: no dotted dependency beside a solid relationship, straight arrow between stacked cards, spread ends, cross-page lanes (5ada42896, 61ce521ba, 861b06cfa, 708e61efe, 99fd2b417 live check).
- fd9db8278537 (Bolt, open): diagram links: story to scenario file or acceptance test, whiteboard story link, class card to model heading or code (4533f28e5, e023a22d3, f0230fd74, c53ca7f06, ffb31b027 live check); pending: story to the mockup screen that shows it (shownOn).
- 28798ce2f1da (Gizmo, done): Files app right-click menu (delete, validate, violations, add to practice) and All files scope (5606bea59, 3af6f1b48, 8d12e3033, 0c244f2c8, 8c9596efb, e89ed3407, acbb7d184, d4f148d4b, 80993e5a9, 1eeff85a4, 95afbb875 e2e twin).
- 432134f1e66e (Cog, done): Given and When realizations as code-like statements; rules repositories-called-only-by-the-flow and domain-operations-call-no-repository; explorer from pml-web's Choose Lines equals its published one (1fc174754, 8799b8b47, 59da37725, 8302866bb, 3ad27a6c0, debbd9ded, 172b29bbd, 831af6fbe); repin left for the person.
- c0a832f14680 (Rivet, done): a robot's whole row in the queue band takes the click (84507b659, a3b503bad).
- 0e4471021857 (Rivet, done): after + on an empty prompt box, the next message sent becomes that card's task (a37bd1d13).
- 19b39b42b977 (Rivet, done): each robot carries a one-sentence theme, shown while its cards are closed (57eaf5bca).
- b56779ab42c9 (Pixel, done): plan for a cached knowledge graph, CDR 0005 proposed (b4b14fe11).
- a18df7baaad3 (open, decision required): approve and build the graph cache; step 1 done (482bb82bc).
- 280eb6e82d43 (open, decision required): repin the dev lane after the pml-web demo and check the fixes live.
- Earlier on the branch: format chips take a press anywhere (778866be2) and show they are filtering (48b156f34); a board send waits for the chat's turn (a11a6a51f); diagram links open in the Files app (6ab5a3cda, bc97a2c27); canvases named by published title (32ec08e1b).

## Open decisions

1. **Approve the graph cache build** (`harness/graph/.context/cdr/0005-session-graph-is-cached-and-filters-never-build.md`). The differential spec `harness/graph/graph_incremental_heavy_spec.py` (heavy tier, 482bb82bc) shows today's `Graph.refresh` equals a fresh build for only 4 of 17 edits (TypeScript class change, renamed TypeScript operation steps invoke, sample scenario file, observed examples). The 13 that fail come down to these faults:
   - Every refresh of a story file drops stories that are in scenario files but not on the story map (54 nodes).
   - Every refresh flips the BDD spec `subject` of `graph_spec.py` and `saved_graph_spec.py`.
   - Refreshing a Python file leaves model-document-only nodes with a stale `written_in`.
   - Module facts (`public_source_files`, `imported_classes_by_file`, `sibling_imports`, `holds_production_code`) are not recomputed on an add, delete or rename; a delete leaves a stale `conforms-to-schema` violation.
   - A renamed class heading in a `*-model.md` leaves the code class's old `written_in`, base and association edge.
   - Renaming a Python operation that steps invoke leaves `model_written: false` on 54 Then steps.
   - A renamed bounded context loses 4 `owns`/`belongsTo` edges to unchanged aggregates.
   - A renamed TypeScript file changes DDD's `unresolved_calls_otherwise` (2, not 3).
   - `dependencies_to_own` order differs.

   No production code is changed yet; fixes wait for approval.
2. **Repin the dev lane after the pml-web demo**, then check live.

## Waiting on a repin to be seen live

- format chips
- board sends
- robot rows and themes (`prompt-queue.set_theme` reaches the server only then)
- + then send
- explorer class card and realizations
- draw.io and whiteboard links
- Files app file menu and All files
- the new practice rules

## Standing rules from the person

- Don't touch pml-web's files or boards.
- pml-web runs on the dev lane: never repin or restart during its demos.
- Practice roots take files and folders.
- Realizations are code-like statements.
