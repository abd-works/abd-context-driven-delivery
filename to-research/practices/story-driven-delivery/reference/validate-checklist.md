# Story-Driven Delivery — Shared Validate Checklist

Apply these items during [`common/reference/rule-checklist.md`](../../../common/reference/rule-checklist.md) for every SDD practice skill.

---

## All SDD practice skills

- **No bundle markers** — `SKILL.md` has no `<!-- execute_rules:bundle_rules -->` markers.
- **Template instructions omitted** — generated project files contain stakeholder-facing content only; no `## Instructions` blocks copied from `templates/`.
- **Story-graph parity** — when `story-graph.json` exists, story names in markdown artifacts match the graph character-for-character (including parenthetical qualifiers).

---

## Diagram skills (mapping, AC, thin-slicing)

- **Diagram on disk** — the `.drawio` file named in `reference/diagram-workflow.md` exists before the cell is marked done.
- **Graph readable** — `story_graph_cli.py read --file story-graph.json` succeeds after graph writes.

---

## Cross-perspective

- **Incomplete context** — gaps surfaced honestly; no fabricated structure to fill holes. See [`handling-incomplete-context.md`](./handling-incomplete-context.md).
- **System mode** — new-system vs existing-system discipline applied. See [`new-vs-existing-system.md`](./new-vs-existing-system.md).
