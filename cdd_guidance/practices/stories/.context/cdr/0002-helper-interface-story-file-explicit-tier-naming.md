# Story file declares a helper interface; every tier is named explicitly

`{story}_story.<ext>` (scenario fidelity, no suffix) now declares one
helper-interface method per distinct Given/When/Then clause and wires
`story()`/`scenario()` blocks that call those methods only — no assertions, no
tier mechanism, no ExampleFactory import in the story file itself. Every tier
implements that interface in `{story}_test_helper.{tier}.<ext>` and calls
`create{Story}Story(new TierHelper())`. `{tier}` is always named explicitly —
including the baseline (`domain`) — there is no implicit no-suffix tier file.
`{tier}` is project-specific (`domain | client | server | e2e`, or another
layer the AI chooses from context, e.g. `api`, `db`), matching how `Tier` is
already modeled as a discovered, not fixed, value on `SubEpic.testSuites`.

This formalizes a pattern that was already validated by hand in
`story-ui/stories` before the tool caught up to it (see
`AssignStoryToIncrementHelper`, `BrowseStoryHierarchyHelper`) — the tool's
scaffolder previously emitted a `mode: string` parameter
(`fake | isolated | production`) with assertions inlined directly into the
story file, which the hand-authored story-ui files had already abandoned in
favor of a per-story helper interface implemented once per tier.

## Considered Options

- **Mode-string story file + isolated/production spec split** (previous,
  `0001`'s follow-on) — rejected: the story file still owned assertions and an
  implicit no-suffix tier, blurring "scenario fidelity, tier-neutral" with
  "acceptance-test fidelity, tier-specific"; every tier past `isolated`/
  `production` needed a special case in the scaffolder.
- **Helper interface in the story file + explicit `_test_helper.{tier}`
  per tier** (chosen) — the story file is a pure seam declaration (interface +
  wiring); every tier file is symmetric (implements the interface, no
  no-suffix special case); tier vocabulary generalizes past isolated/
  production to the project's real architectural layers.

## Language notes

- JavaScript has no static interfaces — the seam is documented via a JSDoc
  `@typedef` and enforced only by duck-typing the helper parameter.
- Python declares the interface as a `typing.Protocol`; the story file returns
  a `{test_name: fn}` dict that each tier file binds at module scope via
  `globals().update(...)` so pytest discovers the generated test functions.
- Java's file-name-matches-class-name rule cannot use a literal `.` before the
  tier segment, so the tier PascalCase is concatenated onto the class name
  (`{Story}TestHelper{Tier}.java`) instead of dot-separated — the same kind of
  per-language naming exception as the existing Python snake-case epic helper.
