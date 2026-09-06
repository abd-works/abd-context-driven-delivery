# Generate — abd-ux-mockup

## Read before generating

Read these files in full before generating. Do not skip any file.

- **`reference/concepts.md`** — what a mockup is, source IA, design image reference, UI element types and state formats, field input types, domain terms and AC verbatim rules, the shape of a good state file, rendering approach (CLI vs AI-crafted XML), mxGraph XML patterns, and CLI reference.
- **`reference/aria-pipeline.md`** — ARIA fidelity model, input resolution (IA → mockup), promotion rules (structural → detailed), `aria.yaml` output format, and two-pass rendering protocol.

## Output shape

See [`reference/output.md`](output.md).

| Template | What to produce |
| --- | --- |
| `templates/ux-mockup.md` | Structured spec: screen name, source paths, layout, design reference catalog, regions with affordance traces, in-scope stories, domain terms (verbatim), and AC (verbatim) |

## Generation flow

**Input resolution (before step 1):** Check whether `docs/ux/ia/<screen-slug>.aria.yaml` exists for the in-scope screen. If found, use as the structural base and promote to detailed fidelity per `reference/aria-pipeline.md`. If not, construct the detailed tree from `initial-ia.md` and the design image catalog.

1. **Agree scope** — which screens, stories, or epics are in scope.
2. **Resolve inputs** — path to `docs/ux/initial-ia.md`, UL file, AC file, agreed screens/stories.
3. **Reference design images** — read ALL design images in `Design/` folders; catalog UX elements per screen.
4. **Read in-scope screens from the initial IA** — layout, regions, stories, domain terms.
5. **Collect in-scope stories and AC.**
6. **Write `docs/ux/mockups/<screen-slug>.aria.yaml`** — promote the structural ARIA tree (or construct from IA) to detailed fidelity using the promotion rules in `reference/aria-pipeline.md`. Every control must have exact type, all live states, and required relationship attributes.
7. **Build the state JSON** — derive `<screen-slug>-state.json` from the detailed `aria.yaml`, mapping each ARIA node to the correct element type matching the design image.
8. **Pass 1 — Render wireframe:** Generate the wireframe via `scripts/drawio-mockup.mjs` driven from the state JSON. Save.
9. **Write `mockup.md` alongside the wireframe** — under each screen heading list:
   - **Stories:** every in-scope user and system story for that screen, verbatim from the story map (`(U)` / `(S)` prefix · Epic → Story title)
   - **Domain terms:** every domain term visible on that screen, verbatim from the Domain Language file, as a `·`-separated inline list
   - **AC:** every acceptance criterion for in-scope stories, verbatim.
10. **Pass 2 — Annotate:** Add yellow stories box and green domain terms box beside each screen in the drawio. No wireframe layout changes in this pass. Save.

Diagram commands: [`reference/diagram-workflow.md`](diagram-workflow.md).
