fidelity: discovery / modules / bounded_context / behavior
scope: Transformer mixes onto existing practice models (same pattern as Node). TechStackTransformer runs a passed template pack against any practice's domain logic. LERN templates are the first pack.
status: mistakes carried — graph-style model extension; tech stack guts are templates not hardcoded lern stories
source: practices/*/model/codeql/codeql_model.py Node mix-in; practices/clean_engineering/specifications/lern_domain_driven/templates

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
  knowledge_graph                  // Node mixed into practice models
  transformers                     // Transformer mixed the same way; TechStackTransformer runs templates
practices/
  stories/
    model                          // StoryMap mixes Node today; mixes Transformer for sketch-to-domain-logic
    transformation                 // templates for that transform — not a second model
  clean_engineering/
    model                          // CleanEngineeringModel mixes Node today; mixes Transformer
    transformation
    specifications/
      lern_domain_driven           // existing PracticeGuidance; templates/ are a pack passed to TechStackTransformer
  bdd/
    model                          // Description mixes Node today; mixes Transformer
    transformation
  ddd/
    model                          // BoundedContext / Entity mix Node today; mix Transformer
    transformation

Transformer
  model
  transform model
  // mixed into the live practice model — wrap or extend, do not scrape a parallel type
  // same pattern as Node on StoryMap, CleanEngineeringModel, Description, BoundedContext
  // never owns the template pack — files sit beside the practice model or on a specification

  ----
 TechStackTransformer : Transformer
      templates
      transform model templates
          -> templates.render
      // takes domain logic from any practice model
      // runs every template in the pack — files and folders come from the templates
      // must not hardcode lern server, client, or view as operations

  ----
 LernDomainDriven : PracticeGuidance
      templates
      // first architecture pack — pass templates into TechStackTransformer

bdd:
a practice model
  that mixes transformer
    it should transform that model
    it should not invent a parallel sketch type
a tech stack transformer
  that has been given templates
    it should run those templates against domain logic from any practice

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
        - TechStackTransformer
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
StoryMap
  transform
  // mixes Transformer — markdown python typescript java javascript json drawio miro stay format channels

  ----
 CleanEngineeringModel
      transform

  ----
 Description
      transform

  ----
 BoundedContext
      transform

  ----
 Transformer
      transform model
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
  // uses the practice transformation templates
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
TechStackTransformer : Transformer
  templates
  transform model templates
      -> templates.render
  // model is domain logic from any practice
  // templates are the pack — lern templates create {epicSlug}/, {domainName}.ts, {domainName}-server.ts, {domainName}-client.tsx, {EpicName}View.tsx, tests/
  // transformer does not decide those paths — the templates do

  ----
 LernDomainDriven : PracticeGuidance
      templates
      rules
      // modified so its templates consume domain logic and emit the lern target state

bdd:
a tech stack transformer
  that has been given lern templates
    with domain logic from a practice model
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
          crosses: Transformer, TechStackTransformer
          integrate: TechStackTransformer.transform model templates

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
GraphRule : Rule
  predicate
  validate
  // new architecture rules add new predicates — reuse existing UL predicates when they already name the constraint

  ----
 LernDomainDriven : PracticeGuidance
      templates
      rules
      describe architecture
          -> templates
          -> rules
      // templates are the guts the TechStackTransformer runs
      // predicates hang as GraphRule like other practice rules

bdd:
lern templates
  that describe the tech stack
    it should be runnable by the tech stack transformer
    it should bind predicates as graph rules on the specification

ddd:
Guidance
  vendor: custom
  aggregates:
    PracticeGuidance
    Rule
      refs:
        - LernDomainDriven

~> Increment 1: Mix Transformer onto practice models and run LERN templates through TechStackTransformer: Write Clean Engineering Sketch, Scaffold Model, Scaffold Domain Code, Pass Lern Templates, Run Tech Stack Templates, Write Lern Transform Templates, Write Lern Predicates
