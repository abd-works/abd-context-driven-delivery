---
scanner: domain_structure_scanner.py
---

# Rule: Organize by Domain Module

Organize code by **business capability** (domain module) first, then by technical layer within each module. This ensures that all code for a single domain lives together — changes rarely ripple to other domains, teams can own entire domains, and each module can become its own microservice later without restructuring.

## DO

- Structure each domain as `packages/{domain}/{shared|client|server}`.
- Include `index.ts` and `package.json` in each tier folder for clean imports.
- Keep the app shell (`app-server/`, `app-client/`) at the packages level as composition roots.
- **Ensure `packages/app-server/` and `packages/app-client/` exist** as part of generating a domain module. If either root is missing, scaffold it. If either already exists, update it to mount or render the new domain module instead of generating a duplicate shell.
- **Ensure the client tier provides UI for every user action defined in the specs.** If the requirements say a user can create a board, add tasks, or move items — the client must have corresponding forms, buttons, or controls. Derive required UI from the spec, not from a mechanical endpoint mirror.
- **Wire navigation in `app-client/App.tsx`** to support all spec-driven user flows (e.g., create → view → interact). The composition root must manage view state when multiple views are needed.
- **Always create `scripts/dev.ps1`** (and `scripts/dev.sh`) if no startup script exists. The script must start both `packages/app-server/` and `packages/app-client/` so the developer can open `http://localhost:3000` immediately after running it. Also add `dev:api` and `dev:client` entries to the root `package.json` scripts.
- **Always include a home page at `/`** in `app-client/App.tsx`. The home page must render navigable links to every major page route in the app. This is the entry point a user hits at `localhost:3000` — without it, the app appears blank and every page route is unreachable from the browser.
- - **Ensure every user action has a user-facing form and server endpoint/route.** Some POST routes exist for system-to-system workflows, background processing, or integration callbacks and should remain server-only unless the specs explicitly define a user action behind them.
- Place test files under `tests/{epic}/{sub-epic}/` mirroring the domain structure.

```
project-root/
├── packages/
│   ├── recipients/              # Domain module
│   │   ├── shared/              # Domain core (entities, schemas, value objects)
│   │   │   ├── Recipient.ts
│   │   │   ├── recipient.schema.ts
│   │   │   ├── index.ts
│   │   │   └── package.json
│   │   ├── client/              # React frontend for this domain
│   │   │   ├── RecipientListView.tsx
│   │   │   ├── CreateRecipientView.tsx
│   │   │   ├── RecipientDetailView.tsx
│   │   │   ├── useRecipients.ts
│   │   │   ├── recipients.api.ts
│   │   │   ├── index.ts
│   │   │   └── package.json
│   │   └── server/              # @app/<domain>-server
│   │       ├── <Entity>s.ts             # Server-side domain — extends shared; owns <<operation>>()
│   │       ├── <domain>.routes.ts       # HTTP adapter — delegates to server-side domain
│   │       ├── <domain>.repository.ts   # Infrastructure — used by server-side domain only
│   │       ├── index.ts
│   │       └── package.json
│   ├── app-server/              # Composition root: create if missing, otherwise reuse
│   │   ├── app.ts              # Creates Express app, mounts domain routers
│   │   ├── index.ts
│   │   └── package.json
│   └── app-client/              # Composition root: create if missing, otherwise reuse
│       ├── App.tsx             # React Router — maps paths to top-level views
│       ├── <<Feature>>View.tsx # Top-level view — composes domain views
│       ├── main.tsx
│       └── package.json
├── tests/
└── package.json
```

## DON'T

- Organize by technical layer at the top level (`controllers/`, `models/`, `views/`, `routes/`).
- Scatter a single domain's code across multiple unrelated folders.
- Mix multiple domain concerns in a single folder.
- **Generate domain module packages in a new project without also scaffolding missing composition roots.** Without these, the application cannot start and E2E tests fail with `ERR_CONNECTION_REFUSED`.
- **Create duplicate `app-server/` or `app-client/` shells, or overwrite an existing composition root, when adding a module to an existing project.** Extend the existing shells instead.
- **Ship a client tier that omits user actions defined in the specs.** If the requirements say users can create, edit, or move things, the UI must expose those capabilities — not just read-only search/list.
- **Mirror POST endpoints into UI controls by default.** A server route may support integrations or internal workflows without implying a corresponding form or button in the client tier.
- **Render a single static component in App.tsx when the specs define multiple user flows.** If users need to create entities and interact with detail views, the composition root must manage view state to support those flows.
- **Omit a home page at `/`.** Every app must have a `HomePage.tsx` with links to all page routes. Without it, hitting `localhost:3000` shows a blank page.
- **Omit a startup script.** Always create `scripts/dev.ps1` and `scripts/dev.sh` that start both the API server and the React frontend. Without them, the developer has no single command to bring the app up.
- **Do not assume every POST endpoint needs a user-facing form.** Some POST routes exist for system-to-system workflows, background processing, or integration callbacks and should remain server-only unless the specs explicitly define a user action behind them.

```
# WRONG — technical-first organization
project-root/
├── controllers/
│   ├── recipientController.ts    # Recipient logic scattered
│   └── paymentController.ts
├── models/
│   ├── Recipient.ts              # ... across multiple folders
│   └── Payment.ts
├── routes/
│   ├── recipientRoutes.ts        # ... making changes ripple everywhere
│   └── paymentRoutes.ts
└── views/
    ├── RecipientList.tsx
    └── PaymentForm.tsx
```
