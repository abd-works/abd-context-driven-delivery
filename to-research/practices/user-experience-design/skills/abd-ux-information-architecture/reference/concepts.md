# abd-information-architecture — Concepts

## What is information architecture?

**Information architecture (IA)** is the practice of structuring, organizing, and labeling the surfaces and content of a solution so users can find what they need and understand where they are. It covers two dimensions — **navigation** (how a user moves through the solution and the components that carry that movement) and **content** (what lives on each surface, how it is grouped, what it is called, and what users can do with it).

A **site map** — the inventory of screens and the directed transitions between them — is one component of the IA: the navigation backbone. This skill produces it alongside the rest of the IA in a single low-fidelity pass.

## Core outputs

The IA is captured on a single canvas covering two dimensions.

### Navigation

- **Site map** — screens as named boxes, with directed transitions between them showing how users flow from one screen to the next. There should be a simple, obvious mapping from stories to this layer: in-scope stories live on screens, and the events in those stories drive the transitions.
- **Per-screen layout** — for each screen, the standard layout template it follows in conventional terms (e.g. `header + body + footer`, `header + left panel + body (2-column)`, `header + 3-column body`, `header + body grid (2 columns × 2 rows)`, `modal dialog`). The layout names the slots; the regions (next bullet) name what fills each slot.
- **Navigational components** — each screen has an initial description and approximate layout of the persistent surfaces that carry navigation: menus, primary navigation, sidebars, headers, footers, breadcrumbs, link groups. Named regions only, no controls, no styling.

### Content

- **Content types** — the kinds of things users read, create, or act on; where the context provides domain terms, concepts, or classes, a content type is typically one of those. Capture the hierarchy of each content type and any collections it belongs to.
- **Per-screen content layout** — for each screen, a categorized layout of what content lives there, visually depicting high-level relationships (hierarchy, collection) and the key navigation between content.
- **Labels and tags** — preliminary labels and tags needed to identify content elements on the canvas.
- **Key actions per content type** — the headline things a user can do with each content type (browse, create, edit, archive, share, …). There should be a simple, obvious mapping from stories to actions: each in-scope story that acts on a content type contributes an action to that type. No controls, no copy.

## Stories and domain as sources

The story map and the Domain Language are **sources** for this skill, not its subjects. They feed the IA but are not what it speaks in.

- Use **UX terms** on UX output — *screen*, *region*, *navigation*, *sidebar*, *header*, *footer*, *content type*, *action*, *label*, *tag*.
- When a story or a domain concept appears on the canvas, include only its **name** — the story title or the domain term — and a link to the full source. No acceptance criteria, no full definitions, no behavioral detail on the IA artifact.
- Stories and domain concepts in scope must be **referenceable** from the IA: every in-scope *user* story is reachable from a screen (as a story name listed on it, or as a transition trigger); every in-scope domain concept that the user perceives appears as a screen, content type, label, or action.

## Scope

The slice of the solution this IA covers — typically one **increment**, one **epic**, or one **sprint**. Only stories and domain concepts inside the scope contribute screens, navigation, content types, and labels.

## Screen

A **screen** is a distinct user-visible state — what the user sees and acts on when one set of stories is active. Two states that differ only in transient data are the same screen; states that differ in which regions exist, which navigational components are present, or which actions are available are different screens.

**Story budget signal:** a screen should carry ~4 user stories. Consistently more than ~4 almost always means a tab state, a detail/edit screen, or a mode has not been separated out. Each story on a screen must be directly and visibly satisfied by a region or action on that screen — not by a region on a sibling or ancestor screen.

## Transition

A **transition** is a directed move from one screen to another. Its label names the **trigger** — the user action or system event that causes the move — using a UX term when the trigger is structural (e.g. *opens primary nav*) or a domain concept name when the trigger is domain-specific (e.g. *submits valid path*), with a link to the source story or term.

## Layout templates

Use `node $DUXCLI templates` to print the full list with ASCII diagrams. Available templates and their slots:

```
stack        — single column                          slot: body
modal        — centered overlay dialog (rounded)      slot: body
form         — single-column form (stacked inputs)    slot: body
sidebar      — left panel + right workspace           slots: panel | body
split-screen — two equal columns                      slots: left | right
flyout       — main content + contextual side panel   slots: body | panel
holy-grail   — header + nav + body + aside + footer   slots: header, nav, body, aside, footer
```

`header` and `footer` slots always render as full-width bands above and below the column section, regardless of template. Any region assigned an unknown slot falls through to `body` (or the first defined column).

## Navigational component

A **navigational component** is a persistent surface that carries navigation across screens — menus, primary navigation, sidebars, headers, footers, breadcrumbs, link groups. Components are listed and named in UX terms, with the screens or content types they link to. They are not styled and they do not name controls.

## Canvas layout convention

The diagram uses a **column × row grid**. Every screen gets a `--col` (horizontal) and `--row` (vertical) when added. **Both are required — never rely on insertion order.**

**Decision rule — linear vs option (be aggressive):**

- **No — always visited:** linear. Put it in row 0, increment col.
- **Yes — sometimes visited:** option. Keep col the same as its trigger, increment row.

If in doubt, call it an option. Placing an optional screen in the linear row causes its column to push everything right, creating overlapping connections.

## Tab state

A **panel with N tabs generates N separate screens on the site map.** Each tab state is a full screen node — named `{{parent screen}} — {{tab label}}`. The inactive tabs are shown as greyed labels in the tab bar of each sibling screen. The transition between tab states is an arrow labeled "selects {{tab}} tab".

The outer chrome of a multi-tab screen is shared across all tab-state screens. On the canvas this chrome is drawn once on each sibling screen box but described only in the primary screen block in the spec — sibling blocks note `chrome: same as {{parent screen}}`.

On the diagram, sibling-screen chrome is drawn with `add-chrome --dimmed`, which fills it with light grey (`#f5f5f5`). **Grey is used only for this purpose** — to de-emphasise chrome that repeats unchanged across sibling tab screens. Data rows and form fields are never grey.

**Red flag:** treating a tabbed panel as one screen with sub-regions is wrong. If you find yourself writing "character detail panel — tab: Identities … tab: Abilities … tab: Movements" inside one screen block, stop — each tab is a separate screen.

## Content type

A **content type** is a kind of thing a user interacts with — typically a domain concept the user reads, edits, or acts on. Each content type carries a hierarchy, collections, labels and tags, and a small set of key actions.

## User story vs system story

A **user story** has a user-visible interaction. Each in-scope user story lives on at least one screen and contributes affordances and actions to that screen. On the IA a user story appears by **name** with a **link** — never by full text or acceptance criteria.

A **system story** has no user-visible interaction. It does not get its own screen — it is grouped (by name, with a link) with the closest user-visible screen whose interaction surfaces it.

## Domain term / concept / class

A domain term appears on a screen only if it names something the user can see or directly interact with — a data field label, a list row type name, a region name, or a screen name. Internal model concepts that do not appear as visible text are excluded. The full sub-concept hierarchy of a KA is never listed wholesale; list only the sub-concepts that appear as named items in the UI.

## Mental model alignment

Screen names, content type names, navigational component names, and the IA as a whole reflect the user's mental model of the solution rather than the technical decomposition. Prefer the term the product owner, domain expert, or user uses unprompted in conversation. If you are reaching for a system or framework name, stop and pick a domain or UX term instead.

## Card sorting (informally)

Before drawing per-screen content layouts and per-component link groupings, candidate labels are grouped by affinity — what reads as one surface or one cluster to a user. The resulting groups become the named regions, content groupings, and component link sets.
