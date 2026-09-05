# Rule: Template uses the source spec's placeholder vocabulary verbatim

Every placeholder in `template/` and `templates/tests/` MUST appear in the source `architecture-context.md` § Canonical Patterns or § File Structure verbatim, and every placeholder used MUST be declared in `parameters.json`. The placeholder vocabulary is the **contract** between the spec and the template; if the template invents `{Thing}` while the spec uses `{Feature}`, `abd-architecture-code` cannot map between them and readers cannot trust either document. Failing this means a spec author writes `{Feature}` in the spec, opens the template package expecting to see `{Feature}` in `template/`, finds `{Thing}` instead, and now has to maintain a mental translation table forever.

## DO

- Copy the placeholder vocabulary from the source spec verbatim — same name, same casing, same brace style.

  **Example (pass):** Source spec § Canonical Patterns uses `{System}`, `{operation}`, `{Domain}`. `template/` uses the same three tokens in the same form. `parameters.json` declares all three.

- Declare every placeholder in `parameters.json` with a `bindsTo` and `scope`.

  **Example (pass):**
  ```json
  { "name": "{System}", "bindsTo": "partner system name (PascalCase)", "scope": "both", "example": "ExampleCoPartner" }
  ```

- When the source spec is ambiguous about a placeholder (used inconsistently between File Structure and Class Specification), stop and route back to the spec author. Do not pick.

  **Example (pass):** Source File Structure shows `{System}Handler.ts`; Class Specification shows `class {Partner}Handler`. The skill reports drift and asks the spec author which token to keep. No work proceeds until the spec is consistent.

- Add placeholders the source spec does not name only when authoring the test scaffolds (e.g. `{epicSlug}`, `{subEpicSlug}`) — and only when the test-helpers context file defines them. Declare them in `parameters.json` with `bindsTo` matching the helpers context file.

  **Example (pass):** Test-helpers context file's folder structure uses `{epicSlug}` and `{subEpicSlug}` for sub-epic-per-file mapping. `templates/tests/` uses both, declared in `parameters.json` with `scope: filename`.

## DO NOT

- Invent a placeholder the source spec does not use.

  **Example (fail):** Source spec uses `{Domain}` everywhere. Template uses `{Domain}` and `{Aggregate}` — `{Aggregate}` was added because "it makes the example feel more DDD". `abd-architecture-code` has nothing to bind `{Aggregate}` to; the bound version under `example/` either falls back to `{Domain}` (defeating the addition) or hard-codes a value (defeating templating).

- Normalise a placeholder's casing or brace style.

  **Example (fail):** Source spec uses `{System}` (PascalCase, single braces). Template normalises to `{{system}}` (camelCase, double braces) "for consistency with Handlebars". The two documents no longer talk about the same thing.

- Use a placeholder in `template/` without declaring it in `parameters.json`.

  **Example (fail):** `template/{System}Handler.ts` contains a call to `{validator}.run(...)`. `parameters.json` declares `{System}` only. `abd-architecture-code` substitutes `{System}` correctly but leaves `{validator}` as-is, producing code that does not compile.

- Use placeholder syntax in `example/`.

  **Example (fail):** `example/{System}Handler.ts` exists. `example/` is the bound version — placeholders are forbidden there. (See [`./template-is-runnable.md`](./template-is-runnable.md).)

- Lift a placeholder from a different mechanism's spec because it "would also fit here".

  **Example (fail):** The Caching mechanism's spec uses `{Tenant}`. The Partner Integrations template adopts `{Tenant}` for multi-tenancy support that nothing in the Partner Integrations spec mentions. The template now overreaches the spec; future readers cannot tell which placeholders are authoritative.

**Source:** Practice-skill authoring convention (abd-architecture-template). The vocabulary chain — outline → blueprint → spec → template → code — only works if each link uses the previous link's words verbatim.
