# knowledge_graph sketch — increment 1 (Create Customer + Get Number)

One file: object model + BDD. Extends existing practice nodes. CodeQL populate is a later increment behind the same `load`.

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

Property : GraphNode
  practice = clean_engineering
  Property — belongsTo — Class
  Property — hasType — Class              # field, getter, or observable state type

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
  Aggregate — hasRoot — EntityRoot

Entity : Class
  practice = ddd
  Entity — hasIdentity — Property | Operation   # identification field or operation

EntityRoot : Entity
  EntityRoot — belongsTo — Aggregate

ValueObject : Class
  practice = ddd

Repository : Class
  practice = ddd
  Repository — manages — EntityRoot

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

Step : GraphNode                         # existing Clause; Given / When / Then
  practice = stories

Example : GraphNode
  practice = stories
  Example — scopedBy — Epic | Story | Scenario
```

---

## BDD (practice)

```
Description : GraphNode
  practice = bdd
  Description — owns — Context

Context : GraphNode
  practice = bdd
  Context — owns — Observation
  Context — owns — Context               # nested

Observation : GraphNode
  practice = bdd
```

---

## Cross-practice graph relationships

All cross-practice joins are `GraphRelationship` rows with explicit left and right.

```
# --- Stories → CE ---
Step — invokes — Operation               # When
Step — observes — Property               # Then
Step — observes — Operation              # Then
Step — uses — Example

Example — expresses — Class

# --- BDD → CE / Stories ---
Description — describes — Class

Context — namesState — Example
Context — namesState — Background
Context — namesState — Step              # Given / standing state

Observation — observes — Property
Observation — observes — Operation       # same observables a Step uses

# --- reverse (materialized on GraphNode) ---
GraphNode — usedBy — GraphNode           # to.usedBy includes from for every row above
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
    Aggregate["Customer"] — hasRoot — Customer : EntityRoot
      EntityRoot Customer — belongsTo — Aggregate["Customer"]
      Entity Customer — hasIdentity — id
    CustomerRepository : Repository
      Repository CustomerRepository — manages — Customer
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
    Aggregate["Cart"] — hasRoot — Cart : EntityRoot
    CartRepository : Repository
      Repository CartRepository — manages — Cart
  BoundedContext["Customer"] — owns — aggregates["AccountCredentials"] : Aggregate
    Aggregate["AccountCredentials"] — hasRoot — AccountCredentials : EntityRoot
    AccountRepository : Repository
      Repository AccountRepository — manages — AccountCredentials

modules["Inventory"] : BoundedContext
  BoundedContext["Inventory"] — owns — aggregates["Porting"] : Aggregate
    Aggregate["Porting"] — hasRoot — Portability : EntityRoot
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
      Example stored customer — expresses — Customer
      Example stored customer — expresses — AccountCredentials

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
      it should include the example that expresses Customer
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
