# knowledge_graph sketch — increment 1 (Create Customer + Get Number)

One file: object model + BDD + guidance rule binding. Extends existing practice nodes. CodeQL populate and rule evaluation are later increments behind the same `load`.

This is a **practice graph** — one navigable object model. Each node is **both**:

- a **graph node** (participates in the unified practice graph), and
- a **practice instance** (a typed node from Clean Engineering, DDD, Stories, or BDD).

Practices are **stereotypes and extra edges** on that model, not four parallel trees.

```
practices/knowledge_graph/
  graph -> stories, clean_engineering, ddd, bdd
```

---

## Practice graph (root)

```
PracticeGraph
  load(path)
    StoryMap — loadedFrom — path
    CleanEngineeringModel — loadedFrom — path
  stories                           # keyed Epic roots (Stories practice view)
  modules                           # keyed Module roots (CE / DDD practice view)
  descriptions                      # keyed Description roots (BDD practice view)
  nodes                             # all GraphNodes keyed by stable id (optional flat index)
  relationships                     # all GraphRelationships (from, kind, to)
  evaluate_rules()                  # bind guidance rules; fill node.rules.*.violations (increment 2+)
```

Every typed node below **is a GraphNode** unless noted.

---

## GraphNode (common)

```
GraphNode
  graph                             # PracticeGraph — memberOf — GraphNode
  practice                          # clean_engineering | ddd | stories | bdd
  usedBy                            # reverse index: GraphNode — usedBy — GraphNode
```

`usedBy` is populated from `GraphRelationship.to` — e.g. `CustomerRepository.usedBy` includes the Step that has `Step — invokes — CustomerRepository.load`.

---

## Guidance rules on nodes

Every node is subject to one or more **guidance rules** — **directly** (the rule names that node type at that fidelity) or **through a parent** (rules scoped to ancestors or containers also apply to descendants in scope).

Guidance is organised per practice (`stories`, `clean_engineering`, `ddd`, `bdd`). Each practice publishes:

- **Shared rules** — apply across fidelities when the node (or an ancestor in scope) matches the practice and the rule’s node filter.
- **Fidelity-specific rules** — apply only when the active fidelity narrows which node types are in scope.

**Fidelity narrows the node set**, not a separate tree. Examples:

| Practice | Fidelity | Node types in scope (typical) | Cross-practice edges rules may use |
|----------|----------|--------------------------------|-------------------------------------|
| Stories | `story_map` | Epic, SubEpic, Story | — |
| Stories | `scenarios` | Scenario, Background, Step, Example | — |
| Stories | `acceptance_tests` | Step (runnable), Example | Step — invokes — Operation; Step — uses — Example |
| Clean Engineering | `modules` | Module | Module — dependsOn — Module |
| Clean Engineering | `model` | Module, Class, Property, Operation | Class — associates — Class; hasType / returns |
| Clean Engineering | `code` | Class, Property, Operation (from source) | Operation — invokes — Operation |
| DDD | `bounded_context` | BoundedContext, Aggregate (concept names) | BoundedContext — owns — Aggregate |
| DDD | `building_blocks` | Entity, EntityRoot, Repository, ValueObject, … | Repository — accesses — EntityRoot |
| BDD | `behavior` | Description, Context, Observation | Observation — observes — Property/Operation |

A **Scenario** node at scenarios fidelity is directly subject to scenarios rules. It may also inherit story-map rules when the rule scope includes Story-owned descendants. An **acceptance_tests** Step is subject to acceptance-test rules that can require `Step — invokes — Operation` and trace examples to classes.

### Rule binding (sketch)

```
GuidanceRule
  slug: string                        # e.g. scenarios-must-have-examples
  practice: string                    # stories | clean_engineering | ddd | bdd
  fidelity: string | null             # null = shared; else fidelity name
  applies_to: string[]                # semantic types: Scenario, Step, Class, Repository, …
  inherits_to_children: bool          # when true, owned descendants are also in scope
  predicate                          # graph constraint (see below)
```

Rules are **not** stored as parallel trees. They attach to **GraphNodes** already in the practice graph. Evaluation uses the same `relationships` index as navigation (plus CodeQL populate facts when loaded).

### Node.rules — violation queries

Each graph node exposes a **rules view** for violations already evaluated on the loaded graph (increment 2+; sketch API first):

```
GraphNode
  rules
    violations                       # all violations for every rule that applies
                                     # (direct + inherited from ancestors in scope)

    direct
      violations                     # rules whose practice + closest fidelity match
                                     # this node’s type — e.g. Scenario → scenarios fidelity

    practice(name)                   # optional filter — only that practice’s rules
      .shared
        violations
      .fidelity(name)                # optional — only that fidelity’s rules
        violations
```

**Examples**

```python
scenario.rules.violations
# every rule that applies to this scenario (scenarios + inherited story_map if in scope)

scenario.rules.direct.violations
# only rules that target Scenario at the closest matching fidelity (typically scenarios)

scenario.rules.practice("stories").fidelity("acceptance_tests").violations
# only acceptance-test rules that apply to this node (empty on a Scenario unless
# the rule scope includes Scenario or a owned Step/Example)
```

**Closest fidelity:** the finest-grained fidelity whose `applies_to` includes the node’s `_semantic_type_name` and whose practice matches `node.practice` (or the practice that owns the rule for cross-practice rules). Direct violations exclude rules that only apply because a **parent** was in scope unless `inherits_to_children` propagates them to this node.

### Rule evaluation — graph + CodeQL, not per-file scanners

Today, scanners reopen files, re-parse AST, and look for one local shape per rule. The practice graph + CodeQL populate path replaces that with **constraints over the shared model**:

1. **Load** — prose skeleton + CodeQL facts (`PracticeGraph.load`).
2. **Bind rules** — for each node, compute applicable rule set from practice, fidelity, type, and ancestor scope.
3. **Evaluate** — run each rule’s predicate against graph edges (and CodeQL export where needed).
4. **Attach** — materialise violations on `node.rules.*.violations`.

A rule predicate is a **graph query** (CodeQL or declarative filter over `relationships`), not a file walk. Examples:

```
# scenarios-must-have-examples
Scenario scenario
where not exists(Example e | scenario — scopes — e)
select scenario, "Scenario has no examples."

# step-invokes-domain-operation (acceptance_tests)
Step step
where step.phase = "when"
  and not exists(Operation op | step — invokes — op)
select step, "When step does not invoke a domain operation."

# example-demonstrates-class
Example example
where not exists(Class c | example — demonstrates — c)
select example, "Example is not linked to a domain class."

# repository-owns-lifecycle-not-domain-behaviour (building_blocks)
Operation op, Repository repo
where repo — owns — op
  and op mutates aggregate state internally on Class owned by repo
  and not op.isCollectionLifecycle()
select op, "Repository exposes business behaviour instead of collection lifecycle."

# entity-owns-its-mutations (building_blocks / code)
Operation op, Class cls
where cls — owns — op
  and op writes fields on cls
  and exists(Operation other | other — invokes — op | other on sibling Class)
select op, "Object with the data does not own the operation."
```

CodeQL is the reliable source for **calls, mutations, and type resolution**; the graph holds **practice identity** (Scenario, Repository, Step — invokes — Operation). A rule may combine both: graph edge must exist **and** CodeQL confirms the callee mutates state.

Existing file scanners remain useful during migration; new rules should target the graph query surface first.

### Violation shape

```
RuleViolation
  rule_slug: string
  node: GraphNode                     # the node in scope (may be parent if inherited)
  message: string
  practice: string
  fidelity: string | null
  source                             # optional SourceLocation from node or CodeQL site
```

---

## GraphRelationship (every edge)

Every relationship names **left**, **kind**, and **right**. No one-sided fields.

```
GraphRelationship
  from: GraphNode
  kind: string
  to: GraphNode
```

---

## Clean Engineering (base practice)

```
Module : GraphNode
  practice = clean_engineering
  Module — owns — Class

Class : GraphNode
  practice = clean_engineering
  Class — belongsTo — Module
  Class — owns — Property
  Class — owns — Operation
  Class — associates — Class              # same-module composition / reference
  Example — demonstrates — Class        # cross-practice: fixture data shows the Class
  Description — describes — Class       # cross-practice: BDD subject under test
  Repository — accesses — EntityRoot    # cross-practice: DDD collection lifecycle entry

Property : GraphNode
  practice = clean_engineering
  Property — belongsTo — Class
  Property — hasType — Class              # field, getter, or observable state type
  Step — observes — Property              # cross-practice: Stories Then step
  Observation — observes — Property       # cross-practice: BDD outcome
  Entity — hasIdentity — Property         # cross-practice: DDD identification

Parameter : GraphNode
  practice = clean_engineering
  Parameter — belongsTo — Operation
  Parameter — hasType — Class

Operation : GraphNode
  practice = clean_engineering
  Operation — belongsTo — Class           # declaring class
  Operation — hasParameter — Parameter
  Operation — returns — Class             # void / absent when no return type
  Operation — invokes — Operation         # callee on same class or another class
  Step — invokes — Operation              # cross-practice: Stories When step
  Step — observes — Operation             # cross-practice: Stories Then step
  Observation — observes — Operation      # cross-practice: BDD outcome
  Entity — hasIdentity — Operation        # cross-practice: DDD identification
```

**Type resolution:** `hasType` and `returns` resolve to `Class` nodes (domain types, interfaces, generics instantiated to a class). Builtins and primitives (`string`, `number`, `boolean`, …) are not graph nodes — they terminate the type edge.

**Invocation:** `Operation — invokes — Operation` is a direct call from the body of one operation to another. The callee’s declaring class may be the same as the caller’s or different. CodeQL (or the language channel) resolves call targets to `Operation` nodes; unresolved dynamic calls are omitted until resolved.

**Cross-module dependencies** are derived from type and invoke edges that cross a module boundary:

```
Class — dependsOn — Class                 # when any owned Property, Parameter, or Operation
                                          # hasType / returns / invokes reaches a Class in another Module
Module — dependsOn — Class                # rollup from owned classes
Module — dependsOn — Module               # derived from external Class home modules
```

Same-module `Class — associates — Class` covers references that do not cross the module boundary. Cross-module references always go through `Class — dependsOn — Class` (never only through `associates`).

---

## DDD (specialises Module and Class)

```
BoundedContext : Module
  practice = ddd
  BoundedContext — owns — Aggregate

Aggregate : Module
  practice = ddd
  Aggregate — root — EntityRoot

Entity : Class
  practice = ddd

EntityRoot : Entity
  EntityRoot — belongsTo — Aggregate
  Repository — accesses — EntityRoot

ValueObject : Class
  practice = ddd

Repository : Class
  practice = ddd

DomainEvent : Class
  practice = ddd

DomainService : Class
  practice = ddd
```

---

## Stories (practice)

```
Epic : GraphNode
  practice = stories
  Epic — owns — Epic                     # child epics / sub-epics
  Epic — owns — Story
  Epic — scopes — Example

SubEpic : Epic

Story : GraphNode
  practice = stories
  Story — owns — Scenario
  Story — scopes — Example

Scenario : GraphNode
  practice = stories
  Scenario — owns — Background
  Scenario — owns — Step
  Scenario — scopes — Example

Background : GraphNode
  practice = stories
  Background — owns — Step
  Context — namesState — Background       # BDD standing state

Step : GraphNode                         # existing Clause; Given / When / Then
  practice = stories
  Step — invokes — Operation              # When → CE
  Step — observes — Property              # Then → CE
  Step — observes — Operation             # Then → CE
  Step — uses — Example
  Context — namesState — Step             # BDD Given / standing state

Example : GraphNode
  practice = stories
  Example — scopedBy — Epic | Story | Scenario
  Example — demonstrates — Class            # → CE
  Step — uses — Example
  Context — namesState — Example          # BDD standing state
```

---

## BDD (practice)

```
Description : GraphNode
  practice = bdd
  Description — owns — Context
  Description — describes — Class         # → CE subject under test

Context : GraphNode
  practice = bdd
  Context — owns — Observation
  Context — owns — Context                  # nested
  Context — namesState — Example            # → Stories standing state
  Context — namesState — Background         # → Stories shared Given
  Context — namesState — Step               # → Stories Given step

Observation : GraphNode
  practice = bdd
  Observation — observes — Property         # → CE (same observables as Step Then)
  Observation — observes — Operation        # → CE
```

---

## Cross-practice relationship index

Every row below is already declared on the node types above. This index groups them by join — not a separate edge vocabulary.

```
# Stories ↔ CE
Step — invokes — Operation
Step — observes — Property
Step — observes — Operation
Example — demonstrates — Class

# BDD ↔ CE
Description — describes — Class
Observation — observes — Property
Observation — observes — Operation

# BDD ↔ Stories
Context — namesState — Example
Context — namesState — Background
Context — namesState — Step
Step — uses — Example

# DDD ↔ CE (specialisation + edges on shared Class / Module nodes)
BoundedContext — owns — Aggregate
Aggregate — root — EntityRoot
EntityRoot — belongsTo — Aggregate
Repository — accesses — EntityRoot
Entity — hasIdentity — Property
Entity — hasIdentity — Operation

# CE cross-module (derived from type + invoke edges)
Class — dependsOn — Class
Module — dependsOn — Class
Module — dependsOn — Module

# reverse (materialized on every GraphNode)
GraphNode — usedBy — GraphNode
```

---

## Increment 1 Paradise slice

Stories (names from the map and `*_story.test.md`):

```
stories["onboard-a-customer"]
  epics["create-customer"]
    stories["create_unconfirmed_user_story"]
    stories["verify_account_story"]
    stories["create_customer_story"]
    stories["load_customer_story"]
    stories["create_empty_cart_story"]
  epics["get-number"]
    stories["determine_number_story"]
    stories["pick_number_story"]
    stories["enter_porting_number_story"]
    stories["verify_ported_number_story"]
```

DDD / CE (from `domain/bounded-context-map.md` and `domain/domain-model.md`):

```
modules["Customer"] : BoundedContext
  BoundedContext["Customer"] — owns — aggregates["Customer"] : Aggregate
    Aggregate["Customer"] — root — Customer : EntityRoot
      EntityRoot Customer — belongsTo — Aggregate["Customer"]
      Entity Customer — hasIdentity — id
    CustomerRepository : Repository
      Repository CustomerRepository — accesses — Customer
      Operation load — returns — Customer
      Operation load — invokes — IMavenirClient.fetchCustomer   # example cross-class invoke
    Identity
      Property id — hasType — string                          # primitive; no Class node
    Address
      Property street — hasType — string
      Property city — hasType — string
    Customer
      Property identity — hasType — Identity
      Property address — hasType — Address
  BoundedContext["Customer"] — owns — aggregates["Cart"] : Aggregate
    Aggregate["Cart"] — root — Cart : EntityRoot
    CartRepository : Repository
      Repository CartRepository — accesses — Cart
  BoundedContext["Customer"] — owns — aggregates["AccountCredentials"] : Aggregate
    Aggregate["AccountCredentials"] — root — AccountCredentials : EntityRoot
    AccountRepository : Repository
      Repository AccountRepository — accesses — AccountCredentials

modules["Inventory"] : BoundedContext
  BoundedContext["Inventory"] — owns — aggregates["Porting"] : Aggregate
    Aggregate["Porting"] — root — Portability : EntityRoot
  Module["Inventory"] — dependsOn — Customer              # cross-module rollup
    Class Portability — dependsOn — Customer              # when get-number crosses BC
```

One fully wired story — Load Customer (`load_customer_story.test.md`):

```
Story load_customer
  Story load_customer — owns — Scenario "Load My Paradise customer and store in session"
    Step When "My Paradise loads the customer from Mavenir"
      Step — invokes — CustomerRepository.load
    Step Then "the result is a Paradise customer with identity and address"
      Step — observes — Customer.identity
      Step — observes — Customer.address
    Example stored customer
      Example stored customer — demonstrates — Customer
      Example stored customer — demonstrates — AccountCredentials

Description "a Customer"
  Description "a Customer" — describes — Customer
  Description "a Customer" — owns — Context "that has been loaded"
    Context "that has been loaded" — namesState — Example stored customer
    Context "that has been loaded" — owns — Observation "should have identity and address from Mavenir"
      Observation — observes — Customer.identity
      Observation — observes — Customer.address
```

Create Customer wires the same Aggregate through `CustomerRepository.create`. Get Number wires `Portability` (and Cart when the number is stored). `CustomerRepository.usedBy` includes load and create customer stories because those Steps have `Step — invokes — CustomerRepository.load` and `Step — invokes — CustomerRepository.create`.

---

Fidelity: behavior

a Paradise practice graph
  that has been loaded from the pml-domainmodel workspace
    with only the create-customer and get-number onboard slice
      it should include the onboard-a-customer epic
      it should include create-customer as a child epic of onboard-a-customer
      it should include get-number as a child epic of onboard-a-customer
      it should include the create unconfirmed user story
      it should include the verify account story
      it should include the create customer story
      it should include the load customer story
      it should include the create empty cart story
      it should include the determine number story
      it should include the pick number story
      it should include the enter porting number story
      it should include the verify ported number story
      it should include the load-customer scenarios
      it should include the when step that loads the customer
      it should include the example that demonstrates Customer
      it should include the Customer bounded context
      it should include the Customer aggregate
      it should include Customer as the Customer aggregate root
      it should include CustomerRepository as a class in the Customer aggregate
      it should include Operation — returns — Class for domain operations
      it should include Property — hasType — Class for typed fields
      it should include Operation — invokes — Operation for resolved call edges
      it should include the Inventory bounded context
      it should include the Porting aggregate
      it should include Portability as the Porting aggregate root
      it should include Class — dependsOn — Class when stories cross bounded contexts
      it should include the load customer story among the usedBy of CustomerRepository
      it should include the create customer story among the usedBy of CustomerRepository
      it should include a description of Customer
      it should include an observation that Customer has been loaded
