# Design judgment: Clean Engineering, DDD, BDD, agent BDD, TDD, sketch document

Judged: the production Python under `cdd_guidance/practices/{clean_engineering, ddd, bdd, agent_bdd, tdd, sketch_document}` (practice classes, `model/` packages with their format adapters, graph readings, `rules/`). `_examples`, templates, fixtures, and practice markdown were left out; specs were read only to see how a class is used. Stories and UX were read for comparison only.

How it was checked: every production file was outlined (classes, operations, signatures, line counts); an import table was built with `ast` for every file, counting imports inside functions and `importlib` calls; each public name was searched across the repository before any "unused" or "used in one place" claim. The large files were read with docstrings removed. Files read in outline plus targeted ranges rather than line by line: `c_family_parse.py`, `python_class_model.py`, `diagram/class_layout.py`, `ddd/model/markdown/nodes.py`, `code_class_model.py`. Findings in those files are limited to what the ranges read confirm.

Theme tags: [1] module boundaries, [2] the same work in different shapes, [3] resource orientation, [4] domain orientation.

## Findings

### cdd_guidance/practices/clean_engineering/model/graph_reading.py

- graph_reading.py:28 `CardLines` import — one-way-deps — This is the one import that closes the `model` ↔ `model/markdown` cycle the graph reports: `graph_reading.py` (a file of `model/`) imports `model/markdown/card_lines.py`, and `markdown_class_model.py` imports `base_class_model`, `operation`, `property`, `field_types`, `type_refs`, `source_facts`, `call_graph`, and `class_stereotypes` back. `CardLines` is used only by the two graph readings (here at :162 and `ddd/model/graph_reading.py:590`), never by the markdown adapter, so it sits in the wrong package. [1]
- graph_reading.py:34 `GraphReading` — use-consistent-naming — The other practices name theirs `DddReading`, `BddGraphReading`, `StoriesReading`, `UxReading`; Clean Engineering's carries no practice name, so a reader of `bdd/model/graph_reading.py` cannot tell from the type which reading it holds. [4]
- graph_reading.py:54 `code_index`, :55 `model_documents` — public-seam-only — BDD and Stories call these (`bdd/model/graph_reading.py:192,202`, `bdd/model/graph_bdd_model.py:78,119`, `stories/model/graph_reading.py:434,502`), yet the module card's seam terms name neither, so the real seam between the practices is undocumented and typed as the base `PracticeReading`. [1]
- graph_reading.py:212 `_every_folder` — eliminate-duplication — The same `os.walk` with `dirnames[:] = [... if not skips_folder(name)]` is written again at `code_read.py:442`, `ddd/model/graph_reading.py:379` and `:434`; `harness/graph/skipped_folders.py:54` already owns the walk for files but offers none for folders. [2]

### cdd_guidance/practices/clean_engineering/model/call_links.py

- call_links.py:54 `ClassesInReach`, :120 `ClassLinks`, :160 `CallLinks`, :210 `CallerBody` — shape-classes-around-resources — Four classes are each made from `reading`, copy `reading.graph`, `reading.in_graph`, and `reading.code_index` into their own fields, run once (`link()`), and are thrown away (`graph_reading.py:62-68`). They are steps of one read, acting on graph nodes they treat as data; the graph hit "ClassLinks copies the fields of ClassNodes" is this pattern showing. [3]
- call_links.py:72 `_in_reach` — eliminate-duplication — "Which class does this file mean by this name" is answered here and again by `ImportedClasses.resolve` (`imported_classes.py:27-49`), and both rebuild `ClassReference` lists from the same `imported_classes_by_file` fact (`call_links.py:109-117`, `module_exposure.py:115-124`). Two resolvers will disagree on re-exports: only `ImportedClasses` follows them. [2]
- call_links.py:135 and :339 base-name parsing — eliminate-duplication — `str(base).split("[")[0].split("<")[0].strip()` is written twice here, `ClassGraph.bases_of` (`class_graph.py:116`) strips a dotted prefix and `[` but not `<`, and `class_facts.py:118` compares the raw `bases` fact. A base written `pkg.Base[T]` gets three different names. [2]
- call_links.py:234 `_class_declaring` — hold-state-on-the-object-not-in-parameters — A member's class is found by reading the member's `owner` name and searching classes of that name in the same file, although `code_read.py:284` already joined the two nodes with an `owns` edge. `get_fact("owner")` is compared against a class name in 20 places across the practices. [3]
- call_links.py:48 `_language_of` — prefer-class-operations — A module function used only by `ClassesInReach._beside`; and "what language is this file" is asked four more ways (`operation_counts.py:30`, `rules/operation_checks.py:139`, `rules/module_graph_rules.py:48`, `bdd/model/graph_reading.py:122`) while every node already answers `file_language` (`harness/graph/graph.py:708`). [2]

### cdd_guidance/practices/clean_engineering/model/code_read.py

- code_read.py:49 `CodeRead`, :143 `OutsideScope`, :205 `DescribedClasses`, :226 `ClassNodes`, :318 `CodeFolders` — shape-classes-around-resources — Five more one-read doers, each unpacking the same `reading`; `ClassNodes.add(relative, folder, cls)` and `CodeFolders.take(relative, module)` are handed the path, the folder node, and the model on every call because none of the three knows the other two. [3]
- code_read.py:188, :218, :375 folder lookup — eliminate-duplication — `{node.source.file: node for kind in ("Module", "Package") ...}` is rebuilt three times here and again at `call_links.py:112`, `ddd/model/graph_reading.py:244`, `folder_facts.py:38`, `rules/practice_wide_rules.py:165`, `rules/coupling_rules.py:97`. The pair `("Module", "Package")` is a constant twice (`folder_facts.py:15`, `rules/practice_wide_rules.py:20`) and a literal seven times. [2]
- code_read.py:245-247 add, own, belong — eliminate-duplication — Every practice spells a node id with an f-string and then makes the same three calls (`in_graph.add`, `edges.link("owns", …)`, `edges.relate("belongsTo", …)`): here, `ddd/model/graph_reading.py:400-404`, `:444-446`, `:554-556`, `:690-694`, `:773-775`, and `bdd/model/graph_reading.py:98-105`. A change to how a child joins its parent has to be made in eight places. [2]
- code_read.py:354, :367, :408, :430 parent folder — eliminate-duplication — `str(Path(x).parent).replace("\\", "/")` four times, beside `folder_facts.parent_folder` (`folder_facts.py:33`, empty string at the root) and DDD's `folder_of` (`ddd/model/graph_reading.py:540`, `"."` at the root). Two functions give different answers for a file at the root. [2]
- code_read.py:464-466 `module.type = "Module" / "Package"` — use-intention-revealing-names — One `Module` class stands for two node types, chosen by assigning a string to `type` after construction; "package" is a term of the practice (a folder with no module card) with no class of its own. [4]
- code_read.py:40 `DESCRIBED_FACT` — low-coupling — A fact name private to this read is imported by `ddd/model/graph_reading.py:27` and tested with `has_fact(DESCRIBED_FACT)` in eight places, so "is this class described by a model document" is a string lookup in another practice instead of a property of the class. [1]

### cdd_guidance/practices/clean_engineering/model/class_graph.py

- class_graph.py:72 `ClassGraph` — put-logic-on-the-owning-resource — `fields(node)`, `bases_of(node)`, `operations(node)`, `has_behavior(node)`, `is_production(node)`, `is_mixin(node)` (:96-127) each take the class they are about: the class node is a data bag and the logic about one class lives on an index of all of them. The name also misleads; it is no graph but the production classes by name. [3]
- class_graph.py:77 `classes` — hide-inner-details — A public list that five recorder classes iterate directly (`class_facts.py:54,84,89,213,250`, `module_exposure.py:51`). [3]
- class_graph.py:186 `parameters_of`, :192 `names_in` — prefer-class-operations — Module functions that take a node and a type hint; `parameters_of` is imported across the practice boundary by `bdd/model/graph_bdd_model.py:21`. [3]

### cdd_guidance/practices/clean_engineering/model/class_facts.py, operation_facts.py, folder_facts.py, module_exposure.py, compared_facts.py

- class_facts.py:45 `ResourceShapes`, :76 `ParallelModels`, :201 `Forwarding`, :272 `DomainExtensions`, :318 `BuiltCollaborators`; operation_facts.py:23 `BodyCopies`, :76 `FailureMessages`; folder_facts.py:48 `ImportCycleFacts`, :74 `SiblingFanOut`; module_exposure.py:22 `ModuleExposure`; compared_facts.py:31 `ComparedFacts` — shape-classes-around-resources — Eleven classes with one public `record()`, each built from `(in_graph, classes)` (the "__init__ duplicates the body of __init__" graph hits), each writing one or two string-keyed facts onto nodes. The rule that reports the fact is a second class in `rules/` that reads the same string (`constructs_collaborator`: written `class_facts.py:330`, read `rules/operation_checks.py:98`), so every rule is split into a measurer and a reporter joined by a key. The area uses 86 distinct fact keys this way. [3]
- class_facts.py:45 `ResourceShapes`, :201 `Forwarding`, compared_facts.py:31 `ComparedFacts`, folder_facts.py:48 `ImportCycleFacts` — use-intention-revealing-names — The names say neither what the object is nor which rule it serves: `ResourceShapes` finds services that take data bags, `Forwarding` finds pass-through classes, `ComparedFacts` runs the other ten. [4]
- folder_facts.py:18 `record_fact`, :26 `is_under`, :33 `parent_folder`, :38 `folders_of`, :43 `imported_folders`; class_facts.py:38 `record_on_production_classes` — prefer-class-operations — Six module functions that take the node or the practice's nodes as their first parameter and reach into it. [3]
- module_exposure.py:93 `ClassNamers` — eliminate-duplication — `_references` (:115-132) rebuilds each file's `ClassReference` list from folder facts, the same work as `ClassesInReach._imports_of` (`call_links.py:109-117`). [2]

### cdd_guidance/practices/clean_engineering/model/source_facts.py

- source_facts.py:58 `ClassSourceFacts`, :140 `OperationSourceFacts`; base_class_model.py:440 `ModuleSourceFacts` — hide-inner-details — `load()` copies a dict onto its owner with `setattr` (`source_facts.py:79-80`, `:168-169`; `base_class_model.py:467-468`), so `OoadClass` gains `method_count`, `operation_shapes`, `property_names`, `constructs`, `prose_comment`, and `prototype_swap` that no constructor declares; only the `graph_facts` tuple (`base_class_model.py:99-114`) names them. A misspelt key makes a new attribute and nothing fails. [3]
- source_facts.py:90 `operation_shapes` — do-not-invent-parallel-object-models — Each operation is kept a second time as a dict (`name`, `is_property`, `is_private`, `callees`, built at :131-137) on its class, and read as a dict by `class_graph.py:118-123`, `operation_counts.py:29-39` (`shape: dict`), and `rules/class_rules.py:23`, beside the `Operation` nodes the graph already holds. [2]
- source_facts.py:33 `CONSTRUCTOR_NAMES` — eliminate-duplication — The same two names are a second constant at `bdd/model/graph_reading.py:32` and a third at `cdd_guidance/actions/render/reshaped_code.py:48`; `Operation.is_constructor` (`operation.py:76`) answers the question, yet `class_graph.py:121`, `class_facts.py:349`, `operation_counts.py:31`, and `markdown/markdown_class_model.py:793` test the name against the constant. [2]
- source_facts.py:58, :140 `*SourceFacts` — use-intention-revealing-names — "Facts" names the storage (graph facts), not the thing: these are the class's and the operation's source span and what was measured in it. [4]

### cdd_guidance/practices/clean_engineering/model/operation.py, property.py, base_class_model.py, field_types.py

- operation.py:69 `Operation` — keep-classes-single-responsibility — One class holds the designed operation (name, parameters, return type, callees, invariants), where its code is (line, body, fingerprint), and seventeen rule measures as flat fields (:159-177); 28 names in `graph_facts` (:85-114). A change to any rule's measure edits the class every format adapter subclasses. [4]
- operation.py:280 `_copy_measures_from` — eliminate-duplication — `clone()` copies six of the seventeen measures (:282-287); `packed_parameters`, `io_and_domain`, `raises_on_empty`, `mutates_without_record`, and seven more are dropped. It is correct only while every clone is measured again, which nothing states. [3]
- operation.py:236 import inside `take_parameters` — one-way-deps — `type_refs` is already imported at the top (:14) and does not import `operation`, so the inner import hides nothing and should not be there. [1]
- base_class_model.py:28 `MODULE_FUNCTION_HOLDER` — use-intention-revealing-names — A module function is modelled as an operation of a class named `"_module"`, and nine production places compare a name to that constant to tell functions from methods (`call_links.py:69,94`, `class_graph.py:127`, `module_exposure.py:57`, `rules/class_rules.py:23`, `bdd/model/graph_reading.py:268`, `stories/model/graph_reading.py:455`, `space/session/session_file.py:330`). The domain has module functions; the model has none. [4]
- base_class_model.py:94 `OoadClass`, ooad_node.py:17 `OoadNode` — use-intention-revealing-names — An abbreviation (object-oriented analysis and design) on the central class of the practice, whose own rules say "class" and "do not abbreviate". The name is in 316 lines of 85 files and is the node type in saved graphs, so this is recorded, not proposed for change. [4]
- base_class_model.py:36-92 — prefer-class-operations — Seven module functions about names (`path_parent`, `is_interface_name`, `interface_name_for`, `production_name_for`, `example_extension_kind`, `base_type_name_for`, `companion_interface_name`) above the classes they serve; `production_name_for` and `interface_name_for` are used only inside this file. [3]
- base_class_model.py:486 `CleanEngineeringModel.__init__(name: str | Graph)` — use-typed-signatures — The first parameter is a name or a graph, sorted out with `isinstance` (:487-490); a caller cannot tell from the signature which one to pass. [3]
- field_types.py:21 `Relationship` — use-intention-revealing-names — The file holds one class, `Relationship`, and is named for something else; `base_class_model.py`, likewise, is the class model itself, not a base. [4]

### cdd_guidance/practices/clean_engineering/model/type_refs.py

- type_refs.py:38-79 — put-logic-on-the-owning-resource — A type hint is a bare string handed to six functions here, and parsed again in five other files: `names_in` (`class_graph.py:192`), `_names_in` and `_HINT_WORD` (`code_read.py:43,304`), `_COLLECTION` and `_OPTIONAL` (`call_links.py:38-39`), `_key_type` (`class_facts.py:184`), `_TYPE_WORD` (`ddd/model/graph_reading.py:69`). No object owns "the classes this hint names", "what this collection holds", or "is this optional". [2]

### cdd_guidance/practices/clean_engineering/model/operation_metrics.py

- operation_metrics.py:169 `SourceText` and :477 `PythonFunctionBody` — eliminate-duplication — Two unrelated classes answer the same questions about an operation body, one from text and one from Python's syntax tree: `control_flow_depth` (:185 / :488), `unnamed_numbers` (:201 / :551), `reaches_peer_private` (:345 / :603), `built` (:362 / :629), catch-all and swallow (:283-288 / :546). They share no type, so each caller picks one by language and a new measure is written twice. [2]
- operation_metrics.py:169 `SourceText` — low-coupling — Imported from this practice's `model` by two pattern packages (`cdd_guidance/patterns/cdd_web_domain_access/access_facts.py:9`, `cdd_guidance/patterns/lern_domain_driven/tier_facts.py:12`); it is a general tool for reading source text kept inside one practice's metrics file. [1]
- operation_metrics.py:400 `CardBullets` — high-cohesion — The bold bullets of a markdown model card are read in the file that measures operation bodies. [1]

### cdd_guidance/practices/clean_engineering/model/production_code.py, script_imports.py, code_body.py

- production_code.py:84 `is_spec_file`, :89 `is_test_code`, :94 `is_example_code` — low-coupling — The repository's convention for which files are tests is three module functions inside Clean Engineering's `model`, imported by the session code (`space/session/practice_session_output.py:11`, `space/session/proposed_roots.py:9`), by BDD, DDD, and the rules. `space/` reaches four folders into a practice for a file-name rule. [1]
- code_body.py:45 `CodeLanguage`, :127 `CodeBody`, :191 `BraceCall`, :223 `WrittenBlock`, :292 `InsideLines`; bracket_structure.py:7; call_graph.py:35 — low-coupling — Stories imports these from Clean Engineering's `model` in 14 files and BDD in 7. They model source text in a language, not the class model, and have no seam: `clean_engineering/model/__init__.py` is one line, so every caller names an internal file. [1]
- script_imports.py:122 `PythonImports`, :167 `ScriptImportClauses` — eliminate-duplication — Two classes with the same three fields and the same `references()` and no shared type, chosen by file suffix at :80 (the graph hit is real). [2]

### cdd_guidance/practices/clean_engineering/model/markdown/card_lines.py, markdown_class_model.py

- card_lines.py:31-35, :65-72 — eliminate-duplication — Headings and the lines under a heading are scanned by hand, although `harness/markdown/markdown.py` gives `MarkdownText.headings()` (:160) and `section_lines()` (:213). The `_HEADING` pattern at :16 is repeated at `markdown_class_model.py:57` and `sketch/sketch_class_model.py:29`, and `markdown_class_model.py:720-731` is a third heading scan. [2]
- markdown_class_model.py:116 `MarkdownOoadClass` — eliminate-duplication — Reads and writes the class-card notation (`------` properties, `----` operations, `-> callee`, `// note`, `+`/`-` access, `<< kind >>`) in about 175 lines (:138-169, :213-355). DDD writes the same reader and writer again; see `ddd/model/markdown/class_cards.py`. [2]
- markdown_class_model.py:757 `UnwrittenProse` — eliminate-duplication — Gives a rendered class back the words only the earlier file held (intent, callees, invariants, description) by matching members by name (:784-802). DDD's `_ReplacedCard` does the same on the same `Operation` and `Property` objects (`ddd/model/markdown/replaced_document.py:130-156`). [2]

### cdd_guidance/practices/clean_engineering/model/drawio/

- drawio/page/drawio_page.py:139-236 — put-logic-on-the-owning-resource — Twelve module functions take a raw `ET.Element` or a style string (`class_title_in`, `class_name_in`, `cell_box`, `edge_kind`, `is_inheritance`, `anchor_fractions`, `share_inheritance_trunk`, `style_value`, `style_number`, `anchor_point`, `segment_hits_box`, `quoted_title`). A cell and an arrow of a drawing have no object; every scanner passes XML elements around. [3]
- drawio/page/drawio_page.py:20 `DrawioPage` — eliminate-duplication — A third reader and writer of a draw.io file: Stories has `_DrawIOPage`, `_KeptPlaces`, and `_drawn_geometries` (`stories/model/drawio/nodes.py:250-322`) and its own parse (:459-523); UX has `CellStyle` and its own cell walk (`ux/model/drawio/nodes.py:90-117`, `:368-401`); `cdd_guidance/actions/render/kept_document.py` and `harness/catalog_generator/drawio_diagram.py` read the file again. The page skeleton (`mxfile` → `diagram` → `mxGraphModel` → `root` → cells `0` and `1`) is written at `drawio_class_model.py:438-445` with `:520-524` and at `stories/model/drawio/nodes.py:253-258`. [2]
- drawio/drawio_class_model.py:283 `_read_arrows` — eliminate-duplication — The same steps as `whiteboard/whiteboard_class_model.py:670-684` `_take_arrows` (inheritance to bases, `«label»` to a dependency, `take_arrow`, then `prop.arrow.derive()`), and `_DEPENDENCY_LABEL` is defined in both files (:78 and whiteboard :76). [2]
- drawio/drawio_class_model.py:92-95 `previous`, `keep_positioning`, `close_gaps` — hold-state-on-the-object-not-in-parameters — The earlier drawing reaches the model two ways: as the `previous` parameter of `render` and as a public field `drawio.py:68-69` sets from outside, reconciled by `previous or self.kept_previous()` (:140-145). [3]
- drawio/drawio_class_model.py:515, :520, :527, :550, :568 — prefer-class-operations — Five module functions; `_class_card_members` returns a four-part tuple that `_class_cards` unpacks and that `_folded_classes` rebuilds for each folded class. [3]
- drawio/scanners/_drawio_base.py:24 `DrawioScanner` — keep-classes-single-responsibility — The base of each layout scanner is also the runner of all of them (`run_report` :102 makes every scanner), the command line (`run_main` :121 with `argparse`), the file collector (:136), and the registry (`every` :80). [3]
- drawio/scanners/_drawio_base.py:96 `importlib.import_module` — one-way-deps — The base imports each of its subclasses' files by name at run time while each of those files imports the base; by the rule this is a cycle between the files of one folder. [1]
- drawio/scanners/_drawio_base.py:80 `every` — eliminate-duplication — Layout rules are a second rule mechanism beside `PracticeGraphRule`: found by a glob over `*_scanner.py`, keyed by a `RULE` attribute read with `getattr` (:28, :88), run by their own runner, while `rules/__init__.py` lists the practice's other rules in a tuple. [2]
- drawio/drawio.py:14 — low-coupling — The toolset imports `scanners._drawio_base`, a file whose name marks it private. [1]
- drawio/drawio.py:113 `verify_regression` — abstraction-focus — A published tool that discards its one parameter (`_ = examples_root`) and returns a fixed sentence. [4]

### cdd_guidance/practices/clean_engineering/model/diagram/

- diagram/geometry.py:11 `Geometry` — eliminate-duplication — A second rectangle beside `harness/whiteboard/whiteboard.py:36` `Box` (`x, y, w, h`); `whiteboard/whiteboard_class_model.py:148-150` converts one to the other field by field. `Point` is an alias here (:7) and a different alias at `diagram/class_layout.py:21`. [2]
- diagram/class_layout.py:412 `_RouteGrid.is_open_for`, :436 `carries_arrow` — no-legacy-api-after-refactor — No caller in the repository. [3]
- diagram/class_view.py:319 `plain_class_name` — use-consistent-naming — A second function of the same name at `ddd/model/stereotypes.py:55` strips more (code marks, ` extends `, ` : `), so the same name gives two results depending on the import. [2]

### cdd_guidance/practices/clean_engineering/rules/

- rules/operation_checks.py:118 `operation_label`, :123 `operation_line_count`; rules/limit_operation_parameters.py:28 `counted_parameters`; rules/module_graph_rules.py:46 `_python_class_folder`; rules/practice_wide_rules.py:165 `_folders` — prefer-class-operations — Module functions that take the node they are about; `_folders` and `operation_line_count` each have one caller. [3]
- rules/rule_examples.py:89 `assert_python_example_pair`, :109 `assert_module_example_pair` — no-legacy-api-after-refactor — No caller in the repository. [3]

### cdd_guidance/practices/ddd/model/graph_reading.py

- graph_reading.py:31 `MarkdownBoundedContextMap` import — one-way-deps — This is the import that closes the DDD `model` ↔ `model/markdown` cycle: `graph_reading.py` (a file of `model/`) imports `model/markdown/nodes.py`, and `markdown/nodes.py:19`, `markdown/class_cards.py:15,25`, and `markdown/replaced_document.py:15` import `model/nodes.py` and `model/stereotypes.py` back. [1]
- graph_reading.py:27-30 — low-coupling — Four imports of Clean Engineering internals: `code_read.DESCRIBED_FACT`, `field_types.Relationship`, `markdown.card_lines.CardLines`, `production_code.is_test_code`. Across the practice DDD imports 13 different Clean Engineering files, none through a seam. [1]
- graph_reading.py:72 `BuildingBlock` — do-not-invent-parallel-object-models — A second node for a class the graph already holds, joined to it by an `isA` edge (:450), which answers `facts`, `has_fact`, and `get_fact` by falling through to the first node (:139-151). It wraps a `TacticalClass`, which wraps an `OoadClass`: three objects for one class. [2]
- graph_reading.py:326 `_WorkingCopyRead` (212 lines), :623 `_DescribedDomain` (168 lines) — shape-classes-around-resources — Two doers that read everything; the document, the aggregate, and name pairs are handed down through four- and five-parameter operations (`_link_sides` :512, `_AggregateBlocks.add` :551, `_read_block` :703, `_read_mapping` :745) because the aggregate being read is not an object that reads itself. [3]
- graph_reading.py:375, :408 tuple types — use-typed-signatures — `list[tuple[str, BoundedContext, str]]` (a marked context: folder, context, marker file; :375, :386, :397, :492), `tuple[TacticalClass, str]` (a class and its kind; :248, :408, :423, :440), and `tuple[str, str]` keys (context name, aggregate name; :638-639, :703, :745) stand for three concepts with no name. [4]
- graph_reading.py:584 `_DomainDocument` — eliminate-duplication — One object holds `CardLines`, `MarkdownText`, the raw lines, and its own `## ` scan (:598-602): three heading readers for one document. [2]
- graph_reading.py:202 `_domain_classes`, :185 `own_graph_checks` — hold-state-on-the-object-not-in-parameters — The Clean Engineering reading is found as `practice.working_set.extended` then `graph.practices.loaded(type(extended))`; BDD writes `graph.practices.loaded(CleanEngineering)` (`bdd/model/graph_reading.py:73`); both also declare `reads_after = ("clean_engineering",)` as a name string (:164, bdd :40). The reading it depends on is looked up three ways and held nowhere. [3]
- graph_reading.py:540 `folder_of` — prefer-class-operations — A module function used ten times in this file on `node.source.file`; the folder of a node's file belongs to the node's location. [3]

### cdd_guidance/practices/ddd/model/nodes.py, stereotypes.py

- nodes.py:49 `Integration` — shape-classes-around-resources — Nine string fields read and written by name through `FIELDS` and `PARTS` tuples with `getattr` and `setattr` (:85, :97; `markdown/nodes.py:132,138`): a record whose behaviour (reading an arc, writing its lines) is on a subclass in the markdown package. [3]
- nodes.py:100 `InvariantObject(DomainNode, Property)`, :161 `DomainEvent(DomainNode, Property)`, :200 `Aggregate(DomainNode, Module)`, :376 `BoundedContext(DomainNode, Module)` — use-intention-revealing-names — The domain terms are made by inheriting Clean Engineering's drawing types: a domain event is a property appended to its root's properties (:667), which `markdown/class_cards.py:144-145` then has to filter back out with `isinstance`. The API says an event is a kind of property and an aggregate a kind of module. [4]
- nodes.py:462 `BoundedContextMap` — abstraction-focus — The model's root asks format questions of itself: `holds_document_words` (:493), `holds_classes_only` (:512), `has_class_cards` (:518) exist so one format can tell which other format made the object. [4]
- nodes.py:416 `BoundedContext.context_file`, :345 `ContextFile.naming` — no-legacy-api-after-refactor — Called only from specs (`model/context_file_spec.py`, `context_links_alignment_heavy_spec.py:86`); no production code writes a context's file through them. [3]
- stereotypes.py:23 `KIND_OF_STEREOTYPE`, :35 `BUILDING_BLOCK_KINDS` — put-logic-on-the-owning-resource — A building block's kind is a string (`"EntityRoot"`, `"Repository"`, …) compared throughout the reading and rules, while `Entity`, `ValueObject`, `Repository` classes exist in `nodes.py`; `markdown/class_cards.py:415` keeps a dict from the kind string to a class. [3]
- stereotypes.py:55-100 — prefer-class-operations — Six module functions (`plain_class_name`, `root_kept_by`, `kind_named_by`, `carries_a_stereotype`, `names_a_building_block`, `marks_another_system`) beside `TacticalClass`, which answers the same kind of question as an object. [3]

### cdd_guidance/practices/ddd/model/markdown/class_cards.py, nodes.py, replaced_document.py

- class_cards.py:65 `ClassCard`, :233 `_CardBody` — eliminate-duplication — A second reader and writer of the class-card notation (:148-229, :233-265), with its own `_OPERATION` and `_PROPERTY` patterns (:424-425), although `Operation.from_signature` says "every format that writes members as such lines reads them here" (`clean_engineering/model/operation.py:180`). About 115 lines repeat `MarkdownOoadClass`. [2]
- class_cards.py:268 `_SketchFence` — eliminate-duplication — 104 lines that read a sketch fence "the way the clean-engineering sketch" does, beside `SketchOoadClass.read_member` and `read_uml_member` (`clean_engineering/model/sketch/sketch_class_model.py:111-190`). [2]
- class_cards.py:76-118 — prefer-instance-operations — Five `@staticmethod`s on `ClassCard`; `read` and `_named` are not creation names the rule exempts, and `ClassCard._named(...)` is called through the class (:87, :109). [3]
- class_cards.py:374-409 — class-not-property-instance-or-subtype — Seven empty classes (`MarkdownClass`, `MarkdownValueObject`, `MarkdownRepository`, `MarkdownDomainService`, `MarkdownSpecification`, `MarkdownFactory`, and `MarkdownEntity` with one override) exist only to join `ClassCard` to each kind. [2]
- class_cards.py:43 `MarkdownDomainNode` — shape-classes-around-resources — A base class of three string helpers that read no state (`plain_name`, `member_name`, `owner_from`), mixed into every markdown node. [3]
- nodes.py:141 `MarkdownAggregate` — keep-classes-single-responsibility — 331 lines and ten public operations (the graph hit is real): it reads map lines, sketch lines, and class cards, infers relationships, and writes all three forms. [3]
- nodes.py:155-173, :533-575 sketch reading on markdown nodes; :53-59 exported `SKETCH_INDENT`, `SKETCH_CONTEXT`, `BUILD_ORDER`, `fenced`, `sketch_level` — one-way-deps — The sketch format is half inside the markdown format: `sketch/sketch_ddd_model.py:10-18` imports markdown's constants and node types, and the markdown nodes carry `take_sketch_line`, `load_sketch`, `sketch_lines`, `read_sketch_lines`. Neither format can change without the other. [1]
- nodes.py:480-485 `notes`, `module_notes`, `group_notes` — single-boundary — Words every format must keep are fields of the markdown subclass only, so the drawn map and the sketch build markdown nodes to have somewhere to put them (`drawn/drawn_map.py:13,84`, `sketch/sketch_ddd_model.py:41`), and `ReplacedDocument` reads them off objects typed as the base. The markdown subclass is the real model. [1]
- nodes.py:84-120 `MarkdownIntegration.read_arcs`, `targeting`, `kept_by` — prefer-instance-operations — Three `@staticmethod`s outside the exempt creation names. [3]

### cdd_guidance/practices/ddd/model/drawio/, whiteboard/, ddd.py, rules/

- drawio/drawio_bounded_context_map.py:31 `DrawIOBoundedContextMap`, whiteboard/whiteboard_bounded_context_map.py:69 — use-intention-revealing-names — Each is a bounded-context map and a Clean Engineering class model at once, and has to call the second parent through its class (`DrawIOCleanEngineeringModel.render(self, self, previous)` :43, `.parse(self, text)` :57; whiteboard :81, :94) to say which one it means. [4]
- drawio/drawio_bounded_context_map.py:13-14, whiteboard/whiteboard_bounded_context_map.py:16-22 — low-coupling — Imports of Clean Engineering's drawio and whiteboard internals (`DrawIOModule`, `ClassBoard`, `WhiteboardModule`). [1]
- ddd.py:23-37 `_FORMATS` — one-way-deps — Seven adapters named by module-path and class-name strings for the framework to import, three of them Clean Engineering's code models; an import written as a string is still a dependency, and a rename of the target breaks it at run time with nothing to find it by. [1]
- rules/tactical.py:9 — low-coupling — A rule imports `CONSTRUCTOR_NAMES` from Clean Engineering's `source_facts`. [1]

### cdd_guidance/practices/bdd/model/graph_reading.py, nodes.py, graph_bdd_model.py

- graph_reading.py:114, :179 `clean: PracticeReading` — low-coupling — Typed as the framework's base but used as Clean Engineering's reading: `.code_index` (:192, :202) and, in `graph_bdd_model.py:78`, `.model_documents` exist only on `GraphReading`. The type hides which module BDD depends on. [1]
- graph_reading.py:108 `ObservationLinks`, :174 `ImportedCode`, :229 `ReachedMembers`; nodes.py:64 `reach_of` — eliminate-duplication — A third resolver from "the names this code calls" to graph members, about 155 lines, beside Clean Engineering's `CallerBody` and `ClassesInReach` (`clean_engineering/model/call_links.py:54-117, 210-340`) and Stories' `StoryLinks` and `ImportedFiles` (`stories/model/graph_reading.py:299-513`). The patterns at `nodes.py:25` (`_BARE_CALL`) and `:33` (`_BUILT`) repeat `call_links.py:32` and `:35`. Each resolver has its own rule for a name two classes share, so one call can link to different members depending on which practice asks. [2]
- nodes.py:52 `Reach`, :64 `reach_of`, :37 `private_probe_in_text` — shape-classes-around-resources — What a block reaches is a dict built by a module function, saved as a fact, and interpreted by `ReachedMembers` in another file with `reach.get("names")`, `reach.get("receivers", {})`: a data bag and a doer. [3]
- graph_reading.py:83 and :182 — hide-inner-details — A spec's imports are flattened to lists (`[list(reference) …]`) to be saved, then rebuilt as `ClassReference(*pair)`; the same rebuild is at `clean_engineering/model/call_links.py:116` and `module_exposure.py:123,130`. Four places know how a `ClassReference` is stored. [3]
- graph_reading.py:30 `_PYTHON` — eliminate-duplication — `(node.file_language == _PYTHON) == is_python` is written five times (:122, :135, :181, :195, :207). [2]
- nodes.py:119 `children_blocks` — hide-inner-details — The base `BehaviorNode` reads `contexts` and `observations` with `getattr` because only its subclass `DescribeBlock` declares them (:127-129); `bdd_model.py:77-78` and `:119` do the same. [3]
- graph_bdd_model.py:31 `Member = tuple[str, str]` — put-logic-on-the-owning-resource — A member is carried as (owner name, member name) and looked up again by both strings (:115-119) where the graph holds the member's node. [3]

### cdd_guidance/practices/bdd/model/spec_reshape.py, code_spec_model.py, bdd_model.py, spec_source.py

- spec_reshape.py:32 `SpecBlock`, :58 `SpecOutline` — do-not-invent-parallel-object-models — A second reading of a spec file into its own block tree, beside the model's `Description`, `Context`, and `Observation`, which already hold `line`, `end_line`, and `written` (`nodes.py:95-97`). `_python_name` (:102-108) repeats `PythonBddModel._block_kind` (`code_spec_model.py:324-332`). [2]
- spec_reshape.py:62, :125 `python_kinds`, `script_calls` — hold-state-on-the-object-not-in-parameters — The constructor is told its language three ways: `language`, a dict of mamba block names, and a callable; which of the last two is `None` picks the parser (:66). The format adapter that makes it (`code_spec_model.py:295`, `:376`) already is the language. [3]
- spec_reshape.py:26 `NO_LONGER_IN_MODEL` — eliminate-duplication — The same sentence is a constant in five files: here, `stories/model/reshaped_story_file.py:34`, `ux/model/view/reshaped_view.py:29`, `cdd_guidance/actions/render/kept_document.py:33`, `cdd_guidance/actions/render/reshaped_code.py:37`. A reader's search for kept blocks depends on all five staying equal. [2]
- bdd_model.py:16 `BddModel` — use-consistent-naming — The class is `BddModel`, its node type is `Spec` (:17), and the language of the practice says "spec"; three words for one thing. [4]
- code_spec_model.py:52 `KeptLines`, :38 `ChildBlock = Tuple[int, int, Callable…]` — use-intention-revealing-names — `KeptLines` translates a body written in another language to and from comments; `ChildBlock` is a tuple of first line, last line, and a reader function. Neither name says so. [4]
- spec_source.py:19 `has_signature_marker`, :25 `is_developed`, :37 `reads_like_code` — prefer-class-operations — A file of functions that answer questions about a spec's text; `BddModel.load_source_facts` (`bdd_model.py:59`) calls them and copies the answers onto itself. [3]

### cdd_guidance/practices/agent_bdd/

- agent_bdd_common.py:327 `session.record.save()` — source-parses (runs wrong) — `AgentSession` declares `chat_id`, `session_file`, and `save()` (:294-311) and no `record`; the first time a session file is missing, `from_workspace` raises `AttributeError` after the chat is created, so the chat id is never saved. Only the path that resumes an existing session works. [3]
- agent_bdd_common.py:23 `_YAML = YamlFence()`, agent_cli_bdd.py:275 `CURSOR_AGENT = CursorCli()` — use-explicit-dependencies — Two objects made at import and shared by every caller; `CURSOR_AGENT` is the default of a constructor parameter (:284). [3]
- agent_bdd_common.py:297-301 `AgentSession.__post_init__` — use-explicit-dependencies — Builds two `CursorCli` objects itself although `from_workspace` (:315) is handed one, so the command line a spec passes in is used to create the chat and a different one to run it. [3]
- agent_bdd_common.py:123 `JudgeResult.from_stdout` — put-logic-on-the-owning-resource — Makes a throwaway `JudgeResult(verdict="ERROR", reason="")` to call seven parsing operations (:131-207) that read none of its fields; the parser is a different thing from the result it produces. [3]
- agent_bdd_common.py (682 lines, 14 classes) — high-cohesion — Results, the YAML fence, the chat session, the toolset request, its run, and the deadline share one file named "common"; `agent_cli_bdd.py:46` `_StreamBuckets` (225 lines) is likewise named for its storage, not for reading the agent's event stream. [4]
- agent_block.py:116 import inside `generate_and_judge` — one-way-deps — `spec_helpers` imports only `agent_bdd_common`, so there is no cycle to avoid; the import is hidden for no reason. [1]

### cdd_guidance/practices/tdd/

- tiers.py:38 `is_test_code` — use-consistent-naming — The same name as `clean_engineering/model/production_code.py:89` with a different meaning: here "the file has a code suffix", there "the file is a spec, a test, or test support". [4]
- graph_overlay.py:18 `TEST_FILE_NODES`, rules/__init__.py:22 `node_types_by_practice` — eliminate-duplication — The pairs (BDD, `Spec`) and (Stories, `Story`) are listed twice; adding a practice with test files means editing both. [2]

### cdd_guidance/practices/sketch_document/

- No finding. `SketchOutline` and `DiscoveryDocument` are the one shared reader and writer three practices use, each through its constructor and two or three operations; this is the shape the proposals below aim for elsewhere.

## Fixes that change no design

Each can be made in one pass with the unit specs of the files named. None adds or removes a class or changes an operation another module calls, except where stated.

1. **Fix `session.record.save()`** — `agent_bdd/agent_bdd_common.py:327` → `session.save()`. Callers: none change. Spec: add one example to `agent_bdd_spec.py` that creates a session with no file (a fake `CursorCli`), since no spec takes this path today. Risk: none; the line cannot run as written.
2. **Delete two dead operations** — `clean_engineering/model/diagram/class_layout.py:412-422` `_RouteGrid.is_open_for` and `:436-437` `carries_arrow`. No caller in production or specs. Risk: none.
3. **Delete two dead functions** — `clean_engineering/rules/rule_examples.py:89` `assert_python_example_pair` and `:109` `assert_module_example_pair`. No caller. `python_example_pair` and `module_example_pair` stay (specs call them). Risk: none.
4. **Move two hidden imports to the top** — `clean_engineering/model/operation.py:236` (add `parse_parameter` to the import at :14) and `agent_bdd/agent_block.py:116`. Risk for the second: `spec_helpers` imports `expects`, so `agent_block` then needs `expects` at import; it is already a spec harness, but run `agent_bdd_spec.py` and `agent_block_spec.py`.
5. **Make a static method an instance method** — `ddd/model/drawio/drawio_bounded_context_map.py:52` `name_from_modules_title` → `_names_the_modules_title(self, cell)`; one caller at :48. Risk: none.
6. **Move each single-use module function onto its class** (private, same body):
   - `call_links.py:48` `_language_of` → `ClassesInReach` (caller :107).
   - `code_class_model.py:44` `_without_note` → `CodeCleanEngineeringModel` (caller :270).
   - `diagram/diagram_node.py:62` `_names_in` → `DiagramClass` (callers :97, :100).
   - `drawio/drawio_class_model.py:550` `_folded_classes` → `_ClassDiagramReader` (caller :278).
   - `rules/practice_wide_rules.py:165` `_folders` → `OneWayDeps` (caller :38).
   - `class_stereotypes.py:67` `marked_intent` → `DocComment` (caller :89).
   - `rules/operation_checks.py:123` `operation_line_count` → `KeepOperationsSmall` (caller :148).
   - `operation_metrics.py:162` `names_call_io_and_domain` → `OperationSourceFacts._delegates_io_and_domain` (`source_facts.py:190-194`, its only caller).
   Specs: none name these functions (checked by search). Risk: low.
7. **Type three untyped parameters** — `bdd/model/spec_reshape.py:110` `calls: DescribeCalls`, `:113` `call: DescribeCall` (import under `TYPE_CHECKING`, because `code_spec_model.py` imports `spec_reshape`); `clean_engineering/model/code_class_model.py:268` `member: Operation | Property`. Risk: none.
8. **One constant for the folder node types** — make `folder_facts.py:15` `FOLDER_TYPES` public and use it at `code_read.py:188, 218, 375`, `call_links.py:112`, `rules/practice_wide_rules.py:20, 35`, `rules/coupling_rules.py:97`, `rules/module_graph_rules.py:76`, `rules/module_naming_rules.py:73`. Risk: low; `ddd/model/graph_reading.py:244` would import one more Clean Engineering name, so leave DDD until proposal 7.
9. **One `_DEPENDENCY_LABEL`** — define it once in `diagram/class_view.py` and import it at `drawio/drawio_class_model.py:78` and `whiteboard/whiteboard_class_model.py:76`. Risk: none.
10. **One constructor-name constant in BDD** — `bdd/model/graph_reading.py:32` `_CONSTRUCTORS` → `CONSTRUCTOR_NAMES` from Clean Engineering (BDD already imports five names from it). Risk: `constructors_of` (:210-218) loops over the constant, so its result order follows the tuple; iterate `sorted(CONSTRUCTOR_NAMES)` to keep `__init__` first, and run `graph_reading_spec.py`.
11. **Ask the operation, not the name** — replace `x.name in CONSTRUCTOR_NAMES` with the existing `Operation.is_constructor` where the object is an `Operation` model (`markdown/markdown_class_model.py:793`, `source_facts.py:86`). Where the object is a graph node (`class_graph.py:121`, `class_facts.py:349`, `operation_counts.py:31`) leave it until proposal 4. Risk: none.
12. **Flatten two nested operations** (graph hits, real) — `call_links.py:109` `_imports_of` and `source_facts.py:108` `constructor_fields`: extract the inner loop of each into a private helper. Risk: low.
13. **Rename TDD's `is_test_code`** — `tdd/tiers.py:38` → `is_code_file`; one caller (`tdd/graph_overlay.py:9, 29`). Removes the clash with Clean Engineering's function of the same name. Risk: none.
14. **Two spec-only operations: decide, then delete or wire** — `ddd/model/nodes.py:416` `BoundedContext.context_file` with `ContextFile.naming` (:345), and `clean_engineering/model/code_body.py:166` `CodeBody.from_written`, are called only by specs. The repository's rule is to delete code kept alive by its own spec, but `context_file` reads like a feature not yet connected to the Render action. Needs the owner's word before deleting; no change to callers either way.

## Proposed design changes

Each proposal stands alone. Sizes are estimates from the line counts measured above; none has been prototyped.

### 1. The graph reading leaves `model/` (removes both import cycles)

**Problem.** In both practices the reading of the working copy lives inside the model package and imports one of the model's own format packages, which imports the model back.

- Clean Engineering: `model/graph_reading.py:28` imports `model/markdown/card_lines.py`; `model/markdown/markdown_class_model.py` imports eight files of `model/`.
- DDD: `model/graph_reading.py:31` imports `model/markdown/nodes.py`; `model/markdown/nodes.py:19`, `class_cards.py:15,25`, `replaced_document.py:15` import `model/nodes.py` and `model/stereotypes.py`.

The reading is a client of the model and of its formats; it is not part of the model. In Clean Engineering fourteen files of `model/` exist only for the reading and the rules (`graph_reading`, `code_read`, `call_links`, `compared_facts`, `class_facts`, `class_graph`, `folder_facts`, `operation_facts`, `module_exposure`, `public_routes`, `import_cycles`, `near_copies`, `operation_counts`, `imported_classes`; about 2,300 lines), mixed with the class model that every format adapter and three other practices import.

**Before.**

```
clean_engineering/model/          (one package, 37 files)
  base_class_model, operation, property, …      the class model
  graph_reading, code_read, call_links, *_facts  the reading      ──imports──▶ model/markdown/card_lines
  markdown/  CardLines, MarkdownCleanEngineeringModel             ──imports──▶ model/*
ddd/model/
  nodes, stereotypes                             the domain model
  graph_reading                                  the reading      ──imports──▶ model/markdown/nodes
  markdown/                                                       ──imports──▶ model/nodes, model/stereotypes
```

**After.**

```
clean_engineering/model/                         the class model and its formats only
  markdown/  MarkdownCleanEngineeringModel
clean_engineering/reading/                    + new package (own module card)
  → graph_reading, code_read, call_links, compared_facts, class_facts, class_graph, folder_facts,
    operation_facts, module_exposure, public_routes, import_cycles, near_copies, operation_counts,
    imported_classes                             (moved from model/)
  → card_lines                                   (moved from model/markdown/)
  imports model/ and model/markdown/; nothing in model/ imports reading/
ddd/model/                                       nodes, stereotypes, formats
ddd/reading/graph_reading.py                  → moved from ddd/model/
```

No class changes. Dependencies run `reading → formats → model` in both practices.

**Callers affected.** Clean Engineering: `clean_engineering.py` (one import), the two rule files that import `class_graph` (`rules/limit_operation_parameters.py`, `rules/operation_checks.py`), `bdd/model/graph_reading.py:20`, `bdd/model/graph_bdd_model.py:21`, `ddd/model/graph_reading.py:27,29`, `stories/model/graph_reading.py`, the specs that import the moved files, both module cards and `ooad-model.md`. DDD: `ddd.py`, `graph_reading_spec.py`, the module card.

**Size.** About 16 files moved, 45 to 55 import lines changed, two new module cards. No logic.

**What could go wrong.** The framework finds a practice's rules and reading by package path (`PracticeReading.package`, `rules_in(module_path)` in `harness/guidance/practice_reading.py:42,135`); confirm it reads `reading_type` from the practice class and not a fixed `model.graph_reading` path before moving. The deep-module measure is taken per folder with a module card, so the new `reading` module is measured on its own and may report a wide seam until proposal 4 narrows it.

**Smallest first step, if the whole move is not wanted.** Move only `card_lines.py` from `model/markdown/` to `model/` (two importers), and have DDD's `_DomainDocument` ask the practice for its markdown adapter (`reading.practice.formats.adapter("markdown")`), as Clean Engineering's `ModelDocuments` already does with `practice.model_document_format` (`graph_reading.py:142`). Both graph hits clear; the mixing of reading and model stays.

### 2. One reader and writer of the class-card notation

**Problem.** The notation for a class's members (`------`, `----`, `+ name(args): Type`, `-> callee`, `// note`, `<< kind >>`) is read and written by two practices in two shapes, and the sketch notation by two more:

| What | Clean Engineering | DDD |
|---|---|---|
| Card body, read and write | `MarkdownOoadClass` `markdown_class_model.py:138-169, 213-355` (about 175 lines) | `ClassCard`, `_CardBody` `class_cards.py:148-229, 233-265`, patterns `:424-425` (about 115 lines) |
| Sketch fence, read | `SketchOoadClass.read_member`, `read_uml_member` `sketch_class_model.py:111-190` (about 80 lines) | `_SketchFence` `class_cards.py:268-371` (104 lines) |
| Member line → model | `Operation.from_signature`, `Property.from_signature` | own regexes, `_add_operation` `:213-220`, `_add_property` `:222-229` |

They already differ: DDD writes `<< kind >> name: Type` with `access` from `+`/`-`; Clean Engineering prefixes a private operation's name with `_`; DDD keeps one description per member, Clean Engineering keeps invariants and notes. A card written by one practice and read by the other loses whichever the reader does not know.

**Before.**

```
MarkdownOoadClass(OoadClass)            ClassCard(MarkdownDomainNode)          _SketchFence
  read_body(body)                         add_member(line, as_operation)         read() → [ClassCard]
  _read_properties / _read_operations     lines()                                _read_line, _add_sketch_member
  _member_lines / _property_line          _property_lines / _operation_lines   SketchOoadClass(OoadClass)
  _note_on_property / _note_on_operation  _add_operation / _add_property         read_member, read_uml_member
                                        _CardBody.read(line)
MarkdownClass, MarkdownEntity, MarkdownValueObject, MarkdownRepository, MarkdownDomainService,
MarkdownSpecification, MarkdownFactory   (each = ClassCard + one domain class)
```

**After.**

```
clean_engineering/model/markdown/class_card.py
  ClassCard                                     + one object for a card's text
    + ClassCard(heading: ClassHeading, body_lines)
    + read_into(oclass: OoadClass)                 (properties, operations, callees, notes, invariants, arrows)
    + lines_of(oclass: OoadClass) → list[str]
  SketchFence                                   + one object for a sketch fence's lines
    + read_into(oclass: OoadClass)

MarkdownOoadClass(OoadClass)
  ~ read_body → asks ClassCard.read_into(self)
  ~ render    → asks ClassCard.lines_of(self)
  - _read_properties, _read_operations, _member_lines, _property_line, _note_on_property, _note_on_operation, …

ddd ClassCard                                   - removed (→ clean_engineering ClassCard)
ddd _CardBody, _SketchFence                     - removed
ddd MarkdownEntity(Entity) …                    ~ plain subclasses of the domain classes; card reading is asked
                                                  of ClassCard with the stereotypes DDD adds (root first, repository
                                                  drawn in its root) passed as the heading
```

DDD keeps what is its own: stereotype order (`ordered_stereotypes`), the repository drawn inside its root (`_REPOSITORY_IN_ROOT`), `**Invariants**` bullets. Those become a small DDD subclass or options of `ClassCard`.

**Callers affected.** `ddd/model/markdown/nodes.py` (`MarkdownAggregate` uses `ClassCard.read`, `from_code`, `from_sketch`, `lines`, `sketch_lines`), `ddd/model/markdown/replaced_document.py`, `ddd/model/sketch/sketch_ddd_model.py`, `clean_engineering/model/sketch/sketch_class_model.py`, and the specs `class_cards_spec.py`, `markdown_class_model_round_trip_spec.py`, `format_round_trip_spec.py`, `sketch_class_model_round_trip_spec.py`.

**Size.** 6 production files, about 220 lines removed from DDD and 80 from the Clean Engineering sketch, about 150 added for the shared class. Net about 150 fewer lines.

**What could go wrong.** The two readers accept slightly different text today; unifying them changes what some existing domain models parse to. The round-trip specs in both practices are the guard; expect a handful to need a decision on which behaviour is right (private-name prefix, where a `//` note is kept). The DDD module card says the model document is DDD's own format; this proposal keeps the format and shares only the member notation.

### 3. One resolver from a call in source to the member it means

**Problem.** Three practices each work out which graph member a name in a piece of code refers to:

| Practice | Classes | Lines |
|---|---|---|
| Clean Engineering | `ClassesInReach`, `CallerBody` (`call_links.py:54-117, 210-340`); `ImportedClasses` (`imported_classes.py:17-62`) | about 240 |
| BDD | `ImportedCode`, `ReachedMembers` (`graph_reading.py:174-283`); `reach_of` and nine patterns (`nodes.py:22-82`) | about 155 |
| Stories (read for comparison) | `ImportedFiles`, `StoryLinks` (`graph_reading.py:299-513`) | about 215 |

All three start from the same inputs (the file's imports as `ClassReference`s, a receiver's class, a member name) and all three reach into Clean Engineering's reading to do it: `clean.code_index.members_named(name)` then filter by `get_fact("owner")`, by file, by language. The rules differ. Clean Engineering types a receiver from parameters, locals, and fields; BDD allows a name when at most two classes declare it (`graph_reading.py:274`); Stories has its own. So the edges `invokes` drawn from an operation, an observation, and a step to the same call can point at different members, and a fix to import resolution (re-exports, the `@cdd/` adapter alias in `script_imports.py:31`) has to be made up to three times.

**Before.**

```
GraphReading (CE)
  code_index: CodeIndex            classes_named(name), members_named(name), class_names()
ClassesInReach(reading)            class_named(name, file), function_named(name, file), only_member_named(name, file, whole)
CallerBody(reading, reach, caller) called() → [Node]
ImportedClasses(classes, refs)     resolve(reference, importer)

BDD:      ImportedCode(clean, classes, spec)  members_named, tool_operations, constructors_of, class_described_by
          ReachedMembers(imported, reach, builds).invoked
          reach_of(text) → Reach (dict)
Stories:  ImportedFiles, StoryLinks
```

**After.**

```
GraphReading (CE)
  code_index: CodeIndex
    + file(relative) → CodeFile                     the one seam other practices ask
CodeFile                                         + (replaces ClassesInReach + ImportedClasses)
    + class_named(name) → Node | None                 own declaration, then import (re-exports followed), then same folder
    + function_named(name) → Node | None
    + members_called_in(source: CodeSpan) → [Node]    what CallerBody.called() does, for any span of this file's code
    + constructors_of(class_name) → [Node]
CodeSpan                                         + a piece of code with the receivers it names
    (text, owner class or none, known locals)        (→ takes over BDD's reach_of and CE's _name_locals)

ClassesInReach, ImportedClasses                  - removed (→ CodeFile)
CallerBody                                       ~ becomes CodeFile.members_called_in for an operation's own span
BDD ImportedCode, ReachedMembers, Reach          - removed; ObservationLinks asks clean.code_index.file(spec file)
                                                   .members_called_in(observation span)
BDD tool_operations (toolset.operation strings)  stays in BDD: only specs name tools that way
Stories StoryLinks                               ~ asks the same seam (outside this judgment's area)
```

**Callers affected.** `clean_engineering/model/call_links.py`, `imported_classes.py`, `module_exposure.py` (`ClassNamers`), `code_read.py` (`ClassNodes.link_types`), `bdd/model/graph_reading.py`, `bdd/model/nodes.py`, `bdd/model/graph_bdd_model.py`, later `stories/model/graph_reading.py`; specs `graph_reading_spec.py` in all three practices, `graph_bookshop_spec.py`, `module_exposure_spec.py`.

**Size.** 7 to 9 production files; about 400 lines removed across CE and BDD, about 250 added. Stories would remove about 150 more when it follows.

**What could go wrong.** This is the riskiest proposal. The three sets of rules were tuned separately against real code (the `whole` flag at `call_links.py:87-99`, BDD's "at most two owners" at `graph_reading.py:274`, setup reach merged before own reach at `:144-154`), and their specs pin today's edges. One resolver will change some edges in at least one practice; each changed edge needs a decision on which answer is right. It should be done as Flow A in the TDD supplement's terms: compare the `invokes` edges of the whole repository's graph before and after, and review every difference, before the unit specs are rewritten. Do Clean Engineering and BDD first; leave Stories until those have held.

### 4. A class in code answers for itself; rule measures stop being three shapes

**Problem.** Inside `clean_engineering/model` the same class or operation exists in three shapes, and the code that reasons about one is not on any of them.

- The parsed model object (`OoadClass`, `Operation`), which also carries the measures as flat fields set by `setattr` from `ClassSourceFacts` and `OperationSourceFacts`.
- The graph node, read with `get_fact("held_fields")`, `get_fact("bases")`, `get_fact("body_text")`, `get_fact("owner")`: 86 string keys in the area.
- The `operation_shapes` dicts on each class (`source_facts.py:90,131-137`), read by `class_graph.py:118-123`, `operation_counts.py:29-39`, `rules/class_rules.py:23`.

`ClassGraph` then offers `fields(node)`, `bases_of(node)`, `operations(node)`, `has_behavior(node)`, `is_production(node)`, `is_mixin(node)`, and eleven recorder classes loop over nodes and write more string-keyed facts for the rules to read back. `SourceText` and `PythonFunctionBody` are two more shapes of "an operation body that can be measured".

**Before.**

```
ClassGraph(reading)
  classes: list[Node]
  fields(node) bases_of(node) operations(node) has_behavior(node) is_production(node) is_mixin(node)
  named(type_name) classes_defining(operation_name) kinds: ClassKinds
ResourceShapes(classes).record()         → fact data_bags_taken
ParallelModels(classes).record()         → facts copied_fields, copied_references
Forwarding(in_graph, classes).record()   → facts forwards_to, forwards_to_module
DomainExtensions, BuiltCollaborators, BodyCopies, FailureMessages, ImportCycleFacts, SiblingFanOut, ModuleExposure
ComparedFacts(reading).record()          runs the ten above
operation_count(node) → OperationCount   reads operation_shapes dicts
ClassSourceFacts.load()                  setattr(oclass, name, fact) for a dict of facts
SourceText(text)  /  PythonFunctionBody(node, owner)      same measures, two classes
```

**After.**

```
ProductionClasses(reading)                    ~ renamed from ClassGraph
  + __iter__ → ProductionClass
  named(type_name) → [ProductionClass]
  defining(operation_name) → {ProductionClass}
ProductionClass                               + one object per class node, made once by ProductionClasses
  node: Node
  + fields: dict[str, str]        → from ClassGraph.fields(node)
  + bases: list[str]              → from ClassGraph.bases_of(node); the one place a base's name is parsed
                                    (removes call_links.py:135, :339 and class_facts.py:118 spellings)
  + operations: list[Node]        → from ClassGraph.operations(node)
  + has_behavior, is_mixin, is_value, is_failure   → from ClassGraph and ClassKinds
  + operation_count: OperationCount               → from operation_counts.operation_count(node)
  + folder: Node                                   → replaces Forwarding._folder_id and the folder lookups
- operation_shapes dicts                       (ProductionClass reads its member nodes instead; see risk)
ClassKinds                                    - removed (→ ProductionClass.is_value / is_failure)

Recorders keep their work but each is named for what it finds and shares one base:
ComparedFact(classes: ProductionClasses)      + base with record(); holds in_graph through classes
  ServicesTakingDataBags   ~ was ResourceShapes
  CopiedModels             ~ was ParallelModels
  PassThroughClasses       ~ was Forwarding
  DomainExtensions, BuiltCollaborators, BodyCopies, FailureMessages, ImportCycles→FolderImportCycles, SiblingFanOut, ModuleExposure
ComparedFacts                                 ~ stays the list of them

MeasuredBody (Protocol)                       + control_flow_depth(), unnamed_numbers(), reaches_peer_private(…),
                                                built(…), catches_everything(), swallows()
  SourceText, PythonFunctionBody              ~ both declare it; PythonOperation.measure and OperationSourceFacts
                                                ask one interface
ClassSourceFacts.load / OperationSourceFacts.load
  ~ assign declared fields; - setattr by name (base_class_model.py:468, source_facts.py:80, :169)
OoadClass.__init__                            + declares method_count, property_names, constructs, prose_comment,
                                                prototype_swap (today created by setattr)
```

This does not remove the string-keyed facts between recorder and rule: the framework saves facts on nodes so a graph read back from JSON can run rules without the source, and that is outside this area to change. It removes the logic that sits beside the object it is about, the duplicated base-name parsing, and the hidden attributes.

**Callers affected.** `class_facts.py`, `operation_facts.py`, `folder_facts.py`, `module_exposure.py`, `compared_facts.py`, `class_graph.py`, `operation_counts.py`, `source_facts.py`, `base_class_model.py`, `operation_metrics.py`, `python/python_class_model.py`, the rules that import `class_graph` (`limit_operation_parameters.py`, `operation_checks.py`), `bdd/model/graph_bdd_model.py:21` (`parameters_of`), and the specs `module_exposure_spec.py`, `compared_facts_spec.py`, `operation_metrics_spec.py`, `ce_rules_spec.py`, `coupling_rules_spec.py`.

**Size.** 12 to 14 production files, about 350 lines changed, net roughly even. Can be done in three passes: `ProductionClass`; recorder base and names; declared fields and `MeasuredBody`.

**What could go wrong.** `operation_shapes` cannot simply go: it lists getters, which the graph holds as `Property` nodes, not `Operation` nodes (`code_read.py:251-253`), so `has_behavior` and the operation counts would change unless `ProductionClass` reads both kinds of member. If that turns out awkward, keep the fact and give it a typed shape (`OperationShape` named tuple) instead of dicts. The guardrails warn that moving behaviour onto an owner makes the owner grow; `ProductionClass` must stay a view of one node and not collect the recorders' logic. Run the metrics gate on each pass.

### 5. One draw.io page and one rectangle in the framework

**Problem.** Reading and writing a draw.io file, and keeping the places a person gave its cells, is written in each practice that draws:

| Work | Clean Engineering | Stories | UX | Elsewhere |
|---|---|---|---|---|
| Read pages and cells | `DrawioPage` `drawio_page.py:20-136` | `nodes.py:459-523` | `nodes.py:368-401` | `harness/catalog_generator/drawio_diagram.py`, `actions/render/kept_document.py` |
| Write the page skeleton | `drawio_class_model.py:438-445, 515-524` | `_DrawIOPage` `nodes.py:250-278` | own | |
| Keep earlier positions | `DrawioPage.positions`, `edges_by_ends` `:62-77` | `_KeptPlaces`, `_drawn_geometries` `:281-322` | | `KeptDocument._drawio` |
| Cell style values | `style_value`, `style_number` `:206-217` | | `CellStyle` `nodes.py:90-117` | |
| A rectangle | `Geometry(x, y, width, height)` `geometry.py:11` | `Vertex.x/y/width/height` | | `harness/whiteboard` `Box(x, y, w, h)` |

About 200 to 250 lines do the same job three to five times. The whiteboard format does not have this problem: `harness/whiteboard` owns `Whiteboard`, `BoardElement`, `Box`, and `keep_places`, and each practice subclasses `WhiteboardNode`.

**Before.**

```
CE:      DrawioPage(file_path, name, root)   pages_in, whole, cell, positions, edges_by_ends, kind_of, segments
         + 12 module functions over ET.Element and style strings
         Geometry(x, y, width, height)       overlaps, shifted, moved_to, clear_gap_to, center
Stories: _DrawIOPage(name, page_id) add(vertex) text();  _KeptPlaces.from_text(drawio) place(vertex)
UX:      CellStyle;  own ET walk
harness: whiteboard.Box(x, y, w, h) holds(other)
```

**After.**

```
harness/drawio/                              + new framework module, mirroring harness/whiteboard
  Drawing                                    + a draw.io file
    + from_text(text) → Drawing                 (raises UnreadableDrawing)
    + pages: list[Page]
    + add_page(name, page_id) → Page             (writes the skeleton once)
    + keep_places(previous: Drawing | None)      (same contract as Whiteboard.keep_places)
    + save() → str
  Page                                       → from CE DrawioPage
    cells, vertices, edges, cell(id), positions()
    + add(cell: Cell)
  Cell                                       + one vertex or arrow
    id, label, style: CellStyle, box: Box | None, source, target
    + is_inheritance, anchor_fractions(end), segments()   → from the module functions in drawio_page.py
  CellStyle                                  → from UX; value(key), number(key)
harness (shared)  Box                        ~ one rectangle: gains overlaps, shifted, moved_to, clear_gap_to, center
CE Geometry                                  - removed (→ Box)
CE DrawioPage and its 12 functions           - removed (→ Page, Cell); CE keeps class_title_in / class_name_in,
                                               which read a class card's HTML and are its own
Stories _DrawIOPage, _KeptPlaces             - removed (→ Drawing, keep_places)
```

**Callers affected.** In this area: `drawio/page/drawio_page.py`, `drawio/drawio_class_model.py`, `drawio/diagram_node.py`, all ten scanners, `diagram/geometry.py` and its users (`class_layout.py`, `class_view.py`, `diagram_node.py`, `module_layout.py`, `whiteboard_class_model.py`), `ddd/model/drawio/`. Outside it: Stories and UX drawio nodes, `kept_document.py`, `drawio_diagram.py`, and their specs.

**Size.** About 25 files across the repository; about 300 lines added in `harness/drawio`, about 450 removed. In this area alone: 18 files, mostly import and type-name changes.

**What could go wrong.** `Geometry` is a `NamedTuple` used positionally in places (`b[0] + b[2]` at `drawio_class_model.py:328-329`) and `Box` is a frozen dataclass with `w`/`h`; the rename touches the layout code, which is the most intricate in the area (`class_layout.py`, 927 lines), so it must be a mechanical pass with the layout specs and the heavy render spec run. Stories names its cells differently from Clean Engineering (a linked cell sits inside a `UserObject`); `Cell` has to cover both. Worth doing in two steps: the framework module with Clean Engineering moved onto it, then Stories and UX.

### 6. One way to give a rendered model back the words the file held

**Problem.** When a model is rendered onto a file that is already there, what only the file held must stay. The area does this in three places with three mechanisms, beside the two the Render action has (`KeptDocument`, `ReshapedCode`):

- `UnwrittenProse` (`clean_engineering/model/markdown/markdown_class_model.py:757-802`): clones every class before translation, then copies intent, callees, invariants, and description back by member name.
- `ReplacedDocument`, `_ReplacedAggregate`, `_ReplacedCard` (`ddd/model/markdown/replaced_document.py`, 166 lines): walks contexts, aggregates, and cards by name and copies `x = x or was.x` field by field; `_ReplacedCard.give_its_words` and `_give_operation` (:130-156) do to `Operation` and `Property` what `UnwrittenProse._give_back_to_member` does.
- `SpecReshape` (`bdd/model/spec_reshape.py`, 176 lines), beside Stories' `ReshapedStoryFile` (168 lines) and UX's `ReshapedView` (283 lines), each defining `NO_LONGER_IN_MODEL` again.

The first two are the same idea (match by name, keep the earlier words where the new one has none) written on the outside of the objects that own the words.

**Before.**

```
UnwrittenProse(model)            give_back()            reads oclass.intent, member.callees, .invariants, .description
ReplacedDocument(replaced, read) give_its_words()       reads context.notes, .module_notes, aggregate.description, …
  _ReplacedAggregate, _ReplacedCard                     reads card.invariants, prop.description, operation.callees
```

**After.**

```
OoadNode
  + take_words_from(earlier: OoadNode)        each node keeps what it has and takes what it lacks
OoadClass.take_words_from                     + intent; then each member by name (constructor matched as today)
Operation.take_words_from / Property.take_words_from
                                              + description, callees, invariants
Module.take_words_from                        + language, constraint, description cut short by a drawing
DDD: BoundedContext / Aggregate .take_words_from
                                              + notes, group, consumed events, integrations (ReplacedDocument's rules)
UnwrittenProse                                - removed (→ model.take_words_from(earlier model))
_ReplacedCard                                 - removed (→ OoadClass.take_words_from plus DDD's invariants)
ReplacedDocument, _ReplacedAggregate          ~ shrink to the integration matching only (same_target, draws_no_arrow)
NO_LONGER_IN_MODEL                            ~ one definition beside Reshaped in harness/guidance/practice_formats.py;
                                                the five copies import it
```

The code side (`SpecReshape` against `ReshapedCode` and Stories' and UX's reshapers) is left out of this proposal: `cdd_guidance/actions/render/reshaped_code.py` was not read closely enough here to say how much of `SpecReshape` it could take over. That comparison is worth a separate judgment.

**Callers affected.** `markdown_class_model.py` (`MarkdownCleanEngineeringModel.render` :743-748), `base_class_model.py`, `operation.py`, `property.py`, `ddd/model/markdown/replaced_document.py`, `ddd/model/markdown/nodes.py:712`; the five files that define the constant; specs `markdown_class_model_round_trip_spec.py`, `class_model_trip_spec.py`, `format_round_trip_spec.py`.

**Size.** 8 production files; about 110 lines removed, about 70 added.

**What could go wrong.** `UnwrittenProse` clones before `translate_from` because translation overwrites the objects in place; `take_words_from` needs the earlier model kept the same way, so the clone stays (it moves into `render`). DDD's rules are subtler than "keep what is missing" for integrations and events, which is why those stay in `ReplacedDocument`. Requires proposal 7's step of putting the DDD word fields on the base classes.

### 7. Seams between the practices: a source-code module, a class-model seam, and DDD's words on its own model

**Problem.** Three separate boundary faults with one cause: code that several modules need is an internal file of one practice.

- **Source text in a language.** `CodeLanguage`, `CodeBody`, `WrittenBlock`, `BraceCall`, `InsideLines` (`code_body.py`), `BracketStructure`, `CallGraph`, `SourceText` (`operation_metrics.py:169`), `ScriptImports` and `ClassReference` (`script_imports.py`), and the test-file convention (`production_code.py`) are imported from `clean_engineering/model/…` by Stories (14 files), BDD (7 files), two pattern packages, and `space/session` (2 files). None is about the Clean Engineering class model.
- **The class model has no seam.** `clean_engineering/model/__init__.py` is one line. DDD imports 13 internal files, BDD 10.
- **DDD's formats depend on one another.** The drawn map and the sketch build `MarkdownBoundedContext` and `MarkdownIntegration` (`drawn/drawn_map.py:13,84`, `sketch/sketch_ddd_model.py:10,41`) because the fields every format must carry (`notes`, `module_notes`, `group_notes`, `description`, `group`, `consumed_events`) and the sketch reading live on the markdown subclasses (`markdown/nodes.py:155-173, 480-485, 533-575`).

**Before.**

```
clean_engineering/model/   code_body, bracket_structure, call_graph, script_imports, production_code,
                           operation_metrics(SourceText), base_class_model, operation, property, field_types, …
                           __init__.py  (empty)
stories, bdd, ddd, patterns, space/session  ──import internal files──▶ clean_engineering/model/*
ddd/model/drawn, ddd/model/sketch           ──import──▶ ddd/model/markdown/nodes
```

**After.**

```
cdd_guidance/practices/source_code/          + new shared module beside sketch_document (same standing: not a practice)
  → code_body.py        CodeLanguage, CodeSpelling, CodeBody, BraceCall, WrittenBlock, InsideLines, PYTHON, TYPESCRIPT, JAVASCRIPT
  → bracket_structure.py, call_graph.py
  → script_imports.py   ScriptImports, ClassReference
  → source_text.py      SourceText, SpanFailures, SpanCollaborators   (split out of operation_metrics.py)
  → test_files.py       TestFileName, is_spec_file, is_test_code, is_example_code   (was production_code.py)
  module card: seam = the names above; depends on nothing in practices

clean_engineering/model/__init__.py          ~ the class-model seam, exported by name:
  CleanEngineeringModel, Module, OoadClass, Operation, Parameter, Property, Invariant, Relationship,
  CONSTRUCTOR_NAMES, MODULE_FUNCTION_HOLDER, marks_in, without_marks, module_path_in
  ddd, bdd import from here, not from base_class_model / operation / property / field_types / class_stereotypes

ddd/model/nodes.py
  BoundedContext   + notes, module_name, module_notes, group_notes     → from MarkdownBoundedContext
  Aggregate        + description, group, consumed_events, integrations  → from MarkdownAggregate (those not already on the base)
ddd/model/sketch/                             → takes the sketch reading (take_sketch_line, load_sketch, sketch_lines,
                                                read_sketch_lines, SKETCH_* constants) out of markdown/nodes.py
ddd/model/drawn/drawn_map.py                  ~ bounded_context_type = BoundedContext; no markdown import
```

`harness/` is not the place for the source-code module unless the owner wants it there: it holds no knowledge of the framework, and the precedent for a module several practices share is `sketch_document`.

**Callers affected.** About 45 import lines in Stories, BDD, DDD, the two pattern packages, `space/session/practice_session_output.py`, `space/session/proposed_roots.py`, `space/session/session_file.py`; inside Clean Engineering about 30 import lines; specs that import the moved files (`compared_facts_spec`, `c_family_parse_spec`, `operation_metrics_spec`, `script_imports_spec`, `spec_files_spec`). DDD part: `markdown/nodes.py`, `sketch/sketch_ddd_model.py`, `drawn/drawn_map.py`, `replaced_document.py`, and their specs.

**Size.** Source-code module: 6 files moved, one split, about 75 import lines, one module card. Class-model seam: one `__init__.py`, about 40 import lines. DDD fields and sketch reading: 4 files, about 250 lines moved between them. Three independent passes.

**What could go wrong.** Clean Engineering's own model depends on `code_body` (operations hold a `CodeBody`), so `clean_engineering/model` gains a dependency on `source_code`; that is one-way and correct, but the deep-module and low-coupling measures for both modules will change and should be read after the move. Exporting names from `model/__init__.py` makes importing the package load the whole class model; check import time and that it adds no cycle with `clean_engineering.py`. Moving the sketch reading out of the 778-line `markdown/nodes.py` is the part most likely to break round trips, because that file was read here in outline and by ranges, not line by line; a closer read should come before the pass.

## Graph hits judged noise

Hits in the area from `clean-engineering-code-20261121T212842.md`. Hits not listed here were confirmed and appear above (findings or fixes).

| File:line | Rule | Why it is noise |
|---|---|---|
| clean_engineering/model/.context/ooad-model.md:418, :732, :745, :831 (`Relationship`, `CodeSpelling`, `CodeLanguage`, `CallGraphEntry` "copy the fields of" themselves) | do-not-invent-parallel-object-models | The model document describes the class the code declares; the graph reads both as classes and reports the description as a copy of the code. One class, two readings. |
| clean_engineering/model/diagram/geometry.py:11 (`Geometry` copies the fields of `Geometry`) | do-not-invent-parallel-object-models | Same cause: the other `Geometry` is its description in `ooad-model.md`. (The real duplicate is `harness.whiteboard.Box`, which the hit does not name; see finding and proposal 5.) |
| ddd/model/.context/ddd-model.md:331 (`MarkdownBoundedContext` copies `group_notes`, `module_notes`, `notes`) | do-not-invent-parallel-object-models | A document describing the code class. The fields do sit on the wrong class (proposal 7), but not for the reason the hit gives. |
| clean_engineering/model/imported_classes.py:27 (`resolve` reaches into a collaborator's private state) | hide-inner-details | The line is `reference._replace(name=name)`; `_replace` is the public operation of a `NamedTuple`, named with an underscore by Python. |
| clean_engineering/model/markdown/markdown_class_model.py:358 (`MarkdownModule` holds `_card_name`, a name copy) | do-not-invent-parallel-object-models | `_card_name` (:380) is the name the module had when its card was read, compared at :491 to see whether the module was renamed since; it is a remembered earlier value, not a copy of another object's name. |
| clean_engineering/model/.context/ooad-model.md:1081, :1090, :1091 and drawio/.context/drawio-model.md:47 (parameters `x`, `y`, `dx`, `dy`, `value`) | use-intention-revealing-names | Hits on documents, which are outside this judgment; `x` and `y` on a geometry are the names the domain uses. |
| clean_engineering/model/.context/ooad-model.md:422, :660, :736, :749, :1081, :1097, :1129 (constructors over three parameters) | limit-operation-parameters | Document hits; each is the constructor of a value (`Relationship`, `ClassHeading`, `CodeSpelling`, `CodeLanguage`, `Geometry`, `DiagramArrow`), which the rule exempts as creation. |
| clean_engineering/model/.context/ooad-model.md:687, :695, :707, :713, :719 (`record` needs a domain type) | use-typed-signatures | Document hits on the JSON adapter's `from_record(record: JsonRecord)`: a JSON record is the external contract the adapter exists to read. |
| ddd/model/nodes.py:290 (`ContextMapping.__init__` takes 4 parameters) | limit-operation-parameters | A constructor; creation is exempt. |
| bdd/model/spec_reshape.py:36 (`SpecBlock.__init__` takes 6 parameters) | limit-operation-parameters | A constructor of a value made in two places; creation is exempt. (The class itself is questioned in the findings for another reason.) |
| bdd/model/graph_reading.py:108 (`ObservationLinks` constructs `ImportedClasses` in its constructor) | use-explicit-dependencies | `ImportedClasses` here is an index of class nodes built once from what the object already holds; the rule exempts a part "the class builds once from nothing outside itself and keeps". (Its being a third resolver is the real issue; proposal 3.) |
| cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py:79 | eliminate-duplication | Outside the area, and the OSS portal pattern is left out of Clean Engineering judging. |
| clean_engineering/model/.context/ooad-model.md:304, :435 and drawio/.context/drawio-model.md:140 (`SourceText`, `ModuleContext`, `DrawioScanner` expose 10 public operations) | keep-classes-single-responsibility | Document hits, one over a budget of "about nine". `DrawioScanner` does have more than one job (finding above), which a count of ten does not show; `SourceText` and `ModuleContext` at ten operations of one kind are not a design fault. |

Confirmed real and handled above: the two circular-import hits per practice (proposal 1); `ClassLinks` copies the fields of `ClassNodes` and the four "`__init__` duplicates the body of `__init__`" hits (`class_facts.py:278, :325`, `module_exposure.py:99`, `operation_facts.py:81`; proposal 4); `PythonImports` copies `ScriptImportClauses` (finding); the static method at `ddd/model/drawio/drawio_bounded_context_map.py:52` (fix 5); the two nesting hits (fix 12); the five "module function used from one class" hits (fix 6); the three missing type annotations (fix 7); `operation_counts.py:35` `shape: dict` (proposal 4); `MarkdownAggregate` exposes 10 public operations (finding); the parameter-count hits in `ddd/model/graph_reading.py:512, :551, :629, :703, :745` (finding on the two DDD doers), `diagram/diagram_node.py:90`, `whiteboard/whiteboard_class_model.py:514`, `rules/operation_checks.py:359`, and `bdd/model/spec_reshape.py:62, :161` (finding on `SpecReshape`).
