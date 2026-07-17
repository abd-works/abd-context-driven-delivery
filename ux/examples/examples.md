# UX examples

## Sketch shape (IA → mockup)

Site map on top; screen boxes show what the user sees; key under each screen for glyphs/interactions. See `sketch-template.md`. No margin fidelity tags.

```
Fidelity: ia

═══════════════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════════════

character sheet — abilities
  └─ [action] edit ──────────────────→ ability editor

═══════════════════════════════════════════════════════════
  SCREENS
═══════════════════════════════════════════════════════════

[ character sheet — abilities ]                 left panel + body
  ┌────────────────┬────────────────────────────┐
  │ ▼ All chars    │ [ Abilities ]              │
  │   › Char A ‹   ├────────────────────────────┤
  │                │ › Strike · 3 · Q ‹         │
  │                │ [ Create ] [ Delete ] [ Edit ]
  └────────────────┴────────────────────────────┘
  Stories (~3): Create Ability · Delete Ability · Update Ability Rank
  Domain terms: ability · ability rank
  key:
    tree · list · [ btn ] button
    ›sel‹ selected
    on [ Edit ] → ability editor
```

## Channel round-trip

`JsonUxMap` ↔ `DrawioUxMap` (drawio-ux CLI: Detailed IA + Site Map) ↔ `HtmlUxMap` (mockup left, stories at bottom).

## Artifact layout (colocated)

```
sandbox/<epic>/
  ux-map.json
  <user-goal>.html                           <- mockup+
  <sub-epic>/<leaf>/…_stories.py|.js
  .context/
    information-architecture.drawio           <- ia (drawio-ux CLI)
    ux-sketch.md
    ux-context.md
```

IA render: `Ux.transform` / `DrawioUxMap.render` → `node ux/diagram/drawio/drawio_ux.mjs write …`

## Increment 1 sandbox

Live tree: `sandbox/play-core-mechanics/`

- IA: `.context/information-architecture.drawio`
- Sketch / context: `.context/ux-sketch.md`, `.context/ux-context.md`
- Model: `ux-map.json`
- Mockup: `play-core-mechanics.html`
- Stories JS beside Python dicts under `manage-character-sheet/` and `resolve-checks/`
- Emit helper: `python ux/scripts/emit_story_javascript.py <story.py>…`
- Open the HTML via a static server; **Check** / **Done** switch screens; story names load from JS modules into the footer.
