# UX — Procedural Guidance (shared)

## Think in screens, not features

A screen is a coherent user goal — one thing the user is trying to accomplish. Not a feature list, not a component library, not a page in the app's routing table.

Key thinking:

1. **Each screen answers one question** — "What am I looking at?" "What can I do here?" If a screen tries to answer three different questions, it's probably three screens.
2. **~4 user stories per screen** — this is the budget. If a screen serves more stories than that, it needs decomposition. Fewer is fine.
3. **Tab states are separate screens** — if a tab shows fundamentally different content with different interactions, it's a separate screen that shares chrome with its siblings.

## Name screens in domain language

Screen labels come from the domain, not from technical or chapter labels. "Browse Catalog" not "ProductList." "Verify Identity" not "KYCForm." If domain language exists (from DDD or Stories), the screen name traces to it.

## Invariants and context notes

Things that aren't visible on screens but constrain the UX (business rules, interaction constraints, timing dependencies) go in `ux-context.md`. This is the same role as `story-context.md` or `module-context.md` — notes the visual artifact can't express.
