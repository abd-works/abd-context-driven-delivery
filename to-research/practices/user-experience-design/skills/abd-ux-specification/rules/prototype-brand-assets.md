# Rule: Brand assets are resolved before hi-fi styling; gaps are asked, then documented

**Scanner:** AI review

A clickable prototype must read as a real product site or app — not a grey wireframe. Before authoring CSS or placeholder logos, the agent **searches the host project** for existing brand assets and **asks key questions** when anything is missing. Provisional assets the agent creates must be recorded in `ux-specification.md` with explicit stand-in boundaries.

## DO

- **Search the host project first** for brand sources: `brand-guidelines`, design tokens, CSS variables, logo files (`*.svg`, `*.png`), `abd-visual-branding` skill output, or a `brand/` / `assets/` folder referenced in IA or mockup specs.

  **Example (pass):** Agent finds `brand-guidelines.html` and `assets/logo.svg` in the engagement root; prototype imports those tokens and the logo verbatim.

- **Ask the brand-assets key questions** from `reference/brand-assets-questionnaire.md` using the **`AskQuestion` tool** (steps A–F) when no authoritative brand package exists, or when existing assets are incomplete. Wait for tool responses before choosing colours, type, logos, or photography.

  **Example (pass):** No logo on disk — agent calls `AskQuestion` for colour scheme and logo; user selects `Coral + teal (retail)` and `create-provisional-svg`; agent records decisions in `ux-specification.md` before building CSS.

- **Use `AskQuestion` for structured brand choices** — colour scheme, typography, tone, logo policy, photography, trust chrome, and create-vs-wait. Use chat follow-up only for free-text paths, hex values, or brand names when the user picks `other`.

  **Example (pass):** Step C `AskQuestion` offers three domain-aligned palettes plus `use-host-tokens`; user picks one option; agent does not re-ask the same question in prose.

- **Offer to create provisional stand-ins** when assets are missing and the user agrees: simple SVG wordmark, CSS custom properties for colour/type, and licensed stock photography (e.g. Unsplash URLs) — clearly labelled as prototype-only in the spec.

  **Example (pass):** `ux-specification.md` includes a **Brand assets** section listing `prototype/assets/logo.svg` as *provisional wordmark — replace before production* and documents primary `#E85D4C`, secondary `#2D6A6A`, font *Plus Jakarta Sans*.

- **Apply resolved assets consistently** across consumer screens: header logo, favicon, footer, promo strip, product imagery, and staff/portal variants where the flow includes them.

  **Example (pass):** Cart lines, confirmation, and PDP gallery all use the same product image URLs from the stub catalogue; header and footer share one logo path.

- **Record brand decisions in `ux-specification.md`**: source paths (or *created for prototype*), colour roles, typography, imagery policy, and what must be swapped before production.

  **Example (pass):** Spec table row: `Logo | prototype/assets/logo.svg | Provisional SVG; client brand pack TBD`.

## DO NOT

- **Ship a hi-fi prototype with default browser styling** when brand assets were never sought and the user was not asked.

  **Example (fail):** Unstyled HTML tables, system font, and no logo because the agent skipped the questionnaire and never searched the repo.

- **Invent a parallel brand system** that contradicts authoritative host brand files when those files exist.

  **Example (fail):** Host `brand-guidelines.html` specifies abd.works tokens; prototype uses a unrelated purple palette and a different wordmark because the agent did not read the guidelines.

- **Use copyrighted logos or client trademarks** from the public web without explicit user direction.

  **Example (fail):** Dropping a real competitor's logo into the header as a placeholder.

- **Leave provisional assets undocumented** so reviewers mistake stand-ins for approved brand.

  **Example (fail):** Agent generates `logo.svg` and Unsplash URLs but `ux-specification.md` has no **Brand assets** section.

- **Proceed past missing assets without asking** whether to create stand-ins or pause for design input.

  **Example (fail):** Agent notices no logo, silently uses text "Logo" in the header, and continues the build.

- **Paste the brand questionnaire as a numbered chat list** instead of calling `AskQuestion`.

  **Example (fail):** Agent posts "1. Brand name? 2. Colour scheme? …" in chat and immediately starts CSS without waiting for structured answers.
