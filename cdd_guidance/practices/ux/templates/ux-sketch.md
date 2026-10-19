# UX sketch — visual ASCII, match active fidelity

The questions to ask are in `ux.md`, under **Sketch** for the active fidelity. The shell's level of detail is that fidelity's **Scaffold** section. This file is the notation for the `user experience:` section.

The site map **is** the structure: a screen lives under the touchpoint it belongs to, inside the journey that reaches it, with its outbound links and its box together in one place. There is no second SCREENS list — a screen is described once, where it sits.

Control types and states are drawn as glyphs inside the box — not written as `type=` / `state=` labels. Put a **key under each screen** for glyph meanings and interaction notes.

**Order:** journeys and touchpoints (`ia`) → screens with their outbound links, regions / rows / verb rows (`ia`) → visual controls + states inside boxes (`mockup`) → brand/stub notes in key (`specification`) → real frontend / backend wiring (`front_end_code`, usually outside this sketch).

**Do not annotate sketch lines.** No `<-i` / `<-m` / `<-s` (or any margin fidelity tags). Declare fidelity once at the top of the file. Mockup wiring lives in HTML — do not litter the ASCII with "this line is mockup" markers.

**IA discipline:** no toolbar dumps, AC, or copy walls. ~4 user stories per screen. Tab states are **separate screens** under the same touchpoint; sibling chrome dimmed / `chrome: same as …`.

**Layouts:** pick from the reference library at `specifications/generic/` (`sidebar`, `tabbed`, `modal-dialog`, `form`, `list`, `split-screen`, `holy-grail`, `breadcrumb`, `kanban-board`, … — 43 patterns, one `.md` ASCII + one `.drawio` fragment per layout) — the default, unbranded set. If a specific brand applies (e.g. abd.works), use its sibling folder under `specifications/` instead (e.g. `specifications/abd-works/`). Open the matching file(s), read its slots, and alter it for this screen rather than drawing the box from scratch. `apply_layout` just records the chosen layout name — append the regions yourself.

## Notation — headings carry the hierarchy

Journeys, touchpoints, and screens nest through markdown headings, so each folds on its own. `## user experience:` is the section heading; the map starts one level below it.

| Heading | Holds |
|---|---|
| `### {Journey}` | an end-to-end journey, named for what the person is trying to get done |
| `#### {Touchpoint}` | one moment in that journey — where the person meets the product |
| `##### [ {screen name} ]` | one screen at that touchpoint, with its layout name on the same line |

Under a screen heading, one fenced block holds, in order: the screen's **outbound links**, its **box**, its **Stories**, its **Domain terms**, and its **key**. A screen reached from more than one touchpoint is drawn under the touchpoint that owns it and referenced by name from the others.

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

  ┌─────────────────────────────┐
  │ {region}                    │
  │ {field} · {field}           │  — representative row
  │ [ Create ] [ Delete ]       │  — verb row
  │ name [____________]         │
  │ kind [ Model      ▾ ]       │
  │ [x] active   [ ] default    │
  │ › selected row ‹            │
  │ (dim) disabled action       │
  │ ! validation feedback       │
  └─────────────────────────────┘

  Stories (~N): {Story} · {Story}
  Domain terms: {term} · {term}
  key:
    [____] text · [▾] dropdown · [x]/[ ] check · [ btn ] button
    ›sel‹ selected · (dim) disabled · ! error
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

  ┌────────────────┬────────────────────────────┐
  │ ▼ All chars    │ Identities                 │
  │   ▶ Crowd 1    │ [ Abilities ]              │  inactive greyed
  │   › Char A ‹   │ Movements                  │
  │   Char B       ├────────────────────────────┤
  │                │ ability · rank · key       │
  │                │ › Strike · 3 · Q ‹         │
  │                │ Guard · 2 · E              │
  │                │ [ Create ] [ Delete ] [ Edit ]
  └────────────────┴────────────────────────────┘

  Stories (~4): Update Ability Rank · Create Ability · Delete Ability · Set Key
  Domain terms: ability · ability rank · activation key
  key:
    tree · list rows · [ btn ] button bar
    ▼/▶ expand · ›sel‹ selected
    on [ Edit ] → ability editor
```

##### [ character sheet — identities ]               left panel + body

```
  └─ [action] selects Abilities tab ─→ character sheet — abilities

  ┌──────────┬────────────────┐
  │ (dim)    │ [Identities]   │
  │ tree     │ Abilities      │
  │          │ Movements      │
  │          ├────────────────┤
  │          │ identity row   │
  │          │ [ Add ][ Remove ]
  └──────────┴────────────────┘

  Stories (~2): Add Identity · Remove Identity
  Domain terms: identity
  key:
    chrome: same as character sheet — abilities
    (dim) = shared chrome
```

#### Change An Ability

##### [ ability editor ]                             modal dialog

```
  └─ [action] save ──────────────────→ character sheet — abilities

  ┌─────────────────────────────┐
  │ ability name                │
  │ name [ Strike_________ ]    │
  │ rank [ 3 ▾ ]  key [ Q__ ]   │
  │ [x] persistent              │
  │ [ Save ] [ Cancel ]         │
  │ ! rank must be 1–10         │
  └─────────────────────────────┘

  Stories (~2): Update Ability Rank · Toggle Persistence
  Domain terms: ability rank
  key:
    [____] text · [▾] dropdown · [x] check · [ btn ] button
    ! error
    on [ Save ] → character sheet — abilities (update rank)
    // rank update must leave the sheet consistent
```
~~~
