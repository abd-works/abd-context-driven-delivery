---
name: ux-front_end_code
description: "Provide guidance for creating IA, mockups, and front-end code."
disable-model-invocation: true
---

# ux-front_end_code

Use ux guidance at `front_end_code` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@ux-mockup
@ux-ia

# Contexts

UX looks at the product through user navigatin and information architecture, from layout and transitions to more formal screens, regions, and controls — how users see and act on the solution — mapped at increasing fidelity.

**Canonical model** (reuse, do not reinvent): `UxMap` → `Screen` → `Region` → `Control` → `Interaction`, plus `Transition`, `ContentType`, `NavComponent` on the map. Optional `UxContext` holds notes/invariants not visible on screens.

**Layout (mirror Stories; colocated):**

```
sandbox/<epic>/
  ux-map.json                              <- canonical model (optional peer)
  <user-goal>.html                        <- mockup+ (one file per concrete user goal)
  <sub-epic>/…_stories.py|.js
  .context/
    information-architecture.drawio        <- ia (drawio-ux CLI: Detailed IA + Site Map)
    ux-sketch.md                           <- scratch sketch
    ux-context.md                          <- optional notes/invariants
```

Sketch/context MD stay in `.context/` (same pattern as other generators). Story / object-model JS stay where Stories / CE emit them; HTML imports those modules.

**Stories + object model:** `UxMap.story_references` / `object_references` store **paths** to Stories / Clean Engineering JS artifacts. If missing, run that generator’s `transform` to `javascript`. Mockup/spec HTML imports those paths.

**Story Demo shell (mockup+):** Generated HTML uses `templates/html/mockup_shell.html` — product screens **LEFT**, story explorer **RIGHT**. `story-demo/mount-generated-mockup.js` loads `create{Story}Story` exports, runs `PlayDualRunner`, and paints the explorer. Serve from **repo root** so `/context_tools/...` imports resolve.

**Worked example:** `context_tools/ux/examples/manage-customer-orders/` (Place New Order mockup + stories + shopping_cart domain) — general UX output sample that happens to run in the Story Demo shell.

**One control model:** `ux_model.Control` is vanilla. Controls that bind to GWT steps are `StoryDemoControl` (`bound_field` + `story_steps`) — HTML emits `data-bound-field` / `data-story-steps`. Do **not** invent a second page/control model in freehand HTML.

**Interactive (domain-agnostic):** `StoryDemoControl` may also carry `set_input`, `item_story_steps`, `item_value`, `item_label`. Emit:
- `number` / `quantity` → `data-input-field`
- `bound-list` / `list-host` → `data-bound-list` + `data-bound-field` (expose path) + optional `data-item-story-steps` / `data-set-input`  
Do **not** bake product words (catalog, cart) into the template — those are bound_field paths / story language only.

**Markdown:** optional context only (thinking, invariants, interaction notes). Primary path is **drawio (IA) → html (mockup/spec)**.

**Specifications (layouts):** `specifications/` holds the full IA screen-template set as ready-to-adapt reference artifacts, one sibling folder per style:

- `specifications/generic/` — **default.** One `.md` ASCII reference + one `.drawio` XML fragment per layout (accordion, breadcrumb, kanban-board, sidebar, tabbed, wizard-stepper, … 43 patterns), mirrored verbatim from abd-skills. No brand.
- `specifications/abd-works/` — the same 43 layouts as real, brand-styled HTML (`<id>.html` + `index.html`), all sharing `abd-works-brand.css` (tokens/type/components copied from the `abd-visual-branding` SKILL.md: colors, Inter/JetBrains Mono type scale, buttons, cards, dual Executive/Engineering mode). Use this folder instead of `generic/` whenever the screen needs the abd.works brand (see `brand-is-opt-in` below).
- Add further sibling folders under `specifications/` for other brands/styles the same way; each folder's own files stay self-contained (own stylesheet, own copies).

Before sketching a screen's ASCII box, drawio region cells, or brand-layer html, open the matching file(s) in the specification folder that applies — `generic/` unless a specific brand is asked for or already established for this work — read its slots, and alter that file for the real screen. Do not draw box art, drawio cells, or brand markup from scratch when one of these already covers the shape. `Screen.apply_layout(layout_id)` just records that choice as the layout name; append the real `Region`s yourself from the slots you just read.

**Channels:** drawio, html, markdown, json — peer parse/render; `transform` moves sideways at the same fidelity. One `html` channel deepens by fidelity (js interactions → optional brand layer + honest stubs at **mockup** → real frontend at **front_end_code**; host FE stacks welcome at **front_end_code**).

---

This skill operates at **multiple levels of fidelity**. Start from grill + sketch and deepen. Each level **adds** artifacts — do not invent detail from a deeper fidelity.

| Fidelity | Default format | Output |
|---|---|---|
| **ia** | drawio | Site map + per-screen regions/nav (html optional via transform) |
| **mockup** | html | Wired greybox screens (html+js); one HTML per concrete user goal (not one file per screen, not one mega-file per epic); drawio remains a peer channel; optional brand layer; honest stub catalogue |
| **front_end_code** | html (or host FE stack) | Real frontend — production UI wired to real backend; not Story Demo / greybox alone |

**Templates (AI generate):** drawio + html under `templates/`. Markdown context template optional. Other formats via channels / `transform`.

**Cross-format scanners:** channels parse into the canonical model; scanners read model fields only — never file syntax.

---

## Shared rules

- **`tab-states-are-separate-screens`** — N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.
- **`screen-story-budget`** — ~4 user stories per screen; more signals missed decomposition.
- **`screen-names-use-domain-terms`** — Screen labels trace to domain language when it exists.
- **`ia-named-regions-only`** — At IA, regions are named slots; no control detail yet.
- **`story-domain-js-imported`** — At mockup+, when context_tools/stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

---

## front_end_code

**Default format:** html (or the host app’s frontend stack)

**Goal:** Real frontend for the product — production UI and client wiring to a real backend. Not greybox, not Story Demo as the shipping surface, not stub-only services.

- Replace mockup stubs with the real client (routing, state, API calls, auth as needed).
- Call CE **code**-fidelity backend / Production collaborators — not Fake factory or in-browser demo domain alone.
- Story Demo may still exist as a review/exploration shell; it is not the product UI at this fidelity.
- Carry IA vocabulary and control decisions forward; do not redecide screens under a new product name.

### Rules

- **`real-frontend-not-mockup`** — Shipping UI is production frontend code, not the greybox Story Demo frame.
- **`real-backend-wired`** — Client talks to real services/persistence (CE **code**); no silent Fake path as the only path.
- **`upstream-decisions-carried`** — Layout and domain terms from earlier fidelities stay authoritative.

## Sketching

When sketching, use the following sketch template. Do not use the produce templates below — stop reading this skill when sketching.

# UX sketch — visual ASCII, match active fidelity

Sketch the **site map first** (connection tree), then **screen boxes** that show what the user sees. Control types and states are drawn as glyphs inside the box — not written as `type=` / `state=` labels. Put a **key under each screen** for glyph meanings and interaction notes.

**Order:** site map (`ia`) → screen boxes with regions / rows / verb rows (`ia`) → visual controls + states inside boxes (`mockup`) → brand/stub notes in key (`specification`) → real frontend / backend wiring (`front_end_code`, usually outside this sketch).

**Do not annotate sketch lines.** No `<-i` / `<-m` / `<-s` (or any margin fidelity tags). Declare fidelity once at the top of the file. Mockup wiring lives in HTML — do not litter the ASCII with “this line is mockup” markers.

**IA discipline:** no toolbar dumps, AC, or copy walls. ~4 user stories per screen. Tab states are **separate boxes**; sibling chrome dimmed / `chrome: same as …`.

**Layouts:** pick from the reference library at `specifications/generic/` (`sidebar`, `tabbed`, `modal-dialog`, `form`, `list`, `split-screen`, `holy-grail`, `breadcrumb`, `kanban-board`, … — 43 patterns, one `.md` ASCII + one `.drawio` fragment per layout) — the default, unbranded set. If a specific brand applies (e.g. abd.works), use its sibling folder under `specifications/` instead (e.g. `specifications/abd-works/`). Open the matching file(s), read its slots, and alter it for this screen rather than drawing the box from scratch. `apply_layout` just records the chosen layout name — append the regions yourself.

---

## Template

```
Fidelity: ia | mockup | specification | front_end_code

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

## Templates

### html

## mockup.html

<!DOCTYPE html>
<!--
  AI mockup template (Story Demo shell).
  Prefer filling the model + HtmlUxMap.render (uses mockup_shell.html).
  When authoring HTML directly, keep this split: product LEFT + explorer RIGHT.

  Controls that participate in a story step MUST be StoryDemoControl in the model, which emits:
    data-bound-field="…"
    data-story-steps='[{"kind":"when","label":"…"}]'
  Serve from repo root. mount-generated-mockup.js collects create{Story}Story exports.
-->
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>UX — {{SCOPE}}</title>
  <style>
    body { margin: 0; font-family: ui-monospace, Consolas, monospace; }
    #shell { display: grid; grid-template-columns: 1fr 1fr; min-height: 100vh; }
    #story-demo-frame { border-right: 1px solid #ccc; padding: 1rem; }
    #explorer-frame { padding: 1rem; }
    .control.emphasized { outline: 2px solid #2563eb; }
    .control.tinted { background: #fecaca; }
  </style>
</head>
<body data-story-demo-shell>
  <header>
    <span data-story-demo-mode>Play</span>
    <button type="button" data-set-mode="Play">Play</button>
    <button type="button" data-set-mode="Interactive">Interactive</button>
  </header>
  <div id="shell">
    <section id="story-demo-frame">
      <main id="mockup">
        <!-- screens / regions / controls — emit data-story-steps on StoryDemoControls -->
      </main>
    </section>
    <section id="explorer-frame">
      <button type="button" data-reset>Reset</button>
      <ul data-explorer-tree></ul>
      <button type="button" data-play-next>Play next</button>
      <p data-explorer-message hidden></p>
      <p data-story-demo-status></p>
      <footer id="stories"><ul><!-- story names --></ul></footer>
    </section>
  </div>
  <script type="module" src="{{STORY_MODULE}}" data-ux-story-ref></script>
  <script type="module" src="{{DOMAIN_MODULE}}" data-ux-object-ref></script>
  <script type="module" src="/context_tools/ux/story-demo/mount-generated-mockup.js"></script>
</body>
</html>


## mockup_shell.html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>UX — @@TITLE@@</title>
  <style>
    :root { --ink: #222; --line: #666; --wash: #f0f0f0; --sel: #dbeafe; --emph: #2563eb; --tint: #fecaca; }
    body { margin: 0; font-family: ui-monospace, Consolas, monospace; color: var(--ink);
           min-height: 100vh; background: #fafafa; }
    header.shell-bar { display: flex; gap: 0.75rem; align-items: center; padding: 0.75rem 1rem;
                       border-bottom: 1px solid #ccc; background: #fff; }
    header.shell-bar h1 { font-size: 1rem; margin: 0; flex: 1; }
    header.shell-bar button { font: inherit; padding: 0.25rem 0.6rem; cursor: pointer; }
    header.shell-bar button.active { background: var(--sel); outline: 1px solid #6c8ebf; }
    #shell { display: grid; grid-template-columns: 1fr 1fr; min-height: calc(100vh - 3rem); }
    #story-demo-frame, #explorer-frame { padding: 1rem; overflow: auto; }
    #story-demo-frame { border-right: 1px solid #ccc; }
    .screen { border: 1px dashed var(--line); margin-bottom: 1rem; padding: 0.75rem;
               background: #fff; max-width: 52rem; }
    .screen[hidden] { display: none; }
    .screen[data-layout="modal"] {
      max-width: 28rem; margin: 2rem auto; border-style: solid;
      box-shadow: 0 0 0 9999px rgba(0,0,0,0.12);
    }
    .layout { color: #666; font-size: 0.85rem; margin-top: -0.5rem; }
    .regions { display: flex; flex-direction: column; gap: 0.5rem; }
    .screen[data-layout="sidebar"] .regions { display: grid; grid-template-columns: 12rem 1fr; }
    .screen[data-layout="split-screen"] .regions { display: grid; grid-template-columns: 1fr 1fr; }
    .screen[data-layout="holy-grail"] .regions {
      display: grid; grid-template-columns: 8rem 1fr 8rem;
      grid-template-areas: "header header header" "nav body aside" "footer footer footer";
    }
    .screen[data-layout="holy-grail"] .region[data-slot="header"] { grid-area: header; }
    .screen[data-layout="holy-grail"] .region[data-slot="nav"] { grid-area: nav; }
    .screen[data-layout="holy-grail"] .region[data-slot="body"] { grid-area: body; }
    .screen[data-layout="holy-grail"] .region[data-slot="aside"] { grid-area: aside; }
    .screen[data-layout="holy-grail"] .region[data-slot="footer"] { grid-area: footer; }
    .screen[data-layout="tabbed"] .region[data-slot="tab-bar"] { background: #e8e8e8; }
    .region { margin: 0; padding: 0.5rem; border: 1px solid #ddd; background: var(--wash); }
    .region h3 { margin: 0 0 0.5rem; font-size: 0.9rem; }
    .control { display: block; margin: 0.35rem 0; }
    .control[hidden], .control.hidden { display: none !important; }
    .control.button { display: inline-block; margin-right: 0.35rem;
                       padding: 0.25rem 0.6rem; border: 1px solid var(--ink); background: #eee;
                       cursor: pointer; font: inherit; }
    .control.button.primary { background: #e5e5e5; font-weight: 600; }
    .control.button.emphasized, .control.emphasized { outline: 2px solid var(--emph); background: #eff6ff; }
    .control.button.tinted, .control.tinted { background: var(--tint); }
    .control.selected, .tree-node.selected { background: var(--sel); outline: 1px solid #6c8ebf; }
    .control.disabled, .tree-node.dimmed { opacity: 0.45; }
    .control.error { color: #a00; }
    input[type="text"], select { font: inherit; padding: 0.15rem 0.35rem;
                                   border: 1px solid var(--ink); background: #fff; min-width: 8rem; }
    .tree-node { padding: 0.1rem 0.25rem; cursor: pointer; }
    .tree-node .twist { display: inline-block; width: 1.2rem; }
    .tree-node[data-role="folder"] { font-weight: 600; cursor: default; }
    .screen-stories { font-size: 0.85rem; color: #444; }
    .key { font-size: 0.8rem; color: #555; margin-top: 0.75rem; }
    .panel { border: 1px dashed var(--line); background: #fff; padding: 0.75rem; }
    #explorer-tree ul { margin: 0.25rem 0 0.25rem 1rem; padding: 0; list-style: none; }
    #explorer-tree li.current, #explorer-tree .current { background: var(--sel); font-weight: 600; }
    .message { color: #a00; margin-top: 0.75rem; min-height: 1.2rem; }
    .chrome { margin-top: 1rem; display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
    .status { font-size: 0.8rem; color: #555; margin-top: 0.5rem; }
    .toast { position: fixed; right: 1rem; bottom: 1rem; background: #222; color: #fff;
              padding: 0.5rem 0.75rem; font-size: 0.85rem; display: none; z-index: 2; }
    .toast.show { display: block; }
  </style>
</head>
<body data-story-demo-shell>
  <header class="shell-bar">
    <h1>@@TITLE@@ · <span data-story-demo-mode>Play</span></h1>
    <button type="button" data-set-mode="Play" class="active">Play</button>
    <button type="button" data-set-mode="Interactive">Interactive</button>
  </header>

  <div id="shell" data-layout="split-screen">
    <section id="story-demo-frame" aria-label="Product mockup">
      <main id="mockup">
        @@SCREENS@@
        <p class="key">LEFT: product screens · «emph» / bind via data-bound-field · Interactive uses data-story-steps</p>
      </main>
    </section>

    <section id="explorer-frame" aria-label="Story explorer">
      <div class="panel">
        <h2>explorer</h2>
        <div class="chrome">
          <button type="button" data-reset>Reset</button>
        </div>
        <ul id="explorer-tree" data-explorer-tree></ul>
        <div class="chrome">
          <button type="button" data-play-next>▶▶ Play next</button>
        </div>
        <p class="message" data-explorer-message hidden></p>
        <p class="status" data-story-demo-status></p>
        <p class="key">RIGHT: GWT from collect · Play next is chrome only · not product controls</p>
        <footer id="stories" style="margin-top:1rem;border-top:1px solid #ddd;padding-top:0.5rem;">
          <strong>Stories</strong>
          <ul id="story-list">@@STORIES_LIST@@</ul>
        </footer>
      </div>
    </section>
  </div>

  <div id="toast" class="toast" role="status"></div>
@@ENSURE_HINT@@@@STORY_IMPORTS@@
@@OBJECT_IMPORTS@@
  <script type="module" src="/context_tools/ux/story-demo/mount-generated-mockup.js"></script>
  <script type="module">
    // Generic screen nav (data-goto). Story Play / Interactive is mounted by mount-generated-mockup.js.
    const transitions = [
@@TRANSITIONS_JS@@
    ];
    const toast = document.querySelector('#toast');
    const list = document.querySelector('#story-list');
    const seen = new Set([...list.querySelectorAll('li')].map((li) => li.textContent));

    for (const script of document.querySelectorAll('[data-ux-story-ref]')) {
      try {
        const mod = await import(script.getAttribute('src'));
        const names = mod.storyNames
          || Object.values(mod)
              .filter((value) => value && typeof value === 'object' && value.story)
              .map((value) => value.story);
        for (const name of names || []) {
          if (!name || seen.has(name)) continue;
          seen.add(name);
          const li = document.createElement('li');
          li.textContent = name;
          list.appendChild(li);
        }
      } catch (_err) {
        // Artifact may be missing until Stories transform / JS emit runs.
      }
    }

    function flash(msg) {
      toast.textContent = msg;
      toast.classList.add('show');
      clearTimeout(flash._t);
      flash._t = setTimeout(() => toast.classList.remove('show'), 1600);
    }

    function showScreen(name) {
      for (const screen of document.querySelectorAll('.screen')) {
        const title = screen.querySelector('h2')?.textContent?.trim();
        screen.hidden = title !== name;
      }
    }

    function visibleScreen() {
      return [...document.querySelectorAll('.screen:not([hidden])')][0];
    }

    document.querySelectorAll('[data-goto]').forEach((el) => {
      el.addEventListener('click', () => {
        const dest = el.getAttribute('data-goto');
        showScreen(dest);
        flash(`→ ${dest}`);
      });
    });

    document.querySelectorAll('[data-trigger]').forEach((el) => {
      el.addEventListener('click', () => {
        if (el.hasAttribute('data-story-steps')) return; // Story Demo owns these in Interactive
        const trigger = el.getAttribute('data-trigger');
        const from = visibleScreen()?.querySelector('h2')?.textContent?.trim();
        const hit = transitions.find((t) => t.from === from && t.trigger === trigger)
          || transitions.find((t) => t.trigger === trigger);
        if (hit) showScreen(hit.to);
      });
    });
  </script>
  <!-- ux-map-json:
@@MODEL_JSON@@
  -->
</body>
</html>


See examples in `context_tools/ux/examples/` if needed.