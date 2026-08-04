# DDD sketch

Declare fidelity once at the top. Use only the sketch for that fidelity — do not fill later-fidelity detail early.

---

## bounded_context

Name each BC, the aggregates it holds, and each dependency with relationship pattern. No class flesh-out yet. Use experts' words.

```
fidelity: bounded_context

{{ContextName}}
  aggregates: {{Root}}, {{Root}}
{{ContextName}}
  aggregates: {{Root}}

{{Source}} → {{Target}}
  direction: {{upstream / downstream | mutual}}
  crosses: {{concepts}}
  integrate: {{concrete call site}}
  pattern: {{Shared Kernel | Customer/Supplier | Conformist | ACL | Open Host | Separate Ways}}
```

---

## building_blocks

Flesh out each aggregate under its BC. Root, invariants, cross-agg and cross-BC deps, sync objects. Stereotypes as you decide them.

```
fidelity: building_blocks

{{ContextName}}
  {{Root}} <<Aggregate Root>> <<Entity>>
    invariants: {{rule}}; {{rule}}
    members: {{Part}} <<Value Object|Entity>>; {{Part}}
    cross-agg:
      → {{OtherRoot}} (by {{IdType}}) — {{immediate | eventual | snapshot}}; {{rule}}
    cross-bc:
      → {{OtherContext}}.{{Root}} via {{SyncObject}} — {{how / when}}
    repo: {{Root}}Repository
    events: {{SomethingHappened}} — consumers: {{who}}
  {{Root}}
    …

{{Source}} → {{Target}}
  sync objects: {{ProductId}}, {{unit_price snapshot}}, …
  integrate: {{concrete call site using those objects}}
  pattern: {{catalogue pattern}}
```

---

## tactics

Architecture + which seams get real adapters.

```
fidelity: tactics

architecture: {{from context | asked | default node+json}}
  repos: {{Root}}Repository → {{persistence}}
  events: {{SomethingHappened}} → {{publish / handle}}
  sync across BC: {{SyncObject}} via {{mechanism}}
```
