# UX — Procedural Guidance (mockup fidelity)

## How to build mockups

Mockups deepen IA regions into typed controls with key interactions, running inside the Story Demo shell:

1. **Ensure story/domain JS exists** — if Stories or CE haven't emitted JavaScript modules yet, run `transform` first. The mockup imports real domain modules, not UX-only adapters.
2. **Deepen regions with controls** — each IA region slot gets concrete control types: text input, dropdown, button, list, tabs.
3. **Wire GWT-bound controls** — controls that participate in story Given/When/Then use `StoryDemoControl` with `bound_field` (the expose path) and `story_steps` (matching step text exactly). This generates `data-story-steps` attributes for the Story Demo explorer.
4. **One HTML per user goal** — not one file per screen, not one mega-file per epic. Each concrete user goal the user can demo gets its own HTML file.

## Interactive controls thinking

For controls that take user input or display dynamic data:

- **Number/quantity inputs** → `data-input-field`
- **Bound lists** → `data-bound-list` + `data-bound-field` (expose path) + optional `data-item-story-steps`
- **Don't bake product words into the template** — "catalog," "cart" are bound_field paths and story language, not template tokens.

## Branding is opt-in

Default output is greybox — functional, no branding. Add brand/CSS only when:
- The user explicitly asks for it, or
- Brand tokens already exist in the workspace

When branding is active, use the matching `specifications/` folder (e.g. `specifications/abd-works/`). Don't invent brand tokens.

## Stub catalogue honesty

Every faked behavior must be explicitly listed. No silent pretence of production services. If the mockup stubs a payment gateway, that's documented in the HTML or a companion note.

## Shell layout is fixed

Product mockup on the LEFT (`#story-demo-frame`). Explorer on the RIGHT (`#explorer-frame`). `data-goto` navigates between product screens. Don't rebuild the shell — use `mockup_shell.html` and fill screens/controls on the model.
