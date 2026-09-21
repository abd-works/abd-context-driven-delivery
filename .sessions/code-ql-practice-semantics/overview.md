Exactly. This is where CodeQL becomes much more valuable than the current scanners.

The current scanners generally do this:

Rule
→ open files
→ parse AST
→ look for one local shape
→ report violation

The stronger architecture would be:

CodeQL extracts one shared semantic model
→ classes, stereotypes, packages, properties, operations, calls, mutations
→ each scanner becomes a small constraint over those relationships

So the scanner stops rediscovering classes, methods, imports and calls for every rule.

Examples
Repository and Aggregate must share a Module
Repository
→ manages Aggregate Root
→ Repository.module must equal Aggregate.module

Conceptually:

from Repository repo, Aggregate aggregate
where repo.manages(aggregate)
  and repo.getModule() != aggregate.getModule()
select repo,
  "Repository and its Aggregate must be in the same module."

CodeQL resolves manages from relationships such as:

repository return and parameter types;
stored collection type;
interface generic type;
load, find, save, remove operations;
declared CE/DDD relationship.

That is far more reliable than checking filenames for Repository.

Repository exposes only collection-lifecycle operations
from Repository repo, Operation operation
where repo.declares(operation)
  and operation.isPublic()
  and not operation.isAggregateLifecycleOperation()
select operation,
  "Repository exposes business behaviour instead of collection lifecycle."

Allowed lifecycle semantics would include:

create
load/find/get
search/list
save/update
retire/remove/delete

But the better test is not just operation-name matching. Check what the operation does:

locating an Aggregate;
persisting an Aggregate;
replacing or retiring an Aggregate;
translating persistence or external-system records.

Flag operations that:

calculate domain values;
make domain decisions;
enforce business rules that belong to the Aggregate;
directly change an Aggregate’s internal state;
reproduce an operation already present on the Aggregate.
Domain object must own behaviour
from DomainClass domainClass
where domainClass.hasDomainState()
  and not domainClass.hasDomainOperation()
select domainClass,
  "Domain class holds state but has no behaviour."

This detects flaccid objects more semantically than “class has fields but no methods.” It can exclude:

Value Objects whose meaningful behaviour consists of equality or validation;
events;
interfaces;
external records;
framework/configuration types.

You could make it stronger:

Class has domain state
AND another Class repeatedly reads that state
AND the other Class makes decisions from it
AND the owning Class exposes no equivalent operation

That identifies displaced behaviour, not merely a low method count.

Reject doer classes
from Class doer, Class domainObject
where doer.hasDoerName()
  and doer.operatesOn(domainObject)
  and domainObject.ownsStateUsedBy(doer)
select doer,
  "Behaviour appears displaced from " + domainObject.getName()

Evidence could include:

operation accepts the domain object as a parameter;
reads several of its properties;
calculates or validates something using those properties;
changes it through setters or collection mutation;
returns a changed version;
does not represent a real external system or genuinely cross-object domain operation.

This differentiates a bad OrderManager from a legitimate external PaymentGateway or genuinely homeless Domain Service.

The object with the data owns the operation

This is probably the most valuable query:

Operation
→ reads properties
→ evaluates rules
→ writes properties
→ which Class owns those properties?

Then check:

from Operation operation, Class stateOwner
where operation.changesStateOwnedBy(stateOwner)
  and operation.getDeclaringClass() != stateOwner
  and not operation.delegatesChangeTo(stateOwner)
  and not operation.isAuthorizedCrossObjectOperation()
select operation,
  "Operation changes state owned by " + stateOwner.getName()

The critical distinction is:

// Bad: CheckoutService owns Cart behaviour
checkoutService.checkout(cart);

versus:

// Good: orchestration asks the state owner
checkoutService.submit(cart);
// internally:
cart.checkout();

The second class coordinates, but Cart still owns and performs its state change. The query should follow the call graph far enough to see that delegation.

The significant architectural change

You would have a reusable layer such as:

CDD.qll
  Module
  Class
  Interface
  Property
  Operation
  Relationship

DDD.qll
  BoundedContext
  Aggregate
  AggregateRoot
  Entity
  ValueObject
  Repository
  DomainService
  DomainEvent

Behavior.qll
  Epic
  Story
  Scenario
  Step
  Example

Architecture.qll
  ownsState
  invokes
  observes
  mutates
  manages
  dependsOn
  publishes
  subscribes

Then rules become small:

RepositoryOutsideAggregateModule.ql
RepositoryContainsBusinessOperation.ql
AnemicDomainObject.ql
DisplacedDomainBehavior.ql
ModuleDependencyCycle.ql
AggregateBypassedRoot.ql
EventWithoutSubscriber.ql
StoryStepWithoutDomainOperation.ql

The difficult work happens once in the shared predicates:

repo.manages(aggregate)
operation.mutates(class)
operation.delegatesTo(class)
class.belongsTo(module)
step.invokes(operation)

After that, most scanners really do become simple required/prohibited relationship checks.

The only caution is that CodeQL does not inherently know that something is an Aggregate, Repository, Example, or Story. Your code representations supply those semantics. Once those identities are reliably recognized, CodeQL is considerably better than separate AST scanners because it can join facts across files, packages, types, inheritance, calls, property access and data flow.

What about generating code - right now getting g chat to follow rules is trial and error when a lot the scaffolding could be interpreted by knowing a few verbs and nouns; not near the whole thing we still need ai; but could code ql play a better role; eg we figure out we need customer, subscriptions, porting, msdidn inventory, device, invoices plan. Telephone lime as aggregates; imagine we know the architecture ; eg repos are facades for web services, etc etc 

Yes—but CodeQL should not be the code generator itself. It should provide the structural intelligence that makes generation mostly deterministic.

Right now the AI receives dozens of prose rules and must repeatedly reinterpret them. Instead, treat the architecture as a model that can be compiled into scaffolding and verified through CodeQL.

The division of work
Domain nouns and verbs
        +
Known architecture profile
        ↓
Expected semantic graph
        ↓
Deterministic scaffold generator
        ↓
AI fills domain-specific behaviour
        ↓
CodeQL compares actual graph to expected graph
        ↓
Precise missing/incorrect relationships
Deterministic work

Once the nouns and architecture are known, ordinary code should generate:

package/module structure;
interfaces;
class declarations;
repository façades;
web-service adapters;
constructor dependencies;
factory structure;
example fixture structure;
test shells;
imports and exports;
relationship declarations.
AI work

AI is still needed to decide or implement:

which object owns an ambiguous operation;
business invariants;
operation parameters and results;
translations between bounded contexts;
event timing and payload;
behavioural variations;
actual web-service mappings;
production behaviour.
CodeQL work

CodeQL determines:

what already exists;
how the existing architecture is actually implemented;
what relationships the generated code must preserve;
which expected relationships are missing;
where generated code contradicts the model.
Your example

Suppose the known aggregate modules are:

Customer
Subscription
Porting
MSISDN Inventory
Device
Invoice
Plan
Telephone Line

And the known architecture says:

Each Aggregate is a Module
Each Aggregate has exactly one root
Repositories belong to their Aggregate Module
Repositories are façades over web services
Repositories expose collection lifecycle only
External clients stay behind repository implementations
Domain operations remain on domain objects

That produces an expected pattern for each aggregate:

Aggregate Module
  Aggregate Root
  Repository interface
  Web-service-backed Repository implementation
  External service interface/client
  Entities and Value Objects
  Domain Events
  Example Factory

Not every aggregate necessarily requires every element. The architecture policy determines what is mandatory and what is conditional.

For Customer, for example:

Customer Module
  Customer                         Aggregate Root + Entity
  CustomerRepository               Repository interface
  WebServiceCustomerRepository     Repository implementation
  CustomerWebService               external service interface
  Address                          Value Object
  CustomerExampleFactory           examples

The generator can create all of that without an AI interpreting paragraphs.

Where CodeQL helps before generation

CodeQL can mine the established implementation pattern from existing aggregates:

Subscription
→ SubscriptionRepository
→ ProductionSubscriptionRepository
→ MavenirSubscriptionService
→ SubscriptionExampleFactory

Then compare the pattern across all existing aggregates:

Architectural role	Customer	Subscription	Porting	Invoice
Aggregate root	✓	✓	✓	✓
Repository seam	✓	✓	✓	missing
Web-service implementation	✓	✓	✓	missing
External client	✓	✓	✓	missing
Example factory	✓	✓	✓	✓

This allows you to derive an architecture profile from code rather than continually describing it to the AI.

But I would not let CodeQL silently declare “the majority pattern is correct.” It reports the observed pattern; the explicit architecture model decides which parts are required.

Generating from nouns and verbs

You could give the system a relatively small input:

aggregate: Subscription
root: Subscription

concepts:
  - Subscription
  - TelephoneLine
  - Plan

operations:
  Subscription:
    - activate
    - suspend
    - changePlan

events:
  - SubscriptionActivated
  - SubscriptionSuspended

persistence: web-service-repository

The architecture profile supplies everything else:

web-service-repository:
  repository_location: aggregate-module
  public_operations:
    - load
    - search
    - save
    - retire
  implementation: external-service-facade
  constructor_injection: required
  business_operations: prohibited
  example_factory: required

The generator can mechanically produce:

export interface SubscriptionRepository {
  load(id: SubscriptionId): Promise<Subscription>;
  save(subscription: Subscription): Promise<Subscription>;
}

export class Subscription {
  activate(): SubscriptionActivated;
  suspend(): SubscriptionSuspended;
  changePlan(plan: Plan): void;
}

export class WebServiceSubscriptionRepository
  implements SubscriptionRepository {
  constructor(private readonly service: SubscriptionWebService) {}
}

That is structural scaffolding. AI then fills the business rules and verified service mapping.

CodeQL after generation

Instead of prompting the AI with every rule, run queries that return exact failures:

Invoice aggregate has no Repository implementation.

WebServiceSubscriptionRepository does not implement
SubscriptionRepository.

CustomerRepository declares calculateEligibility().
This is a business operation and Customer owns the data used by it.

PortingService.portNumber() modifies TelephoneLine state without
calling an operation on TelephoneLine.

SubscriptionActivated has a publisher but no subscriber.

DeviceRepository is located in the Customer module but manages Device.

Then the AI receives only the relevant correction:

{
  "rule": "state-owner-performs-change",
  "operation": "PortingService.portNumber",
  "state_owner": "TelephoneLine",
  "evidence": [
    "reads TelephoneLine.status",
    "writes TelephoneLine.status",
    "TelephoneLine has no port operation"
  ],
  "required_relationship": "PortingService -> TelephoneLine.port"
}

That is radically easier for the AI than rereading a large rulebook and guessing which rules matter.

CodeQL as an architectural completion engine

For generation, the most useful query is not merely “find violations.” It is:

Given this Aggregate, what required architectural roles and relationships
exist, and which are missing?

For example:

Aggregate: Invoice

Present:
  root: Invoice
  examples: InvoiceExampleFactory
  operations: issue, cancel

Missing:
  Repository interface
  web-service Repository implementation
  external-service dependency
  Story coverage for cancel
  Scenario Step invoking Invoice.cancel

An external generator can create the mechanical missing pieces. AI handles Invoice.cancel() because only the domain context can determine what cancellation means.

The key change

The future harness should not work like:

Tell AI all rules
→ ask it to generate code
→ hope it remembered everything
→ run many unrelated AST scanners

It should work like:

Model declares intended semantic relationships
Architecture profile expands predictable structure
Generator creates scaffolding
AI implements unresolved semantics
CodeQL constructs the actual semantic graph
Queries compare expected relationships with actual relationships
AI receives only the remaining deltas

CodeQL becomes the reliable architectural feedback mechanism. A conventional generator becomes the scaffolder. AI is reserved for decisions and behaviour that cannot be derived from the nouns, verbs, model relationships, and selected architecture.

Tuesday 11:41 AM
I need a one page summary in fact not a summary a one page design document that I can drop into my cursor IDE

Created the one-page Cursor-ready design document:

codeql-semantic-generation-design.md

codeql-semantic-generation-design.md
Document

All conversations
Favorites
Archived
⇅ A→Z
Agile By Design
3 folders -
8 chats
Augmented Team
0 folders -
43 chats
mm3e Foundry
0 folders -
23 chats
Paradise
1 folder -
3 chats
Roach Boy
0 folders -
1 chat
Social Media
0 folders -
14 chats
Notes
See All Notes
Saved automatically