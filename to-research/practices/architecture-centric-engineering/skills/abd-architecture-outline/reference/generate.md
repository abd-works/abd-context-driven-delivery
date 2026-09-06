# Generate — abd-architecture-outline

## Read before generating

- **`reference/concepts.md`** — unified document model, system context completeness requirement, packages, mechanisms (merge/remove/rename/add guidance), rules, decisions with stage front matter.
- **`reference/system-context.md`** — deeper guidance on the system context diagram.
- **[`common/reference/record-all-architecture-violations.md`](../../../../../common/reference/record-all-architecture-violations.md)** — violation workflow (existing systems only).

## Output paths

| Artefact | Path |
|---|---|
| Root document (outline fidelity) | `src/architecture-context.md` |
| System context diagram (editable) | `src/system-context.drawio` |
| ADR files | `src/decisions/ADR-NNN-{slug}.md` |

Do **not** write to `docs/architecture/`. The document lives in `src/` alongside the code it describes.

## Step 2a — Surrounding systems section first

The **Surrounding systems** subsection of `src/architecture-context.md` is the canonical element inventory; write it before the diagram. For every system the subject connects to, produce a `###` heading (linked to the system's GitHub repo or product site where applicable) followed by 2–3 sentences naming the system's major functions, its relationship to the subject, and the protocol on the integration boundary. For the subject system itself include a one-line Tech Stack statement for this repo.

The completeness bar is the same as the diagram's: every caller and every downstream is named here. Do not abbreviate or omit entries on the grounds that "detail comes later."

| Template | Output file |
|---|---|
| `templates/architecture-context.md` | The outline-fidelity `src/architecture-context.md` (Surrounding systems section filled in first) |

## Step 2b — Seed system-context.drawio

Create `src/system-context.drawio` as a draw.io XML file. Place the subject system in the centre. Callers on the left, downstreams on the right. Each node shows the system name, a one-line description, and the protocol on each arrow. Use the `<mxfile>` / `<mxGraphModel>` / `<root>` / `<mxCell>` structure. **The diagram nodes and the Surrounding systems `###` entries must be in one-to-one correspondence** — if you add a node, add an entry; if you add an entry, add a node.

## Step 2c — Remaining sections and ADRs

Only after the Surrounding systems section and the diagram are in lockstep, fill in the rest of the document and the ADRs:

| Template | What to produce |
|---|---|
| `templates/architecture-context.md` | The remaining sections of `src/architecture-context.md`: Packages, Architecture Mechanisms, Rules, Decision Records. |
| `templates/decisions/decision-record.md` | One ADR per outline-level decision under `src/decisions/`. |

### System Context section

The surrounding-systems table is **complete at outline stage**. Every system the subject connects to — callers and downstreams alike — is listed with a 2–3 sentence description and a clear role statement. Do not abbreviate or omit entries on the grounds that "detail comes later."

Include a hyperlink to `./system-context.drawio` at the top of the System Context section:

```markdown
> Source: [`./system-context.drawio`](./system-context.drawio)
>
> <!-- ![System Context](./system-context.png) -->
```

The PNG embed comment is left commented-out; it activates once the diagram has been exported.

### Packages section

Write one entry per package. Each entry is the package name — linked to its `architecture-context.md` if that file already exists, plain bold text if it does not — followed by 2–3 sentences covering: the seam it owns, the constraint it places on the rest of the codebase, and the technology named inline in prose. No sub-category labels. All packages are just packages.

On a greenfield system no per-folder files exist yet so no links appear. On an existing system include links wherever the files are present.

### Architecture Mechanisms section

A mechanism is a **recurring code shape that multiple components instantiate** — a pattern, not a topic. Discover the mechanisms this system has by:

1. Walking the surrounding-systems table and asking: what code shapes will repeat across these integrations?
2. Walking the standard vocabulary (Security, Error Handling & Resilience, Logging & Observability, Validation, Configuration & Secrets, Caching, Persistence, Communication) as **discovery prompts** — does this system have this pattern? If yes, include it; if no, omit it silently.
3. Naming bespoke mechanisms when this system has a recurring shape the standard vocabulary does not capture.

Each mechanism entry is: the mechanism name — linked to its `architecture-context.md` if that file already exists, plain bold text if it does not — followed by **one sentence** describing the recurring pattern it establishes.

**Order mechanisms by request flow, not alphabetically.** Ask: what does the system do first when a request arrives? A typical HTTP proxy flows: Configuration → Authentication → primary structural mechanism → Validation → Error Handling → Logging. Reorder to match how your system actually processes a request.

On a greenfield system no per-folder files exist yet so no links appear. On an existing system include links wherever the files are present. Do **not** include an "Omitted" list — simply leave out mechanisms that don't apply.

### Rules section

Write 5–8 one-sentence decidable constraints. Each must name what it constrains (a layer, a folder, a code path, a naming convention) and be verifiable by a reviewer looking at a pull request.

### Decision Records section

List only outline-stage ADRs. The table has columns: `ID | Stage | Decision | One-line consequence`. Write `stage: outline` front matter in each ADR file.

ADR decisions at outline fidelity typically cover: platform and runtime choices, deployment model, significant mechanism merges or removals that represent a deliberate architectural stance.

### ADR front matter

Every ADR file must have a YAML front matter block:

```yaml
---
status: Accepted
date: YYYY-MM-DD
stage: outline
---
```

## Step 2c — Record violations (existing systems only)

If documenting an existing system, follow [`common/reference/record-all-architecture-violations.md`](../../../../../common/reference/record-all-architecture-violations.md) after completing steps 2a and 2b.

## Validate

After generation, verify the diagram:

```powershell
.\scripts\arch-drawio.ps1 verify -ProjectRoot <target-project-root>
```

Then run [`common/reference/rule-checklist.md`](../../../../../common/reference/rule-checklist.md).

**Quality bar:**
- `src/system-context.drawio` present with subject in centre, all surrounding systems as nodes
- Hyperlink to `./system-context.drawio` present in the System Context section
- Every surrounding system has a `###` heading linked to its GitHub repo or product site, followed by 2–3 sentences of prose
- Diagram nodes and Surrounding-systems `###` entries are in one-to-one correspondence (no third inventory file)
- Every package entry is name + link + 2–3 sentences; no sub-category labels
- Every mechanism entry is name + link + one sentence; no Omitted list
- ADRs on disk under `src/decisions/` with `stage: outline` front matter
- Decision Records table has Stage column
