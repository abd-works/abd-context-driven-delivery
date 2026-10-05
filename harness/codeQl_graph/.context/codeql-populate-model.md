# CodeQLGraph

CodeQL walks fact rows onto a `CodeQLGraph`. The CodeQL types are type-safe constructors for those nodes. They do not stitch. `populate` fills `practice.nodes` and `practice.edges`. `buildGraph` walks from each practice root.

A node query names a `semantic_type`. That type is a CodeQL class. An edge query names a `kind`, `order`, and `display`. Both catalogs grow as the queries run.

`order` and `display` are literals in the edge query. display = direct | grouped | relationship.

Loaders: `queries/{language}/{practice}/nodes`, then `queries/{language}/{practice}/edges`, then `queries/{language}/{practice}/rules`. Pass `language` to `populate` so the graph reads that pack.

A cross-practice edge is stored on the parent's practice. The reverse, child to parent with the same kind, is stored on the child's practice.

`node_id` = `{practice}:{semantic_type}:{file}:{name}` (add class or operation when the name is not unique).

---

## CodeQLGraph

+ CodeQLPracticeGraph: dict
	// practice name → CodeQLPracticeGraph
----
+ populate(path, practices, language): CodeQLGraph
	// language selects queries/{language}/{practice}. For each practice: run node queries, then edge queries, then rule queries, then buildGraph
+ buildGraph(): None
	// for each practice: root = practice.rootNode; root.populate()

## CodeQLPracticeGraph

+ name: str
+ nodes: dict
	// by node type → list[CodeQLNode]. filled from node queries
+ edges: dict
	// by edge type → list[Edge]. filled from edge queries. node ↔ node
+ node_types: set of all node types
	// semantic_type as queries run
+ edge_types: set of all edge types
	// EdgeType as queries run, keyed by order
+ rootNode: CodeQLNode
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
+ parent: CodeQLNode
+ child: CodeQLNode

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

## CodeQLNode

The type-safe CodeQL class for this semantic_type. Lives in `practice.nodes[type]`.

+ practice: Practice
+ type: str
	// semantic_type
+ node_id: str
+ name: str
+ source: Source
+ children: list[CodeQLNode]
----
+ from_fact(row): CodeQLNode
	// this type. source from file, line, end_line
+ populate(parent=None): None
	// if parent: parent.children.add(this)
	// for edge_type in practice.edge_types sorted by order
	//   for edge in practice.edges[edge_type.kind] where edge.parent is this
	//     display=grouped:
	//       group = existing child named edge.kind, or a new group CodeQLNode
	//       children.add(group)
	//       edge.child.populate(group)
	//     display=direct:
	//       edge.child.populate(this)
	//     display=relationship:
	//       rel = existing child named edge.kind, or a new relationship CodeQLNode
	//       children.add(rel)
	//       edge.child.populate(rel)

## CodeQLNode fact

Every node query `select`s this, then practice columns.

```
node_id, name, semantic_type, practice, file, line, end_line
```

## GraphEdge fact

Every edge query `select`s this. `kind`, `order`, and `display` are hardcoded in that query.

```
parent_id, child_id, kind, order, display
```

## Rule fact

Every practice has a `rules` folder beside `nodes` and `edges`. A rule query names one rule. It binds node facts and edge facts already loaded. It does not select classes, calls, or files on its own.

A rule may name more than one node kind. Each kind it names is a subject it checks.

A rule that passes selects no row. A rule that fails selects a violation:

```
rule, node_id, violation
```

`violation` is `{rule} violation suspected at {node_id} {violation details}`.

When the check is a relationship, the same row also carries the edge already loaded:

```
rule, node_id, parent_id, child_id, kind, violation
```

`node_id` is the subject. The same slug is one query file in each language pack that already has that rule. A slug that exists only for TypeScript stays in the TypeScript pack.

---

# Clean Engineering

Practice: `clean_engineering`. A class is an OoadClass. DDD stereotypes are the DDD queries.


## CodeQLNode queries

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
Class methods.

**functions.ql**
```
node_id, name, semantic_type=Operation, practice=clean_engineering, file, line, end_line,
module
```
File-level functions. They are operations with no class. The module owns them so a bare function stays visible.

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

**class-relative-properties.ql**
```
parent_id, child_id, kind=relative, order=1, display=direct
```
OoadClass→Property when type_hint names another loaded class.

**repo-owns-modules.ql**, **module-owns-classes.ql**, **module-owns-operations.ql**, **class-owns-operations.ql**, **operation-owns-parameters.ql**
```
parent_id, child_id, kind=owns, order=2, display=direct
```
Repo→Module, Module→OoadClass, Module→file-level Operation, OoadClass→Operation, Operation→Parameter.

**class-properties-properties.ql**
```
parent_id, child_id, kind=properties, order=3, display=grouped
```
OoadClass→leftover Property. Heading = properties.

**class-belongs-to-module.ql**
```
parent_id, child_id, kind=belongsTo, order=4, display=relationship
```

**operation-has-parameter-parameters.ql**
```
parent_id, child_id, kind=hasParameter, order=5, display=relationship
```
Operation→Parameter.

**property-has-type-class.ql**
```
parent_id, child_id, kind=hasType, order=6, display=relationship
```
Property→OoadClass named by type_hint.

**operation-returns-class.ql**
```
parent_id, child_id, kind=returns, order=7, display=relationship
```
Operation→OoadClass named by return_type.

**operation-invokes-operations.ql**
```
parent_id, child_id, kind=invokes, order=8, display=relationship
```
Operation→Operation.

**class-depends-on-classes.ql**
```
parent_id, child_id, kind=dependsOn, order=9, display=relationship
```
OoadClass→OoadClass when an invokes row leaves the owner.

**class-associates-classes.ql**
```
parent_id, child_id, kind=associates, order=10, display=relationship
```
OoadClass→OoadClass.

**class-composition-classes.ql**
```
parent_id, child_id, kind=composition, order=11, display=relationship
```
OoadClass→OoadClass.

**class-aggregation-classes.ql**
```
parent_id, child_id, kind=aggregation, order=12, display=relationship
```
OoadClass→OoadClass.

## Rule queries

**keep-operations-small-focused.ql** — Operation. Source of that operation is longer than 20 statements.

**limit-operation-parameters.ql** — Operation, Parameter. `hasParameter` / `owns`. More than two parameters.

**avoid-vague-parameter-names.ql** — Operation, Parameter. `hasParameter`. Parameter name is data, options, or info.

**simplify-control-flow.ql** — Operation. Source nests control flow more than three levels.

**never-swallow-exceptions.ql** — Operation. Source catches and ignores.

**use-exceptions-properly.ql** — Operation. Source has a bare except.

**use-explicit-dependencies.ql** — OoadClass, Operation. `owns`. Constructor operation constructs another class.

**use-property-not-accessor.ql** — OoadClass, Operation. `owns`. Operation is an accessor for a property.

**prefer-class-operations.ql** — Module, Operation. `owns`. Operation is owned by the module.

**prefer-instance-operations.ql** — Operation. Operation is static.

**hide-inner-details.ql** — Operation, Property. Operation source reads a private property.

**low-coupling.ql** — Operation, Property. Operation source reaches a property past the owning class.

**shape-classes-around-resources.ql** — OoadClass. `associates`, `dependsOn`. One class acts on another class that only holds properties.

**put-logic-on-the-owning-resource.ql** — Operation, Parameter. `hasParameter`. Operation works through a parameter instead of the parameter's class.

**use-typed-signatures.ql** — Operation, Parameter. `hasParameter`. Parameter has no type.

**provide-meaningful-context.ql** — Operation, Parameter. `hasParameter`. Parameter name is numbered.

**deep-module.ql** — Module, OoadClass. `owns`. Public class count against class count.

**one-way-deps.ql** — Module. `dependsOn`. Two modules depend on each other.

**extensions-live-with-the-domain.ql** — OoadClass, Module. `belongsTo`. An extending class sits in a different module from the class it extends.

**layer-separation.ql** — Operation. `invokes`. Operation has one invoke and no other work.

**keep-classes-single-responsibility.ql** — OoadClass, Operation. `owns`. Owned operations split into more than one concern.

**do-not-invent-parallel-object-models.ql** — OoadClass, Operation. `owns`, `associates`, `dependsOn`, `composition`, `aggregation`.

A collection is one OoadClass plus every OoadClass reached from it by those edges. Its class count is the size of that set. Its nouns are those class names with a leading `Graph`, `CodeQL`, or `Ooad` removed. Its verbs are the names of the Operations those classes `owns`. Its method count is the number of those operations.

Two collections mirror each other when they share a noun and share a verb, and both the class counts and the method counts differ. The violation is on each class in the collection with the smaller method count. Details name the other collection's class count and method count.

A single class also fails when it links two classes that have no path between them through those edges once that class is left out. That class is joining two shapes the rest of the graph keeps apart.

**missing-module-context.ql**, **language-modules-one-section.ql**, **public-seam-only.ql**, **modules-not-model-blocks.ql** — Module, OoadClass. `owns`, `belongsTo`. Class file and module do not match the module layout.

**eliminate-duplication.ql** — Operation. Two operations share portions of one body.

**limit-comments.ql** — Operation. Source comment narrates the operation.

**named-seam-and-constraint.ql** — Module. Module source does not name a seam and a constraint.

**constants-not-magic-strings.ql** — Operation, Property. Source string is not a named constant on the class.

**no-screen-map-banner-comments.ql** — Module. Module file opens with a screen or story banner comment.

**prefix-own-class-member.ql** — OoadClass, Property, Operation. `owns`, `invokes`. Member is used only by its owning class.

**use-consistent-naming.ql** — Module, Operation. `owns`. Operations in one module mix snake_case and camelCase.

**use-intention-revealing-names.ql** — Operation. Operation or a name in its source hides the intent.

---

# Stories

Practice: `stories`. Story edges may name a Clean Engineering node_id already registered.

## CodeQLNode queries

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

**repo-owns-epics.ql**, **epic-owns-stories.ql**, **story-owns-scenarios.ql**, **story-owns-backgrounds.ql**, **scenario-owns-steps.ql**, **story-owns-steps.ql**
```
parent_id, child_id, kind=owns, order=1, display=direct
```
Repo→Epic, Epic→Story, Story→Scenario, Story→Background, Scenario→Step, Story→Step.

**step-scopes-examples.ql**
```
parent_id, child_id, kind=scopes, order=2, display=grouped
```
Step→Example. Heading = examples.

**example-demonstrates-class.ql**
```
parent_id, child_id, kind=demonstrates, order=3, display=grouped
```
Example→OoadClass. Heading = examples on the class.

**story-belongs-to-epic.ql**
```
parent_id, child_id, kind=belongsTo, order=4, display=relationship
```

**step-invokes-operations.ql**
```
parent_id, child_id, kind=invokes, order=5, display=relationship
```
Step→Operation on a when.

**class-demonstrated-through-examples.ql**
```
parent_id, child_id, kind=demonstratedThrough, order=6, display=relationship
```
OoadClass→Example.

**example-retrieved-using-operations.ql**, **example-retrieved-using-properties.ql**
```
parent_id, child_id, kind=retrievedUsing, order=7, display=relationship
```
Example→Operation, Example→Property.

**step-observes-examples.ql**
```
parent_id, child_id, kind=observes, order=8, display=relationship
```
then Step→Example.

**epic-uses-modules.ql**
```
parent_id, child_id, kind=uses, order=9, display=relationship
```
Epic→Module.

## Rule queries

**verb-noun-format.ql** — Story. Story name.

**story-name-captures-system-mechanic.ql** — Story. Story name.

**vocabulary-traces-to-domain-source.ql** — Story, OoadClass. Story name against class names already loaded.

**plain-english-gwt-steps.ql** — Step. Step name is a code identifier.

**gwt-steps-trace-to-domain-operations.ql** — Step, OoadClass. `invokes`. Step name against a class, or the step's invoke.

**domain-operation-in-the-step.ql** — Step, Operation. `invokes`. Step body is one domain operation call.

**kebab-case-paths.ql** — Epic, Story, Scenario, Step, Example. Node file path.

**four-to-nine-children.ql** — Story, Scenario. `owns`. Scenario count under the story.

**right-size-story-nodes.ql** — Story, Epic. `owns`. Sibling story names under one epic.

**domain-fixture-example-files.ql** — Example. Example file name.

**example-role-names.ql** — Example. Example name says entered, stored, or expected.

**initialize-from-fixture-then-seed.ql** — Example, OoadClass. Story source constructs a class instead of an example.

**originating-sub-epic-examples.ql** — Example, Epic, Story. `owns`. Example file sits on the epic instead of the story that owns it.

---

# DDD

Practice: `ddd`. Clean Engineering already registered the class as OoadClass. A DDD node fact is the stereotyped type for the same source span. `class_node_id` is that OoadClass. Load does not promote. DDD `nodes` are only DDD stereotypes: BoundedContext, Aggregate, Entity, EntityRoot, ValueObject, Repository, DomainService, DomainEvent, Specification, Factory. An OoadClass, Operation, Property, Parameter, Exception, CodeQLNode, or Client does not appear on the DDD graph.


## CodeQLNode queries

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

**aggregate-root-entity-root.ql**
```
parent_id, child_id, kind=root, order=1, display=direct
```
Aggregate→EntityRoot.

**repo-owns-bounded-contexts.ql**, **bounded-context-owns-aggregates.ql**, **aggregate-owns-entities.ql**, **aggregate-owns-value-objects.ql**, **aggregate-owns-repositories.ql**, **aggregate-owns-domain-services.ql**, **aggregate-owns-domain-events.ql**, **aggregate-owns-specifications.ql**, **aggregate-owns-factories.ql**
```
parent_id, child_id, kind=owns, order=2, display=direct
```
Repo→BoundedContext, BoundedContext→Aggregate, Aggregate→Entity | ValueObject | Repository | DomainService | DomainEvent | Specification | Factory.

**entity-has-identity-property.ql**, **entity-root-has-identity-property.ql**
```
parent_id, child_id, kind=hasIdentity, order=3, display=direct
```
Entity→Property, EntityRoot→Property.

**aggregate-belongs-to-bounded-context.ql**, **entity-belongs-to-aggregate.ql**, **entity-root-belongs-to-aggregate.ql**, **value-object-belongs-to-aggregate.ql**, **repository-belongs-to-aggregate.ql**, **domain-service-belongs-to-aggregate.ql**, **domain-event-belongs-to-aggregate.ql**, **specification-belongs-to-aggregate.ql**, **factory-belongs-to-aggregate.ql**
```
parent_id, child_id, kind=belongsTo, order=4, display=relationship
```

**repository-accesses-entity-root.ql**
```
parent_id, child_id, kind=accesses, order=5, display=relationship
```
Repository→EntityRoot.

**entity-associates-entities.ql**, **entity-root-associates-entities.ql**
```
parent_id, child_id, kind=associates, order=6, display=relationship
```

**type-composition-types.ql**
```
parent_id, child_id, kind=composition, order=7, display=relationship
```

**type-aggregation-types.ql**
```
parent_id, child_id, kind=aggregation, order=8, display=relationship
```

## Rule queries

**building-blocks-fidelity-requires-tactical-stereotype.ql** — OoadClass. No DDD stereotype node for that class.

**domain-concepts-not-technical-names.ql** — Aggregate, Entity, EntityRoot, ValueObject, Repository, DomainService. Node name.

**screen-interface-not-a-domain-object.ql** — Entity, EntityRoot, ValueObject, Aggregate, DomainService. Node name is a screen driver.

**flaccid-data-object-no-behavior.ql** — Entity, EntityRoot, ValueObject. `owns`. No owned operation.

**no-orphaned-objects.ql** — Entity, EntityRoot, ValueObject. `associates`, `composition`, `aggregation`, `belongsTo`. No relationship edge.

**repository-is-collection-lifecycle.ql** — Repository, Operation. `owns`. Repository name without lifecycle operations.

**aggregate-owns-operation-repo-is-crud.ql** — Repository, Operation. `owns`. Owned operation is not create, read, update, or delete.

**repository-stores-related-aggregate-by-id.ql** — Repository, Property, Aggregate. `properties`, `hasType`. Property holds another aggregate instead of its id.

**service-is-homeless.ql** — DomainService, Operation. `owns`. Operations belong on an entity or aggregate.

**load-with-identity-in-hand.ql** — Repository, Operation, Parameter. `hasParameter`. Operation named load has no parameter.

**domain-objects-own-their-attributes.ql** — Aggregate, Entity, Property. `owns`, `properties`. Property describes another aggregate.

**aggregate-lives-in-its-own-folder.ql** — Aggregate, EntityRoot. `belongsTo`. File path of the root.

**fluent-operation-returns-next-aggregate.ql** — Operation, Aggregate. `returns`. Return is the next aggregate.

**operation-verb-matches-scenario.ql** — Operation, Step. `invokes`. Step name and operation name.

**private-cross-aggregate-step.ql** — Operation, Aggregate. `invokes`. Operation on one aggregate is only called from another aggregate.

**private-method-naming.ql** — Operation. `invokes`. Private operation is invoked from outside its class.

**caller-orchestrates-cross-aggregate-flow.ql** — Operation, Repository, Aggregate. `invokes`, `accesses`. Caller operation reaches another aggregate's repository.

**construct-repository-at-the-caller.ql** — Module, Repository, Operation. `owns`. Repository is constructed on the module.

**throw-typed-exception-with-message.ql** — Operation. Source throws a plain object.

**arrange-with-empty-and-seed.ql** — Example, Repository, Operation. `invokes`. Example seeds through a repository operation.

---

# BDD

Practice: `bdd`.

## CodeQLNode queries

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

**repo-owns-specs.ql**, **spec-owns-descriptions.ql**, **description-owns-descriptions.ql**, **description-owns-contexts.ql**, **context-owns-contexts.ql**, **context-owns-observations.ql**
```
parent_id, child_id, kind=owns, order=1, display=direct
```
Repo→Spec, Spec→Description, Description→Description, Description→Context, Context→Context, Context→Observation.

**description-belongs-to-spec.ql**, **description-belongs-to-description.ql**, **context-belongs-to-description.ql**, **context-belongs-to-context.ql**, **observation-belongs-to-context.ql**
```
parent_id, child_id, kind=belongsTo, order=2, display=relationship
```

## Rule queries

**describe-is-subject-not-internal.ql** — Description. Description name is an internal type.

**state-not-when.ql** — Context. Context name starts with when.

**observable-behavior.ql** — Observation. Observation source reads a private attribute.

**one-assertion-per-test.ql** — Observation. Observation source has more than one assertion.

**layer-isolation.ql** — Observation. Observation source mocks an internal module.

---

# UX

Practice: `ux`.

## CodeQLNode queries

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

**repo-owns-maps.ql**, **map-owns-screens.ql**, **screen-owns-regions.ql**, **region-owns-controls.ql**, **control-owns-interactions.ql**, **map-owns-transitions.ql**, **map-owns-content-types.ql**, **map-owns-nav-components.ql**, **map-owns-contexts.ql**
```
parent_id, child_id, kind=owns, order=1, display=direct
```
Repo→UxMap, UxMap→Screen, Screen→Region, Region→Control, Control→Interaction, UxMap→Transition, UxMap→ContentType, UxMap→NavComponent, UxMap→UxContext.

**screen-belongs-to-map.ql**, **region-belongs-to-screen.ql**, **control-belongs-to-region.ql**, **interaction-belongs-to-control.ql**, **transition-belongs-to-map.ql**, **content-type-belongs-to-map.ql**, **nav-component-belongs-to-map.ql**, **context-belongs-to-map.ql**
```
parent_id, child_id, kind=belongsTo, order=2, display=relationship
```

**transition-names-state-screens.ql**
```
parent_id, child_id, kind=namesState, order=3, display=relationship
```
Transition→Screen from_screen and to_screen.

## Rule queries

**screen-names-use-domain-terms.ql** — Screen, OoadClass. Screen name against a class name already loaded.

**key-interactions-wired.ql** — Screen, Interaction. `owns` through Region and Control. Screen has no interaction.

**story-domain-js-imported.ql** — Screen, Module. `dependsOn`. Screen module depends on a stub instead of a story or domain module.

---

# Behavior

Fidelity: behavior

Each practice is its own sketch. Path: `harness/codeQl_graph/.examples`.

Two steps. First `that has run the queries` — node counts, node types, edge types. Those have to pass. Then `that has been populated` — walk `children`. Each child is named as what it is: module, class, relative, property, operation, parameter, grouped heading, or relationship. Direct kinds (relative, owns) share one list, ordered by edge type: relatives first, then owned members. Grouped and relationship insert an extra node named for the kind; members sit under that extra node.

a clean_engineering practice
  that has run the queries on harness/codeQl_graph/.examples
    with the Account Credentials codebase below
      it should have 3 Module nodes
      it should have 14 OoadClass nodes
      it should have node types Module, OoadClass, Operation, Property, Parameter
      it should have 136 edges across 8 types
      it should have edge types relative, owns, properties, belongsTo, hasParameter, hasType, invokes, dependsOn
      that has been populated
        it should have children module account-credentials, module customer, module onboarding
        with module account-credentials
          it should have children class ValidationCode, class ValidationCodeMessage, class AccountToken, class AccountCredentials, class AccountCredentialsException, class ValidationCodeResendWaitException, class AccountCredentialsRepository, class AccountCredentialsNode, class AccountCredentialsClient
          with class ValidationCode
            it should have children grouped properties, relationship belongsTo
            with grouped properties
              it should have children property code, property sentAt
            with relationship belongsTo
              it should have children module account-credentials
          with class ValidationCodeMessage
            it should have children grouped properties, relationship belongsTo
            with grouped properties
              it should have children property sentAt, property email, property code, property executed
            with relationship belongsTo
              it should have children module account-credentials
          with class AccountToken
            it should have children grouped properties, relationship belongsTo
            with grouped properties
              it should have children property email, property customerId, property jwt
            with relationship belongsTo
              it should have children module account-credentials
          with class AccountCredentials
            it should have children relative token, relative customer, operation register, operation verify, operation authenticateAccount, operation resendValidationCode, operation signOut, operation storeCustomerId, operation emailValidationCode, operation issueSessionToken, operation missingRequirements, grouped properties, relationship belongsTo, relationship dependsOn
            with relative token
              it should have children relationship hasType
              with relationship hasType
                it should have children class AccountToken
            with relative customer
              it should have children relationship hasType
              with relationship hasType
                it should have children class Customer
            with operation register
              it should have children relationship invokes
              with relationship invokes
                it should have children operation AccountCredentialsRepository.load, operation AccountCredentialsRepository.create
            with operation verify
              it should have children parameter validationCode, relationship hasParameter, relationship invokes
              with parameter validationCode
                it should have children relationship hasParameter
              with relationship hasParameter
                it should have children parameter validationCode
              with relationship invokes
                it should have children operation AccountCredentialsRepository.update
            with operation authenticateAccount
              it should have children relationship invokes
              with relationship invokes
                it should have children operation AccountCredentialsRepository.load, operation AccountCredentialsRepository.update
            with operation resendValidationCode
              it should have children relationship invokes
              with relationship invokes
                it should have children operation AccountCredentialsRepository.update
            with operation storeCustomerId
              it should have children parameter customerId, relationship hasParameter
              with relationship hasParameter
                it should have children parameter customerId
            with grouped properties
              it should have children property email, property password, property confirmPassword, property validationCode, property verified, property customerId, property requirements
            with relationship belongsTo
              it should have children module account-credentials
            with relationship dependsOn
              it should have children class AccountCredentialsRepository, class Customer
          with class AccountCredentialsException
            it should have children relative accountCredentials, grouped properties, relationship belongsTo
            with relative accountCredentials
              it should have children relationship hasType
              with relationship hasType
                it should have children class AccountCredentials
            with grouped properties
              it should have children property operation, property cause
            with relationship belongsTo
              it should have children module account-credentials
          with class ValidationCodeResendWaitException
            it should have children grouped properties, relationship belongsTo
            with grouped properties
              it should have children property availableAt
            with relationship belongsTo
              it should have children module account-credentials
          with class AccountCredentialsRepository
            it should have children relative customerRepository, operation new, operation create, operation load, operation find, operation update, relationship belongsTo
            with relative customerRepository
              it should have children relationship hasType
              with relationship hasType
                it should have children class CustomerRepository
            with operation create
              it should have children parameter accountCredentials, relationship hasParameter
              with relationship hasParameter
                it should have children parameter accountCredentials
            with operation load
              it should have children parameter email, relationship hasParameter
              with relationship hasParameter
                it should have children parameter email
            with operation find
              it should have children parameter email, relationship hasParameter
              with relationship hasParameter
                it should have children parameter email
            with operation update
              it should have children parameter accountCredentials, relationship hasParameter
              with relationship hasParameter
                it should have children parameter accountCredentials
            with relationship belongsTo
              it should have children module account-credentials
          with class AccountCredentialsNode
            it should have children operation destination, operation authDestination, relationship belongsTo
            with relationship belongsTo
              it should have children module account-credentials
          with class AccountCredentialsClient
            it should have children operation enterEmail, operation enterPassword, operation enterConfirmPassword, operation snapshot, relationship belongsTo
            with operation enterEmail
              it should have children parameter email, relationship hasParameter
              with relationship hasParameter
                it should have children parameter email
            with operation enterPassword
              it should have children parameter password, relationship hasParameter
              with relationship hasParameter
                it should have children parameter password
            with operation enterConfirmPassword
              it should have children parameter confirmPassword, relationship hasParameter
              with relationship hasParameter
                it should have children parameter confirmPassword
            with relationship belongsTo
              it should have children module account-credentials
        with module customer
          it should have children class Identity, class Address, class Customer, class CustomerException, class CustomerRepository
          with class Identity
            it should have children grouped properties, relationship belongsTo
            with grouped properties
              it should have children property email, property name, property lastName, property fullName
            with relationship belongsTo
              it should have children module customer
          with class Address
            it should have children grouped properties, relationship belongsTo
            with grouped properties
              it should have children property street, property city, property parish, property postalCode, property country
            with relationship belongsTo
              it should have children module customer
          with class Customer
            it should have children relative accountCredentials, relative identity, relative address, operation terminated, grouped properties, relationship belongsTo
            with relative accountCredentials
              it should have children relationship hasType
              with relationship hasType
                it should have children class AccountCredentials
            with relative identity
              it should have children relationship hasType
              with relationship hasType
                it should have children class Identity
            with relative address
              it should have children relationship hasType
              with relationship hasType
                it should have children class Address
            with grouped properties
              it should have children property id, property verified, property done
            with relationship belongsTo
              it should have children module customer
          with class CustomerException
            it should have children relative accountCredentials, grouped properties, relationship belongsTo
            with relative accountCredentials
              it should have children relationship hasType
              with relationship hasType
                it should have children class AccountCredentials
            with grouped properties
              it should have children property operation, property cause
            with relationship belongsTo
              it should have children module customer
          with class CustomerRepository
            it should have children operation new, operation create, operation load, operation save, relationship belongsTo
            with operation new
              it should have children parameter customer, relationship hasParameter
              with relationship hasParameter
                it should have children parameter customer
            with operation create
              it should have children parameter accountCredentials, relationship hasParameter
              with relationship hasParameter
                it should have children parameter accountCredentials
            with operation load
              it should have children parameter accountCredentials, relationship hasParameter
              with relationship hasParameter
                it should have children parameter accountCredentials
            with operation save
              it should have children parameter customer, relationship hasParameter
              with relationship hasParameter
                it should have children parameter customer
            with relationship belongsTo
              it should have children module customer
        with module onboarding
          it should have no children

a stories practice
  that has run the queries on harness/codeQl_graph/.examples
    with the Account Credentials codebase below
      it should have 1 Epic node
      it should have 3 Story nodes
      it should have 14 Scenario nodes
      it should have 1 Background node
      it should have 7 Example nodes
      it should have node types Epic, Story, Scenario, Background, Step, Example
      it should have 86 edges across 5 types
      it should have edge types owns, scopes, demonstrates, belongsTo, invokes
      that has been populated
        it should have children epic Onboard A Customer
        with epic Onboard A Customer
          it should have children story Create Account, story Enter Validation Code, story Sign In With Existing Account, relationship belongsTo
          with story Create Account
            it should have children scenario Display Create Account, scenario Enter Valid account credentials, scenario Log out and log back in, scenario Enter Invalid account credentials: missing email, scenario Email already registered, scenario Create account, relationship belongsTo
            with scenario Display Create Account
              it should have children step when the User proceeds to create an account from the Paradise Mobile website, step then the User can enter account credentials
              with step then the User can enter account credentials
                it should have children step and the email and password rules are unmet, step and the customer cannot save the customer account
            with scenario Enter Valid account credentials
              it should have children step when the User enters valid account credentials, step then account credentials are validated continuously
              with step then account credentials are validated continuously
                it should have children step and the customer can save the customer account
            with scenario Log out and log back in
              it should have children step given the User has entered valid account credentials, step when the User logs out of the site, step then the account has no browser session, step when the User enters the username and password, step then the account is logged in
            with scenario Enter Invalid account credentials: missing email
              it should have children step when the User registers missing email, step then the account cannot be registered
              with step then the account cannot be registered
                it should have children step and the emailRequired requirement is unmet
            with scenario Email already registered
              it should have children step given already-registered account credentials are already registered, step when the User registers already-registered account credentials, step then the email is already registered
            with scenario Create account
              it should have children step when the User creates their account, step then the account is unconfirmed and a validation code is emailed
              with step when the User creates their account
                it should have children grouped examples, relationship invokes
                with grouped examples
                  it should have children example unverifiedAccountCredentials
                  with example unverifiedAccountCredentials
                    it should have children grouped examples
                    with grouped examples
                      it should have children class AccountCredentials
                with relationship invokes
                  it should have children operation AccountCredentials.register
            with relationship belongsTo
              it should have children epic Onboard A Customer
          with story Enter Validation Code
            it should have children background, scenario Enter validation code, scenario Activate with unusable validation code: mismatch validation code, scenario Resend validation code, relationship belongsTo
            with background
              it should have children step given the User has submitted valid account credentials
              with step given the User has submitted valid account credentials
                it should have children step and an unconfirmed account exists, step and a validation code has been sent to the User
            with scenario Enter validation code
              it should have children step when the User verifies the account with the emailed validation code, step then the account is verified
              with step when the User verifies the account with the emailed validation code
                it should have children grouped examples, relationship invokes
                with grouped examples
                  it should have children example unverifiedAccountCredentials
                with relationship invokes
                  it should have children operation AccountCredentials.verify
              with step then the account is verified
                it should have children step and the account has a token for the browser session
            with scenario Activate with unusable validation code: mismatch validation code
              it should have children step when the User verifies with mismatch validation code, step then the validation code is rejected
            with scenario Resend validation code
              it should have children step when more than 60 seconds has passed, step and the User resends the validation code
              with step and the User resends the validation code
                it should have children relationship invokes
                with relationship invokes
                  it should have children operation AccountCredentials.resendValidationCode
            with relationship belongsTo
              it should have children epic Onboard A Customer
          with story Sign In With Existing Account
            it should have children scenario Sign in with already-registered account credentials, scenario Email format is unmet, scenario Authenticate with incorrect account credentials: wrong password, scenario Authenticate with incorrect account credentials: unknown email, scenario Authenticate with unconfirmed account, relationship belongsTo
            with scenario Sign in with already-registered account credentials
              it should have children step given an already-registered account exists, step when the Customer authenticates already-registered account credentials, step then the account has a token for the browser session
              with step given an already-registered account exists
                it should have children step and the Customer is not signed in, step and the Customer has already-registered account credentials
              with step when the Customer authenticates already-registered account credentials
                it should have children relationship invokes
                with relationship invokes
                  it should have children operation AccountCredentials.authenticateAccount
              with step then the account has a token for the browser session
                it should have children step and the account holds the customer id
            with scenario Email format is unmet
              it should have children step given the Customer has invalid email format account credentials, step when the Customer authenticates invalid email format, step then the authentication is rejected
              with step then the authentication is rejected
                it should have children step and the account has no token
            with scenario Authenticate with incorrect account credentials: wrong password
              it should have children step given an already-registered account exists, step when the Customer authenticates wrong password, step then the authentication is rejected
            with scenario Authenticate with incorrect account credentials: unknown email
              it should have children step given an already-registered account exists, step when the Customer authenticates unknown email, step then the authentication is rejected
            with scenario Authenticate with unconfirmed account
              it should have children step given an unconfirmed account exists, step when the Customer authenticates unconfirmed sign-in, step then the account has a token for the browser session
              with step then the account has a token for the browser session
                it should have children step and the account has no customer, step and the Customer can enter the validation code, step and the Customer is on the Verify Account step
            with relationship belongsTo
              it should have children epic Onboard A Customer

a ddd practice
  that has run the queries on harness/codeQl_graph/.examples
    with the Account Credentials codebase below
      it should have 1 BoundedContext node
      it should have 2 Aggregate nodes
      it should have 0 Entity nodes
      it should have 2 EntityRoot nodes
      it should have 5 ValueObject nodes
      it should have 2 Repository nodes
      it should have 26 edges across 5 types
      it should have edge types root, owns, belongsTo, accesses, associates
      it should have node types BoundedContext, Aggregate, EntityRoot, ValueObject, Repository
      it should have no OoadClass
      it should have no Property
      it should have no Operation
      it should have no Parameter
      it should have no Module
      it should have no AccountCredentialsException
      it should have no ValidationCodeResendWaitException
      it should have no AccountCredentialsNode
      it should have no AccountCredentialsClient
      it should have no CustomerException
      that has been populated
        it should have children bounded context
        with bounded context
          it should have children aggregate account-credentials, aggregate customer
          with aggregate account-credentials
            it should have children EntityRoot AccountCredentials, ValueObject ValidationCode, ValueObject ValidationCodeMessage, ValueObject AccountToken, Repository AccountCredentialsRepository
            with EntityRoot AccountCredentials
              it should have children relationship belongsTo, relationship associates
              with relationship belongsTo
                it should have children aggregate account-credentials
              with relationship associates
                it should have children EntityRoot Customer
            with ValueObject ValidationCode
              it should have children relationship belongsTo
              with relationship belongsTo
                it should have children aggregate account-credentials
            with ValueObject ValidationCodeMessage
              it should have children relationship belongsTo
              with relationship belongsTo
                it should have children aggregate account-credentials
            with ValueObject AccountToken
              it should have children relationship belongsTo
              with relationship belongsTo
                it should have children aggregate account-credentials
            with Repository AccountCredentialsRepository
              it should have children relationship belongsTo, relationship accesses
              with relationship belongsTo
                it should have children aggregate account-credentials
              with relationship accesses
                it should have children EntityRoot AccountCredentials
            with relationship belongsTo
              it should have children bounded context
          with aggregate customer
            it should have children EntityRoot Customer, ValueObject Identity, ValueObject Address, Repository CustomerRepository
            with EntityRoot Customer
              it should have children relationship belongsTo, relationship associates
              with relationship belongsTo
                it should have children aggregate customer
              with relationship associates
                it should have children EntityRoot AccountCredentials
            with ValueObject Identity
              it should have children relationship belongsTo
              with relationship belongsTo
                it should have children aggregate customer
            with ValueObject Address
              it should have children relationship belongsTo
              with relationship belongsTo
                it should have children aggregate customer
            with Repository CustomerRepository
              it should have children relationship belongsTo, relationship accesses
              with relationship belongsTo
                it should have children aggregate customer
              with relationship accesses
                it should have children EntityRoot Customer
            with relationship belongsTo
              it should have children bounded context

a bdd practice
  that has run the queries on harness/codeQl_graph/.examples
    with the Account Credentials codebase below
      it should have 0 Spec nodes
      it should have 0 Description nodes
      it should have 0 Context nodes
      it should have 0 Observation nodes
      it should have 0 edges across 0 types
      it should have node types Spec, Description, Context, Observation
      that has been populated
        it should have no children

a ux practice
  that has run the queries on harness/codeQl_graph/.examples
    with the Account Credentials codebase below
      it should have 0 UxMap nodes
      it should have 0 Screen nodes
      it should have 0 Region nodes
      it should have 0 Control nodes
      it should have 0 Transition nodes
      it should have 0 edges across 0 types
      it should have node types UxMap, Screen, Region, Control, Interaction, Transition, ContentType, NavComponent, UxContext
      that has been populated
        it should have no children


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

DDD
- DDD graph is only DDD stereotypes: BoundedContext, Aggregate, EntityRoot, ValueObject, Repository
- implicit bounded context over the examples path
- aggregate account-credentials — EntityRoot AccountCredentials, ValueObjects ValidationCode, ValidationCodeMessage, AccountToken, Repository AccountCredentialsRepository; associates EntityRoot Customer
- aggregate customer — EntityRoot Customer, ValueObjects Identity, Address, Repository CustomerRepository; associates EntityRoot AccountCredentials
- no Exception, CodeQLNode, Client, Property, Operation, or unstereotyped OoadClass on the DDD graph
- no inner Entity that is not a root, no DomainService, DomainEvent, Specification, Factory in this slice

BDD, UX
- this slice has no describe/it spec, no UX map
