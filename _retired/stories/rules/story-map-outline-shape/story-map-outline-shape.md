---
rule: story-map-outline-shape
fidelity: [shaping]
artifact: [story-map]
---

# Rule — Story Map Outline Shape

At shaping fidelity the story map is an **outline**, not a fully decomposed map.

## Required

1. **Every epic has an estimate** — a `* approx N–M total stories` line sizing all work under it.
2. **Every sub-epic has an estimate** — a `* approx N–M more stories` line sizing unmapped work in that sub-epic.
3. **Map is not fully decomposed** — at least one sub-epic must be estimate-only (no named stories), confirming shaping depth rather than discovery depth.

## Violations

| Violation | Meaning |
| --- | --- |
| Epic missing estimate | Every epic needs `* approx N–M total stories` |
| Sub-epic missing estimate | Every sub-epic needs `* approx N–M more stories` |
| All sub-epics fully named | If every sub-epic has stories and none is estimate-only, the map is at discovery depth |

## Good example (shaping)

```
(E) Move money
    * approx 22-27 total stories
    (E) Compose transfer
        (S) Treasurer --> Draft transfer details
        * approx 2-3 more stories (select source account, enter destination)
    (E) Approve transfer
        * approx 4-6 more stories (review, approve, reject)
    (E) Route transfer
        (S) Treasurer --> Route transfer before cutoff
        * approx 2-3 more stories (fraud routing, settlement window)
    (E) Track transfer
        * approx 2-3 more stories (view pending, approved, settled, rejected)
```

## Bad example (discovery depth disguised as shaping)

```
(E) Move money
    (E) Compose transfer
        (S) Treasurer --> Draft transfer details
        (S) Treasurer --> Enter destination account
        (S) Treasurer --> Enter amount
    (E) Approve transfer
        (S) Approver --> Review transfer
        (S) Approver --> Approve transfer
        (S) Approver --> Reject transfer
```

No estimates anywhere, every sub-epic fully named — this is discovery depth.
