# Brand assets — key questions

Use this questionnaire **before** hi-fi CSS, logos, or photography when `abd-ux-specification` runs. Search the host project first; ask only for gaps. **Wait for answers** (or explicit defaults) before styling the prototype.

---

## 1. Discover what already exists

Search the engagement root and upstream UX artifacts for:

| Look for | Typical locations |
| --- | --- |
| Brand guidelines / tokens | `brand-guidelines.html`, `brand-*.html`, `tokens.css`, `:root` variables in host CSS |
| Logo files | `assets/logo.svg`, `brand/`, `public/` |
| Visual branding skill | `abd-visual-branding` in `.cursor/skills` or project agents |
| Design reference from mockup | `ux-mockup.md` **Design reference** section, `Design/` image folders |
| Prior prototype | `docs/**/prototype/`, existing `ux-specification.md` |

**If found:** confirm with the user that these sources are authoritative for this prototype.

**If not found or incomplete:** continue with section 2.

---

## 2. Key questions (ask the user)

**Mandatory:** use the **`AskQuestion` tool** for every step below. Do **not** dump the questionnaire as a numbered list in chat. Wait for each `AskQuestion` response before the next step or before hi-fi styling.

Skip questions already answered by authoritative files found in section 1 — but still confirm with one `AskQuestion` when those files exist (see step A).

---

### Step A — Confirm or gap (always ask when brand affects hi-fi)

Use `AskQuestion`:

| Field | Value |
| --- | --- |
| `id` | `brand-source` |
| `prompt` | Brand assets for this prototype — what should we use? |
| Options | Build dynamically from section 1 discovery |

**Option pattern** (include only what applies):

- `use-found` — Use existing brand files (label names the path found, e.g. `brand-guidelines.html + assets/logo.svg`)
- `partial-found` — Use what we have; ask me about gaps next
- `no-brand-pack` — No brand pack — run full questionnaire
- `other` — Other (I will specify)

If the user picks **partial-found** or **no-brand-pack**, continue with steps B–F. If **use-found**, record paths and skip to section 4 unless they chose **partial-found**.

---

### Step B — Brand name and authoritative source

Use `AskQuestion` with `allow_multiple: false`:

| Field | Value |
| --- | --- |
| `id` | `brand-name` |
| `prompt` | What is the customer-facing brand / site name on screens? |
| Options | Infer 2–3 candidates from domain language, story map, or repo folder name, plus `other` |

If **other**, ask one follow-up in chat for the exact name.

When multiple brand files exist, use `AskQuestion`:

| Field | Value |
| --- | --- |
| `id` | `brand-authority` |
| `prompt` | Which source wins if brand files conflict? |
| Options | `html-guidelines`, `figma-export`, `css-tokens`, `verbal-preference`, `other` |

---

### Step C — Colour scheme

Use `AskQuestion`:

| Field | Value |
| --- | --- |
| `id` | `colour-scheme` |
| `prompt` | Preferred colour scheme for the prototype? |
| Options | Domain-aligned palettes (2–3), each labelled with primary + secondary hex, e.g. `Coral + teal (retail)`, `Navy + gold (premium)`, `Green + slate (clinical)`; plus `use-host-tokens` if tokens exist; plus `other` |

If **other**, follow up in chat for primary, secondary, accent hex values and colours to avoid.

---

### Step D — Typography and tone

Use `AskQuestion` with **two questions** in one call (`allow_multiple: false` each):

1. `id`: `typography` — `prompt`: Preferred typography?  
   Options: `plus-jakarta`, `inter`, `system-ui`, `use-host-fonts`, `other`

2. `id`: `tone` — `prompt`: How should the site feel?  
   Options: `friendly-retail`, `premium-boutique`, `clinical-b2b`, `playful-consumer`, `other`

---

### Step E — Logo and photography

Use `AskQuestion` with **two questions** in one call:

1. `id`: `logo` — `prompt`: Logo for the prototype?  
   Options: `use-existing-file` (if found), `create-provisional-svg`, `text-only`, `other`

2. `id`: `photography` — `prompt`: Product and store imagery?  
   Options: `stock-urls-ok`, `client-assets-only`, `neutral-placeholders`, `other`

If **use-existing-file**, follow up in chat only if the path is ambiguous.

---

### Step F — Chrome and create vs wait

Use `AskQuestion` with `allow_multiple: true` where noted:

1. `id`: `trust-chrome` — `prompt`: Include trust / chrome elements? (`allow_multiple: true`)  
   Options: `promo-strip`, `trust-badges`, `footer-links`, `favicon`, `staff-consumer-dual-branding`, `none-minimal`

2. `id`: `missing-assets` — `prompt`: Missing logo, images, or tokens — what should the agent do?  
   Options: `create-stand-ins-now`, `pause-for-design`, `defaults-ok` (apply section 3 defaults)

---

### After all answers

Record every choice in `ux-specification.md` under **Brand assets** (`templates/brand-assets-brief.md`). Map `AskQuestion` option ids to human-readable decisions in the brief table.

---

## 3. Defaults when the user defers

Only apply when the user explicitly says *use your judgement*, *defaults are fine*, or does not answer after the questionnaire:

| Asset | Default stand-in |
| --- | --- |
| Palette | Domain-appropriate 3-colour scheme documented in the spec |
| Type | One free webfont (e.g. Plus Jakarta Sans or Inter) via Google Fonts |
| Logo | Simple SVG wordmark + icon in `prototype/assets/logo.svg` |
| Product images | Unsplash (or similar licensed stock) URLs in stub fixtures |
| Store/hero images | Stock photography matching the vertical |

Always label these as **provisional** in `ux-specification.md`.

---

## 4. After answers — build checklist

- [ ] CSS custom properties (or host tokens) match agreed colours
- [ ] Logo linked in header, favicon, footer; staff shell if in scope
- [ ] Product and store imagery populated in stub fixtures
- [ ] `ux-specification.md` **Brand assets** section filled
- [ ] Provisional items marked *replace before production*
