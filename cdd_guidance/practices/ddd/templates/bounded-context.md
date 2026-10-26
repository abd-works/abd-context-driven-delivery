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

## Model fidelity

At **model**, keep this map as the strategic source of truth for context · aggregate · concept names, integrations, and event ownership. Draw each `###` aggregate as a class model using `templates/model.md`, which **extends** `practices/clean_engineering/templates/class-model.md`:

- The root (`<<Aggregate Root>> <<Entity>>`) with its properties and domain operations, its `<<Repository>>` directly beneath it (drawn inside the root's card in the rendered view), and its members (`<<Entity>>`, `<<Value Object>>`) composed by it.
- An arrow from each class that needs another aggregate to that aggregate's root, held by identity, with the call on the operation that uses it.
- Nothing else — factories, specifications, domain services, and event classes wait for **tactics**.

Keep integrations and `emits events` / `consumes events` on this map aligned with the model's arrows.
