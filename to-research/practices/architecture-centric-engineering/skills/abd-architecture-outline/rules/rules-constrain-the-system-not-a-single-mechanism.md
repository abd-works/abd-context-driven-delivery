### Rule: Rules in the Rules section constrain the system, not a single mechanism

The Rules section catalogues **system-wide invariants** — constraints that apply across every package, every mechanism, every entity. A rule that only applies inside one mechanism is a **principle of that mechanism** and belongs in the mechanism's own subsection, not in the Rules section. The split keeps the Rules section short and reviewable (a reviewer can hold the list in working memory) and keeps each mechanism self-contained (its principle travels with its pattern and instances). Passing means every entry in the Rules section is a stance the whole system takes; a reviewer can apply each rule to a pull request in *any* package and get a clear yes-or-no. Failing means the Rules section is a dumping ground for mechanism details, restates content that already lives in a mechanism subsection, or contains rules that only one part of the system has any business honouring.

#### DO

- A rule in the Rules section must be applicable to a pull request in any package. The verifying surface (a layer, a folder, a naming convention) crosses the whole system.

  **Example (pass):** "Config is read once at startup — no `process.env` access outside the environment module." This applies to every package, every entity, every utility. A reviewer can grep `process.env` across the whole repo.

- When a constraint applies only inside one mechanism, move it to that mechanism's **Principle** line and remove it from the Rules section.

  **Example (pass):** "JWT validation happens before any handler runs." This is the Authentication mechanism's principle, not a system-wide rule. It lives in `### Authentication` under **Principle**, not in section 6.

- Keep the Rules section short — 5–8 entries is the working range. If the list grows past 10, some entries are probably mechanism principles in disguise.

  **Example (pass):** Seven rules in the Rules section. A candidate eighth ("controllers may not catch errors except to translate them into `Err`") is moved to the Error Handling mechanism's principle line, leaving the system-wide list at seven.

#### DO NOT

- Restate a mechanism principle as a system-wide rule, producing two places where the same constraint lives.

  **Example (fail):** Section 4.2 says "Every protected route validates a JWT before any handler runs." Section 6 says "JWT validation is mandatory on protected routes." When the constraint changes (e.g. token format upgrade), the author updates one and forgets the other.

- Put implementation detail of a mechanism into the Rules section.

  **Example (fail):** "Use `CognitoService.verify()` from `lib/auth/cognito.ts` for token validation; configure the client in `src/lib/auth/index.ts`." This is mechanism implementation detail, not a system-wide rule — it belongs in the Authentication mechanism's Pattern paragraph.

- Add rules that only one package or entity is expected to honour.

  **Example (fail):** "The Mavenir controller may not call PowerTranz directly; all FAC calls go through the FacIframeService." This is a constraint *inside* the Mavenir entity, not a system-wide stance. It belongs in that entity's per-folder `architecture-context.md` at specification fidelity, or in a Mavenir-specific subsection — not in the top-level Rules section.

**Source:** Practice-skill authoring convention (abd-architecture-outline); mirrors the specification skill's "include Instantiating the Domain section" — content belongs in the right place. The Rules section catalogues what the whole system commits to; each mechanism owns its own principle. Mixing them produces drift and dilutes both.
