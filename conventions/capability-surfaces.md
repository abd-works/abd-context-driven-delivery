---
description: A capability exposes its API surface as {capability}/{capability}.{ext} and its agentic surface as {capability}/{capability}.md.
globs: **
---

Every capability folder must expose exactly two entrypoint surfaces, both named after the folder itself:

| File | Role |
|---|---|
| `{capability}/{capability}.py` (or `.ts`, `.js`, …) | **API surface** — code entrypoint invoked by other code, CLIs, or tests |
| `{capability}/{capability}.md` | **Agentic surface** — top-level instructions read by agents and humans |

**Example:**

```
enforce/
  enforce.py        ← code API   (python -m enforce, importable, testable)
  enforce.md        ← agent API  (what the capability does, how to use it)
```

Rationale: predictable entrypoints. To wire a capability into anything — code or agent — always reach for `{capability}.py` or `{capability}.md`. No hunting through subfolders, no `__main__.py`, `index.ts`, or `README.md` guessing games.
