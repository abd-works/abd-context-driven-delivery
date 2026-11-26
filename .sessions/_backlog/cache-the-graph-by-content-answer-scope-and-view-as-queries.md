# Cache The Graph By Content, Answer Scope And View As Queries

Recommended 2026-11-16 in the file-manager chat. Today `SessionExplorer.graph_trees` (space/session/session_explorer.py) calls `graph.load_files` on every request, so every chip press in the Files app (stage, practice, format, Changed/All) re-parses every listed file: 10-20 s of "Reading the session's graph" per toggle. Four dimensions drive the graph's answers and each should invalidate only its own layer: content (a file's text), links and rules (cross-file edges, facts, rule results), scope (which files are in play), and view (node filter, opened branch, node lines).

## Layers

1. **Per-file parse cache, keyed by content**: key = path + git blob id (or a content hash for a dirty file) + the practice reader/format version; value = the file's SavedNodes and facts. On disk (e.g. `~/.cdd/cache/parse/`), shared across worktrees and lanes. Needs a CDR amending harness/graph's "no file-change detection" rule: a blob key asks git what a file is; it watches nothing and compares no dates.
2. **One resident session graph, maintained by refresh**: holds the union of every file any scope asked for; grows when a list names new files, never rebuilt for a filter change. `graph_trees(paths)` = ensure those paths are held (cache hits are near free), then filter. `refresh(paths)` stays the only way content changes.
3. **Links and rules updated only where changed**: a reverse-dependency index (file -> nodes -> edges); on refresh recompute only those files' nodes, the edges touching them, and the CDR 0004 facts of their practices. Rule results cached by (node fact checksum, rule, overlay set, fidelity stage): an overlay change reruns only its rules; a stage change only stage-reading rules such as conforms-to-schema.
4. **Scope and view as index lookups, versioned**: per graph version, id-set indexes by path (with the ancestor closure of bea33125b), practice, type, violation, relationship kind; a filter is their intersection. Memoize explorer_trees / explorer_branch / graph_node_ranges keyed by (graph.build.changed version, normalised filter), small LRU; send the version to the page as an ETag so the Files app skips refetching when only the view changed.

## Invalidation

| Event | Parse cache | Session graph | Links / rules | View memo |
|---|---|---|---|---|
| Scope toggle | - | add unseen files | - | new key |
| View change | - | - | - | new key |
| refresh(paths) | new blobs | drop + re-add those files | dependents only | version bump |
| Overlay change | - | - | affected rules only | version bump |
| Branch switch / pull | old blobs still hit | rebuilt from hits | re-link; rules reused by fact checksum | version bump |

## Order

1. Stop `graph_trees` reloading: resident union graph plus filtering (biggest win, no cache needed).
2. Index-based filtering and the versioned memo: chip toggles become instant.
3. Blob-keyed parse cache with its CDR: fast first loads and branch switches.
4. Rule cache by fact checksum and overlay set; re-link only dependents on refresh.

Each step proven by a timing story test, e.g. "Toggling the Specification stage answers the graph view within 1 second on file-manager's files".
