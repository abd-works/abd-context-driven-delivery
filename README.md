# ABD Context Driven Delivery Harness

Agentic tools that bring the best of agile product, delivery, and engineering practices into the age of AI.

## Install

1. Clone this repository into the project workspace, or as a sibling checkout the agent can see.
2. In chat, run [`/install`](installation/installer.py). That writes skills, rules, MCP, and hooks into the IDE path (`.cursor` for Cursor).

Open [`catalog/index.html`](catalog/index.html) for the board of practices, stages, and actions.

## Basic usage

Name a practice and a action. The action is what to do. The practice is which view of the work.

```
/stories-scenarios /generate  {{context}}  ← write the scenario files for that slice
/clean-engineering-code /validate  context ← check code against practice rules
```

Iteratively sketch using multiple views

```
/stories /domain-driven-design /sketch  ← sketch the journey and the domain together, in short passes

```

## Stages

Work moves through three stages. Stay on the current stage until that view agrees, then go deeper on one slice.

- [Discovery](practices/cdd/cdd.md#discovery) — outcome, journey, and architecture, still cheap to change.
- [Specification](practices/cdd/cdd.md#spec) — one increment: scenarios, domain behavior, and the experience.
- [Implementation](practices/cdd/cdd.md#engineer) — tests, touchpoints, and the solution on the target stack.

## Practices

The knowledge graph is these models and the relationships between them. CodeQL reads them out of the code.

- [Stories](practices/stories/stories.md) — actors, systems, and the interactions that deliver the solution.
- [Domain-driven design](practices/ddd/ddd.md) — the business concepts and the boundaries that protect them.
- [Clean engineering](practices/clean_engineering/clean_engineering.md) — modules, contracts, and the code that can be generated and checked.
- [Behavior-driven development](practices/bdd/bdd.md) — behavior tests written in the language of the domain.
- [User experience](practices/ux/ux.md) — how people move through and act on the solution.

## Actions

- [`/partition`](actions/partition/partition.md) — split context into an index and verbatim segments for each practice.
- [`/document`](actions/document/document.md) — record what already exists, without correcting it.
- [`/sketch`](actions/sketch/sketch.md) — grill in short passes and sketch only what each answer unlocked.
- [`/grill`](actions/grill_context/grill_context.py) — interview the plan against files you have read.
- [`/generate`](actions/generate/generate.md) — write the artifacts for a practice at its current stage.
- [`/validate`](actions/validate/validate.md) — check artifacts against the practice rules.
- [`/satisfy`](actions/satisfy/satisfy.md) — validate, apply the fixes, and validate again.
- [`/render`](actions/render/AGENTS.md) — convert generated content into another format.
- [`/repair`](actions/improvement/repair.md) — open a repair on a practice and instruct the fix.
- [`/iterate`](actions/iterate/iterate.py) — revise the deliverable in small agreed slices.
