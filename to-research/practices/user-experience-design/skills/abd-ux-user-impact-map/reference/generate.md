# Generate — abd-ux-user-impact-map

## Read before generating

- **`reference/concepts.md`** — what an impact map is, goal/actor/impact/deliverable definitions, goal and impact metrics, assumptions (build and outcome types), phased backlogs, and the shape of a good map.
- **`reference/examples.md`** — a worked hierarchy example (live-ops product) showing nested goals, actors, impacts with metrics, and phased deliverables.

## Output shape

**Deliverables folder:** resolve via [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md) § Output file resolution.

**File name:** `impact-map.md` (and paired outputs). Add a `<name>-` prefix only when disambiguation is needed.

| Template | What to produce |
| --- | --- |
| `templates/impact-map.md` | Hierarchy view: broader to finer `GOAL:` levels, then ACTOR / IMPACT / DELIVERABLE; optional `METRIC:` under goals and impacts; optional phased table. |
| `templates/impact-map.txt` | Same hierarchy tree and phased TSV (if any) as plain text. |
| `templates/impact-map-ascii.md` | ASCII wall sketch (four columns): OBJECTIVE (Why?) \| PERSONA (Who?) \| IMPACT (How?) \| INITIATIVE (What?). |
| `templates/impact-map-ascii.txt` | Same four-column table as plain text. |
| `templates/impact-map-hypotheses.md` | Build and outcome hypothesis sentences: same facts as the tree. `Then` clause uses goal as verb phrase with metric. |
| `templates/impact-map-hypotheses.txt` | Same hypothesis shape as plain text. |

## Parity

Within each pair (hierarchy, ASCII, hypotheses), the `.md` and `.txt` versions match. Across all six files — same goal stack, actors, impacts, deliverables, and phased items. Impacts stay behavioural; each deliverable supports one impact; hypothesis lines use the same names as the hierarchy view.

## Quality bar

Match the concepts in `reference/concepts.md` for structure. Use `rules/*.md` for generative wording (goal, impact, actor, deliverable, assumptions, phased backlog Actor / impact column).

**Depth:** Do not emit only Markdown or only plain text unless the user explicitly asks for a single format.
