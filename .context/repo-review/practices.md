# Relationship review: cdd_guidance/practices

This review checks, by reading the code as it stood on 2026-11-07, every relationship and every production class in `cdd_guidance/practices`: Stories, DDD, UX, Clean Engineering, BDD, agent BDD, and `output_folder.py`. It covers each practice's guidance class, its domain node classes, its format adapters, its rules, and its `graph_practice.py`. The earlier judgments in `.context/repo-runtime.md` and `.context/repo-model-disconnected.md` came from a mechanical rule about how the code reaches the other object. Each one is confirmed or overturned here, and the relationships those files missed are added.

Verdicts: **R** means right as a runtime dependency: the two objects are independent and one asks the other to act. **W** means the code has the wrong shape: it builds the other object per call from strings, re-reads a file another object holds, hands an owner's data to a helper, or constructs what should be a part or a held collaborator. **D** means the class has no use: nothing calls it, nothing builds it at install time, and it uses nothing. A class used only by specs counts as D (spec-only), and its specs go with it.

A `graph_practice.py` class is being folded into its practice class by the option A refactor. Its relationships are still listed, marked "(folding into {Practice} under option A)".

Not production, so not checked as classes: `*_spec.py`, `*.feature.py`, `conftest.py`, spec fixtures, `_examples/`, and the example code under `templates/`.

## Findings that cross the parts

- **One adapter shape, judged once.** `PracticeGuidance._live_adapter` (`harness/guidance/guidance.py`, about lines 592-625) makes a blank adapter, calls `parse(text)`, which returns a *new* model, and calls `render(model)` with a model handed in. The parts below judged this convention from different sides. The ruling for the whole area:
  - An adapter that subclasses the domain class and renders itself, or copies the canonical model into its own subclass with `type(self)(canonical)`, has the right subclass shape (R for the subclass relationship). These are Stories' DrawIO and code models, and CE's Draw.io, Markdown and JSON parts.
  - An adapter that renders the model it is handed without becoming it, or spells each part from outside, wraps the domain class (W). These are Stories' JSON, Markdown and Sketch, CE's Python, TypeScript, Java, JavaScript and Sketch, DDD's `ClassCard`, the DrawIO and Sketch writers, and DDD's whole python/typescript route through `clean_engineering_bridge`.
  - The convention itself (blank instance, `parse` returning a new object, `render` taking a second model) is a W owned by `PracticeGuidance` in harness/guidance, outside this area. The practice holds its current model (composition 1) and each format renders that model, so `render` reads `self` rather than a model passed in. It is counted once, in the UX part (relationship 27 there).
- **Practices look each other up by name in the graph.** Stories, DDD, UX and BDD nodes and graph readers find the `stories`, `clean_engineering`, `ddd`, `bdd` or `ux` practice graph through `graph.practices[name]` or `GraphPractices.named(name)`. Every one of these is W. Under option A, the `Graph` holds the session's PracticeGuidance instances (aggregation 1..*), and a practice that extends another holds that practice (association 1). DDD extends Clean Engineering, Stories links to Clean Engineering and DDD, and BDD links to Clean Engineering.
- **A second format switch beside `formats`.** `CleanEngineeringGraph._language_model`, `Drawio`'s parser table, `BddGraph`'s choice by file suffix, `StoryModel._story_map_file` and `StoryModel.load` each choose an adapter by file suffix or name, beside the practice's `formats` dict. Each is W. The practice's `formats` should be the one place that maps a format to its adapter.
- **Re-reading files the model already holds.** `_StoryLinks`, `GraphStoryModel._file_lines`, `_DddReading._text`, `_ObservationLinks`, `DeepModule`, `_DrawioScannerRule` and `PythonModule` all read source text again that a node already holds. Each is W, and the node that holds the text should answer the question.
- **Defect:** `MiroStoryModel` is registered as the `miro` format (`stories/stories.py:54`) but has no `render` or `parse`, so `Stories.render(format="miro")` raises AttributeError. Remove it from `formats` or give it the two operations.
- **Dead code that is not a whole class:**
  - Methods with no caller: `MarkdownCleanEngineeringModel.load_class` and `from_workspace`, `JsonCleanEngineeringModel.from_workspace`, `Description.load_context`, `Context.load_observation` and `Context.load_context` (in `bdd/model/nodes.py`).
  - Never reached or never read: `DiagramModule.load_class` and `DiagramCleanEngineeringModel.module_type`.
  - Modules that only re-export the practice's rules and that nothing imports: `clean_engineering/model/{python,typescript,javascript}/rules/__init__.py`.
  - `clean_engineering/model/miro/` holds only a stale `__pycache__`.
  - Spec support sitting among production rules: `stories/rules/rule_examples.py`.
  - Seed files that nothing reads: `stories/model/{typescript,java,javascript}/seeds/*`, except `story-types.js`.
- **Outside this area:** `cdd_guidance/patterns/source_text.py:8` is a second `SourceText` class beside `clean_engineering/model/operation_metrics.py:107`.

## Scope of each part

### Clean Engineering: practice class, graph practice, rules, core class model

Scope: `clean_engineering.py`, `graph_practice.py`, `strategies/` (one markdown file, `separate factory.md`, no classes), `rules/` (all), `model/*.py` directly in `model/`, `model/rules_shared/`. Paths below are relative to `cdd_guidance/practices/clean_engineering/` unless they start with another top folder.

### Clean Engineering: format adapters

Scope read: `model/diagram/{diagram_node,class_layout,geometry}.py`, `model/drawio/{diagram_node,drawio,drawio_class_model}.py`, `model/drawio/rules/__init__.py`, `model/drawio/scanners/*.py`, `model/markdown/markdown_class_model.py`, `model/python/python_class_model.py`, `model/{typescript,java,javascript}/*_class_model.py`, `model/{python,typescript,javascript}/rules/__init__.py`, `model/json/json_class_model.py`, `model/sketch/sketch_class_model.py`. `model/miro/` holds only `__pycache__` (no source; Miro has been removed). The diagram trunk read as it is now: `diagram/diagram_node.py` defines `DiagramNode`, `DiagramClass(OoadClass, DiagramNode)`, `ImportedClass`, `DiagramModule(Module, DiagramNode)`, `ContainmentForest`, `DiagramCleanEngineeringModel(CleanEngineeringModel)`; `drawio/diagram_node.py` subclasses those (`DrawIOClass(DiagramClass, DrawioVertex)` etc.).

**Adapter shape, in one paragraph.** Every format model subclasses `CleanEngineeringModel`. Draw.io, Markdown and JSON also subclass the parts they write (`DrawIOModule`/`DrawIOClass`, `MarkdownModule`/`MarkdownOoadClass`, `JsonModule`/`JsonOoadClass`/`JsonProperty`/`JsonOperation`/`JsonRelationship`), and those parts write themselves (`DrawIOClass.html`, `MarkdownOoadClass.render`, `JsonOoadClass.render`) — the right shape. The code channels (Python, TypeScript, Java, JavaScript) and Sketch do not: the model object spells every class, property and operation it is handed (`class_open(oclass)`, `property_line(prop)`, `signature(operation)`, `_SketchSection(canonical)`), and parse builds plain `OoadClass`/`Property`/`Operation`. Those are wrappers around the domain parts, so their relationships to OoadClass, Property and Operation are W below. Separately, every format's `render` takes a second model (`canonical`) instead of rendering itself, and every `parse` returns a new instance of its own class instead of filling `self`.

### Stories: practice class, graph practice, rules, core story model

Read as of this pass. Paths are from `cdd_guidance/practices/stories/` unless written in full. `graph_practice.py` is 184 lines now (the earlier review's line numbers still match). `StoriesGraph` and `_StoryLinks` are being folded into `Stories` under option A; their relationships are listed and marked that way.

### Stories: format adapters

Paths below are relative to `cdd_guidance/practices/stories/model/` unless they start with a top folder. The earlier review files had no relationship in these folders (repo-runtime.md stops at DiagramStoryModel; repo-model-disconnected.md sections 3/4 have none), so every relationship below is new. Only JavaScriptStory appeared, in section 2.

**How the adapters relate to the domain classes.** Every format model subclasses StoryModel (or DiagramStoryModel / CodeStoryModel / BraceStoryModel), and every format has node subclasses of Epic/Story/Scenario/Increment, except Sketch, which has none. The adapter is chosen through `Stories(formats=...)` (stories.py:49-59). `PracticeGuidance._live_adapter` makes a blank instance, then calls `adapter.parse(text)` (the result is a **new** model, not the adapter itself) and `target.render(model)` (the model is **handed in**) (harness/guidance/guidance.py:592, 612, 619, 625). DrawIO and the code models convert the model they are handed into their own subclass through the copy constructor (`type(self)(canonical)`, drawio/nodes.py:381; code_story_model.py:381), so they really are the story map in their format: R. JSON, Markdown and Sketch render the model they are handed straight from its data without becoming it, so they wrap the domain model instead of being a subclass of it: W.

**Defect found:** MiroStoryModel is registered as the `miro` format (stories.py:54) but has no `render` or `parse`; it has only `save`/`load` (miro/nodes.py:309, 335). `Stories.render(format="miro")` fails with AttributeError on the blank adapter. Only story_channel.feature.py:261/274 uses Miro, and it goes through save/load.

### DDD

Slice: `ddd.py`, `graph_practice.py`, `model/` (`nodes.py`, `stereotypes.py`, `clean_engineering_bridge.py`, `markdown/`, `drawio/`, `sketch/`), `rules/`. `model/python`, `model/typescript`, `guidance/`, `agents/`, `templates/` and `_examples/` hold no production `.py`. Paths below are relative to `cdd_guidance/practices/ddd/` unless they start with another top folder.

**Headline: how each DDD format adapter relates to the DDD domain class it represents.**

| format | adapter | subclasses the domain class? | what it does instead |
|---|---|---|---|
| markdown | `MarkdownBoundedContextMap`, `MarkdownBoundedContext`, `MarkdownAggregate`, `MarkdownEntity`, `MarkdownInvariantObject`, `MarkdownIntegration` (`model/markdown/nodes.py`) | Yes for the map, context, aggregate, entity, invariant object, integration | No markdown subclass for ValueObject, Repository, DomainService, DomainEvent, Specification, Factory. Those are written and read through `ClassCard` (`model/markdown/class_cards.py:28`), a **wrapper** holding a plain building-block node (`card.node`) plus a copy of its stereotypes and its invariants. The map also parses each context's aggregates for it (`_fill_context`, `_read_aggregate`) instead of the context reading its own lines. |
| drawio | `DrawIOBoundedContextMap(MarkdownBoundedContextMap)` (`model/drawio/drawio_bounded_context_map.py:107`) | Only the map, and it subclasses the **markdown** map, not `BoundedContextMap` | No DrawIO context, aggregate, or building-block subclasses. Reading builds markdown nodes through `_ContextMapReader` / `_AggregateViewReader`; writing hands the model's contexts and aggregates to `ContextLayout` + `_DiagramWriter` or to `DrawIOAggregateModel`, a separate writer that does not subclass anything and builds Clean Engineering's `DiagramCard` / `DiagramArrow` records from `ClassCard` data. It does not use Clean Engineering's own diagram trunk (`DiagramClass(OoadClass, DiagramNode)`, `DiagramModule(Module, DiagramNode)` in `clean_engineering/model/diagram/diagram_node.py:43,82`). |
| sketch | `SketchDddModel(MarkdownBoundedContextMap)` (`model/sketch/sketch_ddd_model.py:67`) | Only the map, through the markdown map | No sketch node subclasses; `_SketchReader` builds markdown nodes and `_SketchFence` builds `ClassCard`s; `_SketchWriter` walks the model's contexts, aggregates, and cards from outside. |
| python, typescript | Clean Engineering's `PythonCleanEngineeringModel` / `TypeScriptCleanEngineeringModel` | No DDD adapter at all | `Ddd._model_for` copies the map into a fresh `CleanEngineeringModel` (`to_clean_engineering`) and copies back (`from_clean_engineering`), cloning every property and operation, although every DDD node already **is** a Clean Engineering node (`Aggregate`/`BoundedContext` subclass `Module`, building blocks subclass `OoadClass`, `DomainEvent`/`InvariantObject` subclass `Property`). The one outlier is `BoundedContextMap` (`model/nodes.py:446`), which subclasses nothing, so it is not a `CleanEngineeringModel`; that gap is what forces the bridge. |

**How DDD uses Clean Engineering classes.** (1) Inheritance: every DDD node except `BoundedContextMap` and `Integration` subclasses a Clean Engineering model class — right. (2) `Ddd._parse_content` (`ddd.py:67-76`) parses markdown with its own adapter, and when no aggregates come back it constructs `MarkdownCleanEngineeringModel()` per call and parses the same text a second time — another practice's adapter, built per call, outside the `formats` dict. (3) `Ddd._model_for` (`ddd.py:78-93`) converts with the bridge in both directions and then `_python_generics` (`ddd.py:102-114`) rewrites `<>` to `[]` in the Clean Engineering model's type hints, chosen by `type(target).__name__.startswith("Python")`. (4) `DddGraph.own_rules` gets Clean Engineering's graph rules by name from `GraphPractices`, and `_DddReading` gets Clean Engineering's `PracticeGraph` by name and copies each `OoadClass` graph node's facts into a new DDD `Node` (`_tactical_block`). (5) The drawio aggregate view uses Clean Engineering's `ArrowRouter`, `DiagramCard`, `DiagramArrow`, `Geometry`, `EDGE_STYLES`, and `arrow_style`; `arrow_style` is typed for `Dict[str, DrawIOClass]` but DDD passes `Dict[str, DiagramCard]`, which shows the drawing logic is duplicated rather than inherited.

### UX, BDD, agent BDD, output_folder.py

Paths are relative to `cdd_guidance/practices/` unless they start with `harness/` or `space/`. Spec support that is not production and is not listed as a class: `ux/model/ux_map_spec_fixture.py` (OrderingMap), `bdd/rules/rule_examples.py` (functions), `agent_bdd/conftest.py`, every `*_spec.py`, `_examples/`, `templates/`.

**Format adapter check.** Every UX format adapter subclasses the domain class it represents: DrawioUxMap, HtmlUxMap, JsonUxMap, MarkdownUxMap and ClaudeDesignUxMap are `UxMap` subclasses; ClaudeDesignStoryModel, ClaudeDesignEpic and ClaudeDesignStory subclass the Stories `DiagramStoryModel`, `DiagramEpic`, `DiagramStory`. Every BDD format adapter subclasses `BddModel`: SketchBddModel, MarkdownBddModel, CodeBddModel (PythonBddModel, TypeScriptBddModel), GraphBddModel. None wraps or copies its domain class. The shape faults are elsewhere: each adapter instance is created empty and `render(ux_map)` / `render(canonical)` converts another model handed in (relationship 27), HtmlUxMap builds a JsonUxMap instead of being one (relationship 24), and ClaudeDesignUxMap's useful operations are classmethods fed a list of screens (relationship 28).

## 1. Runtime relationships, verified

### Clean Engineering: practice class, graph practice, rules, core class model

| # | from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|---|
| 1 | CleanEngineering → Drawio | creates once, keeps in `_drawio` | clean_engineering.py:62-65 | R | W | The property makes the Drawio toolset on first use and keeps it; every later call reads the same object (composition 1). |
| 2 | CleanEngineering → Drawio | asks it to render | clean_engineering.py:78 | R | | Asks the part it holds to act. |
| 3 | CleanEngineeringGraph → GraphPractices | registers with at import | graph_practice.py:425 | R | | Registers with a registry; the registry imports it by module path (folding into CleanEngineering under option A). |
| 4 | CleanEngineeringModel → ModelChildren | creates its module list once | model/base_class_model.py:644 | R | | Its own part, made once in the constructor. |
| 5 | CleanEngineeringModel → CleanEngineeringModel (another copy on the graph) | finds by type name, clones its modules | model/base_class_model.py:656-665 | W | (new) | Looks another model up on the graph by the string `"CleanEngineeringModel"` and copies its modules instead of being handed it. |
| 6 | CleanEngineeringModel → OoadClass | walks its modules' classes | model/base_class_model.py:667-675 | R | W | `every_class` only reads the classes its own modules already hold; nothing is created. |
| 7 | CleanEngineeringModel → Module | creates a child module (`load_module`, `load_modules`) | model/base_class_model.py:717, :731 | R | W | The factory `_reconcile_collection` calls; the new module goes straight into `self.modules` (composition 0..*). |
| 8 | Module → CodeBody | creates its preamble | model/base_class_model.py:467 | R | | Its own part, made once. |
| 9 | Module → ModelChildren | creates its module and class lists | model/base_class_model.py:468-469 | R | | Its own parts, made once. |
| 10 | Module → OoadClass | creates a child class (`load_class`), appends | model/base_class_model.py:538, :563 | R | W | Factory used by reconciliation; the class is kept in `self.classes` (composition 0..*). |
| 11 | OoadClass → ModelChildren | creates its property and operation lists | model/base_class_model.py:221-226 | R | | Its own parts, made once. |
| 12 | OoadClass → Property | creates (`load_property`), appends (`load_properties`) | model/base_class_model.py:319, :340 | R | | A node making its own children; kept in `self.properties`. |
| 13 | OoadClass → Operation | creates (`load_operation`), appends (`load_operations`) | model/base_class_model.py:327, :354 | R | | A node making its own children; kept in `self.operations`. |
| 14 | Operation → ModelChildren | creates its parameter list | model/operation.py:124 | R | | Its own part. |
| 15 | Operation → CodeBody | creates its body | model/operation.py:130 | R | | Its own part, replaced when a parser reads the body. |
| 16 | CodeBody → CodeLanguage | asks `is_unfinished`, `comment` | model/code_body.py:115, :135 | R | | Holds the language it was read in (association 1) and asks the language handed to `lines_in`. |
| 17 | WrittenBlock → CodeBody | builds a CodeBody from its own line lists on every call | model/code_body.py:186, :190, :193 | W | | Rebuilds bodies from strings it holds each time `inside_for`, `lead_body`, `closing_body` run. |
| 18 | CleanEngineering → format adapters (Markdown, Json, Python, TypeScript, Java, JavaScript, DrawIO, Sketch class models) | names them in `formats` | clean_engineering.py:46-55 | R | (new) | PracticeGuidance builds the adapter for the active format; the practice declares the set once. |
| 19 | CleanEngineeringGraph → rules packages | `rules_in(.rules)`, `rules_in(.model.drawio.rules)` | graph_practice.py:44-48 | R | (new) | Reads the `RULES` / `BY_SLUG` registries of its own rules packages (folding into CleanEngineering under option A). |
| 20 | CleanEngineeringGraph → _CodeReading, _ModelReading | creates a reader per `read`, passes the PracticeGraph | graph_practice.py:52-53 | W | (new) | A method object built per call from the practice's graph (folding into CleanEngineering under option A). |
| 21 | _CodeReading → PracticeGraph / Graph | `add`, `link`, `source_files`, `scope_folders`, `report_progress` | graph_practice.py:61-70, :100, :154-157 | R | (new) | Asks the graph it was handed to act. |
| 22 | _CodeReading → Module | creates one per code folder and adds it to the practice | graph_practice.py:97-100 | R | (new) | Creates the node the practice graph then keeps. |
| 23 | _CodeReading → OoadClass, Operation | hands each its own source slice (`load_source_facts`, `load_span_facts`) | graph_practice.py:153, :195 | W | (new) | The reader slices file text and passes it in; the class and operation should already hold their source span from the parse. |
| 24 | _CodeReading → Parameter | `load_operation_facts(operation)` | graph_practice.py:200; model/operation.py:75 | W | (new) | Hands a parameter the operation it already belongs to (`parameter.parent`). |
| 25 | _CodeReading → Module (folder) | extends, then overwrites its `dependencies` list | graph_practice.py:79, :107 | W | (new) | Writes another object's field from outside, first with import paths, then with node ids. |
| 26 | _CodeReading → OoadClass text | re-scans class text with regexes for getters, fields, extent (`_properties_of`, `_class_extent`, `_class_span`) | graph_practice.py:151, :158, :350-405 | W | (new) | Re-reads text the language parser already read into the OoadClass. |
| 27 | graph_practice `_language_model` → Python/TypeScript/JavaScript CleanEngineeringModel | builds one per file by suffix | graph_practice.py:273, :279-289 | W | (new) | A second suffix-to-adapter switch beside the practice's own `formats`; built per file. |
| 28 | _ModelReading → MarkdownCleanEngineeringModel | builds one per model document | graph_practice.py:232 | W | (new) | Same: builds the markdown adapter per file instead of asking the practice for it. |
| 29 | _ModelReading → ModelDescriptions | builds one per read; it copies every member of each parsed model into dicts set as a root fact | graph_practice.py:228-234; model/model_descriptions.py:31-36, :45-57 | W | (new) | Flattens the parsed models into dictionaries instead of the practice root holding the models read. |
| 30 | graph_practice `_scanned_span` → CFamilyParse | static `method_span_in_text` | graph_practice.py:417-422 | W | (new) | Re-scans file text for an operation's span the parser should have recorded on the Operation. |
| 31 | graph_practice `_folder_role` → `module_card` | probes a folder's card path | graph_practice.py:310-313 | W | (new) | A second probe of the module card beside ModuleContext, which owns that file. |
| 32 | OoadNode → UpdateReport | creates and returns a report per `translate_from` | model/base_class_model.py:128-132 | R | (new) | A result value; but no production caller reads it (see D). |
| 33 | OoadNode → ChildCollectionPair | each node packs its own child list, the source's list, and its own factory into a pair for `_reconcile_collection` | model/base_class_model.py:140, :334, :621, :736; model/operation.py:317 | W | (new) | A data bag of the node's own collection handed to a helper; the collection should reconcile itself. |
| 34 | OoadClass → SourceText | builds one from text passed in | model/base_class_model.py:257 | W | (new) | Measures text handed in from outside, built per call. |
| 35 | OoadClass → Relationship | creates on `depend_on`, `load_relationship` | model/base_class_model.py:311, :400 | R | (new) | Its own dependency records, kept in `self.dependencies` (composition 0..*). |
| 36 | OoadClass → Property | writes `stereotype`, `cardinality`, `origin`, then calls `derive_relationship` | model/base_class_model.py:385-394 | W | (new) | Reaches into the property's fields to set its relationship. |
| 37 | Module → ModuleContext | builds one from a folder path per `load_folder_facts` | model/base_class_model.py:600-612 | W | (new) | The folder path is handed in from outside and the card object is built per call. |
| 38 | Module → OoadClass | sets `peer_names`, `composes_peers` on each class | model/base_class_model.py:586-589 | W | (new) | Writes facts each class can derive from its own stereotypes and its parent module. |
| 39 | Operation → SourceText | builds one per call from text passed in, and once from a string of fake calls made from `callees` | model/operation.py:215, :229, :250 | W | (new) | Measures text handed in; line 250 builds fake source to reuse a pattern. |
| 40 | Operation → PythonFunctionBody | builds one from a syntax tree node the Python model passes | model/operation.py:238; model/python/python_class_model.py:208 | W | (new) | Measures data handed in per call. |
| 41 | Operation → Parameter | creates its parameters from strings | model/operation.py:171-181 | R | (new) | A node making its own children. |
| 42 | Operation → OoadClass | reads the parent's name (`owner`) | model/operation.py:159-161 | R | (new) | Reads its parent through the parent link. |
| 43 | Property → Relationship | creates in `derive_relationship` | model/property.py:137 | R | (new) | Its own part, derived from its type and stereotype. |
| 44 | `append_invariant`, `take_property_note` → Property / Operation, Invariant | free functions set the owner's fields and append Invariants | model/property.py:39-70; callers model/c_family_parse.py:249, :332 | W | (new) | Logic on Property's state lives in module functions that take the property as a parameter. |
| 45 | CodeLanguage → CodeSpelling | holds one | model/code_body.py:53 | R | (new) | Composition 1, given at construction. |
| 46 | language models → CodeLanguage | `CodeLanguage.named("java")` from a class-level registry | model/code_body.py:38, :55, :59; callers model/java/java_class_model.py:17, model/python/python_class_model.py:106 | W | (new) | Found by name string in a global registry though the constants `PYTHON`, `JAVA` … already exist. |
| 47 | CodeCleanEngineeringModel → CleanEngineeringModel (canonical) | reads `every_class`, `modules` | model/code_class_model.py:27-33 | R | (new) | Acts on the canonical model it is handed to render. |
| 48 | CodeCleanEngineeringModel → its own type (kept model) | parses the previous text into a new model | model/code_class_model.py:28 | R | (new) | Reads the earlier file into a model of the same kind to keep its bodies. |
| 49 | CodeCleanEngineeringModel → CodeBody | `in_language_of`, `lines_in`, empty body as "none" | model/code_class_model.py:43, :82-86, :177-204 | R | (new) | Asks the bodies the operations and modules hold. |
| 50 | BraceCleanEngineeringModel → CFamilyParse | builds one per `parse`, passing its own language and two factories | model/code_class_model.py:219-224 | W | (new) | The model hands its own data to a helper that does its parsing. |
| 51 | CFamilyParse → Module, OoadClass, Operation, Property, CodeBody | creates the parsed nodes; builds a throwaway `Module(name="")` to pass to `model.load_module` | model/c_family_parse.py:85, :109, :140, :162, :213, :253, :330 | W | (new) | A helper outside the node tree creates its nodes; once parsing is on the model this is the model making its own children (R). |
| 52 | CFamilyParse → ClassHead | `ClassHead.above(text)` | model/c_family_parse.py:108 | R | (new) | Reads a value object from the text it is parsing. |
| 53 | ClassHead → DocumentedIntent | `DocumentedIntent.read(doc)` | model/class_stereotypes.py:101 | R | (new) | Reads a value object from its own doc comment. |
| 54 | ShapeClassesAroundResources, DoNotInventParallelObjectModels, LayerSeparation → ClassGraph | each builds its own index of the practice graph per check | model/rules_shared/coupling_rules.py:55, :90, :185 | W | (new) | Three rules rebuild the same index from the graph each check. |
| 55 | every rule → Node, RuleCheckContext | `check(node, context)` reads facts | rules/*.py, model/rules_shared/*.py | R | (new) | Acts on the node and context it is handed. |
| 56 | rules → PracticeGraph | `context.practice.registered(id)` with ids kept in facts (`folder`, `dependencies`) | rules/module_graph_rules.py:47; rules/practice_wide_rules.py:43, :45, :216; model/rules_shared/coupling_rules.py:237, :242 | W | (new) | Nodes store other nodes' ids as facts and rules look them up by string instead of following edges. |
| 57 | MissingModuleContext → file system | probes `.context/module-context.md` above the folder | rules/module_graph_rules.py:70-78 | W | (new) | Re-reads card files Module nodes already hold as `has_module_context`. |
| 58 | DeepModule → file system | reads every source file again for imported names | rules/practice_wide_rules.py:124-140 | W | (new) | Re-reads source the code reading already parsed. |

Wrong shapes, owner and redesign:

| # | owner | should be | redesign |
|---|---|---|---|
| 5 | the graph's one CleanEngineeringModel (PracticeGraph) | association 1 | Hand the model the existing model (or have the graph hold one model) instead of finding another copy by type name and cloning it; no production caller opens a model on a graph today, only specs. |
| 17 | WrittenBlock | composition 1 each (inside, lead, closing CodeBody) | Keep the inside, lead and closing lines as CodeBody parts made when the reader fills the block; `inside_for` compares the held body. |
| 20 | CleanEngineering (option A) | composition 1 (its PracticeGraph) | Reading the code and the model documents become operations of the practice over the graph it holds; drop the two one-read classes. |
| 23 | OoadClass, Operation | composition 1 (their source span) | The language parser records each class's and operation's span text when it reads them; the graph code stops slicing lines and passing them in. |
| 24 | Parameter | association 1 (its parent Operation) | `Parameter` reads `self.parent` for the operation name and setter flag; drop the argument. |
| 25 | Module (folder) | aggregation 0..* (the file modules under it) | The folder Module holds its file modules and derives its dependencies from them; the reader stops writing its field twice. |
| 26 | OoadClass | composition 0..* (properties, getters, fields) | Each language parser records getters and declared fields as properties with lines, so the graph reads `cls.properties` only. |
| 27, 28 | CleanEngineering | association 1 (its format adapters) | Ask the practice for the adapter of a file's language from the `formats` it already declares, and keep one adapter per language for the read. |
| 29 | CleanEngineering practice root | aggregation 0..* (the CleanEngineeringModel objects read from `*-model.md`) | Keep the parsed model documents on the root and let realizations walk their members; drop ModelDescriptions' dictionary copy. |
| 30 | Operation | composition 1 (its span) | The brace parser records `end_line` for every operation, so no caller rescans text. |
| 31, 37 | Module | composition 1 (its ModuleContext) | Module is made with its folder and holds its ModuleContext; `_folder_role` asks it instead of probing `module_card`. |
| 33 | ModelChildren (each node's child collection) | composition 1 | Move reconciliation onto the collection (`children.reconcile(source_children, load)`), so a node no longer packs its own list into a pair. |
| 34, 39 | OoadClass, Operation | composition 1 (SourceText of its own span) | Each keeps the SourceText of its span made once at parse; `_delegates_io_and_domain` checks the callee names directly instead of faking source. |
| 36, 44 | Property | — (its own operations) | Add `Property.take_relationship(relationship)` and `Property.take_note(text)`; OoadClass and the parsers call those instead of setting fields or using module functions. |
| 38 | OoadClass | association 1 (its parent Module) | `composes_peers` becomes a property derived from the class's stereotypes and `peer_names` from its parent's classes. |
| 40 | Operation | composition 1 (its PythonFunctionBody) | The Python model gives the operation its syntax node once when it creates it; the operation keeps the measurer. |
| 46 | each language model | association 1 (its CodeLanguage) | Language models hold the module constant (`PYTHON`, `JAVA` …) directly; remove the class-level `_languages` registry and `named`. |
| 50, 51 | BraceCleanEngineeringModel | composition (its modules, classes, operations) | Fold CFamilyParse's operations into BraceCleanEngineeringModel, which already holds `language`; it creates its own nodes, and the `model_factory`/`class_factory` callables and throwaway Module go. |
| 54 | the practice graph (or RuleCheckContext) | composition 1 (one ClassGraph per graph) | Build the class index once per graph and let rules ask `context.classes`. |
| 56 | Node | association (edges `belongsTo`, `dependsOn`) | Follow the edges the graph already records instead of storing node ids in facts and resolving them by string. |
| 57 | Module | association 0..1 (its enclosing Module) | Read the enclosing Module nodes' `has_module_context` through `owns` edges instead of probing disk. |
| 58 | Module | composition (its imported names, recorded at parse) | `Module.load_source_facts` records the class names each file imports; DeepModule reads that fact. |

Also seen, outside this slice: `cdd_guidance/patterns/source_text.py:8` defines a second `SourceText` class beside `model/operation_metrics.py:107` (`do-not-invent-parallel-object-models`), and the lern pattern spec imports the Clean Engineering one.

### Clean Engineering: format adapters

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| ArrowRouter → DiagramArrow | holds the arrows it is handed, routes them, sets their sides/points | diagram/class_layout.py:381-389, :469-471 | R | W | Handed in the constructor and kept in `self._arrows` (aggregation 0..*); :469/:471 are `dict.setdefault`/`dict.items` on a local dict, not DiagramArrow calls. |
| ArrowRouter → DiagramArrow | reads routed, path, source, target, kind, sides, points | diagram/class_layout.py:421-514 | R | | Reads the arrows it holds. |
| ArrowRouter → Geometry | reads x, y, width, height, center of card boxes | diagram/class_layout.py:429-446, :503-509 | R | | Geometry is the value each held card carries. |
| ArrowRouter → _RouteGrid | creates a routing grid for each pass and for each lifted arrow | diagram/class_layout.py:455 | R | | Working grid deliberately rebuilt without the lifted arrow; it is the router's own scratch state. |
| ArrowRouter → _ArrowSearch | creates one search per arrow route | diagram/class_layout.py:516, :518 | R | | Method object run once with the grid and the end points. |
| DiagramCard → Geometry | builds its box from its own x, y, width, height | diagram/class_layout.py:74-79 | R | W | Geometry is an immutable value computed from the card's own fields, not from text held elsewhere. (Simplification only: keep a `geometry` field as DiagramNode does.) |
| CardPlacement → Card (DiagramNode / DiagramCard) | holds the cards and arrows it is handed, sets each card's geometry | diagram/class_layout.py:119-125, :212-220 | R | | Aggregation of handed collaborators. |
| DiagramNode → Geometry | holds its box | diagram/diagram_node.py:33, :49, :89 | R | | Composition 1, set once and replaced as placement moves it. |
| DiagramModule → DiagramClass | load_class translates a class into a DiagramClass | diagram/diagram_node.py:91-94 | R | | Translation override of Module.load_class (note: never reached; DrawIOModule overrides it and ContainmentForest's DiagramModules never load classes). |
| ContainmentForest → Module | creates synthesized parent modules and keeps them in by_name | diagram/diagram_node.py:207 | R | | Composition: the forest owns the containers it invents. |
| ContainmentForest → DiagramModule | builds a throwaway DiagramModule copy of each Module per depth query only to call external_deps | diagram/diagram_node.py:229-233, :243-247 | W | | Copies the owner's data into a helper object per call. |
| | | | | | Owner: Module. Should be: a query on Module itself (no relationship). Redesign: move `external_deps` to Module (its own name and dependencies) and call `module.external_deps()`; drop the copies. |
| DrawIOCleanEngineeringModel → CleanEngineeringModel (canonical) | render(canonical) writes a second model; writers copy each canonical module/class into DrawIOModule/DrawIOClass per write, and `_ModulesDiagramWriter._place`/`_size` reload the same module for every size query; `is_modules_view(canonical)` inspects it from a free function | drawio/drawio_class_model.py:141-144, :343, :389, :403, :671-675; diagram/diagram_node.py:141 | W | | The adapter subclasses the model but writes a model it is handed by copying it, repeatedly. |
| | | | | | Owner: DrawIOCleanEngineeringModel. Should be: composition 0..* DrawIOModule (each composing DrawIOClass) held as its own modules. Redesign: translate the canonical model into the Draw.io model once (`translate_from` with `load_module`/`load_class`) and have the writers read `self.modules`; `is_modules_view` becomes a property of CleanEngineeringModel. |
| DrawIOCleanEngineeringModel → _ModulesDiagramWriter / _ClassDiagramWriter | creates one writer per render | drawio/drawio_class_model.py:143-144 | R | | Per-call method objects so two renders never share ids or positions (stated in the module docstring). |
| _ModulesDiagramWriter → ContainmentForest | builds the forest of the modules it writes | drawio/drawio_class_model.py:298 | R | | Part made once per writer and kept. |
| _ClassDiagramWriter → DrawIOCleanEngineeringModel | holds the channel; asks it for kept_previous, load_class, imported_class | drawio/drawio_class_model.py:430, :539, :670-671 | R | | Held collaborator. |
| _ClassDiagramPage → _ClassDiagramWriter | holds the writer; reads relationships, labels, cell ids | drawio/drawio_class_model.py:572-576 | R | | Held collaborator. |
| _ClassDiagramPage → DiagramArrow | creates the page's arrows | drawio/drawio_class_model.py:608, :634, :639 | R | | Composition: the page makes the arrows it draws. |
| _ClassDiagramPage → CardPlacement | places its new cards | drawio/drawio_class_model.py:681 | R | | Placement algorithm run once on the page's cards. |
| _ClassDiagramPage → ArrowRouter | routes its arrows | drawio/drawio_class_model.py:703 | R | | Routing algorithm run once on the page's cards and arrows. |
| DrawIOCleanEngineeringModel → _ClassDiagramReader / `_parse_modules` | parse hands the XML to a reader | drawio/drawio_class_model.py:136-139 | R | | Per-parse reader; the W is what the reader returns (next relationships). |
| _ClassDiagramReader → DrawIOClass / DrawIOModule | creates the cards and modules it reads | drawio/drawio_class_model.py:216, :227, :254 | R | | Composition while reading the file's own cells. |
| `_parse_modules` → DrawIOModule | builds `DrawIOModule(name='')` only to call `parse_html`, then a second module with the result | drawio/drawio_class_model.py:168, :172 | W | | Throwaway object built to reach a reader method. |
| | | | | | Owner: DrawIOModule. Should be: a class-level constructor (`DrawIOModule.from_cell(value)`) that reads a cell into one new module. Redesign: replace the two constructions with that one. |
| DrawIOModule → DrawIOClass | load_class translates a class into a Draw.io card | drawio/diagram_node.py:147-150 | R | | Translation override of Module.load_class. |
| DrawIOClass → Parameter | `parameter.save()` while writing member lines | drawio/diagram_node.py:94 | R | | Reads the parts of its own operations. |
| Drawio → DrawIOCleanEngineeringModel | creates a channel per create_diagram call and copies `previous`/`keep_positioning` onto it | drawio/drawio.py:268-271 | W | | The toolset duplicates the channel's state and rebuilds the channel per call. |
| | | | | | Owner: Drawio. Should be: composition 1 (Drawio holds one DrawIOCleanEngineeringModel). Redesign: Drawio keeps one Draw.io model whose `previous`/`keep_positioning` are the only copy; drop Drawio's duplicate fields. |
| Drawio → MarkdownCleanEngineeringModel / JsonCleanEngineeringModel / PythonCleanEngineeringModel / DrawIOCleanEngineeringModel | picks a parser class from a name→class table and builds one per call | drawio/drawio.py:276-297 | W | | A second format table beside CleanEngineering's `formats` (clean_engineering.py:46-55). |
| | | | | | Owner: CleanEngineering (its formats through `PracticeGuidance._format_adapter`). Should be: association — Drawio is handed the parsed model (or the practice's format adapter). Redesign: CleanEngineering parses the source with its own format adapter and hands the model to `create_diagram`; remove `_parse_source` and `source_format`. |
| Drawio → DrawioScanner | creates one scanner per scan call with the call's rule and root | drawio/drawio.py:309-310 | R | | One-shot run configured by the call. |
| DrawioScanner → scanner subclasses | discovers `*_scanner.py` and runs each per report | drawio/scanners/_drawio_base.py:133-151, :156-159 | R | | Rule registry by discovery; each rule runs once. |
| DrawioScanner → DrawioPage | builds a page reader for each diagram page of each file | drawio/scanners/_drawio_base.py:123 | W | | DrawioPage is a second reader of draw.io XML (boxes, class names, edge kinds) beside `_ClassDiagramReader`, `_read_positions` and `_read_edges`; `class_name_in`/`edge_kind` restate `_plain_class_name`/`_classify_edge`. |
| | | | | | Owner: DrawIOCleanEngineeringModel (its DrawIOClass cards already carry geometry). Should be: association — scanners read the Draw.io model they are handed. Redesign: give parse the positions and edge routes (cards keep geometry, arrows keep waypoints) and have scanners check that model, so one reader parses draw.io. |
| DrawioScanner → Violation | creates the named failure record | drawio/scanners/_drawio_base.py:117, :131 | R | | Named failure it raises/returns. |
| each `*Scanner` → DrawioPage | reads boxes, edges, class names of the page it is handed | drawio/scanners/*_scanner.py (e.g. base_above_derived_scanner.py:16-30) | R | | Handed per call. |
| drawio/rules → DrawioScanner | builds `DrawioScanner()` only to call `discover` | drawio/rules/__init__.py:359 | W | | Throwaway instance to reach what is a class-level registry. |
| | | | | | Owner: DrawioScanner (the class). Should be: a class method `DrawioScanner.discover()`. Redesign: make discover a classmethod; run_report and the rules module call it on the class. |
| _DrawioScannerRule → scanner subclass | per graph node, builds a scanner and re-reads the `.drawio` file named by `node.source.file` | drawio/rules/__init__.py:369-380 | W | | Re-reads a file the graph already loaded, once per OoadClass/Module/Package node on that file, so each file is scanned and reported once per node. |
| | | | | | Owner: the loaded file (its Draw.io model). Should be: association — the rule checks the Draw.io model once per file. Redesign: register the rule on the file-level node only (or the loaded DrawIOCleanEngineeringModel) so each file is scanned once. (Folding into CleanEngineering under option A.) |
| _DrawioScannerRule → CleanEngineeringGraph | its RULES/BY_SLUG are read by `language_rules("drawio")` | cdd_guidance/practices/clean_engineering/graph_practice.py:48 | R | | Registration by the rules package (folding into CleanEngineering under option A). |
| MarkdownOoadClass → MarkdownCleanEngineeringModel | parse_body builds a throwaway model, sets its `_class_order`, calls its `_parse_class`, then copies the fields into a new MarkdownOoadClass | markdown/markdown_class_model.py:205-217 | W | | Reaches through to construct a model to borrow its parser, then copies the result. |
| | | | | | Owner: MarkdownOoadClass. Should be: composition 0..* of its own Property/Operation/Relationship parts. Redesign: move `_parse_class`, `_parse_properties_and_relationships`, `_parse_operations_and_relationships`, `_strip_ce_prefix` onto MarkdownOoadClass so a class reads its own card body and creates its parts once. |
| MarkdownCleanEngineeringModel → Property | creates properties from member lines of a class card | markdown/markdown_class_model.py:744, :749 | W | | Kept W, reason corrected: the model parses a class's members (through the throwaway host above); the class is the owner. |
| | | | | | Owner: MarkdownOoadClass, composition 0..*. Redesign: as above. |
| MarkdownCleanEngineeringModel → Operation | creates operations from member lines of a class card | markdown/markdown_class_model.py:796 | W | | Kept W, reason corrected: same as Property. |
| | | | | | Owner: MarkdownOoadClass, composition 0..*. Redesign: as above. |
| MarkdownCleanEngineeringModel → CleanEngineeringModel (canonical) | `render(canonical)` calls the private `_render_cards` of another model instance, else copies it in with translate_from | markdown/markdown_class_model.py:495-502 | W | R | Reaches into another model's private renderer instead of asking that model to render. |
| | | | | | Owner: the canonical MarkdownCleanEngineeringModel. Should be: no relationship — each model renders itself. Redesign: callers call `canonical.render()`; `render` takes no second model (translation stays in `translate_from`). |
| MarkdownCleanEngineeringModel → Module | load_module translates a source module into MarkdownModule | markdown/markdown_class_model.py:285-288 | R | | Translation override of CleanEngineeringModel.load_module. |
| MarkdownCleanEngineeringModel → OoadClass | load_class translates a class into MarkdownOoadClass | markdown/markdown_class_model.py:290-293 | R | | Translation shape is right, but this method has no caller (CleanEngineeringModel has no load_class; MarkdownModule.load_class at :228 is the one used) — delete it. |
| MarkdownCleanEngineeringModel → MarkdownModule | creates modules from `#` headings | markdown/markdown_class_model.py:317, :347, :439 | R | | Composition while parsing its own text. |
| MarkdownCleanEngineeringModel / MarkdownOoadClass → ClassHeading | reads a heading into a value / builds one to write | markdown/markdown_class_model.py:125, :224, :396, :473 | R | | Value object. |
| MarkdownModule → MarkdownOoadClass | holds its classes, writes each card | markdown/markdown_class_model.py:228-231, :273-280 | R | | Composition 0..*. |
| PythonCleanEngineeringModel → OoadClass | creates a class per ClassDef of the text it parses | python/python_class_model.py:137, :165 | R | W | Composition while parsing its own text (`self._text`), kept in its module. |
| PythonCleanEngineeringModel → Property | creates a property per annotated field | python/python_class_model.py:265 | R | W | Composition while parsing its own text. |
| PythonCleanEngineeringModel → CodeBody | cuts each operation body and the module preamble from its own text | python/python_class_model.py:218-236 | R | W | The text is the model's own `self._text`; the body is a part given to the operation/module. |
| PythonCleanEngineeringModel → CodeBody | `preamble.lines_in(...)` in file_header | python/python_class_model.py:285 | R | | Acts on the body it is handed. |
| PythonCleanEngineeringModel → PythonModule | creates the file's module while parsing | python/python_class_model.py:122 | R | | Composition while parsing. |
| PythonCleanEngineeringModel → Module | load_module translates a module into PythonModule | python/python_class_model.py:108-109 | R | | Translation override. |
| PythonCleanEngineeringModel → Operation | fills most of an Operation from a FunctionDef, then `operation.load_python_function_facts(node)` fills the rest | python/python_class_model.py:178-209 | W | | Kept W, reason corrected: reading one function is split between the model and the Operation. |
| | | | | | Owner: Operation. Should be: composition 0..* (class owns operations), with the Operation reading its own function node. Redesign: one `Operation.from_python_function(node, text)` (or a PythonOperation) that does all of :178-209. |
| PythonCleanEngineeringModel → OoadClass | `class_open(oclass)`: reads name, declared_bases, stereotypes, intent to spell a Python class | python/python_class_model.py:291-297 | W | | The model spells a class it is handed; the adapter wraps OoadClass instead of subclassing it. |
| | | | | | Owner: OoadClass. Should be: composition through PythonModule of a PythonOoadClass subclass that writes itself. Redesign: add PythonOoadClass (and PythonModule.load_class) and move class_open/class_close onto it. |
| PythonCleanEngineeringModel → Property | `property_line(prop)`: reads name, type_hint | python/python_class_model.py:302-306 | W | | Same wrapper shape. |
| | | | | | Owner: Property. Redesign: PythonProperty writes its own line. |
| PythonCleanEngineeringModel → Operation | `signature`, `_decorators`, `_receiver`: reads name, parameters, return_type, is_property, is_static, is_classmethod | python/python_class_model.py:315-345 | W | | Same wrapper shape. |
| | | | | | Owner: Operation. Redesign: PythonOperation writes its own signature and decorators. |
| PythonCleanEngineeringModel → CleanEngineeringModel (canonical) | `file_header(canonical)` / `_needs_abc(canonical)` call `every_class` on a model it is handed | python/python_class_model.py:284-289, :347-352 | W | R | The channel writes a second model instead of itself (render shape from CodeCleanEngineeringModel.render). |
| | | | | | Owner: PythonCleanEngineeringModel. Should be: composition 0..* PythonModule held as its own modules. Redesign: translate the canonical model into the Python model once, then render `self`. |
| PythonModule → (Python text) | `load_source_facts`/`import_targets` re-parse the file text with `ast.parse` | python/python_class_model.py:39, :50 | W | | Re-parses text that PythonCleanEngineeringModel already parsed into a tree (graph_practice.py:273-275 parses then calls this). |
| | | | | | Owner: PythonCleanEngineeringModel (holds the tree during parse). Should be: the module's helpers and imports filled during the one parse. Redesign: parse records module helpers on each class while it walks the tree; import targets are read from the same tree once file and root are known. |
| PythonCleanEngineeringModel → ClassHead / DocumentedIntent | reads stereotypes and intent above/inside a class | python/python_class_model.py:136, :153 | R | | Value readers from class_stereotypes. |
| Python/TypeScript/Java/JavaScript models → CodeLanguage | `CodeLanguage.named(...)` held as the class's language | python:106, typescript:17, java:17, javascript:21 | R | | Named language value held once per class. |
| TypeScriptCleanEngineeringModel → OoadClass / Property / Operation | class_doc, class_intent, stereotype_decorators, interface_declaration, property_line, constructor_lines, signature spell parts it is handed | typescript/typescript_class_model.py:23-60 | W | | Wrapper shape as in Python. |
| | | | | | Owner: OoadClass/Property/Operation. Redesign: TypeScript subclasses of the parts (loaded by the TypeScript model's load_module/load_class) write their own lines. |
| JavaCleanEngineeringModel → OoadClass / Property / Operation | interface_declaration, property_line, constructor_lines, signature | java/java_class_model.py:27-61 | W | | Wrapper shape as in Python. |
| | | | | | Owner and redesign: as TypeScript. |
| JavaScriptCleanEngineeringModel → OoadClass / Property / Operation | render_class, interface_declaration, class_declaration, constructor_lines, signature | javascript/javascript_class_model.py:31-73 | W | | Wrapper shape as in Python. |
| | | | | | Owner and redesign: as TypeScript. |
| JsonCleanEngineeringModel → JsonModule | creates modules from records while parsing | json/json_class_model.py:136, :138 | R | | Composition while parsing its own text. |
| JsonModule → JsonOoadClass | from_record / load_class | json/json_class_model.py:92-95, :115 | R | | Composition. |
| JsonOoadClass → JsonProperty / JsonOperation / JsonRelationship | from_record and load_* | json/json_class_model.py:56-69, :81-84 | R | | Composition; each part reads its own record. |
| JsonCleanEngineeringModel → CleanEngineeringModel (canonical) | `render(canonical)` translates it in with translate_from, then writes self | json/json_class_model.py:147-150 | R | | Uses the base translation and writes its own state (the shape the other formats should follow). |
| JsonCleanEngineeringModel → JsonParseError | raises | json/json_class_model.py:132, :144 | R | | Named failure. |
| SketchCleanEngineeringModel → _SketchSection | builds a writer handed the canonical model; it spells every module and class | sketch/sketch_class_model.py:64, :70-104 | W | | The adapter wraps the domain parts in a helper instead of subclassing them. |
| | | | | | Owner: Module/OoadClass. Should be: composition 0..* SketchModule (composing SketchOoadClass) on the Sketch model. Redesign: SketchModule/SketchOoadClass write their own heading and fenced members; the model translates canonical in and writes itself. |
| SketchCleanEngineeringModel → Module / OoadClass / Operation / Parameter / Property | module functions create the parts while parsing | sketch/sketch_class_model.py:155, :171, :230, :265, :285-293, :336, :395-398 | R | | Composition while parsing its own text. |
| SketchCleanEngineeringModel → SketchOutline / SketchLens | reads the clean engineering section of the sketch | sketch/sketch_class_model.py:58, :134 | R | | Shared sketch reader from the Sketch action, handed the text. |
| Every format model → its own class | `parse` builds and returns a new instance instead of filling `self` | markdown:330, :420; python:121; json:133; sketch:57; drawio:152, :203 | W | | The receiver is discarded; the base `load(path)` fills `self`, so the two entry points disagree. (5 classes.) |
| | | | | | Owner: the format model instance. Should be: parse fills `self.modules` and returns `self`. Redesign: parse resets and fills self, as `CleanEngineeringModel.load` does. |

Not mine but touching this slice: `CleanEngineering → Drawio` (clean_engineering.py:60-65) was listed W "creates per call"; the code creates it once lazily and keeps it in `self._drawio` — R. `Ddd → MarkdownCleanEngineeringModel` (ddd.py:75) is in the DDD part.

### Stories: practice class, graph practice, rules, core story model

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| Stories → Format | `Format(source or self.format).is_code` built from the stored name on each call | stories.py:68 | W | – | The practice keeps its format as a string and rebuilds a Format each time it needs to ask about it. |
| ↳ W | owner: PracticeGuidance / FidelityGuidance; composition 1 | | | | Hold the current format as a `Format` (made once when the format is set), so `self.format.is_code` is a read. This is the same fix as the Format entry in section 2 of the disconnected list. |
| Stories → Format | `Format(format_name).name != "typescript"` | stories.py:92 | W | – (listed, not judged) | Same as above: a Format rebuilt from a string to compare names. |
| ↳ W | owner: PracticeGuidance; composition 1 | | | | Same redesign. Compare against the Format object the practice already holds. |
| Stories → TypeScriptStoryModel (format adapter) | `self._format_adapter(name)(tests_root=..., story_test_folder=...)` makes a new adapter on every render | stories.py:94 | W | new | A new adapter is built from settings Stories already holds, once per render call. |
| ↳ W | owner: Stories; composition 0..* (one adapter per format) | | | | Stories makes each adapter once with its `default_workspace_folder` and `story_test_folder` and keeps it. Render reads the adapter it holds. |
| Stories → StoryModel | `StoryModel.load_files(files, project)` | stories.py:76 | R | W | `load_files` is a load factory that receives the files the caller named. A new set of paths arrives with every call, so Stories has no single StoryModel it could hold. |
| Stories → Session | `self.session.repo_path` | stories.py:83 | R | new | The session is a collaborator the practice already holds. |
| Stories → PracticeOutsideSession | raises it | stories.py:85 | R | new | Raises a named failure. |
| StoriesGraph → PracticeGraph | reads `practice.graph` and `source_root` from the practice graph it is handed | graph_practice.py:40, :55-56, :70-71 | R | – | Acts on what it is handed (folding into Stories under option A). |
| StoriesGraph → Graph | reads `graph.practices`, `edited_files()`, `report_progress` | graph_practice.py:49, :73 | R | – | Acts on the graph it is handed (folding into Stories under option A). |
| StoriesGraph → GraphStoryModel | `GraphStoryModel(model).record(practice)` on each read | graph_practice.py:46 | W | new | Builds a wrapper around the StoryModel only to write it onto the graph (folding into Stories under option A). |
| ↳ W | owner: StoryModel; composition (each StoryNode is already its own graph node) | | | | `StoryModel.record(practice)`: each epic, story, scenario and step adds itself and its children. Delete GraphStoryModel (see its entries below). |
| StoriesGraph → TypeScriptStoryModel | reads every .ts file itself, then `TypeScriptStoryModel("tests").load(files)` | graph_practice.py:62-64 | W | new | Builds its own adapter with a literal `"tests"`, which ignores the Stories practice's configured adapter and `story_test_folder`. It also reads the files for the adapter and hands their text over (folding into Stories under option A). |
| ↳ W | owner: Stories (its TypeScript format adapter); association 1 | | | | After the fold, the read uses the TypeScript adapter Stories holds, and that adapter reads its own files under the root. |
| _typescript_files → TypeScriptStoryModel | `TypeScriptStoryModel("tests")` built only to call `is_story_file` | graph_practice.py:88 | W | new | A throwaway adapter is built to answer a question about a path. |
| ↳ W | owner: Stories' TypeScript adapter; association 1 | | | | Ask the adapter Stories holds. |
| StoriesGraph → StoryModel | `StoryModel.load(root)` / `load_files(edited, root)` | graph_practice.py:75-76 | R | W | A load factory called once per graph read with the root it was handed. The graph rebuilds from files, so there is no StoryModel to keep between reads (folding into Stories under option A). |
| StoriesGraph → _StoryLinks | `_StoryLinks(graph).link()` on each link | graph_practice.py:50 | W | new | A helper made for each call that then finds both practices by name (next entry) (folding into Stories under option A). |
| _StoryLinks → Graph | `graph.practice("stories")`, `graph.practice("clean_engineering")` | graph_practice.py:102-103 | W | new | Looks up both practice graphs by name string. |
| ↳ W (both) | owner: Stories; association 0..1 to Clean Engineering | | | | After the fold, Stories links its own nodes and holds the Clean Engineering practice it links to. Its link operations become operations on Stories. |
| _StoryLinks → story test files | `path.read_text` for step bodies and `function` declarations | graph_practice.py:156, :169 | W | new | Re-reads files the TypeScript model already read. The Step already keeps its `body` (CodeBody) from BraceStoryReader. |
| ↳ W | owner: Step (body), Example / Story (its file); composition 1 | | | | Read each step's calls from `step.body`, and read example sources from the Story that read the file. |
| _StoryLinks → PracticeGraph | `stories.link(...)`, `clean.link(...)` | graph_practice.py:127-146 | R | new | Adds edges through the practice graphs' own operation. |
| _StoryLinks → Epic | walks parents to the top epic | graph_practice.py:179 | R | new | Type check while walking the node's own parents. |
| StoriesGraph → GraphPractices | `GraphPractices.register(StoriesGraph(...))` at import | graph_practice.py:184 | R | – | Registers with a registry (folding into Stories under option A; the registry goes with it). |
| StoryNode → CodeBody | `self.setup = CodeBody()` | model/story_model.py:114 | R | new | A part made once and kept. |
| Examples → Example | makes an Example when a plain value is set | model/story_model.py:260 | R | new | The collection makes its own parts as they are added. |
| Examples → StoryNode | `self.scope._link(value, "examples")` | model/story_model.py:264 | R | new | Tells the owner it holds the example. |
| Scenario → Example | keeps examples as an Examples table | model/story_model.py:526 | R | – | Composition 0..*. |
| Increment → ModelChildren / Story | children list; copies the source's stories | model/story_model.py:309, :317 | R | new | Composition, copy constructor. |
| Step → ModelChildren | `self._ands = ModelChildren(...)` | model/story_model.py:375 | R | – | Part made once. |
| Step → CodeBody | `self.body = CodeBody()`; `code_key` reads `body.text` | model/story_model.py:383, :392 | R | – | Part made once and kept. |
| Step → StepType | `self.step_type.value` | model/story_model.py:426 | R | – | Held value. |
| Background → Step | copies the source's steps | model/story_model.py:474 | R | new | Copy constructor: the background makes its own parts. |
| Scenario → ModelChildren | backgrounds and steps lists | model/story_model.py:524-525 | R | – | Parts made once. |
| Scenario → Step | `self.steps.append(Step(step))` in `__init__` | model/story_model.py:535 | R | W | This is the copy constructor (`Scenario(source)`). A scenario owns its steps, so it copies the source's steps as its own. That is composition, not a missing collaborator. |
| Scenario → StepType | `StepType.WHEN` / `THEN` | model/story_model.py:569, :573 | R | – | Enum constants. |
| Epic → ModelChildren | epics and stories lists | model/story_model.py:639-640 | R | – | Parts made once. |
| Epic → Story / Epic | `append_story`; the copy constructor copies child epics and stories | model/story_model.py:648-650, :725 | R | – | Composition. |
| Epic → SourceLocation | `SourceLocation(file)` in `place_in` | model/story_model.py:737, :742 | R | new | Value object made from data it is given. |
| Story → ModelChildren / Scenario | lists; `scenario_type(scenario)` copy | model/story_model.py:826-834 | R | – | Composition. |
| StoryModel → ModelChildren / Epic | lists; `append_epic` | model/story_model.py:913, :1080 | R | – | Composition. |
| StoryModel → epic_type / story_type / increment_type | `_copy_map` copies a source map into this map's own types | model/story_model.py:941, :944 | R | new | The subclass names its part types; the map copies into them. |
| StoryModel → graph's StoryModel | `_copy_map_on_graph` searches `practice.nodes["StoryModel"]` and copies the first map it finds | model/story_model.py:949 | W | new | Finds its source by type name in the graph instead of being handed it. Only specs construct `StoryModel(graph)`. |
| ↳ W | owner: the caller that holds the source map; association 1 | | | | Callers pass the source map (`StoryModel(source, graph=...)`). Drop the graph search. |
| StoryModel → JsonStoryModel / MarkdownStoryModel | `load` imports its own subclasses and tries each one's `from_workspace` | model/story_model.py:960-977 | W | new | The base class keeps its own map of formats to subclasses (a lazy import back into the subclasses, which is a dependency cycle), duplicating the `formats` Stories holds. |
| StoryModel → DrawIOStoryModel / MarkdownStoryModel | `_story_map_file` picks the class by file suffix and passes it the file text | model/story_model.py:1047-1055 | W | new | Same: the base class picks the format and reads the file for it. |
| StoryModel → PythonStory / TypeScriptStory / JavaScriptStory | `story_test_type(path).load_all(path.read_text())` | model/story_model.py:1029, :1109-1126 | W | new | Same: a suffix-to-class map kept in the base module. |
| ↳ W (three above) | owner: Stories (its format adapters); association 0..* | | | | Stories, or the format adapter it holds for each format, decides which adapter reads a file. StoryModel then only merges the maps and scenarios it is given, with no imports of its subclasses. |
| is_story_map_file → Name | `Name(path.stem).title_slug` | model/story_model.py:1134 | R | new | Value made from a file name; no object owns that name. |
| CodeStoryNode → Name | `Name(self.name)` in slug, snake, pascal and camel, on every call | model/code_story_model.py:84-93 | W | new | The node rebuilds a Name from its own name each time it needs a form of it. |
| ↳ W | owner: the story node; composition 1 | | | | Keep the name as a `Name` property on the node, so the node reads `self.name.title_slug`. |
| CodeScenario → Background / Step | makes them while parsing its own body | model/code_story_model.py:133, :166-178 | R | new | A node making its children from its own text is composition. |
| CodeStory → scenario_type | `add_scenario`, and `fill` uses `example_names` / `backgrounds_in` / `scenario_blocks` | model/code_story_model.py:248, :277-286 | R | new | The story makes its own scenarios from its own content. |
| CodeStoryModel → its own class | `_copy_of` (`type(self)(canonical, ...)`); `parse` (`type(self)(root).load(...)`) | model/code_story_model.py:381, :631 | R | new | Copy and parse factories of its own kind. |
| CodeStoryModel → render_call_graph_block | passes `step.call_graph` into a helper function | model/code_story_model.py:458 | W | new | Hands a Step's data to a helper. |
| ↳ W | owner: Step; composition 1 (a CallGraph) | | | | The Step holds a CallGraph object that renders itself (`step.call_graph.as_comment_block()`), instead of a bare list of CallGraphEntry. |
| CodeStoryModel → CodeBody / WrittenBlock | `as_read`, `lines_in`, `in_language_of`, `is_in` | model/code_story_model.py:411, :427, :624 | R | new | Asks values the node holds. |
| CodeStoryModel → CodeEpic | `CodeEpic(epic_name).slug()` | model/code_story_model.py:661 | W | new | Builds a throwaway epic only to turn a name into a slug. |
| ↳ W | owner: Name; none to hold | | | | Use `Name(epic_name).title_slug` directly, or the epic made on the next line. |
| CodeStoryModel → epic_type | `epic_for` / `sub_epic_for` make epics while reading its own files | model/code_story_model.py:645, :721 | R | new | Composition while parsing. |
| CodeStoryModel → story_type / SourceLocation / read_code | `_take_stories` | model/code_story_model.py:684-690 | R | new | Composition while parsing; value object. |
| BraceScenario → BraceScenario | `cls(name="").calls_in(body)` | model/brace_story.py:67 | W | new | Builds an empty scenario only to call an instance method on text that belongs to a background. |
| ↳ W | owner: Background; composition | | | | The Background reads its own steps from its body, or `calls_in` becomes a class-level parse. No throwaway scenario. |
| BraceScenario → Background | makes backgrounds while parsing | model/brace_story.py:70 | R | new | Composition while parsing. |
| BraceStoryModel → BraceStoryReader | `BraceStoryReader(self.language, content, unescape).read(stories, path)` | model/brace_story.py:122 | W | new | The reader writes `written`, `setup` and `body` onto Story, Scenario and Step objects from outside. The logic for the code a node was written with sits off the node that owns it. |
| ↳ W | owner: Story / Scenario / Step (the code each was written with); composition 1 each | | | | The reader only finds the blocks. Each node reads its own block (`story.take_written(block)`, and so on down to steps). |
| BraceStoryReader → BraceCall | one BraceCall per matched call | model/brace_story_reader.py:124, :129, :141 | R | new | Parts made while parsing its own text. |
| StoryReader / BraceStoryReader → WrittenBlock | builds the file's and each block's WrittenBlock | model/story_reader.py:27; model/brace_story_reader.py:148 | R | new | Value made from the lines it is reading. |
| DiagramStoryNode → DiagramStoryModel | `_layout` returns `DiagramStoryModel()`, an empty map, when the node has no map | model/diagram_story_model.py:22 | W | new | Builds an empty map on each call only to read layout numbers. drawio/miro nodes call it at drawio/nodes.py:101, :161, :223 and miro/nodes.py:160, :217. |
| ↳ W | owner: DiagramStoryModel (the owning map); association 0..1 through parent | | | | The node reads layout from the map it sits on. With no map it uses the class-level constants, without building a map. |
| DiagramStoryNode → DiagramStoryModel | `base_width`, `row_height` class constants | model/diagram_story_model.py:31-50 | R | new | Constants. |
| DiagramStoryModel → DiagramEpic | `nested_row_y`, `bar_height`, `depth_gap` | model/diagram_story_model.py:170, :179, :186 | R | – | Constants. |
| DiagramStoryModel → DiagramStory | `story_type = DiagramStory` | model/diagram_story_model.py:154 | R | – | Names its part type. |
| GraphStoryModel → StoryModel | holds `self.model` and writes it onto a graph | model/graph_story_model.py:87 | W | new | An adapter that wraps the domain class instead of being it. A StoryNode is already a ModelNode, so it is its own graph node. |
| ↳ W | owner: StoryModel; composition | | | | Move `record` onto StoryModel and each node type. Delete GraphStoryModel. |
| GraphStoryModel ↔ _StoryGraphRecording | `record` makes a recording, which then calls GraphStoryModel's private `_file_under`, `_file`, `_name_span`, `_source_span`, `_ensure_source`, `_epic_evidence` and `_file_facts` | model/graph_story_model.py:94, :209-262 | W | new | One job is split across two classes that reach into each other's private operations. |
| ↳ W | owner: each story node; composition | | | | Each node records itself and its children (`epic.record(practice, parent)`). The progress count stays on the StoryModel. |
| GraphStoryModel → story files | `_file_lines` re-reads each story's file from disk | model/graph_story_model.py:165 | W | new | Re-reads files the format model already read. |
| ↳ W | owner: Story (the file it was read from); composition 1 | | | | The Story keeps its file facts (exports, imports, classes) when it is read. |
| _StoryGraphRecording → PracticeGraph | `practice.add`, `practice.link` | model/graph_story_model.py:218, :292 | R | new | Acts on the practice graph it is handed. |
| _StoryGraphRecording → Example node | `practice.add_named("Example", ..., name, source)` for each example name | model/graph_story_model.py:270-273 | W | new | Makes a bare node from the example's name, although the Scenario already holds that Example as a StoryNode. |
| ↳ W | owner: Scenario (its Examples); composition 0..* | | | | Add the Example objects themselves as nodes, the same way epics, stories and steps are added. |
| _StoryGraphRecording → SourceLocation / load_map_facts | stamps the source and asks each node to load its facts | model/graph_story_model.py:214-215 | R | new | Value object; asks the node to act on itself. |
| PracticeGraphRule subclasses → Node / RuleCheckContext | `get_fact`, `context.children`, `child_count` | rules/*.py | R | new | Read the node and context handed to `check`. |
| GivenNamesComplexStateRootFirst (_owned_parts) → Graph | `context.practice.graph.practices.get("ddd")` | rules/scenarios.py:196 | W | new | Finds the DDD practice by name string. |
| ↳ W | owner: Stories (option A); association 0..1 to DDD | | | | The Stories practice holds the DDD practice whose aggregates it checks, and the rule reads it through the context. |
| _parent_story → PracticeGraph | `context.practice.edges.get("scenarios")` | rules/scenarios.py:278 | R | new | Walks the practice graph it is handed. |
| DomainFixtureExampleFiles → Format | `Format.from_extension(suffix)` | rules/acceptance_tests.py:49 | R | new | Factory from a file extension; nothing owns that value. |
| rules/__init__ → each rule class | each rule made once in `RULES`, read as `BY_SLUG` by `rules_in` | rules/__init__.py:36-65 | R | new | Registry made at import. |

### Stories: format adapters

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| JsonStoryModel → StoryModel (handed in) | render reads the epics, stories, and increments of a story map handed in | json/nodes.py:86-97 | W | new | The adapter does not become the map (no `JsonStoryModel(story_map)`); it reads another object's data. |
| | *owner: StoryModel / JsonStoryModel. Should be: the JSON map IS the story map (inheritance plus the copy constructor, as DrawIO does). Redesign: render copies the canonical with `type(self)(canonical)` and writes itself; `save()` = render of self.* | | | | |
| JsonStoryModel → JsonEpic | creates each epic while parsing its own document | json/nodes.py:240 | R | new | The root makes its children from its own text (composition 0..*). |
| JsonStoryModel → JsonStory, JsonScenario, Step, Background | builds every story, scenario, step, and background from dicts | json/nodes.py:249-304 | W | new | The node subclasses are empty; reading a story or scenario record lives on the root, not on the node that owns the record. |
| | *owner: JsonEpic/JsonStory/JsonScenario. Should be composition per level. Redesign: each Json node reads its own record (`JsonStory.from_record`) and makes its own children; the root only makes epics.* | | | | |
| JsonStoryModel → Story (increment's stories) | makes a new plain `Story(name)` for each name an increment lists | json/nodes.py:316 | W | new | The increment gets copies by name, not the map's own Story. |
| | *owner: Increment. Should be association 0..* to the map's existing Story. Redesign: resolve the names against `every_story()` after the epics are read.* | | | | |
| JsonStoryModel → SourceLocation | stamps its file onto each node | json/nodes.py:115 | R | new | A value made once per file and kept on the nodes. |
| MarkdownStoryModel → StoryModel (handed in) | render writes the map handed in through `_StoryMapWriter` | markdown/nodes.py:1018-1036 | W | new | As for JSON: no copy into a MarkdownStoryModel; it writes another object's data. |
| | *owner: MarkdownStoryModel. Should be inheritance plus copy constructor. Redesign: `type(self)(canonical)` and render self; `save()` already calls `render(self)`.* | | | | |
| MarkdownStoryModel → StoryMapLinks | `StoryMapLinks.from_workspace(workspace)` walks the folder on each render | markdown/nodes.py:1029 | W | new | Builds the links from a path string per call. |
| | *owner: the story map placed in a workspace. Should be association 0..1 (the map holds the links for the folder it is placed in). Redesign: give the map its folder once (placed in), and make the links once from it.* | | | | |
| MarkdownStoryModel → _StoryMapWriter | makes a writer per render and hands it the story map | markdown/nodes.py:1030-1035 | W | new | A helper is handed the owner's data. |
| | *owner: MarkdownEpic/MarkdownStory. Redesign: each Markdown node writes its own outline/heading lines; the writer goes.* | | | | |
| _StoryMapWriter → StoryMapLinks | holds the links it was given and asks `story_file(story)` | markdown/nodes.py:876, 933 | R | new | A collaborator handed in at construction and held. |
| _StoryMapWriter → MarkdownScenario.render_scenarios | hands a story's scenarios and backgrounds to a class operation | markdown/nodes.py:916 | W | new | A story's data passed to a class helper. |
| | *owner: MarkdownStory. Redesign: MarkdownStory renders its own backgrounds and scenarios.* | | | | |
| _StoryMapWriter, MarkdownStoryModel, MarkdownIncrement → MarkdownScenario() | a blank scenario is made only to call `strip_backticks` / `_strip_markup` | markdown/nodes.py:95, 101, 937, 1064 | W | new | Throwaway object built to reach a text helper. |
| | *owner: none (text rule). Redesign: one module-level markup function, or a property on the node whose text it is.* | | | | |
| MarkdownStoryModel → MarkdownEpic, MarkdownStory, MarkdownScenario | creates them while parsing its own story-map text | markdown/nodes.py:1376, 1395, 1402, 1416, 1427, 1475, 1488, 1503 | R | new | Composition: the root makes its children from its own text. |
| MarkdownStoryModel → MarkdownScenario (as parser) | `parser = MarkdownScenario()` then `parse_text`, and takes its `document_parts`, `tree_heading`, `document_examples` | markdown/nodes.py:1142-1161 | W | new | A blank scenario holds parse state for a whole document and creates its sibling scenarios. |
| | *owner: MarkdownStoryModel (the scenarios document) / MarkdownStory. Should be composition: the document makes stories, a story makes its scenarios. Redesign: move `parse_text` state to a document-level reader owned by MarkdownStoryModel, so MarkdownScenario only reads its own block.* | | | | |
| MarkdownScenario → MarkdownScenario, MarkdownStep, Background, _StorySection | `parse_text` creates the scenarios, steps, backgrounds, and story sections of a file | markdown/nodes.py:232-267, 319, 543 | W | new | Same: the scenario class is the file parser (see above). Steps made by the scenario they belong to would be R. |
| MarkdownStoryModel → MarkdownScenario.from_workspace, MarkdownStory.load_scenarios | reads every scenario file under the folder, then hands the full list to each story, which keeps those whose `story_name` matches its name | markdown/nodes.py:1005-1007, 760-790 | W | new | Matching by a name string across a re-read of the folder. |
| | *owner: MarkdownStory. Should be composition 0..* (a story owns the scenarios in its own story file). Redesign: link each story to its own story file (StoryMapLinks already finds it) and let the story read it.* | | | | |
| MarkdownStoryModel → MarkdownIncrement.from_workspace | reads the increments file in its own folder | markdown/nodes.py:1010 | R | new | The map makes its own increments from its own folder. |
| MarkdownIncrement → Story (increment's stories) | appends the story names as strings | markdown/nodes.py:115 | W | new | An increment holds names, not the map's Story objects. |
| | *owner: Increment. Should be association 0..* to the map's Story. Redesign: resolve names to `every_story()` when the map takes the increments.* | | | | |
| MarkdownStoryModel → _ScenarioDocument | kept on the map when it was read from a scenarios document | markdown/nodes.py:956, 1161 | R | new | Composition 0..1, made once at parse. |
| _ScenarioDocument → MarkdownEpic | holds the epic the document's stories sit on | markdown/nodes.py:821-824 | R | new | Association 1, held. |
| MarkdownStoryModel → _StepLines | made per render of a document, story, or scenario and handed `parts` the node holds | markdown/nodes.py:1176, 1200, 1223 | W | new | Rendering a node's lines lives on the root and a helper, not on the node. |
| | *owner: MarkdownStory/MarkdownScenario (they hold `markdown_parts`). Redesign: each node writes its own lines from the parts it holds.* | | | | |
| StoryMapLinks → _Anchors | counts anchors during one `entries` call | markdown/links.py:132 | R | new | A local counter for one pass. |
| DomainModelLinks → _Anchors | same during `headings` | markdown/links.py:184 | R | new | Local counter (but DomainModelLinks is spec-only, see D). |
| MarkdownScenario → DomainModelLinks | `render_scenarios(domain_links=...)` asks it to link terms | markdown/nodes.py:600-628 | R | new | Collaborator handed in; no production caller passes one. |
| DrawIOStoryModel → DrawIOStoryModel (copy of canonical) | `type(self)(canonical)` then draws itself | drawio/nodes.py:381 | R | new | A subclass made from the domain map: the intended shape. |
| DrawIOStoryModel → StoryMapLinks | `from_workspace(workspace)` per render | drawio/nodes.py:380 | W | new | Same as Markdown: built per call from a path. Owner and redesign as above. |
| DrawIOStoryModel / Vertex → StoryMapLinks.entries | asks for an `id(node)` → anchor dict, then hands dict and links to each vertex | drawio/nodes.py:390-392, 340-347 | W | new | The vertex is handed a lookup table keyed by object identity. |
| | *owner: StoryMapLinks. Redesign: `links.entry_for(node)`; the vertex asks the links it is given for its own node.* | | | | |
| DrawIOEpic, DrawIOStory → DrawIOStoryModel.Vertex | each node draws its own cells | drawio/nodes.py:108, 113, 207, 222, 230, 238 | R | new | Composition: a node creates its own drawing parts. |
| DrawIOStory/DrawIOEpic → DiagramStoryModel (`_layout`) | reads layout heights and y from the owning map | diagram_story_model.py:19 (used drawio/nodes.py:97) | R | new | Reaches its own owner through `parent`. |
| DrawIOStoryModel → _PlacedCell, DrawIOEpic, DrawIOStory | `load` reads each cell and creates the epics and stories it places | drawio/nodes.py:411-470 | R | new | Composition while parsing its own text (into a new DrawIOStoryModel, not self). |
| DrawIOIncrement → DrawIOStoryModel | `save`/`load` make a blank DrawIOStoryModel to write or read a thin slice of a map handed in | drawio/nodes.py:53, 57 | W | new | An increment reaches out to construct a model; spec-only operations. |
| | *owner: DrawIOStoryModel (it holds its increments). Redesign: thin-slice save/load are DrawIOStoryModel instance operations on its own increments; drop the class operations.* | | | | |
| DrawIOStoryModel → DrawIOIncrement, DrawIOStory | `_read_thin_slice` makes increments and new placeholder stories by name | drawio/nodes.py:601, 610 | W | new | Placeholder stories, not the map's stories (as JSON). |
| MiroStoryModel → MiroEpic, MiroStory | `load` creates them from its own SVG | miro/nodes.py:365-378 | R | new | Composition while parsing. |
| MiroIncrement → StoryModel (handed in) | class `save(story_map)` writes the thin-slice table of a map handed in | miro/nodes.py:53 | W | new | An increment class renders a whole map; spec-only. |
| | *owner: MiroStoryModel. Redesign: an instance operation on MiroStoryModel over its own increments, each increment writing its own `table_row`.* | | | | |
| MiroIncrement → MiroStory | `from_cells` makes placeholder stories by name | miro/nodes.py:47 | W | new | As JSON: should reference the map's stories. |
| SketchStoryModel → SketchLens | `SketchLens.of("stories")` finds the Stories practice's lens by name on each parse | sketch/sketch_story_model.py:39 | W | new | Lookup by name string of a lens the owning practice already defines (`Stories.sketch_titles`). |
| | *owner: Stories (practice). Should be association 1: the sketch format holds the lens of the practice it belongs to. Redesign: Stories hands its lens to the sketch adapter when it makes it.* | | | | |
| SketchStoryModel → SketchOutline | wraps the sketch text being parsed | sketch/sketch_story_model.py:39 | R | new | A reader over the input text; the input belongs to the call. |
| SketchStoryModel → _SketchReader | hands a new plain StoryModel to a reader that builds plain Epic/Story/Scenario/Step/Background/Increment | sketch/sketch_story_model.py:38-40, 99-166 | W | new | No Sketch node subclasses; the parse logic sits in a helper handed the model. |
| | *owner: SketchStoryModel and its nodes. Should be inheritance (SketchEpic, SketchStory) plus composition. Redesign: sketch nodes read their own lines; the reader goes.* | | | | |
| SketchStoryModel → _SketchWriter | writes the map handed in (or self) | sketch/sketch_story_model.py:45 | W | new | Helper handed the owner's data; also wraps rather than copies the map handed in. |
| | *owner: SketchStoryModel. Redesign: copy the canonical into a SketchStoryModel and let each node write its lines.* | | | | |
| CodeStoryModel subclasses (Python, TypeScript, Java, JavaScript) → own type (copy of canonical) | `render` → `_copy_of(canonical)` = `type(self)(canonical, tests_root=...)`, then `save()` | code_story_model.py:374, 381; typescript/typescript_story_model.py:52 | R | new | A subclass made from the domain map, with its own node types through `epic_type`/`story_type`/`scenario_type`. |
| PythonStoryModel, JavaStoryModel, JavaScriptStoryModel, TypeScriptStoryModel → their Story type | `story_type.load(content, slug)` per story file | python/python_story_model.py:51; java/java_story_model.py:66; javascript/javascript_story_model.py:76; typescript/typescript_story_model.py:142 | R | new | The story reads its own file text (composition). |
| PythonStory, TypeScriptStory, JavaScriptStory, JavaStory → their Scenario type | `fill` → `add_scenario` → `scenario_type(...)` and `read(body)` | code_story_model.py:247-251, 276-293 | R | new | A story creates its scenarios from its own text. |
| PythonStoryModel → PythonStoryReader | makes a reader per file to read the same text a second time and stamp `written` onto the stories | python/python_story_model.py:55 | W | new | Re-reads text PythonStory.load already parsed; the reader is handed the stories' data. |
| | *owner: PythonStory (it already holds its file text). Should be composition of what it read. Redesign: the story keeps the code block it was read with while it reads itself, so a second pass is not needed. Same shape: BraceStoryModel → BraceStoryReader (brace_story.py:122, top-level slice).* | | | | |
| PythonScenario → PythonScenario | `backgrounds_in` makes `cls(name="")` only to call `calls_in` | python/nodes.py:40 | W | new | Throwaway object for a text helper. Redesign: make `calls_in` a class-level reading of the text, or have the background read its own steps. |
| PythonStory, TypeScriptStory, JavaScriptStory, JavaStory → their StoryModel | class `create(story)` builds a blank story model and a copy of the story to call `story_text` | python/nodes.py:99; typescript/nodes.py:64; javascript/nodes.py:47; java/nodes.py:110 | W | new | A story constructs a model per call to render itself. |
| | *owner: the CodeStoryModel the story sits in (its parent chain). Should be association 1 (story → its map). Redesign: story text is an instance operation on the language story that asks its own map for spelling; only JavaScriptStory.create has a production caller (ux/scripts/emit_story_javascript.py:68).* | | | | |
| JavaStoryModel → JavaScenario.create | class operation handed each scenario to render | java/java_story_model.py:38 | W | new | The scenarios are JavaScenario instances already (Story copy uses `scenario_type`, story_model.py:833); the class operation takes the instance's data. Redesign: instance operation `scenario.lines()`. |
| TypeScriptEpic → CodeEpic | builds a CodeEpic from a word to get `pascal()`/`slug()` | typescript/nodes.py:72, 78 | W | new | Throwaway node built for naming; use `Name(...)` directly. |
| TypeScriptStoryModel → story_file functions | passes its own folder to module functions for the seed path and import path | typescript/typescript_story_model.py:38, 48, 66 | W | new | State the model holds handed to free functions. Redesign: properties on TypeScriptStoryModel (TypeScriptStory.create's default import also reads them). |
| TypeScriptStoryModel, JavaScriptStoryModel → seed files | `_story_test_text` / `_story_test_js` read seeds/story-test.{ts,js} for a new tree | typescript/nodes.py:116-124; javascript/javascript_story_model.py:82-89 | R | new | Reads its own shipped file once per save. |
| StoriesGraph → TypeScriptStoryModel | `TypeScriptStoryModel("tests").load(files)`; `_typescript_files` builds one only to ask `is_story_file` | graph_practice.py:64, 88 | W | new | Built per call from the string "tests"; the second exists only to call a filename test (folding into Stories under option A). Owner: Stories, which already holds its TypeScript adapter; redesign: use the practice's own adapter. |

Inbound uses from the top-level Stories files (judged by that part; listed here as evidence of use): StoryModel.load → JsonStoryModel.from_workspace, MarkdownStoryModel.from_workspace (story_model.py:960-975, 1061-1076); StoryModel._story_map_file → MarkdownStoryModel.from_workspace, `DrawIOStoryModel().load` (story_model.py:1046-1058); story_test_type → PythonStory, TypeScriptStory, JavaScriptStory (story_model.py:1109-1126).

### DDD

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| Ddd → format adapters (`formats` dict) | names its five adapters by module path; `PracticeGuidance._format_adapter` imports them lazily | ddd.py:43-58; harness/guidance/guidance.py:506 | R | new | The registry route the framework uses for every practice; the classes named there are the practice's published channels. |
| Ddd → Format | `Format(source_format).name` per call | ddd.py:69 | W | — (W kept) | Builds a value from a string each call. |
| Ddd → MarkdownCleanEngineeringModel | `MarkdownCleanEngineeringModel().parse(...)` per call, second parse of the same text | ddd.py:71-75 | W | — (W kept; redesign changed) | Reaches past its own markdown adapter to construct another practice's adapter. |
| Ddd → clean_engineering_bridge (`to_clean_engineering`, `from_clean_engineering`) | copies the map into a new Clean Engineering model and back | ddd.py:81-92 | W | new | Copies a model whose nodes already are Clean Engineering nodes. |
| Ddd → Clean Engineering model classes (`_python_generics`) | rewrites properties' and operations' type hints of another object, picked by class-name prefix | ddd.py:89-90, 102-114 | W | new | Logic on another object's data, chosen by a name string. |
| DddGraph → GraphPractices (register) | registers at import | graph_practice.py:175 | R | — | A registry it registers with (folding into Ddd under option A). |
| DddGraph → GraphPractices.named("clean_engineering") | looks up Clean Engineering's graph practice by name to merge its rules | graph_practice.py:30 | W | R | Finds a peer it `extends` by name string in a class-level registry instead of holding it (folding into Ddd under option A). |
| DddGraph → _DddReading | new reader per `read` call, handed the practice graph | graph_practice.py:34 | W | new | Per-call helper doing the practice's own reading (folding into Ddd under option A). |
| _DddReading → PracticeGraph (`add`, `link`, `root_node`, `graph.report_progress`) | adds and links the nodes it reads | graph_practice.py:50, 60-62, 88-90, 101-105, 117 | R | new | Asks the graph it was given to hold the nodes (folding into Ddd under option A). |
| _DddReading → Clean Engineering's PracticeGraph | `self.practice.graph.practices.get("clean_engineering")`, reads its `OoadClass` nodes | graph_practice.py:72-73 | W | new | Reaches through the graph to another practice by name string (folding into Ddd under option A). |
| _DddReading → TacticalClass | `TacticalClass(cls.name, cls.get_fact("stereotypes"))` per class | graph_practice.py:78 | W | new | Builds a wrapper from strings the class node already holds (folding into Ddd under option A). |
| _DddReading → Aggregate | creates one per folder, the aggregate loads its own folder facts | graph_practice.py:86-87 | R | new | Reading folders into the nodes they are; the node reads its own folder (folding into Ddd under option A). |
| _bounded_contexts / _unmarked_context → BoundedContext | creates the context, which reads its own `.context/bounded-context.md` | graph_practice.py:150-151, 160-161 | R | new | The node reads its own resource (folding into Ddd under option A). |
| _tactical_block → Node (copy of the CE class node) | new `Node`, `block.data.update(cls.facts)` | graph_practice.py:132-134 | W | new | Copies Clean Engineering's class node into a second node (folding into Ddd under option A). |
| _tactical_block → tactical_facts | free function computes facts from a parsed class's operations | graph_practice.py:134; model/nodes.py:105-123 | W | new | Owner's data passed into a helper (folding into Ddd under option A). |
| _DddReading._text → source file | re-reads the class's file to find `// foreign Name` | graph_practice.py:113-124 | W | new | Re-reads a file Clean Engineering's parser already read (folding into Ddd under option A). |
| tactical_facts → TacticalClass | `TacticalClass(parsed.name, parsed.stereotypes)` per call | model/nodes.py:109, 122 | W | new | Builds a wrapper from strings the class holds. |
| BoundedContextMap → BoundedContext | loads, appends, owns its contexts | model/nodes.py:475-494 | R | new | Composition. |
| BoundedContextMap (copy constructor) → BoundedContext(source=) | copies each context as the base type before subclasses set their types; aggregates are not copied | model/nodes.py:456-461, 353-355 | W | new | Copies instead of holding; the copy silently drops aggregates. |
| BoundedContext → Aggregate, nested BoundedContext | `ModelChildren`, `append_*`, `load_*` | model/nodes.py:359-360, 386-443 | R | new | Composition. |
| BoundedContext (graph constructor) → another BoundedContext on the graph | clones the children of a same-named context already on the graph | model/nodes.py:363-375 | W | new | Copies another object's children instead of referring to that object. |
| Aggregate → Entity (root) | `take_root` sets `is_root`, `aggregate` | model/nodes.py:318-329 | R | new | The aggregate holds its root (composition 1). |
| Entity → InvariantObject | loads its own invariant objects | model/nodes.py:150-162 | R | new | Composition. |
| DomainEvent → Property (subject) | holds its subject property | model/nodes.py:237-252 | R | new | Composition. |
| MarkdownBoundedContextMap → MarkdownBoundedContext | reads each `## ` heading into a context | model/markdown/nodes.py:300-310 | R | new | The map parsing its own text into its children. |
| MarkdownBoundedContextMap → MarkdownAggregate | `_fill_context` / `_read_aggregate` cut each context's aggregate sections and create them | model/markdown/nodes.py:409-440 | W | new | The map parses the context's lines for it; `BoundedContext` already has `has_more_aggregate` / `get_next_aggregate_from_file` for the context to do this itself. |
| MarkdownBoundedContextMap → DomainEvent, DomainService (`wire_events`, `_consumer`) | wires the event map section onto producer roots; one service per name per map | model/markdown/nodes.py:346-351, 461-486 | R | new | The map owns its event-map section. |
| MarkdownBoundedContextMap.render → `type(self)(source)` | copies a non-markdown map into a markdown one before saving | model/markdown/nodes.py:319-324 | W | new | Copy conversion; because of the copy constructor above, the copy has base `BoundedContext`s that `save` skips, so it writes no contexts. |
| MarkdownAggregate → ClassCard (`split_cards`, `read_card`) | parses its own `####` sections into cards | model/markdown/nodes.py:96-98 | R | new | The aggregate parsing its own text (the card itself is a W below). |
| MarkdownAggregate → MarkdownEntity, Operation, DomainEvent (`_open_root`) | builds its root from its own lines | model/markdown/nodes.py:167-175 | R | new | Composition while parsing its own text. |
| MarkdownAggregate → MarkdownIntegration | builds its arcs from its own `Integrations:` lines | model/markdown/nodes.py:177-201 | R | new | Composition while parsing its own text. |
| MarkdownAggregate.take_root_card → MarkdownInvariantObject | re-creates every member card as an invariant object by name | model/markdown/nodes.py:131-133 | W | new | Copies the member classes into name-only stand-ins on the root. |
| MarkdownAggregate.take_root_card → Repository.accesses | points each repository at the root | model/markdown/nodes.py:134-136 | R | new | Association 1 from the repository to its root. |
| MarkdownEntity → MarkdownInvariantObject | reads its own member lines | model/markdown/nodes.py:78-84 | R | new | Composition. |
| ClassCard → Entity / ValueObject / Repository / DomainService / Specification / Factory (`building_block_type`) | the card constructs the building-block node and wraps it as `card.node`, keeping stereotypes and invariants beside it | model/markdown/class_cards.py:31-45; model/nodes.py:272-287 | W | new | A format wrapper around the domain class instead of a subclass of it. |
| _SketchFence → ClassCard | per-fence reader builds the entity's and repository's cards | model/markdown/class_cards.py:208-264 | W | new | Per-call helper building wrappers. |
| to_clean_engineering → CleanEngineeringModel, Module, OoadClass | builds new Clean Engineering objects and clones each card's properties and operations | clean_engineering_bridge.py:29-44, 77-83 | W | new | Copies nodes that already are `OoadClass`/`Module`. |
| from_clean_engineering → ClassCard, MarkdownBoundedContextMap, MarkdownBoundedContext, MarkdownAggregate, MarkdownEntity | rebuilds the map from each class's intent text, cloning properties and operations | clean_engineering_bridge.py:47-70, 86-99, 131-156 | W | new | Copies the Clean Engineering model back into a parallel model, with place encoded in intent text. |
| _take_integrations → MarkdownIntegration | parses arcs out of a class's intent text | clean_engineering_bridge.py:186-203 | W | new | Integrations stored as doc-comment text on another object and re-parsed. |
| SketchDddModel → SketchOutline, SketchLens | reads the ddd section of the incoming sketch | model/sketch/sketch_ddd_model.py:70 | R | new | The sketch action's reader of the input document. |
| SketchDddModel → _SketchReader | per-parse reader building `MarkdownBoundedContext`, `MarkdownAggregate`, cards | model/sketch/sketch_ddd_model.py:68-71, 94-201 | W | new | Helper builds markdown nodes; no sketch node reads its own lines. |
| SketchDddModel → _SketchWriter | per-render writer walking the model's contexts, aggregates, cards | model/sketch/sketch_ddd_model.py:73-75, 204-266 | W | new | Writes other objects' data from outside. |
| DrawIOBoundedContextMap → DrawnDiagram | parses the incoming draw.io text | model/drawio/drawio_bounded_context_map.py:118 | R | new | The input document. |
| DrawnDiagram → DrawnCell; DrawnCell → _LabelText | the document holds its cells; a cell reads its label | model/drawio/drawn_diagram.py:65, 28 | R | new | Composition. |
| DrawIOBoundedContextMap → DrawIOAggregateModel | new writer per render and new reader per parse | model/drawio/drawio_bounded_context_map.py:113, 119 | W | new | Builds a separate drawing object per call instead of the nodes drawing themselves. |
| DrawIOBoundedContextMap → _ContextMapReader | per-parse reader building markdown nodes from cells | model/drawio/drawio_bounded_context_map.py:119, 134-174 | W | new | DrawIO reads into markdown types through a helper. |
| DrawIOBoundedContextMap → ContextLayout, _DiagramWriter | hands the model's contexts to a layout and a writer per render | model/drawio/drawio_bounded_context_map.py:124-131, 177-447 | W | new | Owner's data passed into helpers. |
| ContextLayout → _IntegrationLink | copies each integration's target into a record | model/drawio/drawio_bounded_context_map.py:194-201 | W | new | Copies data the `Integration` holds (`target_parts`). |
| _DiagramWriter → _StraightRoutes, _EdgePlan, _CellRecord, _Route | its own routing parts | model/drawio/drawio_bounded_context_map.py:369, 377, 427, 476 | R | new | Parts of the writer's one job (they go when the writer does). |
| DrawIOAggregateModel → _AggregateViewReader | per-parse reader building markdown nodes and cards | model/drawio/drawio_aggregate_model.py:127, 247-296 | W | new | Helper builds markdown nodes; DrawIO nodes do not read their own cells. |
| DrawIOAggregateModel → MarkdownAggregate cards (ClassCard) | draws each aggregate from its `root_card`, `repository`, `member_cards` | model/drawio/drawio_aggregate_model.py:154-196, 309-310 | W | new | Draws other objects' data from outside. |
| DrawIOAggregateModel → DiagramCard, DiagramArrow, Geometry | builds Clean Engineering's diagram records from card data | model/drawio/drawio_aggregate_model.py:203, 211, 215 | W | new | Builds records instead of the nodes being `DiagramClass`/`DiagramModule`. |
| DrawIOAggregateModel → ArrowRouter | asks Clean Engineering's router to route the arrows | model/drawio/drawio_aggregate_model.py:219 | R | new | A shared routing collaborator asked to act, as Clean Engineering uses it. |
| DrawIOAggregateModel → arrow_style, EDGE_STYLES | calls a Clean Engineering drawio function with `DiagramCard`s where it expects `DrawIOClass`es | model/drawio/drawio_aggregate_model.py:223; clean_engineering/model/drawio/drawio_class_model.py:738 | W | new | Borrows a module function of another adapter instead of inheriting its drawing. |
| rules (9 classes) → building-block graph node facts | read `peer_private_operations`, `tactical_stereotype`, `operation_shapes`, … | rules/tactical.py:27-144 | R | new | A rule checks the node it is given. |
| rules → tactical_helpers functions | `public_operation_names(node)`, `is_screen_driver_class(node)` … compute from the node's facts | rules/tactical.py:7-13; rules/tactical_helpers.py:31-55 | W | new | Owner's data passed into module functions. |
| RULES / BY_SLUG → GraphPractices (`rules_in`) | the practice's rules list read by package path | rules/__init__.py:15-27; harness/graph/graph_practice.py:25 | R | new | The registry route for graph rules. |
| rule_examples (spec support) → graph_practice._tactical_block | spec helper calls a private function of the graph reader | rules/rule_examples.py:21-33 | W | new | Spec-only; reaches a private function. |

**Owner, relationship it should be, and redesign for each W**

- Ddd → Format: owner the active `FidelityGuidance` (as in the cross-repo Format item). Composition 1 (`fidelity.format`). Ddd reads the format it already holds.
- Ddd → MarkdownCleanEngineeringModel: owner `MarkdownBoundedContextMap`. Inheritance (the map is a Clean Engineering model). Make `BoundedContextMap` a `CleanEngineeringModel` and `MarkdownBoundedContextMap` a `MarkdownCleanEngineeringModel`, so one markdown adapter reads a plain class model or an aggregate model and `_parse_content` needs no override.
- Ddd → bridge, and both bridge functions, and `_take_integrations`: owner `BoundedContextMap`. Inheritance (`BoundedContextMap(CleanEngineeringModel)`, aggregates are its modules). The code adapters then render the map's own `OoadClass` nodes; `Aggregate` keeps its integrations as typed `Integration` parts that the code adapters write, so nothing is copied or parsed out of intent text.
- Ddd → `_python_generics`: owner `PythonCleanEngineeringModel`. The python adapter writes generic types in Python form itself; no type-name sniffing on the practice.
- DddGraph → `GraphPractices.named`: owner `Ddd`. Association 1 to its Clean Engineering companion (`clean_engineering_companion` already exists on `PracticeGuidance`). Under option A, Ddd asks the companion for its rules.
- DddGraph → _DddReading, and _DddReading → Clean Engineering's PracticeGraph: owner `Ddd` (after option A). Association 1 to the Clean Engineering practice it extends. Ddd reads its own nodes from the class nodes the Clean Engineering practice hands over, instead of finding them by name.
- _DddReading / tactical_facts → TacticalClass: owner `OoadClass`. The class's building-block kind becomes a property of the class (it already holds `stereotypes` and `peer_names`), so no wrapper is built per call.
- _tactical_block (copy) and tactical_facts: owner the DDD building-block node. Inheritance: the graph node for a building block is an `Entity` / `ValueObject` / `Repository` (each an `OoadClass`) that computes its own tactical facts from its own operations, instead of a generic `Node` filled with copied facts.
- _DddReading._text: owner the Clean Engineering class node (its parser). The parser records `// foreign Name` references as a fact or property on the class when it reads the file; DDD reads that.
- BoundedContextMap copy constructor and `MarkdownBoundedContextMap.render` copy: owner `BoundedContextMap`. With one model shared by every adapter, render takes the map as it is; drop the copy constructors (they also drop aggregates today).
- BoundedContext graph constructor clone: owner the context already on the graph. Association 1 to that context instead of cloning its children.
- MarkdownBoundedContextMap → MarkdownAggregate: owner `MarkdownBoundedContext`. Composition 0..*. The context receives its lines and implements `has_more_aggregate` / `get_next_aggregate_from_file` (hooks already on `BoundedContext`).
- MarkdownAggregate → MarkdownInvariantObject copies: owner `Entity` (root). Association 0..* to the member building blocks the aggregate already holds, instead of name-only stand-ins.
- ClassCard: owner each building block (`Entity`, `ValueObject`, `Repository`, `DomainService`, `Specification`, `Factory`). Inheritance: markdown subclasses of each building block (or one markdown mixin on them, like `MarkdownDomainNode`) read and write their own `####` card; stereotypes stay in `OoadClass.stereotypes` and invariants become a property of the node. `ClassCard` and `building_block_type`'s card use go away.
- _SketchFence, _SketchReader, _SketchWriter: owner `SketchDddModel`. Inheritance: sketch subclasses of the context, aggregate, and building blocks (as Stories and Clean Engineering do per format) each read and write their own sketch lines; composition from map to contexts to aggregates.
- DrawIOBoundedContextMap → DrawIOAggregateModel, _ContextMapReader, ContextLayout, _DiagramWriter, and _AggregateViewReader, DrawIOAggregateModel → cards / DiagramCard / arrow_style, ContextLayout → _IntegrationLink: owner `DrawIOBoundedContextMap`. Inheritance: subclass `BoundedContextMap` (not the markdown map) and Clean Engineering's diagram trunk; DrawIO context and aggregate subclasses of `BoundedContext`/`Aggregate` plus `DiagramModule`, and DrawIO building blocks of each block plus `DiagramClass`, each placing, drawing, and reading its own cells; arrows come from `Integration.target_parts` directly.
- rules → tactical_helpers: owner the building-block node. Its public operation names, lifecycle operations, and screen-driver shape become properties of the node (`Operation` already knows its name and access), and rules read them.
- rule_examples → `_tactical_block`: spec support; goes when `_tactical_block` does (the spec then builds the building-block node the practice builds).

### UX, BDD, agent BDD, output_folder.py

| # | from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|---|
| 1 | Ux → PracticeCatalogue | `PracticeCatalogue.create(key)` when Ux has no session | ux/ux.py:63 | W | - | builds a fresh practice from a key on every call, without the caller's session, fidelity or format |
| 2 | Ux → Session (its practices) | `self.session.practices[key].guideline` | ux/ux.py:63 | R | new | asks the session it works in for that session's own Stories or Clean Engineering practice |
| 3 | UxGraph → GraphPractices | `register(UxGraph("ux", ...))` at import | ux/graph_practice.py:28 | R | - | registers with the registry at import (folding into Ux under option A) |
| 4 | UxNode → PracticeGraph "ux" | `_graph_practice = "ux"`, looked up by `graph.practice(name)` in ModelNode | ux/model/ux_node.py:14; harness/graph/model_node.py:87 | W | new | every UX node finds its practice graph by a name string |
| 5 | UxMap → ReferencePaths | creates two in `__init__` and keeps them | ux/model/ux_map.py:56-57 | R | new | composition 1 each: story and object references |
| 6 | UxMap → Transitions, ContentTypes, NavComponents | creates each in `__init__` | ux/model/ux_map.py:59-61 | R | new | composition 1 each |
| 7 | UxMap → UxContext | creates and links in `__init__` | ux/model/ux_map.py:62-63 | R | new | composition 1 |
| 8 | UxMap → Screen | `screens` ModelChildren, `append_screen` | ux/model/ux_map.py:58, :113 | R | new | composition 0..* |
| 9 | UxMap → another UxMap on the graph | `create(graph)` builds a new map and `_copy_screens_on_graph` copies the other map's screen names | ux/model/ux_map.py:70-71, :88-93 | W | new | "the map already on that graph" is answered with a copy, not that map |
| 10 | UxComponentCollection → ModelChildren | creates its item list on the owner | ux/model/collections.py:21 | R | new | composition 1 |
| 11 | Control, Region, Screen → their children | `ModelChildren` for interactions, controls, regions | ux/model/nodes.py:77, :123, :161 | R | new | composition 0..* |
| 12 | Screen → StoryLink | `StoryLink.from_item` in `_show`, kept in `_story_links` | ux/model/nodes.py:224 | R | new | composition 0..* |
| 13 | StoryLink → PracticeGraph node stores | `_candidates` walks `graph.practices.values()` then `practice.nodes.get(type)` | ux/model/story_link.py:54 | W | new | reaches through the graph into every practice's name-keyed node store |
| 14 | StoryDemoControl → StoryStep | `story_steps_from(...)` in `__init__` | ux/model/nodes.py:110 | R | new | composition 0..* of value objects |
| 15 | Screen → Name | `Name(name).title_slug` | ux/model/nodes.py:151 | R | new | value object |
| 16 | Transition, Interaction, NavComponent → Screen | hold `from_screen`/`to_screen`, `destination`, `destinations` | ux/model/nodes.py:244-262, :42-57, :275-283 | R | new | association to the Screen itself |
| 17 | MarkdownUxMap → MarkdownContextReader | made per parse, fills the new map | ux/model/markdown/nodes.py:27 | R | new | parse-scoped reader that composes the map's context from its own text |
| 18 | DrawioUxMap → DrawioUxMapReader | made per parse, fills the new map | ux/model/drawio/nodes.py:69 | R | new | same as 17 |
| 19 | DrawioUxMap → JsonUxMap | `JsonUxMap.create().parse(...)` when the text is JSON | ux/model/drawio/nodes.py:64 | W | new | the draw.io format builds the JSON format per call to read text that is not draw.io |
| 20 | DrawioUxMap → cli_state functions | `ux_map_to_cli_state(ux_map, ...)` reads every screen, region, control and transition | ux/model/drawio/nodes.py:78; ux/model/drawio/cli_state.py:25-90 | W | new | module functions take the map's data apart outside the map |
| 21 | DrawioUxMap → drawio_ux.mjs CLI | `subprocess.run(["node", ...])` | ux/model/drawio/nodes.py:79, :86 | R | new | external program |
| 22 | JsonUxMap → JsonUxMapReader | made per parse, fills the new map | ux/model/json/nodes.py:27 | R | new | same as 17 |
| 23 | JsonUxMap → JsonUxMapWriter | `JsonUxMapWriter().map_record(ux_map)` | ux/model/json/nodes.py:30 | W | new | a stateless writer built per call and handed the whole map |
| 24 | HtmlUxMap → JsonUxMap | `JsonUxMap.create().parse(...)` and `.render(ux_map)` | ux/model/html/nodes.py:33, :59 | W | new | the HTML page carries the JSON document, yet builds a JSON map per call to read and write it |
| 25 | HtmlUxMap → Control, StoryDemoControl | module functions `_render_control`, `_interaction_attrs`, `_story_demo_attrs` read each control's fields | ux/model/html/nodes.py:90, :116-200 | W | new | the control's HTML is decided outside the control from its data |
| 26 | HtmlUxMap → mockup_shell.html | reads the template on render | ux/model/html/nodes.py:36 | R | new | template asset |
| 27 | each UX format adapter → the UxMap handed to `render(ux_map)` | adapter instance is empty (`create()` with no data), render reads another map | ux/model/json/nodes.py:29 (same in drawio, html, markdown, claude_design) | W | new | the adapter acts as a helper over another map's data; the convention is set by `PracticeGuidance._render` (harness/guidance/guidance.py:539) |
| 28 | ClaudeDesignStoryModel → ClaudeDesignUxMap | classmethods `pages`, `boards`, `prototype_names`, class attributes `page`, `folder`, fed `self.screens` | ux/model/claude_design/story_canvas.py:127-128, :182, :189, :287 | W | new | the story model holds a bare screen list and passes it to classmethods of the UX format |
| 29 | ClaudeDesignStoryModel → JsonUxMap | `JsonUxMap.from_workspace(workspace)` reads `ux.json` when no screens are passed | ux/model/claude_design/story_canvas.py:385 | W | new | re-reads the file the UX map owns instead of receiving the map |
| 30 | ClaudeDesignStoryModel → DesignCanvas | `canvas()` builds a new DesignCanvas on each call from its own name; `files()` calls it | ux/model/claude_design/story_canvas.py:179, :175 | W | new | per-call construction of what should be the model's part |
| 31 | ClaudeDesignStoryModel → canvas project files | `_screen_files`, `_fixture_scripts`, `_stylesheets`, `_blank` glob and read `workspace/project/...` | ux/model/claude_design/story_canvas.py:350, :359, :369, :379 | W | new | reads the canvas project's boards, stylesheets and images from disk instead of asking the canvas that owns that project |
| 32 | ClaudeDesignStoryModel → ClaudeDesignStoryModel | `render` builds `type(self)(source, workspace=..., screens=..., sources=...)` | ux/model/claude_design/story_canvas.py:166 | R | new | converts the story map into this format's node types, the Stories format convention |
| 33 | ClaudeDesignStory → Screen | `screen.lists(self)` | ux/model/claude_design/story_canvas.py:106 | R | new | asks each screen whether it shows the story |
| 34 | `shown_on` (used by ClaudeDesignStoryModel, ClaudeDesignStory) → PracticeGraph | `node.practice.edges_from("shownOn", node)` | ux/model/claude_design/story_canvas.py:394 | W | new | reaches through the node to its practice graph's edge store |
| 35 | ClaudeDesignEpic, ClaudeDesignStory, ClaudeDesignStoryModel → design_canvas drawing functions | `box`, `artboard`, `thumbnail`, `stem`, `LOOK` | ux/model/claude_design/story_canvas.py:67, :97, :257 | R | new | shared drawing functions and constants |
| 36 | ScreenStoryBudget → RuleCheckContext | `context.child_count(node, ("shows",))` | ux/rules/screen_rules.py:17 | R | new | asks the context it is handed |
| 37 | UX rules → GraphPractice | listed in `RULES`/`BY_SLUG`, read by `rules_in` | ux/rules/__init__.py:5-6; harness/graph/graph_practice.py:25 | R | new | registry of rules read by module path |
| 38 | emit_story_javascript script → Story, Scenario, Step, JavaScriptStory | builds a Story from a Python dict, then `JavaScriptStory.create(story)` | ux/scripts/emit_story_javascript.py:34-58, :68 | W | new | parses the story dict itself beside the Stories practice's own Python and JavaScript formats; no caller (only `.context/module-context.md` names it) |
| 39 | BddGraph → PracticeGraph | `practice.source_root`, `practice.graph.source_files`, `report_progress` | bdd/graph_practice.py:36-41 | R | - | acts on the practice graph it is handed (folding into Bdd under option A) |
| 40 | BddGraph → Graph | `graph.practices` membership test in `link` | bdd/graph_practice.py:45 | R | - | acts on the graph it is handed (folding into Bdd under option A) |
| 41 | BddGraph → GraphPractices | `register(BddGraph("bdd", ...))` at import | bdd/graph_practice.py:186 | R | - | registry (folding into Bdd under option A) |
| 42 | BddGraph `_add_spec` → PythonBddModel, TypeScriptBddModel | `(PythonBddModel() if suffix == ".py" else TypeScriptBddModel()).parse_code(text)` | bdd/graph_practice.py:57 | W | new | picks the language model by file suffix, beside Bdd's own `formats` map (folding into Bdd under option A) |
| 43 | BddGraph `_add_spec` → PracticeGraph | `practice.add`, `practice.link` for spec and behavior nodes | bdd/graph_practice.py:64-71 | R | new | adds nodes to the graph it is handed (folding into Bdd under option A) |
| 44 | BddGraph → _ObservationLinks | `_ObservationLinks(graph).link()` | bdd/graph_practice.py:46 | R | new | one linking pass over the graph handed in (folding into Bdd under option A) |
| 45 | _ObservationLinks → PracticeGraph "bdd", "clean_engineering" | `graph.practice("bdd")`, `graph.practice("clean_engineering")`, then `.nodes`, `.by_id` | bdd/graph_practice.py:88-91 | W | new | finds both practices by name and walks their node stores (folding into Bdd under option A) |
| 46 | _ObservationLinks → spec files on disk | `path.read_text()` for every spec file during `link` | bdd/graph_practice.py:103 | W | new | re-reads text `_add_spec` already read into the observations (folding into Bdd under option A) |
| 47 | _ObservationLinks → PracticeGraph (bdd and clean) | `self.bdd.link("invokes", ...)`, `self.clean.link("invokedBy", ...)` | bdd/graph_practice.py:118-119 | R | new | records edges on the graphs it works on |
| 48 | BehaviorNode, BddModel → PracticeGraph "bdd" | `_graph_practice = "bdd"` looked up by name in ModelNode | bdd/model/nodes.py:43; bdd/model/bdd_model.py:20 | W | new | same as 4 |
| 49 | BddModel → _SketchReader | `_SketchReader().read(text)` in `parse` | bdd/model/bdd_model.py:49 | R | new | parse-scoped reader composing the model's own descriptions |
| 50 | _SketchReader → Description, Context, Observation, CallGraphEntry | creates them while reading lines | bdd/model/bdd_model.py:186-240 | R | new | composition while parsing |
| 51 | BddModel → another Spec on the graph | `_copy_descriptions_on_graph` clones the other spec's descriptions | bdd/model/bdd_model.py:31 | W | new | same as 9 |
| 52 | BddModel → spec_source functions, `private_probe_in_text` | `load_source_facts(text)` | bdd/model/bdd_model.py:56-65 | R | new | pure functions over the spec text it is loading |
| 53 | BehaviorNode → CodeBody, WrittenBlock | `setup`, `written` | bdd/model/nodes.py:50-51 | R | new | composition 1 |
| 54 | Observation → CallGraphEntry, CodeBody | `call_graph`, `body` | bdd/model/nodes.py:118-120 | R | new | composition |
| 55 | SketchBddModel → SketchOutline | `SketchOutline(text)` | bdd/model/sketch/sketch_bdd_model.py:14 | R | new | outline of the text it is parsing |
| 56 | SketchBddModel → SketchLens → PracticeCatalogue | `SketchLens.of("bdd")` twice per parse, which looks up `PracticeCatalogue.practice_class("bdd").sketch_titles` | bdd/model/sketch/sketch_bdd_model.py:15-16; cdd_guidance/actions/sketch/sketch_outline.py:17 | W | new | finds its own practice's sketch titles by key on every parse |
| 57 | PythonBddModel, TypeScriptBddModel → CodeLanguage | `CodeLanguage.named(...)` class attribute | bdd/model/code_spec_model.py:198, :284 | R | new | looked up once when the class is defined |
| 58 | CodeBddModel → CodeBddModel | `type(self)().parse(previous)` in `render` | bdd/model/code_spec_model.py:52 | R | new | parses the target file's previous text in its own format |
| 59 | PythonBddModel, TypeScriptBddModel → Description, Context, Observation | `_behavior_node(...)` while parsing | bdd/model/code_spec_model.py:256, :351, :379 | R | new | composition while parsing own text |
| 60 | GraphBddModel → SavedGraph | `SavedGraph.from_text(text).restored_graph()` | bdd/model/graph_bdd_model.py:32 | R | new | reads its own input format |
| 61 | GraphBddModel → PracticeGraph "bdd", "clean_engineering" | `graph.practice(name)`, `.nodes`, `root_node.get_fact("model_members")` | bdd/model/graph_bdd_model.py:33-34, :104, :109 | W | new | finds practices by name and reads the Clean Engineering model's members out of a fact dictionary |
| 62 | BDD rules → GraphPractice | `SPEC_RULES` in `RULES`/`BY_SLUG`, read by `rules_in`; each rule reads `node.get_fact` | bdd/rules/__init__.py:5-6; bdd/rules/spec_rules.py:45 | R | new | registry of rules; each checks the node it is handed |
| 63 | AgentBdd → Bdd | `Bdd(format=self.format)` inside `generate_output` | agent_bdd/agent_bdd.py:22 | W | - | a new Bdd per call, without the session's fidelity |
| 64 | AgentBdd → Generate | `Generate(self.session).generate(...)` | agent_bdd/agent_bdd.py:22 | R | W | an action is made with the session it acts on, as every other caller does (space/session/session_probe.py:57); nothing holds action objects |
| 65 | `agent()` → AgentBddConf | `AgentBddConf().configure()` | agent_bdd/agent_block.py:197 | R | new | process setup when a spec opens an agent |
| 66 | `agent()` → ChatAgentBlock, CliAgentBlock | chooses the class, `opened(...)` | agent_bdd/agent_block.py:199-203 | R | new | factory for the block the spec uses |
| 67 | AgentBlock → YamlFence, HarnessLog | made in `__init__` and kept | agent_bdd/agent_block.py:45-46 | R | new | composition 1 each |
| 68 | AgentBlock → ToolsRunYaml | `ToolsRunYaml(self._workspace, prefix)` in `instruct_use_tool`; `yaml_from_prompt` makes another `ToolsRunYaml()` | agent_bdd/agent_block.py:83, :89; agent_bdd/agent_bdd_common.py:482 | W | new | builds the reader per call from the block's own workspace |
| 69 | AgentBlock → ToolsetInvoke (via `build_run_request`, `invoke_run_request`) | builds a request dict from keyword arguments, which `ToolsetInvoke.create` re-reads | agent_bdd/agent_block.py:106-107; agent_bdd/agent_bdd_common.py:497-518 | W | new | round-trips its own arguments through a dict |
| 70 | AgentBlock → JudgeResult, RunResponse | `JudgeResult.from_stdout`, `RunResponse.from_cli_output` | agent_bdd/agent_block.py:150, :160 | R | new | value objects parsed from output |
| 71 | ChatAgentBlock → ChatAgentBlock (judge) | new block on the `-judge.json` session for each judgement | agent_bdd/agent_chat_bdd.py:21 | R | new | the judge runs in its own session by design |
| 72 | CliAgentBlock → AgentSession | `AgentSession.from_workspace` kept as `_session`; a fresh one per judgement | agent_bdd/agent_cli_bdd.py:273, :295 | R | new | held session; fresh judge session by design |
| 73 | CliAgentBlock, AgentSession → CursorCli | `CursorCli()` / `CursorCli(resume=session.chat_id, ...)` built per call | agent_bdd/agent_cli_bdd.py:276, :321; agent_bdd/agent_bdd_common.py:309, :319 | W | new | the command object is rebuilt each call from the session's chat id |
| 74 | CliAgentBlock → _StreamBuckets | one per run | agent_bdd/agent_cli_bdd.py:301 | R | new | per-run collector of the process's output |
| 75 | _StreamBuckets → ToolsRunYaml, _ShellCapture | made in `__init__`; captures appended | agent_bdd/agent_cli_bdd.py:44, :145, :170 | R | new | composition |
| 76 | AgentSession → HarnessLog, cursor-agent CLI | `HarnessLog(...)`; `subprocess.run(args)` | agent_bdd/agent_bdd_common.py:278, :342 | R | new | composition; external program |
| 77 | ToolsRunYaml → YamlFence | made in `__init__` | agent_bdd/agent_bdd_common.py:401 | R | new | composition 1 |
| 78 | ToolsRunYaml → `invoke_run_request` | `run_request` | agent_bdd/agent_bdd_common.py:472 | R | new | asks the in-process invoke to run the request |
| 79 | `invoke_run_request` → ToolRunDeadline, ToolsetInvoke | per request | agent_bdd/agent_bdd_common.py:591-593 | R | new | one timed run per request |
| 80 | ToolRunDeadline → _TimedAttempt | per run | agent_bdd/agent_bdd_common.py:608 | R | new | the attempt is the run's own record |
| 81 | ToolsetInvoke → AgentToolSet | `AgentToolSet.instantiate({"toolset": path, ...})` | agent_bdd/agent_bdd_common.py:511 | R | new | the run request names its toolset by the published reference, the way the MCP host is called |
| 82 | ToolsetInvoke → Sessions | `Sessions(project).named(name)` | agent_bdd/agent_bdd_common.py:526 | W | new | builds the project's session registry per call from a path |
| 83 | ToolsetInvoke → AgentInstructions, AgentOperation | `instructions[name].expand`, `member.invoke` | agent_bdd/agent_bdd_common.py:545, :583 | R | new | asks the toolset's own operations to run |
| 84 | RunResponse → YamlFence | `YamlFence().load_fenced(text)` | agent_bdd/agent_bdd_common.py:240 | R | new | parses text it is given; YamlFence holds only the fence language |
| 85 | AgentBddConf → RepositoryToolsets | `RepositoryToolsets(repo_root).ensure_import_path()` | agent_bdd/conf.py:40 | R | new | process setup |
| 86 | `stage_invoke_commands` → UserHome, SpecServer | builds both side by side, `home.enter()`, `server.install()` | agent_bdd/spec_helpers.py:100-107 | W | new | spec support; the server's home is built beside the server |
| 87 | `stage_invoke_commands` → Installer, AgentToolSet | `Installer(...).install([...])` | agent_bdd/spec_helpers.py:98-104 | R | new | fixture composition root (spec support) |

**W: owner, relationship it should be, redesign**

- **1 Ux → PracticeCatalogue.** Owner: the Session's practices. Association 1 (Ux → the session's JavaScript-writing practice). Make Ux require its session for `ensure_javascript`, or have the caller hand it the Stories / Clean Engineering practice; drop the catalogue fallback that makes a sessionless copy.
- **4, 48 UX and BDD nodes → practice graph by name.** Owner: Graph (aggregation 1..* of practices, `.context/repo-model-disconnected.md` section 1). Under option A the node reaches its practice through the graph that aggregates practice objects, not by `_graph_practice` string.
- **9, 51 UxMap / BddModel copying the map or spec already on the graph.** Owner: the existing UxMap / Spec node on the graph. Association 1. `create(graph)` should return that node (found through the Graph's aggregation of the practice) instead of a new map holding copied screen names or cloned descriptions.
- **13 StoryLink, 34 `shown_on`, 45 and 61 name lookups into practice node stores.** Owner: Graph (and each node for its own edges). Ask the Graph for nodes of a type and the node for its `shownOn` edges, so callers stop reaching through `graph.practices[...].nodes` and `node.practice.edges_from`.
- **19 DrawioUxMap → JsonUxMap.** Owner: Ux (the practice chooses the adapter from `source`). Delete the JSON fallback; callers that hold JSON pass `source="json"`.
- **20 DrawioUxMap → cli_state.** Owner: DrawioUxMap. Make the CLI state an operation of the map (`self.cli_state()`) over its own screens and transitions, with region and screen pieces on draw.io subclasses of the nodes if needed.
- **23 JsonUxMap → JsonUxMapWriter.** Owner: JsonUxMap. Move `map_record` and the screen/control records onto JsonUxMap (or JSON subclasses of the nodes) so the map writes itself; drop the stateless writer.
- **24 HtmlUxMap → JsonUxMap.** Owner: JsonUxMap. Generalization: HtmlUxMap should subclass JsonUxMap, because the page carries the JSON document; parse and render call `super()` for the embedded JSON.
- **25 HtmlUxMap → Control.** Owner: Control / StoryDemoControl. Give the HTML format its own control subclass (as Stories does for its format nodes) that renders its markup and data attributes.
- **27 format adapters → the UxMap handed to render.** Owner: the UxMap being rendered. Convert the canonical map into the target format class once and let it render itself (`render()` with no model argument); the change belongs in `PracticeGuidance._render`, so it applies to every practice.
- **28, 29 ClaudeDesignStoryModel → ClaudeDesignUxMap / JsonUxMap.** Owner: the UX map (a ClaudeDesignUxMap). Association 1: the story model holds the ClaudeDesignUxMap it is drawn with, received from the caller (or the session's Ux), and asks it for `pages()` and `boards()` as instance operations over its own screens; drop the classmethods fed a screen list and the `ux.json` re-read.
- **30 ClaudeDesignStoryModel → DesignCanvas.** Owner: ClaudeDesignStoryModel. Composition 1: build the canvas once when the model is made (render already makes a new model per render) and keep it; `files()` asks the held canvas.
- **31 ClaudeDesignStoryModel → canvas project files.** Owner: DesignCanvas (the canvas project). Give DesignCanvas its project root so it answers which screen boards, stylesheets and fixture bundle it already has; the story model asks its held canvas.
- **38 emit_story_javascript.** Owner: Stories practice. Use `Stories.render("javascript", ..., source="python")` (what `Ux.ensure_javascript` already does), or delete the script: nothing calls it.
- **42 BddGraph → PythonBddModel / TypeScriptBddModel by suffix.** Owner: Bdd (its `formats` map). Under option A, `Bdd.read` asks its own format adapter for the file's language instead of a second suffix switch.
- **46 _ObservationLinks re-reads spec files.** Owner: Observation (and its enclosing Description/Context). Each behavior node keeps its span text, or the member names it reaches, when `_add_spec` reads it; linking uses that instead of reading the file again.
- **56 SketchBddModel → SketchLens.of("bdd").** Owner: Bdd (`sketch_titles`). Build the lens once from `Bdd.sketch_titles` (a class attribute on SketchBddModel) or have Bdd hand it over; no catalogue lookup per parse.
- **61 GraphBddModel reads `model_members`.** Owner: the Clean Engineering model on the graph. Ask the Clean Engineering practice (aggregated by Graph) for a member's interactions and return type instead of reading a fact dictionary on its root.
- **63 AgentBdd → Bdd.** Owner: Session (its practices). Association 1 through the session: call `Generate(self.session).generate(["bdd"])` so the session's own Bdd, with its fidelity, is generated.
- **68 AgentBlock → ToolsRunYaml.** Owner: AgentBlock. Composition 1: make one ToolsRunYaml for the block's workspace in `__init__`; `yaml_from_prompt` and `run_request` are asked of it.
- **69 AgentBlock → ToolsetInvoke through a dict.** Owner: AgentBlock. Build the ToolsetInvoke straight from `run_toolset`'s arguments; keep the dict form only for requests read from a YAML prompt.
- **73 CursorCli rebuilt per call.** Owner: AgentSession. Composition 1: AgentSession holds its CursorCli (resumed on its chat id) and answers `command(prompt)`; CliAgentBlock asks the session.
- **82 ToolsetInvoke → Sessions.** Owner: the project the block works in. Hand ToolsetInvoke the project's Sessions (or the named Session) from the block instead of building the registry from a path per request.
- **86 UserHome beside SpecServer.** Owner: SpecServer (harness/mcp/spec_support.py). Composition 1: SpecServer holds the UserHome it serves from and enters/leaves it in `install`/`stop`.

## 2. Every class has a use

### Clean Engineering: practice class, graph practice, rules, core class model

| class | file:line | used by (inbound) | uses (outbound) | build time | verdict |
|---|---|---|---|---|---|
| CleanEngineering | clean_engineering.py:19 | cdd_guidance/context_setup/context_setup.py:73 | PracticeGuidance, Drawio, format adapters | `@agent_toolset`, `@agent_instructions`; `PracticeCatalogue._REFS` harness/guidance/practice_catalogue.py:35; catalog card | ok |
| CleanEngineeringGraph | graph_practice.py:29 | GraphPractices (registered :425) | _CodeReading, _ModelReading, rules_in | imported by `GraphPractices._discover` harness/graph/graph_practice.py:195-206 | ok (folding into CleanEngineering under option A) |
| _CodeReading | graph_practice.py:56 | CleanEngineeringGraph.read :52 | PracticeGraph, Module, language models, CFamilyParse | — | ok |
| _ModelReading | graph_practice.py:214 | CleanEngineeringGraph.read :53 | MarkdownCleanEngineeringModel, ModelDescriptions | — | ok |
| LimitOperationParameters | rules/limit_operation_parameters.py:38 | RULES rules/__init__.py:34 | Node facts | `rules_in` harness/graph/graph_practice.py:25 | ok |
| NamedSeamAndConstraint | rules/module_graph_rules.py:15 | RULES :35 | Node facts | rules_in | ok |
| PublicSeamOnly | rules/module_graph_rules.py:30 | RULES :36 | Node facts, `registered` | rules_in | ok |
| MissingModuleContext | rules/module_graph_rules.py:50 | RULES :37 | Node facts, file system | rules_in | ok |
| LanguageModulesOneSection | rules/module_graph_rules.py:81 | RULES :38 | Node facts | rules_in | ok |
| ModulesNotModelBlocks | rules/module_graph_rules.py:95 | RULES :39 | Node facts | rules_in | ok |
| DomainNounsOnly | rules/module_naming_rules.py:21 | RULES :54 | Node facts | rules_in | ok |
| NoModulePerClass | rules/module_naming_rules.py:37 | RULES :55 | practice nodes | rules_in | ok |
| NoPrototypeSwapping | rules/no_prototype_swapping.py:14 | RULES :57 | Node facts | rules_in | ok |
| OneWayDeps | rules/practice_wide_rules.py:29 | RULES :49 | practice nodes, `registered` | rules_in | ok |
| LowCoupling | rules/practice_wide_rules.py:56 | RULES :51 | `registered` | rules_in | ok |
| DeepModule | rules/practice_wide_rules.py:78 | RULES :52 | practice nodes, file system | rules_in | ok |
| ExtensionsLiveWithTheDomain | rules/practice_wide_rules.py:154 | RULES :53 | Node facts | rules_in | ok |
| SourceParses | rules/practice_wide_rules.py:172 | RULES :50 | Node facts | rules_in | ok |
| WriteInteractions | rules/write_interactions.py:16 | RULES :56 | Node facts | rules_in | ok |
| ClassGraph | model/rules_shared/class_graph.py:26 | coupling_rules.py:55, :90, :185 | practice nodes and edges | — | ok |
| KeepClassesSingleResponsibility | model/rules_shared/class_rules.py:36 | RULES :41 | Node facts | rules_in | ok |
| HideInnerDetails | model/rules_shared/coupling_rules.py:25 | RULES :44 | Node facts | rules_in | ok |
| PutLogicOnOwningResource | model/rules_shared/coupling_rules.py:35 | RULES :45 | Node facts | rules_in | ok |
| ShapeClassesAroundResources | model/rules_shared/coupling_rules.py:48 | RULES :46 | ClassGraph | rules_in | ok |
| DoNotInventParallelObjectModels | model/rules_shared/coupling_rules.py:82 | RULES :47 | ClassGraph | rules_in | ok |
| LayerSeparation | model/rules_shared/coupling_rules.py:178 | RULES :48 | ClassGraph, `registered` | rules_in | ok |
| UseExplicitDependencies | model/rules_shared/operation_checks.py:94 | CODE_RULES :315 → RULES :58 | Node facts | rules_in | ok |
| OperationMeasureRule | model/rules_shared/operation_checks.py:109 | base of LimitOperationParameters and four measure rules | — | — | ok (base) |
| KeepOperationsSmall | operation_checks.py:133 | CODE_RULES :317 | Node facts | rules_in | ok |
| SimplifyControlFlow | operation_checks.py:144 | CODE_RULES :318 | Node facts | rules_in | ok |
| UseExceptionsProperly | operation_checks.py:159 | CODE_RULES :319 | Node facts | rules_in | ok |
| NeverSwallowExceptions | operation_checks.py:168 | CODE_RULES :320 | Node facts | rules_in | ok |
| ProvideMeaningfulContext | operation_checks.py:177 | CODE_RULES :321 | Node facts | rules_in | ok |
| AvoidVagueParameterNames | operation_checks.py:187 | CODE_RULES :322 | Node facts | rules_in | ok |
| UseIntentionRevealingNames | operation_checks.py:207 | CODE_RULES :323 | Node facts | rules_in | ok |
| UseConsistentNaming | operation_checks.py:236 | CODE_RULES :316 | Node facts | rules_in | ok |
| PreferInstanceOperations | operation_checks.py:261 | CODE_RULES :324 | Node facts | rules_in | ok |
| UsePropertyNotAccessor | operation_checks.py:276 | CODE_RULES :325 | Node facts | rules_in | ok |
| EliminateDuplication | operation_checks.py:293 | CODE_RULES :326 | practice Operation nodes | rules_in | ok |
| KeepOperationsSingleResponsibility | model/rules_shared/operation_semantics.py:31 | SEMANTIC_RULES :89 → CODE_RULES | Node facts | rules_in | ok |
| ErrorsOutOfExistence | operation_semantics.py:51 | SEMANTIC_RULES :90 | Node facts | rules_in | ok |
| StateChangeReturnsRecordOrNamedFailure | operation_semantics.py:63 | SEMANTIC_RULES :91 | Node facts | rules_in | ok |
| DomainExceptionCarriesContext | operation_semantics.py:75 | SEMANTIC_RULES :92 | Node facts | rules_in | ok |
| PreferClassOperations | model/rules_shared/prefer_class_operations.py:14 | RULES :40 | Node facts | rules_in | ok |
| UseTypedSignatures | model/rules_shared/typed_and_comments.py:21 | RULES :42 | Node facts, type_refs | rules_in | ok |
| LimitComments | typed_and_comments.py:39 | RULES :43 | Node facts | rules_in | ok |
| UnreadableSource | model/base_class_model.py:32 | raised model/python/python_class_model.py:117; caught graph_practice.py:121 | — | — | ok |
| OoadNode | model/base_class_model.py:105 | base of every Clean Engineering node | UpdateReport, ChildCollectionPair, TranslationError | node type via `_graph_practice` | ok (base) |
| OoadClass | model/base_class_model.py:178 | Module.load_class :538; c_family_parse.py:109 (class_factory from code_class_model.py:222); python model | ModelChildren, Property, Operation, Relationship, SourceText | node type `OoadClass` in model/schema.yaml and `class_types` graph_practice.py:32 | ok |
| File | model/base_class_model.py:416 | none | — | none | **D** |
| Module | model/base_class_model.py:434 | graph_practice.py:97, :274; CleanEngineeringModel.load_module :731; c_family_parse.py:85 | CodeBody, ModelChildren, OoadClass, ModuleContext | node type `Module` (anchor_types graph_practice.py:36) | ok |
| CleanEngineeringModel | model/base_class_model.py:634 | base of every format adapter; code_class_model.py:22; model_descriptions.py:31 | ModelChildren, Module | node type | ok |
| CFamilyParse | model/c_family_parse.py:51 | code_class_model.py:220; graph_practice.py:419 | OoadClass, Operation, Property, Module, CodeBody, ClassHead | — | ok |
| CallGraphEntry | model/call_graph.py:18 | cdd_guidance/practices/bdd/model/nodes.py:118; bdd/model/graph_bdd_model.py:77; stories/model/story_model.py:380 | — | — | ok |
| DocumentedIntent | model/class_stereotypes.py:54 | class_stereotypes.py:101; model/python/python_class_model.py:24 | — | — | ok |
| ClassHead | model/class_stereotypes.py:70 | c_family_parse.py:108 | DocumentedIntent | — | ok |
| CodeSpelling | model/code_body.py:17 | code_body.py:196, :203 (PYTHON_SPELLING, C_FAMILY_SPELLING given to CodeLanguage) | — | module constants at import | ok |
| CodeLanguage | model/code_body.py:35 | code_body.py:205-254 constants; java_class_model.py:17; python_class_model.py:106; stories and bdd readers | CodeSpelling | registers in `_languages` at import | ok |
| CodeBody | model/code_body.py:102 | operation.py:130; base_class_model.py:467; c_family_parse.py:253; stories story_model, bdd nodes | CodeLanguage | — | ok |
| WrittenBlock | model/code_body.py:149 | bdd/model/code_spec_model.py:177; stories/model/story_reader.py:27; stories/model/python/story_reader.py:45 | CodeBody | — | ok |
| CodeCleanEngineeringModel | model/code_class_model.py:22 | subclassed by python_class_model, javascript_class_model; BraceCleanEngineeringModel | CleanEngineeringModel, CodeBody, CodeLanguage | through `formats` clean_engineering.py:49-52 | ok |
| BraceCleanEngineeringModel | model/code_class_model.py:216 | subclassed by typescript, java, javascript class models | CFamilyParse | through `formats` | ok |
| Relationship | model/field_types.py:12 | base_class_model.py:311, :400; property.py:137; markdown and json class models | — | — | ok |
| ModelDescriptions | model/model_descriptions.py:14 | graph_practice.py:228 | CleanEngineeringModel, Operation, Property | — | ok |
| ModuleContext | model/module_context_files.py:26 | base_class_model.py:604 | file system | — | ok |
| Parameter | model/operation.py:42 | operation.py:180; sketch_class_model; graph_practice.py:202 | — | node type `Parameter` | ok |
| Operation | model/operation.py:81 | base_class_model.py:327; c_family_parse.py:140, :162, :213; python model | ModelChildren, CodeBody, Parameter, SourceText, PythonFunctionBody | node type `Operation` | ok |
| SourceText | model/operation_metrics.py:107 | base_class_model.py:257; operation.py:215, :229, :250 | — | — | ok |
| PythonFunctionBody | model/operation_metrics.py:280 | operation.py:238 (called from python_class_model.py:208) | — | — | ok |
| Invariant | model/property.py:17 | property.py:45 (`append_invariant`, called from c_family_parse and markdown) | — | node type `Invariant` (`_belongs` base_class_model.py:116) | ok |
| Property | model/property.py:91 | base_class_model.py:319; c_family_parse.py:330, :340; python and markdown models | Relationship, Invariant | node type `Property` | ok |
| TranslationError | model/update_report.py:13 | raised base_class_model.py:125 | — | — | ok |
| ChangeKind | model/update_report.py:17 | update_report.py:46-58 only | — | — | **D** (with UpdateReport) |
| Change | model/update_report.py:26 | update_report.py:46-52 only | — | — | **D** (with UpdateReport) |
| ChildCollectionPair | model/update_report.py:35 | base_class_model.py:334, :621, :736; operation.py:317 | — | — | ok (shape W, relationship 33) |
| UpdateReport | model/update_report.py:42 | built base_class_model.py:128; field_types.py:37 | Change, ChangeKind | — | **D** |

D evidence:
- **File** (model/base_class_model.py:416). Grep for `File(`, `import … File`, `"File"` across .py and .ts: only its own definition (and Playwright's unrelated type). Not in `OoadNode._belongs`, not in `model/schema.yaml`, not in `anchor_types`, not in any `formats` dict, `RULES`/`BY_SLUG`, registry, catalog, markdown recipe, or `.context` model. Delete.
- **UpdateReport, Change, ChangeKind** (model/update_report.py:17-58). Production builds an UpdateReport in `OoadNode.translate_from` and `Relationship.translate_from`, and `CleanEngineeringModel.sync` returns it, but no production code reads it: every production `translate_from` call discards the result (base_class_model.py:148, :153; diagram_node.py:93; drawio/diagram_node.py:149; drawio_class_model.py:116, :125; json_class_model.py:149; markdown_class_model.py:499), `sync` has no production caller, and `adds()`/`removes()` are read only in model/base_class_model_spec.py. No ts, yaml, markdown recipe, or registry names them. Spec-only reader: delete the three classes and let `translate_from` return nothing (keep `TranslationError`).

### Clean Engineering: format adapters

| class | file:line | used by (inbound, file:line) | uses (outbound) | build time | verdict |
|---|---|---|---|---|---|
| Geometry | diagram/geometry.py:6 | DiagramNode diagram_node.py:33; ArrowRouter class_layout.py:429; drawio_class_model.py:348, :662 | — | — | ok |
| DiagramNode | diagram/diagram_node.py:27 | base of DiagramClass/DiagramModule :43, :82; `Card` type class_layout.py:107 | Geometry | — | ok |
| DiagramClass | diagram/diagram_node.py:43 | base of DrawIOClass drawio/diagram_node.py:59; ImportedClass :56 | OoadClass (subclass), Geometry | — | ok (via subclass) |
| ImportedClass | diagram/diagram_node.py:56 | base of DrawIOImportedClass drawio/diagram_node.py:116 | DiagramClass | — | ok (via subclass) |
| DiagramModule | diagram/diagram_node.py:82 | ContainmentForest :229, :243; base of DrawIOModule drawio/diagram_node.py:144 | Module (subclass), Geometry, DiagramClass | — | ok |
| ContainmentForest | diagram/diagram_node.py:160 | _ModulesDiagramWriter drawio_class_model.py:298 | Module, DiagramModule | — | ok |
| DiagramCleanEngineeringModel | diagram/diagram_node.py:265 | base of DrawIOCleanEngineeringModel drawio_class_model.py:93 | CleanEngineeringModel (subclass), DiagramModule (`module_type`, read by nothing for this class) | — | ok (via subclass; one subclass since Miro left — the `module_type` attribute is unused) |
| DiagramCard | diagram/class_layout.py:60 | ddd/model/drawio/drawio_aggregate_model.py:215 | Geometry | — | ok |
| DiagramArrow | diagram/class_layout.py:83 | drawio_class_model.py:608, :634; ddd drawio_aggregate_model.py:203 | — | — | ok |
| CardPlacement | diagram/class_layout.py:110 | drawio_class_model.py:681 | Card, DiagramArrow | — | ok |
| _RouteGrid | diagram/class_layout.py:251 | ArrowRouter :455 | Geometry | — | ok |
| _ArrowSearch | diagram/class_layout.py:306 | ArrowRouter :516 | _RouteGrid | — | ok |
| ArrowRouter | diagram/class_layout.py:378 | drawio_class_model.py:703; ddd drawio_aggregate_model.py:219 | DiagramArrow, Geometry, _RouteGrid, _ArrowSearch | — | ok |
| DrawioVertex | drawio/diagram_node.py:40 | mixin of DrawIOClass :59, DrawIOModule :144 | — | — | ok |
| DrawIOClass | drawio/diagram_node.py:59 | drawio_class_model.py:115, :254; DrawIOModule.load_class :148 | DiagramClass, DrawioVertex, Parameter | — | ok |
| DrawIOImportedClass | drawio/diagram_node.py:116 | DrawIOCleanEngineeringModel.imported_class drawio_class_model.py:120 | ImportedClass, DrawIOClass | — | ok |
| DrawIOModule | drawio/diagram_node.py:144 | drawio_class_model.py:102, :168, :172, :216, :227 | DiagramModule, DrawioVertex, DrawIOClass | — | ok |
| DrawIOCleanEngineeringModel | drawio/drawio_class_model.py:93 | CleanEngineering formats clean_engineering.py:53; Drawio drawio.py:268, :290 | the writers/readers, ContainmentForest, CardPlacement, ArrowRouter | format adapter (formats dict → `PracticeGuidance._format_adapter`) | ok |
| _ClassDiagramReader | drawio/drawio_class_model.py:199 | DrawIOCleanEngineeringModel.parse :138-139 | DrawIOClass, DrawIOModule | — | ok |
| _ModulesDiagramWriter | drawio/drawio_class_model.py:293 | render :143 | ContainmentForest, DrawIOModule | — | ok |
| _ClassDiagramWriter | drawio/drawio_class_model.py:424 | render :144 | _ClassDiagramPage, channel | — | ok |
| _ClassDiagramPage | drawio/drawio_class_model.py:568 | _ClassDiagramWriter :538, :549 | DiagramArrow, CardPlacement, ArrowRouter, DrawIOClass | — | ok |
| Drawio | drawio/drawio.py:228 | CleanEngineering.drawio clean_engineering.py:60-65, generate_output :78 | DrawIOCleanEngineeringModel, DrawioScanner, the parser classes | `@agent_toolset` with `@agent_tool` create_diagram/scan/verify_regression and `@agent_instructions` validate/repair/render; composed by CleanEngineering (no separate skill found in .claude/skills) | ok |
| DrawioPage | drawio/scanners/_drawio_base.py:29 | DrawioScanner.scan_file :123; every scanner's scan_page | — | — | ok |
| DrawioScanner | drawio/scanners/_drawio_base.py:75 | Drawio.scan drawio.py:309; drawio/rules/__init__.py:359 | DrawioPage, Violation, scanner subclasses | rules RULES/BY_SLUG via `language_rules("drawio")` graph_practice.py:48 | ok |
| BaseAboveDerivedScanner, ClassTitleNoMarkdownBoldScanner, DistinctAnchorPointsScanner, EdgesApproachPerpendicularScanner, EdgesDoNotCrossClassesScanner, EdgesDoNotCrossOtherEdgesScanner, EdgesDoNotOverlapEdgesScanner, LeafNodesNotInHorizontalRowScanner, PreferShortRoutesScanner, StereotypeAboveClassNameScanner (10) | drawio/scanners/*_scanner.py | `DrawioScanner.discover` (glob `*_scanner.py`) :133-151 → run_report :159 and drawio/rules RULES | DrawioPage, Violation | discovered at import of drawio/rules; each also a `__main__` CLI | ok (10) |
| _DrawioScannerRule | drawio/rules/__init__.py:362 | RULES/BY_SLUG :383-387 read by `rules_in(...model.drawio.rules)` graph_practice.py:48 | scanner subclasses | graph rule registration | ok |
| ClassHeading | markdown/markdown_class_model.py:67 | MarkdownOoadClass.heading :125; :224, :396, :473 | — | — | ok |
| MarkdownOoadClass | markdown/markdown_class_model.py:105 | MarkdownModule :225, :229; markdown model :400, :475 | ClassHeading, MarkdownCleanEngineeringModel (throwaway host) | — | ok |
| MarkdownModule | markdown/markdown_class_model.py:220 | markdown model :286, :347, :439, `module_type` :811 | MarkdownOoadClass | — | ok |
| MarkdownCleanEngineeringModel | markdown/markdown_class_model.py:283 | formats clean_engineering.py:47; graph_practice.py:232; ddd.py:75; drawio.py:287 | MarkdownModule, MarkdownOoadClass, Property, Operation | format adapter | ok (dead methods: `load_class` :290 no caller; `from_workspace` :505 no caller) |
| PythonModule | python/python_class_model.py:36 | python model :109, :122; `module.load_source_facts` graph_practice.py:275 | — | — | ok |
| PythonCleanEngineeringModel | python/python_class_model.py:105 | formats clean_engineering.py:49; graph_practice.py:286; drawio.py:289; ddd.py:52 (lazy string); scripts/clean-engineering-validate.py:57 | OoadClass, Operation, Property, CodeBody, PythonModule | format adapter | ok |
| TypeScriptCleanEngineeringModel | typescript/typescript_class_model.py:20 | formats clean_engineering.py:50; graph_practice.py:289; ddd.py:56 | CodeLanguage | format adapter | ok |
| JavaCleanEngineeringModel | java/java_class_model.py:24 | formats clean_engineering.py:51 | CodeLanguage | format adapter | ok |
| JavaScriptCleanEngineeringModel | javascript/javascript_class_model.py:29 | formats clean_engineering.py:52; graph_practice.py:288 | CodeLanguage | format adapter | ok |
| JsonParseError | json/json_class_model.py:18 | raised :132, :144; caught :160 | — | — | ok |
| JsonProperty | json/json_class_model.py:22 | JsonOoadClass :57, :81 | Property | — | ok |
| JsonOperation | json/json_class_model.py:33 | JsonOoadClass :62, :82 | Operation | — | ok |
| JsonRelationship | json/json_class_model.py:44 | JsonOoadClass :67, :84 | Relationship | — | ok |
| JsonOoadClass | json/json_class_model.py:55 | JsonModule :93, :115; model :140 | Json parts | — | ok |
| JsonModule | json/json_class_model.py:91 | model :124, :136, :138 | JsonOoadClass | — | ok |
| JsonCleanEngineeringModel | json/json_class_model.py:122 | formats clean_engineering.py:48; drawio.py:288 | JsonModule, JsonParseError | format adapter | ok (dead method: `from_workspace` :153 no caller) |
| SketchCleanEngineeringModel | sketch/sketch_class_model.py:53 | formats clean_engineering.py:54 | _SketchSection, SketchOutline, SketchLens, domain parts | format adapter | ok |
| _SketchSection | sketch/sketch_class_model.py:70 | SketchCleanEngineeringModel.render :64 | — | — | ok |
| _Nest | sketch/sketch_class_model.py:343 | `_take_nest` :371, `_add_member` :323 | — | — | ok |

Not classes, but checked: `model/python/rules/__init__.py`, `model/typescript/rules/__init__.py`, `model/javascript/rules/__init__.py` only re-export the practice's `BY_SLUG`/`RULES`; nothing imports them (grep for `python.rules`, `typescript.rules`, `javascript.rules`, `model/*/rules` in py/ts/md/yaml finds only the module card that describes them, and `language_rules` reads only `model.drawio.rules`). They are dead re-export modules and are the cause of the practice↔model import cycle the module card names — delete them. `model/miro/` has only stale `__pycache__`.

### Stories: practice class, graph practice, rules, core story model

| class | file:line | used by (inbound) | uses (outbound) | build time | verdict |
|---|---|---|---|---|---|
| PracticeOutsideSession | stories.py:13 | Stories._project_of raises it, stories.py:85 | – | – | ok |
| Stories | stories.py:18 | harness/guidance/practice_catalogue.py:32 (`_REFS`); cdd_guidance/patterns/domain_driven_stack.py:29 | PracticeGuidance, Format, StoryModel, its format adapters, Session | `@agent_toolset`; installer publishes the practice toolset; catalog_card | ok |
| StoriesGraph | graph_practice.py:21 | GraphPractices registry (registered at :184); imported by GraphPractices._discover (harness/graph/graph_practice.py:200) | PracticeGraph, Graph, GraphStoryModel, TypeScriptStoryModel, StoryModel, _StoryLinks | registers at import | ok (folding into Stories under option A) |
| _StoryLinks | graph_practice.py:94 | StoriesGraph.link :50 | Graph, PracticeGraph, Epic | – | ok (folding into Stories under option A) |
| StoryNode | model/story_model.py:32 | base of every story node here and in markdown/json/drawio/miro nodes | ModelNode, CodeBody, WrittenBlock | node types in model/schema.yaml (`storyNode`) | ok |
| Example | model/story_model.py:193 | Examples :260; ux/scripts/emit_story_javascript.py:16 | – | schema `example` | ok |
| Examples | model/story_model.py:247 | Background/Scenario/Epic/StoryModel :470, :526, :641, :915; model/json/nodes.py:45, :220 | Example, StoryNode | – | ok |
| Increment | model/story_model.py:288 | StoryModel._copy_map :942; Code/Diagram/Json/Markdown increments subclass it | ModelChildren, Story | schema | ok |
| Step | model/story_model.py:342 | Scenario/Background :474, :535; CodeScenario.steps_from :166-178; graph_story_model.py:17 | ModelChildren, CodeBody, StepType, CallGraphEntry | schema `step` | ok |
| Background | model/story_model.py:460 | Scenario/Story :533, :832; code_story_model.py:133; brace_story.py:70 | ModelChildren, Examples, Step | schema | ok |
| StepType | model/story_model.py:496 | Scenario :569; code_story_model.py:104; markdown/nodes.py:569; ux/scripts/emit_story_javascript.py:16 | – | – | ok |
| Scenario | model/story_model.py:504 | Story.scenario_type :808; CodeScenario subclass; graph_story_model.py:17 | ModelChildren, Examples, Step, Background, StepType | schema | ok |
| StoryType | model/story_model.py:609 | Story :814; code_story_model.py:229, :476; diagram_story_model.py:94 | – | – | ok |
| Epic | model/story_model.py:628 | StoryModel.epic_type :905; CodeEpic/DiagramEpic subclasses; graph_practice.py:176; ux/model/claude_design/story_canvas.py:29 | ModelChildren, Examples, Story, SourceLocation | schema `epic`/`subEpic` | ok |
| Story | model/story_model.py:806 | StoryModel.story_type :906; Epic :646; story_reader.py:8; ux/model/claude_design/story_canvas.py:29 | ModelChildren, Scenario, Background, StoryType | schema `story` | ok |
| StoryModel | model/story_model.py:903 | stories.py:76; graph_practice.py:75-76; ux/model/claude_design/story_canvas.py:29; every format model subclasses it | Epic, Story, Increment, Examples, the Json/Markdown/DrawIO models, the Python/TypeScript/JavaScript stories, SourceLocation, Name | – | ok |
| CodeStoryModelError | model/code_story_model.py:44 | raised at :373, :726; java/java_story_model.py:51; the javascript/python/typescript models | – | – | ok |
| CodeStoryNode | model/code_story_model.py:80 | mixin of CodeScenario, CodeStory, CodeIncrement, CodeEpic | Name | – | ok |
| CodeScenario | model/code_story_model.py:100 | CodeStory.scenario_type :215; BraceScenario; java/nodes.py:11; python/nodes.py:11 | Step, Background, StepType | – | ok |
| CodeStory | model/code_story_model.py:214 | CodeStoryModel.story_type :336; java, javascript, python and typescript nodes subclass it | CodeScenario | – | ok |
| CodeIncrement | model/code_story_model.py:306 | CodeStoryModel.increment_type :337, read by StoryModel._copy_map :942 | – | – | ok |
| CodeEpic | model/code_story_model.py:310 | CodeStoryModel.epic_type :335; :660-661; java, javascript, python and typescript nodes subclass it | Name | – | ok |
| CodeStoryModel | model/code_story_model.py:332 | BraceStoryModel; java/java_story_model.py:12; python/python_story_model.py:18 | CodeBody, WrittenBlock, render_call_graph_block, CodeEpic, SourceLocation | the subclasses are named in Stories' `formats` | ok |
| DiagramStoryNode | model/diagram_story_model.py:10 | mixin of DiagramEpic, DiagramStory, DiagramIncrement; `_layout` is called from drawio/nodes.py:101 and miro/nodes.py:160 | DiagramStoryModel | – | ok |
| DiagramEpic | model/diagram_story_model.py:112 | DiagramStoryModel.epic_type :153; drawio/nodes.py:120; miro/nodes.py:194; ux story_canvas.py | – | – | ok |
| DiagramStory | model/diagram_story_model.py:127 | DiagramStoryModel.story_type :154; drawio/nodes.py:60; miro/nodes.py:137 | – | – | ok |
| DiagramIncrement | model/diagram_story_model.py:140 | drawio/nodes.py:25; miro/nodes.py:23 | – | – | ok |
| DiagramStoryModel | model/diagram_story_model.py:148 | drawio/nodes.py:300; miro/nodes.py:299; ux/model/claude_design/story_canvas.py | DiagramEpic, DiagramStory | the subclasses are named in Stories' `formats` | ok |
| GraphStoryModel | model/graph_story_model.py:83 | graph_practice.py:46 (rules/rule_examples.py:27 and :145 are spec support) | StoryModel, _StoryGraphRecording, SourceLocation | – | ok (W: fold into StoryModel) |
| _StoryGraphRecording | model/graph_story_model.py:192 | GraphStoryModel.record :94 | PracticeGraph, Source, SourceLocation | – | ok (W) |
| BraceScenario | model/brace_story.py:13 | javascript/nodes.py:12; typescript nodes | Background, Step | – | ok |
| BraceStoryModel | model/brace_story.py:116 | javascript/javascript_story_model.py:19; typescript_story_model | BraceStoryReader | the subclasses are named in Stories' `formats` | ok |
| BraceCall | model/brace_story_reader.py:25 | BraceStoryReader :124, :129, :141 | – | – | ok |
| BraceStoryReader | model/brace_story_reader.py:58 | BraceStoryModel.read_code brace_story.py:122 | BraceCall, CodeBody, WrittenBlock, flat_steps | – | ok |
| StoryReader | model/story_reader.py:15 | BraceStoryReader; python/story_reader.py:19 | WrittenBlock | – | ok |
| SourceLocation | model/source_location.py:10 | story_model.py:737, :1031; code_story_model.py:688; graph_story_model.py:135, :214; markdown/nodes.py:96; json/nodes.py | – | – | ok |
| 26 graph rules: DomainFixtureExampleFiles, ExampleRoleNames, OriginatingSubEpicExamples, ExamplesExportDataNotRepository (acceptance_tests.py:25-86); AndChaining, ButMarksMissingState, WhenHoldsTheOperation, OutlineRequiresManyPermutations, ExamplesTraceDomainModel, WhenNamesIntentNotInterfaceGesture, BehavioralAndSystemObservableOutcomes, FlaggedWritesIntendedGwt, GivenNamesComplexStateRootFirst, ScenarioNamesContinuation, ScenariosShape, PlainEnglishGwtSteps, GwtStepsTraceToDomainOperations, DomainOperationInTheStep (scenarios.py:40-335); VerbNounFormat, FourToNineChildren, StoryScenariosAtMostSeven, KebabCasePaths, StoryNameCapturesSystemMechanic, RightSizeStoryNodes, BranchOnMechanicalUniqueness, BehavioursNotOneTimeTasks (story_map.py:17-121) | rules/*.py | each is made once in `RULES` (rules/__init__.py:36-63) and read through `BY_SLUG` by `rules_in("cdd_guidance.practices.stories.rules")` (harness/graph/graph_practice.py:25) | Node, RuleCheckContext, Format (DomainFixtureExampleFiles), Graph (GivenNamesComplexStateRootFirst) | registered at import of the rules package; slugs named in model/schema.yaml | ok (all 26) |

Note: `rules/rule_examples.py` holds no classes. It is spec support ("Spec support" in its docstring), and only `rules/stories_examples_spec.py` imports it. It sits beside production rules but is spec-only. Move it beside the specs or into the spec fixtures. It is not counted as a class.

No class in this slice is D. Checks for the least-used classes:
- `CodeIncrement`: no grep hits outside its file, but `CodeStoryModel.increment_type` names it, and `StoryModel._copy_map` (:942) reads it whenever a map is copied into code.
- `PracticeOutsideSession`: raised at stories.py:85. No caller catches it by type, but a named failure that is raised counts as a use.
- `BraceCall` and `_StoryGraphRecording`: used only inside their own module, by the class next to them.

### Stories: format adapters

| class | file:line | used by (inbound) | uses (outbound) | build time | verdict |
|---|---|---|---|---|---|
| MarkdownStoryModel | markdown/nodes.py:944 | stories.py:51 formats; story_model.py:963, 1050, 1066; markdown/__init__.py | MarkdownEpic, MarkdownStory, MarkdownScenario, MarkdownIncrement, _StoryMapWriter, _StepLines, _ScenarioDocument, StoryMapLinks | format adapter (lazy import via PracticeGuidance._format_adapter) | ok |
| MarkdownEpic | markdown/nodes.py:805 | MarkdownStoryModel.epic_type :949, parse :1146, 1376… | MarkdownStory.load_scenarios | — | ok |
| MarkdownStory | markdown/nodes.py:752 | MarkdownStoryModel.story_type :950, :1165, :1402 | MarkdownScenario | — | ok |
| MarkdownScenario | markdown/nodes.py:185 | MarkdownStoryModel :1007, 1142, 1416; _StoryMapWriter :916 | MarkdownStep, _StorySection, Background, DomainModelLinks | — | ok |
| MarkdownStep | markdown/nodes.py:160 | MarkdownScenario.make_step :545; _StepLines :866 | — | — | ok |
| MarkdownIncrement | markdown/nodes.py:61 | MarkdownStoryModel._attach_markdown :1010 | MarkdownScenario (markup helper) | — | ok |
| MarkdownParseError | markdown/nodes.py:940 | raised :991, :1303; markdown/__init__.py | — | — | ok |
| _StorySection | markdown/nodes.py:149 | MarkdownScenario :319; MarkdownStoryModel :1152, 1164 | Background | — | ok |
| _ScenarioDocument | markdown/nodes.py:818 | MarkdownStoryModel :1161, 1174 | MarkdownEpic | — | ok |
| _StepLines | markdown/nodes.py:833 | MarkdownStoryModel :1176, 1200, 1223 | MarkdownStep | — | ok |
| _StoryMapWriter | markdown/nodes.py:873 | MarkdownStoryModel.render :1030 | StoryMapLinks, MarkdownScenario | — | ok |
| StoryMapLinks | markdown/links.py:76 | MarkdownStoryModel :1029; DrawIOStoryModel :380, 390 | _Anchors | — | ok |
| _Anchors | markdown/links.py:63 | StoryMapLinks :132; DomainModelLinks :184 | — | — | ok |
| DomainModelLinks | markdown/links.py:154 | only markdown/markdown_story_model_spec.py:545-576; production `render_scenarios` has a `domain_links` parameter no production caller passes (only call: markdown/nodes.py:916, without it) | _Anchors | none: not in a formats dict, no RULES/BY_SLUG, no registry, no catalog; md mention only in model/.context/story-model.md:393 | **D** (spec-only) |
| DrawIOStoryModel | drawio/nodes.py:300 | stories.py:53 formats; story_model.py:1055; DrawIOIncrement :53, 57 | DrawIOEpic, DrawIOStory, DrawIOIncrement, _PlacedCell, Vertex, StoryMapLinks | format adapter | ok |
| DrawIOStoryModel.Vertex | drawio/nodes.py:310 | DrawIOEpic/DrawIOStory.cells :108-238; `_cell` :487 | StoryMapLinks | — | ok |
| DrawIOEpic | drawio/nodes.py:120 | epic_type :301; load :436 | Vertex, DiagramStoryModel layout | — | ok |
| DrawIOStory | drawio/nodes.py:60 | story_type :302; load :458; _read_thin_slice :610 | Vertex | — | ok |
| DrawIOIncrement | drawio/nodes.py:25 | increment_type :303 (copy constructor, story_model.py:942); _read_thin_slice :601 | DrawIOStoryModel (save/load are spec-only: drawio_story_model_spec.py:173) | — | ok (its `save`/`load` operations spec-only) |
| DrawIOParseError | drawio/nodes.py:249 | raised :422-429, 583-586; drawio/__init__.py | — | — | ok |
| _PlacedCell | drawio/nodes.py:253 | DrawIOStoryModel.load :411 | — | — | ok |
| JsonStoryModel | json/nodes.py:79 | stories.py:52 formats; story_model.py:960, 1074 | JsonEpic, JsonStory, JsonScenario, JsonIncrement, Step, Background, Story, SourceLocation | format adapter | ok |
| JsonEpic | json/nodes.py:69 | epic_type :82; :240 | — | — | ok |
| JsonStory | json/nodes.py:65 | story_type :83; :250 | — | — | ok |
| JsonScenario | json/nodes.py:61 | JsonStory.scenario_type :66; :271 | — | — | ok |
| JsonIncrement | json/nodes.py:57 | increment_type :84; :317 | — | — | ok |
| JsonParseError | json/nodes.py:75 | raised :103, 129; json/__init__.py | — | — | ok |
| MiroStoryModel | miro/nodes.py:299 | stories.py:54 formats (but has no render/parse, so that route fails); story_channel.feature.py:261, 274 (save/load) | MiroEpic, MiroStory | format adapter (broken) | ok, with defect |
| MiroEpic | miro/nodes.py:194 | epic_type :300; load :365, 373 | — | — | ok |
| MiroStory | miro/nodes.py:137 | story_type :301; load :378; MiroIncrement.from_cells :47 | — | — | ok |
| MiroIncrement | miro/nodes.py:23 | increment_type :302 (copy constructor) | MiroStory (save/load/from_cells spec-only: miro_round_trip_spec.py:26, miro_story_model_spec.py:278) | — | ok (its `save`/`load` operations spec-only) |
| MiroParseError | miro/nodes.py:295 | raised :101, 342, 355; miro/__init__.py | — | — | ok |
| PythonStoryModel | python/python_story_model.py:18 | stories.py:55 formats; python/nodes.py:99 | PythonEpic, PythonStory, PythonStoryReader | format adapter | ok |
| PythonStory | python/nodes.py:69 | story_type python_story_model.py:21; story_test_type story_model.py:1117 | PythonScenario, PythonStoryModel | — | ok (`create` spec-only: code_story_name_spec.py:18) |
| PythonScenario | python/nodes.py:11 | PythonStory.scenario_type :70 | — | — | ok |
| PythonEpic | python/nodes.py:103 | epic_type python_story_model.py:20 | — | — | ok |
| PythonStoryReader | python/story_reader.py:19 | PythonStoryModel.read_code :55 | WrittenBlock, CodeBody | — | ok |
| TypeScriptStoryModel | typescript/typescript_story_model.py:25 | stories.py:56 formats, stories.py:94; graph_practice.py:64, 88; typescript/nodes.py:64; typescript/__init__.py | TypeScriptEpic, TypeScriptStory, story_file functions, seed | format adapter | ok |
| TypeScriptStory | typescript/nodes.py:19 | story_type :28; story_test_type story_model.py:1121 | TypeScriptScenario, TypeScriptStoryModel | — | ok (`create` spec-only: typescript_story_model_spec.py:140) |
| TypeScriptScenario | typescript/nodes.py:15 | TypeScriptStory.scenario_type :20 | — | — | ok |
| TypeScriptEpic | typescript/nodes.py:68 | epic_type :27; folder_files calls `examples_file` | CodeEpic | — | ok |
| JavaStoryModel | java/java_story_model.py:12 | stories.py:57 formats; java/nodes.py:110 | JavaEpic, JavaStory, JavaScenario | format adapter | ok |
| JavaStory | java/nodes.py:89 | story_type java_story_model.py:15 | JavaScenario, JavaStoryModel | — | ok (`create` spec-only) |
| JavaScenario | java/nodes.py:11 | JavaStory.scenario_type :90; JavaStoryModel :38 | Background, Step | — | ok |
| JavaEpic | java/nodes.py:113 | epic_type java_story_model.py:14 | — | — | ok |
| JavaScriptStoryModel | javascript/javascript_story_model.py:19 | stories.py:58 formats; javascript/nodes.py:47 | JavaScriptEpic, JavaScriptStory, seed | format adapter | ok |
| JavaScriptStory | javascript/nodes.py:16 | story_type :22; story_test_type story_model.py:1125; ux/scripts/emit_story_javascript.py:68 | JavaScriptScenario, JavaScriptStoryModel | — | ok |
| JavaScriptScenario | javascript/nodes.py:12 | JavaScriptStory.scenario_type :17 | — | — | ok |
| JavaScriptEpic | javascript/nodes.py:51 | epic_type :21 | — | — | ok |
| SketchStoryModel | sketch/sketch_story_model.py:36 | stories.py:50 formats; sketch/__init__.py | SketchOutline, SketchLens, _SketchReader, _SketchWriter | format adapter | ok |
| _SketchReader | sketch/sketch_story_model.py:48 | SketchStoryModel.parse :40 | Epic, Story, Scenario, Step, Background, Increment | — | ok |
| _SketchWriter | sketch/sketch_story_model.py:169 | SketchStoryModel.render :45 | — | — | ok |
| `_Background`, StoryNodeTransformer, StoryExampleCollector (seed) | python/seeds/story_test.py:20, 53, 299 | none: no code reads or copies this file (grep "seeds", "story_test.py", class names across py/ts/md/toml/ps1/sh); PythonStoryModel.save writes no seed, unlike TypeScript/JavaScript; the deployed copies are templates/py/story_test.py and space/kanban/story_test.py, which differ from it | mamba | none | **D** (the whole seed file; .context/architecture-context.md:27 says runners live in seeds, but nothing ships this one) |

Seed files that are not Python classes, for the coordinator: typescript/seeds/story-test.ts and javascript/seeds/story-test.js are read (typescript/nodes.py:117, javascript/javascript_story_model.py:83). javascript/seeds/story-types.js is named only as the default import path in ux/scripts/emit_story_javascript.py:64. typescript/seeds/story-runner.ts and story-types.ts, java/seeds/StoryRunner.java and StoryTypes.java, and javascript/seeds/story-runner.js have no reader in Python, TypeScript, or the installer; only their own siblings import them.

### DDD

| class | file:line | used by (inbound, file:line) | uses (outbound) | build time | verdict |
|---|---|---|---|---|---|
| Ddd | ddd.py:11 | PracticeCatalogue `_REFS` harness/guidance/practice_catalogue.py:33; ContextSetup cdd_guidance/context_setup/context_setup.py:74 | PracticeGuidance, Format, MarkdownCleanEngineeringModel, bridge, BoundedContextMap | `@agent_toolset` published by the installer; `catalog_card` read by the catalog generator | ok |
| DddGraph | graph_practice.py:22 | GraphPractices registry (graph_practice.py:175), found by `GraphPractices._discover` | GraphPractices, _DddReading | registers at import | ok |
| _DddReading | graph_practice.py:37 | DddGraph.read graph_practice.py:34 | PracticeGraph, TacticalClass, Aggregate, BoundedContext, tactical_facts | — | ok |
| Integration | model/nodes.py:40 | Aggregate.integrations nodes.py:310; MarkdownIntegration markdown/nodes.py:63; ContextLayout drawio_bounded_context_map.py:194 | — | — | ok |
| InvariantObject | model/nodes.py:79 | Entity nodes.py:140,148; MarkdownInvariantObject markdown/nodes.py:67; plain_properties class_cards.py:131 | Property | schema.yaml type | ok |
| Entity | model/nodes.py:126 | building_block_type nodes.py:279-280; Aggregate.take_root nodes.py:325; MarkdownEntity markdown/nodes.py:71 | InvariantObject | schema.yaml type | ok |
| ValueObject | model/nodes.py:165 | building_block_type nodes.py:274 (→ ClassCard.from_name class_cards.py:45) | OoadClass | schema.yaml type | ok |
| Repository | model/nodes.py:187 | building_block_type nodes.py:275; MarkdownAggregate.take_root_card markdown/nodes.py:135 | OoadClass | schema.yaml type | ok |
| DomainService | model/nodes.py:207 | building_block_type nodes.py:276-277; `_consumer` markdown/nodes.py:485 | OoadClass | schema.yaml type | ok |
| DomainEvent | model/nodes.py:225 | Aggregate.events nodes.py:336; MarkdownAggregate._open_root markdown/nodes.py:173; `_wire_event` markdown/nodes.py:470; plain_properties class_cards.py:131 | Property | schema.yaml type | ok |
| Specification | model/nodes.py:255 | building_block_type nodes.py:273 | OoadClass | schema.yaml type | ok |
| Factory | model/nodes.py:263 | building_block_type nodes.py:278 | OoadClass | schema.yaml type | ok |
| Aggregate | model/nodes.py:290 | _DddReading._aggregate graph_practice.py:86; BoundedContext nodes.py:440; MarkdownAggregate markdown/nodes.py:87 | Entity, Integration, DomainEvent | schema.yaml type | ok |
| BoundedContext | model/nodes.py:339 | _bounded_contexts / _unmarked_context graph_practice.py:150, 160; BoundedContextMap nodes.py:452; bridge `_label` clean_engineering_bridge.py:73 | Aggregate, ModelChildren | schema.yaml type | ok |
| BoundedContextMap | model/nodes.py:446 | Ddd._model_for ddd.py:85-91; `_has_aggregates` ddd.py:97; MarkdownBoundedContextMap markdown/nodes.py:287 | BoundedContext, Aggregate | — | ok |
| TacticalClass | model/stereotypes.py:40 | _DddReading graph_practice.py:78; tactical_facts nodes.py:122; bridge clean_engineering_bridge.py:92 | class_stereotypes `marks_in` | — | ok |
| MarkdownDomainNode | model/markdown/nodes.py:50 | base of the six markdown nodes, markdown/nodes.py:63-287 | — | — | ok (mixin) |
| MarkdownIntegration | model/markdown/nodes.py:63 | MarkdownAggregate markdown/nodes.py:197; bridge :196; _ContextMapReader drawio_bounded_context_map.py:169 | Integration | — | ok |
| MarkdownInvariantObject | model/markdown/nodes.py:67 | MarkdownEntity :76,84; take_root_card :132; _ContextMapReader drawio_bounded_context_map.py:160 | InvariantObject | — | ok |
| MarkdownEntity | model/markdown/nodes.py:71 | _open_root :169; bridge :69; drawio readers drawio_bounded_context_map.py:159, drawio_aggregate_model.py:264 | Entity, MarkdownInvariantObject | — | ok |
| MarkdownAggregate | model/markdown/nodes.py:87 | MarkdownBoundedContextMap :291, :432; bridge :135; _SketchReader sketch_ddd_model.py:176; drawio readers | Aggregate, ClassCard, MarkdownEntity, MarkdownIntegration, DomainEvent | — | ok |
| MarkdownBoundedContext | model/markdown/nodes.py:234 | MarkdownBoundedContextMap :290, :304; bridge :146; _SketchReader sketch_ddd_model.py:151; drawio readers | BoundedContext | — | ok |
| MarkdownBoundedContextMap | model/markdown/nodes.py:287 | `formats["markdown"]` ddd.py:49; base of DrawIOBoundedContextMap and SketchDddModel; bridge :49 | MarkdownBoundedContext, MarkdownAggregate, DomainEvent, DomainService | format adapter | ok |
| ClassCard | model/markdown/class_cards.py:28 | MarkdownAggregate :98; bridge :93; _SketchFence :215; drawio aggregate view drawio_aggregate_model.py:296 | building_block_type, Property, Operation | — | ok (W wrapper) |
| _SketchFence | model/markdown/class_cards.py:211 | card_from_sketch :208 (→ _SketchReader sketch_ddd_model.py:99) | ClassCard | — | ok |
| _LabelText | model/drawio/drawn_diagram.py:12 | label_texts :28 | HTMLParser | — | ok |
| DrawnCell | model/drawio/drawn_diagram.py:31 | DrawnDiagram :65; both drawio readers | _LabelText | — | ok |
| DrawnDiagram | model/drawio/drawn_diagram.py:58 | DrawIOBoundedContextMap.parse drawio_bounded_context_map.py:118 | DrawnCell | — | ok |
| _Cell | model/drawio/drawio_aggregate_model.py:79 | DrawIOAggregateModel._add :206 | — | — | ok |
| DrawIOAggregateModel | model/drawio/drawio_aggregate_model.py:94 | DrawIOBoundedContextMap :113, :119 | ArrowRouter, DiagramCard, DiagramArrow, Geometry, arrow_style, _AggregateViewReader, ClassCard | — | ok |
| _AggregateViewReader | model/drawio/drawio_aggregate_model.py:247 | DrawIOAggregateModel.contexts_in :127 | Markdown nodes, ClassCard | — | ok |
| _EdgePlan | model/drawio/drawio_bounded_context_map.py:73 | _DiagramWriter :377 | — | — | ok |
| _Route | model/drawio/drawio_bounded_context_map.py:80 | _StraightRoutes :476 | — | — | ok |
| _IntegrationLink | model/drawio/drawio_bounded_context_map.py:89 | ContextLayout :199 | — | — | ok |
| _CellRecord | model/drawio/drawio_bounded_context_map.py:98 | _DiagramWriter :427 | — | — | ok |
| DrawIOBoundedContextMap | model/drawio/drawio_bounded_context_map.py:107 | `formats["drawio"]` ddd.py:45-48; model/drawio/__init__.py | DrawnDiagram, DrawIOAggregateModel, _ContextMapReader, ContextLayout, _DiagramWriter | format adapter | ok |
| _ContextMapReader | model/drawio/drawio_bounded_context_map.py:134 | DrawIOBoundedContextMap.parse :119 | Markdown nodes | — | ok |
| ContextLayout | model/drawio/drawio_bounded_context_map.py:177 | DrawIOBoundedContextMap._write_diagram :125 | _IntegrationLink | — | ok |
| _DiagramWriter | model/drawio/drawio_bounded_context_map.py:329 | DrawIOBoundedContextMap._write_diagram :126 | _StraightRoutes, _EdgePlan, _CellRecord | — | ok |
| _StraightRoutes | model/drawio/drawio_bounded_context_map.py:450 | _DiagramWriter.draw_integration_edges :369 | _Route | — | ok |
| SketchDddModel | model/sketch/sketch_ddd_model.py:67 | `formats["sketch"]` ddd.py:44; model/sketch/__init__.py | SketchOutline, _SketchReader, _SketchWriter | format adapter | ok |
| _SketchReader | model/sketch/sketch_ddd_model.py:78 | SketchDddModel.parse :70 | Markdown nodes, card_from_sketch | — | ok |
| _SketchWriter | model/sketch/sketch_ddd_model.py:204 | SketchDddModel.render :75 | MarkdownAggregate cards | — | ok |
| PrivateMethodNaming | rules/tactical.py:27 | RULES rules/__init__.py:16 | PracticeGraphRule | `rules_in` reads RULES/BY_SLUG | ok |
| FlaccidDataObject | rules/tactical.py:43 | RULES :17 | tactical_helpers | same | ok |
| EveryClassCarriesDddStereotype | rules/tactical.py:57 | RULES :18 | tactical_helpers | same | ok |
| DomainConceptsNotTechnicalNames | rules/tactical.py:70 | RULES :19 | tactical_helpers | same | ok |
| ServiceIsHomeless | rules/tactical.py:79 | RULES :20 | — | same | ok |
| RepositoryIsCollectionLifecycle | rules/tactical.py:93 | RULES :21 | tactical_helpers | same | ok |
| LoadWithIdentityInHand | rules/tactical.py:112 | RULES :22 | — | same | ok |
| NoOrphanedObjects | rules/tactical.py:123 | RULES :23 | — | same | ok |
| ScreenInterfaceNotADomainObject | rules/tactical.py:135 | RULES :24 | tactical_helpers | same | ok |

`rules/rule_examples.py` and `rules/tactical_helpers.py` hold functions only (no classes); `rule_examples.py` is used only by `rules/ddd_rules_spec.py` (spec support).

Side note found while checking: `BoundedContextMap.load(path)` (model/nodes.py:463) is reached only from `model/ddd_channel.feature.py`; production parses through `parse(text)`.

### UX, BDD, agent BDD, output_folder.py

| class | file:line | used by (inbound, file:line) | uses (outbound) | build time | verdict |
|---|---|---|---|---|---|
| NoJavascriptPractice | ux/ux.py:12 | raised by Ux.javascript_practice, ux/ux.py:65 | - | - | ok |
| Ux | ux/ux.py:17 | PracticeCatalogue._REFS harness/guidance/practice_catalogue.py:34; ContextSetup cdd_guidance/context_setup/context_setup.py:20, :75 | PracticeCatalogue, Session, format adapters | `@agent_toolset`, `@agent_tool`; catalog card | ok |
| UxGraph | ux/graph_practice.py:11 | GraphPractices._discover imports `ux.graph_practice` (harness/graph/graph_practice.py:200) | GraphPractices | registers at import | ok (folding into Ux under option A) |
| UxNode | ux/model/ux_node.py:11 | base of every UX node and UxMap | ModelNode, Graph | - | ok |
| UxMap | ux/model/ux_map.py:46 | base of the five format adapters; Ux formats ux/ux.py:45-49 | ReferencePaths, collections, UxContext, Screen | - | ok |
| ScreenNotOnMap | ux/model/ux_map.py:38 | raised by UxMap.find_screen, ux_map.py:127 | - | - | ok |
| StoryStep | ux/model/nodes.py:21 | StoryDemoControl nodes.py:110; JsonUxMapWriter json/nodes.py:215; html/nodes.py:144 | - | - | ok |
| Interaction | ux/model/nodes.py:42 | JsonUxMapReader json/nodes.py:113 | Screen | schema.yaml node type | ok |
| Control | ux/model/nodes.py:60 | Region.append_control; JsonUxMapReader json/nodes.py:106 | ModelChildren, Interaction | schema.yaml | ok |
| StoryDemoControl | ux/model/nodes.py:84 | JsonUxMapReader json/nodes.py:96; HtmlUxMap html/nodes.py:130 | StoryStep | schema.yaml | ok |
| Region | ux/model/nodes.py:117 | DrawioUxMapReader drawio/nodes.py:136; JsonUxMapReader json/nodes.py:86 | Control | schema.yaml | ok |
| Screen | ux/model/nodes.py:130 | UxMap; readers drawio/nodes.py:121, json/nodes.py:60; ClaudeDesignStory story_canvas.py:106 | StoryLink, Name, Region | schema.yaml; UxGraph node_types | ok |
| UxComponent | ux/model/nodes.py:238 | base of Transition, ContentType, NavComponent; UxComponentCollection._item_type | - | - | ok |
| Transition | ux/model/nodes.py:244 | Transitions collections.py:66; readers drawio/nodes.py:165, json/nodes.py:125 | Screen | schema.yaml | ok |
| ContentType | ux/model/nodes.py:264 | ContentTypes collections.py:71; JsonUxMapReader json/nodes.py:135 | - | schema.yaml | ok |
| NavComponent | ux/model/nodes.py:275 | NavComponents collections.py:76; JsonUxMapReader json/nodes.py:140 | Screen | schema.yaml | ok |
| UxContext | ux/model/nodes.py:286 | UxMap ux_map.py:62 | - | schema.yaml | ok |
| UxComponentCollection | ux/model/collections.py:13 | base of Transitions, ContentTypes, NavComponents | ModelChildren | - | ok |
| Transitions, ContentTypes, NavComponents | ux/model/collections.py:65, :70, :75 | UxMap ux_map.py:59-61 | ModelChildren | - | ok |
| ReferencePaths | ux/model/reference_paths.py:8 | UxMap ux_map.py:56-57 | - | - | ok |
| StoryLink | ux/model/story_link.py:19 | Screen nodes.py:224 | Graph practices | - | ok |
| MarkdownUxMap | ux/model/markdown/nodes.py:17 | Ux formats ux/ux.py:47 | MarkdownContextReader | format adapter (lazy import) | ok |
| MarkdownContextReader | ux/model/markdown/nodes.py:44 | MarkdownUxMap.parse :27 | UxMap | - | ok |
| DrawioCliMissing, DrawioCliFailed, DrawioCliTimedOut, UnreadableDrawio | ux/model/drawio/nodes.py:33, :37, :41, :45 | raised by DrawioUxMap :74, :81, :89, :91, :68 | - | - | ok |
| DrawioUxMap | ux/model/drawio/nodes.py:49 | Ux formats ux/ux.py:45 | DrawioUxMapReader, JsonUxMap, cli_state, drawio_ux.mjs | format adapter | ok |
| DrawioUxMapReader | ux/model/drawio/nodes.py:94 | DrawioUxMap.parse :69 | Screen, Region, Transition | - | ok |
| JsonUxMap | ux/model/json/nodes.py:21 | Ux formats ux/ux.py:48; DrawioUxMap :64; HtmlUxMap :33, :59; ClaudeDesignStoryModel story_canvas.py:385 | JsonUxMapReader, JsonUxMapWriter | format adapter | ok |
| JsonUxMapReader | ux/model/json/nodes.py:33 | JsonUxMap.parse :27 | UX node classes | - | ok |
| JsonUxMapWriter | ux/model/json/nodes.py:148 | JsonUxMap.render :30 | UX node classes | - | ok (W relationship 23) |
| UxMapNotEmbedded | ux/model/html/nodes.py:17 | raised by HtmlUxMap.parse :32 | - | - | ok |
| HtmlUxMap | ux/model/html/nodes.py:22 | Ux formats ux/ux.py:46 | JsonUxMap, mockup_shell.html | format adapter | ok |
| ClaudeDesignScreensNotReadable | ux/model/claude_design/nodes.py:16 | raised by ClaudeDesignUxMap.parse :33 | - | - | ok |
| ClaudeDesignUxMap | ux/model/claude_design/nodes.py:20 | Ux formats ux/ux.py:49; ClaudeDesignStoryModel story_canvas.py:127-128, :182, :189, :287 | - | format adapter | ok |
| ClaudeDesignEpic | ux/model/claude_design/story_canvas.py:35 | ClaudeDesignStoryModel.epic_type :124 | design_canvas functions | - | ok |
| ClaudeDesignStory | ux/model/claude_design/story_canvas.py:81 | ClaudeDesignStoryModel.story_type :125 | Screen, design_canvas functions | - | ok |
| ClaudeDesignStoryModel | ux/model/claude_design/story_canvas.py:121 | no Python caller outside its spec; the recipe `ux/model/claude_design/story_canvas.md:7` tells the agent to call `ClaudeDesignStoryModel().render(...)`, reached from `stories/stories.md:61` | DesignCanvas, ClaudeDesignUxMap, JsonUxMap | markdown recipe | ok (recipe-only; not in any `formats` map) |
| ScreenStoryBudget, ScreenNamesUseDomainTerms | ux/rules/screen_rules.py:8, :25 | `RULES` ux/rules/__init__.py:5, read by `rules_in` harness/graph/graph_practice.py:25 | RuleCheckContext | rules registry | ok |
| Bdd | bdd/bdd.py:10 | PracticeCatalogue._REFS practice_catalogue.py:36; AgentBdd agent_bdd/agent_bdd.py:22 | format adapters | `@agent_toolset`; catalog card | ok |
| BddGraph | bdd/graph_practice.py:28 | GraphPractices._discover imports `bdd.graph_practice` | PracticeGraph, Graph, language models, _ObservationLinks | registers at import | ok (folding into Bdd under option A) |
| _ObservationLinks | bdd/graph_practice.py:81 | BddGraph.link :46 | Graph, PracticeGraph, Name | - | ok (folding into Bdd under option A) |
| BehaviorNode | bdd/model/nodes.py:37 | base of Description, Context, Observation | CodeBody, WrittenBlock | - | ok |
| Description, Context, Observation | bdd/model/nodes.py:65, :88, :113 | _SketchReader bdd_model.py; `_behavior_node` code_spec_model.py:379-385; GraphBddModel graph_bdd_model.py:62-72 | CallGraphEntry, CodeBody | schema.yaml; BddGraph node_types | ok (note: `Description.load_context`, `Context.load_observation`, `Context.load_context` at nodes.py:84, :106, :109 have no caller) |
| BddModel | bdd/model/bdd_model.py:19 | base of every BDD format adapter | _SketchReader, spec_source, CodeBody | schema.yaml (`Spec`) | ok |
| MarkdownBddModel | bdd/model/bdd_model.py:142 | Bdd formats bdd/bdd.py:39 | - | format adapter | ok |
| _SketchReader | bdd/model/bdd_model.py:146 | BddModel.parse :49 | Description, Context, Observation, CallGraphEntry | - | ok |
| SketchBddModel | bdd/model/sketch/sketch_bdd_model.py:9 | Bdd formats bdd/bdd.py:38 | SketchOutline, SketchLens | format adapter | ok |
| UnreadableSpec | bdd/model/code_spec_model.py:29 | raised by PythonBddModel.check_readable :204 | - | - | ok |
| CodeBddModel | bdd/model/code_spec_model.py:37 | base of PythonBddModel, TypeScriptBddModel | CodeLanguage, WrittenBlock, CodeBody | - | ok |
| PythonBddModel, TypeScriptBddModel | bdd/model/code_spec_model.py:195, :281 | Bdd formats bdd/bdd.py:40-41; BddGraph `_add_spec` bdd/graph_practice.py:57 | Description, Context, Observation | format adapters | ok |
| GraphBddModel | bdd/model/graph_bdd_model.py:28 | Bdd formats bdd/bdd.py:43 | SavedGraph, PracticeGraph | format adapter | ok |
| LayerIsolation, ObservableBehavior, SharedDescribeSubject, PlainEnglishOnly, SignatureMarkers, DescribeSubjectNotInternal, StateNotWhen, OneAssertionPerTest, NoImplementation | bdd/rules/layer_isolation.py:22; observable_behavior.py:43; shared_describe_subject.py:174; spec_rules.py:24, :35; tree_rules.py:22, :33, :44, :55 | `SPEC_RULES` bdd/rules/spec_rules.py:45, `RULES` bdd/rules/__init__.py:5, read by `rules_in` | node facts | rules registry | ok |
| AgentBdd | agent_bdd/agent_bdd.py:11 | no Python caller; published by the installer (installed skill `practices-agent-bdd`) | Bdd, Generate | `@agent_toolset`, `@agent_instructions` | ok |
| AgentHarnessError | agent_bdd/agent_bdd_common.py:52 | raised throughout agent_bdd_common, agent_block.py:85, :148, agent_cli_bdd.py:61, :70 | - | - | ok |
| AgentJudgeError | agent_bdd/agent_bdd_common.py:73 | raised by AgentBlock._verdict agent_block.py:153 | - | - | ok |
| ChatInboxPending | agent_bdd/agent_bdd_common.py:77 | raised by ChatAgentBlock agent_chat_bdd.py:29 | - | - | ok |
| ToolRunTimedOut | agent_bdd/agent_bdd_common.py:81 | raised by ToolRunDeadline.run :614 | - | - | ok |
| AgentResult | agent_bdd/agent_bdd_common.py:90 | AgentSession.run :331; ChatAgentBlock :18; CliAgentBlock agent_cli_bdd.py:291 | - | named in agent_bdd/agent_bdd.md:79 | ok |
| JudgeResult | agent_bdd/agent_bdd_common.py:103 | AgentBlock._verdict agent_block.py:150 | - | named in agent_bdd.md:79 | ok |
| RunResponse | agent_bdd/agent_bdd_common.py:204 | AgentBlock :160; ToolsetInvoke :550, :571; spec_helpers.py:14 | YamlFence | named in agent_bdd.md:3, :79 | ok |
| _ShellCapture | agent_bdd/agent_bdd_common.py:247 | AgentBlock agent_block.py:49-50; _StreamBuckets agent_cli_bdd.py:145, :170 | - | - | ok |
| HarnessLog | agent_bdd/agent_bdd_common.py:258 | AgentBlock agent_block.py:46; AgentSession :278, :302 | stdout | - | ok |
| AgentSession | agent_bdd/agent_bdd_common.py:271 | CliAgentBlock agent_cli_bdd.py:273, :295 | CursorCli, HarnessLog | - | ok |
| ToolsRunYaml | agent_bdd/agent_bdd_common.py:395 | AgentBlock agent_block.py:89; `yaml_from_prompt` :482; _StreamBuckets agent_cli_bdd.py:44 | YamlFence, `invoke_run_request` | - | ok |
| ToolsetInvoke | agent_bdd/agent_bdd_common.py:485 | `invoke_run_request` :591, :593 | AgentToolSet, Sessions, AgentOperation | - | ok |
| ToolRunDeadline | agent_bdd/agent_bdd_common.py:599 | `invoke_run_request` :593 | _TimedAttempt | - | ok |
| _TimedAttempt | agent_bdd/agent_bdd_common.py:618 | ToolRunDeadline.run :608 | - | - | ok |
| AgentSpecManifest | agent_bdd/agent_bdd_common.py:671 | only `read_manifest` :699, whose only caller is agent_bdd/agent_bdd_spec.py:65 | - | none | **D (spec-only)** |
| AgentBlock | agent_bdd/agent_block.py:37 | base of ChatAgentBlock, CliAgentBlock; `agent()` :193 | YamlFence, HarnessLog, ToolsRunYaml, JudgeResult, RunResponse | named in agent_bdd.md:15, :79; imported by templates/agent_bdd.py:19 | ok (spec support by design: the library agent specs import) |
| ChatAgentBlock | agent_bdd/agent_chat_bdd.py:11 | `agent()` agent_block.py:200 | AgentResult | named in agent_bdd.md:15 | ok |
| _StreamBuckets | agent_bdd/agent_cli_bdd.py:31 | CliAgentBlock._run :301 | ToolsRunYaml, _ShellCapture | - | ok |
| CliAgentBlock | agent_bdd/agent_cli_bdd.py:262 | `agent()` agent_block.py:202 | AgentSession, CursorCli, _StreamBuckets | named in agent_bdd.md:15 | ok |
| AgentBddConf | agent_bdd/conf.py:13 | `agent()` agent_block.py:197; conftest.py | RepositoryToolsets | - | ok |
| CursorAgentNotFound, ChatNotCreated | agent_bdd/cursor_cli.py:14, :21 | raised by CursorCli :201, :181, :184 and CliAgentBlock agent_cli_bdd.py:278 | - | - | ok |
| CursorCli | agent_bdd/cursor_cli.py:31 | AgentSession :309, :319; CliAgentBlock agent_cli_bdd.py:276, :321 | cursor-agent program | - | ok |
| YamlFence | agent_bdd/yaml_fence.py:13 | AgentBlock :45; ToolsRunYaml :401; RunResponse :240; `load_fenced` :55, used by harness/agent_tools/agent_tools_spec.py:45 | PyYAML | - | ok |
| OutputFolder | output_folder.py:12 | only clean_engineering/model/class_channel.feature.py:15, :140, :492 and stories/model/story_channel.feature.py:13, :247, :369 | shutil | none | **D (spec-only)** |

Evidence for the two D verdicts:
- **AgentSpecManifest** (and its builder `read_manifest`): grep for `AgentSpecManifest|read_manifest|agent-spec-manifest` across `*.py`, `*.ts`, `*.md` (excluding `.venv`, `retired`, `.sessions`) finds only `agent_bdd/agent_bdd_common.py` and `agent_bdd/agent_bdd_spec.py`. Not in any `formats` map, `RULES`/`BY_SLUG`, `PracticeCatalogue._REFS`, annotation, or recipe; `agent_bdd.md` never names the manifest header. Move it into the spec or delete it with its spec.
- **OutputFolder**: grep for `OutputFolder|output_folder` across `*.py`, `*.ts`, `*.md`, `*.yaml` finds only the two `*.feature.py` files above. No annotation, registry, formats entry, catalog or recipe use. It is feature-spec support; move it beside the features that use it (a spec-support module) or keep it only if spec support is allowed to live in `practices/`.

Spec support inside production modules, not classes but worth the same call: `agent_bdd/spec_helpers.py` holds the car fixtures (`CAR`, `CAR_CTX`, `invoke_request_for_path`, `stage_invoke_commands`, `ensure_invoke_staged`, `run_skill`, `command_path`, `car_tool_argument`), used only by `agent_bdd/spec_helpers_spec.py`; the template uses only `repo_root_from`, `sessions_dir`, `expect_ok_action`, `expect_instructions_contain`. `ux/scripts/emit_story_javascript.py` has no caller (relationship 38).

## 3. Disconnected classes, verified

### Clean Engineering: practice class, graph practice, rules, core class model

None in this slice. Section 2 of `.context/repo-model-disconnected.md` lists no class from clean_engineering.py, graph_practice.py, rules/, model/rules_shared/ or the top-level model files.

### Clean Engineering: format adapters

None in this slice (section 2 of `.context/repo-model-disconnected.md` has no class from these folders).

### Stories: practice class, graph practice, rules, core story model

| class | earlier | verdict | reason |
|---|---|---|---|
| Example | A (Scenario keeps its examples as Example) | confirmed A | `Examples.__setitem__` (model/story_model.py:258-264) makes and keeps Example parts for Scenario, Background, Epic and StoryModel. But `_StoryGraphRecording._scenario` (model/graph_story_model.py:270-273) does not use those objects: it adds bare Example nodes from names (W above). |
| DiagramStory | A (DiagramStoryModel makes its stories as DiagramStory) | confirmed A | `story_type = DiagramStory` (model/diagram_story_model.py:154), used by StoryModel._copy_map :941, and `story_y` reads its constants at :186. |
| JavaScriptStory | A (outside the seam) | not in this slice | It lives in model/javascript/ (another agent's slice). `story_test_type` in this slice also names it (model/story_model.py:1123). |

### Stories: format adapters

| class | earlier | verdict | reason |
|---|---|---|---|
| JavaScriptStory | A (outside the seam), javascript/javascript_story_model.py:22 `story_type = JavaScriptStory` | **confirmed A** | Wired by `story_type` (line 22); also by story_test_type (story_model.py:1123-1125) and ux/scripts/emit_story_javascript.py:68. To draw it, the Stories page needs JavaScriptStoryModel too. Its `create` is W (see the runtime table). |

### DDD

None in this slice (section 2 of `.context/repo-model-disconnected.md` lists no DDD class).

### UX, BDD, agent BDD, output_folder.py

| class | earlier | verdict | reason | owner and redesign |
|---|---|---|---|---|
| DesignCanvas (harness/design_canvas) | A (outside the seam), wired by `ClaudeDesignStoryModel.canvas` story_canvas.py:179 | **Confirmed A; the call is W (relationship 30)** | `canvas()` builds a new DesignCanvas from the model's name on every call and `files()` calls `canvas()` again; nothing holds it | Owner ClaudeDesignStoryModel, composition 1: build the canvas once when the model is made and keep it. ClaudeDesignStoryModel is reached only through the `story_canvas.md` recipe, so draw it on the UX page to show this wiring |
| UserHome (harness/mcp), evidence agent_bdd/spec_helpers.py:100 | B | **Confirmed B (relationship 86)** | `stage_invoke_commands` builds `UserHome()` and `SpecServer()` side by side and drives both; it is spec support (only spec_helpers_spec.py reaches it) | Owner SpecServer, composition 1: SpecServer holds its UserHome and enters/leaves it in `install`/`stop`, so agent BDD asks the server for its home |

## 4. Summary

| part | relationships checked | R | W | overturned | classes checked | D |
|---|---|---|---|---|---|---|
| Clean Engineering core | 58 | 31 | 27 | 4 | 75 | 4 |
| Clean Engineering formats | 73 | 46 | 27 | 7 | 55 | 0 |
| Stories core | 70 | 46 | 24 | 3 | 63 | 0 |
| Stories formats | 49 | 20 | 29 | 0 | 54 (+3 seed classes) | 4 (DomainModelLinks + 3 seed classes) |
| DDD | 58 | 24 | 34 | 1 | 52 | 0 |
| UX, BDD, agent BDD, output_folder | 87 | 58 | 29 | 1 | 94 | 2 |
| **Total** | **394** | **225** | **169** | **16** | **396** | **10** |

`StoriesGraph → TypeScriptStoryModel("tests")` is listed in both Stories parts. It is counted once in the total, which is why the total has one W fewer than the column sum. The Clean Engineering formats part also noted `CleanEngineering → Drawio` W → R, but that overturn is counted only in the Clean Engineering core part.

Overturned (16):
- W → R (13):
  - `CleanEngineering → Drawio`.
  - `CleanEngineeringModel → Module` and `→ OoadClass`; `Module → OoadClass`.
  - `ArrowRouter → DiagramArrow`; `DiagramCard → Geometry`.
  - `PythonCleanEngineeringModel → OoadClass`, `→ Property`, `→ CodeBody` (parse side).
  - `Scenario → Step`.
  - `Stories → StoryModel.load_files`; `StoriesGraph → StoryModel.load/load_files`.
  - `AgentBdd → Generate`.
- R → W (3):
  - `MarkdownCleanEngineeringModel → CleanEngineeringModel._render_cards`.
  - `PythonCleanEngineeringModel → CleanEngineeringModel` (renders a second model).
  - `DddGraph → GraphPractices.named`.

**D: no use, delete (10 classes):**
- `File` (`clean_engineering/model/base_class_model.py:416`): nothing builds or reads it.
- `UpdateReport`, `Change`, `ChangeKind` (`clean_engineering/model/update_report.py`): production builds the report, but every caller discards it. Only `base_class_model_spec.py` reads it (spec-only). `ChildCollectionPair` and `TranslationError` in the same file stay.
- `DomainModelLinks` (`stories/model/markdown/links.py:154`): spec-only. `MarkdownStoryModel` accepts it as an optional parameter, but no production caller passes one.
- `_Background`, `StoryNodeTransformer`, `StoryExampleCollector` (`stories/model/python/seeds/story_test.py`): nothing reads or copies the file. The copies in use are `stories/templates/py/story_test.py` and `space/kanban/story_test.py`.
- `AgentSpecManifest` with `read_manifest` (`agent_bdd/agent_bdd_common.py`): spec-only (`agent_bdd_spec.py`).
- `OutputFolder` (`practices/output_folder.py`): spec-only (`class_channel.feature.py`, `story_channel.feature.py`).
