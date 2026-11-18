# UX sketch — screens drawn in the design canvas, match active fidelity

The questions to ask are in `ux.md`, under **Sketch** for the active fidelity. The shell's level of detail is that fidelity's **Scaffold** section. This file is the notation for the `user experience:` section.

The site map **is** the structure: a screen lives under the touchpoint it belongs to, inside the journey that reaches it, with its outbound links and its link to the drawn screen together in one place. There is no second SCREENS list — a screen is described once, where it sits.

**Draw screens in the design canvas, never as ASCII boxes.** Each screen is a greybox `.dc.html` artboard in the session's design canvas, so the person sees and comments on a real layout and the story explorer can later run it on the stories' fixtures. Draw it into the canvas's working version under the UX practice's root, `<ux root>/design-canvas/version-N/project/screens/{screen-slug}.dc.html` (start the next version from the latest when the latest is published, as `story_canvas.md` § Versions says), with the version's shared `styles/greybox.css`. Publish the version as a Claude Design canvas, record its link in `versions.json`, and update it in place on every refinement, so the sketch and the canvas never disagree. The sketch file holds the site map and links each screen to its artboard; the drawing itself lives only in the canvas, because a box drawn twice drifts.

What each artboard shows follows the fidelity: at **ia**, the screen's regions and representative rows, labelled; at **mockup**, its real controls in their states (selected, disabled, validation messages); at **specification**, brand and stub notes in the key. A screen's interaction notes go in its **key** in the sketch.

**Order:** journeys and touchpoints (`ia`) → screens with their outbound links and a regions artboard each (`ia`) → controls and states on each artboard (`mockup`) → brand/stub notes in the key (`specification`) → real frontend / backend wiring (`front_end_code`, usually outside this sketch).

**Do not annotate sketch lines.** No `<-i` / `<-m` / `<-s` (or any margin fidelity tags). Declare fidelity once at the top of the file.

**IA discipline:** no toolbar dumps, AC, or copy walls. ~4 user stories per screen. Tab states are **separate screens** under the same touchpoint; sibling chrome dimmed / `chrome: same as …`.

**Layouts:** pick from the reference library at `specifications/generic/` (`sidebar`, `tabbed`, `modal-dialog`, `form`, `list`, `split-screen`, `holy-grail`, `breadcrumb`, `kanban-board`, … — 43 patterns, one `.md` ASCII + one `.drawio` fragment per layout) — the default, unbranded set. If a specific brand applies (e.g. abd.works), use its sibling folder under `specifications/` instead (e.g. `specifications/abd-works/`). Open the matching file(s), read its areas, and lay the screen's artboard out on them rather than inventing a layout. `apply_layout` just records the chosen layout name — append the regions yourself.

## Notation — headings carry the hierarchy

Journeys, touchpoints, and screens nest through markdown headings, so each folds on its own. `## user experience:` is the section heading; the map starts one level below it.

| Heading | Holds |
|---|---|
| `### {Journey}` | an end-to-end journey, named for what the person is trying to get done |
| `#### {Touchpoint}` | one moment in that journey — where the person meets the product |
| `##### [ {screen name} ]` | one screen at that touchpoint, with its layout name on the same line |

Under a screen heading, one fenced block holds, in order: the screen's **outbound links**, its **canvas** artboard, its **Stories**, its **Domain terms**, and its **key**. A screen reached from more than one touchpoint is drawn under the touchpoint that owns it and referenced by name from the others.

Nav tags: `[Quick Action]` · `[top nav]` · `[drawer nav]` · `[secondary nav]` · `[action]` · `[system]`

---

## Template

~~~markdown
Fidelity: ia | mockup | specification | front_end_code

### {Journey}

#### {Touchpoint}

##### [ {screen name} ]                              {layout}

```
  ├─ [{nav_type}] {action} ──────────→ {Destination screen}
  └─ [{nav_type}] {action} ──────────→ {Destination screen}

  canvas: screens/{screen-slug}.dc.html

  Stories (~N): {Story} · {Story}
  Domain terms: {term} · {term}
  key:
    on [ Edit ] → {destination or effect}
    // stub/brand notes (specification only)
```

##### [ {next screen at this touchpoint} ]            {layout}

#### {Next touchpoint}
~~~

---

## Example

~~~markdown
Fidelity: ia

### Build A Character

#### Review The Character Sheet

##### [ character sheet — abilities ]                left panel + body

```
  ├─ [action] edit ──────────────────→ ability editor
  ├─ [action] selects Identities tab → character sheet — identities
  └─ [action] selects Movements tab ─→ character sheet — movements

  canvas: screens/character-sheet-abilities.dc.html

  Stories (~4): Update Ability Rank · Create Ability · Delete Ability · Set Key
  Domain terms: ability · ability rank · activation key
  key:
    left panel: the character tree · body: the ability list with Create, Delete, Edit
    on [ Edit ] → ability editor
```

##### [ character sheet — identities ]               left panel + body

```
  └─ [action] selects Abilities tab ─→ character sheet — abilities

  canvas: screens/character-sheet-identities.dc.html

  Stories (~2): Add Identity · Remove Identity
  Domain terms: identity
  key:
    chrome: same as character sheet — abilities, dimmed
```

#### Change An Ability

##### [ ability editor ]                             modal dialog

```
  └─ [action] save ──────────────────→ character sheet — abilities

  canvas: screens/ability-editor.dc.html

  Stories (~2): Update Ability Rank · Toggle Persistence
  Domain terms: ability rank
  key:
    on [ Save ] → character sheet — abilities (update rank)
    ! rank must be 1–10 shows under the rank field
    // rank update must leave the sheet consistent
```
~~~
