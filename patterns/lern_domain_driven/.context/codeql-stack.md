# Stack — lern_domain_driven

These node and edge files belong to the pattern, under `patterns/lern_domain_driven/practices/<practice>/model/typescript/codeql/`. The original practice packs stay as they are. Each new edge file selects `parent_id, child_id, kind, order, display` and calls the id helpers the existing node files use.

Put an edge file in the pattern pack of the parent. A domain edge stays on the domain view. Clean engineering already shows a class related to another class.

## Domain nodes

The domain entity is already `entity-roots.ql` (`semantic_type=EntityRoot`): `{Domain}` in `src/<domain-slug>/<domain-slug>.ts`. Repository stays `repositories.ql`.

New files in `patterns/lern_domain_driven/practices/ddd/model/typescript/codeql/nodes/`:

**domain-client.ql** — `semantic_type=DomainClient`, `<domain-slug>-client.tsx`, class `{Domain}Client`

**domain-node.ql** — `semantic_type=DomainNode`, `<domain-slug>-node.ts`, class `{Domain}Node`

**json-store.ql** — `semantic_type=JsonStore`, `<domain-slug>.json`

**route.ql** — `semantic_type=Route`, one file beside its aggregate: `src/account-credentials/account-credentials-routes.ts` is the AccountCredentials route, `src/customer/customer-routes.ts` is the Customer route.

**destination.ql** — `semantic_type=Destination`, each `router.get` / `router.post` in that file. `router.get('/destination', …)` is one destination.

**domain-view.ql** — `semantic_type=DomainView`, the screen file within an aggregate: `src/account-credentials/create-account.tsx`, `enter-validation-code.tsx`, `sign-in-with-existing-account.tsx`; `src/customer/create-customer.tsx`; `src/plan/select-plan.tsx`.

## Domain edges

New files in `patterns/lern_domain_driven/practices/ddd/model/typescript/codeql/edges/`. `destination-invokes-operation.ql` and `view-renders-operation.ql` name the entity-root operation. Those rows stay on the domain view.

A route file navigates to one aggregate. That route receives requests. Each request is a destination, and that destination invokes an operation on the aggregate's entity root. `src/account-credentials/account-credentials-routes.ts` navigates to AccountCredentials; `POST /api/account/register` invokes `register`. `src/customer/customer-routes.ts` navigates to Customer; `POST /api/customer/load` invokes `load`, `POST /api/customer/create` invokes `create`.

A view renders an entity. That entity can be any entity, and one view can render more than one. Each rendered entity is its own row. The same view renders an entity operation when the screen calls one. `CreateAccountView` renders AccountCredentials and renders `register`. `EnterValidationCodeView` renders `verify` and `resendValidationCode`. `SignInWithExistingAccountView` renders `authenticateAccount`. `SelectPlanView` in `src/plan/select-plan.tsx` renders Plan and has no operation row. `CreateCustomerView` in `src/customer/create-customer.tsx` renders Customer.

| File | parent | child | kind | order | display |
|---|---|---|---|---|---|
| client-interacts-entity.ql | DomainClient | EntityRoot | interacts | 5 | relationship |
| node-hosts-entity.ql | DomainNode | EntityRoot | hosts | 5 | relationship |
| json-file-entity.ql | JsonStore | EntityRoot | jsonFile | 5 | relationship |
| route-navigates-aggregate.ql | Route | Aggregate | navigates | 5 | relationship |
| route-has-destination.ql | Route | Destination | has | 2 | direct |
| destination-invokes-operation.ql | Destination | Operation | invokes | 5 | relationship |
| view-renders-entity.ql | DomainView | Entity | renders | 5 | relationship |
| view-renders-operation.ql | DomainView | Operation | renders | 5 | relationship |
| node-decides-view.ql | DomainNode | DomainView | decides | 9 | relationship |

## Story nodes

`patterns/lern_domain_driven/practices/stories/model/typescript/codeql/nodes/`

**story-shared.ql** — `semantic_type=StoryShared`, `tests/<epic>/<sub-epic>/<snake>.story.shared.ts`. One `shareStory` body: Given, When, Then. It imports `examples/` and calls the domain operation.

**domain-spec.ql** — `semantic_type=DomainSpec`, `<snake>.story.domain.spec.ts`. Executes the shared story with the domain repository.

**server-spec.ql** — `semantic_type=ServerSpec`, `<snake>.story.server.spec.ts`. Executes the shared story with the node repository, and asks the route for the destination.

**playwright-spec.ql** — `semantic_type=PlaywrightSpec`, `<snake>.story.playwright.ts`. Executes the shared story in the browser. The screen shows the destination.

Epic, Story, Scenario, Step, and Example stay the story node queries in the stories practice pack.

## Story edges

`patterns/lern_domain_driven/practices/stories/model/typescript/codeql/edges/`. These rows relate the tests to each other through the shared story. `story-tests-aggregate.ql` names an Aggregate, so that row is also stored on the domain view.

The shared story states the story and links to the aggregate. The domain spec, the server spec, and the playwright spec each execute that shared story.

| File | parent | child | kind | order | display |
|---|---|---|---|---|---|
| shared-states-story.ql | StoryShared | Story | states | 5 | relationship |
| story-tests-aggregate.ql | StoryShared | Aggregate | links | 5 | relationship |
| domain-executes-shared.ql | DomainSpec | StoryShared | executes | 5 | relationship |
| server-executes-shared.ql | ServerSpec | StoryShared | executes | 5 | relationship |
| playwright-executes-shared.ql | PlaywrightSpec | StoryShared | executes | 5 | relationship |

## Rules already in the pattern

These rule files are already in the pattern, under `patterns/lern_domain_driven/practices/<practice>/model/typescript/codeql/rules/`. They select `rule, node_id, violation`. The `node_id` is a node a node query registers, or the parent of an edge an edge query registers.

| Rule | Applies to |
|---|---|
| domain-core-file-matches-folder-slug | EntityRoot, DomainClient, DomainNode |
| share-domain-logic | EntityRoot, DomainClient, DomainNode |
| node-decides-next-page | DomainNode, Destination, edge `node-decides-view` |
| views-render-only | DomainView, edges `view-renders-entity`, `view-renders-operation` |
| cross-layer-method-naming | EntityRoot, DomainClient, DomainNode |
| property-casing-transform | Entity |
| ensure-type-safe-routes | Destination |
| standard-mutation-response | Destination |
| include-all-external-dependencies | EntityRoot, DomainClient, DomainNode, DomainView, Route |
| implement-full-interfaces | Repository |
| one-json-store-per-aggregate | JsonStore, edge `json-file-entity` |
| repository-owns-aggregate-lifecycle | Repository, EntityRoot |
| one-repository-per-aggregate | Repository, Aggregate |
| ask-cross-aggregate-sync | EntityRoot |
| use-ubiquitous-language | Entity, EntityRoot |
| implement-domain-entities-correctly | Entity, EntityRoot |
| use-ctx-repository-directly | StoryShared, DomainSpec, ServerSpec |
| test-story-driven | StoryShared, DomainSpec, ServerSpec, PlaywrightSpec |
| scaffold-test-scripts | PlaywrightSpec |
| use-thorough-e2e-tests | PlaywrightSpec |
| pml-artifact-layout | StoryShared, DomainSpec, ServerSpec |
| examples-export-data-not-repository | StoryShared |
| browser-then-asserts-screen-widgets | PlaywrightSpec, edge `playwright-executes-shared` |
