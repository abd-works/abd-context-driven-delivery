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

The *{{ClassName}}* is {{what it is for, told from the class: the job a caller hires it for}}. The {{ClassName}} {{how it works at a high level, and which classes it works with: who does what to whom}}.

The {{ClassName}} {{the states it moves through: what it is created from, its starting status, and each way it ends}}.

- **{{Responsibility}}.** The {{ClassName}} {{does this, in plain English; behaviour that serves the same responsibility stays in this one bullet}}. {{Where it needs another class: the {{ClassName}} asks the *{{OtherClass}}* to {{do its part}}, and stops there.}}
- **{{Responsibility}}.** The {{ClassName}} has a *{{PartClass}}*, calculated from {{what}}; {{where a value it calculates goes once it is done with it}}.

+ {{ClassName}}({{constructor parameters}})
	// {{what creates it}}
------
+ {{propertyName}}: {{Type}}
	// {{an invariant this property keeps, or why it exists}}
+ << {{composition | aggregation | association}} >> {{collaborator}}: {{Type}}
----
+ {{operationName}}({{parameters}}): {{ReturnType}}
	-> {{Collaborator}}.{{operation}}
	// {{constraint or outcome — use -> named failures when a rule rejects the act}}
+ {{stateChangingOperation}}({{parameters}}): {{ReturnType | DomainEvent}}
	-> {{EventPublisher | Repository}}.{{publish | save | update}}
	// state change on this resource; submit the domain event when other aggregates or contexts must react

**Invariants**

- {{must / never / always — a rule no single member governs; one a single member governs is a `//` line under it}}

---

## Event map

| Event | Emitted by | Operation | Consumed by |
|-------|------------|-----------|-------------|
| {{PastTenseEvent}} | {{Aggregate Root}} | {{operation that builds and submits it}} | {{Consumer}} |
