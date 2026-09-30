<!--
  Bounded context map. A context is a module of aggregates.
  A nested context is a context whose parent is a context.
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

`emits:` on the aggregate that publishes. `consumes:` on the aggregate that reacts. The event map at the bottom names the producer and every consumer.

```
emits:
  - {{EventName}}
consumes:
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

emits:
  - {{EventName}}

## {{NestedContextName}} | {{owner}}

### {{Aggregate}}

{{Root Entity}} - one line
  {{Member}}

## event map

- {{EventName}}: emitted by {{Aggregate}}; consumed by {{Aggregate}}, {{Aggregate}}
