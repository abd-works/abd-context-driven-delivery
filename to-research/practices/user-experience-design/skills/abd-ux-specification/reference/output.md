# Output — abd-ux-specification

**Deliverables folder:** resolve via [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md) § Output file resolution.

**File names:**

| Artifact | Purpose |
| --- | --- |
| `<screen-slug>.html` (and linked `.css` / `.js` as needed) | Runnable clickable prototype — open in browser, no build required unless the host project already uses one for previews |
| `ux-specification.md` | Structured spec: source paths, **brand assets** (resolved or provisional), design carry-over, stub boundaries, AC → demonstrated behaviour map, and what is intentionally **not** implemented |
| `ux-specification.html` | Spec review page — embeds `prototype/index.html` (or `example/index.html`) in an `<iframe>`; link to the Markdown spec in the header |

Add a `<name>-` prefix only when disambiguation is needed. Default folder: `docs/ux/prototype/` (or the host project's UX prototype convention).
