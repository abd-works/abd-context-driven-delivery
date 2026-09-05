# Input traps — drawio-story-sync

Pre-flight only — not grill questions.

- **Wrong sync path** — Did you chain `apply-report` from stale exploration/increment diagrams instead of using **`sync`** from the outline?
- **Graph not validated** — Did you skip **`story_graph_cli.py read`** after writing `story-graph.json`?
- **PYTHONPATH missing** — Can `import drawio_story_sync` and `import story_graph_ops` both succeed?
- **Persona inheritance** — When syncing personas from outline chips, did you apply the same forward-fill model the renderer uses?
- **Companion diagrams stale** — After outline sync, will acceptance-criteria and thin-slicing diagrams be re-rendered unless `--no-refresh-diagrams` was intentional?
