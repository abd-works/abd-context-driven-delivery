# story-demo

UX Story Demo: shell (`StoryDemoPage` / frames / controls) + `play-dual-runner/`.

## Seam

Callers load a story via `StoryDemoPage.load(createStory, mode)`, Play via explorer `playNext`, Interactive via `StoryDemoControl` `story_steps` → When `fn`.

**Model:** Python `ux_model.StoryDemoControl : Control`. HTML emits `data-bound-field` / `data-story-steps` / Interactive extras. JS hydrates via `fromElement`.

**Bound lists (generic):** `[data-bound-list]` + `data-bound-field` (expose array path). Optional:
- `data-item-story-steps` — shared When; row click runs When (`input` via `data-set-input` / `data-item-value`)
- `data-set-input` alone — row selects only; a button When reads `input(...)`
- `data-item-label` — `{field}` template for row text

**Interactive inputs:** `data-input-field` / `data-set-input` → `input(key, default)`.

**Interactive session:** mount keeps expose domain (`cart`, `product`, …) across story switches; stories use `session("cart", () => factory…)`. Reset clears session.

**Interactive story jump:** control When label → owning story on the map, then run When.

**Runner:** `play-dual-runner/` (same UX Story Demo package — not Stories).

Constraint: vanilla `Control` has no `story_steps`. HTML imports `story-test-core` only.

Worked UX example (not part of this package): `contexts/ux/examples/manage-customer-orders/`.

Engagement wire (e.g. Create Character HTML) lives under `sandbox/…`.
