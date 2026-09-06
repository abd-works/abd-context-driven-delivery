# Concepts — abd-architecture-template

> **Practice-level model:** [`../../../reference/architecture-context-model.md`](../../../reference/architecture-context-model.md). This skill consumes the spec-fidelity content the specification skill writes, and produces the runnable scaffold the code skill instantiates.

## What a template package is

A **template package** is a self-contained directory that pairs three things in one place:

1. A **runnable parameterized reference module** (`template/`) — real source files in the project's actual stack, named with placeholders (`{System}`, `{Feature}`, `{DomainName}`) that match those used in the source mechanism's Canonical Patterns verbatim.
2. **One concrete instantiation** of that module (`example/`) — same files, with placeholders bound to a sentinel name (e.g. `PartnerA`), that compiles and whose tests pass under the project toolchain.
3. The **rules** (`rules/`) and **test scaffolds** (`templates/tests/`) needed to instantiate a new feature against the template.

A template package is the answer to the question "*what does a new instance of this mechanism look like in code?*" — expressed as code you can copy, not prose you have to interpret.

## Why a separate skill

The specification skill writes the **design** (Class Specification, File Structure, Rules, Canonical Patterns as markdown). The template skill writes the **scaffold** (real runnable code embodying that design). The two have different cadences:

- The spec is updated whenever the mechanism's design evolves (often, story-driven).
- The template is updated whenever the recipe itself changes (rarely, decision-driven).

Keeping them separate means the spec can churn without forcing a code rewrite, and the template can be rebuilt without rewriting the spec.

## Two modes

| Mode | Output location | Scope |
|---|---|---|
| `project` *(default)* | `docs/architecture/templates/<project-slug>/` | One template package per project, covering the project's primary (most-instantiated) mechanism. Matches the legacy reference-application shape — catalog-hero, Recipients, hero-vtt, MERN-domain-first all worked this way. |
| `mechanism` *(opt-in)* | `docs/architecture/templates/<mechanism-slug>/` | One template package per named mechanism. Run the skill once per mechanism. Use when the project has multiple mechanisms whose recipes diverge enough that a single shared scaffold loses fidelity. |

Both modes produce the same internal package structure (`README.md`, `template/`, `templates/tests/`, `example/`, `rules/`, `parameters.json`). Only the location and the choice of which mechanism to scaffold differ. Choosing `mechanism` mode and re-running per mechanism produces N peer packages under `docs/architecture/templates/`.

## Package structure (both modes)

```
docs/architecture/templates/<slug>/
├── README.md
├── parameters.json
├── template/
│   ├── {participant-1}.{ext}
│   ├── {participant-2}.{ext}
│   └── ...
├── templates/
│   └── tests/
│       ├── {epicSlug}.domain.test.{ext}
│       ├── {epicSlug}.server.test.{ext}
│       └── ...
├── example/
│   ├── <sentinel-name>/
│   │   └── ...                       (a concrete bound instantiation)
│   └── tests/
│       └── ...                       (concrete tests; pass under the project toolchain)
└── rules/
    ├── <rule-1>.md                   (lifted verbatim from source architecture-context.md § Rules)
    └── ...
```

### `template/`

Real source files in the project's actual language and toolchain. Filenames and identifiers use placeholders (`{Domain}`, `{Feature}`, `{System}`) that **match the source mechanism's `architecture-context.md` § Canonical Patterns verbatim**. The `template/` directory is what `abd-architecture-code` copies and renames; it does not compile on its own (placeholders are not valid identifiers) — that is intentional.

### `templates/tests/`

Parameterized test files, one per tier defined by the test-helpers package-tier `architecture-context.md` (typically `tests/<helpers>/architecture-context.md`). Folder structure and helper naming mirror that file exactly. Test files use the same placeholder vocabulary as `template/`.

### `example/`

A concrete instantiation of `template/` with placeholders bound to a sentinel name (a real but unused-by-real-features value — e.g. `PartnerA` for a Partner Integrations template). The `example/` directory **compiles and its tests pass** under the project toolchain. This is the "runnable proof" that the template is not just decorative.

### `rules/`

The mechanism's Rules section from `architecture-context.md`, lifted into one file per rule. The code skill reads these via `<spec-root>/rules/` exactly as it always has. Lifting them here (rather than referencing the markdown) keeps the template package self-contained — `abd-architecture-code` only needs the template package path; it does not need to navigate back to the central spec for rules.

### `parameters.json`

Declarative list of every placeholder the template defines:

```json
{
  "placeholders": [
    { "name": "{Domain}", "bindsTo": "domain entity name", "example": "Recipient" },
    { "name": "{Feature}", "bindsTo": "story sub-epic slug", "example": "addRecipient" }
  ],
  "renameMap": [
    { "from": "{Domain}.ts", "to": "<Domain>.ts" }
  ]
}
```

`abd-architecture-code` reads this to know what to substitute and where.

### `README.md`

Short. Names the source mechanism, links back to that mechanism's `architecture-context.md`, lists the placeholders, gives the runbook for `example/`.

## Boundaries

### What the template skill does NOT do

- **Does not author specifications.** If the source mechanism's `architecture-context.md` is incomplete (File Structure or Canonical Patterns empty), the template skill stops and routes back to `abd-architecture-specification`. It does not guess.
- **Does not generate per-feature code.** Generating real feature code from the template (substituting placeholders with story-specific names, writing the actual scenarios) is `abd-architecture-code`'s job. The template skill produces the *thing that gets copied*; the code skill is what copies and renames.
- **Does not enforce the spec.** Rule lifting is a copy, not a translation. If a rule in the spec is wrong, the fix happens in the spec; this skill mirrors what is there.

### What the template skill DOES do

- Reads the source mechanism's `architecture-context.md` verbatim, including its placeholder vocabulary.
- Reads the test-helpers package-tier `architecture-context.md` for tier names and helper layout.
- Reads the project's toolchain (existing source files, build configuration) to know what "runnable" means in practice — language, build tool, test runner, linter.
- Writes the template package directory.
- Verifies `example/` builds and its tests pass.

## Idempotency

Re-running the template skill against an existing template package must:

- Detect drift between the package and the current `architecture-context.md` (added participant, renamed placeholder, changed rule) and surface it via the violation workflow.
- Append new rules and new participants without removing manual edits to `example/` (the sentinel binding may have been adjusted by a real reader).
- Never silently overwrite. A drift report is the normal output of a re-run.

## How `abd-architecture-code` consumes a template package

The code skill resolves `<spec-root>` as the path to one template package:

| Code skill artefact | Resolves to |
|---|---|
| `<spec-root>/template/` | `docs/architecture/templates/<slug>/template/` |
| `<spec-root>/templates/tests/` | `docs/architecture/templates/<slug>/templates/tests/` |
| `<spec-root>/example/` | `docs/architecture/templates/<slug>/example/` |
| `<spec-root>/rules/` | `docs/architecture/templates/<slug>/rules/` |
| `<spec-root>/architecture-specification.md` | The central spec at `docs/architecture/specification/architecture-specification.md`, with the per-mechanism `architecture-context.md` reached via Where-to-Start. |

In `project` mode (default), `<slug>` is the project slug. In `mechanism` mode, the code skill maps the story's mechanism-in-scope to the right `<slug>` via the central spec's Where-to-Start table.

## Decision records at this level

When the template captures a non-obvious binding decision (which mechanism to template in `project` mode, how to handle a placeholder that has no natural sentinel value, why two near-identical mechanisms share one template vs. get separate ones), write an ADR under `docs/architecture/decisions/`. The README links to the relevant ADRs.
