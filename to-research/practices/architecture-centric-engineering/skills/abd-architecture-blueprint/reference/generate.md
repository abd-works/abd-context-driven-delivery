# Generate — abd-architecture-blueprint

## Read before generating

- **`reference/concepts.md`** — what blueprint fidelity adds to `src/architecture-context.md`, mechanism code shapes, packages, architecture flow, testing architecture, per-folder context files, decision records, and what the blueprint does NOT contain.
- **[`common/reference/record-all-architecture-violations.md`](../../../../../common/reference/record-all-architecture-violations.md)** — violation workflow (existing systems only).

Read the project's **`src/architecture-context.md`** before starting. The blueprint deepens what is already there — it does not re-state or re-decide what that document already records.

### Scan existing per-folder context files (existing systems)

If the target project already contains per-folder `architecture-context.md` files, scan them before authoring. Pick up signals at blueprint fidelity:

- **Package signals** — context files name the seam and constraint a folder owns; gather these to validate the Packages section.
- **Code-shape descriptions** — existing files describe canonical patterns; cross-check against the code-shape constraints you intend to write for each mechanism.
- **Inter-package dependencies** — consumer lists surface real dependencies between packages.

Treat per-folder files as a contributing source of truth, not as authority over `src/architecture-context.md`. Where they disagree, surface the conflict via the violation workflow rather than silently overwriting either side.

---

## Output

The blueprint adds to **`src/architecture-context.md`** in place — it does not create a new file. Two sections are added or deepened:

- **Architecture Flow** — added at blueprint fidelity (was absent at outline)
- **Mechanisms** — deepened from one-liners to prose code-shape paragraphs
- **Packages** — deepened from prose to entries linked to per-folder context files (if those files now exist)

ADRs continue numbering from the outline under `src/decisions/`.

Per-folder `architecture-context.md` files are a **default deliverable** at blueprint fidelity — see Step 3.

---

## Step 2a — Architecture Flow section

Add the **Architecture Flow** section to `src/architecture-context.md`. Seed the draw.io diagram:

| Artefact | Path |
|---|---|
| Architecture flow diagram | `src/architecture-flow.drawio` |

The Architecture Flow section contains:
- A link to `./architecture-flow.drawio`
- A prose paragraph describing a typical end-to-end request: entry point → mechanism layers it crosses → downstream call → response path
- A table with columns `Step | Layer / File | Mechanisms active` — one row per layer crossing; the right column names every mechanism active at that step

The diagram and table must stay in sync.

---

## Step 2b — Deepen Mechanisms section

For each mechanism already named in `src/architecture-context.md`, replace the one-liner with a blueprint-fidelity entry:

- The mechanism name — linked to its per-folder `architecture-context.md` if that file exists, plain bold text if it does not
- Technology choice (brief, inline)
- **One to two prose paragraphs** describing the code shape it imposes: what every package that participates in this mechanism must do, what it must not do, and what the seam looks like from a consumer's perspective

**Mechanisms come from `src/architecture-context.md` — not from a standard checklist.** Only deepen mechanisms already named there. If blueprint work surfaces a new mechanism, add it to `src/architecture-context.md` first, then deepen it here.

**Order mechanisms by request flow** — the same order established at outline fidelity.

---

## Step 2c — Deepen Packages section

For each package already named in `src/architecture-context.md`, update its entry:

- Link the package name to its per-folder `architecture-context.md` if that file now exists
- Deepen the description to 2–3 sentences covering: seam owned, constraint on consumers, technology, and key consumers

If blueprint work reveals a package that is missing from `src/architecture-context.md`, add it there first, then include it here.

---

## Step 2d — Deepen Testing Architecture section

Replace the outline's intent paragraph with a tier table:

| Tier | Scope | What is real | What is stubbed | Where it runs |
|---|---|---|---|---|
| Unit | … | … | … | … |
| Sandbox / Acceptance | … | … | … | … |
| Integration | … | … | … | … |

Name the exact stub boundary (the file or interface where external systems are replaced in tests). This becomes the input the per-folder test-helpers context file will reference.

---

## Step 2e — Decision Records

Add blueprint-stage ADRs to the Decision Records table in `src/architecture-context.md` (Stage column value: `blueprint`). Write each ADR file under `src/decisions/` with `stage: blueprint` front matter. Number continues from the last outline ADR.

Blueprint-stage ADRs cover: package boundary decisions, test-tier vocabulary, data ownership patterns, significant mechanism code-shape choices.

---

## Step 3 — Per-folder context files (default, always run)

This step is **not opt-in**. At blueprint fidelity the team has enough structure — package names, mechanism participation, code-shape constraints, dependencies — to write meaningful per-folder `architecture-context.md` files.

### Step 3a — Pre-flight

1. Resolve `<src-root>` — the project's source root. Ask if ambiguous; never guess.
2. Read existing `architecture-context.md` files under `<src-root>` and tabulate: folder exists? context file exists? content matches blueprint?
3. Surface any conflict via the violation workflow before proceeding.

### Step 3b — Write per-folder files

For each package named in `src/architecture-context.md` and each mechanism-host folder:

- Create the folder under `<src-root>` if it does not exist.
- Write `<folder>/architecture-context.md` with blueprint-fidelity content:
  - **Seam** — what boundary this folder owns
  - **Mechanism(s)** — which mechanisms it implements or participates in, and what code shape that imposes on this folder's consumers
  - **Technology** — named inline
  - **Key exports / entry point** — not a full file listing; enough to convey the surface (e.g. "exports `handleError(res, error)` and the `Err` discriminated union")
  - **Consumers** — which other packages depend on this one
  - **Test tier** — which tier this package belongs to and how it is stubbed in tests
  - **Dependencies** — which other packages or external systems this folder depends on

This is **not a stub**. Write enough content that a developer reading only this file understands what the folder is responsible for and how it fits the mechanisms. File structure and canonical patterns are specification-fidelity concerns — defer those.

If `architecture-context.md` already exists in a target folder, **do not overwrite**. Append new blueprint-fidelity content under a "Blueprint updates" section dated with the run timestamp. Surface a conflict if existing content disagrees with `src/architecture-context.md`.

### Step 3c — Report

Produce a run report listing: folders created, files written, files skipped (already exist and match), files updated (content appended), conflicts surfaced.

---

## Step 4 — Record violations (existing systems only)

Follow [`common/reference/record-all-architecture-violations.md`](../../../../../common/reference/record-all-architecture-violations.md). Collect violations found across mechanism and package descriptions, present the table, ask fix or defer, and write a Deferral ADR for every deferred item.

---

## Validate

After generation, verify diagrams:

```powershell
.\scripts\arch-drawio.ps1 verify -ProjectRoot <target-project-root>
```

Then run [`common/reference/rule-checklist.md`](../../../../../common/reference/rule-checklist.md).

**Quality bar:**
- Architecture Flow section present in `src/architecture-context.md` with diagram link and mechanism table
- Every mechanism entry deepened to prose code-shape paragraphs; no one-liners remaining
- Every mechanism and package name matches `src/architecture-context.md` verbatim
- Testing Architecture section has tier table with named stub boundary
- Per-folder `architecture-context.md` present for every package and mechanism-host folder
- Per-folder files have meaningful seam, mechanism, technology, consumers, test tier, and dependencies content — not empty markers
- Blueprint-stage ADRs on disk under `src/decisions/` with `stage: blueprint` front matter
- Decision Records table has Stage column
