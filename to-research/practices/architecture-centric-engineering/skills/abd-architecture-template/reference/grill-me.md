# Grill me — abd-architecture-template

**Mechanics:** [`common/reference/grill-me-with-practice-skill.md`](../../../../../common/reference/grill-me-with-practice-skill.md) — one question at a time; generate-to-learn when enough is shared.

Ask until the source mechanism is template-ready, the placeholder vocabulary is locked, and the sentinel binding is unambiguous:

- Which mechanism is the canonical one for this project? If you picked `project` mode, why is this mechanism the right one to scaffold — what makes it more instantiated or more central than the others?
- Is the source `architecture-context.md` complete? Specifically: does its File Structure show every participant file, does its Class Specification cover every public method of the central type, and does its Canonical Patterns block compile mentally?
- What placeholders does the source Canonical Patterns use? Are they consistent across File Structure (filenames) and Class Specification (identifiers)?
- What sentinel are you binding placeholders to in `example/`? Does it collide with any real feature, real partner, real product? If a reader confused the sentinel for a real thing, what could go wrong?
- What language and toolchain does `example/` need to be runnable under? What is the existing project command to build and to test? If you cannot name those commands now, the example will not be verifiable.
- What test tiers does the test-helpers context file define, and does `templates/tests/` need to mirror all of them, or only some?
- Which rules from § Rules in the source spec are mechanism-specific (belong in the template package) versus project-wide (belong elsewhere)? Are any of them inferred from prose rather than stated explicitly?
- If you re-ran the skill against this package six months from now, what would change in `template/`? What would change in `example/`? What user edit to `example/` should survive a re-run?
- In `mechanism` mode: how does the code skill discover which template package to use for a given story? Is the central spec's Where-to-Start row for this mechanism going to carry the link?
