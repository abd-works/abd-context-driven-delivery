# UX sketch — visual ASCII, match active fidelity

Sketch the **site map first** (connection tree), then **screen boxes** that show what the user sees. Control types and states are drawn as glyphs inside the box — not written as `type=` / `state=` labels. Put a **key under each screen** for glyph meanings and interaction notes.

**Order:** site map (`ia`) → screen boxes with regions / rows / verb rows (`ia`) → visual controls + states inside boxes (`mockup`) → brand/stub notes in key (`specification`) → real frontend / backend wiring (`code`, usually outside this sketch).

**Do not annotate sketch lines.** No `<-i` / `<-m` / `<-s` (or any margin fidelity tags). Declare fidelity once at the top of the file. Mockup wiring lives in HTML — do not litter the ASCII with “this line is mockup” markers.

**IA discipline:** no toolbar dumps, AC, or copy walls. ~4 user stories per screen. Tab states are **separate boxes**; sibling chrome dimmed / `chrome: same as …`.

**Layouts:** pick from the thin catalog (`sidebar`, `tabbed`, `modal`, `form`, `stack`, `split-screen`, `holy-grail`, …) — `apply_layout` seeds named region slots.

---

## Template

```
Fidelity: ia | mockup | specification | code

═══════════════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════════════

{Screen name}
  ├─ [{nav_type}] {action} ──────────→ {Destination screen}
  └─ [{nav_type}] {action} ──────────→ {Destination screen}

{Screen name}
  └─ [action] {action} ──────────────→ {Destination screen}

Nav tags: [Quick Action] · [top nav] · [drawer nav] · [secondary nav] · [action] · [system]

═══════════════════════════════════════════════════════════
  SCREENS
═══════════════════════════════════════════════════════════

[ {screen name} ]                                    {layout}
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
    [____] text · [▾] dropdown · [x]/ ] check · [ btn ] button
    ›sel‹ selected · (dim) disabled · ! error
    on [ Edit ] → {destination or effect}
    // stub/brand notes (specification only)
```

---

## Example

```
Fidelity: ia

═══════════════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════════════

character sheet — abilities
  ├─ [action] edit ──────────────────→ ability editor
  ├─ [action] selects Identities tab → character sheet — identities
  └─ [action] selects Movements tab ─→ character sheet — movements

ability editor
  └─ [action] save ──────────────────→ character sheet — abilities

═══════════════════════════════════════════════════════════
  SCREENS
═══════════════════════════════════════════════════════════

[ character sheet — abilities ]                 left panel + body
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

[ ability editor ]                              modal dialog
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

[ character sheet — identities ]     [ character sheet — movements ]
  ┌──────────┬────────────────┐        ┌──────────┬────────────────┐
  │ (dim)    │ [Identities]   │        │ (dim)    │ Identities     │
  │ tree     │ Abilities      │        │ tree     │ Abilities      │
  │          │ Movements      │        │          │ [Movements]    │
  │          ├────────────────┤        │          ├────────────────┤
  │          │ identity row   │        │          │ movement row   │
  │          │ [ Add ][ Remove ]       │          │ [ Add ][ Remove ]
  └──────────┴────────────────┘        └──────────┴────────────────┘
  chrome: same as character sheet — abilities
  key: (dim) = shared chrome

// context: rank update must leave sheet consistent
```
