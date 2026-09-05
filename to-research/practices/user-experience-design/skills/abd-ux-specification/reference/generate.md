# Generate — abd-ux-specification

## Read before generating

- **`reference/concepts.md`** — what a clickable prototype is, carry-over from upstream, brand assets, stub vs real boundaries, accessibility at prototype fidelity, and the shape of a good prototype package.
- **`reference/brand-assets-questionnaire.md`** — key questions to ask when brand assets are missing or incomplete.

## Output shape

See [`reference/output.md`](output.md).

| Output | What to produce |
| --- | --- |
| `ux-specification.md` | Screen name, source paths (IA, lo-fi, hi-fi/design refs), **brand assets brief** (`templates/brand-assets-brief.md`), design tokens used, region → element map, **stub catalogue** (what is faked and how), AC → click/demo path |
| Prototype files | Self-contained or host-folder HTML/CSS/JS that renders the screen and wires primary flows |
| `ux-specification.html` | When prototype folder contains `index.html`, copy `templates/ux-specification.html`, set `{{PROTOTYPE_INDEX}}` to the relative path (default `prototype/index.html`), iframe that entry |

## Generation flow

1. **Resolve inputs** — lo-fi path, AC file, domain language, screen name, design reference (tokens, brand CSS, or hi-fi export). Confirm where prototypes live in the host project.
2. **Resolve brand assets** — search the host project for guidelines, logos, and tokens. If anything is missing, run section 2 of `reference/brand-assets-questionnaire.md` using the **`AskQuestion` tool** (steps A–F) — do not paste the questionnaire as chat text. Record answers in the **Brand assets** section of `ux-specification.md` (`templates/brand-assets-brief.md`). Do not proceed to hi-fi styling until `AskQuestion` responses are received or the user approves provisional stand-ins.
3. **Carry over upstream decisions** — regions, affordances, labels, copy, typography roles, colour roles, density, and spacing from lo-fi and design reference. Do not invent new vocabulary or affordances.
4. **Author `ux-specification.md` first** — brand assets brief, then the stub catalogue: list every behaviour that is simulated (fake API JSON, `setTimeout` loading, toggled CSS classes for states, `localStorage` only if the demo requires it).
5. **Build the visual layer** — semantic HTML, real CSS (project tokens or documented stand-ins), logo and imagery from resolved assets, component structure that mirrors how production will eventually be organized without pulling in full app infrastructure.
6. **Wire interactions** — links, buttons, tabs, modals, and form submits navigate or swap visible states. Use minimal JavaScript: event handlers, DOM class toggles, template literals for fake responses. **Do not** integrate real APIs, databases, or domain services.
7. **Demonstrate AC paths** — each AC clause maps to a click path or visible state a reviewer can trigger manually; document the path in `ux-specification.md`. Happy paths first; edge/error states via stubbed responses or pre-seeded demo data.
8. **Mark prototype boundaries** — comment or document anything that looks real but is fake (`// PROTOTYPE: stub`). No silent pretence that stubbed behaviour is production-ready.
9. **Basic accessibility** — programmatic labels on inputs, keyboard-reachable controls, visible focus, text labels (not colour-only state). Full test suites and performance budgets are **out of scope** for this skill.
10. **Author `ux-specification.html`** — when an `example/` or `prototype/` folder contains `index.html`, generate the HTML spec page from `templates/ux-specification.html` with iframe `src` pointing at that index (relative path). List both spec files in `ux-specification.md` metadata.
11. **Verify in browser** — open `ux-specification.html` (or `prototype/index.html`), walk every documented AC path, confirm labels match UL/AC verbatim; confirm logo, colours, and imagery match the brand assets brief.
