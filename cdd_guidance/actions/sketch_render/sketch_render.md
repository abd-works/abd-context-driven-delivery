# sketch_render

Sketch interactively, then render the approved sketch in a background sub-agent.

## Flow

1. Same sketch loop as `/sketch` — grill, save, review.
2. On `review_sketch` approval, AskQuestion whether to render (unless the user already asked). Do not offer a single-format choice — each stage requires a pair.
3. `build_render_calls` — one explicit `render.render` entry per listed Guidance and format, using the stage's required pair.
4. `render_approved_sketch` — non-blocking sub-agent runs those calls, then `place_rendered`.

## Required formats by stage

| Stage | Formats (always both) |
|---|---|
| discovery | `drawio`, `markdown` |
| specification | `typescript`, `markdown` |

Pass both to `build_render_calls` for each listed Guidance that supports them. `SKETCH_RENDER_FORMATS` names which practice × stage combinations actually transform a sketch — Stories discovery gets `drawio` + `markdown`; DDD discovery gets `markdown` (bounded-context map from sketch); UX discovery gets `drawio` only. UX markdown is `ux-context` notes, not IA.

## Sub-agent contract

`build_render_calls` returns JSON. Each entry:

```json
{
  "tool": "render.render",
  "arguments": {
    "guidance": {"toolset": "…", "fidelity": "…"},
    "format": "drawio",
    "content": "<sketch file>",
    "source": "sketch"
  }
}
```

Pass that JSON as `render_calls` to the sub-agent. Do not invent render parameters in the sub-agent.
