# lib

Shared Python for **story-driven-delivery** diagram backends.

## diagram_story_sync/

Platform-agnostic layout, geometry, comparison, and abstract diagram nodes.

**Used by:**

- `skills/drawio-story-sync` — DrawIO XML backend
- `skills/miro-story-sync` — Miro REST API backend

## PYTHONPATH

Backend `_bootstrap.py` modules prepend:

1. `story-driven-delivery/lib/` (or `.cursor/lib/` when deployed)
2. `story-driven-delivery/skills/story-graph-ops/scripts/`
