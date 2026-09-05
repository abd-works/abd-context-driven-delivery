---
generating-skill: abd-architecture-blueprint
fidelity: blueprint
---

# {SystemName} — Architecture Context

{One or two sentences. What this system is and the primary problem it solves.}

---

## System Context

{Prose. 3–5 sentences. Where this system sits in the larger platform; what initiates calls to it; what downstream systems it orchestrates; what kind of data flows through it. Include the owning repository link as markdown — use the local path for the repo this document lives in; use the public git URL for external repos.}

Source: [./system-context.drawio](./system-context.drawio)

---

## Architecture Flow

{Prose. 2–3 sentences describing a typical end-to-end request: entry point → mechanism layers it crosses → downstream call → response path.}

Source: [./architecture-flow.drawio](./architecture-flow.drawio)

| Step | Layer / File | Mechanisms active |
|---|---|---|
| 1 | **Caller** invokes `{operation}` | — |
| 2 | `{entry-point file}` — request enters | {First mechanism (e.g. Configuration)} |
| 3 | `{auth-middleware file}` — identity verified | {Authentication mechanism} |
| 4 | `{controller or router file}` — payload validated, downstream called | {Validation · System Entity Controllers} |
| 5 | `{downstream adapter file}` — external system called | {System Entity Controllers · Error Handling} |
| — | **RESPONSE** — downstream result mapped and returned | {Error Handling · Logging} |

*Add or remove rows to match the actual layer crossings. The diagram annotates the same steps visually — keep them in sync.*

---

## Packages

{Prose. 2–3 sentences. How packages are organised — by mechanism ownership, by domain entity, or a mix — and what the consistent naming or folder convention is.}

**{package-folder-name}** — [{architecture-context.md}](./{package-folder-name}/architecture-context.md)
{2–3 sentences: seam this package owns, constraint on consumers, technology, key consumers.}

**{package-folder-name}** — [{architecture-context.md}](./{package-folder-name}/architecture-context.md)
{2–3 sentences.}

**{package-folder-name}** — [{architecture-context.md}](./{package-folder-name}/architecture-context.md)
{2–3 sentences.}

*Link each package name to its per-folder `architecture-context.md` where that file now exists. Use plain bold text for packages whose folder files have not been written yet.*

---

## Architecture Mechanisms

{Prose. 1–2 sentences. State the ordering principle (e.g. by request flow: configuration is resolved first, authentication gates every protected path, etc.).}

**{Mechanism Name}** — [{architecture-context.md}](./{mechanism-folder}/architecture-context.md)
{Technology choice — brief, inline. Then 1–2 prose paragraphs describing the code shape it imposes: what every package that participates in this mechanism must do, what it must not do, what the seam looks like from a consumer's perspective.}

**{Mechanism Name}** — [{architecture-context.md}](./{mechanism-folder}/architecture-context.md)
{Technology choice. 1–2 paragraphs.}

**{Mechanism Name}** — [{architecture-context.md}](./{mechanism-folder}/architecture-context.md)
{Technology choice. 1–2 paragraphs.}

*Mechanisms come from this document — not from a standard checklist. Deepen only the mechanisms already named here. Add new mechanisms above if blueprint work surfaces one not yet recorded.*

---

## Testing Architecture

{Prose. 2 sentences on overall test philosophy and the primary quality gate (the tier that must pass before a change ships).}

| Tier | Scope | What is real | What is stubbed | Where it runs |
|---|---|---|---|---|
| Unit | {e.g. Single module, no I/O} | {Module under test} | {All downstream adapters and external SDKs} | {In-process, CI} |
| Sandbox / Acceptance | {e.g. Full HTTP server, stubs at network boundary} | {Express server, real middleware, route handlers} | {All outbound HTTP; stub at `{specific file or interface}`} | {CI} |
| Integration | {e.g. Against real downstream systems in controlled env} | {Everything} | {Nothing} | {Pre-release, gated} |

**Stub boundary:** `{file or interface name}` — the exact location where external systems are replaced in tests. Every per-folder context file references this boundary.

---

## Rules

{One sentence per rule. Each rule is a system-wide, decidable constraint that applies regardless of which package or mechanism is being modified. If you cannot decide from the rule alone whether a given line of code passes or fails, rewrite the rule.}

- {Rule one.}
- {Rule two.}
- {Rule three.}

---

## Decision Records

| ID | Stage | Decision | One-line consequence |
|---|---|---|---|
| [ADR-001](./decisions/ADR-001-{slug}.md) | outline | {Decision} | {Consequence} |
| [ADR-002](./decisions/ADR-002-{slug}.md) | blueprint | {Decision} | {Consequence} |
