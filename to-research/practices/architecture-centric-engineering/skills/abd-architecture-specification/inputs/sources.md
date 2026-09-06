# Sources this skill consumes

This skill produces two artefacts -- a central `architecture-specification.md`
and many per-folder `architecture-context.md` files -- and the only way to
produce them faithfully is to read the codebase being specified plus a
small set of supporting documents. This file lists what to read and why.

## Primary source

Ground truth depends on whether code already exists.

### Existing codebase

The source tree on disk. The procedure in [`../reference/discovery.md`](../reference/discovery.md) Step 1 is a recursive walk; treat what you find as ground truth and the documents below as supporting evidence.

| What to look for | Where to find it |
|---|---|
| **Entry point / bootstrap** | The file or module that starts the process in this repo. |
| **Composition root** | Where this stack wires modules together. |
| **Full source tree** | All folders under the repo's source and test roots. |
| **Test root(s)** | Conventional test folders for this repo (`tests/`, `test/`, …). |
| **Existing context files** | Any `architecture-context.md` under source or test roots — update incrementally. |

### New system (no code yet)

Agreed design artefacts — not an empty folder list. Step 1 in discovery is **design the intended tree**, not walk disk.

| What to look for | Common sources |
|---|---|
| **Mechanisms and layers** | [`abd-architecture-blueprint`](../../abd-architecture-blueprint/), [`abd-architecture-outline`](../../abd-architecture-outline/) |
| **Domain boundaries** | [`abd-domain-specification`](../../../domain-driven-design/skills/abd-domain-specification/), story map |
| **First slices / integrations** | Thin-slice plan, acceptance criteria — which folders will exist at first ship |
| **Folder conventions** | Sibling repo, ADR, team habit — only when the team has actually agreed it |

Documentation mode: spec and context files describe this planned tree. Code mode ([`abd-architecture-code`](../../abd-architecture-code/)): scaffold from the spec.

## Supporting documents

These define the vocabulary and the constraints the central spec must
respect. Read them BEFORE authoring; cite them in `## References`.

| Information needed | Common sources |
|---|---|
| **Architecture source of truth** -- the agreed names for layers, mechanisms, systems. The central spec must use these names verbatim. | ADRs, `docs/architecture/blueprint/*.md`, a sibling skill's output ([`abd-architecture-blueprint`](../../abd-architecture-blueprint/), [`abd-architecture-outline`](../../abd-architecture-outline/)). |
| **Domain specification** -- what the domain types and operations are; the architecture spec stops at the seam between architecture and domain. | `docs/domain/*.md`, output of [`abd-domain-specification`](../../../domain-driven-design/skills/abd-domain-specification/) and [`abd-domain-model`](../../../domain-driven-design/skills/abd-domain-model/). |
| **Coding and testing standards** -- the conventions the codebase already follows, which the spec describes (not invents). | The project's CONTRIBUTING / AGENTS / CLAUDE document, ESLint/Prettier configs, the team's testing skill ([`abd-clean-code`](../../../../foundations/abd-clean-code/), [`abd-story-acceptance-test`](../../../../foundations/abd-story-acceptance-test/) when in scope). |

## Stakeholder input

The Where to Start table at the top of the central spec is a *requirements*
view, and requirements come from the team that ships features. If you are
authoring the spec without access to that team, the routing table will be
generic and unhelpful.

Collect, from the team or from the engagement record:

- **The last three feature requests they shipped**, in the team's own
  words. These become the seed for the Where to Start questions
  ([`../reference/grill-me.md`](../reference/grill-me.md)).
- **The two folders new engineers ask about most often** -- usually the
  composition root and the main repeating-pattern folder. Make sure those are
  context-file documented to a high standard; they are the most-read
  pages.
- **Any house rules the team enforces verbally but has never written
  down** — "every failure path converges at one handler",
  "all third-party SDKs are wrapped before use". These belong in the
  relevant mechanism's `### Rules` section.

## What this skill does NOT consume

- **Generic stack documentation** ("framework X docs say...", "conventional
  patterns for stack Y..."). The spec describes THIS system, not a
  framework tutorial. If the team's actual code differs from conventional
  patterns, the spec describes what the team does.
- **Architectural opinions from outside the engagement.** Do not
  introduce mechanisms the codebase does not have because they would
  be "better practice". That work belongs in a deferral ADR and a
  separate refactor story, not in this spec.
- **Runnable example code.** This skill's previous version produced a
  `template/` slice of runnable code; that responsibility now belongs
  to [`abd-architecture-code`](../../abd-architecture-code/). The
  golden fixture under [`../eval/pass/golden-spec/`](../eval/pass/golden-spec/)
  serves as the worked example for THIS skill.

## Worked example

The fully-worked output for the `pml-midtier` codebase lives at
[`../eval/pass/golden-spec/`](../eval/pass/golden-spec/). It shows the
exact shape this skill produces. Refer to it whenever ambiguity arises
about what a section or context file should look like.

## Outputs

The artefacts this skill produces:

| Output | Path |
|---|---|
| Central spec | `docs/architecture/specification/architecture-specification.md` (or the project's equivalent) |
| Per-folder context files | `<folder>/architecture-context.md` for every folder in the classification table that is documented |

The classification table from discovery is not itself an output (it's a
working artefact); the central spec's `## Package Context` section is
the public, contractual index of every documented folder.
