# Story-Driven Delivery — Diagram Workflow (shared)

Draw.io story diagrams render from `story-graph.json` via **drawio-story-sync**. Skills that produce diagrams ship `reference/diagram-workflow.md` with their **mode** and output path; this file owns the shared CLI.

**Prerequisites:** `story-graph.json` must exist (**story-graph-ops**). The `.drawio` file must exist on disk before the CDD cell is marked done.

**CLI:** `drawio_story_sync_cli.py` from `practices/story-driven-delivery/skills/supporting/drawio-story-sync/scripts/`.

---

## Render from graph

```bash
python drawio_story_sync_cli.py render \
  --mode <mode> \
  --graph docs/stories/story-graph.json \
  --out   docs/stories/<output>.drawio
```

| Skill | `--mode` | Default output |
| --- | --- | --- |
| `abd-story-mapping` | `outline` | `story-map.drawio` |
| `abd-story-acceptance-criteria` | `acceptance-criteria` | `acceptance-criteria.drawio` |
| `abd-thin-slicing` | `thin-slicing` | `thin-slicing.drawio` |

Run once after `story-graph.json` is in place for the current fidelity level.

---

## Sync diagram edits back to graph

When the user edits the **outline** story map diagram:

```bash
python drawio_story_sync_cli.py sync \
  --drawio docs/stories/story-map.drawio \
  --graph  docs/stories/story-graph.json
```

For **thin-slicing** or **acceptance-criteria** as the edited diagram, use the same command with `--diagram-type thin-slicing` (or `acceptance-criteria`) and the matching `.drawio` path. See **drawio-story-sync** `SKILL.md` for companion re-render behaviour.

After any graph write, run **`story_graph_cli.py read --file story-graph.json`** from **story-graph-ops**.
