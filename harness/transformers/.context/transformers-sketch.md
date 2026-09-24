fidelity: discovery / modules / bounded_context / behavior
scope: Transformer is one mix-in (like Node). model/transformation/ copies model/codeql/. A template pack is an argument to transform, not a second type. LERN templates are the first pack.
status: copy codeql mix-in and KnowledgeGraph agent marks (mcp, Skill, agent_tool)
source: practices/*/model/codeql/codeql_model.py; harness/knowledge_graph/model/graph_node.py Node; harness/knowledge_graph/model/knowledge_graph.py KnowledgeGraph; harness/guidance/rule.py Rule; practices/clean_engineering/specifications/lern_domain_driven/templates

=========
theme: Discover Solution
---------
stories:
Discover Solution
    * approx 12-16 total stories
    Human --> Provide Context
    Agent --> Write Stories Sketch
    Agent --> Write Clean Engineering Sketch
    Agent --> Write Ddd Sketch
    Agent --> Write Bdd Sketch
    Transformer --> Scaffold Story Map
    Transformer --> Scaffold Modules
    Transformer --> Scaffold Bounded Context
    Transformer --> Scaffold Bdd Behavior

ce:
harness/
  knowledge_graph                  // Node mix-in; KnowledgeGraph agent toolset
  transformers                     // Transformer mix-in and agent toolset
practices/
  stories/
    model
      codeql                       // StoryMap : SourceStoryMap, Node  (and Epic, SubEpic, Story, …)
      transformation               // StoryMap : SourceStoryMap, Transformer  (same types as codeql)
  clean_engineering/
    model
      codeql                       // CleanEngineeringModel : SourceModel, Node  (and Module, OoadClass, Operation, Property, Parameter, File)
      transformation               // CleanEngineeringModel : SourceModel, Transformer  (same types as codeql)
    specifications/
      lern_domain_driven           // templates/ passed into transform
  bdd/
    model
      codeql                       // Description : SourceDescription, Node  (and Context, Observation)
      transformation               // Description : SourceDescription, Transformer
  ddd/
    model
      codeql                       // BoundedContext : SourceBoundedContext, Node  (and Aggregate, Entity, …)
      transformation               // BoundedContext : SourceBoundedContext, Transformer

KnowledgeGraph
  refresh_master
  reload_working_copy
  create_database root
  update_working_copy paths
  return_nodes filter root
  fix_violations filter root
  // @agent_toolset domain_slug knowledge-graph
  // return_nodes: mcp Skill agent_tool
  // fix_violations: mcp Skill agent_instructions

  ----
 Transformer
      transform model
      transform model templates
          -> templates.render
      // harness/transformers — mix-in like Node; toolset like KnowledgeGraph
      // mixed only in model/transformation/, never on canonical model/ types
      // mcp Skill agent_tool on transform — same marks as return_nodes
      // templates argument is the pack — like Node.join graph
      // must not hardcode lern server, client, or view as operations
      // Node members are not a toolset — Module does not install mcp

  ----
 CleanEngineeringModel : SourceModel, Transformer
      transform model
      // practices/clean_engineering/model/transformation/ — copy codeql_model.py
      // same names as codeql: Module, OoadClass, Operation, Property, Parameter, File
      // each is (SourceType, Transformer)

  ----
 StoryMap : SourceStoryMap, Transformer
      transform model

  ----
 Description : SourceDescription, Transformer
      transform model

  ----
 BoundedContext : SourceBoundedContext, Transformer
      transform model

  ----
 LernDomainDriven : PracticeGuidance
      templates
      // first architecture pack — pass templates into Transformer.transform

bdd:
a practice model
  that mixes transformer
    it should transform that model
    it should not invent a parallel sketch type
  that has been given templates
    it should run those templates against domain logic from any practice
a transformer
  that mixes mcp skill and agent tool
    it should expose transform the way knowledge graph exposes return nodes

ddd:
Guidance
  vendor: custom
  aggregates:
    PracticeGuidance
      members:
        - StoryMap
        - CleanEngineeringModel
        - Description
        - BoundedContext
      refs:
        - Transformer (by mix-in)
        - LernDomainDriven

=========
theme: Specify Solution
---------
stories:
Specify Solution
    Transformer --> Scaffold Story Scenarios
    Transformer --> Scaffold Model
    Transformer --> Scaffold Building Blocks
    Transformer --> Scaffold Bdd Signatures

ce:
StoryMap : SourceStoryMap, Transformer
  transform model
  // markdown python typescript java javascript json drawio miro stay format channels
  // this mix-in is only in model/transformation/

  ----
 CleanEngineeringModel : SourceModel, Transformer
      transform model

  ----
 Description : SourceDescription, Transformer
      transform model

  ----
 BoundedContext : SourceBoundedContext, Transformer
      transform model

  ----
 Transformer
      transform model
      // mcp Skill agent_tool — same marks as KnowledgeGraph.return_nodes
      // must keep names from the model
      // must not invent domain semantics

bdd:
a practice model
  that has mixed transformer
    it should scaffold the next fidelity from that model
    it should keep the names from the model

ddd:
Guidance
  vendor: custom
  aggregates:
    PracticeGuidance
      refs:
        - StoryMap
        - CleanEngineeringModel
        - Description
        - BoundedContext

=========
theme: Implement Logic
---------
stories:
Implement Logic
    Transformer --> Scaffold Story Acceptance Tests
    Transformer --> Scaffold Domain Code
    Agent --> Fill Domain Bodies
    Transformer --> Scaffold Tactics
    Transformer --> Scaffold Bdd Development
    Agent --> Fill Specs

ce:
Transformer
  transform model
  // practice templates live in model/transformation/ — like .ql in model/codeql/
  // domain code skeleton has empty bodies
  // agent fills bodies — must not rename operations from the model
  // design error revises the practice sketch then regenerates

bdd:
a domain skeleton
  that the practice model has transformed
    it should leave operation bodies unimplemented
  that the agent has filled
    it should keep the public operations from the model

ddd:
Guidance
  vendor: custom
  aggregates:
    PracticeGuidance

=========
theme: Implement Tech Stack
---------
stories:
Implement Tech Stack
    Author --> Pass Lern Templates
    Transformer --> Run Tech Stack Templates
    Agent --> Fill Tech Stack Bodies

ce:
Transformer
  transform model templates
      -> templates.render
  // mcp Skill agent_tool — same marks as KnowledgeGraph.return_nodes
  // model is domain logic from any practice
  // templates are the pack — lern templates create {epicSlug}/, {domainName}.ts, {domainName}-server.ts, {domainName}-client.tsx, {EpicName}View.tsx, tests/
  // transformer does not decide those paths — the templates do

  ----
 LernDomainDriven : PracticeGuidance
      templates
      rules
      // templates consume domain logic and emit the lern target state

bdd:
a practice model
  that mixes transformer
    with lern templates
      it should run every given template
      it should write the files and folders those templates name
      it should keep domain operation names across the emitted layers

ddd:
Guidance
  vendor: custom
  aggregates:
    PracticeGuidance
      refs:
        - LernDomainDriven
      depends:
        Guidance:
          pattern: Shared Kernel
          crosses: Transformer
          integrate: Transformer.transform model templates

=========
theme: Create Tech Stack Rules And Transformers
---------
stories:
Create Tech Stack Rules And Transformers
    Author --> Describe Lern Architecture
    Author --> Write Lern Predicates
    Author --> Write Lern Transform Templates
    Author --> Improve Ddd Sketch Template

ce:
Rule
  validate
  // harness/guidance — same Rule the graph already loads
  // new architecture rules add predicates or scanners — reuse existing UL rules when they already name the constraint

  ----
 LernDomainDriven : PracticeGuidance
      templates
      rules
      describe architecture
          -> templates
          -> rules
      // templates are the guts Transformer.transform runs
      // predicates hang as Rule like other practice rules

bdd:
lern templates
  that describe the tech stack
    it should be runnable by transformer
    it should bind predicates as rules on the specification

ddd:
Guidance
  vendor: custom
  aggregates:
    PracticeGuidance
    Rule
      refs:
        - LernDomainDriven

~> Increment 1: Mix Transformer in model/transformation/ (copy codeql types) and pass LERN templates into transform: Write Clean Engineering Sketch, Scaffold Model, Scaffold Domain Code, Pass Lern Templates, Run Tech Stack Templates, Write Lern Transform Templates, Write Lern Predicates
