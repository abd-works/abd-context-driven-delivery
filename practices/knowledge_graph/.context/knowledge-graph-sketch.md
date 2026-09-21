# knowledge_graph sketch — increment 1 (Create Customer + Get Number)

One file: object model + BDD. Extends existing practice nodes. CodeQL populate is a later increment behind the same `load`.

This is a **practice graph** — one navigable object model. Each node is **both**:

- a **graph node** (participates in the unified practice graph with cross-practice edges), and
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
    -> StoryMap
    -> CleanEngineeringModel
  stories                           # keyed Epic roots (Stories practice view)
  modules                           # keyed Module roots (CE / DDD practice view)
  descriptions                      # keyed Description roots (BDD practice view)
  nodes                             # all GraphNodes keyed by stable id (optional flat index)
```

Every typed node below **is a GraphNode** unless noted.

---

## GraphNode (common)

Every node in the practice graph carries graph membership and cross-practice edges.

```
GraphNode
  graph                             # back-ref to owning PracticeGraph
  practice                          # clean_engineering | ddd | stories | bdd
  usedBy                            # reverse of every cross-practice edge below
```

`usedBy` is not a separate invention per type — it is the reverse index of graph edges (`CustomerRepository.usedBy.stories` because a Step invokes `CustomerRepository.load`).

---

## Clean Engineering (base practice)

```
Module : GraphNode
  practice = clean_engineering
  classes                           # classes owned in this module
  externalClasses                   # all Class nodes used from other modules (deduped rollup)
  dependencies                      # derived: home Module of each externalClass (module names)

Class : GraphNode
  practice = clean_engineering
  module                            # home module
  properties
  operations
  relationships                     # same-module class associations
  externalClasses                   # classes in another module this class depends on
  usedBy

Property
Operation
  usedBy
```

**Cross-module rule:** a class dependency whose home module ≠ this class’s module goes on `Class.externalClasses`. Same-module refs stay on `relationships`. `Module.externalClasses` is the union of `externalClasses` from all classes in the module. CodeQL resolves imports, types, params, returns, fields, and collaborators to Class nodes, then applies the filter.

---

## DDD (specialises Module and Class)

```
BoundedContext : Module
  practice = ddd
  aggregates                        # Aggregate modules in this language

Aggregate : Module
  practice = ddd
  root                              # EntityRoot; required
  # Repository, when it exists, is a Class in this module — not a field on Module

Entity : Class
  practice = ddd
  identity                          # any Entity has identity

EntityRoot : Entity
  aggregate                         # the one Aggregate this root belongs to; only difference from Entity

ValueObject : Class
  practice = ddd

Repository : Class
  practice = ddd
  manages                           # EntityRoot this repository’s collection lifecycle serves

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
  epics                             # child Epics / SubEpics
  stories
  examples                          # Example scope = Epic

SubEpic : Epic

Story : GraphNode
  practice = stories
  scenarios
  examples                          # Example scope = Story

Scenario : GraphNode
  practice = stories
  background
  steps
  examples                          # Example scope = Scenario

Background : GraphNode
  practice = stories
  steps

Step : GraphNode                    # existing Clause; Given / When / Then
  practice = stories
  invokes                           # Operation (When)
  observes                          # Property and/or Operation (Then)
  uses                              # Example

Example : GraphNode
  practice = stories
  expresses                         # Class (usually Entity or Value Object)
  scope                             # Epic | Story | Scenario
```

---

## BDD (practice)

```
Description : GraphNode
  practice = bdd
  describes                         # Class (subject)
  contexts

Context : GraphNode
  practice = bdd
  state                             # Example / Given state (same prior state as Background)
  observations
  contexts                          # nested

Observation : GraphNode
  practice = bdd
  observes                          # Operation and/or Property (same as a Step’s Then)
```

---

## Cross-practice graph edges

These are **first-class fields** on graph nodes — the product, not commentary.

```
# --- DDD within CE ---
BoundedContext
  contains → Aggregate

Aggregate
  root → EntityRoot

EntityRoot
  aggregate → Aggregate

Repository
  manages → EntityRoot

Class
  externalClasses → Class              # target Class in another Module only

Module
  externalClasses → Class              # rollup from owned classes

# --- Stories → CE ---
Step
  invokes → Operation                    # When
  observes → Property | Operation      # Then
  uses → Example

Example
  expresses → Class

# --- BDD → CE / Stories ---
Description
  describes → Class

Context
  state → Example | Background | Step  # Given / standing state

Observation
  observes → Property | Operation      # same observables a Step uses

# --- reverse index (on GraphNode) ---
GraphNode
  usedBy → GraphNode[]                 # stories, scenarios, steps, descriptions, observations, …
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
  aggregates["Customer"] : Aggregate
    root Customer : EntityRoot
      aggregate → aggregates["Customer"]
      identity id
    CustomerRepository : Repository
      manages → Customer
    Identity
    Address
  aggregates["Cart"] : Aggregate
    root Cart : EntityRoot
    CartRepository : Repository
  aggregates["AccountCredentials"] : Aggregate
    root AccountCredentials : EntityRoot
    AccountRepository : Repository

modules["Inventory"] : BoundedContext
  aggregates["Porting"] : Aggregate
    root Portability : EntityRoot
  externalClasses: Customer             # when get-number crosses BC into Customer types
```

One fully wired story — Load Customer (`load_customer_story.test.md`):

```
Story load_customer
  Scenario "Load My Paradise customer and store in session"
    Step When "My Paradise loads the customer from Mavenir"
      invokes → CustomerRepository.load
    Step Then "the result is a Paradise customer with identity and address"
      observes → Customer.identity
      observes → Customer.address
    Example stored customer
      expresses → Customer
      expresses → AccountCredentials

Description "a Customer"
  describes → Customer
  Context "that has been loaded"
    state → Example stored customer
    Observation "should have identity and address from Mavenir"
      observes → Customer.identity
      observes → Customer.address
```

Create Customer wires the same Aggregate through `CustomerRepository.create`. Get Number wires `Portability` (and Cart when the number is stored). `CustomerRepository.usedBy` therefore includes the load and create customer stories because those Steps invoke its operations.

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
      it should include the Inventory bounded context
      it should include the Porting aggregate
      it should include Portability as the Porting aggregate root
      it should include cross-module externalClasses when stories cross bounded contexts
      it should include the load customer story among the usedBy of CustomerRepository
      it should include the create customer story among the usedBy of CustomerRepository
      it should include a description of Customer
      it should include an observation that Customer has been loaded
