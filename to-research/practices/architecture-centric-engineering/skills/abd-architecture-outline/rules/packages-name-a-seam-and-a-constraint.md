### Rule: A package names a seam and the constraint it imposes

A package in the outline catalogue is **a boundary that imposes a code shape on its consumers** — not a folder, not a grab-bag of files, not "the place where related code lives." Naming a package as part of the architecture is a commitment that the package owns a seam (the contract its consumers depend on), enforces a constraint (the code shape consumers must follow to use it), and serves a goal (what the architecture gains by treating this as a unit). If you cannot name the seam and the constraint, you have not identified a package — you have identified a folder. The outline distinguishes four kinds of packages: **mechanism-host** (owns the implementation of a mechanism that other packages instantiate), **service package** (owns the boundary to one or more external systems), **entity instance** (a concrete instance of the entity-controller pattern for one downstream), and **utility / legacy** (does not own a stable seam — flagged so consumers do not depend on it). Passing means a reviewer can see, for every package, what the boundary is and what consumers must do to honour it. Failing means a package is described by what files it contains, what folder it lives in, or what topics it covers.

#### DO

- For each package, state the **seam** (what boundary the package owns), the **constraint** (the code shape it imposes on consumers — what they must do or must not do), and the **goal** (what the architecture gains by having this package).

  **Example (pass):** *Auth (mechanism-host)*. **Seam:** the `Auth` middleware and the `CognitoService` interface. **Constraint:** no route handler may verify JWTs or call AWS Cognito directly; protected route groups mount `Auth` ahead of all handlers. **Goal:** one place to change identity provider; route handlers stay framework-agnostic.

- Categorise each package as mechanism-host, service package, entity instance, or utility/legacy — and let the category drive what the description focuses on.

  **Example (pass):** *Twilio (service package)*. **Seam:** the `TwilioClient` export. **Constraint:** no module may import `twilio` directly; all SMS calls go through `TwilioClient`. **Goal:** the Mavenir and My entities can swap SMS provider without touching their controllers.

- Mark utility / legacy packages explicitly. Their description should warn consumers not to depend on them as stable seams.

  **Example (pass):** *legacy-helpers (utility / legacy)*. **Seam:** none stable — direct imports of named utilities. **Constraint:** new code must not import from this package; existing usages migrate into the entity that owns the call site. **Goal:** quarantine pre-refactor helpers so they shrink rather than grow.

#### DO NOT

- Describe a package by listing the files or folders it contains.

  **Example (fail):** *Subscriber.* "Contains `SubscriberController.ts`, `SubscriberRouter.ts`, `subscriber.schema.ts`, and three test files under `__tests__/`." This is a file inventory, not a package description — the reader has no idea what the seam is or what consumers must do.

- Describe a package by topic without naming the boundary or the constraint.

  **Example (fail):** *Logging.* "Handles all logging concerns across the application." Topic, not seam. Does logging happen by importing a function, by injecting a logger, by writing to a transport? What must callers do? The description tells the reader nothing.

- Conflate a mechanism-host package with the mechanism it hosts.

  **Example (fail):** *Authentication mechanism.* The catalogue entry under Packages says "see section 4.1 for the mechanism." The package is the boundary that hosts the mechanism (the middleware, the verifier service, the export surface); the mechanism is the recurring pattern consumers follow. Describe both — they are separate architectural commitments.

**Source:** Practice-skill authoring convention (abd-architecture-outline); mirrors the specification skill's "mechanism is a pattern with named instances" — at outline fidelity, packages are seams with constraints, not folders with files. Without this discipline the Packages section becomes a directory listing dressed up as architecture.
