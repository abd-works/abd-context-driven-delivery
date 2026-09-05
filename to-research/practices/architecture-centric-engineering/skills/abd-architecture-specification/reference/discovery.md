# Architecture discovery

Procedure: classify each folder (mechanism, package, miscellaneous), tag dead/legacy in Source Layout when needed, use grilling questions when ambiguous. Why this is mandatory: [`concepts.md` § Architecture discovery](./concepts.md#architecture-discovery).

**Supporting skills** (optional; none replaces discovery):

| Skill | Use |
|---|---|
| [`abd-code-research`](../../abd-code-research/) | Explorer + Deep Dive when an existing codebase is unfamiliar |
| [`abd-architecture-outline`](../../abd-architecture-outline/) | Layer and system names — required input on new systems |
| [`abd-architecture-blueprint`](../../abd-architecture-blueprint/) | Mechanisms catalogue — design input on new systems; name cross-check on existing |



## Existing vs new — same procedure, different Step 1

The outcome is always the same: a full tree, a classification table, context files, and a Source Layout. Only where the tree comes from changes.

| Situation | Step 1 | Steps 2–3 evidence |
|---|---|---|
| **Existing codebase** | Recursively enumerate what is on disk | Read files — entry point and activation layer, repetition, consumers |
| **New system** | Design the intended tree before code exists | Blueprint, outline, domain spec, stories — which patterns repeat, which packages, where folders should live |

Steps 4–7 (decision tree, tabulate, sanity-check) are identical. On a new system the tree in Step 1 is **planned**, not discovered by `ls`.



## Documentation mode vs code mode

This skill produces **documentation**. On a new system, documentation mode is usually the whole job first: name mechanisms and packages, pick folder paths, write context files and Source Layout **in advance of any code**.

**Code mode** (typically [`abd-architecture-code`](../../abd-architecture-code/) in a follow-up pass): create folder skeletons and minimal stubs from the spec. Do not invent structure at scaffold time — implement what the spec already describes.

On an existing codebase, documentation mode means walk → update stale docs. Code mode means the spec already exists and implementation changes follow it.



Tier definitions and templates: [concepts.md § Three tiers](./concepts.md#three-tiers). Dead or legacy folders are not a tier — tag them `[dead code]` or `[legacy]` in Source Layout.



## Procedure — step by step

**Grilling mode** — open [`grill-me.md`](./grill-me.md) before starting (mechanics: [`common/reference/grill-me-with-practice-skill.md`](../../../../common/reference/grill-me-with-practice-skill.md)). Ask each question visibly, then answer it yourself by reading code, files, or other available context. Only surface a question to the user when no source can answer it. On a **new system** there is no code yet, so most answers must come from the user — grill first before naming a single folder. On an **existing codebase** the code is the primary source of answers; grill throughout and answer from what you read.

Take notes throughout for the Where to Start table and Package Context list.

### Step 1. Establish the full tree

**Existing codebase** — recursively walk every source root (`src/`, `app/`, `lib/`, `packages/<name>/src/`, …) and every test root (`tests/`, `test/`, `__tests__/`, `spec/`). List the complete folder tree — all nesting levels. Include bootstrap and composition-root entry files where they sit (names vary by stack).

**New system** — design the same shape before folders exist. Start from blueprint, outline, domain spec, and story map: decide mechanism folders (with replication recipes), package folders, miscellaneous holders, bootstrap and composition-root paths, test-helper layout. Write the tree as you intend it on disk. Grilling and the decision tree apply to **planned** modules the same way they apply to existing folders.

Do not classify yet — enumerate or design the tree only.

Example shape (folder names are illustrative — use what this system actually has or plans):

```
src/
+-- bootstrap.*
+-- composition.*
+-- config/
+-- setup/
|   +-- Identity/
+-- shared/
|   +-- errors/
|   +-- validation/
+-- adapters/
|   +-- OutboundClient/
|   +-- IdentityProvider/
|   +-- Logging/
+-- integrations/
|   +-- PartnerA/
|   +-- PartnerB/
+-- legacy-types/

tests/
+-- test-helpers/
+-- partner-a/
|   +-- ...
```

### Step 2. Pin down the entry point and activation layer

**Existing:** find the bootstrap/entry file — where this stack starts the process — AND the activation layer behind it: composition root (explicit wiring), framework scanner config (auto-discovery), or the base class plus its known consumers (inheritance-style activation). Note which folder each lives in.

**New:** decide where those files will live and which activation style the system will use. A folder reliably activated when standing up a repeating pattern — whether by explicit registration, framework scan, or consumer-side construction of an inherited base — is almost certainly part of a mechanism, not miscellaneous.

### Step 3. For each folder, pull three signals

**Existing codebase** — read what is on disk:

1. **Repetition** — sibling subfolders or files with the same internal skeleton? Templated pattern ⇒ likely mechanism.
2. **Surface** — one coherent public API, or unrelated utilities in one folder?
3. **Consumer** — who imports this today? Many callers, one consumer, or nobody (dead code)?

Judge from contents, not folder names (`services/`, `helpers/`, …).

**New system** — read what the design says each planned folder is for:

1. **Repetition** — will new features add siblings with the same skeleton? (blueprint, story map, thin slice.) Templated pattern ⇒ likely mechanism.
2. **Surface** — one coherent module at first ship, or a holder for unrelated utilities?
3. **Consumer** — who will depend on this when the first slice lands? Many callers, one consumer, or nothing planned yet?

Judge from planned role, not the folder name you picked in Step 1.

### Step 4. Classify each folder against the decision tree

```
Is there an activation layer that brings this folder's files to life —
explicit wiring, framework scan, or consumer-side use of an inherited
base — OR sibling subfolders that share the same skeleton (3+ files
in the same shape)?

|-- YES: Does the folder document HOW NEW SIBLINGS ARE ADDED?
|   |   (recipe: "start with these files; add optional files when needed")
|   |
|   |-- YES: --> MECHANISM
|   |-- NO:  --> Step 5 (package with organic structure, or undocumented recipe)
|
|-- NO: Does the folder expose a coherent public surface?
|
|   |-- YES: More than two sentences to describe? --> PACKAGE / else MISCELLANEOUS (tiny)
|   |-- NO:  Multiple unrelated utilities? --> MISCELLANEOUS (grab-bag)
|            Else still imported? --> MISCELLANEOUS (tiny) / else DEAD CODE
```

### Step 5. Resolve ambiguous cases

When the decision tree does not settle a folder, return to [`grill-me.md`](./grill-me.md) — one question at a time; generate-to-learn when enough is shared.

Heuristics while grilling:

- One class, long file — package if consumers pick between named operations; miscellaneous-tiny if one entry point always does the same thing.
- Sibling subfolders that drift — package if drift is acceptable; mechanism if every new sibling must follow a fixed recipe.
- Helper imported everywhere — miscellaneous-tiny unless the team extends it with a defined recipe (then mechanism).

### Step 6. Tabulate

Record a classification table — folder, tier, one-sentence why. One row per folder from Step 1 that owns code or will appear tagged in Source Layout; empty parent containers roll up to their children. Worked example (illustrative paths):

| Folder | Tier | Why |
|---|---|---|
| `src/config/` | Mechanism | Bootstrap: env → secrets → typed settings; every new setting follows the same recipe. |
| `src/setup/Identity/` | Mechanism | Wired from composition root; new protected areas copy the skeleton. |
| `src/integrations/` | Mechanism | Sibling `{Partner}/` folders share the same file skeleton. |
| `src/shared/errors/` | Mechanism | Typed failure pipeline every inbound handler uses. |
| `src/adapters/OutboundClient/` | Package | Single factory; multiple consumers; connection behaviour. |
| `src/adapters/IdentityProvider/` | Package | One module; Identity setup consumer. |
| `src/adapters/SupportTickets/` | Package | Payload builders; one consumer (PartnerA integration). |
| `src/adapters/Logging/` | Miscellaneous (tiny) | Singleton entry point; used everywhere. |
| `src/shared/` | Miscellaneous (grab-bag) | Validation, tokens, dates, deprecated helpers — no shared abstraction. |
| `src/legacy-types/` | Dead code | Old schema types; nothing live imports them. |
| `tests/test-helpers/` | Mechanism (testing) | Templated test fixtures every story extends. |

For a real codebase-shaped fixture, see [`../eval/pass/golden-spec/`](../eval/pass/golden-spec/).

The table catalogs what you learned or designed; it is not a substitute for understanding the system.

### Step 7. Sanity-check

Every folder from Step 1 that owns code appears in the table or is explicitly marked `[no context file]` with a one-sentence reason. Do not silently drop nested folders you never opened.



## Anti-patterns

- Classifying by folder name instead of contents (existing) or planned role (new).
- Promoting everything to mechanism — most folders are packages or miscellaneous.
- Documenting domain rules in architecture context files — internals are fair game, but business invariants and state machines belong in `abd-domain-specification`.
- Inventing patterns the team does not actually follow (existing) or will not follow (new).
- Skipping discovery because you "already know" the codebase — that is remembering, not mapping.
- Skipping discovery because **no code exists yet** — design the tree and classify planned folders first; empty disk is not an excuse.
- Walking disk on a greenfield repo with nothing to walk — use blueprint/stories and design Step 1 instead.



## Handoff to authoring

When architecture discovery is complete you have:

1. **Understanding** — entry point, activation layer (composition root / scanner / inheritance contract), how areas relate, rules (observed or intended).
2. **Classification table** — every documented folder; proof you walked or designed the tree.
3. **Mechanism rules** — must/must-never for context file Rules sections.
4. **Recent feature examples** — raw material for Where to Start.
5. **Source-of-truth pointers** — ADRs, blueprint, outline for References.

Next: [`generate.md`](./generate.md).
