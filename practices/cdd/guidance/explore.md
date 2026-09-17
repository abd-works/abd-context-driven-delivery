# CDD — Procedural Guidance (explore fidelity)

## How to run explore

Explore deepens one increment or a large subsection. The scope narrows from discovery:

1. **Pick the increment** — which thin slice or sub-epic are you exploring?
2. **Deepen each active lens** — from discovery's thin output to richer detail:
   - Stories → exploration (scenarios per story)
   - DDD → building_blocks (stereotypes and classifications)
   - UX → mockup (wired controls and interactions)
   - Clean Engineering → model (empty public seams)
   - BDD → behavior (describe/it hierarchies with SIGNATURE markers)

## Cross-lens reconciliation thinking

Explore is where the lenses really need to agree:

- **Does every story scenario trace to a domain operation?** If a scenario step can't map to a named operation in the DDD/CE model, that's a gap in one of the models.
- **Does every screen control correspond to a story interaction?** If a mockup has a button that no story covers, either the story is missing or the control is invented.
- **Does every domain aggregate have stories that exercise it?** An aggregate with no story coverage is either premature or missing stories.

Reconcile in the same pass, not in a separate "alignment" step.

## BDD enters at explore

This is the first stage where BDD becomes active. The behavior hierarchies should align with what Stories and DDD have already named — the subjects are the domain concepts, the states come from the lifecycle, the conditions come from the scenarios.
