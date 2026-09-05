# Input traps — miro-story-sync

Pre-flight only — not grill questions.

- **Token missing** — Is `MIRO_ACCESS_TOKEN` set for real-board writes, or did you intend `--dry-run`?
- **PYTHONPATH** — Are `common/`, this skill's `scripts/`, and **story-graph-ops** `scripts/` importable?
- **Graph not validated** — Will you run **`story_graph_cli.py read`** before and after graph-affecting operations?
- **Transport choice** — Is `RestMiroTransport` appropriate, or should this run use in-memory dry-run validation first?
- **Planned parity** — `report` / `apply-report` / `sync` are not yet shipped; do not assume drawio-story-sync commands work here without checking CLI help.
