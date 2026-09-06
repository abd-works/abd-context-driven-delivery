<!--
  Meta-template: the shape of a generated template package.
  This file documents what abd-architecture-template produces on disk.
  It is NOT a file copied into the generated package; it is the spec for
  what the generated package looks like.

  DELETE this leading "Meta-template:" instruction block if you adapt this
  file for inclusion in a generated package's README.
-->

# Template package structure

A generated template package at `docs/architecture/templates/<slug>/` looks like this:

```
docs/architecture/templates/<slug>/
├── README.md                              # Short. What this is + runbook for example/.
├── parameters.json                        # Declared placeholders + rename map (see parameters.schema.md).
├── template/                              # The runnable parameterized reference module.
│   ├── {Participant1}.{ext}              #   Uses placeholders verbatim from source Canonical Patterns.
│   ├── {Participant2}.{ext}              #   Does NOT compile on its own (placeholders are not identifiers).
│   └── ...                                #   File hierarchy matches source File Structure exactly.
├── templates/
│   └── tests/                             # Parameterized test files, one per tier.
│       ├── {epicSlug}.{tier1}.test.{ext}  #   Tier names + paths from test-helpers context file.
│       ├── {epicSlug}.{tier2}.test.{ext}
│       └── ...
├── example/                               # Concrete instantiation. Builds + tests pass.
│   ├── <Sentinel>/                        #   Bound version of template/ with placeholders replaced.
│   │   ├── <Sentinel>.{ext}
│   │   └── ...
│   └── tests/                             #   Bound version of templates/tests/.
│       ├── <sentinel-feature>.{tier1}.test.{ext}
│       └── ...
└── rules/                                 # One file per § Rules bullet in source architecture-context.md.
    ├── <rule-1-slug>.md
    ├── <rule-2-slug>.md
    └── ...
```

## Where each section comes from

| Section | Source |
|---|---|
| `template/` | Source mechanism's `architecture-context.md` § File Structure + § Class Specification + § Canonical Patterns. |
| `templates/tests/` | Test-helpers package-tier `architecture-context.md` (typically `tests/<helpers>/architecture-context.md`). |
| `example/` | The skill binds placeholders in `template/` + `templates/tests/` to a sentinel name; runs the project toolchain to verify build + tests. |
| `rules/` | Source mechanism's `architecture-context.md` § Rules, lifted verbatim into one file per bullet. |
| `parameters.json` | Declared as a side effect of authoring `template/` — every placeholder used in code becomes a declared parameter. |
| `README.md` | Authored from a fixed template: name, source spec link, placeholder table, runbook, code-skill consumption note. |

## What `abd-architecture-code` reads

| `<spec-root>` artefact | Path inside the package |
|---|---|
| `<spec-root>/template/` | `template/` |
| `<spec-root>/templates/tests/` | `templates/tests/` |
| `<spec-root>/example/` | `example/` |
| `<spec-root>/rules/` | `rules/` |

The code skill resolves the package path itself (project mode: project slug; mechanism mode: mechanism slug looked up via the central spec's Where-to-Start). Once resolved, the four subdirectories above are the authority chain for `generated-code-matches-spec-file-layout.md` and `scaffold-test-layout-before-scenarios.md`.
