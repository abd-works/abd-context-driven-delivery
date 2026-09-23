# Grill Answers

### Active sketch lenses

Stories, Clean Engineering, and BDD stay in the transformers sketch — each already has a usable sketch template. DDD is in because its sketch template needs to improve so a later transform can consume it. UX is out for now; other practices wait.

### Fidelity-shaped transform epics

Stories follow fidelity, not a single sketch-to-architecture pipe: Human provides context; Agent writes each practice sketch; Transformer scaffolds that practice’s next fidelity (Stories: map then scenarios then acceptance tests; CE and DDD interspersed the same way). Epics are Discover Solution, Specify Solution, Implement Logic, Implement Tech Stack. A fifth epic, Create Tech Stack Rules And Transformers, turns an architecture description (LERN first) into CodeQL predicates and transform templates that Implement Tech Stack uses.

### Transformers live on practice guidance

Transformation is not a Transformers bounded context with its own Sketch aggregate. Each PracticeGuidance already has a canonical model (`StoryMap`, `CleanEngineeringModel`, BDD `Description`, DDD `BoundedContext` on CE classes) and format instantiations under `practices/{practice}/model/`. A `transformation/` folder next to that model extends `Transformer` (base in `harness/transformers`, same pattern as `StoryNode` / `OoadNode`) and `transform`s that model. `sketch-to-domain-logic` and `domain-logic-to-tech-stack` are files in that folder (or a subfolder of it), not properties on Transformer. LERN stays a clean_engineering specification; its transform files hang on `practices/clean_engineering/transformation`.


### Child template notation only

Lens bodies must use only the child sketch templates: stories indent (Epic / Sub-epic / Actor --> Verb Noun, ~> increment), clean_engineering module nest then ClassName / property / operation / ---- / ->, BDD plain-English subject / that / with / it should. Do not use < scaffold tags, YAML keys, or story-shaped lines inside ce: or bdd:.

### Extend practice models; template-pack tech stack

Same mix-in as graph Node on live practice types (StoryMap, CleanEngineeringModel, Description): Transformer is mixed onto those models, not a parallel Sketch aggregate. One TechStackTransformer takes domain logic from any practice model plus a template pack and runs every template to write files and folders. Guts live in the templates. LERN stays LernDomainDriven; its templates/ are the first pack passed in. Do not hardcode server/client/view as Transformer operations.

