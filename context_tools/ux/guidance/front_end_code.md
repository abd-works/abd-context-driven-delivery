# UX — Procedural Guidance (front_end_code fidelity)

## From mockup to production frontend

This fidelity is about real shipping UI, not enhanced greybox. The thinking shift:

1. **Replace stubs with real clients** — routing, state management, API calls, authentication. The mockup's faked behaviors become real service integrations.
2. **Wire to real backend** — CE code-fidelity backend with Production collaborators. Not Fake factory, not in-browser demo domain.
3. **Story Demo is now a companion, not the product** — the Story Demo shell may still exist for review/exploration, but it's not the shipping UI.
4. **Carry forward all IA decisions** — layout vocabulary, control decisions, screen decomposition from earlier fidelities are still authoritative. Don't re-decide screens under a new product name.

## What "real frontend" means

A vertical is NOT at code fidelity while it depends on:
- A mockup/Story Demo shell as the only UI
- In-memory or fake factories as the only "backend"

Code means real backend AND real frontend — not greybox + demo domain alone.

## Host framework awareness

At this fidelity, the host app's frontend stack takes over (React, Vue, Angular, vanilla). The IA and mockup decisions inform component structure and routing, but the implementation uses the real framework's patterns.
