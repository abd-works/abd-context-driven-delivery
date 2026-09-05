---
generating-skill: abd-architecture-outline
fidelity: outline
owner: {team-or-person}
last-updated: YYYY-MM-DD
---

# {SystemName} — Architecture Context

> **Purpose.** First-fidelity picture of {SystemName} — what it is, every system it connects to, how its packages organise cross-cutting concerns, the mechanisms that impose code shape, and the rules that govern every deeper decision. This document evolves in place through blueprint and specification fidelity; it is never replaced.

---

## System Context

> Source: [`./system-context.drawio`](./system-context.drawio)
>
> <!-- ![System Context](./system-context.png) -->

{Two or three sentences: what {SystemName} does, who calls it, and what it calls out to. Name the dominant protocol pattern.}

**Tech stack (this repo):** {runtime} · {framework} · {key libs}

### Surrounding systems

Every system {SystemName} connects to is named here at outline stage — knowing the full surface is what makes it possible to define the package structure and decide which concerns need mechanism treatment. Each system name links to its GitHub repo if one exists. Third-party services with no repo are plain text — no product branding links. Links to other repos' own `architecture-context.md` files appear once those files exist.

### [{Caller A}]({github-or-product-url})

{2–3 sentences: what it is, what it does, and how it uses this system — which routes or operations it consumes.}

### [{Caller B}]({github-or-product-url})

{2–3 sentences.}

### [{Downstream A}]({github-or-product-url})

{2–3 sentences: what it is, what it does, and how this system uses it — which operations cross the boundary.}

### [{Downstream B}]({github-or-product-url})

{2–3 sentences.}

*(Every system the subject connects to must appear here at outline stage. Do not omit any.)*

---

## Packages

*(One entry per package. Each entry is the package name as a hyperlink to its `architecture-context.md` once that file exists, followed by 2–3 sentences: the seam it owns, the constraint it places on the rest of the codebase, and the technology named inline.)*

**[{Package name}](./{path}/architecture-context.md)**

{The seam this package owns and the constraint it places on the rest of the codebase. Technology named inline. 2–3 sentences.}

**[{Package name}](./{path}/architecture-context.md)**

{…}

---

## Architecture Mechanisms

*(One entry per mechanism. A mechanism is a recurring code shape that multiple components instantiate. Each entry is the mechanism name as a hyperlink to its `architecture-context.md` once that file exists, followed by one sentence: the recurring pattern this mechanism establishes.)*

**[{Mechanism name}](./{path}/architecture-context.md)**

{One sentence: the recurring pattern this mechanism establishes and why it matters.}

**[{Mechanism name}](./{path}/architecture-context.md)**

{One sentence.}

---

## Testing Architecture

> Source: [`../tests/`](../tests/)
>
> *(At outline fidelity: one paragraph stating the intent, tier names, and what infrastructure tests may or may not require. At blueprint fidelity this expands with per-tier detail.)*

{Testing intent paragraph. Example: "{SystemName} distinguishes unit tests (no network, no file system), sandbox/acceptance tests (full server with real middleware, downstream dependencies stubbed), and integration tests (real downstream services in a controlled environment). All unit tests run in CI without any external service dependency."}

---

## Rules

The rules below are the one-sentence constraints that apply system-wide. Every rule is decidable against a real code change or a design proposal.

- **{Rule name}.** {One sentence naming the constraint and the thing it constrains.}
- **{Rule name}.** {One sentence.}
- **{Rule name}.** {One sentence.}
- **{Rule name}.** {One sentence.}
- **{Rule name}.** {One sentence.}

*(5–8 rules. Each must be one sentence, must name what it constrains — a layer, a folder, a code path, a naming convention — and must be verifiable by a reviewer inspecting a pull request.)*

---

## Decision Records

Outline-stage decisions are listed below. Each has a full record at [`src/decisions/ADR-NNN-{slug}.md`](./decisions/).

| ID | Stage | Decision | One-line consequence |
|---|---|---|---|
| [ADR-001](./decisions/ADR-001-{slug}.md) | outline | {Decision in a few words} | {What becomes true because of this choice.} |
| [ADR-002](./decisions/ADR-002-{slug}.md) | outline | {Decision} | {Consequence.} |

*(Blueprint-stage ADRs are added when this document advances to blueprint fidelity, continuing the same numbering.)*
