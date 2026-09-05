# Rule: Template stays in sync with the source spec

A template package is a **mirror** of one specific mechanism's `architecture-context.md`. Every participant in `template/`, every test tier in `templates/tests/`, every bullet in `rules/` MUST trace verbatim to its source — File Structure, Class Specification, Canonical Patterns, Rules sections of the named mechanism. Re-running the template skill must produce a drift report whenever the source has changed, and must never silently overwrite. Failing this means the template package becomes a second, divergent source of truth; readers reading the spec generate code one way, readers reading the template generate it another, and `abd-architecture-code` produces output that nobody recognises.

## DO

- Lift participant filenames and identifiers from § File Structure and § Class Specification verbatim.

  **Example (pass):** Source spec lists `{System}Handler.ts`, `{System}Payload.ts`, `{System}.config.ts` under File Structure. `template/` has exactly those three files with exactly those three names.

- Lift Rules into `rules/<kebab-name>.md` files one per bullet, preserving the rule statement and rationale.

  **Example (pass):** Source spec § Rules has the bullet *"**Every handler registers in the composition root** — registration is the only way a partner is reachable; missing registration is dead code."* The template package has `rules/every-handler-registers-in-the-composition-root.md` with the same statement and rationale plus DO / DO NOT examples.

- Surface drift on re-run as a structured report.

  **Example (pass):** Re-running against a package whose source spec has added a new `{System}Telemetry.ts` participant produces a report: `+ template/{System}Telemetry.ts (new participant in source spec)`. The skill asks the user to confirm before writing the new file.

## DO NOT

- Invent a participant the source spec does not name.

  **Example (fail):** Source spec lists three participants. Template package contains four — the fourth (`{System}Validator.ts`) was added because "every handler should have one". The spec did not say so; the template now teaches a pattern the spec does not authorise.

- Rename a placeholder.

  **Example (fail):** Source spec uses `{System}`. Template uses `{Partner}` because "it reads better in this codebase". `abd-architecture-code` now has to maintain a translation table to follow the spec; readers comparing the two get confused.

- Edit a Rule's text on the way into `rules/`.

  **Example (fail):** Source spec § Rules says *"Handlers MUST NOT call other handlers directly."* Template `rules/handlers-do-not-call-other-handlers.md` says *"Handlers SHOULD avoid calling other handlers."* This is now a separate, weaker rule. The spec author cannot find their own words.

- Silently overwrite on re-run.

  **Example (fail):** Source spec adds two participants. The skill re-runs and replaces `template/` wholesale, including reformatting the existing participants. The drift report is never shown; manual fixes inside the existing files (formatting, comments) are lost.

- Treat the template as authoritative when the spec changes.

  **Example (fail):** A reader notices a Rule in `rules/` that no longer matches the source spec and updates `rules/` to match a different design they prefer, without updating the spec. The template is now ahead of the spec; the next re-run will surface this as drift in the *opposite* direction and confuse everyone. The fix is always in the spec first, then mirror.

**Source:** Practice-skill authoring convention (abd-architecture-template). The template is a faithful renderable of the spec; if it diverges, the spec stops being the source of truth.
