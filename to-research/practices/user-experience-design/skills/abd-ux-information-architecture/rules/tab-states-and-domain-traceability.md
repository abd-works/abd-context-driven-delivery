# Rule: Tab states are separate screens; domain terms are visible-only

**Scanner:** AI review (run after `initial-ia.md` is authored and after the canvas is drawn)

---

## Rule 1 — Each tab state is a separate screen on the site map

A panel with N tabs produces N **separate screen nodes**. Each is named `{{parent screen}} — {{tab label}}`. The tab-state screens are siblings on the site map, connected by "selects {{tab}} tab" transition arrows. The outer chrome (toolbar, sidebar, status bar) is shared and noted once on the primary screen; sibling screens reference it as `chrome: same as {{primary screen}}`.

### DO

- Create a separate `#### crowd manager — identities`, `#### crowd manager — abilities`, and `#### crowd manager — movements` screen block in the spec. Connect them with tab-switch arrows on the canvas.

  **Example (pass):**
  ```
  #### crowd manager — identities
  - Inactive tabs (greyed): Abilities, Movements
  - Content regions:
      identity list
        rows: name · type (Model/Costume) · active · default
        verb row: add · remove · set default · set active · reorder
  - Stories (~4): Add Identity · Set Default Identity · Set Active Identity · Remove Identity

  #### crowd manager — abilities
  - Inactive tabs (greyed): Identities, Movements
  - Content regions:
      ability list
        rows: name · activation key · persistent · attack
        verb row: create · delete · play · stop · edit · reorder
        edit → new screen: ability editor
  - Stories (~4): Create Animated Ability · Delete · Set Activation Key · Toggle Persistence
  ```

- On the canvas, draw each tab state as a separate screen box. Show the inactive tab names as greyed labels in the tab bar inside the box.

### DO NOT

- Describe a tabbed panel as one screen with sub-region blocks per tab.

  **Example (fail):**
  ```
  #### crowd manager
  - character detail panel — tab: Identities
      identity list: rows, actions
  - character detail panel — tab: Abilities
      ability list: rows, actions
  ```
  This collapses three screens into one and hides the transitions between them.

- Use "tabs: X, Y, Z" shorthand in a single screen block.

  **Example (fail):**
  ```
  character detail panel — tabs: Identities, Abilities, Movements
  ```

---

## Rule 2 — Domain terms per screen are visible-only

A domain term belongs on a screen's annotation only if it names something the user can **see or directly interact with** on that screen: a data field label, a list row type name, a region name, or a screen name.

Internal model concepts that are not visible as UI text are excluded. The full sub-concept hierarchy of a key abstraction is never listed wholesale — only the sub-concepts that appear as distinct named rows or fields.

### DO

- List only the terms that label a row field, a row type, or a region on this screen.

  **Example (pass) — crowd manager — abilities:**
  ```
  Domain terms: animated ability · activation key · persistent · attack
  ```
  These are the field names visible in the ability list rows.

### DO NOT

- Copy the full KA concept list into the domain terms annotation.

  **Example (fail):**
  ```
  Domain terms: animated ability · animation element · FX effect element · MOV element ·
    sound element · pause element · sequence element · reference ability · identity element ·
    animation resource · attack · on-hit animation · And sequence · Or sequence
  ```
  Most of these are not visible on the abilities list screen. They belong on the ability editor screen, where those element types appear as distinct rows.

- Include internal model terms that never appear as visible UI text.

  **Example (fail):**
  ```
  Domain terms: option group · animation sequence type · persistence flag
  ```
  These are implementation concepts. The user sees "ability", "activation key", "persistent" — use those.

---

## Completeness test (run before marking the IA done)

Verify against `docs/ux/initial-ia.md` **and** the canvas:

- [ ] Every tab-bearing panel is represented as N separate screen blocks (one per tab state), not as one block with sub-regions.
- [ ] Every tab-state screen block has: inactive tabs listed, chrome noted by reference, ~4 user stories, domain terms (visible only).
- [ ] The canvas shows each tab state as a separate screen box with greyed inactive tab labels and tab-switch arrows between siblings.
- [ ] A **story trace table** (build step 4a) exists with every GM story mapped to screen, region, action/trigger — no empty cells.
- [ ] A **domain term trace table** (build step 4b) exists with every term mapped to screen and visible element — no "annotation only" entries without justification.
- [ ] Every "edit" action in a verb row has a corresponding transition to a named detail/editor screen.
- [ ] No screen carries more than ~4 user stories without a documented reason.
- [ ] Domain terms per screen are limited to visible field labels and row type names (max ~5).
