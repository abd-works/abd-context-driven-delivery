---
fidelity: [shaping, discovery]
artifact: [story-map]
scanner: brownfield-story-mapping
kind: quality

---

# Rule: Brownfield story mapping

When the source is **existing code, an existing product, or an observed running system**, the story map records **what the system does**, not what it *should* do. Reshape and redesign happen in a separate slice, driven by evidence.

Two failure modes to avoid:

1. **Silent redesign** — the map replaces observed behaviour with idealised behaviour, and the delta is invisible
2. **Deferred-gap dumping** — observed mechanics are labelled "not yet supported" or "gap" instead of being mapped

## DO

- Map every observed behaviour as a story under the right activity — even if you think it's wrong or badly designed
- Cite the code path, endpoint, screen, or observation next to each brownfield story
- Record disagreements as **observed quirks** in the story itself (see `document-observed-quirks.md`), not as deletions
- Keep a `## Redesign candidates` list separate from the map — never edit the map to reflect a proposed redesign
- When the code and the interview disagree, map both and flag the conflict

## DON'T

- "Improve" a story name to describe the redesigned behaviour — this hides the delta
- Label a working behaviour as a "gap" or "deferred" because it's inconvenient — if the system does it, map it
- Combine two distinct behaviours in the code into one story just because they *should* be one
- Drop stories that describe legacy or awkward behaviour — legacy behaviour is behaviour

## The two failure modes

### Silent redesign

```
Observed in code: POST /payments rejects payment when account.status == "FROZEN"
                  POST /payments rejects payment when account.balance < amount

Wrong — mapped as one idealised story
- Story: Payment is rejected when account cannot cover it

Correct — both observed mechanics mapped, quirks recorded
- Story: Payment is rejected when account is Frozen
  _Evidence: src/payments/api.ts:47_
- Story: Payment is rejected when balance is insufficient
  _Evidence: src/payments/api.ts:52_
  _Observed quirk: rejection message does not distinguish this from "frozen"_
```

### Deferred-gap dumping

```
Observed in code: partial refunds work only via /admin/refunds, not /refunds

Wrong — dumped as a gap
- Story: Full refund via /refunds
- Gap: Partial refunds not supported

Correct — mapped where it lives
- Story: Full refund via /refunds
- Story: Partial refund via admin endpoint
  _Evidence: src/admin/refunds.ts_
  _Observed quirk: exposed only under /admin, not the public API_
```

## Evidence formats accepted

- **Code path:** `src/payments/api.ts:47`
- **Endpoint / route:** `POST /payments`
- **Screen / component:** `PaymentSubmitForm.tsx line 82` or `Payments → Submit`
- **Runtime observation:** `curl POST /payments {…} → 400 "insufficient funds"`
- **Test citation:** `test/payments/submit.spec.ts § "rejects on frozen account"`

Every brownfield story cites at least one. If none is available, mark the story `_Evidence: **UNVERIFIED**_` and treat it as speculative until confirmed — see `story-map-discipline.md`.

## Where redesign lives

Redesign proposals live in a **separate document** (`redesign-candidates.md` or an ADR), not in the map. When a redesign is approved and scheduled, it becomes new stories in a *future* thin-slice increment with clear before/after wording.

## Cross-references

- `story-map-discipline.md` — evidence and scope rules that this rule specialises for existing code
- `document-observed-quirks.md` — how the observed-but-wrong / observed-but-surprising details get recorded on the story
- `thin-slice-ordering.md` — redesign slices are scheduled here, not applied to the map
