# Generate — abd-architecture-template

Concepts and package shape: [`concepts.md`](./concepts.md). Practice-level model: [`../../../reference/architecture-context-model.md`](../../../reference/architecture-context-model.md).

## Step 0 — Required inputs

Gather all of these before writing any file in the template package.

| Input | Required | Resolution order | If missing |
|---|---|---|---|
| **Mode** | Yes | User-supplied (`project` or `mechanism`); default `project` if unspecified. | **AskQuestion** — confirm mode before resolving the rest. |
| **Source mechanism** | Yes | In `project` mode: the project's primary mechanism (most-instantiated; ask the user when ambiguous). In `mechanism` mode: the named mechanism passed at invocation. | **AskQuestion** — which mechanism's `architecture-context.md` is the source of truth? |
| **Source `architecture-context.md`** | Yes | Resolved from the central spec's Where-to-Start row for the named mechanism. | Stop and route back to `abd-architecture-specification` if the file is missing or carries `<!-- spec to fill -->` markers for File Structure, Participants, Class Specification, Rules, or Canonical Patterns. |
| **Test-helpers context file** | Yes | Test-helpers package-tier `architecture-context.md` (typically at `tests/<helpers>/architecture-context.md`). | Stop and route back to `abd-architecture-specification`. The template's `templates/tests/` layout cannot be derived without it. |
| **Project toolchain** | Yes | Existing build configuration (`package.json`, `csproj`, `pyproject.toml`, etc.) and a known-runnable existing test command. | **AskQuestion** — what build tool, language, and test runner does `example/` need to be runnable under? |
| **Output slug** | Yes | In `project` mode: project slug (from repo name or `architecture-outline.md` § Application Architecture). In `mechanism` mode: kebab-cased mechanism name. | **AskQuestion** — which slug to use for `docs/architecture/templates/<slug>/`? |
| **Sentinel binding** | Yes | A real-but-not-real domain name for `example/` (e.g. `PartnerA` for Partner Integrations). Should not collide with any actual feature in the project. | **AskQuestion** — propose a sentinel and confirm. |

## Step 1 — Read context

**MANDATORY — read all of these before designing the package:**

| Artefact | Path | Purpose |
|---|---|---|
| Central spec | `docs/architecture/specification/architecture-specification.md` | Where-to-Start lookup; mechanism one-liner; reachable context files. |
| Source mechanism context file | `<host-folder>/architecture-context.md` (resolved from Where-to-Start) | File Structure, Participants, Class Specification, Rules, Canonical Patterns, Across the Codebase — the design source of truth. |
| Test-helpers context file | `tests/<helpers>/architecture-context.md` | Tier names, helper layout, folder structure, spec-alignment table — defines `templates/tests/`. |
| Project toolchain | `package.json` / `csproj` / `pyproject.toml` / `Cargo.toml` / etc. | Language, build, lint, test commands; dependency manifest the example must satisfy. |
| Existing template package (if any) | `docs/architecture/templates/<slug>/` | For idempotent re-runs — drift detection input. |

Do not start Step 2 until the source mechanism's File Structure and Canonical Patterns are both present and non-empty in `architecture-context.md`.

## Step 2 — Design the package

Produce a one-page design (in chat, before writing files) covering:

1. **Package slug** — `<project-slug>` (project mode) or `<mechanism-slug>` (mechanism mode).
2. **Placeholder vocabulary** — every placeholder in the source Canonical Patterns + every additional placeholder needed for the test tiers. Vocabulary must match the spec's verbatim (no inventing new placeholder names).
3. **Participant list** — every file the template package's `template/` directory will contain, copied from the source File Structure.
4. **Tier list for `templates/tests/`** — every tier named in the test-helpers context file, with parameterized file name pattern.
5. **Sentinel binding** — the concrete value each placeholder takes in `example/`.
6. **Rules to lift** — every bullet under § Rules in the source `architecture-context.md`, one file per rule.
7. **Open questions** — anything ambiguous in the source spec that requires a clarifying decision before generation. Surface these as `AskQuestion` items; do not guess.

Wait for user confirmation of the design before proceeding to Step 3.

## Step 3 — Scaffold

### Step 3a — Create the directory

Create `docs/architecture/templates/<slug>/` with subdirectories `template/`, `templates/tests/`, `example/`, `rules/`. Create `README.md` and `parameters.json` placeholders at the package root.

### Step 3b — Write `template/`

For each participant in the source File Structure:

- Create the file at the path the source File Structure prescribes (under `template/`).
- Fill the file with code matching the source Canonical Patterns and Class Specification, using placeholders verbatim (e.g. `class {Domain}Service` not `class DomainService` or `class ExampleService`).
- File **does not need to compile** — placeholders are not valid identifiers. This is intentional and documented in `README.md`.

### Step 3c — Write `templates/tests/`

For each tier in the test-helpers context file:

- Create the parameterized test file under `templates/tests/` at the path the helpers context file prescribes, with placeholder substitution markers (`{epicSlug}`, `{subEpicSlug}`, `{Domain}`).
- Fill the file with the canonical test shape (Given/When/Then or arrange/act/assert) the helpers context file documents, using the same placeholder vocabulary as `template/`.

### Step 3d — Write `rules/`

For each bullet under § Rules in the source `architecture-context.md`:

- Create one file `rules/<kebab-case-rule-name>.md`.
- Body uses the practice's standard rule shape (rule statement + DO / DO NOT with examples). Lift the rationale and failure-mode language from the source bullet verbatim where possible.

### Step 3e — Write `example/`

Bind every placeholder to the sentinel value and write the bound version of every `template/` file and every `templates/tests/` file under `example/`. The bound files **must compile and the bound tests must pass** under the project toolchain.

### Step 3f — Write `parameters.json`

Declare every placeholder used in `template/` and `templates/tests/`, with binding hints (what kind of value binds here) and the sentinel example used in `example/`. Declare the rename map: which placeholder substitutions transform filenames as well as file content.

### Step 3g — Write `README.md`

Short. Sections: **What this is** (one paragraph naming the source mechanism + link to its `architecture-context.md`), **Placeholders** (table from `parameters.json`), **Runbook for `example/`** (build + test commands the user can copy-paste), **How `abd-architecture-code` uses this package** (one paragraph + link to the code skill).

## Step 4 — Run the example

Execute the project toolchain against `example/`:

1. Install dependencies if needed.
2. Build `example/` — must succeed.
3. Run `example/`'s tests — every test must pass.
4. Run the project's lint or static analysis over `example/` — must pass with zero warnings (or document an accepted exception in `README.md`).

If any step fails, fix the template (not the spec) and re-run. If the problem is in the source `architecture-context.md` (a rule that cannot be satisfied, a missing participant), stop and route back to `abd-architecture-specification`.

## Step 5 — Validate

Run every rule in [`rules/`](../rules/) against the produced package. Each rule names what passes and what fails.

For drift detection on re-runs:

- Diff `template/` and `rules/` against what the current source `architecture-context.md` would produce.
- Drift in `template/` (new participant, renamed placeholder) is a violation against [`../rules/template-stays-in-sync-with-spec.md`](../rules/template-stays-in-sync-with-spec.md); fix by re-scaffolding.
- Drift in `rules/` (new rule, changed rule text) is the same; lift the new rule content verbatim.

Run [`common/reference/rule-checklist.md`](../../../../../common/reference/rule-checklist.md) when validation completes.

## Step 6 — Register

Update the central spec's Where-to-Start (or References) section to link the new template package. The link makes the template package discoverable from the spec; the code skill follows this link when resolving `<spec-root>`.

In `mechanism` mode, also update the mechanism's `architecture-context.md` § Overview to link to its template package (one-line link, no inline content).

## Quality bar

- Every source-spec placeholder appears in `template/` verbatim.
- Every test tier from the test-helpers context file appears in `templates/tests/`.
- Every rule bullet from the source spec has a corresponding file in `rules/`.
- `example/` builds, tests pass, lint passes.
- `parameters.json` declares every placeholder used in `template/` and `templates/tests/`.
- `README.md` names the source mechanism and links back to its `architecture-context.md`.
- Re-running on an already-scaffolded package produces a drift report and no silent overwrites.
