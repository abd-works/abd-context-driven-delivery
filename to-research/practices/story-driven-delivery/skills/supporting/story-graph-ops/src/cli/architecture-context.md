---
generating-skill: abd-architecture-specification
type: package-context
fidelity: specification
---

# Package: cli/

---

## Overview

`cli/` contains the single unified entry point for all story graph operations. Each
command loads a `StoryMap` from `story-graph.json` (via `formats/document/json/`) and
delegates to the appropriate format backend. The CLI owns no business logic — it
wires inputs to backends and reports results.

---

## Why this shape

**The problem.** It is always tempting to put "just a little" logic in the CLI — parse a flag, filter a list, transform a report before printing. Every time this happens, the same logic re-appears in a different form when the format backends are called from a test or another entry point. The CLI becomes a second, parallel implementation of behavior that already lives in the backends.

**The inversion — CLI is a router, not a layer.** Each command does exactly three things: load the graph via `formats/document/json/`, dispatch to the appropriate backend, print the returned `UpdateReport` as a Markdown summary. Anything more than that gets pushed down into a backend. If the same "small transformation" needs to happen from two entry points, it belongs in `core/` or in the relevant format package — not here.

**The disciplines.** *No business logic in the CLI* — rendering, diffing, generation all happen in `formats/`. *JSON is always loaded via `formats/document/json/`* — never with an inline `json.loads`, otherwise there are two parsers. *`UpdateReport` is printed via its own Markdown summary* — no per-command formatter, so every command reports the same shape.

---

## File Structure

```
cli/
+-- architecture-context.md
+-- story_graph_cli.py     <- unified CLI: parse, sync-drawio, sync-miro, generate-ts
```

---

## Commands

| Command | Backend called | Output |
| --- | --- | --- |
| `parse <markdown>` | `formats/document/markdown/MarkdownSynchronizer` | Updates `story-graph.json` |
| `sync-drawio <file>` | `formats/diagram/drawio/DrawIOSynchronizer` | `UpdateReport` (printed as Markdown summary) |
| `sync-miro <board-id>` | `formats/diagram/miro/MiroSynchronizer` | `UpdateReport` (printed as Markdown summary) |
| `generate-ts` | `formats/code/typescript/TypeScriptStoryMap` | Writes `tests/**/*-stories.ts` |

---

## Rules

- **CLI owns no business logic** — all rendering, diffing, and generation is in `formats/`.
- **CLI always loads `story-graph.json` via `formats/document/json/`** — it does not parse JSON directly.
- **`UpdateReport` is printed as a human-readable Markdown summary** — not raw JSON.
- **Exit code reflects `UpdateReport` state** — non-empty changes → exit 0 (changes reported); error → exit 1.
