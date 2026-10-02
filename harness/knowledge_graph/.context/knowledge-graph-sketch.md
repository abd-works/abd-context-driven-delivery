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

## Populate, then copy, then save

```
CodeQL
  root
  database
  populate
    -> storyModel.load
    -> cleanEngineeringModel.load
    -> boundedContextMap.load
    // the practice models. CodeQL does not write the knowledge-graph file

StoryModel
  // codeql channel. rows are the cursor. the model builds its own children

CleanEngineeringModel
  // codeql channel

BoundedContextMap
  // codeql channel

KnowledgeGraph
  storyModel
  ceModel
  boundedContextMap
  KnowledgeGraph storyModel ceModel boundedContextMap
    -> KnowledgeGraphStoryModel storyModel
    -> KnowledgeGraphCleanEngineeringModel ceModel
    -> KnowledgeGraphBoundedContextMap boundedContextMap
  save
    // one document. the TypeScript app loads this
  load path
    // TypeScript. reads the document from save
    // does not call CodeQL

  refreshMaster
    -> codeQL.rewriteMaster
    -> codeQL.populate
    -> KnowledgeGraph storyModel ceModel boundedContextMap
    -> save
    -> copyMasterToWorkingCopy
  updateWorkingCopy paths
    -> codeQL.extractWorkingCopy
    -> codeQL.populate
    -> KnowledgeGraph storyModel ceModel boundedContextMap
    -> save
  copyMasterToWorkingCopy
  copyWorkingCopyToMaster
```

## Knowledge-graph channel

A copy constructor. The source is the practice model CodeQL already built. Each object copies itself and constructs its children in this channel. `save` writes that tree. TypeScript `load` reads it back into the same types.

Subtypes record only the copy and the child type slots. Fields stay on the practice classes.

```
KnowledgeGraphStoryModel : StoryModel
  epicType
    // KnowledgeGraphEpic
  KnowledgeGraphStoryModel source
    // each source epic becomes a KnowledgeGraphEpic
  save
  load path
    -> loadContent
    -> loadEpics
  ----
 KnowledgeGraphEpic : Epic
      storyType
      KnowledgeGraphEpic source
        -> loadEpics
        -> loadStories
        -> loadExamples
  ----
 KnowledgeGraphStory : Story
      scenarioType
      KnowledgeGraphStory source
        -> loadScenarios
        -> loadBackgrounds
  ----
 KnowledgeGraphScenario : Scenario
      KnowledgeGraphScenario source
        -> loadBackground
        -> loadSteps
        -> loadExamples
  ----
 KnowledgeGraphBackground : Background
      KnowledgeGraphBackground source
        -> loadSteps
  ----
 KnowledgeGraphStep : Step
      KnowledgeGraphStep source
        // invokes, observes, and loads are the nodes already on the source
  ----
 KnowledgeGraphExample : Example
      KnowledgeGraphExample source
        // demonstrates is the class already on the source

KnowledgeGraphCleanEngineeringModel : CleanEngineeringModel
  moduleType
  KnowledgeGraphCleanEngineeringModel source
  save
  load path
    -> loadModules
  ----
 KnowledgeGraphModule : Module
      classType
      KnowledgeGraphModule source
        -> loadModules
        -> loadClasses
        // a child module stays a package, a bounded context, or an aggregate
  ----
 KnowledgeGraphOoadClass : OoadClass
      propertyType
      operationType
      relationshipType
      KnowledgeGraphOoadClass source
        -> loadProperties
        -> loadOperations
        -> loadRelationships
  ----
 KnowledgeGraphProperty : Property
      KnowledgeGraphProperty source
        -> loadRelationship
  ----
 KnowledgeGraphRelationship : Relationship
      KnowledgeGraphRelationship source
        // target, kind, cardinality from the source property
  ----
 KnowledgeGraphOperation : Operation
      KnowledgeGraphOperation source
        -> loadParameters
        // invokes and returns are the nodes already on the source

KnowledgeGraphBoundedContextMap : BoundedContextMap
  boundedContextType
  KnowledgeGraphBoundedContextMap source
  save
  load path
    -> loadBoundedContexts
  ----
 KnowledgeGraphBoundedContext : BoundedContext
      KnowledgeGraphBoundedContext source
        -> super.KnowledgeGraphModule
        // children are modules. an aggregate appears in the descendants
  ----
 KnowledgeGraphAggregate : Aggregate
      KnowledgeGraphAggregate source
        -> loadRoot
```

## Web

TypeScript uses these knowledge-graph classes. `load` is the channel read of the saved document. `getNext` takes the next object out of that document. The explorer asks the loaded objects for their children.

```
KnowledgeGraph
  load path
    -> storyModel.load
    -> ceModel.load
    -> boundedContextMap.load
    // path is the document save wrote
```
