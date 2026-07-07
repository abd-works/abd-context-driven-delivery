# Artifact Layout — Flat

One file for everything. The only mode `.json` supports; also valid for tiny markdown projects and for small codebases where the folder hierarchy would be overkill.

## Output locations

| Format | Location |
|---|---|
| `json` | `stories.json` |
| `md` | `stories.md` |
| code (tiny app) | `stories.<fmt>` |

## When to escape

Flat is a starting shape, not a permanent one. Escape to another mode when:

- **→ Consolidated:** the doc is getting too long to navigate; scenarios span more than 2–3 iterations; multiple people are editing partial slices in parallel
- **→ Expanded:** the codebase has more than a handful of stories; testing is happening at any real scale; the file structure would benefit from being the packaging
