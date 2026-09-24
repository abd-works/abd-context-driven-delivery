fidelity: discovery / modules / behavior
scope: Transformer is the mix-in (like Node). Transformers is the agent toolset (like KnowledgeGraph). model/transformation/ wraps each codeql type as {Source}Transformer — bind to a logical Jinja template and recurse, not a second iterator. Transformers.transform sketch loads that channel from the sketch then render "logical" on the loaded root. Transformers.transform logic renders a passed pack (LERN first) against filled logic.
status: wrap codeql types as TypeTransformer; Transformers holds the agent marks; Transformer.render looks up templates
source: practices/*/model/codeql/codeql_model.py; harness/knowledge_graph/model/graph_node.py Node; harness/knowledge_graph/model/knowledge_graph.py KnowledgeGraph; harness/guidance/rule.py Rule; practices/clean_engineering/specifications/lern_domain_driven/templates

stories:
Discover Solution
    * approx 12-16 total stories
    Human --> Provide Context
    Agent --> Write Stories Sketch
    Agent --> Write Clean Engineering Sketch
    Agent --> Write Ddd Sketch
    Agent --> Write Bdd Sketch
    Transformers --> Scaffold Story Map
    Transformers --> Scaffold Modules
    Transformers --> Scaffold Bounded Context
    Transformers --> Scaffold Bdd Behavior
Specify Solution
    Transformers --> Scaffold Story Scenarios
    Transformers --> Scaffold Model
    Transformers --> Scaffold Building Blocks
    Transformers --> Scaffold Bdd Signatures
Implement Logic
    Transformers --> Scaffold Story Acceptance Tests
    Transformers --> Scaffold Domain Code
    Agent --> Fill Domain Bodies
    Transformers --> Scaffold Tactics
    Transformers --> Scaffold Bdd Development
    Agent --> Fill Specs
Implement Tech Stack
    Author --> Pass Lern Templates
    Transformers --> Run Tech Stack Templates
    Agent --> Fill Tech Stack Bodies
Create Tech Stack Rules And Transformers
    Author --> Describe Lern Architecture
    Author --> Write Lern Predicates
    Author --> Write Lern Transform Templates
    Author --> Improve Ddd Sketch Template

ce:
harness/
  knowledge_graph                  // Node mix-in; KnowledgeGraph agent toolset
  transformers                     // Transformer mix-in; Transformers agent toolset
practices/
  stories/
    model
      codeql                       // StoryMap, Epic, SubEpic, Story, Scenario, Background, Step, Example : Source, Node
      transformation               // StoryMapTransformer, EpicTransformer, SubEpicTransformer, StoryTransformer, ScenarioTransformer, BackgroundTransformer, StepTransformer, ExampleTransformer
  clean_engineering/
    model
      codeql                       // CleanEngineeringModel, Module, File, OoadClass, Operation, Property, Parameter : Source, Node
      transformation               // CleanEngineeringTransformer, ModuleTransformer, FileTransformer, OoadClassTransformer, OperationTransformer, PropertyTransformer, ParameterTransformer
    specifications/
      lern_domain_driven           // templates/ passed into Transformers.transform logic
  bdd/
    model
      codeql                       // Description, Context, Observation : Source, Node
      transformation               // DescriptionTransformer, ContextTransformer, ObservationTransformer
  ddd/
    model
      codeql                       // BoundedContext, Aggregate, Entity, EntityRoot, ValueObject, Repository, DomainEvent, DomainService : Source, Node
      transformation               // BoundedContextTransformer, AggregateTransformer, EntityTransformer, EntityRootTransformer, ValueObjectTransformer, RepositoryTransformer, DomainEventTransformer, DomainServiceTransformer, SpecificationTransformer, FactoryTransformer

KnowledgeGraph
  refresh_master
  reload_working_copy
  create_database root
  update_working_copy paths
  return_nodes filter root
  get_fix_violation_instructions filter root
  // @agent_toolset domain_slug knowledge-graph
  // return_nodes: mcp Skill agent_tool
  // get_fix_violation_instructions: mcp Skill agent_instructions

  ----
 Transformer
      children
      getTemplatesFor kind
      render kind
          -> templates = getTemplatesFor kind
          -> if templates
              -> for each template
                  -> template.render this
          -> else keep rendering
      // mix-in on *Transformer types in model/transformation/ — not an agent toolset
      // this practice's tree is enough — signatures come from this sketch, not from related practices
      // only place that looks up templates that hang on this node
      // templates call children; child.render kind if that child has templates for kind, else the template keeps rendering
      // template.render this: this node is the Jinja context

  ----
 Transformers
      transform sketch -> practiceModels[]
          -> Jinja LoadEnvironment
          -> practices = determinePracticesFrom sketch
          -> for each practice
              -> transformerNode = practice.model.transformer.load(sketch)
              -> transformerNode.render "logical"
      transform logic templates
          -> start at filled logic node
          -> for each template
              -> template.render filled logic node
      // @agent_toolset domain_slug like KnowledgeGraph
      // transform sketch, transform logic: mcp Skill agent_tool — same marks as return_nodes
      // Jinja LoadEnvironment once
      // practice.model.transformer.load(sketch): that practice's transformer channel parses the sketch — same seam as markdown/python parse
      // transform sketch starts render "logical" on that loaded root — getTemplatesFor stays on Transformer
      // transform logic: LERN pack is the argument — those templates are not on the node, so Transformers renders the pack against the filled node
      // practiceModels[] is the loaded transformerNode roots
      // cross-practice joins deferred

  ----
 StoryMapTransformer : StoryMap, Transformer
      EpicTransformer
      SubEpicTransformer
      StoryTransformer
      ScenarioTransformer
      BackgroundTransformer
      StepTransformer
      ExampleTransformer
      // practices/stories/model/transformation/ — wrap each stories/model/codeql type
      // EpicTransformer: folder template; StoryTransformer: language file; ScenarioTransformer BackgroundTransformer StepTransformer ExampleTransformer: no file — story template keeps rendering
      // theme Discover Solution — starts
      // theme Specify Solution
      // markdown python typescript java javascript json drawio miro stay format channels
      // theme Specify Solution — ends

  ----
 CleanEngineeringTransformer : CleanEngineeringModel, Transformer
      ModuleTransformer
      FileTransformer
      OoadClassTransformer
      OperationTransformer
      PropertyTransformer
      ParameterTransformer
      // practices/clean_engineering/model/transformation/ — wrap each clean_engineering/model/codeql type
      // ModuleTransformer: folder; FileTransformer OoadClassTransformer: language file; OperationTransformer PropertyTransformer ParameterTransformer: no file unless it has a logical template — parent keeps rendering
      // theme Discover Solution — starts
      // theme Implement Logic
      // OoadClassTransformer operations are the domain skeleton
      // theme Implement Tech Stack
      // filled logic is the start node for transform logic — pack argument, not getTemplatesFor
      // theme Implement Tech Stack — ends

  ----
 DescriptionTransformer : Description, Transformer
      ContextTransformer
      ObservationTransformer
      // practices/bdd/model/transformation/ — wrap each bdd/model/codeql type
      // DescriptionTransformer: language file; ContextTransformer ObservationTransformer: no file — description template keeps rendering
      // theme Discover Solution — starts
      // theme Specify Solution — signatures stay on DescriptionTransformer / ContextTransformer / ObservationTransformer
      // theme Specify Solution — ends

  ----
 BoundedContextTransformer : BoundedContext, Transformer
      AggregateTransformer
      EntityTransformer
      EntityRootTransformer
      ValueObjectTransformer
      RepositoryTransformer
      DomainEventTransformer
      DomainServiceTransformer
      SpecificationTransformer
      FactoryTransformer
      // practices/ddd/model/transformation/ — wrap each ddd/model/codeql type
      // BoundedContextTransformer: module annotated as bounded context
      // AggregateTransformer: module folder — not a class named Aggregate
      // that folder holds the root entity, its entities and value objects, and the repository
      // DomainEventTransformer DomainServiceTransformer SpecificationTransformer FactoryTransformer optional in that folder
      // EntityRootTransformer: <<Aggregate Root>> <<Entity>> and identifier; EntityTransformer: <<Entity>> and identifier
      // RepositoryTransformer: <<Repository>> in the aggregate folder, named for the root — add remove update, search only by identity, plus find by / new / search from the sketch
      // EntityTransformer owns OperationTransformer PropertyTransformer like codeql Entity uses CE members
      // theme Discover Solution — starts
      // theme Specify Solution — building blocks stay on these types
      // theme Specify Solution — ends

  ----
 LernDomainDriven : PracticeGuidance
      templates
      rules
      describe architecture
          -> templates
          -> rules
      // theme Discover Solution — first architecture pack — pass templates into Transformers.transform logic
      // theme Implement Tech Stack — templates consume domain logic and emit the lern target state
      // theme Create Tech Stack Rules And Transformers — templates are the guts Transformers.transform logic runs
      // predicates hang as Rule like other practice rules

  ----
 Rule
      validate
      // theme Create Tech Stack Rules And Transformers
      // harness/guidance — same Rule the graph already loads
      // new architecture rules add predicates or scanners — reuse existing UL rules when they already name the constraint

bdd:
a sketch
  that has been transformed
    with clean engineering
      it should return a clean engineering transformer
      it should keep names from the sketch
    with stories
      it should return a story map transformer
    with bdd
      it should return a description transformer
    with domain driven design
      it should return a bounded context transformer

shared_examples "story map from the sketch"
  it should create the epics from the sketch
  with nested sub epics
    it should nest the sub epics in those epics
    with stories
      it should nest the stories in those sub epics
      with nested stories
        it should nest the nested stories in those stories
      with backgrounds
        it should nest the backgrounds in those stories
      with scenarios
        it should nest the scenarios in those stories
        with nested scenarios
          it should nest the nested scenarios in those scenarios
        with steps
          it should nest the steps in those scenarios
        with examples
          it should nest the examples in those scenarios
  with stories
    it should nest the stories in those epics

a story map
  that a story map transformer produced
    in markdown
      it_behaves_like "story map from the sketch"
      it should transform to markdown
    in python
      it_behaves_like "story map from the sketch"
      it should transform to python
    in typescript
      it_behaves_like "story map from the sketch"
      it should transform to typescript
    in java
      it_behaves_like "story map from the sketch"
      it should transform to java
    in javascript
      it_behaves_like "story map from the sketch"
      it should transform to javascript
    in json
      it_behaves_like "story map from the sketch"
      it should transform to json
    in drawio
      it_behaves_like "story map from the sketch"
      it should transform to drawio
    in miro
      it_behaves_like "story map from the sketch"
      it should transform to miro

shared_examples "clean engineering model from the sketch"
  it should create the modules from the sketch
  with files
    it should nest the files in those modules
  with ooad classes
    it should nest the ooad classes in those modules
    with operations
      it should nest the operations in those ooad classes
      with parameters
        it should nest the parameters in those operations
      with return types
        it should nest the return types in those operations
      it should leave those operation bodies unimplemented
    with properties
      it should nest the properties in those ooad classes
  with nested modules
    it should nest the nested modules in those modules
    with nested modules
      it should nest the nested modules in those nested modules
    with ooad classes
      it should nest the ooad classes in those nested modules
      with operations
        it should nest the operations in those ooad classes
        with parameters
          it should nest the parameters in those operations
        with return types
          it should nest the return types in those operations
        it should leave those operation bodies unimplemented
      with properties
        it should nest the properties in those ooad classes

a clean engineering model
  that a clean engineering transformer produced
    in markdown
      it_behaves_like "clean engineering model from the sketch"
      it should transform to markdown
    in python
      it_behaves_like "clean engineering model from the sketch"
      it should transform to python
    in typescript
      it_behaves_like "clean engineering model from the sketch"
      it should transform to typescript
    in java
      it_behaves_like "clean engineering model from the sketch"
      it should transform to java
    in javascript
      it_behaves_like "clean engineering model from the sketch"
      it should transform to javascript
    in json
      it_behaves_like "clean engineering model from the sketch"
      it should transform to json
    in drawio
      it_behaves_like "clean engineering model from the sketch"
      it should transform to drawio
    in miro
      it_behaves_like "clean engineering model from the sketch"
      it should transform to miro
  that the agent has filled
    it should keep those ooad class transformer operation names
  that is a domain sketch
    it_behaves_like "bounded contexts from the sketch"

shared_examples "bounded contexts from the sketch"
  it should create the bounded contexts from the sketch
  it should express those bounded contexts as modules
  it should annotate those modules as bounded contexts
  it should keep the vendor on those bounded contexts
  with nested bounded contexts
    it should nest the nested bounded contexts in those bounded contexts
  with aggregates
    it should nest the aggregates in those bounded contexts
    it should express those aggregates as modules
    with nested aggregates
      it should nest the nested aggregates in those aggregates
    with a root entity
      it should nest the root entity in those aggregate modules
      it should annotate those classes as aggregate root
      it should annotate those classes as entity
      it should tag the unique identifier on those classes
    with entities
      it should nest the entities in those aggregate modules
      it should annotate those classes as entity
      it should tag the unique identifier on those entities
      with nested entities
        it should nest the nested entities in those entities
    with value objects
      it should nest the value objects in those aggregate modules
      it should annotate those classes as value object
    with repositories
      it should nest the repositories in those aggregate modules
      it should annotate those classes as repository
      it should name those repositories after the aggregate root
      it should serve only the aggregate root from those repositories
      it should search those repositories only by identity
      it should nest add on those repositories
      it should nest remove on those repositories
      it should nest update on those repositories
      with find by criteria from the sketch
        it should nest those find by operations on those repositories
      with new from the sketch
        it should nest those new operations on those repositories
      with search from the sketch
        it should nest those search operations on those repositories
    without an independent lookup
      it should omit a repository
    with domain events
      it should nest the domain events in those aggregate modules
      it should annotate those classes as domain event
      it should keep past tense names on those domain events
      it should nest the consumers from the sketch on those domain events
    with domain services
      it should nest the domain services in those aggregate modules
      it should annotate those classes as domain service
    with specifications
      it should nest the specifications in those aggregate modules
    with factories
      it should nest the factories in those aggregate modules
    with emits from the sketch
      it should nest those events on those aggregates
    with consumes from the sketch
      it should nest those events on those aggregates
    with depends from the sketch
      it should nest those dependencies on those aggregates
    with refs from the sketch
      it should nest those refs by identity on those aggregates
    with invariants from the sketch
      it should nest those invariants on those classes
  with an event map
    it should keep the event map from the sketch
  it should classify every named type from the sketch

a bounded context
  that a bounded context transformer produced
    in markdown
      it_behaves_like "bounded contexts from the sketch"
      it should transform to markdown
    in python
      it_behaves_like "bounded contexts from the sketch"
      it should transform to python
    in typescript
      it_behaves_like "bounded contexts from the sketch"
      it should transform to typescript
    in java
      it_behaves_like "bounded contexts from the sketch"
      it should transform to java
    in javascript
      it_behaves_like "bounded contexts from the sketch"
      it should transform to javascript
    in json
      it_behaves_like "bounded contexts from the sketch"
      it should transform to json
    in drawio
      it_behaves_like "bounded contexts from the sketch"
      it should transform to drawio
    in miro
      it_behaves_like "bounded contexts from the sketch"
      it should transform to miro

shared_examples "description from the sketch"
  it should create the contexts from the sketch
  with nested contexts
    it should nest the nested contexts in those contexts
    with observations
      it should nest the observations in those nested contexts
  with observations
    it should nest the observations in those contexts

a description
  that a description transformer produced
    in markdown
      it_behaves_like "description from the sketch"
      it should transform to markdown
    in python
      it_behaves_like "description from the sketch"
      it should transform to python
    in typescript
      it_behaves_like "description from the sketch"
      it should transform to typescript
    in java
      it_behaves_like "description from the sketch"
      it should transform to java
    in javascript
      it_behaves_like "description from the sketch"
      it should transform to javascript
    in json
      it_behaves_like "description from the sketch"
      it should transform to json
    in drawio
      it_behaves_like "description from the sketch"
      it should transform to drawio
    in miro
      it_behaves_like "description from the sketch"
      it should transform to miro

filled domain logic
  with lern templates
    that has been transformed
      it should write the epic slug folder those templates name
      it should write the domain typescript those templates name
      it should write the domain server those templates name
      it should write the domain client those templates name
      it should write the view those templates name
      it should write the tests folder those templates name
      it should keep ooad class transformer operation names across the emitted layers

templates that describe the tech stack
  that have been written
    it should bind predicates as rules on the specification

~> Increment 1: logical story map in python from the sketch: Scaffold Story Map
~> Increment 2: logical clean engineering model in python from the sketch: Scaffold Modules
~> Increment 3: logical domain driven model in python from the sketch: Scaffold Bounded Context
~> Increment 4: logical bdd in python from the sketch: Scaffold Bdd Behavior
~> Increment 5: logical markdown from the sketch: Scaffold Story Map, Scaffold Modules, Scaffold Bounded Context, Scaffold Bdd Behavior
~> Increment 6: logical typescript from the sketch: Scaffold Story Map, Scaffold Modules, Scaffold Bounded Context, Scaffold Bdd Behavior
~> Increment 7: logical java from the sketch: Scaffold Story Map, Scaffold Modules, Scaffold Bounded Context, Scaffold Bdd Behavior
~> Increment 8: logical javascript from the sketch: Scaffold Story Map, Scaffold Modules, Scaffold Bounded Context, Scaffold Bdd Behavior
~> Increment 9: logical json from the sketch: Scaffold Story Map, Scaffold Modules, Scaffold Bounded Context, Scaffold Bdd Behavior
~> Increment 10: logical drawio from the sketch: Scaffold Story Map, Scaffold Modules, Scaffold Bounded Context, Scaffold Bdd Behavior
~> Increment 11: logical miro from the sketch: Scaffold Story Map, Scaffold Modules, Scaffold Bounded Context, Scaffold Bdd Behavior
// stop — sketch LERN to logical model mapping before coding
~> Increment 12: tech stack LERN from logical models: Pass Lern Templates, Run Tech Stack Templates
// stop — sketch how cross model works
~> Increment 13: logical place clean engineering into scenarios: Scaffold Story Scenarios
~> Increment 14: logical place clean engineering into acceptance tests: Scaffold Story Acceptance Tests
~> Increment 15: logical place clean engineering into bdd tests: Scaffold Bdd Signatures, Scaffold Bdd Development
~> Increment 16: logical add missing info
