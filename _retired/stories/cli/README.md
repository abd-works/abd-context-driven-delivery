# `stories/cli/`

Thin CLI wrapper over the deterministic code-path generators in
`stories/src/stories/formats/`. This is the **code path** described in
[`stories/behavior/code-scaffolding-vs-ai-editing.md`](../behavior/code-scaffolding-vs-ai-editing.md).

## When to reach for it

- The **first** render of a spec-file tree in a code backend (`ts`, `tsx`, `py`, `js`).
- The **first** scaffold of tier files for a story (write-once — never overwrites).
- The **first** render — or a bulk re-render — of the drawio views for a
  workspace (story map, thin slice, scenario / AC).
- Bringing a whole story subtree into a new backend.

`create` is the canonical entry point (render-tree + scaffold-tiers in one
pass; the scaffold phase is a no-op for `--format drawio`). Use `render-tree`
or `scaffold-tiers` on their own only when you specifically need one half of
the pipeline.

For anything smaller — filling a tier body, tweaking a step, renaming an
actor — use the AI. The CLI has no `edit` subcommand on purpose.

## Commands

Code backends:

```
python stories/cli/main.py create          --workspace <path> --format <ts|tsx|py|js> --tiers server,client,e2e,domain [--tier-ext client=tsx] [--tests-root tests] [--no-shared] [--dry-run]
python stories/cli/main.py render-tree     --workspace <path> --format <ts|tsx|py|js> [--tests-root tests] [--no-shared] [--dry-run]
python stories/cli/main.py scaffold-tiers  --workspace <path> --format <ts|tsx|py|js> --tiers server,client,e2e,domain [--tier-ext client=tsx] [--dry-run]
```

Drawio (diagram) backend:

```
python stories/cli/main.py create          --workspace <path> --format drawio [--view story-map|thin-slice|scenario|all] [--tests-root diagrams] [--dry-run]
python stories/cli/main.py render-tree     --workspace <path> --format drawio [--view story-map|thin-slice|scenario|all] [--tests-root diagrams] [--dry-run]
```

`--view` accepts a single view or a comma-separated list; `all` (the default)
emits every supported view. Views whose required artifact is missing from the
workspace are silently skipped — a workspace with no thin-slice produces no
`thin-slicing.drawio`. Every view is re-rendered deterministically; hand-edits
to the `.drawio` file are not preserved across runs.

The entry point is called `main.py` (not `stories.py`) to avoid shadowing the
top-level `stories/` package during import.

Every command:

- Loads a `Workspace` from `--workspace` (must have a story map + scenarios).
- Emits under `--output` (defaults to `--workspace`), inside `<output>/<tests-root>/`.
- Reports a JSON summary on stdout: `{written: [...], skipped_existing: [...], dry_run: bool}`.
- **Never** overwrites tier files that already exist. Write-once is enforced twice — once inside the scaffolder, once at the emit boundary.
- Exit 0 on success, 2 on argument error, 3 on a not-yet-implemented backend.

## Why a thin wrapper and not free-form `python -c`

The callables under `stories/src/stories/formats/` will change signatures as
backends evolve. The CLI is the stable contract: skill instructions, behavior
docs, and eval prompts all point at it, so a rename inside the package
propagates in one place instead of dozens.

## Format shortcuts

- `--format ts` → TypeScript, all tiers use `.ts`.
- `--format tsx` → TypeScript with the `client` tier defaulted to `.tsx` (React clients).
- `--format py` → Python (snake_case files inside kebab-case folders).
- `--format js` → JavaScript with JSDoc-typed shared files.
- `--format java` → Java with JUnit 5 + records. `StoryTypes.java` / `StoryRunner.java` shared under `<tests-root>/stories/`. Tier files are `<StoryPascalCase><TierPascalCase>Tier.java`.
- `--format md` → Markdown. Renders `story-map.md` (no `tests/` sub-folder by default). No tier concept.
- `--format drawio` → three diagram views (story-map, thin-slice, scenario);
  `--tests-root` defaults to `diagrams`; no tier concept.

## Not exposed here

- Fine-grained per-story renders (single `<slug>-stories.<ext>`). Add via a subcommand later if needed — for now the tree renderer is idempotent per story so re-rendering the whole tree is cheap.
- Reverse translation (parse a spec file back into a `StoryMap`). That lives in `stories/src/stories/formats/code/*/*_story_map.py` as a Python API.
