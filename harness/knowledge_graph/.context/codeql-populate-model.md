# CodeQLKnowledgeGraph

CodeQL walks fact rows onto a `CodeQLKnowledgeGraph`. The CodeQL types are type-safe constructors for those nodes. They do not stitch. `populate` fills `practice.nodes` and `practice.edges`. `buildGraph` walks from each practice root.

A node query names a `semantic_type`. That type is a CodeQL class. An edge query names a `kind`, `order`, and `display`. Both catalogs grow as the queries run.

`order` and `display` are literals in the edge query. display = direct | grouped | relationship.

Loaders: `practices/{practice}/model/{language}/codeql/loaders/{name}.ql`.

`node_id` = `{practice}:{semantic_type}:{file}:{name}` (add class or operation when the name is not unique).

---

## CodeQLKnowledgeGraph

+ CodeQLPracticeGraph: dict
	// practice name → CodeQLPracticeGraph
----
+ populate(path, practices): CodeQLKnowledgeGraph
	// for each practice: run node queries, then edge queries, then buildGraph
+ buildGraph(): None
	// for each practice: root = practice.rootNode; root.populate()

## CodeQLPracticeGraph

+ name: str
+ nodes: dict
	// by node type → list[Node]. filled from node queries
+ edges: dict
	// by edge type → list[Edge]. filled from edge queries. node ↔ node
+ node_types: set of all node types
	// semantic_type as queries run
+ edge_types: set of all edge types
	// EdgeType as queries run, keyed by order
+ rootNode: Node
----
- load_nodes(queries): None
	// for query in node_queries
	//   node_types.add(query.semantic_type)
	//   nodes[query.semantic_type].append(CodeQLType[semantic_type].from_fact(row))
- load_edges(queries): None
	// for query in edge_queries
	//   edge_types.add(EdgeType(kind, order, display))
	//   edges[kind].append(Edge(parent, child, kind, order, display))

## EdgeType

Taken from an edge query as rows arrive.

+ kind: str
+ order: int
+ display: str
	// direct | grouped | relationship

## Edge

+ kind: str
+ order: int
+ display: str
+ parent: Node
+ child: Node

## Source

+ path: str
+ line_start: int
	// from the node query
+ line_end: int
	// from the node query
+ call_folds: list[CallFold]
	// nested call markers inside contents. nesting_level is fold depth
----
+ contents: str
	// get: read path, slice line_start..line_end, insert call fold markers by nesting_level

## CallFold

+ line: int
	// line in the source slice
+ nesting_level: int
	// 0 is the outer call. inner calls increment
+ callee: str

## Node

The type-safe CodeQL class for this semantic_type. Lives in `practice.nodes[type]`.

+ practice: Practice
+ type: str
	// semantic_type
+ node_id: str
+ name: str
+ source: Source
+ children: list[Node]
----
+ from_fact(row): Node
	// this type. source from file, line, end_line
+ populate(parent=None): None
	// if parent: parent.children.add(this)
	// for edge_type in practice.edge_types sorted by order
	//   for edge in practice.edges[edge_type.kind] where edge.parent is this
	//     display=grouped:
	//       group = existing child named edge.kind, or a new group Node
	//       children.add(group)
	//       edge.child.populate(group)
	//     display=direct:
	//       edge.child.populate(this)
	//     display=relationship:
	//       rel = existing child named edge.kind, or a new relationship Node
	//       children.add(rel)
	//       edge.child.populate(rel)

## Node fact

Every node query `select`s this, then practice columns.

```
node_id, name, semantic_type, practice, file, line, end_line
```

## GraphEdge fact

Every edge query `select`s this. `kind`, `order`, and `display` are hardcoded in that query.

```
parent_id, child_id, kind, order, display
```

---

# Clean Engineering

Practice: `clean_engineering`. A class is an OoadClass. DDD stereotypes are the DDD queries.


## Node queries

**modules.ql**
```
node_id, name, semantic_type=Module, practice=clean_engineering, file, line, end_line
```

**classes.ql**
```
node_id, name, semantic_type=OoadClass, practice=clean_engineering, file, line, end_line,
module
```

**operations.ql**
```
node_id, name, semantic_type=Operation, practice=clean_engineering, file, line, end_line,
class_name, return_type
```

**properties.ql**
```
node_id, name, semantic_type=Property, practice=clean_engineering, file, line, end_line,
class_name, type_hint, stereotype, cardinality, origin
```

**parameters.ql**
```
node_id, name, semantic_type=Parameter, practice=clean_engineering, file, line, end_line,
class_name, operation
```

## Edge queries

**relative.ql**
```
parent_id, child_id, kind=relative, order=1, display=direct
```
OoadClass→Property when type_hint names another loaded class.

**owns.ql**
```
parent_id, child_id, kind=owns, order=2, display=direct
```
Module→Module, Module→OoadClass, OoadClass→Operation, Operation→Parameter.

**grouped-properties.ql**
```
parent_id, child_id, kind=properties, order=3, display=grouped
```
OoadClass→leftover Property. Heading = properties.

**belongs-to.ql**
```
parent_id, child_id, kind=belongsTo, order=4, display=relationship
```

**has-parameter.ql**
```
parent_id, child_id, kind=hasParameter, order=5, display=relationship
```
Operation→Parameter.

**has-type.ql**
```
parent_id, child_id, kind=hasType, order=6, display=relationship
```
Property→OoadClass named by type_hint.

**returns.ql**
```
parent_id, child_id, kind=returns, order=7, display=relationship
```
Operation→OoadClass named by return_type.

**invokes.ql**
```
parent_id, child_id, kind=invokes, order=8, display=relationship
```
Operation→Operation.

**depends-on.ql**
```
parent_id, child_id, kind=dependsOn, order=9, display=relationship
```
OoadClass→OoadClass, Module→Module, when an invokes row leaves the owner.

**associates.ql**
```
parent_id, child_id, kind=associates, order=10, display=relationship
```
OoadClass→OoadClass.

**composition.ql**
```
parent_id, child_id, kind=composition, order=11, display=relationship
```
OoadClass→OoadClass.

**aggregation.ql**
```
parent_id, child_id, kind=aggregation, order=12, display=relationship
```
OoadClass→OoadClass.

---

# Stories

Practice: `stories`. Story edges may name a Clean Engineering node_id already registered.

## CodeQLStoryModel : StoryModel, CodeQLNode

## CodeQLEpic : Epic, CodeQLNode

## CodeQLStory : Story, CodeQLNode

## CodeQLBackground : Background, CodeQLNode

## CodeQLScenario : Scenario, CodeQLNode

## CodeQLStep : Step, CodeQLNode

## CodeQLExample : Example, CodeQLNode

## Node queries

**epics.ql**
```
node_id, name, semantic_type=Epic, practice=stories, file, line, end_line
```

**stories.ql**
```
node_id, name, semantic_type=Story, practice=stories, file, line, end_line,
epic
```

**scenarios.ql**
```
node_id, name, semantic_type=Scenario, practice=stories, file, line, end_line,
story
```

**backgrounds.ql**
```
node_id, name, semantic_type=Background, practice=stories, file, line, end_line,
story, scenario
```

**steps.ql**
```
node_id, name, semantic_type=Step, practice=stories, file, line, end_line,
keyword, story, scenario, background
```
keyword = given | when | then | and | but.

**examples.ql**
```
node_id, name, semantic_type=Example, practice=stories, file, line, end_line,
class_name
```
class_name = domain class the factory constructs, or empty.

## Edge queries

**owns.ql**
```
parent_id, child_id, kind=owns, order=1, display=direct
```
Epic→Story, Story→Scenario, Story→Background, Scenario→Step.

**scopes.ql**
```
parent_id, child_id, kind=scopes, order=2, display=grouped
```
Background→Example, Step→Example. Heading = examples.

**demonstrates.ql**
```
parent_id, child_id, kind=demonstrates, order=3, display=grouped
```
Example→OoadClass. Heading = examples on the class.

**belongs-to.ql**
```
parent_id, child_id, kind=belongsTo, order=4, display=relationship
```

**invokes.ql**
```
parent_id, child_id, kind=invokes, order=5, display=relationship
```
Step→Operation | Property on a when.

**demonstrated-through.ql**
```
parent_id, child_id, kind=demonstratedThrough, order=6, display=relationship
```
OoadClass→Example.

**retrieved-using.ql**
```
parent_id, child_id, kind=retrievedUsing, order=7, display=relationship
```
Example→Operation | Property.

**observes.ql**
```
parent_id, child_id, kind=observes, order=8, display=relationship
```
then Step→Example.

**uses.ql**
```
parent_id, child_id, kind=uses, order=9, display=relationship
```
Epic→Module.

---

# DDD

Practice: `ddd`. Clean Engineering already registered the class as OoadClass. A DDD node fact is the stereotyped type for the same source span. `class_node_id` is that OoadClass. Load does not promote.


## Node queries

**bounded-contexts.ql**
```
node_id, name, semantic_type=BoundedContext, practice=ddd, file, line, end_line
```

**aggregates.ql**
```
node_id, name, semantic_type=Aggregate, practice=ddd, file, line, end_line,
context
```

**entities.ql**
```
node_id, name, semantic_type=Entity, practice=ddd, file, line, end_line,
class_node_id, is_root=false
```

**entity-roots.ql**
```
node_id, name, semantic_type=EntityRoot, practice=ddd, file, line, end_line,
class_node_id, is_root=true
```

**value-objects.ql**
```
node_id, name, semantic_type=ValueObject, practice=ddd, file, line, end_line,
class_node_id
```

**repositories.ql**
```
node_id, name, semantic_type=Repository, practice=ddd, file, line, end_line,
class_node_id
```

**domain-services.ql**
```
node_id, name, semantic_type=DomainService, practice=ddd, file, line, end_line,
class_node_id
```

**domain-events.ql**
```
node_id, name, semantic_type=DomainEvent, practice=ddd, file, line, end_line,
class_node_id
```

**specifications.ql**
```
node_id, name, semantic_type=Specification, practice=ddd, file, line, end_line,
class_node_id
```

**factories.ql**
```
node_id, name, semantic_type=Factory, practice=ddd, file, line, end_line,
class_node_id
```

## Edge queries

**root.ql**
```
parent_id, child_id, kind=root, order=1, display=direct
```
Aggregate→EntityRoot.

**owns.ql**
```
parent_id, child_id, kind=owns, order=2, display=direct
```
BoundedContext→BoundedContext, BoundedContext→Aggregate, Aggregate→Entity | EntityRoot | ValueObject | Repository | DomainService | DomainEvent | Specification | Factory.

**has-identity.ql**
```
parent_id, child_id, kind=hasIdentity, order=3, display=direct
```
Entity | EntityRoot → Property | Operation.

**belongs-to.ql**
```
parent_id, child_id, kind=belongsTo, order=4, display=relationship
```

**accesses.ql**
```
parent_id, child_id, kind=accesses, order=5, display=relationship
```
Repository→EntityRoot.

**associates.ql**
```
parent_id, child_id, kind=associates, order=6, display=relationship
```

**composition.ql**
```
parent_id, child_id, kind=composition, order=7, display=relationship
```

**aggregation.ql**
```
parent_id, child_id, kind=aggregation, order=8, display=relationship
```

---

# BDD

Practice: `bdd`.

## Node queries

**specs.ql**
```
node_id, name, semantic_type=Spec, practice=bdd, file, line, end_line
```

**descriptions.ql**
```
node_id, name, semantic_type=Description, practice=bdd, file, line, end_line,
parent_name
```
name = describe() subject.

**contexts.ql**
```
node_id, name, semantic_type=Context, practice=bdd, file, line, end_line,
parent_name, setup
```
name = that() / with() text. setup = before block, or empty.

**observations.ql**
```
node_id, name, semantic_type=Observation, practice=bdd, file, line, end_line,
parent_name
```
name = it() text.

## Edge queries

**owns.ql**
```
parent_id, child_id, kind=owns, order=1, display=direct
```
Spec→Description, Description→Description, Description→Context, Context→Context, Context→Observation.

**belongs-to.ql**
```
parent_id, child_id, kind=belongsTo, order=2, display=relationship
```

---

# UX

Practice: `ux`.

## CodeQLUxMap : UxMap, CodeQLNode

## CodeQLScreen : Screen, CodeQLNode

## CodeQLRegion : Region, CodeQLNode

## CodeQLControl : Control, CodeQLNode

## CodeQLStoryDemoControl : StoryDemoControl, CodeQLNode

## CodeQLInteraction : Interaction, CodeQLNode

## CodeQLTransition : Transition, CodeQLNode

## CodeQLContentType : ContentType, CodeQLNode

## CodeQLNavComponent : NavComponent, CodeQLNode

## CodeQLUxContext : UxContext, CodeQLNode

## Node queries

**maps.ql**
```
node_id, name, semantic_type=UxMap, practice=ux, file, line, end_line
```

**screens.ql**
```
node_id, name, semantic_type=Screen, practice=ux, file, line, end_line
```

**regions.ql**
```
node_id, name, semantic_type=Region, practice=ux, file, line, end_line,
screen
```

**controls.ql**
```
node_id, name, semantic_type=Control, practice=ux, file, line, end_line,
screen, region
```

**interactions.ql**
```
node_id, name, semantic_type=Interaction, practice=ux, file, line, end_line,
control
```

**transitions.ql**
```
node_id, name, semantic_type=Transition, practice=ux, file, line, end_line,
from_screen, to_screen
```

**content-types.ql**
```
node_id, name, semantic_type=ContentType, practice=ux, file, line, end_line
```

**nav-components.ql**
```
node_id, name, semantic_type=NavComponent, practice=ux, file, line, end_line
```

**contexts.ql**
```
node_id, name, semantic_type=UxContext, practice=ux, file, line, end_line
```

## Edge queries

**owns.ql**
```
parent_id, child_id, kind=owns, order=1, display=direct
```
UxMap→Screen, Screen→Region, Region→Control, Control→Interaction, UxMap→Transition, UxMap→ContentType, UxMap→NavComponent, UxMap→UxContext.

**belongs-to.ql**
```
parent_id, child_id, kind=belongsTo, order=2, display=relationship
```

**names-state.ql**
```
parent_id, child_id, kind=namesState, order=3, display=relationship
```
Transition→Screen from_screen and to_screen.

---

# Behavior

Fidelity: behavior

Path: `harness/codeQl_graph/.examples`. Order, display, and group headings are the literals on the edge queries above. `Node.populate` walks those edge types by order.

a CodeQLKnowledgeGraph
  that is populated from harness/codeQl_graph/.examples
    with the Account Credentials codebase below
      it should hold a clean_engineering practice whose modules are account-credentials, customer, and onboarding
      it should hold a clean_engineering class ValidationCode
      it should hold a clean_engineering class ValidationCodeMessage
      it should hold a clean_engineering class AccountToken
      it should hold a clean_engineering class AccountCredentials
      it should hold a clean_engineering class AccountCredentialsException
      it should hold a clean_engineering class ValidationCodeResendWaitException
      it should hold a clean_engineering class AccountCredentialsRepository
      it should hold a clean_engineering class AccountCredentialsNode
      it should hold a clean_engineering class AccountCredentialsClient
      it should hold a clean_engineering class Identity
      it should hold a clean_engineering class Address
      it should hold a clean_engineering class Customer
      it should hold a clean_engineering class CustomerException
      it should hold a clean_engineering class CustomerRepository
      it should own AccountCredentials under module account-credentials
      it should own AccountCredentialsRepository under module account-credentials
      it should own AccountCredentialsNode under module account-credentials
      it should own AccountCredentialsClient under module account-credentials
      it should own Customer under module customer
      it should own CustomerRepository under module customer
      it should own Identity under module customer
      it should own Address under module customer
      it should list AccountCredentials.token as a direct child before AccountCredentials.register
      it should list AccountCredentials.customer as a direct child before AccountCredentials.register
      it should use relative order=1 display=direct for AccountCredentials.token
      it should use relative order=1 display=direct for AccountCredentials.customer
      it should use relative order=1 display=direct for Customer.accountCredentials
      it should use relative order=1 display=direct for Customer.identity
      it should use relative order=1 display=direct for Customer.address
      it should use relative order=1 display=direct for AccountCredentialsRepository.customerRepository
      it should use owns order=2 display=direct for module account-credentials to AccountCredentials
      it should use owns order=2 display=direct for module account-credentials to AccountCredentialsRepository
      it should use owns order=2 display=direct for module account-credentials to AccountCredentialsNode
      it should use owns order=2 display=direct for module account-credentials to AccountCredentialsClient
      it should use owns order=2 display=direct for module customer to Customer
      it should use owns order=2 display=direct for module customer to CustomerRepository
      it should use owns order=2 display=direct for AccountCredentials.register
      it should use owns order=2 display=direct for AccountCredentials.verify
      it should use owns order=2 display=direct for AccountCredentials.authenticateAccount
      it should use owns order=2 display=direct for AccountCredentials.resendValidationCode
      it should use owns order=2 display=direct for AccountCredentials.signOut
      it should use owns order=2 display=direct for AccountCredentials.storeCustomerId
      it should use owns order=2 display=direct for AccountCredentials.emailValidationCode
      it should use owns order=2 display=direct for AccountCredentials.issueSessionToken
      it should use owns order=2 display=direct for AccountCredentials.missingRequirements
      it should use owns order=2 display=direct for AccountCredentialsRepository.new
      it should use owns order=2 display=direct for AccountCredentialsRepository.create
      it should use owns order=2 display=direct for AccountCredentialsRepository.load
      it should use owns order=2 display=direct for AccountCredentialsRepository.find
      it should use owns order=2 display=direct for AccountCredentialsRepository.update
      it should use owns order=2 display=direct for CustomerRepository.new
      it should use owns order=2 display=direct for CustomerRepository.create
      it should use owns order=2 display=direct for CustomerRepository.load
      it should use owns order=2 display=direct for CustomerRepository.save
      it should list a properties group on AccountCredentials after the owns operations
      it should use properties order=3 display=grouped for AccountCredentials.email
      it should use properties order=3 display=grouped for AccountCredentials.password
      it should use properties order=3 display=grouped for AccountCredentials.confirmPassword
      it should use properties order=3 display=grouped for AccountCredentials.validationCode
      it should use properties order=3 display=grouped for AccountCredentials.verified
      it should use properties order=3 display=grouped for AccountCredentials.customerId
      it should use properties order=3 display=grouped for AccountCredentials.requirements
      it should use belongsTo order=4 display=relationship for AccountCredentials to module account-credentials
      it should use hasType order=6 display=relationship for AccountCredentials.token to AccountToken
      it should use hasType order=6 display=relationship for AccountCredentials.customer to Customer
      it should use hasType order=6 display=relationship for Customer.accountCredentials to AccountCredentials
      it should use invokes order=8 display=relationship for AccountCredentials.register to AccountCredentialsRepository.load
      it should use invokes order=8 display=relationship for AccountCredentials.register to AccountCredentialsRepository.create
      it should use invokes order=8 display=relationship for AccountCredentials.verify to AccountCredentialsRepository.update
      it should use invokes order=8 display=relationship for AccountCredentials.authenticateAccount to AccountCredentialsRepository.load
      it should use invokes order=8 display=relationship for AccountCredentials.authenticateAccount to AccountCredentialsRepository.update
      it should use invokes order=8 display=relationship for AccountCredentials.resendValidationCode to AccountCredentialsRepository.update
      it should use dependsOn order=9 display=relationship for AccountCredentials to AccountCredentialsRepository
      it should use dependsOn order=9 display=relationship for AccountCredentials to Customer
      it should walk AccountCredentials edge types in order relative, owns, properties, belongsTo, hasType, invokes, dependsOn
      it should hold a stories epic Onboard A Customer
      it should hold a stories story Create Account
      it should hold a stories story Enter Validation Code
      it should hold a stories story Sign In With Existing Account
      it should hold a stories scenario Display Create Account
      it should hold a stories scenario Enter Valid account credentials
      it should hold a stories scenario Log out and log back in
      it should hold a stories scenario Enter Invalid account credentials: missing email
      it should hold a stories scenario Email already registered
      it should hold a stories scenario Create account
      it should hold a stories scenario Enter validation code
      it should hold a stories scenario Activate with unusable validation code: mismatch validation code
      it should hold a stories scenario Resend validation code
      it should hold a stories scenario Sign in with already-registered account credentials
      it should hold a stories scenario Email format is unmet
      it should hold a stories scenario Authenticate with incorrect account credentials: wrong password
      it should hold a stories scenario Authenticate with incorrect account credentials: unknown email
      it should hold a stories scenario Authenticate with unconfirmed account
      it should hold a stories example unverifiedAccountCredentials
      it should hold a stories example verifiedAccountCredentials
      it should hold a stories example alreadyRegisteredAccountCredentials
      it should hold a stories example missingEmailAccountCredentials
      it should hold a stories example invalidEmailFormatAccountCredentials
      it should hold a stories example wrongPasswordAccountCredentials
      it should hold a stories example unknownEmailAccountCredentials
      it should use owns order=1 display=direct for Onboard A Customer to Create Account
      it should use owns order=1 display=direct for Onboard A Customer to Enter Validation Code
      it should use owns order=1 display=direct for Onboard A Customer to Sign In With Existing Account
      it should use owns order=1 display=direct for Create Account to Display Create Account
      it should use owns order=1 display=direct for Create Account to Enter Valid account credentials
      it should use owns order=1 display=direct for Create Account to Create account
      it should use owns order=1 display=direct for Enter Validation Code to Enter validation code
      it should use owns order=1 display=direct for Enter Validation Code to Resend validation code
      it should use owns order=1 display=direct for Sign In With Existing Account to Sign in with already-registered account credentials
      it should list an examples group on Create account from scopes order=2 display=grouped
      it should use scopes order=2 display=grouped for Create account to unverifiedAccountCredentials
      it should use scopes order=2 display=grouped for Enter validation code to unverifiedAccountCredentials
      it should list an examples group on AccountCredentials from demonstrates order=3 display=grouped
      it should use demonstrates order=3 display=grouped for unverifiedAccountCredentials to AccountCredentials
      it should use demonstrates order=3 display=grouped for verifiedAccountCredentials to AccountCredentials
      it should use demonstrates order=3 display=grouped for alreadyRegisteredAccountCredentials to AccountCredentials
      it should use belongsTo order=4 display=relationship for Create Account to Onboard A Customer
      it should use invokes order=5 display=relationship for Create account when to AccountCredentials.register
      it should use invokes order=5 display=relationship for Enter validation code when to AccountCredentials.verify
      it should use invokes order=5 display=relationship for Resend validation code when to AccountCredentials.resendValidationCode
      it should use invokes order=5 display=relationship for Sign in with already-registered account credentials when to AccountCredentials.authenticateAccount
      it should walk Create Account edge types in order owns, scopes, belongsTo, invokes
      it should hold no ddd BoundedContext
      it should hold no ddd Aggregate
      it should hold no ddd Entity
      it should hold no ddd EntityRoot
      it should hold no ddd ValueObject
      it should hold no ddd Repository
      it should hold no ddd owns edge
      it should hold no ddd root edge
      it should hold no ddd hasIdentity edge
      it should hold no bdd Spec
      it should hold no bdd Description
      it should hold no bdd Context
      it should hold no bdd Observation
      it should hold no bdd owns edge
      it should hold no ux UxMap
      it should hold no ux Screen
      it should hold no ux Region
      it should hold no ux Control
      it should hold no ux Transition
      it should hold no ux owns edge

## Given — Account Credentials codebase

Modules
- account-credentials — src/account-credentials
- customer — src/customer
- onboarding — src/onboarding

Classes in account-credentials
- ValidationCode — code
- ValidationCodeMessage — sentAt, email, code, executed
- AccountToken — email, customerId, jwt
- AccountCredentials — token (relative AccountToken), customer (relative Customer), customerId, email, password, confirmPassword, validationCode, verified, requirements, register, verify, authenticateAccount, resendValidationCode, signOut, storeCustomerId, emailValidationCode, issueSessionToken, missingRequirements
- AccountCredentialsException — operation, accountCredentials, cause
- ValidationCodeResendWaitException — availableAt
- AccountCredentialsRepository — customerRepository (relative CustomerRepository), new, create, load, find, update
- AccountCredentialsNode — destination, authDestination
- AccountCredentialsClient — enterEmail, enterPassword, enterConfirmPassword, snapshot

Classes in customer
- Identity — email, name, lastName, fullName
- Address — street, city, parish, postalCode, country
- Customer — accountCredentials (relative AccountCredentials), identity (relative Identity), address (relative Address), id, verified, done, terminated
- CustomerException
- CustomerRepository — new, create, load, save

Stories
- Epic: Onboard A Customer — tests/onboard-a-customer
- Sub-epic folder: Authenticate User — tests/onboard-a-customer/authenticate-user
- Story Create Account — scenarios Display Create Account, Enter Valid account credentials, Log out and log back in, Enter Invalid account credentials: missing email, Email already registered, Create account
- Story Enter Validation Code — scenarios Enter validation code, Activate with unusable validation code: mismatch validation code, Resend validation code
- Story Sign In With Existing Account — scenarios Sign in with already-registered account credentials, Email format is unmet, Authenticate with incorrect account credentials: wrong password, Authenticate with incorrect account credentials: unknown email, Authenticate with unconfirmed account

Examples
- unverifiedAccountCredentials
- verifiedAccountCredentials
- alreadyRegisteredAccountCredentials
- missingEmailAccountCredentials
- invalidEmailFormatAccountCredentials
- wrongPasswordAccountCredentials
- unknownEmailAccountCredentials

DDD, BDD, UX
- this slice has no <<stereotype>> markers, no describe/it spec, no UX map
