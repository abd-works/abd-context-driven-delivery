# Rule: Decision prompts for increments

Before locking increments, answer **why this order** and **what you are optimizing**. Use the prompts below (from prioritization guardrails) as a checklist; capture conclusions in **slicing notes** or team docs.

## Questions to settle

- Which map areas carry the most **business or delivery risk**?
- Which areas deliver the most **value if shipped early**?
- Which are **complex relative to value**?
- Should thin slices be as **end-to-end** as possible? (Default for this skill: **yes**, unless constraints say otherwise.)
- What must be **reused** across many stories—validate that **early**?
- What **program constraints** (compliance, date, dependency) force order?
- Which **users or segments** must go first so others can follow?

## Thin-slicing dimensions (how you make a slice thinner)

Pick explicitly when useful: **users** (role/context first); **workflow** (simple path before variants); **interfaces** (one channel first); **data variations** (one type first); **environment** (one deployment context); **business rules** (subset of rules first); **subjective quality** (lower NFR bar for early adopters); **spike** (throwaway learning).

## How increments are grouped (strategy options)

Examples: **end-to-end journey**; **validate impact / feasibility**; **maximize earned value**; **increase reuse / reduce dependency risk**; **quick win**; **validate impact** with users (Wizard of Oz, landing page, stubs, etc.).

## What value this increment optimizes

Examples: **end-to-end journey**; **earned value for a bounded capability**; **quick win**; **stakeholder validation**.

## Earliest uncertainty to validate

Examples: **architecture / reuse**; **impact** (do users care?); **operations** (deploy, monitor, support); **system integration** (external APIs, partners).

## DO

- Tie **Increment 1** to the **riskiest** or **most informative** uncertainty you can address in a **short vertical** slice.
- State **which dimension** you sliced on when it helps stakeholders reason about scope.

## DON'T

- Sequence increments only by **component build order** with no **outcome** or **learning** rationale.
- Skip **stakeholder-visible** naming—prompts should surface in **increment titles** and **outcomes**, not stay in a private worksheet only.
