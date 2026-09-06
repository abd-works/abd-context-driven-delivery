# Generate — abd-ux-information-architecture

## Read before generating

Read these files in full before generating. Do not skip any file.

- **`reference/concepts.md`** — core IA dimensions (navigation + content), screen/transition/layout/tab-state definitions, content types, story and domain term traceability rules, mental model alignment, canvas layout convention, and CLI layout templates.
- **`reference/examples.md`** — worked example of a good initial IA showing tab-state decomposition, representative rows, verb rows, chrome conventions, and story budget.
- **`reference/aria-pipeline.md`** — ARIA fidelity model, input resolution (extractor → IA), structural fidelity rules, `aria.yaml` output format, and two-pass rendering protocol.

## Output shape

**Deliverables folder:** resolve via [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md) § Output file resolution.

**File names:** `information-architecture.md` (structured spec), `information-architecture.drawio` (diagram), and one `screens/<screen-slug>.aria.yaml` per screen — all in `docs/ux/information-architecture/`. See [`common/reference/folder-conventions.md`](../../../../common/reference/folder-conventions.md).

| Template | What to produce |
| --- | --- |
| `templates/initial-ia.md` | Structured spec: scope, source paths, screen flow map, screens (regions, content types, actions, stories, domain terms), transitions, navigational components, content-type details. |

## Generation flow (16-step build)

**Input resolution (before step 1):** Check whether `docs/extracted-context/from-application/pages/<slug>/aria.yaml` exists for any in-scope screen. If found, use as structural seed per `reference/aria-pipeline.md`; otherwise construct from story map and domain language.

1. Resolve inputs: story map, scope filter, Domain Language file.
2. Filter story map by scope; read the Domain Language.
3. Identify screens by tab state (N tabs = N screens). Check ~4 story budget per screen.
4. Walk every story — produce a **story trace table** (story → screen → region → action/trigger). Every cell must be filled before proceeding.
5. Walk every in-scope domain term — produce a **domain term trace table** (term → appears as → on screen → in region).
6. Identify transitions with labeled triggers.
7. Identify navigational components in UX terms.
8. Identify content types with hierarchy, collections, key actions.
9. Lay out content per screen as rows (representative data rows + verb row), not prose.
10. Draft labels and tags.
11. **Write `docs/ux/ia/<screen-slug>.aria.yaml`** for each screen at structural fidelity. Use `reference/aria-pipeline.md` for the fidelity rules and output format. One file per screen slug.
12. Author the **Screen flow — complete connection map** section of `docs/ux/initial-ia.md`: one ASCII block showing navigation components (drawer nav, secondary nav, etc.) then each screen → [type] action → destination screen, using the format in `templates/initial-ia.md`.
13. Author the rest of `docs/ux/initial-ia.md` from the template.
14. Run the completeness test from `rules/tab-states-and-domain-traceability.md` — fix gaps before touching the canvas.
15. **Pass 1 — Structure from ARIA:** Choose output mode (Mode A: `drawio-ux` CLI; Mode B: filled prompt for external AI) and produce `initial-ia.drawio` driven from the `aria.yaml` trees. Map landmarks to layout regions, navigation links to site-map arrows, primary actions to verb rows. Save. The CLI `save` command always writes **two pages**: Page 1 — Detailed IA (full screen layouts); Page 2 — Site Map (one box per screen, arrows only).
16. **Pass 2 — Annotate:** Add yellow stories boxes and green domain terms boxes alongside each screen in the drawio. Update the story-trace and domain-term-trace tables in `initial-ia.md`. No layout changes in this pass. Save.

Diagram commands: [`reference/diagram-workflow.md`](diagram-workflow.md).
