# Generate — abd-architecture-specification

Follow every file in `rules/`; fill templates exactly.

## When to use

- You want to document an existing codebase so an AI (or new engineer) can navigate and generate code from it reliably.
- No architecture specification exists, or the existing one is stale enough that no one trusts it.
- A spec exists but lacks per-folder `architecture-context.md` files; the central spec carries all detail and is hard to keep current.
- A major refactor or new mechanism has landed and spec + context files need re-alignment.
- An AI assistant or new engineer cannot find their entry point and you want the central spec's Where to Start table to be that entry point.

## Read context

- **`reference/concepts.md`** — two-artefact model, three tiers, boundaries.
- **`reference/discovery.md`** — the classification procedure (walk the tree or design it).
- **`reference/testing-architecture.md`** — test-helpers context file content spec and the central spec pointer rule.
- **[`../../../reference/architecture-mechanism.md`](../../../reference/architecture-mechanism.md)** — mechanism definitions used across the ACE practice.
- **[`common/reference/record-all-architecture-violations.md`](../../../../../common/reference/record-all-architecture-violations.md)** — violation workflow (existing systems only).

## Output

| Artefact | Path | Content |
|---|---|---|
| Central spec | `docs/architecture/specification/architecture-specification.md` | Where to Start table, Overview (≤2 paragraphs), Mechanisms one-liners with links, Package Context categorised list, Source Layout annotated tree, Testing pointer paragraph, References. |
| Per-folder context files | `<folder>/architecture-context.md` for every documented folder | Mechanism / Package / Miscellaneous tier shape per the classification table from discovery. |

## Workflow

Always incremental: discovery first, then create or refresh whichever artefacts the walk or design pass shows are needed.

### Phase 1. Architecture discovery (mandatory)

Follow [discovery.md](./discovery.md) end to end. Do not start Phase 2 without a complete classification table.

**Documentation mode** stops after Phase 3. **Code mode** on a new system continues with [abd-architecture-code](../../abd-architecture-code/) to scaffold the folder structure.

### Phase 2. Author context files first

Author per-folder context files BEFORE the central spec, in this order:

1. **Mechanism-tier files** — largest; central spec summarises them. Fill in: Overview, File Structure, Participants, Class Specification, Rules, Canonical Patterns. Add `### Across the Codebase` when multiple instances exist.
2. **Package-tier files** — one paragraph naming the package and its consumers, then bolded method list for the public surface with one-line "when called" descriptions. Also document internals (helpers, lifecycle, wiring) when they matter for change; stay out of domain rules ([package-context-file-stays-out-of-domain-details](../rules/package-context-file-stays-out-of-domain-details.md)).
3. **Miscellaneous-tier files** — one sentence for tiny; bolded-name flat list for grab-bags. Flag legacy entries inline.
4. **Test-helpers context file** — package-tier file at `tests/<helpers>/architecture-context.md`. Must carry: pattern + stub boundary, layer-to-tech mapping table, folder structure, epic/sub-epic map, spec-alignment table, principles. Full content spec: [testing-architecture.md](./testing-architecture.md).

Use workspace-root paths starting with `/` everywhere. No backticks around links.

#### If a blueprint-scaffolded stub already exists

When `abd-architecture-blueprint` has previously run in `mode: scaffold` (see [`abd-architecture-blueprint` § Optional: scaffold mode](../../abd-architecture-blueprint/reference/concepts.md#optional-scaffold-mode)), per-folder `architecture-context.md` files will already exist with blueprint-fidelity content pre-filled and spec-fidelity slots marked `<!-- spec to fill -->`. In that case:

- **Preserve** the blueprint-fidelity sections (Outline context, Blueprint context, owning module, mechanism code-shape, technology + ADR link, dependencies, test tier) verbatim. Do not edit or remove them.
- **Fill** only the sections marked `<!-- spec to fill -->`. Replace each marker with the spec-fidelity content for that section.
- **Verify** vocabulary alignment as you fill: every mechanism / module / system name used in spec-fidelity content must match the names already present in the blueprint-fidelity sections (and therefore in the centralized documents). Surface drift via the violation workflow rather than silently correcting it.
- **Promote** the seeded `> **Source:** seeded by abd-architecture-blueprint ...` line to also record the spec-author run: append `· spec slots filled by abd-architecture-specification on {ISO-date}` so the file's provenance is auditable.

### Phase 3. Author the central spec

Start from [../templates/architecture-specification.md](../templates/architecture-specification.md) and fill sections in this order:

1. **Where to Start table** — one row per mechanism (and feature-touching package). Each question phrased as a requirement; each link pointing at a context file that exists.
2. **Overview** — at most two short paragraphs naming what the system is, what it is NOT responsible for, and the small set of architectural concerns. No numbered principle list. End with a `> Sources:` blockquote.
3. **Mechanisms** — one one-line entry per mechanism: bold name, parenthetical folder, one-sentence description, link to context file.
4. **Package Context** — categorised list (Mechanisms / Services / Utilities & Legacy / Testing) of every folder that has an `architecture-context.md`.
5. **Source Layout** — annotated tree. Each line has an arrow description; mechanism lines carry a `[Mechanism Name]` tag; dead/legacy folders carry `[dead code]`/`[legacy]`.
6. **Instantiating the Domain** (optional) — short bulleted observation list flagging where the pattern is not uniform.
7. **Testing Architecture** — one paragraph (two short max) pointing at the test-helpers context file. No principles, sandbox examples, or layout tables.
8. **References** — ADR list, blueprint pointer, domain spec, story acceptance criteria, coding/testing standards.

## Update vs author

- **Add a new mechanism / package** — author the new context file; add an entry to Mechanisms or Package Context; update Source Layout; add a Where to Start row if feature-touching.
- **Remove a mechanism / package** — delete the context file; remove from Package Context, Mechanisms, and Source Layout; remove or rewrite the Where to Start row.
- **Rename a mechanism** — update the source of truth (ADR / blueprint) first; then rename the context-file heading, every Where to Start link, every Package Context entry, every Source Layout tag, and every cross-reference.

## Quality bar

- Classification table complete — every documented folder has a tier with a one-sentence justification.
- Context files authored before the central spec; no context-file content inlined in the central spec.
- Where to Start questions are requirements, not code artefacts.
- Every folder with an `architecture-context.md` appears in Package Context.
- Source Layout tags correct: `[Mechanism Name]`, `[dead code]`, `[legacy]`.
- No backtick-wrapped links anywhere.
- Domain rules absent from package-tier context files.
