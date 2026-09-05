# Initial information architecture — {{SCOPE}}

> **Companion to** `docs/ux/initial-ia.tldr` / `initial-ia.svg`. This markdown is the structured spec for the canvas. Author or update **this file first**, then drive the canvas from it. After the canvas is updated, sync any change back into this file so the two never diverge.

## Metadata

| Field | Value |
| --- | --- |
| Scope | {{SCOPE}} (e.g. `Increment 1`, `Crowd Manager Epic`, `Sprint 4`) |
| Story map | {{STORY_MAP_PATH}} |
| Domain Language | {{UBIQUITOUS_LANGUAGE_PATH}} |
| Canvas (`.tldr`) | `docs/ux/initial-ia.tldr` |
| Canvas (`.svg`) | `docs/ux/initial-ia.svg` |
| Last canvas update | {{ISO_DATE}} |

## Description

{{ONE_PARAGRAPH_DESCRIPTION}}

One paragraph: what the IA covers, what conversation it supports, who reads it.

---

## Navigation

### Screen flow — complete connection map

One ASCII block. List navigation components first (anything available from every screen), then each screen as a tree showing all outgoing transitions tagged with navigation type. This section must stay in sync with the Site Map page of `initial-ia.drawio`.

```
═══════════════════════════════════════════════════════════
  NAVIGATION COMPONENTS (present on every screen)
═══════════════════════════════════════════════════════════

  {{NAV_COMPONENT_NAME}} ({{UX_TYPE}} — available from every screen)
    ├─ {{LINK_LABEL}} ───────────────────────────→ {{DESTINATION_SCREEN}}
    └─ {{LINK_LABEL}} ───────────────────────────→ {{DESTINATION_SCREEN}}

  {{NAV_COMPONENT_NAME}} ({{UX_TYPE}} — {{SCOPE}})
    └─ {{LINK_LABEL}} ───────────────────────────→ {{DESTINATION_SCREEN}}

═══════════════════════════════════════════════════════════
  SCREEN FLOW
═══════════════════════════════════════════════════════════

{{SCREEN_NAME}}
  ├─ [{{NAV_TYPE}}] {{ACTION_LABEL}} ──────────→ {{DESTINATION_SCREEN}}
  └─ [{{NAV_TYPE}}] {{ACTION_LABEL}} ──────────→ {{DESTINATION_SCREEN}}

{{SCREEN_NAME}}
  └─ [action] {{ACTION_LABEL}} ────────────────→ {{DESTINATION_SCREEN}}
```

Nav type tags: `[Quick Action]` · `[top nav]` · `[drawer nav]` · `[secondary nav]` · `[action]` · `[system]`

---

### Site map — screens

One block per **user-visible state**. A panel with N tabs produces N separate screen blocks, each named `{{parent screen}} — {{tab label}}`. Inactive tabs appear in each sibling's block under "Inactive tabs (greyed)".

**Story budget:** each screen block should carry ~4 user stories. More than ~4 is a signal that a tab, edit/detail screen, or mode is missing.

Transitions are recorded inside each screen block as **From** (incoming) and **To** (outgoing) lists.

#### {{SCREEN_NAME}}

- **Description:** {{ONE_LINE_DESCRIPTION}}
- **Source:** [{{DOMAIN_OR_STORY_NAME}}]({{LINK_TO_SOURCE}})
- **Layout:** `{{LAYOUT_DESCRIPTOR}}` — e.g. `modal dialog`, `header + left panel + body + footer`

```
[{{SCREEN_NAME}}]
(copy the filled ASCII art from screen-templates/{{LAYOUT_TEMPLATE}}.md
 · Replace each [slot-name] zone with actual region name and representative row fields
 · Use ············ dotted borders for chrome that repeats dimmed from a primary sibling screen)
```
- **Inactive tabs (greyed):** {{OTHER_TAB_NAMES}} — omit this line if the screen has no sibling tab states
- **Chrome (shared regions — named only, no actions listed here):**
  - toolbar, crowd tree panel, status bar — (or whichever persistent chrome this screen shares)
  - For tab-state sibling screens add: `chrome: same as {{primary screen name}}`
- **From (incoming transitions):**
  - from {{SOURCE_SCREEN}} — trigger: {{TRIGGER}}
- **To (outgoing transitions):**
  - to {{DESTINATION_SCREEN}} — trigger: {{TRIGGER}}
- **Content regions** — active content only (not chrome). For each region: name (UX term), the list row fields a user sees, and the verb row below the list. Edit actions produce a transition to a new detail screen.
  - **{{REGION_NAME}}**
    - Row fields: `{{FIELD_1}} · {{FIELD_2}} · {{FIELD_3}}`  *(show representative field labels a user reads — no prose)*
    - Actions: `{{VERB_1}} · {{VERB_2}} · {{VERB_3}}`  *(verb row only — edit/configure → see transition below)*
  - *(repeat for each content region)*
- **In-scope user stories (~4 max):**
  - {{USER_STORY_TITLE}} — maps to: {{REGION}} / {{ACTION OR TRANSITION}}
  - *(more than ~4 stories here is a decomposition signal — find the missing screen)*
- **Groups system stories:**
  - {{SYSTEM_STORY_TITLE}}
- **Domain terms (visible only — field labels and row type names on this screen):**
  - {{TERM_1}}, {{TERM_2}}, {{TERM_3}}
  - *(only terms visible as data field labels or row type names — not internal model terms)*

<!-- duplicate the #### block for each screen, including one block per tab state -->

---

### Navigational components

Persistent surfaces that carry navigation across screens (menus, headers, sidebars, footers, breadcrumbs). Named in UX terms only — no action lists here.

#### {{COMPONENT_NAME}} ({{UX_TYPE}})

- **Appears on:** {{SCREEN_NAMES}}
- **Links to:** {{SCREEN_OR_REGION_NAMES}}
- **Notes:** {{ONE_LINE}}

<!-- duplicate for each component -->

---

## Content types (shared across screens)

Only content types referenced by **more than one** screen are described here. Single-screen content stays inline in the screen block above.

#### {{CONTENT_TYPE_NAME}}

- **Source:** [{{DOMAIN_TERM}}]({{LINK_TO_UL}})
- **Used on:** {{SCREEN_NAME_1}}, {{SCREEN_NAME_2}}
- **Hierarchy / collections:** {{e.g. identity belongs to character}}
- **Key actions:** {{ACTION_1}}, {{ACTION_2}}, {{ACTION_3}}

<!-- duplicate for each shared content type -->

---

## Change log

Append a row whenever the canvas changes, in either direction (canvas → md or md → canvas).

| Date | Direction | Summary |
| --- | --- | --- |
| {{ISO_DATE}} | initial | First draft. |
