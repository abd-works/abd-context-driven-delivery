# Architecture Blueprint — Concepts

## What is an architecture blueprint?

An **architecture blueprint** is the second fidelity level of `src/architecture-context.md` — the same single document that started as an outline. At blueprint fidelity, three things are added or deepened in place:

1. **Architecture Flow** — the section that was absent at outline fidelity is added: a diagram and mechanism-annotated table showing how a typical request flows through the system.
2. **Mechanisms deepened** — each one-liner in the Mechanisms section is expanded to prose: what technology it uses and, critically, what code shape every package that participates in it must adopt.
3. **Packages deepened** — each package entry gains a link to its per-folder `architecture-context.md`, and per-folder files are written with blueprint-fidelity content.

The blueprint also deepens the Testing Architecture section from an intent paragraph to a tier table with named stub boundaries, and adds blueprint-stage ADRs.

---

## The unified document

`src/architecture-context.md` carries the same sections at every fidelity level. Blueprint fidelity adds and deepens — it never replaces or restructures the document.

| Section | Outline | Blueprint |
|---|---|---|
| System Context | Complete; never stripped | Unchanged |
| Architecture Flow | Absent | **Added** — diagram + mechanism table |
| Packages | Prose, no folder links | Deepened — links to per-folder files where they exist |
| Architecture Mechanisms | One-liners | **Deepened** — prose code-shape paragraphs |
| Testing Architecture | Intent paragraph | **Deepened** — tier table + named stub boundary |
| Rules | System-wide constraints | Unchanged; may gain new entries |
| Decision Records | Outline-stage ADRs | **Extended** — blueprint-stage ADRs added, Stage column grows |

---

## Mechanisms as code shapes

The outline states each mechanism's technology choice and one-sentence pattern. The blueprint goes further: for each mechanism it describes **the code shape every package must adopt** — what a developer follows when writing code that participates in that mechanism.

| Dimension | Outline | Blueprint |
|---|---|---|
| Technology choice | Named | Named (retained) |
| One-sentence pattern | Present | Expanded to 1–2 paragraphs |
| Code shape constraint | Not present | **What every participating package must do / must not do** |
| Consumer interactions | Not present | **Which packages call into the mechanism and what they pass** |

**Mechanisms come from `src/architecture-context.md` — not from a standard checklist.** Only deepen mechanisms already named there. If blueprinting surfaces a new mechanism, add it to `src/architecture-context.md` first (in the Mechanisms section), then deepen it here. The master context document is the single source of mechanism vocabulary.

---

## Packages

At blueprint fidelity, per-folder `architecture-context.md` files are written for every package and mechanism-host folder. This is a **default deliverable** — not an opt-in mode.

Each per-folder file carries blueprint-fidelity content:
- Seam owned
- Mechanism(s) it implements or participates in, and what code shape that imposes on consumers
- Technology (named inline)
- Key exports / entry point (enough to convey the surface — not a full file listing)
- Consumers (which other packages depend on this one)
- Test tier and how it is stubbed in tests
- Dependencies on other packages or external systems

This is **not a stub**. A developer reading only this file should understand what the folder is responsible for and how it fits the mechanisms. File structure, participants, class specifications, and canonical patterns are specification-fidelity concerns and are deferred.

Per-folder files are safe to write on both new and existing systems:
- **New system** — create the folders and write the files from the blueprint's package and mechanism descriptions
- **Existing system** — write or update files in folders that already exist, using existing code to validate the content

---

## Architecture flow

The Architecture Flow section is added at blueprint fidelity. It contains a diagram (`src/architecture-flow.drawio`) and a mechanism-annotated table — each row is one layer or boundary in a typical end-to-end request; the right column names every mechanism active at that step. The diagram and table must stay in sync.

The flow is not an exhaustive sequence diagram. It shows which mechanism governs each layer crossing (e.g. Configuration at startup, Authentication at the request gate, Entity Controllers at the downstream call). More than one flow is acceptable when different mechanism combinations apply to meaningfully different paths.

---

## Testing architecture at this level

The outline says "tests exist and what they intend". The blueprint names the **test tiers common to the whole system** — scope, what each tier treats as real vs stubbed, the exact stub boundary (the file or interface where external systems are replaced), and where each tier runs.

The stub boundary is architecture — naming it here means every per-folder context file and every developer writing a new test knows exactly where to draw the line.

---

## Decision records at this level

Blueprint-stage decisions are choices visible at this level: package boundary decisions, test-tier vocabulary, data ownership patterns, significant mechanism code-shape choices. Mechanism technology choices have their ADRs at outline fidelity and are not re-recorded here.

ADRs continue numbering from the last outline ADR. Each blueprint ADR has `stage: blueprint` front matter.

---

## What the blueprint does NOT contain

- Code-level walkthroughs of a mechanism — those belong in per-folder `architecture-context.md` at specification fidelity
- Sequence diagrams with more than three participants — those belong in the mechanism's per-folder file at specification fidelity
- Per-folder file structures (the `src/` tree for a package) — specification fidelity
- Class specifications and canonical patterns — specification fidelity
- Test code examples — specification fidelity
