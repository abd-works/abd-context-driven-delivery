# powers

Shared base for all power effects: compose, cost, descriptors, and activate protocol. Owns **Effect**. Sheet ownership: effects belong on character; resolve paths use checks. Typed children nest under this module (containment).

## Modules fidelity

### Module `powers`

- **Purpose:** Own the shared Effect seam so typed power children and gear can specialize without sibling deps.
- **Seam (terms):** Effect
- **Dependencies (one-way):** `character`, `checks`
- **Build order:** see `sandbox/.context/sessions/discovery/module-build-order.md`
