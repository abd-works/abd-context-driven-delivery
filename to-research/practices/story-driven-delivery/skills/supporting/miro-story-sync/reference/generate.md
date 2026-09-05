# Generate — miro-story-sync

## What this skill owns

- Python package **`miro_story_sync/`** (under `scripts/`) — Miro-specific story node hierarchy, transport abstractions, and story-map orchestrator.
- CLI **`scripts/miro_story_sync_cli.py`**: `render` (today; `report` / `apply-report` / `sync` planned — mirror **drawio-story-sync**).

## Story diagram kinds

| Workflow | `renderer_command` | CLI `--mode` aliases | Output role |
| --- | --- | --- | --- |
| Outline | `render-outline` (default) | `outline`, `story-map` | Epic / sub-epic / story map |
| Exploration | `render-exploration` | `exploration`, `acceptance-criteria` | Outline plus AC boxes (planned) |
| Prioritization | `render-increments` | `increments`, `prioritization`, `thin-slices` | Outline base plus increment lanes (planned) |

## Dependencies (PYTHONPATH)

1. **`common/`** at the repo root (so `import diagram_story_sync` works).
2. **This skill's `scripts/`** (so `import miro_story_sync` works).
3. **story-graph-ops** `scripts/` — same domain types as **drawio-story-sync**.

All three are auto-prepended by `miro_story_sync._bootstrap` and `miro_story_sync_cli.py` when the standard monorepo layout is present.

## Transport options

| Transport | Use case | Auth / state |
| --- | --- | --- |
| **`RestMiroTransport`** | Production. Miro v2 API items API. | `MIRO_ACCESS_TOKEN` env var; board ID in CLI. |
| **`InMemoryMiroTransport`** | Tests and `--dry-run`. | None — no network. |

## Common module

Imports from `common/diagram_story_sync` — geometry, layout, comparison, `UpdateReport` re-export from `story_graph_ops`. `MiroEpic` / `MiroSubEpic` / `MiroStory` subclass common diagram types.

## Commands

```text
python miro_story_sync_cli.py render --mode outline --graph <story-graph.json> --board <BOARD_ID>
python miro_story_sync_cli.py render --mode outline --graph <story-graph.json> --dry-run
```

`--dry-run` swaps in `InMemoryMiroTransport`. Without `MIRO_ACCESS_TOKEN`, `render` falls back to dry-run.

## Agent checklist

1. Put **`skills/story-analysis/common/`**, this skill's **`scripts/`**, and **story-graph-ops** `scripts/` on `PYTHONPATH` (or rely on auto-bootstrap).
2. Set `MIRO_ACCESS_TOKEN` for real-board writes.
3. Use `--dry-run` for local validation without network.
4. Run **`story_graph_cli.py read --file story-graph.json`** from **story-graph-ops** before / after graph-affecting operations once `report` and `apply-report` ship.

## Tests (acceptance shape)

Tests under `tests/miro_acceptance/` follow **abd-story-acceptance-test**. Connectivity uses **`LocalMiroServer`** — real HTTP to loopback, production `RestMiroTransport` unaltered. See skill `tests/miro_acceptance/local_miro_server.py`.

## See also

- **drawio-story-sync** — sibling skill rendering the same model to DrawIO XML.
- **story-graph-ops** — canonical read/write/validate for `story-graph.json`.
- [`../../../reference/diagram-workflow.md`](../../../reference/diagram-workflow.md) — practice-level diagram overview.
