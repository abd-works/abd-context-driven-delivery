# ABD Context Driven Delivery Harness

Agentic tools that bring the best of agile product, delivery, and engineering practices into the age of AI.

## Install

1. Clone this repository into the project workspace, or as a sibling checkout the agent can see.
2. In chat, run `[/install](installation/installer.py)`. That writes skills, rules, MCP, and hooks into the IDE path (`.cursor` for Cursor).

Open `[catalog/index.html](catalog/index.html)` for the board of practices, stages, and actions.

## Basic usage

Name a practice and a action and optionally a format. The action is what to do. The practice is which view of the work.

```
/stories-map /generate /miro {{context}}  ← write the scenario files for that slice

/clean-engineering-code /generate /python {{context}}  <- write software craftmanship level code 

/ddd-tactical-building-block /validate {{context}}  <-- validate ddd elements pass all practice guidance rules
```

Iteratively sketch using multiple views

```
/stories /domain-driven-design /sketch  ← sketch the journey and the domain together, in short passes

```



## Stages

Work moves through three stages. Stay on the current stage until that view agrees, then go deeper on one slice.

- [Discovery](practices/cdd/cdd.md#discovery) — outcome, journey, and architecture, still cheap to change. 
*Use the [Discoverer](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/cdd/agents/discovery.md) agent to run discovery.*
- [Specification](practices/cdd/cdd.md#spec) — one increment: scenarios, domain behavior, and the experience. 
*Use the [Specification](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/cdd/agents/specification.md) agent to run specification.*
- [Implementation](practices/cdd/cdd.md#engineer) — tests, touchpoints, and the solution on the target stack. 
*Use the [Implementation](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/cdd/agents/implementation.md) agent to run implementation.*



## Practices

Tools that refine context in stages, according to a particular perspective.

- [Stories](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/stories.md) — actors, systems, and the interactions that deliver the solution.
  *Use [story-map](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/stories.md#story_map), [scenarios](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/stories.md#scenarios), [acceptance-tests](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/stories/stories.md#acceptance_tests).*
- [Domain-driven design](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ddd/ddd.md) — the business concepts and the boundaries that protect them.
  *Use [bounded-context](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ddd/ddd.md#bounded_context), [building-blocks](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ddd/ddd.md#building_blocks), [tactics](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ddd/ddd.md#tactics).*
- [Clean engineering](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/clean_engineering/clean_engineering.md) — modules, contracts, and the code that can be generated and checked.
  *Use [modules](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/clean_engineering/clean_engineering.md#modules), [model](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/clean_engineering/clean_engineering.md#model), [code](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/clean_engineering/clean_engineering.md#code).*
- [Behavior-driven development](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/bdd/bdd.md) — behavior tests written in the language of the domain.
  *Use [behavior](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/bdd/bdd.md#behavior), [development](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/bdd/bdd.md#development).*
- [User experience](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ux/ux.md) — how people move through and act on the solution.
  *Use [ia](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ux/ux.md#ia), [mockup](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ux/ux.md#mockup), [front-end-code](https://github.com/abd-works/abd-context-driven-delivery/blob/main/practices/ux/ux.md#front_end_code).*

## Actions

- `[/partition](actions/partition/partition.md)` — split context into an index and verbatim segments for each practice.
- `[/document](actions/document/document.md)` — document current state, without adding best practices or correcting it.
- `[/sketch](actions/sketch/sketch.md)` — grill in short passes and sketch only what each answer unlocked.
- `[/grill](actions/grill_context/grill_context.py)` — interview the plan against files you have read.
- `[/generate](actions/generate/generate.md)` — write the artifacts for a practice at its current stage.
- `[/validate](actions/validate/validate.md)` — check artifacts against the practice rules.
- `[/satisfy](actions/satisfy/satisfy.md)` — validate, apply the fixes, and validate again.
- `[/render](actions/render/AGENTS.md)` — convert generated content into another format.
- `[/repair](actions/improvement/repair.md)` — open a repair on a practice and instruct the fix.
- `[/iterate](actions/iterate/iterate.py)` — revise the deliverable in small agreed slices.

