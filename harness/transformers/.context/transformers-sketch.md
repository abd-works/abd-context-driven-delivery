fidelity: discovery / modules / bounded_context / behavior
scope: Transformer is the mix-in (like Node). Transformers is the agent toolset (like KnowledgeGraph). model/transformation/ copies model/codeql/ as {Source}Transformer types listed by family. Transformers.transform sketch -> practiceModels[] (family roots and nested transformers). transform logic writes files the pack names. A template pack is an argument to transform logic, not a second type. LERN templates are the first pack.
status: copy codeql types as TypeTransformer; put KnowledgeGraph agent marks on Transformers only
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
      transformation               // BoundedContextTransformer, AggregateTransformer, EntityTransformer, EntityRootTransformer, ValueObjectTransformer, RepositoryTransformer, DomainEventTransformer, DomainServiceTransformer

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
      // harness/transformers — mix-in like Node.join; no mcp Skill agent_tool
      // mixed only onto *Transformer types in model/transformation/, never on canonical model/ types
      // the node is the data a template binds — name, members, children
      // *Transformer members are not a toolset — ModuleTransformer does not install mcp

  ----
 Transformers
      transform sketch -> practiceModels[]
      transform logic templates
          -> templates.render
      // @agent_toolset domain_slug like KnowledgeGraph
      // both operations: mcp Skill agent_tool — same marks as return_nodes
      // theme Discover Solution — starts
      // practiceModels[] family roots when those sections are in the sketch:
      //   StoryMapTransformer, CleanEngineeringTransformer, DescriptionTransformer, BoundedContextTransformer
      // nested transformers belong on those roots — not a second bag of “practice models”
      // theme Specify Solution
      // must keep names from the sketch
      // must not invent domain semantics
      // start at the given node — do not require the whole model
      // theme Implement Logic
      // practice templates live in model/transformation/ — like .ql in model/codeql/
      // OoadClassTransformer operations become domain skeleton with empty bodies
      // agent fills bodies — must not rename operations from CleanEngineeringTransformer
      // design error revises the practice sketch then regenerates
      // theme Implement Tech Stack
      // transform logic writes the files and folders the pack names
      // logic is filled domain from CleanEngineeringTransformer, start at the given node
      // templates are the pack — lern templates create {epicSlug}/, {domainName}.ts, {domainName}-server.ts, {domainName}-client.tsx, {EpicName}View.tsx, tests/
      // Transformers does not decide those paths — the templates do
      // theme Implement Tech Stack — ends
      // templates argument is the pack — like Node.join graph
      // must not hardcode lern server, client, or view as operations

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
      // these are the transformer objects, not StoryMap / Epic without the suffix
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
      // these are the transformer objects, not CleanEngineeringModel / Module / OoadClass
      // theme Discover Solution — starts
      // theme Implement Logic
      // OoadClassTransformer operations are the domain skeleton
      // theme Implement Tech Stack
      // filled logic is the start node for transform logic
      // theme Implement Tech Stack — ends

  ----
 DescriptionTransformer : Description, Transformer
      ContextTransformer
      ObservationTransformer
      // practices/bdd/model/transformation/ — wrap each bdd/model/codeql type
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
      // practices/ddd/model/transformation/ — wrap each ddd/model/codeql type
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
a story map transformer
  that comes from a stories sketch
    it should include an epic transformer
    it should include a sub epic transformer
    it should include a story transformer
    it should include a scenario transformer
    it should include a background transformer
    it should include a step transformer
    it should include an example transformer
    it should not be an agent tool
  that has been specified
    it should keep names from the sketch
    it should be among the models transform sketch returns

a clean engineering transformer
  that comes from a clean engineering sketch
    it should include a module transformer
    it should include a file transformer
    it should include a class transformer
    it should include an operation transformer
    it should include a property transformer
    it should include a parameter transformer
    it should not be an agent tool
  that has been specified
    it should keep names from the sketch
    it should be among the models transform sketch returns
  that has filled domain logic
    with lern templates
      it should run every given template
      it should write the files and folders those templates name
      it should keep class operation names across the emitted layers

a description transformer
  that comes from a bdd sketch
    it should include a context transformer
    it should include an observation transformer
    it should not be an agent tool
  that has been specified
    it should be among the models transform sketch returns

a bounded context transformer
  that comes from a ddd sketch
    it should include an aggregate transformer
    it should include an entity transformer
    it should include an entity root transformer
    it should include a value object transformer
    it should include a repository transformer
    it should include a domain event transformer
    it should include a domain service transformer
    it should not be an agent tool
  that has been specified
    it should be among the models transform sketch returns

transformers
  that an agent can invoke
    it should transform a sketch into the transformer family roots from that sketch
    it should transform filled logic with a template pack
    it should start at the given node

a domain skeleton
  that a clean engineering transformer produced
    it should leave operation bodies unimplemented
  that the agent has filled
    it should keep the public operations from the class transformer

lern templates
  that describe the tech stack
    it should be runnable when transforming filled logic
    it should bind predicates as rules on the specification

ddd:
Guidance
  vendor: custom
  aggregates:
    PracticeGuidance
      members:
        - StoryMapTransformer
        - CleanEngineeringTransformer
        - DescriptionTransformer
        - BoundedContextTransformer
      refs:
        - Transformer (by mix-in)
        - Transformers
        - LernDomainDriven
      depends:
        Guidance:
          pattern: Shared Kernel
          crosses: Transformers
          integrate: Transformers.transform logic templates
    Rule
      refs:
        - LernDomainDriven

~> Increment 1: Mix Transformer onto *Transformer types in model/transformation/ (copy every codeql type in each family); Transformers.transform sketch -> practiceModels[] of those family roots; Transformers.transform logic with LERN templates writes those template paths: Write Clean Engineering Sketch, Scaffold Model, Scaffold Domain Code, Pass Lern Templates, Run Tech Stack Templates, Write Lern Transform Templates, Write Lern Predicates
