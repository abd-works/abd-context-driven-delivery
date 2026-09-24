# Grill Answers

### Active sketch lenses

Stories, Clean Engineering, and BDD stay in the transformers sketch — each already has a usable sketch template. DDD is in because its sketch template needs to improve so a later transform can consume it. UX is out for now; other practices wait.

### Fidelity-shaped transform epics

Stories follow fidelity, not a single sketch-to-architecture pipe: Human provides context; Agent writes each practice sketch; Transformer scaffolds that practice’s next fidelity (Stories: map then scenarios then acceptance tests; CE and DDD interspersed the same way). Epics are Discover Solution, Specify Solution, Implement Logic, Implement Tech Stack. A fifth epic, Create Tech Stack Rules And Transformers, turns an architecture description (LERN first) into CodeQL predicates and transform templates that Implement Tech Stack uses.

### Transformers live on practice guidance

Transformation is not a Transformers bounded context with its own Sketch aggregate. Each PracticeGuidance already has a canonical model (`StoryMap`, `CleanEngineeringModel`, BDD `Description`, DDD `BoundedContext` on CE classes) and format instantiations under `practices/{practice}/model/`.

### Transformation is a model channel folder — copy codeql

`practices/{practice}/model/transformation/` copies `model/codeql/` as far as it still fits, but every channel type is named `{Source}Transformer` — `CleanEngineeringTransformer`, `ModuleTransformer`, `OoadClassTransformer`, not the source/codeql names `CleanEngineeringModel` / `Module`. Mix-ins live only in that folder. Do not use markdown/python `Markdown*` prefixes. Do not copy `knowledge_graph/model/nodes.py` `Graph*` names — that folder is the older parallel; live mix-in is `model/codeql/`.

`Transformer` is one mix-in in `harness/transformers`, like one `Node` in `knowledge_graph`. There is no `TechStackTransformer` type — Node has no pack subtype. Templates are an argument to `transform`, like `graph` is an argument to `Node.join`. Practice transform templates sit in the channel folder the way `.ql` files sit in `model/codeql/`. LERN `templates/` stay on `LernDomainDriven` and are passed in. Do not hardcode server, client, or view as operations. Architecture predicates hang as existing `Rule` (and scanners / `.ql`), not a new `GraphRule` type.

### Agent surface copies KnowledgeGraph

`Transformer` is `@agent_toolset` with `domain_slug` like `KnowledgeGraph` (`harness/knowledge_graph/model/knowledge_graph.py`). Public transform operations take the same marks as that class’s agent seam: `@mcp` `@Skill` `@agent_tool` on the operation that runs (like `return_nodes`). An operation that only instructs the agent takes `@mcp` `@Skill` `@agent_instructions` (like `get_fix_violation_instructions`). Install still writes MCP, Skill, and agent-tool from those marks — do not add a parallel installer. `Node` stays a mix-in without those marks; the toolset is the aggregate (`KnowledgeGraph` / `Transformer`), not every mixed `Module`.


### Child template notation only

Lens bodies must use only the child sketch templates: stories indent (Epic / Sub-epic / Actor --> Verb Noun, ~> increment), clean_engineering module nest then ClassName / property / operation / ---- / ->, BDD plain-English subject / that / with / it should. Do not use < scaffold tags, YAML keys, or story-shaped lines inside ce: or bdd:.

### Extend practice models; template-pack tech stack

One mix-in: `Transformer`. Channel types wrap the live source type. A pack is passed into `transform model templates`. Guts live in the templates. LERN stays LernDomainDriven.

### Transformer mix-in and Transformers toolset

B: `Transformer` is the mix-in only, like `Node` in graph_node.py — mixed into practice types in model/transformation/, unmarked, the data a template binds at that node. `Transformers` is the `@agent_toolset`, like `KnowledgeGraph` — marked `transform` (mcp Skill agent_tool) takes a start node and a template library; it does not load or render the whole model. Mixed `Module` still does not install MCP.

### Two transform operations for the workflow

Two marked operations on Transformers, not one: `transform sketch` turns a practice sketch/model node into the next fidelity or domain skeleton; `transform logic` runs a template pack against filled domain logic (LERN first). Same mcp Skill agent_tool marks as `return_nodes`. The pack stays an argument on `transform logic`, not a subtype.

### Sketch is grouped by model, themes marked inside

Object-model families stay in one `ce:` catalog. Theme names are comments on that family (`// theme Specify Solution`), not a second copy of StoryMapTransformer / CleanEngineeringTransformer per epic. Stories stay as the epic tree. BDD subjects stay one tree per family with `that` / `with` for later themes instead of repeating the subject.

### BDD sketch rules were not CodeQL-scanned

CodeQL BDD rules (`describe-is-subject-not-internal`, `state-not-when`, `observable-behavior`) run on spec files, not on `bdd:` indent in a markdown sketch. Those `bdd:` blocks were written by hand against `practices/bdd/templates/bdd-sketch.md` and were not passed through `scan`. Mix-in wording (`that mixes transformer`), `practiceModels[]` in `it should`, and `a transformers toolset` as a subject violate plain-English / no-mechanism sketch rules and are rewritten with the model regroup.

Channel objects are the transformer-specific wrap of each codeql type, listed by family with `Transformer` at the end — not the source class, not “a practice,” and not a generic practice-model bag. Stories: StoryMapTransformer plus Epic, SubEpic, Story, Scenario, Background, Step, Example. Clean engineering: CleanEngineeringTransformer plus Module, File, OoadClass, Operation, Property, Parameter. BDD: DescriptionTransformer plus Context, Observation. DDD: BoundedContextTransformer plus Aggregate, Entity, EntityRoot, ValueObject, Repository, DomainEvent, DomainService. `transform sketch -> practiceModels[]` holds those family roots (and their nested transformers), not CleanEngineeringModel / StoryMap without the suffix.

