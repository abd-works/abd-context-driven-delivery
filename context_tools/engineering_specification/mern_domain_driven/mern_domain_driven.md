# Contexts

Implementation fidelity for a **domain-module-organized MERN stack** (MongoDB /
Express / React / Node, TypeScript everywhere) on an already-designed vertical
slice — story map, module boundaries, and screens all exist before this tool
runs. `generate` calls `self._stories()` at `acceptance_tests` /
`typescript` — specs first, then Stories' own `ce()` wires matching
production TypeScript. The rules below are additive on top of what Stories
and CleanEngineering already enforce, not a restatement of them.

**No fidelity progression of its own.** Every run pins `stories` at
`acceptance_tests` with `format="typescript"`; production code arrives via
Stories' `ce()` companion at `code` / `typescript`.

---

## Domain module organization

Packages follow the feature → domain hierarchy: a feature package owns process
boot and the feature view; each domain (and subdomain) it needs lives as a
folder inside it, with three tier files — core, server, client:

```
packages/<epicSlug>/                    ← feature package — e.g. wires/
  <EpicName>View.tsx                    ← feature view — e.g. WirePaymentView.tsx
  app.ts / serve.ts                     ← Express app factory + process listen
  main.tsx / index.html / vite.config.ts ← browser process boot
  package.json                          ← @scope/epicSlug
  <domainNames>/                        ← domain nested in the feature — e.g. recipients/
    <domainNames>.ts                    ← domain core — e.g. recipients.ts
    <domainName>-server.ts              ← e.g. recipient-server.ts
    <domainName>-client.tsx             ← e.g. recipient-client.tsx
```

- **`organize-by-domain-module`** — feature package present with process boot (`app.ts`, `serve.ts`, `main.tsx`) and nested domain dirs each having `{domain}.ts`, `{domain}-server.ts`, `{domain}-client.tsx`.
- **`share-domain-logic`** — entities, value objects, Zod schemas, and business rules defined once in `<domain>.ts`; `<domain>-server.ts` and `<domain>-client.tsx` import from there, never re-derive.
- **`maintain-layer-purity`** — `<domain>.ts` is framework-free (no Express, no React, no Mongo driver); `<domain>-server.ts` and `<domain>-client.tsx` never cross-import each other.

## Naming / layering

Every artifact instantiates from the domain — file, class, and method names
derive from domain classes/operations. `<domain>.ts` keeps plain domain names
(`Recipient`, `Recipients`); every extension in `<domain>-client.tsx` or
`<domain>-server.ts` adds a layer qualifier (`RecipientClient`,
`RecipientsServer`, `RecipientHttpClient`, `RecipientRepositoryServer`).
`Domain` is never part of a class name.

| File | Qualifier | Example |
|---|---|---|
| `<domain>.ts` / `recipients.ts` | *(none)* | `Recipient`, `Recipients`, `RecipientRepository` |
| `<domain>-client.tsx` | `Client`, `HttpClient` | `RecipientClient`, `RecipientsClient`, `RecipientHttpClient` |
| `<domain>-server.ts` | `Server`, `RepositoryServer` | `RecipientsServer`, `RecipientRepositoryServer` |

Tier classes **extend** the domain-core class — they do not fork it.
`RecipientsClient extends Recipients`, `RecipientsServer extends Recipients`,
`RecipientClient extends Recipient`. Every operation on the base
(`filterByStatus`, getters, collection queries, …) stays exactly the same on
the subclass: same name, same arguments, same meaning. Subclasses only **add**
layer-specific operations (`load`, `cardCssClass`, repository I/O); they never
rename, redefine, or reimplement a base operation under a different signature.

That same identity holds across the rest of the stack: where an operation
appears on the route, HTTP client, server domain class, or core, it is the
same `{verbNoun}` with the same argument names — only types narrow.

- **`use-ubiquitous-language`** — names come from the domain model; no `Manager`, `Handler`, `Helper`, or `Domain*` prefixes/suffixes.
- **`cross-layer-method-naming`** — the same `{verbNoun}` method stem flows through every tier where an operation appears (domain core → client → server → route → HTTP); subclasses keep every inherited base operation unchanged.
- **`preserve-arg-names-across-layers`** — argument names stay identical across layer boundaries and across base → extension; only types narrow.
- **`property-casing-transform`** — `camelCase` in TypeScript; `snake_case` in JSON and MongoDB documents.
- **`consistent-view-naming`** — React components end in `View` or `CardView`; never `Page`.

## App server / routes

- **`delegate-routes-to-domain-server`** — route handlers in `<domain>-server.ts` are thin: parse the request, delegate to a server-side domain class; never call the repository or apply domain-core logic inline.
- **`ensure-type-safe-routes`** — route handlers compile without implicit `any`; `req.user` and other request extensions are typed.
- **`standard-mutation-response`** — every mutation on the same aggregate returns the same response shape.

## Types & entities

- **`implement-domain-entities-correctly`** — business rules live on domain classes; the Zod schema validates at the repository boundary, not inline in routes or views.
- **`implement-full-interfaces`** — every `implements` clause covers all interface members; no stub no-ops standing in for real behavior.

## Packaging

- **`use-valid-package-names`** — one package per feature (`@scope/epicSlug`) with subpath exports into nested domains (`./recipients`, `./recipients/recipient-server`, …); no placeholder scopes; no phantom imports; no legacy flat `*-shared` / `*-server` / `*-client` package split.
- **`include-all-external-dependencies`** — every import has a declared dependency; the project compiles after a clean install.

## Testing architecture

Companion to `stories`'s `acceptance_tests` fidelity — this tool pins the
generic `*_spec.{tier}` to `tier ∈ {server, client, e2e}` and the stub policy
per tier. Domain unit tests (always present, live beside the class, not under
this tool) are a separate always-on layer.

| Tier | Real | Stubbed | Entry point |
|---|---|---|---|
| domain unit | domain-core classes | nothing | class method call |
| server | domain + repository + test DB | nothing | Supertest → Express route |
| client | React tree + hooks + client domain | HTTP client via `vi.mock` | Testing Library render |
| e2e | full stack | nothing | Playwright `page.goto` |

A base helper (`<sub-epic>.base.ts`) carries Given/When/Then vocabulary in
business terms; each tier helper extends it with the same names, different
mechanism underneath. Prefer building tier helpers from `stories`'
`{Type}ExampleFactory` (`Isolated` mode = ctor-injected mocks for the server
tier's collaborators, `Production` mode = real collaborators) over hand-rolled
fixtures.

- **`test-story-driven`** — tests mirror the story hierarchy (epic → folder, sub-epic → file, story → `describe`, scenario → `it`); Given/When/Then helpers present at all three tiers.
- **`scaffold-test-scripts`** — `scripts/test.sh`, `test.ps1`, `test-e2e.sh`, `test-e2e.ps1` present at the workspace root; unit/component and E2E runners stay separate (Vitest vs Playwright), and `vitest.config.ts` / `playwright.config.ts` don't pick up each other's spec files.
- **`use-thorough-e2e-tests`** — E2E tests are independent (no blanket deletes between tests); the feature package must exist and serve the real frontend (`npm run dev`) before E2E tests can pass.

## UX hand-off

Screens and navigation for this slice were designed upstream by `ux` before
this tool runs. `generate` cites that artifact under **Sources / context** on
the touched view files (`packages/<epicSlug>/<Feature>View.tsx`, views inside
`<domain>/<domain>-client.tsx`, …) — it does not call `ux` itself.
