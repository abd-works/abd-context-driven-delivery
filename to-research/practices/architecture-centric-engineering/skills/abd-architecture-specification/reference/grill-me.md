# Grill me — abd-architecture-specification

Ask each question visibly, then answer it yourself from the available context. Only surface a question to the user when no source can answer it.

- **Existing codebase** — answer from code. Read repetition (sibling skeletons), surface (public exports), consumers (imports), entry point, composition wiring, what is reachable vs orphaned. Escalate to the user only when the code is silent: unwritten team rules, intent behind legacy folders, capabilities not wired through the visible entry point.
- **New system** — no code exists yet; the user is the primary source. Ask requirement and pattern questions that let them describe the architecture they want. Do not invent.

Goal: fill the classification table ([`discovery.md` Step 6](./discovery.md#step-6-tabulate)) and the Where to Start rows. Surface evidence; do not ask the user to pick a tier.



## Existing codebase — questions to ask and answer from code

- Does the composition root import repeating-pattern folders — and do those folders share the same internal skeleton?
- Are there sibling subfolders with 3+ files of the same shape? (templated pattern → mechanism)
- What does each folder's public surface look like — one coherent API, named operations, or unrelated utilities?
- Who imports each folder — many callers, one consumer, or nobody alive?
- What is reachable from the entry point vs orphaned (dead or legacy)?
- Are there capabilities not wired through the visible entry (background jobs, queue consumers, separate processes)?

Escalate to the user only for:

- Unwritten rules a new engineer must follow that no code enforces.
- Intent behind folders that look dead but may be deliberately preserved.
- Where the current shape disagrees with how the team wants the system to work.



## New system — ask requirements and pattern questions

The architecture is a consequence of requirements plus the patterns the team wants to use. Drive both.

**Requirements**

- What does this system own, and what does it explicitly NOT own?
- What systems does it talk to inbound and outbound — and how many of each kind do you expect at first ship vs over time?
- Which capabilities repeat across those systems (per partner / per tenant / per region) and which are one-offs?
- What identity, failure, and observability behaviour must be uniform across every entry path?
- What must be replaceable later (which adapter could be swapped) and what is allowed to be load-bearing?

**Pattern preferences**

- Where one capability has many instances (partners, integrations, feature modules), is each instance a copy of a fixed skeleton, or free-form?
- For shared concerns (identity, failure handling, logging, config), should there be one wired-in mechanism or one helper consumers reach for?
- Are adapters wrapped (one module per external system) or invoked directly from feature code?
- Should domain types live with the feature that uses them, in a shared module, or in their own boundary?
- What does the team copy when they add the next instance of the most common pattern?



## When the decision tree still doesn't settle a folder

Pick the matching pair; ask the requirement/pattern version, not a tier-vote.

**Mechanism vs package** — *is there a recipe?*

- Will (or does) every new instance follow the same skeleton, or does each grow its own shape?
- Is there a must/must-never rule that constrains every instance?
- Would you tell a new engineer "copy that one"?

**Package vs miscellaneous (tiny)** — *is the surface coherent and worth a page?*

- Named operations for different situations, or one entry point everyone calls the same way?
- Could two engineers reasonably pick different operations and that matters?
- More than two sentences to describe what it does?

**Miscellaneous-tiny vs grab-bag** — *one purpose or mixed?*

- Same purpose throughout, or things that didn't fit elsewhere?
- Are deprecated or legacy entries mixed in with live ones?

**Dead code** — *still load-bearing?*

- If deleted tomorrow, what breaks?
- Has something else replaced this?
- Last meaningful change — feature work or just upkeep?



## Where to Start (for the central spec)

Frame as **feature requirements**, never as code artefacts — [`rules/where-to-start-routes-by-feature-need.md`](../rules/where-to-start-routes-by-feature-need.md).

- What kinds of feature requests does the team receive (or expect to receive) most often?
- For each, what business question had to be answered before anyone knew where to work?
- Which capabilities recur — new integration, new credential, new identity rule, new failure mode, new tenant?

Answers feed [`discovery.md` Step 6](./discovery.md#step-6-tabulate).
