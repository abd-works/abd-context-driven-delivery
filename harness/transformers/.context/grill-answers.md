# Grill Answers

### Active sketch lenses

Stories, Clean Engineering, and BDD stay in the transformers sketch — each already has a usable sketch template. DDD is in because its sketch template needs to improve so a later transform can consume it. UX is out for now; other practices wait.

### Fidelity-shaped transform epics

Stories follow fidelity, not a single sketch-to-architecture pipe: Human provides context; Agent writes each practice sketch; Transformer scaffolds that practice’s next fidelity (Stories: map then scenarios then acceptance tests; CE and DDD interspersed the same way). Epics are Discover Solution, Specify Solution, Implement Logic, Implement Tech Stack. A fifth epic, Create Tech Stack Rules And Transformers, turns an architecture description (LERN first) into CodeQL predicates and transform templates that Implement Tech Stack uses.

### Transformers live on practice guidance

Transformation is not a Transformers bounded context with its own Sketch aggregate. Each PracticeGuidance already has a canonical model (`StoryMap`, `CleanEngineeringModel`, BDD `Description`, DDD `BoundedContext` on CE classes) and format instantiations under `practices/{practice}/model/`.

### Transformation is a model channel folder — copy codeql

`practices/{practice}/model/transformation/` copies `model/codeql/` as far as it still fits: same type names, every type is `(SourceType, Transformer)` the way codeql is `(SourceType, Node)`, including members (`Module`, `OoadClass`, `Operation`, …), not only the root. Mix-ins live only in that folder. Do not use markdown/python `Markdown*` prefixes. Do not copy `knowledge_graph/model/nodes.py` `Graph*` names — that folder is the older parallel; live mix-in is `model/codeql/`.

`Transformer` is one mix-in in `harness/transformers`, like one `Node` in `knowledge_graph`. There is no `TechStackTransformer` type — Node has no pack subtype. Templates are an argument to `transform`, like `graph` is an argument to `Node.join`. Practice transform templates sit in the channel folder the way `.ql` files sit in `model/codeql/`. LERN `templates/` stay on `LernDomainDriven` and are passed in. Do not hardcode server, client, or view as operations. Architecture predicates hang as existing `Rule` (and scanners / `.ql`), not a new `GraphRule` type.

### Agent surface copies KnowledgeGraph

`Transformer` is `@agent_toolset` with `domain_slug` like `KnowledgeGraph` (`harness/knowledge_graph/model/knowledge_graph.py`). Public transform operations take the same marks as that class’s agent seam: `@mcp` `@Skill` `@agent_tool` on the operation that runs (like `return_nodes`). An operation that only instructs the agent takes `@mcp` `@Skill` `@agent_instructions` (like `fix_violations`). Install still writes MCP, Skill, and agent-tool from those marks — do not add a parallel installer. `Node` stays a mix-in without those marks; the toolset is the aggregate (`KnowledgeGraph` / `Transformer`), not every mixed `Module`.


### Child template notation only

Lens bodies must use only the child sketch templates: stories indent (Epic / Sub-epic / Actor --> Verb Noun, ~> increment), clean_engineering module nest then ClassName / property / operation / ---- / ->, BDD plain-English subject / that / with / it should. Do not use < scaffold tags, YAML keys, or story-shaped lines inside ce: or bdd:.

### Extend practice models; template-pack tech stack

One mix-in: `Transformer`. Channel types wrap the live source type. A pack is passed into `transform model templates`. Guts live in the templates. LERN stays LernDomainDriven.

