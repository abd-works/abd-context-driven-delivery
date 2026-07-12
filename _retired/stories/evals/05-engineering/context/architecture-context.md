# Architecture context — MERN Domain-First (Cash Management Platform)

## Architecture

Domain-module-organized full-stack TypeScript (MongoDB, Express, React, Node.js). Every artifact derives from the domain model — file names, class names, and method names come from domain classes and operations, never generic `Manager` or `Handler` synonyms.

Each business capability lives in `packages/<domain>/` with three tiers:

- **shared/** — entity classes, collection classes, Zod schemas, repository interfaces. No framework imports. Plain domain names (`Transfer`, `Transfers`, `TransferRepository`).
- **server/** — extends shared; route handlers (thin — delegate to server domain classes), server-side domain (`TransfersServer extends Transfers`), repository implementation (`TransferRepositoryServer implements TransferRepository`), MongoDB.
- **client/** — extends shared; React views, thin hooks, client-side domain (`TransfersClient extends Transfers`), type-safe HTTP client (`TransferApi`). Layer qualifiers on extensions (`Client`, `Server`, `Api`, `Router`).

Composition roots (`app-server/`, `app-client/`) wire packages; domain packages never import from a composition root.

## Testing tiers

Four independent layers — none call each other:

- **domain** — class constructor / method call; real shared domain classes only; no stubs; asserts return values and business rules.
- **server** — Express route via Supertest; real domain + repository + test DB; no stubs; asserts HTTP status and JSON body.
- **client** — `render(<View />)` via Testing Library; real React tree + hooks + client domain; stubs `<<Entity>>Api` via `vi.mock`; asserts DOM via `screen`.
- **e2e** — `page.goto(url)` via Playwright; full stack — real browser, real server, real DB; no stubs; asserts page elements.

Spec files (`<slug>-stories.ts`) are regeneratable data. Tier files (`<slug>-<tier>.test.ts`) are write-once — scaffold empty implementations first, then hand-edit.
