# UX context — Story Demo shell (Manage Character Sheet)

Optional notes not shown on screens. Locked from grill + `connected-contexts`.
Primary sketch: `story-runner-sketch.md` (themes; ce → bdd → ux).

## Invariants (by concern)

**Shell**
- `StoryDemoFrame` LEFT + `ExplorerFrame` RIGHT (epic → story → scenario → steps).
- Two modes of the same shell: **Play** and **Interactive** (separate screens in the sketch).
- UX Story Demo submodule: `StoryDemoPage` / `StoryDemoFrame` / `ExplorerFrame` / `StoryDemoControl`.
  Vanilla `Page` / `Control` stay product UX (no `bound_field` / `story_steps`).
- `PlayDualRunner` lives under UX `story-demo/play-dual-runner/`.

**Play**
- `PlayDualRunner.collect(create{Story}Story, mode)` then `start` / `playNext`.
- Same step `fn`s as node tests; story declares GWT only — runner owns `steps[]`.
- **Only explorer Play next invokes Play** — product `StoryDemoControl`s are not triggered.
- After each `playNext`: `step.fn()` → `PaintReflect` / `StoryDemoFrame.bind(expose())` via `bound_field` → emphasize via `story_steps` (kind+label) → if Then, `ThenFeedback`.
- Stories mode wiring as is: `create{Story}Story(mode)`; `helper.given*({ mode })` only inside step fn bodies.

**Paint vs Then**
- `PaintReflect` → `StoryDemoFrame.bind(snapshot)` — controls update from `bound_field`; do not own domain.
- `ThenFeedback` → Explorer mark/message + `StoryDemoFrame.tintFailed` — peer to paint.
- Emphasize: explorer owns step list; `StoryDemoFrame` matches `story_steps` to current step kind+label.

**StoryDemoControl bindings**
- `bound_field` — what to display from expose.
- `story_steps` — which GWT steps this control participates in (emphasize in Play; which When `fn` to run in Interactive).
- `interactions[]` — trigger (click/hover/drag/…) + effect — not click-only; product controls do not call `playNext`.

**Interactive**
- Same `StoryDemoFrame`; Given already applied.
- `StoryDemoControl.Interaction` → `whenStep` from `story_steps` → `whenStep.fn()` → bind.
- Control does **not** call `helper.given*` — that stays inside the When fn. No ThenFeedback. No `playNext`.

**Product**
- Updating an Ability rank leaves the Character sheet consistent.

## Notes

- Fidelity: **mockup** — greybox; Play, emphasize, Then fail message/tint visible; no brand.
- Demo subject: Manage Character Sheet — Create Character · Update Ability Rank.
- Product IA for the sandbox epic: `sandbox/play-core-mechanics/.context/` (separate).
- Implemented: UX `story-demo/` (shell + `play-dual-runner/`); `ux_model.StoryDemoControl` + HTML emit; JS hydrate. Engagement shell under sandbox.

## Same folder

- `story-runner-sketch.md` — **primary** Story Demo sketch (integrated)
- `ux-model-sketch.md` — vanilla Control + StoryDemoControl.bound_field / story_steps
