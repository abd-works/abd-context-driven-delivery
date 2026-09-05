# abd-ux-specification — Concepts

## What is a clickable prototype

A prototype under this skill is:

- **Hi-fi** — real visual design: tokens, type, colour, spacing, and components that match the approved design direction. Not a lo-fi grey box.
- **Clickable** — buttons, links, tabs, and forms respond; screens and states change so stakeholders can walk flows.
- **Honest** — domain logic, APIs, auth, and persistence are stubbed or faked. The prototype **demonstrates** behaviour; it does not **implement** it.
- **Faithful to upstream** — regions, affordances, labels, and copy match lo-fi and design reference. Ubiquitous-language terms and AC wording stay verbatim in the UI.
- **Browser-runnable** — HTML, CSS, and JavaScript (or the host preview stack). Open and click without deploying backend services.

It is not production code, not a refactor of the host app, and not a substitute for acceptance tests or domain implementation.

---

## Carry-over from upstream

The initial IA and lo-fi are inputs. Their regions, affordances, labels, and acceptance criteria are settled. Visual decisions (typography roles, colour roles, density, spacing) come from the design reference or hi-fi direction. The prototype maps those into markup and styles — it does not redecide layout or vocabulary.

---

## Brand assets and hi-fi chrome

Lo-fi mockups deliberately omit colour and brand polish. The specification stage is where the prototype should **look like a real site**: logo, palette, typography, photography, header/footer, and trust cues (promo strip, badges) when the flow needs them.

**Before styling:**

1. Search the host project for brand guidelines, tokens, logos, and any `abd-visual-branding` output.
2. If anything is missing, run section 2 of **`reference/brand-assets-questionnaire.md`** using the **`AskQuestion` tool** (steps A–F) — colour scheme, type, tone, logo, photography, trust chrome, and whether to **create provisional stand-ins** or wait for design.
3. Record decisions in `ux-specification.md` using the shape in **`templates/brand-assets-brief.md`**.

Provisional logos (simple SVG wordmarks), CSS variables, and licensed stock URLs are acceptable for demos when documented as *replace before production*. Do not silently ship unstyled wireframes or undeclared stand-ins.

---

## Stub vs real

| Real in the prototype | Stubbed or faked |
| --- | --- |
| HTML structure, CSS, layout, typography, colour | API requests → fixture JSON or inline objects |
| Click handlers, route/hash navigation, modals | Server validation → client-side `if` or canned messages |
| Local UI state (open panel, active tab) | Auth/session → assume logged-in or toggle with a demo flag |
| Accessible labels, focus order, visible focus | Database reads/writes → preloaded demo data |
| Copy and labels from UL/AC | Side effects (email, payment, inventory) → `console.log` or toast |

Document every stub in `ux-specification.md` under a **stub catalogue** so reviewers know what is simulated.

---

## Demonstrating acceptance criteria

Each AC clause gets a **demo path**: the clicks or inputs that make the criterion visible. Example: "WHEN stock is zero THEN show out-of-stock banner" → prototype loads with `?demo=out-of-stock` or a "Demo states" control that toggles the banner. Tests and automated assertions are out of scope; manual walkthrough is the verification method.

---

## Accessibility at prototype fidelity

Prototypes still need structural accessibility: inputs have `<label>` or `aria-label`, interactive elements are keyboard reachable, focus is visible, and status is not conveyed by colour alone. Pixel-perfect contrast audits and full ARIA regression suites belong to production implementation, not this skill.

---

## The shape of a good prototype package

```
docs/ux/prototype/store-locator/
  prototype/
    index.html                # entry page; links CSS/JS
    store-locator.css         # tokens + layout + states
    store-locator.js          # click handlers, stub data, state toggles
  ux-specification.md         # sources, stub catalogue, AC demo paths
  ux-specification.html       # review page — iframe → prototype/index.html
  fixtures/
    stores.json               # optional fake API payload
```

Open **`ux-specification.html`** for review: the prototype runs inside the frame (pointing at **`index.html`** in the prototype or `reference/example/` folder). `ux-specification.md` remains the structured spec; serve the folder with a static HTTP server if the iframe is blank under `file://`.

Skill reference packages may ship `reference/example/index.html` — the Foundry skill page embeds that index in the hero frame when present.

---
