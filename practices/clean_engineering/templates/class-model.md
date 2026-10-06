---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

# {{Module or bounded context name}}

**Sources / context:** {{story-map · bounded-context-map · sketch paths — read in full}}

**Module:** `{{module-path}}`

{{One paragraph: what this module owns and the job callers hire it for.}}

---

## {{Resource group — aggregate or collaborating cluster}}

{{Why these types belong together. Invariants that span the cluster.}}

### **{{ClassName}}** <<{{Stereotypes}}>>

+ {{ClassName}}({{constructor parameters}})
------
+ {{propertyName}}: {{Type}}
	// {{why this property exists}}
+ << {{composition | aggregation | association}} >> {{collaborator}}: {{Type}}
----
+ {{operationName}}({{parameters}}): {{ReturnType}}
	-> {{Collaborator}}.{{operation}}
	// {{constraint or outcome — use -> named failures when a rule rejects the act}}
+ {{stateChangingOperation}}({{parameters}}): {{ReturnType | DomainEvent}}
	-> {{EventPublisher | Repository}}.{{publish | save | update}}
	// state change on this resource; submit the domain event when other aggregates or contexts must react

**Invariants**

- {{must / never / always — one rule a caller can break by using the object wrong}}

**Interactions**

- {{which collaborator owns the next act — through a named public operation only}}

---

## Event map

| Event | Emitted by | Operation | Consumed by |
|-------|------------|-----------|-------------|
| {{PastTenseEvent}} | {{Aggregate Root}} | {{operation that builds and submits it}} | {{Consumer}} |
