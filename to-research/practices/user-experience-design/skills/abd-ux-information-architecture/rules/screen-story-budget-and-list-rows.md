# Rule: Story budget, list rows, and edit creates a new screen

**Scanner:** AI review (run after `initial-ia.md` is authored and after the canvas is drawn)

---

## Rule 1 — Story budget: ~4 user stories per screen

A screen should carry approximately 4 user stories. The stories on a screen are the ones whose primary interaction occurs on that screen's content region — not stories that happen elsewhere and are vaguely related.

More than ~4 stories on one screen almost always means one of:
- A tab state has not been separated into its own screen
- A detail/editor form has not been given its own screen
- Stories from different screens have been bundled together

### DO

- Assign each story to the screen where its primary interaction takes place. If two stories share a screen, verify that both are directly satisfied by a visible region and action on that screen.
- When a screen reaches 5+ stories, stop and look for the missed decomposition before proceeding.

  **Example (pass) — crowd manager — abilities (4 stories):**
  ```
  Stories:
    Create Animated Ability   → ability list / create
    Delete Animated Ability   → ability list / delete
    Set Ability Activation Key → ability list row / set key
    Toggle Ability Persistence → ability list row / toggle persistent
  ```

### DO NOT

- Dump all stories that touch a domain concept onto one screen.

  **Example (fail):**
  ```
  Stories:
    Create Animated Ability · Edit Animated Ability · Delete Animated Ability
    Set Ability Activation Key · Toggle Ability Persistence
    Add Movement Element to Ability · Add Sound Element to Ability
    Add FX Element to Ability · Add Reference Element · Add Sequence Element
    Add Pause Element · Add Load-Identity Element · Reorder Animation Elements
    Play Animated Ability on Character · Stop Active Ability
  ```
  This is 15 stories on one screen. It means the ability editor screen, the desktop play screen, and the crowd manager — abilities screen have all been collapsed into one node.

---

## Rule 2 — List regions show rows, not prose

A region that displays a collection is drawn as a set of representative item rows. Each row contains the visible field names only. Below the rows is a single verb row of actions.

This applies everywhere — in the spec, in the canvas prompt, and on the canvas.

### DO

- Show 2–3 representative rows with field names. Add a verb row below.

  **Example (pass):**
  ```
  ability list
    row: name · activation key · persistent · attack
    row: name · activation key · persistent · attack
    verb row: create · delete · play · stop · edit · reorder
  ```

- On the canvas: each row is a small horizontal box; the verb row is a strip directly below the last row.

### DO NOT

- Describe the list in prose form.

  **Example (fail):**
  ```
  ability list — ordered list of animated abilities; active indicator, persistent flag, attack flag,
  activation key; key actions: create, delete, play, stop, set activation key, toggle persistence,
  set as default
  ```
  This is a specification paragraph, not a layout. It tells the reader nothing about what the screen looks like.

- Write "per item: …" to enumerate fields.

  **Example (fail):**
  ```
  per spawned character node:
    name · active badge · combat state (attacker/defender/stunned/dying/dead)
    distance progress bar
    click select · drag move · double-click activate
  ```
  This is prose. Draw a box per spawned character node instead.

---

## Rule 3 — "Edit" creates a new screen

When a verb row contains "edit" (or "configure", "detail", "open"), the edit action transitions to a new named screen — a detail/editor form. That screen is a full site-map node with its own box, its own content regions (the form fields the user edits), its own ~4 stories, and a transition arrow back to the parent screen.

### DO

- Add a transition arrow from the list screen to a named detail screen.

  **Example (pass):**
  ```
  crowd manager — abilities  ──► ability editor   trigger: "opens ability editor"

  #### ability editor
  - Layout: body form
  - Content regions:
      ability header
        row fields: name · activation key · persistent · attack · area-effect
        verb row: save · cancel
      element tree
        row: [FX] resource · ...
        row: [MOV] resource · ...
        row: [sound] file · volume
        ... (one row type per animation element type)
        verb row: add element · drag reorder · delete
  - Stories (~4): Edit Animated Ability · Add FX Element · Add MOV Element · Reorder Elements
  ```

### DO NOT

- Leave "edit" as an action with no destination screen.

  **Example (fail):**
  ```
  ability list
    verb row: create · delete · play · stop · **edit** · reorder
  ```
  …with no transition to an ability editor screen anywhere in the IA. The edit action is orphaned.
