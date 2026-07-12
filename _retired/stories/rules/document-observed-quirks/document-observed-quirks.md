---
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: [story-map, thin-slice, story-scenarios, story-tests]
scanner: observed-quirks
kind: shape

---

# Rule: Document observed quirks and context gaps

When source material is **incomplete**, **contradictory**, or **surprising**, the artifact records the anomaly *inside itself* — not on a side-list, not in a chat thread, not in the author's head.

Two kinds of anomaly:

1. **Context gap** — something is missing from the source (a behaviour is implied but not specified, an actor is not named, a boundary is undefined)
2. **Observed quirk** — something is present in the source but behaves surprisingly (a legacy oddity, a naming mismatch, an inconsistent error path)

Neither one causes the artifact to stop. Both must be **visible on the artifact**.

## DO

- Add `## Context gaps` on any story, scenario, or test whose source material is incomplete — describe what is missing and what was assumed
- Add `_Observed quirk:_ …` next to the item that behaves surprisingly, inline, next to the citation
- Cite the source of the gap or quirk (interview reference, code path, observation)
- Carry the gap or quirk forward — a gap noted at discovery must remain visible at specification and engineering until it is closed
- Close a gap by editing the artifact to replace the gap note with the confirmed answer, citing the source that closed it

## DON'T

- Silently fill in a missing detail with a plausible assumption — the assumption must be labelled
- Delete a quirk because it "shouldn't be like that" — quirks describe reality (see `brownfield-story-mapping.md`)
- Move gaps to a separate tracking document — they belong on the artifact so the reader sees them in context
- Let a gap disappear as fidelity deepens without being closed or restated

## Formats

### Context gap on a story

```markdown
### Story: Customer submits payment from partner API

_Evidence: existing endpoint POST /api/v2/payments_

## Context gaps
- **Rate limits per partner** — endpoint enforces a global limit; per-partner limits mentioned in interview §5 but no rule found in code
- **Idempotency key required?** — header is accepted but not documented; interview did not cover it
```

### Observed quirk inline

```markdown
- **System rejects payment when Amount exceeds daily Limit**
  _Evidence: src/payments/api.ts:52_
  _Observed quirk: rejection returns HTTP 400 with generic message "invalid payment" — does not distinguish limit-exceeded from other invalid states_
```

### Gap on a scenario

```gherkin
Scenario: Refund a settled Payment
  Given a settled Payment of $100
  When the Merchant issues a refund of $60
  Then a Partial Refund is recorded

# Context gap: refund window (how long after settlement) not defined in source; assumed 90 days
```

### Gap on a test

```typescript
it('refunds a partial amount within the refund window', async () => {
  // Context gap: refund window not documented; hardcoding 90 days per assumption in scenario
  const settledAt = daysAgo(30);
  ...
});
```

## Carrying gaps forward

- A gap opened at **shaping** appears on the outcome or activity until discovery closes or refines it
- A gap opened at **discovery** appears on the story until exploration closes or refines it
- A gap opened at **exploration** appears on the scenario until specification closes it
- A gap that survives to **engineering** must be either resolved before test-writing, or marked with a `@gap` tag / skipped test that names it

## Closing a gap

When a gap is answered:

1. Remove the `## Context gaps` bullet or `_Observed quirk:_` note
2. Add the confirmed detail into the artifact body
3. Cite the source that closed it: `_Confirmed: Interview 2026-07-01 with Ops Lead §2_`

Do not silently delete gaps — the closure must be traceable.

## Cross-references

- `story-map-discipline.md` — evidence rules; gaps are what happens when evidence is incomplete
- `brownfield-story-mapping.md` — observed quirks are the brownfield-specific version of this rule
- `revising-story-map.md` (behavior) — when accumulated gaps signal a bad structure, the map itself needs revising
