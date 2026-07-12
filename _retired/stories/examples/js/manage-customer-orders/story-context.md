# Manage Customer Orders

**Status:** partially expanded

**Stories in scope:**
- *Place New Order*
- *Track Order Status*
- *Cancel Order*

**Context / notes:** Epic-root aggregate for the JavaScript code-example tree that mirrors `examples/md/story-map.md`, `examples/ts/manage-customer-orders/`, and `examples/py/manage-customer-orders/`. Spec files use JSDoc `@type` annotations in place of TypeScript's `as const satisfies Story` — the shape contract is enforced at runtime by `story-runner.js`, which validates every step key against the tier dispatch table. Folder structure and story data are identical to the TypeScript examples; only the file extensions and type annotations differ.
