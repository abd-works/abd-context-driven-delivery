# document takes `paths` and ignores them: a missing file, a file outside the project, and no path at all give the same answer

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers Document.
- **Module and class:** `cdd_guidance/actions/document/document.py`, `Document.document` (the body never reads `paths`).
- **Severity:** wrong result (an argument accepted and ignored); question whether the agent alone is meant to read the paths

## Steps
Sandbox `repo`, session `main` (`drv\c11.json`):

    document.document {"guidance": "stories-story-map", "paths": [".context/story-map.md"]}
    document.document {"guidance": "stories-story-map", "paths": ["nope/missing.md", "../../outside.md"]}
    document.document {"guidance": "stories-story-map", "paths": []}

## Expected
"paths: the files and folders to scan." A path that is not there or not under the session's root is refused by name, as validate does, and the answer names the files to scan.

## Actual
All three answer `isError=False` with the same 3,628 characters: the template and the session section. No path is named, checked, or refused.

## Tier that should catch it
Unit: Document has no spec file (`cdd_guidance/actions/document/` holds only document.py and document.md).
