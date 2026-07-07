# Manage Customer Orders

**Status:** partially expanded

**Stories in scope:**
- *Place New Order*
- *Track Order Status*
- *Cancel Order*

**Context / notes:** Epic-root aggregate for the Python code-example tree that mirrors `examples/md/story-map.md` and `examples/ts/manage-customer-orders/`. Story data is pure data (dicts and tuples) so a code adapter can read it without importing a test framework. Folder names follow the kebab-case slug convention used across the code family; the epic helper is the sole snake_case exception because Python's import system does not accept hyphens in module names — see `stories/src/formats/code/architecture-context.md`.
