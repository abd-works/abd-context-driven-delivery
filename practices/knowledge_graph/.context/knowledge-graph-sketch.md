# knowledge_graph sketch — increment 1 (Create Customer + Get Number)

One file: object model + BDD. Extends existing practice nodes. CodeQL populate is a later increment behind the same `load`.

The graph is one object model. Practices are **stereotypes and extra edges** on that model, not four parallel trees.

```
practices/knowledge_graph/
  graph -> stories, clean_engineering, ddd, bdd
```

---

## Across practices (the graph)

Clean Engineering is the base. DDD specialises Module and Class. Stories and BDD hang off Class, Operation, Property, and Example.

```
Knowledge
  load path
    -> StoryMap
    -> CleanEngineeringModel
  stories                           <-- keyed Epics
  modules                           <-- keyed Modules (includes BoundedContext and Aggregate)
  descriptions                      <-- keyed BDD Descriptions

# --- Clean Engineering (base) ---
 Module
      classes
      // never repository — that is a Class inside an Aggregate
 Class
      properties
      operations
      usedBy
 Property
 Operation
      // usedBy is the reverse of every edge below

# --- DDD specialises Module and Class ---
 BoundedContext : Module
      aggregates                    <-- Aggregate modules in this language
      // one meaning per term inside this context
 Aggregate : Module
      root                          <-- EntityRoot; must be present
      // Repository, when it exists, is a Class in this module — not a field on Module
      // must have a known root Entity
 Entity : Class
      // identity outlives attributes
 EntityRoot : Entity
      identity                      <-- identification operation or property; must be present
      // associated with exactly one Aggregate; that Aggregate’s only entry
 ValueObject : Class
 Repository : Class
      // collection lifecycle of the Aggregate’s root only
      // lives in the same Aggregate as the root
 DomainEvent : Class
 DomainService : Class

# --- Stories ---
 Epic
      epics                         <-- child Epics / SubEpics
      stories
      examples                      <-- Example scope = Epic
 SubEpic : Epic
 Story
      scenarios
      examples                      <-- Example scope = Story
 Scenario
      background                    <-- shared Given Steps (existing Scenario.background)
      steps                         <-- Given / When / Then (existing Clause)
      examples                      <-- Example scope = Scenario (existing example_rows)
 Background
      steps
 Step                               <-- existing Clause
      // When invokes Operation; Then observes Property or Operation result
 Example
      // expresses a Class (usually an Entity or Value Object)

# --- BDD ---
 Description
      // describe {subject} — the subject is a Class (or its observable state)
      contexts
 Context
      // that {event} / with {condition} — standing state; same job as Given / Background
      observations
      contexts
 Observation
      // it should {outcome} — one observable; same Operation or Property a Step uses
```

### Edges that join the practices

Write these as real calls / associations — this is the product.

```
BoundedContext
  contains Aggregate

Aggregate
  root EntityRoot
  // Repository class in the same Aggregate, when the root has a collection lifecycle
  -> Repository manages EntityRoot

EntityRoot
  associated with Aggregate
  // must identify itself

Step
  -> Operation.invoke                 <-- When
  -> Property.observe                 <-- Then
  -> Example.use

Example
  -> Class.express                    <-- Customer, AccountCredentials, Portability, …
  // scope is Scenario, Story, or Epic

Description
  -> Class.describe                   <-- same Class the Example expresses

Context
  -> Example / Given state            <-- same prior state a Background or Given Step names

Observation
  -> Operation.observe
  -> Property.observe
  // same Operation a Story Step invokes — acceptance vs unit of one behaviour

UsedBy                                <-- reverse of every edge above
  stories
  scenarios
  steps
  descriptions
  observations
```

So `CustomerRepository.usedBy.stories` is not a field we invented on Module. It is the reverse of `Step -> CustomerRepository.load`.

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
      identity id
    CustomerRepository : Repository
      // Class in this Aggregate; manages Customer
    Identity
    Address
  aggregates["Cart"] : Aggregate
    root Cart : EntityRoot
    CartRepository : Repository
  aggregates["AccountCredentials"] : Aggregate          <-- Authentication · Account
    root AccountCredentials : EntityRoot
    AccountRepository : Repository

modules["Inventory"] : BoundedContext
  aggregates["Porting"] : Aggregate
    root Portability : EntityRoot
```

One fully wired story — Load Customer (`load_customer_story.test.md`):

```
Story load_customer
  Scenario "Load My Paradise customer and store in session"
    Step When "My Paradise loads the customer from Mavenir"
      -> CustomerRepository.load
    Step Then "the result is a Paradise customer with identity and address"
      -> Customer.identity
      -> Customer.address
    Example stored customer
      -> Customer.express
      -> AccountCredentials.express

Description "a Customer"
  Context "that has been loaded"
    Observation "should have identity and address from Mavenir"
      -> Customer.identity
      -> Customer.address
```

Create Customer wires the same Aggregate through `CustomerRepository.create`. Get Number wires `Portability` (and Cart when the number is stored). `CustomerRepository.usedBy.stories` therefore includes `load_customer_story` and `create_customer_story` because those Stories’ When steps invoke its operations.

---

Fidelity: behavior

a Paradise knowledge graph
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
      it should include the load customer story among the stories that use CustomerRepository
      it should include the create customer story among the stories that use CustomerRepository
      it should include a description of Customer
      it should include an observation that Customer has been loaded
