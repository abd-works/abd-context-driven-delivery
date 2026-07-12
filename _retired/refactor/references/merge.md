Merge {capability-a} and {capability-b} into one capability.

## Choosing the master

Specify {master-capability} — the capability whose name and folder location survive:

| Scenario | Result |
|---|---|
| One capability absorbs the other | Keep {master-capability} folder and name; move all surfaces from {absorbed} into it |
| Neither name fits the merged domain | Create a new {merged-capability} folder; treat both originals as the source |

## Merge checklist

1. Identify the master (or create a new folder).
2. Merge agentic surfaces: combine `## Action` sections from both `.md` files into the master's `.md`. Resolve any name collisions — rename or collapse duplicate actions.
3. Merge API surfaces: move classes and methods from the absorbed `.py` into the master's `.py`. Update imports.
4. Merge rules folders: move rule sub-folders from `{absorbed}/rules/` into `{master}/rules/`. Resolve any duplicate rule names.
5. Merge templates and references.
6. Search the repo for `extends: {absorbed}` and update references to point at {master}.
7. Search for `from {absorbed}.{absorbed} import` — update all Python imports.
8. Delete the absorbed capability folder.
9. Clean stale `.cursor/skills/{absorbed}/` and `.cdd/{absorbed}/`.
10. Validate: `/capability validate {master}`.
11. Redeploy: `/capability deploy`.

## Warning

Merging two capabilities that violate the singularity principle produces a larger violation. Only merge when the two domains are genuinely one concept — otherwise extract further rather than merging.
