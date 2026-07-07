---
rule: story-map-shape
kind: shape
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: story-map.md
scanner: story-map-shape-scanner.py
---

# story-map-shape

A `story-map.md` MUST have the fundamental Patton-style skeleton: at least one
outcome, at least one activity, at least one story, and at least one actor named.
Without these, downstream artifacts (thin-slice, scenarios, tests) have nothing
coherent to trace back to.

## The rule

1. Exactly one top-level heading (`#`) naming the map.
2. At least one **Outcome** at `##` level.
3. At least one **Activity** at `###` level (nested under an outcome).
4. At least one **Story** as a bullet under an activity.
5. At least one **Actor** named somewhere in the file (either in an `## Actors`
   section or as bold `**Actor:**` prefixes on stories).

## DO

- Put outcomes at `##`, activities at `###`, stories as `-` bullets.
- Name actors explicitly: an `## Actors` section listing them, or `**Actor:**`
  in front of each story.

## DON'T

- Do not use flat lists of stories with no outcome/activity grouping.
- Do not omit actors — anonymous "the user" hides variance between roles.

## Example — pass

```markdown
# Cash Management Story Map

## Actors
- Treasurer
- Approver

## Outcome: Move money on the same day

### Activity: Initiate a same-day transfer
- **Treasurer:** Enter a same-day transfer
- **Treasurer:** Confirm cutoff time
- **Approver:** Approve the transfer
- **Treasurer:** See settlement confirmation
```

## Example — fail

```markdown
# Cash Management

- Enter transfer
- Approve
- See confirmation
```
(No outcome, no activity, no actors.)

## Cross-references

- `four-to-nine-children` — this shape rule only requires ≥1 child at each level;
  four-to-nine-children enforces the tighter 4–9 count once the shape exists.
- `artifacts-mirror-story-hierarchy` — downstream folders mirror this hierarchy.
