---
scanner: live-and-dead-code-distinguished
---

### Rule: Every folder shown is either tagged with its owning unit or marked dead/legacy

Source Layout MUST tag every folder in the tree either with the mechanism or package it implements, OR with `[dead code]` / `[legacy]` for folders that exist on disk but are not reachable from the system's entry point (whether reached via composition-root wiring, framework auto-discovery, or consumer import of an inherited base class). A folder shown without a tag reads as live architecture; if it is in fact orphaned, the spec actively misleads engineers and AI assistants into treating dead code as load-bearing. Documentation that cannot distinguish living code from rotting code is worse than no documentation. Passing means a reader scanning the tree can tell, for any folder, whether it is part of the running system. Failing means dead folders sit in the tree untagged or share the same visual weight as live ones.

#### DO

- Tag every shown folder, using the mechanism/package name when live and `[dead code]` / `[legacy]` when not.

  **Example (pass):**
  ```
  src/
  +-- composition.ts           <- composition root
  +-- integrations/            <- inbound adapters per partner     [Partner Integrations]
  +-- adapters/
  |   +-- OutboundClient/      <- HTTP client                       [OutboundClient]
  |   +-- Logging/             <- log sink                          [Logging]
  +-- legacy-billing/          <- replaced integration              [dead code]
  +-- types/                   <- old type definitions              [legacy]
  ```

- Verify dead/legacy tags from reachability: trace imports from the entry point (or discovery globs, or known consumers for inheritance-style mechanisms); folders not reached are dead.

  **Example (pass):** `legacy-billing/` is not imported anywhere reachable from `composition.ts` → tagged `[dead code]`. `types/` is imported only by `legacy-billing/` → also dead but kept for git history → tagged `[legacy]`.

- Use `[dead code]` for folders that should be deleted; use `[legacy]` for folders deliberately preserved for reference or rollback.

  **Example (pass):** "`old-zoho-client/` — replaced by `/src/adapters/Zoho/`; kept until 2026-Q4 deletion window. [legacy]"

#### DO NOT

- Show an orphaned folder as if it were live.

  **Example (fail):**
  ```
  src/
  +-- types/                   <- type definitions
  ```
  `types/` is in fact only imported by deleted code; new engineers will read it as the system's type library and add to it.

- Tag a live folder with a vague label that hides which mechanism owns it.

  **Example (fail):**
  ```
  +-- setup/Identity/          <- identity setup            [utility]
  ```
  `Identity Setup` is the mechanism; tagging it `[utility]` severs the mapping to the Mechanisms section.

- Use the tags as decoration without verifying reachability.

  **Example (fail):** Every folder gets `[live]` because the author has not checked imports; a year later half are dead.

**Source:** Code archaeology — a tree shown without distinguishing live from dead encourages every future engineer to extend dead code, doubling the rot.
