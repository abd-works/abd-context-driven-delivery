<!--
  Bounded context map. A context is a module of aggregates.
  A nested context is a context whose parent is a context.
  In code, a context is the folder that contains .context/bounded-context.md.
  The code-format build writes that file when it creates the context folder,
  and creates each aggregate as a folder under that context.
-->

# Bounded Context Map — {{project_name}}

## Map format

`##` is a bounded context. The text after `|` is the **owner** (`custom`, `bespoke`, or the vendor name). `###` is an aggregate inside that context. The first line of the aggregate is its root entity. Indented lines under the root are members — the sub-objects that change with the root.

A nested context is another `##` written inside its parent, before that parent's aggregates. It is a context whose parent is a context, the same way a nested epic sits inside an epic.

Order the contexts you are building first. Systems of record and vendor systems come after them.

### Members

```
{{Root Entity}} - one line
  {{Member}}
  {{Member}}
```

### Integrations

On the aggregate that has the dependency. One target per entry.

| Field | Content |
|---|---|
| **Direction** | upstream, downstream, or mutual — name both sides |
| **What crosses** | What is translated at the boundary |
| **Integration** | The mechanism and the call site |
| **Pattern** | One name from the catalogue |

```
Integrations:
  - {{Target}} (by {{IdType}})
    pattern: Customer/Supplier
    direction: downstream
    crosses: {{what crosses}}
    integration: {{concrete call site}}
```

**Patterns:** Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Open Host / Published Language, Separate Ways.

### Events

`emits events:` on the aggregate that publishes. `consumes events:` on the aggregate that reacts. The event map at the bottom names the producer and every consumer.

```
emits events:
  - {{EventName}}
consumes events:
  - {{EventName}}
```

## {{ContextName}} | {{owner}}

### {{Aggregate}}

{{Root Entity}} - one line
  {{Member}}

Integrations:
  - {{Target}} (by {{IdType}})
    pattern: {{Shared Kernel | Customer/Supplier | Conformist | Anticorruption Layer | Open Host / Published Language | Separate Ways}}
    direction: {{upstream | downstream | mutual}}
    crosses: {{what crosses}}
    integration: {{concrete call site}}

emits events:
  - {{EventName}}

## {{NestedContextName}} | {{owner}}

### {{Aggregate}}

{{Root Entity}} - one line
  {{Member}}

## event map

- {{EventName}}: emitted by {{Aggregate}}; consumed by {{Aggregate}}, {{Aggregate}}

---

## Building blocks fidelity

At **building_blocks**, keep this map as the strategic source of truth for context · aggregate · concept names, integrations, and event ownership. Flesh out each `###` aggregate into a full CE class model using `templates/building-blocks.md`, which **extends** `practices/clean_engineering/templates/class-model.md`.

Under each aggregate in the model artifact:

- Classify every concept with a tactical stereotype (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, `<<Repository>>`, `<<Domain Event>>`, `<<Specification>>`, `<<Factory>>`, `<<Domain Service>>`).
- Add the stereotype-appropriate operations from the **Stereotype operations** table in `building-blocks.md` — repositories `load` · `save` · `search` · `update` · `remove`; specifications `isSatisfiedBy`; aggregate roots own state change and `-> DomainEventPublisher.publish` when a past-tense event must cross the boundary.
- Keep integrations and `emits events` / `consumes events` from this map aligned with the model **Event map** table.

Produce `*-model.md` (artifact `ce-domain-model`) or a `building-blocks` section per context — not a parallel unnamed type list.
