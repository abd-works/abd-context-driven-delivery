## Overview

Implementation fidelity for a **domain-module-organized LERN stack** ([lowdb](https://github.com/typicode/lowdb)
JSON files / Express / React / Node, TypeScript everywhere) on an already-designed
vertical slice — story map, module boundaries, and screens all exist before this
tool runs. `generate` calls `self._stories()` at `acceptance_tests` /
`typescript` — specs first, then Stories' own `ce()` wires matching
production TypeScript. The rules below are additive on top of what Stories
and CleanEngineering already enforce, not a restatement of them.

**No fidelity progression of its own.** Every run pins `stories` at
`acceptance_tests` with `format="typescript"`; production code arrives via
Stories' `ce()` companion at `code` / `typescript`.

---

## Guidance

Enforceable rules live in **§ Shared rules** below. This section explains how
they apply; do not treat guidance bullets as a second rule list.

### Domain-driven design (reference)

This architecture **is** DDD tactics on JSON-file persistence. Stereotypes,
invariants, and repository seams come from
[`practices/ddd/ddd.md`](../../practices/ddd/ddd.md) **building_blocks**. Honour
those definitions; this spec only says how they land on lowdb.

| Stereotype | Meaning (from `ddd.md`) |
|---|---|
| **Entity** | An object defined by its unique identity rather than its attributes, maintaining continuity across state changes over time. |
| **Aggregate** | A cluster of associated domain objects (entities and value objects) grouped together to maintain consistent business rules as a single unit. |
| **Aggregate Root** | The main entity inside an aggregate that acts as the sole gateway, controlling all external access and enforcing consistency rules for the entire cluster. |
| **Value Object** | Fully described by values — interchangeable, replaceable, immutable. Prefer VO unless tracked identity is required. |
| **Repository** | Hides storage so the business loads, saves, and queries **entire aggregates** as if they lived in a memory collection. Collection-style seam: the business finds, stores, and retires this aggregate through the root. |

Each **domain module** is one aggregate. The **Repository** is the only
persistence compartment for that aggregate: it returns **entities** by
**loading**, **creating**, **searching**, and **updating** the **aggregate
root**. Nested entities and value objects travel inside that root's snapshot;
callers never open the JSON store themselves.

---

### Two-root layout: `src/` domains, `packages/` screens

Domain tiers and lowdb stores live **once** under `src/<domain-slug>/`.
Epic packages under `packages/<epicSlug>/` hold process boot, routing, and
screen views only — they import domain tiers through `@src`.

```
src/                                    ← shared domain modules (one copy)
  <domain-slug>/
    <domain-slug>.ts                    ← core aggregate, repository, VOs
    <domain-slug>-node.ts               ← Node tier (Express, destination, repo node)
    <domain-slug>-client.tsx            ← browser client subtype
    <domain-slug>.json                  ← lowdb store for this aggregate

packages/<epicSlug>/                    ← epic package — screens and boot only
  app.ts / serve.ts / main.tsx          ← Express + Vite process boot
  package.json / index.html / vite.config.ts
  <epic-slug>-view.tsx                  ← epic shell view (kebab-case filename)
  <epic-slug>-redirect.tsx              ← fetches destination, mounts sub-epic view
  routes/
    <epic-slug>-routes.ts               ← asks *Node classes; never picks a step locally
  <sub-epic-slug>/                      ← sub-epic screen folder
    <screen-slug>.tsx
```

Rule `epic-package-screens-only` governs this split. Do **not** duplicate
`<domain>.ts`, `<domain>-node.ts`, `<domain>-client.tsx`, `source/`, or
`data/` trees under the epic package — tests and screens already import the
single copy from `@src`.

Rule `domain-core-file-matches-folder-slug` governs filenames: kebab-case core
files (`<domain-slug>/<domain-slug>.ts`), PascalCase exported types
(`{Domain}`).

---

### Persistence: one lowdb JSON store per aggregate

[lowdb](https://github.com/typicode/lowdb) is the adapter (`JSONFilePreset` /
`JSONFile` from `lowdb/node` in production; `Memory` from `lowdb` in tests).
Each aggregate's JSON file sits beside its domain module in `src/<domain-slug>/`.

```
src/<domain-slug>/<domain-slug>.json
{
  "<collection-key>": [                 ← serialized aggregate roots for this aggregate
    { "id": "…", … }
  ]
}
```

Rules `one-json-store-per-aggregate` and `repository-owns-aggregate-lifecycle`
govern this layer. Repositories never open another aggregate's JSON file.
Required operations, named in ubiquitous language:

| Operation | Returns | Role |
|---|---|---|
| `load(id)` | aggregate root or `null` | find by identity already in hand |
| `create(input)` | new aggregate root | birth |
| `search(query?)` | aggregate roots | find by attributes / example |
| `update(root)` | updated aggregate root | persist a mutation already applied on the root |

Zod `.parse()` runs at the repository boundary. One `*Repository` class per
aggregate lives on the domain core (`<domain>.ts`). It is not a client type and
does not take a `Node` suffix — `{Domain}Node` is the Express host, not the
collection. Routes and views never call `JSONFilePreset` / `db.data` themselves.

Cross-aggregate consistency is **outside** a single JSON file. Choose one
coordination style **when generating stories** (see `ask-cross-aggregate-sync`
in § Shared rules) — then keep that choice for the slice.

---

### Three tiers per domain (`src/<domain-slug>/`)

| File | Suffix | Role |
|---|---|---|
| `<domain-slug>.ts` | *(none)* | Core aggregate, repository interface, value objects, exceptions — framework-free |
| `<domain-slug>-node.ts` | `Node` | Express wiring, `{Domain}Node`, `destination`, session on the request context |
| `<domain-slug>-client.tsx` | `Client` | Browser subtype: field entry, touched flags, requirement lines, host operations |

Rule `node-tier-uses-node-suffix` names the Node.js tier **`Node`**, not
`Server` — this tier runs in-process with Express and the Vitest server channel,
not on an external host.

Rule `client-subtypes-domain-hosts-browser-logic`: `{Domain}Client`
and `{Domain}Node` both **extend** `{Domain}`. Domain operations on the core
class are the operations the client hosts for the browser. A field change returns
a **new client instance** for React state.

Tier classes keep every inherited base operation unchanged; subclasses only add
layer-specific behaviour (`destination`, repository I/O).

Rules `share-domain-logic`, `maintain-layer-purity`, `use-ubiquitous-language`,
`cross-layer-method-naming`, `preserve-arg-names-across-layers`, and
`property-casing-transform` govern imports and naming across these three files.

---

### Navigation: node decides, router asks, view renders

**Node decides the next page.** `*Node.destination` maps the domain step to a
browser path. Path maps stay in the `*-node.ts` file (rule
`node-decides-next-page`).

**Router asks the node.** Route modules call `*Node.destination` and return the
path those classes produce. Redirect components fetch that result and mount the
view for the returned path. Neither the route module nor the redirect derives
the page from a step enum locally (rule `router-asks-the-node`).

**Views render only.** A screen view keeps the client instance in React state
and paints the fields, requirement lines, and actions that client exposes.
Field entry, touched flags, requirement strings, host operations, and the next
page stay off the view (rule `views-render-only`).

Epic and sub-epic views use kebab-case filenames (`<epic-slug>-view.tsx`,
`<screen-slug>.tsx`). Exported React components end in `View`
(rule `consistent-view-naming`).

---

### App server / routes

Route handlers stay thin: parse the request, delegate to a `*Node` class or
call `*Node.destination`. Rules `router-asks-the-node`, `ensure-type-safe-routes`
(typed request extensions), and `standard-mutation-response` govern this tier.

Create the aggregate's one repository at the **caller** — production passes the
`*Repository` into route factories; tests construct their own in the scenario
that needs one. Node modules export `{Domain}Node`, not a second repository.

### Types & entities

Business rules live on domain classes; Zod validates at the repository
boundary. Rules `implement-domain-entities-correctly` and
`implement-full-interfaces` govern entities and interfaces.

### Packaging

`@src` alias resolves `src/` for epic packages. One epic package per feature
(`packages/<epicSlug>`) with screen and route subpaths. Rules
`use-valid-package-names` and `include-all-external-dependencies` govern
packaging (`lowdb` on the server).

### Testing architecture

One sub-epic folder under `tests/<epic-slug>/<sub-epic-slug>/` holds one story
and three ways to run it. The shape is the onboard-a-customer tests: Create
Customer and Authenticate User.

| File | What it does |
|---|---|
| `<snake>.story.shared.ts` | States the story once. `shareStory` holds Given, When, and Then. It imports `examples/` and calls the domain operation. |
| `<snake>.story.domain.spec.ts` | Runs that shared story with the domain repository. This proves the entity. |
| `<snake>.story.server.spec.ts` | Runs that shared story with the node repository, and asks the route for the destination. This proves the node. |
| `<snake>.story.playwright.ts` | Runs that shared story in the browser. The screen shows the destination. This proves the view. |
| `examples/<concept>.examples.ts` | Seed data for the entity. The shared story imports it. The file exports data, not a repository. |

`domain-runs-entity`, `server-runs-node`, and `playwright-displays-view` are
those three runs. `shared-states-story` is the shared file stating the story
they all import.

Rules `test-story-driven`, `scaffold-test-scripts`, `use-thorough-e2e-tests`,
and `pml-artifact-layout` govern these files.

### UX hand-off

Screens and navigation for this slice were designed upstream by `ux` before
this tool runs. `generate` cites that artifact under **Sources / context** on
the touched view files (`packages/<epicSlug>/*-view.tsx`, sub-epic screen
folders, …) — it does not call `ux` itself.

### Generating stories — cross-aggregate sync

When a story (or the slice) involves **more than one aggregate**, those
aggregates stay in separate JSON stores under `src/`. Synchronization is a
**choice**, recorded before scenarios are written. Rule
`ask-cross-aggregate-sync` is a hard gate when generating stories.

Use the **AskQuestion** tool (never a plain chat list). One question, two
options; do not write story files until the answer is in
`.context/grill-answers.md` under heading **Cross-aggregate sync**.

**AskQuestion**

- **prompt:** This slice touches more than one aggregate, and each aggregate
  has its own lowdb JSON store (see `practices/ddd/ddd.md` Repository /
  Aggregate Root). How should stories coordinate work that spans aggregates?
- **options:**
  1. **Event-based orchestration** — the acting aggregate publishes a
     past-tense **Domain Event**; the other aggregate's repository loads
     *its* root and applies *its* reaction. Repositories never open another
     aggregate's JSON file. Stories Given/When/Then the event and each
     aggregate's observable outcome.
  2. **Direct repository calls by the client** — the client (HTTP /
     application layer) calls each aggregate's repository (or HTTP API)
     in turn. The client is the orchestrator. Stories Given/When/Then the
     sequence of client calls and each root's visible state.

If the slice is a single aggregate, record `single-aggregate` under that
heading and skip the question.

---

## Generate

1. Follow **session_guidance**. Scaffold domain modules under `src/<domain-slug>/`
   (`<domain>.ts`, `<domain>-node.ts`, `<domain>-client.tsx`, `<domain>.json`)
   and the epic package under `packages/<epicSlug>/` (boot, `routes/`, epic view,
   sub-epic screen folders). Import domain tiers through `@src`.
2. **`ask-cross-aggregate-sync`** — if more than one aggregate is in play,
   AskQuestion as specified above and persist the answer **before** calling
   the Stories companion.
3. Call guidance on the Stories companion. For each sub-epic write
   `<snake>.story.shared.ts`, then `<snake>.story.domain.spec.ts`,
   `<snake>.story.server.spec.ts`, and `<snake>.story.playwright.ts`, plus
   `examples/`. Specs first — small RED cycles before production. Pass that
   companion to this action as a separate tools run.
4. Cite the ux screen/navigation artifact for this slice under **Sources /
   context** on the touched view files — this tool does not call `ux` itself.
5. Run validate. If it fails, fix and validate again until it passes.

## Shared rules

```yaml
alwaysApply: false
globs: "packages/**/*,src/**/*"
```

Whenever you create, alter, or delete a LERN domain module under `src/`, an epic
package under `packages/`, or tests they support. Follow these rules.

If this change will not stay here, follow `practices/clean_engineering/code.mdc`. If the tests are Spec-by-Example, also follow `practices/stories/acceptance_tests.mdc`. DDD aggregate rules in `.context/rules/ddd/tactics/` apply to domain classes.

### Layout and tiers

- **`epic-package-screens-only`** — Keep shared domain tiers and lowdb data only under `src/<domain>/` (`<domain>.ts`, `<domain>-node.ts`, `<domain>-client.tsx`, and per-aggregate json). Limit `packages/<epicSlug>/` to epic boot (`app.ts`, `serve.ts`, `main.tsx`, `*-view.tsx`) plus sub-epic screen views and `routes/` — no second `*-node.ts`, `*-client.tsx`, `source/`, or `data/` tree under the epic package.
- **`domain-core-file-matches-folder-slug`** — Name the domain core file after the folder slug in kebab-case (`<domain-slug>/<domain-slug>.ts`). Keep exported classes PascalCase (`{Domain}`). Place `<domain>-node.ts` and `<domain>-client.tsx` beside the core file in the same `src/<domain>/` folder.
- **`node-tier-uses-node-suffix`** — Name the Node.js LERN tier with the `Node` suffix and `<domain>-node.ts` filenames (`{Domain}Node`). Type request-context fields as `*Node`, not `Server`. The repository is `*Repository`, never `*RepositoryNode`.
- **`client-subtypes-domain-hosts-browser-logic`** — For each `src/<domain>/`, derive `<domain>.ts`, `<domain>-client.tsx`, and `<domain>-node.ts` from the folder slug. The `*Client` and `*Node` classes extend the core domain class. Domain operations on the core are the operations the client hosts for the browser; field changes return a new client instance for React state.

### Navigation and views

- **`node-decides-next-page`** — The node class decides the next page. `*Node.destination` maps the domain step to the browser path; path maps stay in `*-node.ts`.
- **`router-asks-the-node`** — Route modules only ask node classes and return the path they produce. Redirect components fetch that result and mount the view — neither derives the page from a step locally.
- **`views-render-only`** — A screen view only renders. It keeps the client in React state and paints fields, requirement lines, and actions the client exposes. Field entry, touched flags, host operations, and next-page logic stay on the client or node.

### Persistence and repositories

- **`one-json-store-per-aggregate`** — Each aggregate root owns its own JSON file under `src/<domain-slug>/`. Do not put several aggregates in one file. Repositories never open another aggregate's JSON file.
- **`repository-owns-aggregate-lifecycle`** — The domain-core `*Repository` interface is the collection seam for the root: `load`, `create`, `search`, `update` — named in ubiquitous language. Zod `.parse()` runs at this boundary.
- **`one-repository-per-aggregate`** — One `*Repository` per `src/<domain>/`, declared on the aggregate. The client does not declare a repository. Repository names keep the `Repository` suffix only — never `*RepositoryNode`.

### Naming, purity, and packaging

- **`share-domain-logic`** — Entities, value objects, Zod schemas, and business rules defined once in `<domain>.ts`; `-node.ts` and `-client.tsx` import from there, never re-derive.
- **`maintain-layer-purity`** — `<domain>.ts` is framework-free (no Express, no React, no lowdb); `-node.ts` and `-client.tsx` never cross-import each other.
- **`use-ubiquitous-language`** — Names come from the domain model; no `Manager`, `Handler`, `Helper`, or `Domain*` prefixes/suffixes.
- **`cross-layer-method-naming`** — The same `{verbNoun}` method stem flows through core → client → node → route → HTTP; subclasses keep every inherited base operation unchanged.
- **`preserve-arg-names-across-layers`** — Argument names stay identical across layer boundaries; only types narrow.
- **`property-casing-transform`** — `camelCase` in TypeScript; `snake_case` in JSON (lowdb documents and HTTP bodies).
- **`consistent-view-naming`** — React components end in `View`; screen filenames stay kebab-case.
- **`ensure-type-safe-routes`** — Route handlers compile without implicit `any`; request extensions are typed.
- **`standard-mutation-response`** — Every mutation on the same aggregate returns the same response shape.
- **`implement-domain-entities-correctly`** — Business rules live on domain classes; Zod validates at the repository boundary, not inline in routes or views.
- **`implement-full-interfaces`** — Every `implements` clause covers all interface members; no stub no-ops.
- **`use-valid-package-names`** — One epic package per feature with `@src` imports into `src/`; no phantom imports or legacy flat `*-shared` / `*-server` / `*-client` package split.
- **`include-all-external-dependencies`** — Every import has a declared dependency (`lowdb` on the server); the project compiles after a clean install.

### Testing and story generation

- **`test-story-driven`** — Each sub-epic states the story once in `<snake>.story.shared.ts`. The domain spec runs it on the entity, the server spec runs it on the node, and the Playwright spec displays it on the view.
- **`scaffold-test-scripts`** — `scripts/test.sh`, `test.ps1`, `test-e2e.sh`, `test-e2e.ps1` at the workspace root; Vitest and Playwright stay separate.
- **`use-thorough-e2e-tests`** — E2E tests are independent (no wiping entire JSON stores between tests); delete only aggregate roots the test created.
- **`ask-cross-aggregate-sync`** — **Hard gate** when generating stories. Use AskQuestion; persist the answer under **Cross-aggregate sync** in `.context/grill-answers.md` before writing story files.
