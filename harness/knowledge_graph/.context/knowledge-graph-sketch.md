# Knowledge graph

One practice graph. Each node is the practice type with `Node` mixed in, so an epic, a class, a step, and an operation stay the types the practice already uses. The node builds itself and the children it owns. `PracticeGraph` is the registry those nodes join: identity, the relationship index, filter, and rule hits. It does not assemble the tree.

CodeQL and TypeScript are channels of that same model. A channel only changes how the next child is read. CodeQL reads fact rows. TypeScript reads the JSON the CodeQL channel saved. The child walk is the one in `practices/stories/model/.context/practice-strategy.md`.

```
practices/{practice}/model/codeql/     CodeQL channel — the graph types
harness/knowledge_graph/               PracticeGraph, Node, Relationship, rules
harness/knowledge_graph/app/.../       TypeScript channel — same type names, JSON cursor
```

Callers load a root and receive that root. `StoryModel.load` and `CleanEngineeringModel.load` return the channel root. There is no loader beside the root that walks a finished tree to register it, and there is no second `GraphEpic` hierarchy beside the CodeQL types.

---

## Who builds the tree

`load` stores the path. The channel prepares its cursor in `load_content`. The owner of a collection then runs `while has_more_child: append load_next_child()`. `load_next` takes the shell with `get_next_*_from_file()` in that node's `*_type`, then calls the child's load. The child joins the graph in that append, and the parent records `owns` (or `scopes` for an example) on the index.

A copy constructor does the same work from a source tree. `Epic(source)` copies its own fields. Each source child is built with `epic_type` or `story_type`, so the new tree is this channel's types. Depth is parentage. A nested epic is an `Epic` whose parent is an epic.

```
StoryModel
  load(path)
    load_content()                         # channel cursor: file, or CodeQL rows, or JSON
    load_epics()                           # while has_more_epic: append load_next_epic()
  epic_type, story_type, scenario_type, step_type, example_type

Epic
  load_epics()                             # nested epics, same Epic type
  load_stories()
  load_examples()

Story
  load_scenarios()
  load_backgrounds()
  load_examples()

Scenario
  load_background()
  load_steps()
  load_examples()

CleanEngineeringModel
  load_modules()

Module
  load_classes()

OoadClass
  load_properties()
  load_operations()

Operation
  load_parameters()
  load_invokes()                           # each resolved call is this operation's child link

Example
  load_demonstrates()                      # classes this example shows

Step
  load_invokes()
  load_observes()
  load_loads()
```

The root does not append another node's children. `StoryModel` does not create scenarios. `CleanEngineeringModel` does not create operations. Fact rows and JSON objects are the cursor `get_next_*_from_file` reads. Matching a call to an operation, or an example name to a class, happens inside the node that owns that link.

`CodeQL.populate` runs the queries and passes the row lists into the root's `load_content`. Register and relate happen when a parent appends a child. Populate does not walk the rows into nodes itself.

---

## Channels

**CodeQL** (`practices/{practice}/model/codeql`). The cursor is the fact rows for classes, operations, properties, parameters, calls, stories, scenarios, steps, and examples. `has_more_*` and `get_next_*_from_file` are the only reads this channel adds. `load_content` on the clean-engineering root stores class and member rows. `load_content` on the story root stores story rows. A step's `get_next` for `invokes` reads the call rows that name that step.

**Copy from a practice model already loaded.** Markdown, Draw.io, and the code languages load through their own channels. The graph channel copies that tree with the copy constructor. The copy reads a node that is already on a link. It does not look the name up again.

**TypeScript** (`harness/knowledge_graph/app`). The cursor is the JSON document the CodeQL channel saved (`practice-graph.json` and the knowledge-graph document). `Epic`, `Story`, `Scenario`, `Step`, `Example`, `Module`, `OoadClass`, `Operation`, and the DDD and BDD types are classes. Each parent reads its children out of that JSON and constructs them. The explorer asks `children` and the relationship fields. A background's label is `Background.label` (its first Given step). A class's source range is the class's `source`.

The TypeScript channel does not parse source files, emit package nodes the model never built, or rank semantic types to decide parentage. Rule text and hits arrive on `node.rules` from `evaluate_rules`.

A channel stops where its path stops. The TypeScript document contains only the nodes the Python channel saved.

---

## PracticeGraph (registry)

```
PracticeGraph
  root: Path
  story_map: StoryModel
  ce_model: CleanEngineeringModel
  nodes                              # keyed by node_id
  relationships                      # Relationship(from, kind, to) — the index
  register(node)                     # node.join
  relate(edge)                       # one edge, incoming index for the inverse
  filter(filter)                     # practice, connector kind, node type, violations, rule
  evaluate_rules()                   # fills node.rules
```

`KnowledgeGraph` is the aggregate. It reloads the working copy and holds the practice graphs. Filter and follow-relationship run on this registry. Follow-relationship selects the node on the other end of a typed field.

`relationships` is the index of the typed fields below, kept so a filter can select by kind without a branch per field. Setting the field writes the inverse and one `Relationship`. Reading `used_by` reads the incoming index.

```
Relationship
  from: Node
  kind: Kind
  to: Node
```

`Kind` names the field: `owns`, `scopes`, `demonstrates`, `invokes`, `observes`, `hasType`, `returns`, `dependsOn`, and the rest listed on the types below.

---

## Node

```
Node                                 # mixed into the practice types
  graph: PracticeGraph
  node_id
  practice                           # clean_engineering | ddd | stories | bdd
  source                             # file, start line, end line
  rules: NodeRules
  children(): list[Node]             # the collection this node owns, in order
  relate(kind, to)                   # sets the typed field, the inverse, and the index
  related(kind): list[Node]
  used_by: list[Node]                # incoming index
```

The explorer's tree is `children()`. The explorer's connectors are `related(kind)`.

---

## Typed relationships

Each link is a field on the type that owns it and a field on the type at the other end. The field's element type is the practice type. `relate` keeps the two fields and the index on the same write.

Cross-practice fields live on the CodeQL channel types, which already see both practices. The markdown story types do not gain a class field. The markdown class types do not gain a step field.

### Clean Engineering

```
Module
  practice = clean_engineering
  classes: list[OoadClass]                  # inverse OoadClass.module
  depends_on: list[Module]                  # inverse depended_on_by
                                            # rollup when an owned type or invoke
                                            # reaches a class in another module

OoadClass
  module: Module
  properties: list[Property]
  operations: list[Operation]
  associates: list[OoadClass]               # same-module reference
  depends_on: list[OoadClass]               # other-module reference
  demonstrated_by: list[Example]            # inverse Example.demonstrates
  described_by: list[Description]           # inverse Description.describes

Property
  owner: OoadClass
  has_type: OoadClass | None                # absent for string, number, boolean
  observed_by: list[Step | Observation]

Parameter
  operation: Operation
  has_type: OoadClass | None

Operation
  owner: OoadClass
  parameters: list[Parameter]
  returns: OoadClass | None
  invokes: list[Operation]                  # inverse invoked_by
  invoked_by: list[Operation]
  invoked_by_steps: list[Step]              # inverse Step.invokes
  observed_by: list[Step | Observation]
```

`has_type` and `returns` resolve to an `OoadClass`. A primitive terminates the field. `invokes` is a direct call. The operation loads each resolved callee. An unresolved dynamic call stays empty until it resolves.

`depends_on` is set when a property, parameter, return, or invoke reaches a class whose module is different. Same-module references use `associates`.

### DDD

DDD specialises `Module` and `OoadClass`. The graph channel uses these types when the stereotype is known. A bounded context loads aggregates. An aggregate loads its root and its classes.

```
BoundedContext : Module
  practice = ddd
  aggregates: list[Aggregate]

Aggregate : Module
  practice = ddd
  root: EntityRoot                          # inverse EntityRoot.aggregate

Entity : OoadClass
EntityRoot : Entity
  aggregate: Aggregate
  identity: list[Property | Operation]

ValueObject : OoadClass
Repository : OoadClass
  accesses: EntityRoot                      # inverse EntityRoot.repository
DomainEvent : OoadClass
DomainService : OoadClass
```

### Stories

```
StoryModel
  practice = stories
  epics: list[Epic]

Epic
  practice = stories
  parent: StoryModel | Epic
  epics: list[Epic]                         # nested; same Epic type
  stories: list[Story]
  examples: list[Example]

Story
  scenarios: list[Scenario]
  backgrounds: list[Background]
  examples: list[Example]

Scenario
  backgrounds: list[Background]
  steps: list[Step]
  examples: list[Example]

Background
  steps: list[Step]
  label(): str                              # the first Given step's title

Step
  keyword                                   # Given | When | Then | And | But
  phase                                     # given | when | then
  invokes: list[Operation]                  # When
  observes: list[Property | Operation]      # Then
  loads: list[Example]

Example
  scope: Epic | Story | Scenario | Background
  demonstrates: list[OoadClass]
  retrieved_using: Operation | Property | None
```

`scopes` on the index is `examples` on the scope node. An example loads `demonstrates` from the class rows that name it. A when-step loads `invokes`. A then-step loads `observes`.

### BDD

```
Description
  practice = bdd
  contexts: list[Context]
  describes: OoadClass                      # inverse OoadClass.described_by

Context
  observations: list[Observation]
  contexts: list[Context]
  names_state: list[Example | Background | Step]

Observation
  observes: list[Property | Operation]
```

---

## Cross-practice index

The filter uses these kinds. Each kind is one of the fields above.

```
Step — invokes — Operation
Step — observes — Property
Step — observes — Operation
Step — loads — Example
Example — demonstrates — OoadClass
Example — retrievedUsing — Operation | Property
Epic — uses — Module

Description — describes — OoadClass
Observation — observes — Property | Operation
Context — namesState — Example | Background | Step

Repository — accesses — EntityRoot
Entity — hasIdentity — Property | Operation
Aggregate — root — EntityRoot

OoadClass — dependsOn — OoadClass
Module — dependsOn — Module

Node — usedBy — Node                        # incoming index of every field
```

---

## Guidance rules

Rules attach to nodes already in the graph. Fidelity narrows which types are in scope. A rule reads the typed fields. `evaluate_rules` writes `node.rules`. The explorer lists those hits. It does not scan a file to decide a hit.

| Practice | Fidelity | Types in scope | Fields a rule may read |
|----------|----------|----------------|------------------------|
| Stories | `story_map` | Epic, Story | `epics`, `stories` |
| Stories | `scenarios` | Scenario, Background, Step, Example | `steps`, `examples` |
| Stories | `acceptance_tests` | Step, Example | `invokes`, `observes`, `demonstrates` |
| Clean Engineering | `modules` | Module | `depends_on` |
| Clean Engineering | `model` | Module, OoadClass, Property, Operation | `associates`, `has_type`, `returns` |
| Clean Engineering | `code` | OoadClass, Property, Operation | `invokes` |
| DDD | `bounded_context` | BoundedContext, Aggregate | `aggregates` |
| DDD | `building_blocks` | Entity, EntityRoot, Repository, ValueObject | `accesses`, `root` |
| BDD | `behavior` | Description, Context, Observation | `describes`, `observes` |

```
NodeRules
  violations
  direct.violations
  practice(name).shared.violations
  practice(name).fidelity(name).violations
```

```python
scenario.rules.direct.violations
step.rules.practice("stories").fidelity("acceptance_tests").violations
```

A rule is a query over the fields, evaluated through CodeQL where the fact is a call or a mutation:

```
Scenario scenario
where not exists(Example e | e.scope = scenario)
select scenario, "Scenario has no examples."

Step step
where step.phase = "when" and not exists(Operation op | op in step.invokes)
select step, "When step does not invoke a domain operation."

Example example
where not exists(OoadClass c | c in example.demonstrates)
select example, "Example is not linked to a domain class."
```

```
RuleViolation
  rule_slug
  node
  message
  practice
  fidelity
  source
```

Which operation a cloned hit belongs to is decided by that operation when the hit is attached.

---

## Increment 1 Paradise slice

Stories:

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

DDD / Clean Engineering:

```
BoundedContext["Customer"]
  Aggregate["Customer"]
    root: Customer : EntityRoot
    CustomerRepository : Repository
      accesses: Customer
      load.returns: Customer
      load.invokes: the Mavenir fetch
  Aggregate["Cart"]
    root: Cart : EntityRoot
    CartRepository.accesses: Cart
  Aggregate["AccountCredentials"]
    root: AccountCredentials : EntityRoot
    AccountRepository.accesses: AccountCredentials

BoundedContext["Inventory"]
  Aggregate["Porting"]
    root: Portability : EntityRoot
  depends_on: Customer                         # when get-number crosses the context
```

Load Customer, built by the story and the example, not by a walker:

```
Story load_customer
  scenarios["Load My Paradise customer and store in session"]
    Step When "My Paradise loads the customer from Mavenir"
      invokes: CustomerRepository.load
    Step Then "the result is a Paradise customer with identity and address"
      observes: Customer.identity, Customer.address
    Example stored customer
      demonstrates: Customer, AccountCredentials

Description "a Customer"
  describes: Customer
  Context "that has been loaded"
    names_state: Example stored customer
    Observation "should have identity and address from Mavenir"
      observes: Customer.identity, Customer.address
```

`CustomerRepository.used_by` includes the load and create steps because those steps set `invokes`.

---

## Behaviors

Fidelity: behavior

```
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
      it should include Operation.returns for domain operations
      it should include Property.has_type for typed fields
      it should include Operation.invokes for resolved calls
      it should include the Inventory bounded context
      it should include the Porting aggregate
      it should include Portability as the Porting aggregate root
      it should include OoadClass.depends_on when stories cross bounded contexts
      it should include the load customer story among the used_by of CustomerRepository
      it should include the create customer story among the used_by of CustomerRepository
      it should include a description of Customer
      it should include an observation that Customer has been loaded

a Story loaded from CodeQL rows
  that has scenario rows for that story
    the story's load_scenarios builds each scenario
    the scenario's load_steps builds each step
    the story model does not append those scenarios itself

an Example loaded from CodeQL rows
  that names Customer
    the example's load_demonstrates sets demonstrates to that class
    the class's demonstrated_by includes that example

a TypeScript knowledge graph
  that has been loaded from the saved practice-graph JSON
    each epic's children are the stories and nested epics in that JSON
    a class's children are its properties and operations
    a background's label is its first Given step
    the tree follows children()
    the channel does not parse the workspace source
```

Fidelity: rules

```
a Scenario under load_customer_story
  that has been loaded and evaluated
    scenario.rules.direct.violations should include no missing-example violation when it scopes an Example
    scenario.rules.direct.violations should include a missing-example violation when it scopes no Example

a When Step under load_customer_story
  that has been loaded with CodeQL and evaluated
    step.rules.practice("stories").fidelity("acceptance_tests").violations
      should be empty when step.invokes includes CustomerRepository.load
      should include step-invokes-domain-operation when invokes is empty

a CustomerRepository class
  that has been loaded with CodeQL and evaluated at building_blocks fidelity
    repository.rules.direct.violations should flag operations that mutate aggregate state
      when they are not collection-lifecycle operations
```
