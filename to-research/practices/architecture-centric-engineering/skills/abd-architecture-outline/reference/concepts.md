# Architecture Outline — Concepts

## What is an architecture outline?

An **architecture outline** is the first fidelity level of `src/architecture-context.md` — the single root document that evolves through outline → blueprint → specification without ever changing its file path or TOC. At outline fidelity the document is authored before any folder structure exists; it establishes shared facts the whole team starts from.

The outline answers: what is this system, what does it sit next to, what packages govern its cross-cutting concerns, which mechanisms impose code shape, and what rules constrain every decision that follows?

This skill ships **two artefacts**: the `src/architecture-context.md` root document (at outline fidelity), and a `src/system-context.drawio` diagram — the only diagram produced at this stage.

---

## The unified document

`src/architecture-context.md` carries the same sections at every fidelity level. Section headings are **not numbered** — sections are added or absent depending on fidelity, and numbering breaks every time one is added or removed.

- **System Context** — surrounding systems diagram + prose (complete at outline; never stripped later)
- **Architecture Flow** — absent at outline; added at blueprint
- **Packages** — prose paragraphs at outline (no folder links); one-liners + links at specification
- **Architecture Mechanisms** — one-sentence entries at outline (no folder links); one-liners + links at specification
- **Testing Architecture** — intent paragraph at outline; tier table at blueprint
- **Rules** — system-wide constraints; established at outline, refined later
- **Decision Records** — outline-stage ADRs only at this fidelity; stage column grows over time

At blueprint and specification fidelity, the same file is *updated* — content migrates into per-folder `architecture-context.md` files and the root shrinks to one-liners + links. The file is never deleted or replaced.

---

## System context

The outline's primary deliverable. It must be **complete at outline stage** — knowing every system the subject connects to is a prerequisite for every package and mechanism decision. The surrounding-systems table is not a sketch; it is the agreed-upon boundary. It does not shrink at later fidelity levels.

The system context diagram (`src/system-context.drawio`) shows the same information visually: the subject system, every caller, every downstream, and the protocols across each boundary.

The **Surrounding systems** subsection of `src/architecture-context.md` is the canonical element inventory. The diagram and that section are kept in lockstep — every node in the diagram appears as a `###` entry in the section, and every section entry appears as a node in the diagram. There is no third file.

**Tech Stack belongs in the System Context section** as a brief inline statement for *this repo only*. External systems' stacks are described in their own repos' context files, not here.

---

## Packages

Each package entry is the package name — **linked to its per-folder `architecture-context.md` if that file already exists, plain bold text if it does not** — followed by 2–3 sentences covering: the seam it owns, the constraint it places on the rest of the codebase, and the technology named inline. No sub-category labels (mechanism-host, service package, entity-instance, utility). All packages are just packages.

On a **greenfield** system the folders and per-folder context files do not exist yet, so entries have no links. On an **existing** system those files may already be present; include the links when they exist. The result is that an outline for an existing system will look much like a specification in terms of link presence — that is correct and expected.

---

## Architecture mechanisms

A **mechanism** is a recurring code shape that multiple components instantiate — a pattern, not a topic. Naming "Authentication" as a mechanism is a commitment that there is one principle, one named pattern, one technology choice, and a known set of components that will follow that pattern. If you cannot name those four things, you have not identified a mechanism.

The standard mechanism vocabulary — Security, Error Handling & Resilience, Logging & Observability, Validation, Configuration & Secrets, Caching, Persistence, Communication — is a **discovery prompt**. For each entry, ask: does this system have this pattern recurring across multiple components? If yes, include it; if no, omit it silently. When the system has a recurring shape the standard vocabulary does not name, add a **bespoke mechanism**.

Each mechanism entry is the mechanism name — **linked to its per-folder `architecture-context.md` if that file already exists, plain bold text if it does not** — followed by one sentence describing the recurring pattern it establishes.

**Order mechanisms by request flow, not alphabetically.** Ask: what does the system do first when a request arrives, and what is ambient throughout? A typical HTTP proxy flows: Configuration → Authentication → primary structural mechanism → Validation → Error Handling → Logging. Reorder to match how your system actually processes a request.

On a **greenfield** system entries have no links. On an **existing** system include links where the per-folder files exist. Do **not** include an "Omitted" list — simply leave out mechanisms that don't apply.

---

## Rules

The outline establishes **rules** — one-sentence decidable constraints that apply across the whole system. A rule is verifiable: a reviewer can look at a code change and say "this violates rule 3" or "this is fine under rule 3."

Rules are the same section used in per-folder `architecture-context.md` files throughout all fidelity levels.

5–8 rules at outline stage is typical. Rules are added, refined, or removed as the document evolves through later fidelity levels.

---

## Decision records

ADRs live in `src/decisions/` and have `stage: outline` front matter. The outline lists only the ADRs raised during outline work — typically platform choices, deployment model, and the decisions behind any major mechanism merges or removals.

The ADR table in `src/architecture-context.md` includes a **Stage** column. Blueprint-stage ADRs are added at blueprint fidelity (continuing the same numbering); specification-stage ADRs at specification fidelity. The full history accumulates in one table.

---

## What the outline does NOT contain

- **Architecture Flow diagram** — added at blueprint fidelity once folder structure exists
- **Module overview / platform / testing-flow diagrams** — added at blueprint fidelity
- **Folder links** in the Packages or Mechanisms sections — added as folders and per-folder context files are created
- **Separate Technology Stack table** — tech is inline prose in the System Context and Packages sections
- **Separate Major Systems table** — the surrounding systems table in System Context already covers this; a separate section is duplication
- **Separate Principles section** — the concept is expressed through the Rules section
- **Deep mechanism walkthroughs** — those live in per-folder `architecture-context.md` files at specification fidelity
