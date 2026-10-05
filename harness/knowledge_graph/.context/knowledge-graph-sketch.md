# Knowledge graph

CodeQL populates the practice object models. A knowledge-graph channel copies each of those models and saves, the same way JSON copies a story model and saves. TypeScript loads that save. It is the same object model. It does not run CodeQL.

CodeQL runs only to refresh master, refresh the working copy, and copy between them. Those three rebuild the practice models, copy them into the knowledge-graph channel, and save again.

```
practices/stories/model/codeql
practices/clean_engineering/model/codeql
practices/ddd/model/codeql
        |
        |  already loaded practice models
        v
practices/stories/model/knowledge_graph
practices/clean_engineering/model/knowledge_graph
practices/ddd/model/knowledge_graph
        |
        |  save
        v
harness/knowledge_graph/app          # TypeScript loads the save
```

## CodeQL.populate

One run. Node queries first, then edge queries. `PracticeGraph` registers every node row, then relates every edge row. Practice types are constructors from those rows. They do not stitch. Display sorts by `sequential_order` and nests by `immediate`.

```
CodeQL.populate(graph)
  run every node query
    clean_engineering: modules, classes, operations, properties, parameters
    stories: epics, stories, scenarios, backgrounds, steps, examples
    ddd: bounded-contexts, aggregates, entities, entity-roots, value-objects,
         repositories, domain-services, domain-events, specifications, factories
  for each node row
    node = type(semantic_type).from_row(row)
    graph.register(node)

  run every edge query  // one file per Kind
    clean_engineering: owns, belongs-to, relative, has-type, has-parameter,
                       returns, invokes, depends-on, associates, composition, aggregation
    stories: owns, belongs-to, scopes, invokes, demonstrates, demonstrated-through,
             retrieved-using, observes, uses
    ddd: owns, belongs-to, root, has-identity, accesses, associates, composition, aggregation
  for each edge row
    parent = graph.node(parent_id)
    child = graph.node(child_id)
    graph.relate(kind, parent, child, sequential_order, immediate)

children(node)
  edges from node, sorted by sequential_order
  immediate true  -> child listed under node
  immediate false -> child listed under a collapse named after kind
```

Node row: node_id, name, semantic_type, practice, file, line, end_line.

Edge row: parent_id, child_id, kind, sequential_order, immediate. Query `order by sequential_order`.

## Populate, then copy, then save

```
CodeQL
  root
  database
  populate
    -> register node rows
    -> relate edge rows
    // PracticeGraph is the structure. CodeQL does not write the knowledge-graph file

StoryModel
  // codeql channel. nodes and edges already on the graph

CleanEngineeringModel
  // codeql channel

DomainDrivenDesignModel
  // codeql channel

KnowledgeGraph
  storyModel
  ceModel
  domainDrivenDesignModel
  description
  nodes
    // parent set. every KnowledgeGraphNode from the models
  kinds
    // KnowledgeGraphEdgeType. the constrained set for the whole model
  KnowledgeGraph storyModel ceModel domainDrivenDesignModel description
    -> KnowledgeGraphStoryModel storyModel
    -> KnowledgeGraphCleanEngineeringModel ceModel
    -> KnowledgeGraphDomainDrivenDesignModel domainDrivenDesignModel
    -> KnowledgeGraphDescription description
  folder
  saveKnowledgeGraph
    -> CodeStoryModel.load
    -> CodeCleanEngineeringModel.load
    -> CodeDomainDrivenDesignModel.load
    -> KnowledgeGraphStoryModel.save
    -> KnowledgeGraphCleanEngineeringModel.save
    -> KnowledgeGraphDomainDrivenDesignModel.save
  loadKnowledgeGraph path
    -> KnowledgeGraphStoryModel.load path
    -> KnowledgeGraphCleanEngineeringModel.load path
    -> KnowledgeGraphDomainDrivenDesignModel.load path
    -> KnowledgeGraphDescription.load path

  createDatabase
    // CodeQL only. write master. copy master to working copy
    // no saveKnowledgeGraph
  refreshMaster
    -> copyWorkingCopyToMaster
    -> saveKnowledgeGraph
    -> loadKnowledgeGraph path
  reloadWorkingCopy
    // rewrite working copy from the tree
    -> saveKnowledgeGraph
    -> copyWorkingCopyToMaster
    -> loadKnowledgeGraph path
  updateWorkingCopy paths
    // extract those paths onto the working copy
    -> saveKnowledgeGraph
    -> loadKnowledgeGraph path
  copyMasterToWorkingCopy
  copyWorkingCopyToMaster
```

## Knowledge-graph channel

A copy constructor. The source is the practice model CodeQL already built. Each object copies itself and constructs its children in this channel. `save` writes that tree. TypeScript `load` reads it back into the same types.

Subtypes record only the copy and the child type slots. Fields stay on the practice classes. The mix-in is the format, like `CodeStoryNode` (`slug`) and `DiagramStoryNode` (`width`, `x`, `place`). `save` and `load` stay on the model roots, like `JsonStoryModel` and `CodeStoryModel`. A node-valued property becomes an edge. The property name picks a `KnowledgeGraphEdgeType` listed on this node's `KnowledgeGraphNodeType`. That node type is the allowed source.

```
KnowledgeGraphNodeType
  name
    // StoryModel, Epic, Increment, Story, Scenario, Background, Step, Example
    // CleanEngineeringModel, Module, Package, File, OoadClass, Property, Relationship, Operation, Parameter
    // DomainDrivenDesignModel, BoundedContext, Aggregate, Entity, EntityRoot, ValueObject, Repository, DomainEvent, DomainService, Specification, Factory
    // Description, Context, Observation
    // UxMap, Screen, Control
  practice
    // association — Stories, CleanEngineering, Ddd, Bdd
  stage
    // Discovery, Specification, Implementation
    // Story and Epic → Discovery. Step → Specification. OoadClass → Specification
  edgeTypes
    // aggregation 0..* KnowledgeGraphEdgeType
    // kinds this source may emit
  ----
KnowledgeGraphEdgeType
  name
    // owns, belongsTo, scopes, scopedBy, invokes, observes, loads, demonstrates, demonstratedThrough, retrievedUsing, uses, usedBy
    // hasType, hasParameter, returns, dependsOn, composition, aggregation, associates
    // root, accesses, hasIdentity
    // describes, namesState
  fromType
    // association KnowledgeGraphNodeType
  toType
    // association KnowledgeGraphNodeType
  inverse
    // association KnowledgeGraphEdgeType
    // owns belongsTo, demonstrates demonstratedThrough
  cardinality
    // 1, 0..1, 1..*, 0..*
  ----
KnowledgeGraphNode
  name
  sequentialOrder
  nodeType
    // association KnowledgeGraphNodeType
  source
    // composition 1 KnowledgeGraphSource. file content, always code
    // Operation, Property: KnowledgeGraphCallSource
  nodeId
  edges
    // composition 0..* KnowledgeGraphEdge
    // a node-valued property becomes one edge. the property name picks edgeType
  navigateTo edge
    // the other node on that edge
  panel
    // composition 1 KnowledgeGraphPanel
  rules
    // derived. nodeType.practice.fidelities and nodeType.practice.rules
    // practice level: nodeType.practice
    // stage level: practice.fidelity.stage == nodeType.stage
  KnowledgeGraphNode
    -> source
    -> panel.source
        // Python and TypeScript
  ----
KnowledgeGraphSource
  text
  file
  startLine
  endLine
  language
  source
    -> text from the file
  ----
KnowledgeGraphCallSource : KnowledgeGraphSource
  calls
    // composition 0..* KnowledgeGraphCall
    // line, sequentialOrder, the operation or property called
  folds
    // composition 0..* KnowledgeGraphSourceFold
  source
    -> super.source
    -> loadCalls
    -> insertCalls
    -> loadFolds
  loadCalls
    // each invoke in this operation or property
    // line, sequentialOrder, operation
  insertCalls
    // write each call into text at line, in sequentialOrder
  loadFolds
    // one fold per inserted call
    // a call to another class's operation is a call fold. call glyph
  ----
KnowledgeGraphCall
  line
  sequentialOrder
  operation
    // association KnowledgeGraphNode. the Operation or Property called
  ----
KnowledgeGraphSourceFold
  start
  end
  kind
    // call, class
    // call uses the call image
  ----
KnowledgeGraphPanel
  source
    // the node's KnowledgeGraphSource
  language
  ----
KnowledgeGraphEdge
  edgeType
    // association KnowledgeGraphEdgeType. from KnowledgeGraph.kinds
  from
    // association KnowledgeGraphNode. nodeType is edgeType.fromType
  to
    // association KnowledgeGraphNode. nodeType is edgeType.toType
    // the edge is two nodes. cardinality lives on edgeType
  ----
KnowledgeGraphStoryModel : StoryModel KnowledgeGraphNode
  epicType
    // KnowledgeGraphEpic
  incrementType
    // KnowledgeGraphIncrement
  KnowledgeGraphStoryModel source
    // each source epic becomes a KnowledgeGraphEpic
  save --> saves a complete knowledge graph
  load path
    -> loadContent
    -> loadEpics
    -> loadIncrements
  ----
 KnowledgeGraphIncrement : Increment KnowledgeGraphNode
      KnowledgeGraphIncrement source
  ----
 KnowledgeGraphEpic : Epic KnowledgeGraphNode
      storyType
      KnowledgeGraphEpic source
        -> loadEpics
        -> loadStories
        -> loadExamples
  ----
 KnowledgeGraphStory : Story KnowledgeGraphNode
      scenarioType
      KnowledgeGraphStory source
        -> loadScenarios
        -> loadBackgrounds
  ----
 KnowledgeGraphScenario : Scenario KnowledgeGraphNode
      KnowledgeGraphScenario source
        -> loadBackground
        -> loadSteps
        -> loadExamples
  ----
 KnowledgeGraphBackground : Background KnowledgeGraphNode
      KnowledgeGraphBackground source
        -> loadSteps
  ----
 KnowledgeGraphStep : Step KnowledgeGraphNode
      KnowledgeGraphStep source
        // invokes, observes, and loads are the nodes already on the source
  ----
 KnowledgeGraphExample : Example KnowledgeGraphNode
      KnowledgeGraphExample source
        // demonstrates is the class already on the source

KnowledgeGraphCleanEngineeringModel : CleanEngineeringModel KnowledgeGraphNode
  moduleType
  KnowledgeGraphCleanEngineeringModel source
  save
  load path
    -> loadModules
  ----
 KnowledgeGraphModule : Module KnowledgeGraphNode
      classType
      KnowledgeGraphModule source
        -> loadModules
        -> loadClasses
        // a child module stays a package, a bounded context, or an aggregate
  ----
 KnowledgeGraphOoadClass : OoadClass KnowledgeGraphNode
      propertyType
      operationType
      relationshipType
      KnowledgeGraphOoadClass source
        -> loadProperties
        -> loadOperations
        -> loadRelationships
  ----
 KnowledgeGraphProperty : Property KnowledgeGraphNode
      KnowledgeGraphProperty source
        -> loadRelationship
  ----
 KnowledgeGraphRelationship : Relationship KnowledgeGraphNode
      KnowledgeGraphRelationship source
        // target, kind, cardinality from the source property
  ----
 KnowledgeGraphOperation : Operation KnowledgeGraphNode
      KnowledgeGraphOperation source
        -> loadParameters
        // invokes and returns are the nodes already on the source
  ----
 KnowledgeGraphParameter : Parameter KnowledgeGraphNode
      KnowledgeGraphParameter source

KnowledgeGraphDomainDrivenDesignModel : DomainDrivenDesignModel KnowledgeGraphNode
  boundedContextType
  KnowledgeGraphDomainDrivenDesignModel source
  save
  load path
    -> loadBoundedContexts
  ----
 KnowledgeGraphBoundedContext : BoundedContext KnowledgeGraphNode
      KnowledgeGraphBoundedContext source
        -> super.KnowledgeGraphModule
        // children are modules. an aggregate appears in the descendants
  ----
 KnowledgeGraphAggregate : Aggregate KnowledgeGraphNode
      KnowledgeGraphAggregate source
        -> loadRoot
  ----
 KnowledgeGraphEntity : Entity KnowledgeGraphNode
      KnowledgeGraphEntity source
        -> loadProperties
        -> loadOperations
  ----
 KnowledgeGraphEntityRoot : Entity KnowledgeGraphNode
      KnowledgeGraphEntityRoot source
        -> loadProperties
        -> loadOperations
  ----
 KnowledgeGraphValueObject : ValueObject KnowledgeGraphNode
      KnowledgeGraphValueObject source
        -> loadProperties
        -> loadOperations
  ----
 KnowledgeGraphRepository : Repository KnowledgeGraphNode
      KnowledgeGraphRepository source
        -> loadProperties
        -> loadOperations
  ----
 KnowledgeGraphDomainEvent : DomainEvent KnowledgeGraphNode
      KnowledgeGraphDomainEvent source
        -> loadProperties
        -> loadOperations
  ----
 KnowledgeGraphDomainService : DomainService KnowledgeGraphNode
      KnowledgeGraphDomainService source
        -> loadProperties
        -> loadOperations
  ----
 KnowledgeGraphSpecification : Specification KnowledgeGraphNode
      KnowledgeGraphSpecification source

KnowledgeGraphDescription : Description KnowledgeGraphNode
  KnowledgeGraphDescription source
    -> loadContexts
  ----
 KnowledgeGraphContext : Context KnowledgeGraphNode
      KnowledgeGraphContext source
        -> loadObservations
        -> loadContexts
  ----
 KnowledgeGraphObservation : Observation KnowledgeGraphNode
      KnowledgeGraphObservation source
```

## Web

TypeScript loads the knowledge graph these classes saved. The browser and the server each have the same object model — the same types, nodes, edges, and kinds.

The live TypeScript `KnowledgeGraph` holds the same objects. A node's `source` is `KnowledgeGraphSource` — file content, always code. Operation and Property use `KnowledgeGraphCallSource`. The panel host is Monaco.

The graph holds the parent set of nodes. Those nodes hold the edges. `filter` selects a subset of that parent set.

```
KnowledgeGraph
  folder
  nodes
    // parent set. every KnowledgeGraphNode from the save
  filter
    // composition 0..* KnowledgeGraphFilter
  matching
    // aggregation. the nodes that match filter. still those nodes
  saveKnowledgeGraph
    -> CodeStoryModel.load
    -> CodeCleanEngineeringModel.load
    -> CodeDomainDrivenDesignModel.load
    -> KnowledgeGraphStoryModel.save
    -> KnowledgeGraphCleanEngineeringModel.save
    -> KnowledgeGraphDomainDrivenDesignModel.save
  loadKnowledgeGraph path
    -> KnowledgeGraphStoryModel.load path
    -> KnowledgeGraphCleanEngineeringModel.load path
    -> KnowledgeGraphDomainDrivenDesignModel.load path
    -> KnowledgeGraphDescription.load path
  selected
    // association KnowledgeGraphNode. changes when a node is chosen
  expanded
    // aggregation 0..* KnowledgeGraphNode. changes as branches open and close
  createDatabase
    // CodeQL only. master, then copy to working copy
  refreshMaster
    -> copyWorkingCopyToMaster
    -> saveKnowledgeGraph
    -> loadKnowledgeGraph path
  reloadWorkingCopy
    // rewrite working copy from the tree
    -> saveKnowledgeGraph
    -> copyWorkingCopyToMaster
    -> loadKnowledgeGraph path
  updateWorkingCopy paths
    // extract onto working copy
    -> saveKnowledgeGraph
    -> loadKnowledgeGraph path
  ----
KnowledgeGraphFilter
  type
    // Practice, Stage, Node, Relationship, RuleSet, Rule
  selected
    // the chosen values of that type
  available
    // filled once from the path parameters
  KnowledgeGraphFilter practices
    -> StageFilter.available practices
    -> NodeFilter.available practices stages
    -> RelationshipFilter.available nodes
    -> RuleSetFilter.available
    -> RuleFilter.available nodes
  ----
PracticeFilter : KnowledgeGraphFilter
  selected
    // Stories, CleanEngineering, Ddd, Bdd
  available
    // practices on this graph
  ----
StageFilter : KnowledgeGraphFilter
  selected
    // Discovery, Specification, Implementation
  available practices
    // NodeType.stage on those practices
  ----
NodeFilter : KnowledgeGraphFilter
  selected
    // aggregation 0..* KnowledgeGraphNodeType
  available practices stages
    // NodeType whose practice and stage are on the path
  ----
RelationshipFilter : KnowledgeGraphFilter
  selected
    // aggregation 0..* KnowledgeGraphEdgeType
  available nodes
    // edgeTypes on the selected node types
  ----
RuleSetFilter : KnowledgeGraphFilter
  selected
    // base, project
  available
    // base, project
  ----
RuleFilter : KnowledgeGraphFilter
  selected
    // aggregation 0..* practice.rules
  available nodes
    // rules on the selected node types
```
KnowledgeGraphPanel
  open
  theme
  mount
    // Monaco. folding glyphs, expand, collapse
  ----
WebKnowledgeGraphNode : KnowledgeGraphNode
  keyword
  origin
    // association SourceRange. the owning class or file when source is a member
  properties
    // folder and other scalars the tree already shows
  isFile
  isFolder
  ----
PracticeGraph
  id
  name
    // the practice
  nodes
    // aggregation 0..* KnowledgeGraphNode
  relationships
    // aggregation 0..* KnowledgeGraphEdge
  ----
SourceRange
  file
  startLine
  endLine
  text
  ----
RuleHit
  ruleSlug
  message
  body
  practice
  fidelity
  tag
  ----
NodeRules
  applicable
  violations
    // aggregation 0..* RuleHit
  statuses
  status ruleSlug
  hasRule ruleSlug
  details
  tally
  ----
WorkspaceFile
  relativePath
  text
```

## Tests

Fidelity: behavior

a story map
  from a channel
    to knowledge graph
      it behaves like a story map saved through a channel

a class model
  from a channel
    to knowledge graph
      it behaves like a class model saved through a channel

a domain driven design model
  from a channel
    to knowledge graph
      it behaves like a domain driven design model saved through a channel
        // promote check_map into that shared context first

a knowledge graph
  that has been saved
    -> saveKnowledgeGraph
      -> CodeStoryModel.load
      -> CodeCleanEngineeringModel.load
      -> CodeDomainDrivenDesignModel.load
      -> KnowledgeGraphStoryModel.save
      -> KnowledgeGraphCleanEngineeringModel.save
      -> KnowledgeGraphDomainDrivenDesignModel.save
    it should write the knowledge graph models
  that has been loaded from a path
    -> loadKnowledgeGraph path
      -> KnowledgeGraphStoryModel.load path
      -> KnowledgeGraphCleanEngineeringModel.load path
      -> KnowledgeGraphDomainDrivenDesignModel.load path
      -> KnowledgeGraphDescription.load path
    it should rebuild the nodes from that document
  that has created a database
    -> createDatabase
    it should write master
    it should copy master to the working copy
  that has refreshed the master
    -> refreshMaster
      -> copyWorkingCopyToMaster
      -> saveKnowledgeGraph
      -> loadKnowledgeGraph path
    it should be the document that was just saved
  that has reloaded the working copy
    -> reloadWorkingCopy
      -> saveKnowledgeGraph
      -> copyWorkingCopyToMaster
      -> loadKnowledgeGraph path
    it should be the document that was just saved
  that has updated the working copy
    with dirty paths
      -> updateWorkingCopy paths
        -> saveKnowledgeGraph
        -> loadKnowledgeGraph path
      it should be the document that was just saved
  with selected practices
    -> KnowledgeGraphFilter practices
    it should fill available stages from those practices
    it should fill available node types from those practices and stages
    with selected node types
      it should fill available relationships from those nodes
      it should fill available rules from those nodes
    with a rule set
      it should offer base and project
  with a chosen node
    it should hold that node as selected
  with open branches
    it should hold those nodes as expanded

an operation
  that has source
    -> source
      -> super.source
      -> loadCalls
      -> insertCalls
      -> loadFolds
    it should load each call at its line and order
    it should insert those calls into the text
    it should fold each inserted call
  that calls another class's operation
    it should use the call glyph

a property
  that has source
    it behaves like an operation that has source




