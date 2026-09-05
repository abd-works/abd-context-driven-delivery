### Rule: Mechanisms are discovered from the system, not copied from a standard list

The mechanisms named in the outline come from analysing **this system's actual recurring patterns** — its surrounding-systems table, the code it already runs (or will run), the real NFRs the team has accepted, and the shapes that will repeat across many components. The standard vocabulary (Security, Error Handling & Resilience, Logging & Observability, Validation, Configuration & Secrets, Caching, Persistence, Communication) is a **discovery prompt** — "do we need this here? if yes, what does it look like in this system?" — not a checklist to fill in. A mechanism survives in the catalogue only if you can name its principle, pattern, technology, and instances from this system's reality. Passing means a reviewer can hold the outline and the codebase side-by-side and see every mechanism reflected in real or planned code. Failing means a mechanism is in the catalogue because "every system has one" rather than because this system has one.

#### DO

- Walk the eight standard mechanisms as discovery prompts. For each, ask: does this system have this pattern recurring across multiple components? If yes, include it. If no, omit it.

  **Example (pass):** For a stateless proxy midtier — Security (yes, every protected route checks a JWT), Error Handling (yes, every controller funnels into the same `handleError` translator), Logging (yes, every entity creates its own scoped logger), Configuration (yes, every service reads from a central env module), Caching (no, no data stored or cached), Persistence (no, no database owned), Validation (merged into Authentication — single principle), Communication (renamed System Entity Controllers — every external connection follows one controller-per-entity pattern).

- Add bespoke mechanisms when this system has a recurring shape the standard vocabulary does not name. The bespoke entry must satisfy the same bar: principle, pattern, technology, instances.

  **Example (pass):** *System Entity Controllers* as a bespoke mechanism — the principle "no route handler calls an external SDK directly" and the pattern (one controller class per external system) recur across Mavenir, Zoho, Persona, Fygaro, Voucher. The standard vocabulary's "Communication" did not capture this shape.

- When you omit a standard mechanism, leave the reason discoverable in the outline so blueprint work does not silently re-add it.

  **Example (pass):** "Caching and Persistence are omitted — this system is a stateless proxy that owns no data store and maintains no cache. If a future story introduces a data-owning entity, this catalogue is updated first."

#### DO NOT

- Reproduce the eight-mechanism list because "every architecture document has these sections" — without checking whether each one names a real pattern in this system.

  **Example (fail):** A stateless proxy outline includes a `### Persistence` subsection that says "no persistent storage at this time; future enhancements may include a database." There is no pattern, no instance, no principle — the entry exists to fill a slot. It belongs in the omitted-mechanisms note, not in the catalogue.

- Invent a mechanism that the codebase, the surrounding-systems table, or the NFRs do not call for.

  **Example (fail):** Adding *Multi-tenancy* to a single-tenant system because "we might go multi-tenant someday." That decision belongs in a deferred-decisions log; the outline catalogues what is true now (and the immediately foreseeable shape), not aspirations.

- Use a standard mechanism name when the system's actual shape needs a different name. Renaming is part of discovery, not a stylistic choice.

  **Example (fail):** Naming the section *Communication* when every component in the system uses the same controller-per-entity proxy pattern. *Communication* hides the shape; the right name is *System Entity Controllers* (or whatever the team calls the pattern in conversation), and that name carries the principle and pattern with it.

**Source:** Practice-skill authoring convention (abd-architecture-outline); mirrors the specification skill's "grounded in the architecture's source of truth" — at outline fidelity the source of truth is this system's real patterns, surrounding-systems table, and accepted NFRs, not a generic catalogue every project inherits.
