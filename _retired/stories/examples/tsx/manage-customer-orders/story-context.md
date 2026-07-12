# Manage Customer Orders

**Status:** partially expanded

**Stories in scope:**
- *Place New Order*
- *Track Order Status*
- *Cancel Order*

**Context / notes:** Epic-root aggregate for the TSX code-example tree. Spec files (`*-stories.ts`) are **identical** to `examples/ts/manage-customer-orders/` — the TSX backend shares the same TypeScript spec-file format. The distinction between `ts` and `tsx` only appears at the tier layer: client-tier files use the `.tsx` extension (e.g. `submit-order-client.test.tsx`) because they render React components. Everything else — story constants, `story-types.ts`, `story-runner.ts` — is the same as the TS family.
