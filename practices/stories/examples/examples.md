# Stories examples

Reference trees under this folder. Prefer generating fresh trees via
`Stories.transform` / `generate` at the active fidelity rather than copying
these verbatim when the hybrid layout differs.

## Markdown (`md/`) — discovery documents

| Path | What it shows |
|---|---|
| `md/story-map.md` | Discovery story map (verb–noun + actor before `-->`) |
| `md/thin-slice.md` | Vertical increments referencing map story names |
| `md/scenario-main-flow.md` | Main-flow scenario narrative |
| `md/scenario-outline.md` | Scenario outline + examples table |
| `md/scenario-inline.md` | Inline-examples scenario style |

## Python (`py/`) — exploration / specification / engineering layout

| Path | What it shows |
|---|---|
| `py/manage-customer-orders/` | Acceptance layout for one epic (story-spec leaf files + shared runner/types) |
| `py/manage-customer-orders/*/*/*_stories.py` | Regeneratable story-spec constants (`story`, `actor`, scenarios) |
| `py/manage-customer-orders/story_runner.py` | Runner that binds scenarios to tier implementations |
| `py/manage-customer-orders/story_types.py` | Shared story/scenario type shapes |

Prefer the hybrid leaf-file + tier shape from the code formatter over any legacy dict-only layout when they disagree.
