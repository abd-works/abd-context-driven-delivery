---
fidelity: [exploration, specification, engineering]
artifact: [behavior]
section: body
---

# Behavior — Code Scaffolding vs AI Editing

Two producers write into a stories tree — any format, not just code — with
opposite guarantees. Pick explicitly. The wrong choice is either wasteful (AI
regenerates deterministic output) or destructive (scaffolder overwrites
hand-authored content).

## The rule

- **Code path (`stories/cli/main.py create`)** — new format, new subtree, or a
  large regeneration of the *structure* of any format (md, drawio, code):
  folder hierarchy, skeleton files at each node, shared/template files.
  Deterministic. Write-once for artifacts that carry user content
  (`story-context.md` prose, tier bodies).
- **AI edits** — everything else: writing `story-context.md` prose, filling
  tier bodies, adding a scenario, renaming an actor, fixing a step string,
  iterating on scanner feedback.

## Invoking the code path

Code backend (`ts`, `tsx`, `py`, `js`):

```bash
python stories/cli/main.py create \
  --workspace <path>           # loads story map + scenarios from here
  --format <ts|tsx|py|js|java> # java not yet wired via CLI
  --tiers <server,client,...>  # comma-separated tier names
  [--output <path>]            # defaults to --workspace
  [--tests-root <name>]        # default: tests
  [--tier-ext <tier>=<ext>]    # repeatable, e.g. client=tsx
  [--no-shared]                # skip story-types + story-runner emission
  [--dry-run]                  # preview without writing
```

`create` = render-tree + scaffold-tiers in one pass. Idempotent for spec files;
skips tier files that already exist.

Diagram backend (`drawio`):

```bash
python stories/cli/main.py create \
  --workspace <path>           # loads story map + thin-slice + scenarios
  --format drawio
  [--view story-map|thin-slice|scenario|all]  # default: all
  [--output <path>]            # defaults to --workspace
  [--tests-root <name>]        # default: diagrams
  [--dry-run]
```

For `--format drawio` the scaffold phase is a no-op; `create` and
`render-tree` are equivalent. Views are re-rendered deterministically from the
underlying model — hand-edits inside a `.drawio` file are not preserved.
`--view all` (the default) emits `story-map.drawio`, `thin-slicing.drawio`, and
`acceptance-criteria.drawio` under `<output>/<tests-root>/`. Views whose
required artifact is missing (no thin-slice loaded, no scenarios attached) are
skipped without error.

`render-tree` and `scaffold-tiers` are also available as narrower subcommands —
see `stories/cli/README.md`.

## Decision table

| Situation | Producer |
|---|---|
| First render of story-map folder structure + skeleton files (md, drawio, code) | Code path |
| Re-render skeleton / structural files (md, drawio, code) after story-map data change | Code path |
| First render of a spec file for any story (code) | Code path |
| First scaffold of tier files for a new story (code) | Code path |
| First render of drawio views (story map / thin slice / scenario) | Code path |
| Re-render drawio views after AI edited scenarios, thin-slice, or story-map | Code path |
| Translating a subtree into a new backend | Code path |
| Editing `story-types.<ext>` / `story-runner.<ext>` (shared code files) | Code path (templates only) |
| Writing `story-context.md` prose | AI |
| Filling tier bodies with real assertions | AI |
| Adding a step / scenario / Examples row inside an existing file | AI |
| Adjusting a drawio view by hand in the diagram | Not supported — re-edit the model, re-render |
| Adding a new backend under `stories/src/stories/formats/` | AI (skill contributor) |

The CLI wires the `ts / tsx / py / js / java / md / drawio` backends. All seven
are available via `python stories/cli/main.py create --format <backend>`.

## Guardrails

- Spec files must stay **round-trippable** — the AI edits them only in ways
  the code path can parse back and re-render byte-for-byte.
- Tier files are **write-once**. The scaffolder refuses to overwrite; the AI
  and human own them from first emit onward.
- Shared files (`story-types.<ext>`, `story-runner.<ext>`) come verbatim from
  `stories/templates/` — the AI never edits them.
- Engineering fidelity requires **implemented** tier bodies — no TODO stubs.
  Enforced by `stories/rules/tier-bodies-implemented/`.

## Cross-references

- `stories/cli/README.md` — full CLI reference, format shortcuts, output shape.
- `stories/src/stories/formats/code/architecture-context.md` — write-once
  contract, round-trip guarantee, code-path internals.
- `stories/behavior/artifact-layouts-expanded.md` — who writes which file in
  the expanded (code) layout.
