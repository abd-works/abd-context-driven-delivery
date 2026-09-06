# Generate — drawio-story-sync

## What this skill owns

- Python package **`drawio_story_sync/`** (under `scripts/`) — DrawIO story map render, layout extraction, and update-report generation (story diagrams only).
- CLI **`scripts/drawio_story_sync_cli.py`**: `render`, `save-layout`, `report`, **`apply-report`**, **`sync`** (outline → graph + refresh companion diagrams).

## Story diagram kinds

| Workflow | `renderer_command` | CLI `--mode` aliases | Default output file |
| --- | --- | --- | --- |
| Outline | `render-outline` (default) | `outline`, `story-map` | `story-map.drawio` |
| Acceptance Criteria | `render-exploration` | `acceptance-criteria`, `exploration` | `acceptance-criteria.drawio` |
| Thin-slicing | `render-increments` | `thin-slicing`, `increments`, `prioritization`, `thin-slices` | `thin-slicing.drawio` |

## Dependencies (PYTHONPATH)

1. **This skill's `scripts/` directory** (so `import drawio_story_sync` works).
2. **story-graph-ops** `scripts/` — auto-prepended by `drawio_story_sync._bootstrap` when the sibling skill exists at `skills/supporting/story-graph-ops/scripts`.

DrawIO code imports **`story_graph_ops`** from **story-graph-ops**: `StoryMap`, `Epic`, `SubEpic`, `Story`, `StoryGroup`, `StoryNode`, `DomainConcept`, `StoryUser`, etc.

## story-graph-ops integration

- **`load_story_graph_json`** calls **`story_graph_file.load_story_graph_dict`** when **story-graph-ops** is importable, so the same walk validation applies before building `StoryMap`.

## Commands

```text
python drawio_story_sync_cli.py sync --drawio <path/story-map.drawio> --graph <path/story-graph.json>
python drawio_story_sync_cli.py render --mode outline            --graph <path/to/story-graph.json> --out <path/story-map.drawio>
python drawio_story_sync_cli.py render --mode acceptance-criteria --graph ... --out <path/acceptance-criteria.drawio>
python drawio_story_sync_cli.py render --mode thin-slicing        --graph ... --out <path/thin-slicing.drawio>
python drawio_story_sync_cli.py save-layout --drawio <path/file.drawio>
python drawio_story_sync_cli.py report --drawio <path/file.drawio> --graph <path/story-graph.json> [--scope "Node Name"]
python drawio_story_sync_cli.py apply-report --graph <path/story-graph.json> --report <path/*-update-report.json> [--dry-run]
```

### `sync` (preferred for outline edits)

Use **`sync`** when the **outline** diagram is the source of truth for hierarchy/story renames **and**, where the diagram is explicit, for **personas** (`users`).

1. Runs the same **report** diff as `report` (writes `<stem>-extracted.json`, `<stem>-update-report.json`, updates `*-layout.json`). After a successful apply (not `--dry-run`), those three stem sidecars beside the synced diagram are **removed**.
2. **Applies** the report to **`story-graph.json`** (same as `apply-report`). Personas: chips above story columns set explicit persona; following stories inherit until the next explicit chip.
3. Re-renders **`acceptance-criteria.drawio`** and **`thin-slicing.drawio`** next to the outline so exploration/increment views match the graph.

Optional: `--no-refresh-diagrams`, `--out-exploration` / `--out-increments`, `--dry-run`, `--scope`.

**Do not** chain `apply-report` from multiple diagrams unless exploration/increments already match the graph — use **`sync`** instead.

`report` writes `<stem>-extracted.json` and `<stem>-update-report.json` beside the diagram.

`apply-report` loads the report JSON and applies it with **`story_graph_ops.StoryMap.apply_update_report`**, then saves `story-graph.json` (unless `--dry-run`).

## Agent checklist

1. Put **this** `scripts/` and **story-graph-ops** `scripts/` on `PYTHONPATH` (or rely on sibling auto-insert).
2. When the user edits the **outline** DrawIO and wants JSON + other diagrams aligned, run **`sync --drawio <outline> --graph <story-graph.json>`**.
3. Run **`story_graph_cli.py read --file story-graph.json`** from **story-graph-ops** after graph writes.
4. For merges from a **single** report file only (no companion refresh), use **`apply-report`**.

## Tests (acceptance shape)

Tests under `tests/drawio_story_sync/` follow **abd-story-acceptance-test**: epic folder **`drawio_story_sync`**, files **`test_*.py`**, shared helpers in **`drawio_story_sync_helper.py`**. After **`sync`**-driven graph writes, assert **`story_graph_cli.py read`** succeeds when that CLI is present.

## See also

- **story-graph-ops** — canonical read/write/validate for `story-graph.json`.
- [`../../../reference/diagram-workflow.md`](../../../reference/diagram-workflow.md) — practice-level Draw.io overview.
