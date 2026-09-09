# CDD — Procedural Guidance (shared)

## Think in lenses, not steps

CDD orchestrates multiple practice lenses (Stories, DDD, UX, Clean Engineering, BDD) across delivery stages. The key insight: these lenses look at the same thing from different angles. They are not sequential steps — they are concurrent perspectives.

- **Stories** — the interactions lens: who does what, in what order, with what variations?
- **DDD** — the domain lens: what are the language boundaries, consistency clusters, and business rules?
- **UX** — the experience lens: what does the user see, how do they navigate, what controls do they use?
- **Clean Engineering** — the structure lens: what modules exist, how do they relate, what are the public seams?
- **BDD** — the object behavior lens: what does each domain thing do when tested?

## Sketch first, then deepen

Every engagement starts with a sketch file (`cdd-sketch.md`). One file per engagement, deepened in place as fidelity increases. The sketch groups lens blocks under themes (epics, modules, user goals).

Key thinking:

1. **Grill before sketching** — ask clarifying questions per theme. What's the scope? What are the boundaries?
2. **Scaffold before content** — read the sketch template and each active child's sketch template before writing. Don't dump free prose.
3. **All lenses in the same file** — lens blocks for a theme sit beside each other, not in separate files. This forces comparison.

## Views must agree before proceeding

After sketching any lens, ask: does this raise questions another lens would answer? If Stories shows a flow that DDD hasn't modeled, sketch the DDD view before moving on. Only when all active views agree, deepen to the next fidelity or move to the next theme.

This is the agreement check — the reason CDD exists instead of running each tool independently.
