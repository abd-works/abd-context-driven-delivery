Extract a portion of {source-capability} into a new focused {target-capability}.

## What to examine before extracting

Review the full surface of {source-capability} before moving anything:

| Surface | What to check |
|---|---|
| Agentic surface (`{source}.md`) | Which `## Action` sections belong to {portion}? Do any sections straddle the boundary? |
| API surface (`{source}.py`) | Which methods, classes, or functions belong to {portion}? Are there shared helpers? |
| Rules (`{source}/rules/`) | Which rules validate {portion}? Are any rules shared across the boundary? |
| Templates (`{source}/template/`) | Which templates belong to {portion}? |
| References (`{source}/references/`) | Which reference files belong to {portion}? |
| Config (`.cdd-config.json`) | Does the deploy record need to be split? |

## Extract checklist

1. Create `{target-capability}/` using `/capability-create`.
2. Move identified `## Action` sections from `{source}.md` to `{target}.md`.
3. Move identified methods from `{source}.py` to `{target}.py`.
4. Move identified rules folders to `{target}/rules/`.
5. Move identified templates and references.
6. If `{source}` still needs moved actions, set `extends: {target}` and list them in `overrides:` on `{source}`, or remove entirely.
7. Update all `extends:` / `overrides:` frontmatter across the repo that referenced the moved actions.
8. Update all `from {source}.{source} import` statements in scanners and tests.
9. Validate both capabilities: `/capability validate {source}` and `/capability validate {target}`.
10. Redeploy both: `/capability deploy`.

## Warning

If the extracted portion is small (one action, one method) the split may not be worth the rewiring cost. Apply the singularity principle — split only when the two domains are genuinely distinct.
