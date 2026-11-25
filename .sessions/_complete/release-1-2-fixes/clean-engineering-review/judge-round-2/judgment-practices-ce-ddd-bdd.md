# Design judgment, round 2: Clean Engineering, DDD, BDD, agent BDD, TDD, source code

Area: practices-ce-ddd-bdd. Judged: the 153 production files of `cdd_guidance/practices/{clean_engineering, ddd, bdd, agent_bdd, tdd, source_code}` changed since 2026-11-21 (base `66f410de3`), at `5d16245ff` on release-1-2-fixes: practice classes, `model/` packages with their format adapters, Clean Engineering's `reading/` and `measures/`, graph readings, `rules/`, templates. Stories and UX were read for comparison only.

Read: every listed file in full at its current content, the whole file and not only the changed lines, in five parts (Clean Engineering model core; its diagram, draw.io, markdown, whiteboard and sketch adapters; its reading and measures; its rules with the practice class, `source_code` and TDD; DDD, BDD and agent BDD), each against the module cards and models in the modules' `.context/`.

Method: as round 1. Every "unused", "used in one place" or "only used inside" claim was checked with a repository-wide search, specs included. A round-1 finding matched here (same class or code, same rule, same problem, also where the file has since moved, such as `clean_engineering/model/graph_reading.py` to `clean_engineering/reading/graph_reading.py`, or `production_code.py`, `script_imports.py`, `code_body.py` to `practices/source_code/`) is marked "(still open from round 1)". The frozen-dataclass crash in `agent_bdd_common.py:182` was confirmed against the code (`JudgeResult` is `@dataclass(frozen=True)` at :108). `oss_portal_domain_driven` was left out.

Theme tags: [1] module boundaries, [2] the same work in different shapes, [3] resource orientation, [4] domain orientation.

## Counts

- Files read: 153 (52 with no findings).
- Findings: 274.
- Findings still open from round 1: 89.
- Design proposals: 30.

| Rule | Findings |
|---|---|
| eliminate-duplication | 106 |
| prefer-class-operations | 22 |
| put-logic-on-the-owning-resource | 21 |
| hide-inner-details | 15 |
| hold-state-on-the-object-not-in-parameters | 13 |
| use-intention-revealing-names | 13 |
| low-coupling | 8 |
| use-consistent-naming | 8 |
| use-typed-signatures | 8 |
| delete-unused-operations | 7 |
| keep-classes-single-responsibility | 7 |
| prefer-instance-operations | 7 |
| use-explicit-dependencies | 7 |
| shape-classes-around-resources | 6 |
| do-not-invent-parallel-object-models | 4 |
| high-cohesion | 4 |
| one-way-deps | 4 |
| limit-comments | 2 |
| no-legacy-api-after-refactor | 2 |
| refuse-unreadable-input | 2 |
| abstraction-focus | 1 |
| errors-out-of-existence | 1 |
| keep-operations-single-responsibility | 1 |
| limit-class-methods | 1 |
| limit-module-file-lines | 1 |
| provide-meaningful-context | 1 |
| public-seam-only | 1 |
| simplify-control-flow | 1 |

## Findings

### cdd_guidance/practices/clean_engineering/model/base_class_model.py

- base_class_model.py:29 `MODULE_FUNCTION_HOLDER` — use-intention-revealing-names — A module function is still modelled as an operation of a class named `"_module"`, and the name is now compared or imported in 18 production and spec files (45 occurrences), among them `measures/checked_measures.py`, `measures/code_measures.py`, `reading/code_file.py`, `reading/graph_reading.py`, `reading/statement_links.py`, `rules/code_use.py`, `stories/model/graph_reading.py`; it is now exported from `model/__init__.py:5`, so the pseudo-class is part of the seam. The domain has module functions; the model has none. [4] (still open from round 1)
- base_class_model.py:37-92 — prefer-class-operations — Seven module functions about names (`path_parent`, `is_interface_name`, `interface_name_for`, `production_name_for`, `example_extension_kind`, `base_type_name_for`, `companion_interface_name`) above the classes they serve; `interface_name_for` and `production_name_for` are still called only inside this file (:51, :56, :73, :84, :89). "Is this class a contract" is asked of a name at `markdown/class_card.py:174`, `python/python_class_model.py:433`, `typescript/typescript_class_model.py:72`, `reading/class_facts.py:60`, while only `CodeClass.is_contract` (`code_class_model.py:194`) answers it as an object, and `OoadClass` has no such property. [3] (still open from round 1)
- base_class_model.py:95 `OoadClass` — use-intention-revealing-names — An abbreviation (object-oriented analysis and design) on the central class of the practice, whose own rules say "do not abbreviate"; it is in the seam (`model/__init__.py:5`) and is the node type in saved graphs, so recorded, not proposed for change. [4] (still open from round 1)
- base_class_model.py:133 `module_helpers: List[list]` — use-typed-signatures — A graph fact holding untyped `[function name, line]` pairs (filled at `python/python_class_model.py:225`, unpacked by position at `rules/prefer_class_operations.py:25`); the shape is known only by reading both ends. [3]
- base_class_model.py:499-509 `ModuleSourceFacts.load_folder`, `take_public_sources` — hide-inner-details — Round 1's `setattr` copy is gone from `ClassSourceFacts` and `OperationSourceFacts`, but the module still gains ten attributes by `setattr(self._module, name, fact)` (:501-502) from the keys of `module_context_files.py:137-148`, and `take_public_sources` sets `public_source_files` and `public_source_internal` (:508-509); none is declared in `Module.__init__` (:344-357), only named as strings in `Module.graph_facts` (:327-342). A misspelt key makes a new attribute and nothing fails. [3] (still open from round 1)
- base_class_model.py:489 `ModuleSourceFacts.load(file, root)` — hold-state-on-the-object-not-in-parameters — The module never keeps the file it was read from, so the same `(file, root)` pair is handed down three layers: `load` (called at `reading/code_read.py:127`) → `Module.import_targets(file, root)` (:457, overridden at `python/python_class_model.py:241`) → `ScriptImports(...).targets(file, root)` (:460) and `.class_references(file, root)` (:494). [3]
- base_class_model.py:520 `CleanEngineeringModel.__init__(name: str | Graph)` — use-typed-signatures — The first parameter is still a name or a graph, sorted out with `isinstance` (:521-524). [3] (still open from round 1)

### cdd_guidance/practices/clean_engineering/model/c_family_parse.py

- c_family_parse.py:86 `CFamilyParse` — limit-class-methods — 42 methods (`parse` through `_top_level`), past the limit of 30; `BraceCleanEngineeringModel` (`code_class_model.py:472`) then adds every method of `CodeCleanEngineeringModel` and `CleanEngineeringModel` to the same object. [3]
- c_family_parse.py:86, :100-108, :131 `CFamilyParse` — keep-classes-single-responsibility — The class model is also its own parser and the parser's cursor: `parse` stores `_text`, `_class_heads`, `_file_module` on the model, and `_append_classes` rewrites `_class_body` and `_body_start` for each class (:131) as undeclared fields; `PythonCleanEngineeringModel.parse` does the same (`python/python_class_model.py:360`, `:373`). `CodeCleanEngineeringModel.file_module()` (`code_class_model.py:292-294`) raises `AttributeError` on a model that was never parsed. `_class_spans` (:248-254) recomputes every class body `_append_classes` (:127-128) already found, because the parse has nowhere to keep them. [3]
- c_family_parse.py:63-65 `_STRING_RE`, `_COMMENT_OR_STRING_RE` — eliminate-duplication — `_STRING_RE` is the same pattern as `STRING_LITERAL` in `source_code/source_text.py:14`; the "blank every comment and string" substitution is written twice in this file (:116, :343) and a third time, removing comments instead of blanking them, in `operation_metrics.py:35`, `:91`. [2]
- c_family_parse.py:512 `_line_at(text, index)` — hold-state-on-the-object-not-in-parameters — All twelve callers pass `self._text` (:138, :141, :170, :217, :218, :235, :236, :305, :348, :392, :447, :471). [3]

### cdd_guidance/practices/clean_engineering/model/class_channel.feature.py

- class_channel.feature.py:212 `_edge_kind`, :222 `_diagram_edges`, :253 `_solid_class_names` — eliminate-duplication — The spec reads draw.io cells by hand beside `drawio/page/drawio_page.py:122` `class_name_in` and `:134` `edge_kind`, and with a different rule: `_edge_kind` calls any `diamondThin` without `startFill=1` an aggregation and any dashed arrow a dependency, while `edge_kind` requires `startFill=0` and `dashed=1` with `endArrow=open`, so the spec checks the diagram against a reading the format does not use. No tier runs it either: `scripts/test.ps1:373` collects `*_spec.py` and story tiers only, and the docstring (:6) gives a manual command. [2]

### cdd_guidance/practices/clean_engineering/model/code_class_model.py

- code_class_model.py:87 `CodeOperation.take_brace_body` — use-consistent-naming — `line_count` means two things: here the non-blank lines inside a brace body, in Python the whole span from `def` to the last line, blanks and signature included (`python/python_class_model.py:138`). `CODE_LINES` (`measures/code_measures.py:127`) reads `line_count` for `limit-function-lines`, so the same function is measured differently in TypeScript and Python, and `Operation.source_lines` (`operation.py:296-297`) reads `line_count` as a span. [2]
- code_class_model.py:296 `render`, :413 `_render_module`, :369 `render_class`, :379 `_member_groups`, :443 `_constructor_body` — hold-state-on-the-object-not-in-parameters — `kept` (the previous file's model) and `known_names` are handed down five layers, and the previous body is found with `kept.operation_body(oclass.name, operation.name)` (:393, :448; lookup at :359-367), two name strings, although the render holds both the class and the operation. [3]
- code_class_model.py:251 `constructor_lines(constructor, …)`, :254 `constructor_parameters(constructor)`, :261 `_elides_parameters(constructor)` — hold-state-on-the-object-not-in-parameters — The caller asks the class for its constructor (`oclass.constructor()`, :387) and hands it straight back to the same class (:389, :457); `CodeClass.constructor()` (:197) already answers it. [3]

### cdd_guidance/practices/clean_engineering/model/javascript/javascript_class_model.py

- javascript_class_model.py:46 `JavaScriptOperation.signature` — use-consistent-naming — The JavaScript format writes a private operation as `#name` (and `identifier` strips the leading `_`, `source_code/code_body.py:77`), but the brace reading recognises privacy only by the `private` keyword (`c_family_parse.py:83`, `:337`) and its method pattern does not read `#` (`:37-42`), so `_helper` is written as `#helper` and read back as a public `helper`. The format spells one concept two ways. [2]

### cdd_guidance/practices/clean_engineering/model/json/json_class_model.py

- json_class_model.py:63 `JsonOoadClass.from_record`, :82 `JsonModule.from_record` — put-logic-on-the-owning-resource — The JSON spelling of a node is split: the reader is here, the writer is `as_record` on the base classes (`base_class_model.py:227`, `:385`, `:579`; `operation.py:65`, `:306`; `property.py:174`), whose only production caller is this format (`json_class_model.py:75`, `:100`, `:133`). The halves have drifted: `modulePath` and `dependencies` are written (`base_class_model.py:233`, `:238`) and never read, and an operation's callees and invariants are never written (`operation.py:306-312`), so a JSON round trip drops them. Stories and UX keep `as_record` on their JSON node classes (`stories/model/json/nodes.py`, `ux/model/json/nodes.py`). [1]
- json_class_model.py:52-60 `load_property`, `load_operation` — eliminate-duplication — Re-implements `OoadClass.load_property` and `load_operation` (`base_class_model.py:242-252`), which already build `self.property_type` and `self.operation_type`; setting the two class attributes is the mechanism every other format uses (`code_class_model.py:158-159`). [2]
- json_class_model.py:74 `JsonOoadClass.render`, :99 `JsonModule.render` — delete-unused-operations — No caller in the repository: the JSON model dumps the whole record itself (:133), `OoadNode` calls no child `render`, and no `.render()` call reaches a JSON class or module (searched `\w+\.render\(\)` across the repository). [3]

### cdd_guidance/practices/clean_engineering/model/module_context_files.py

- module_context_files.py:133 `ModuleContext.folder_facts` — use-typed-signatures — Answers ten facts as `Dict[str, object]` keyed by strings, which the only caller copies onto the module with `setattr` (`base_class_model.py:501-502`); the fact names exist only as dict keys here and strings in `Module.graph_facts`. [3]
- module_context_files.py:18, :87 the module card path — eliminate-duplication — "Which folder is a module" is decided again in `tdd/module_tiers.py:15` (its own `_MODULE_CARD = Path(".context") / "module-context.md"`) with its own walk up the parents (`:90-95`), beside the walk at `reading/code_read.py:203` that asks `ModuleContext(found).exists()`. [2]

### cdd_guidance/practices/clean_engineering/model/operation.py

- operation.py:75 `Operation` — keep-classes-single-responsibility — One class still holds the designed operation, where its code sits, and the rule measures as flat fields (`_start_measures` :170-184; 24 names in `graph_facts` :100-125), and `CodeOperation` adds seven more (`code_class_model.py:59-68`). A change to any rule's measure edits the class every format subclasses. [4] (still open from round 1)
- operation.py:285 `_copy_measures_from` — eliminate-duplication — `clone()` copies `peer_private_access` here and five more measures in `CodeOperation._copy_measures_from` (`code_class_model.py:107-116`); `packed_parameters`, `io_and_domain`, `io_and_domain_callees`, `raises_on_empty`, `exception_without_message`, `generic_exception_message`, `mutates_without_record`, `prose_comment`, and the bold bullet lines are still dropped on a clone. [3] (still open from round 1)
- operation.py:82 `is_constructor` — eliminate-duplication — "Is this the constructor" has three answers: `Operation.is_constructor` (name in `CONSTRUCTOR_NAMES` only), `CodeOperation.is_constructor_of(oclass)` (`code_class_model.py:144`, also a name equal to the class's, and handed its own `self.parent` at :95), and `OoadClass.member_key` (`base_class_model.py:215`); `class_channel.feature.py:52` is a fourth. The source facts use the first (`source_facts.py:96`, `:116`, `:150`), the render the second (`code_class_model.py:198`), so a constructor named after its class gives no held fields and no `constructs` while the render still writes it as the constructor. [2]

### cdd_guidance/practices/clean_engineering/model/operation_metrics.py

- operation_metrics.py:14 — low-coupling — Imports six names from `source_code/source_text.py` that the package does not export (`OWN_CLASS_RECEIVERS`, `OWN_RECEIVERS`, `SAFE_NUMBERS`, `STRING_LITERAL`, `WIRED_PEER_FIELDS`, `is_dunder`); `source_code/__init__.py` exports only `MeasuredBody`, `SourceText`, `SpanCollaborators`, `SpanFailures` from that file, and its card says callers import from the package. [1]
- operation_metrics.py:42 `CardBullets` — high-cohesion — The bold bullets of a markdown model card are still read in the file that measures Python function bodies; its two callers are `source_facts.py:87`, `:215`. [1] (still open from round 1)
- operation_metrics.py:247 `FunctionCollaborators` — eliminate-duplication — `MeasuredBody` now gives `PythonFunctionBody` and `SourceText` one type for five measures, but the collaborator measures still have two shapes: `FunctionCollaborators.reaches_peer_private()` and `built()` take nothing (:256, :282), `SpanCollaborators.reaches_peer_private(own_objects, own_members)` and `built(parameter_names, start_line)` take what the operation knows (`source_code/source_text.py:354`, `:371`), so `PythonOperation.measure` (`python/python_class_model.py:146`, `:148`) and `CodeOperation.load_brace_body_facts` (`code_class_model.py:94-97`) each call their own. [2] (still open from round 1)
- operation_metrics.py:66 `StatementCount(body, python: bool)` — put-logic-on-the-owning-resource — The one body measure not taken when the operation is read: its only caller, `rules/operation_checks.py:145`, rebuilds it from the saved `body_text` string and a language flag, while the operation holds its body with its `CodeLanguage` (`operation.py:165`) and every other body measure is taken in `CodeOperation.measure_body` (`code_class_model.py:99-105`). [3]

### cdd_guidance/practices/clean_engineering/model/property.py

- property.py:32 `InvariantHolder` — use-intention-revealing-names — The base is in fact the class member (property or operation): its `take_words_from` reads and writes `callees` (:50-51), which it does not declare, and the member's owner is written twice, `owner`, `keep_owner`, `_declared_by` at `property.py:84`, `:120-129` and `operation.py:137`, `:222-231`. [2]

### cdd_guidance/practices/clean_engineering/model/python/python_class_model.py

- python_class_model.py:241 `PythonModule.import_targets` — eliminate-duplication — Every Python file's imports are parsed twice: here from the syntax tree, and by `PythonImports` with regular expressions (`source_code/script_imports.py:127-169`), which `ModuleSourceFacts.load` calls on the same text (`base_class_model.py:494`). Both resolve a relative `from` import against the package (:261-267 and `script_imports.py:163-169`), and they treat `if TYPE_CHECKING:` oppositely, by design (`:244` vs `script_imports.py:130`), with nothing tying the two readings together. [2]
- python_class_model.py:126 `_decorator_name`, :274 `_call_name`, :438 `_bare_decorator_name` — eliminate-duplication — Three readers in one file of "the name an `ast.Name` or `ast.Attribute` writes", and a fourth in `operation_metrics.py:137` `PythonFunctionBody._names`; each handles `ast.Call` and dotted names differently. [2]
- python_class_model.py:214 `PythonModule.__init__(*args, **kwargs)` — use-typed-signatures — Hides `Module.__init__(name, sequential_order, graph)` behind packed arguments; a caller cannot see what to pass. [3]

### cdd_guidance/practices/clean_engineering/model/source_facts.py

- source_facts.py:41 `CONSTRUCTOR_NAMES` — eliminate-duplication — BDD's copy is gone, but `cdd_guidance/actions/render/reshaped_code.py:48` still defines the same two names as `_CONSTRUCTORS`. [2] (still open from round 1)
- source_facts.py:66 `ClassSourceFacts`, :138 `CodeClassSourceFacts`, :167 `OperationSourceFacts` — use-intention-revealing-names — "Facts" names the storage (graph facts), not the thing: the lines of source a class or operation spans and what was measured in them. [4] (still open from round 1)
- source_facts.py:33 `_ASSIGNED_FIELD`, :35 `_ASSIGNED_FROM` — eliminate-duplication — "The fields a constructor assigns" is read three ways with two near-identical patterns: `held_fields` (:91-99) from the constructor's body with the first, `constructor_fields` (:101) from the file's lines and `assigned_fields` (:107) from the body with the second. `held_fields` keeps `_` fields and only the hint the assignment writes, `_fields_from` (:112-123) drops `_` fields and falls back to the parameter's hint, so the two disagree on a field's type. [2]
- source_facts.py:219 `_delegates_io_and_domain` — put-logic-on-the-owning-resource — Turns the callee names back into fake source text, one `name(` per line (:224), so `SourceText.calls_io_and_domain` can parse it again; whether a call is I/O or domain work is a question about the call, answered by writing text to be re-read. [3]

### cdd_guidance/practices/clean_engineering/model/type_refs.py

- type_refs.py:37-79 — put-logic-on-the-owning-resource — A type hint is still a bare string parsed here and again in `reading/production_classes.py:238` `names_in`, `reading/code_read.py:47`, `:369`, `reading/code_file.py:98` `_OPTIONAL`, `reading/class_facts.py:183` `_key_type`, `ddd/reading/graph_reading.py:76` `_TYPE_WORD`. The helpers here disagree with each other: `diagram/diagram_node.py:93` and `ddd/model/nodes.py:431` use `pascal_type_names`, which counts `Optional` and `List` as classes, while `FieldArrow` (`property.py:235`) uses `domain_type_names`, which does not; "is a collection" (`property.py:228`) and "is primitive" (:42) are decided by a lower-case first letter. [2] (still open from round 1)
- type_refs.py:45 `parse_parameter` — eliminate-duplication — A model line's parameter is parsed four ways: `parse_parameter` (keeps a default and a `?` in the name), `Operation.from_signature` (`operation.py:195-197`, strips the default, keeps `?`), `python_class_model.py:66` `_PARAMETER` (reads `?` as optional), and `c_family_parse.py:399-415` `_parameter`. `name?: Type = x` becomes a different `Parameter` by each path, and `Parameter` (`operation.py:26`) has no reading of its own line. [2]


### cdd_guidance/practices/clean_engineering/model/diagram/geometry.py

- geometry.py:6 `Point`, :7 `Segment` — eliminate-duplication — A point is `tuple[float, float]` here and `Tuple[int, int]` at `diagram/class_layout.py:22`, and a straight stretch is `Segment` here and `Run` at `class_layout.py:25`; `drawio/page/drawio_page.py:14` imports this one, the router uses the other. One idea, two names and two types. The `Geometry` rectangle of round 1 is gone (cards now use `harness/whiteboard` `Box`); the two point aliases remain. [2] (still open from round 1)
- geometry.py:10 `segments_cross` — eliminate-duplication — Whether two lines cross is answered three ways: `segments_cross` here (used by `class_layout.py:232` and `drawio_page.py:183`, touching counts), `paths_cross` / `_runs_cross` at `class_layout.py:894-911` (right-angle runs, ends inclusive, no tolerance), and `EdgesDoNotCrossOtherEdgesScanner._right_angle_crossing` at `scanners/edges_do_not_cross_other_edges_scanner.py:184-196` (right-angle runs, strictly inside, `CROSSING_TOLERANCE = 2`). The router keeps a route the layout scanner then reports, or reroutes one the scanner would pass, because the two right-angle tests disagree at the ends. [2]

### cdd_guidance/practices/clean_engineering/model/diagram/module_layout.py

- module_layout.py:148 `grid_extents` — prefer-class-operations — A module function whose only callers are `ModuleLayout.size` (:124) and `ModuleLayout._place` (:139); both also work out `header_height`, `columns`, and the children's sizes again for the same module (:119-124 and :136-139), and `size` recurses into every child on each call, so `_place` re-measures the whole subtree once per level. The grid of one module's children is one thing the layout should work out once and keep. [3]

### cdd_guidance/practices/clean_engineering/model/diagram/diagram_node.py

- diagram_node.py:197 `DiagramNode` docstring — limit-comments — "HTML vs Mermaid is the channel": there is no Mermaid channel (the word appears in no other file of the practice); the channels are draw.io and Claude Whiteboard. [4]
- diagram_node.py:205 `parent_id = '1'` — put-logic-on-the-owning-resource — The id of draw.io's default layer sits on the channel-agnostic base every diagram node extends; only `DrawioVertex.append_to` (`drawio/diagram_node.py:50`) reads it and only `_ModulesDiagramWriter._write_module` (`drawio/drawio_class_model.py:386`) sets it. The module card says `model/diagram` is channel-agnostic; a whiteboard card carries a draw.io field it never uses. [1]
- diagram_node.py:321 `module_tab_label` — prefer-class-operations — A module function that takes a module's name; every caller passes `module.name` (`class_view.py:50`, `:66`, `:110`). It is a property of the module. [3]

### cdd_guidance/practices/clean_engineering/model/diagram/class_view.py

- class_view.py:291-293 `ClassViewPage._card_node` — eliminate-duplication — Sets `fill_color` and `owning_module` on any `DiagramClass`, but the base class declares neither, so each channel declares both again (`drawio/diagram_node.py:63-64`, `whiteboard/whiteboard_class_model.py:157-158`). It also sets them on the model's own class object (`node = oclass`, :291), so drawing a page changes the model it draws. [2]
- class_view.py:187-199 `ClassViewPage._writer` — hide-inner-details — The page reads the view's storage directly: `classes_by_cell` (:195, :248, :256, :276, :288), `module_labels`, `module_fills`, `module_of` (:281, :290-293), `relationships` (:216, :269); the draw.io page goes further, into `self._writer.kept`, `self._writer.channel.close_gaps` (`drawio_class_model.py:485`), `unmarked_properties` (:527) and `relationships` (:505). The field is named `_writer` though it holds a `ClassView`, and the whiteboard page keeps the same object a second time as `_view` (`whiteboard_class_model.py:433`). [3]
- class_view.py:322 `plain_class_name` — use-consistent-naming — `ddd/model/stereotypes.py:55` defines a function of the same name that also strips code marks, ` extends ` and ` : `, so the same name gives two answers depending on the import; `drawio_class_model.py:44` imports this one renamed `_plain_class_name`. [2] (still open from round 1)

### cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py

- class_layout.py:691-697 `ArrowRouter._families` and :749-752 `_one_side_per_base` — eliminate-duplication — Both group the inheritance arrows by their base with the same loop; `route` (:638-639) calls one and then the other, so every route groups them twice, and a change to which arrows form a family has to be made in both. [2]
- class_layout.py:55 `INHERITANCE` — eliminate-duplication — The relationship kinds are string literals defined again in each file: `INHERITANCE` here and at `whiteboard_class_model.py:71`, `KINDS` at `whiteboard_class_model.py:72`, the keys of `EDGE_STYLES` at `drawio_class_model.py:61`, `_RELATIONSHIP_KINDS` at `markdown/class_card.py:38` and `sketch/sketch_class_model.py:31`, and bare `'inheritance'` / `'dependency'` at `class_view.py:132`, `:175`, `:218`, `:265`, `diagram_node.py:245`, `drawio_class_model.py:317`; `field_types.RELATIONSHIP_STRENGTH` already lists the kinds. [2]

### cdd_guidance/practices/clean_engineering/model/drawio/diagram_node.py

- diagram_node.py:102-108 `DrawIOClass._operation_lines` — eliminate-duplication — Writes `- name(params): Type` by hand, though `Operation.save` (`operation.py:300-304`) writes exactly that line; the same expression is written a third time at `whiteboard_class_model.py:176-180`, while the markdown card writes `_public_line(operation.save())` (`markdown/class_card.py:176`). Three writers of one operation line. [2]
- diagram_node.py:72-94 `html` and `folded_html` — eliminate-duplication — The two paragraphs that write the properties and the operations under rules are written twice word for word (:78-80 and :91-93). [2]
- diagram_node.py:134-140 `DrawIOImportedClass.html` — eliminate-duplication — The imported card's `+ name: Type` property line is written again at `whiteboard_class_model.py:217`, instead of once on `ImportedClass`, which already owns `key_properties`. [2]
- diagram_node.py:44-57 `DrawioVertex.append_to` — eliminate-duplication — Writes an `mxCell` and its `mxGeometry` by hand, which `harness/drawio` `DrawioPage.add` (`harness/drawio/drawio.py:174-187`) does; the module card names `harness/drawio` as the reader and writer of the class diagram. [2]
- diagram_node.py:182-193 `DrawIOModule.from_cell(cell: ET.Element)` — put-logic-on-the-owning-resource — Takes a raw element and reads `cell.get('style')` and `cell.get('value')`, although `harness/drawio` `DrawioCell` answers `style` and `label`; the `<b[^>]*>` title regex at :189 is a third beside `drawio_page.py:113` and `:127`. [3]

### cdd_guidance/practices/clean_engineering/model/drawio/drawio_class_model.py

- drawio_class_model.py:92-96 `previous`, `keep_positioning`, `close_gaps` — hold-state-on-the-object-not-in-parameters — The earlier drawing still reaches the model two ways, the `written.previous` parameter of `render` and the public field `drawio.py:69` sets from outside, and the two views reconcile them differently: the modules view takes `written.previous or self.previous` (:141, ignoring `keep_positioning`), the class view `written.previous or self.kept_previous()` (:142). `keep_positioning` and `close_gaps` are set true only by `drawio_module_model_spec.py:134`, `:141`, `:148`, `:401`, so `Drawio._keep_previous_from` (`drawio.py:68`) never runs outside specs. [3] (still open from round 1)
- drawio_class_model.py:342-360, :429-438, :467-474, :550-559 — eliminate-duplication — The page skeleton (`mxfile` → `diagram` → `mxGraphModel` → `root` → cells `0` and `1`) is written by hand twice in this file (`_ModulesDiagramWriter.write`, `ClassDiagramWriter.write` with `_add_diagram_page` and `_add_graph_root`), although `harness/drawio` `DrawioFile.add_page` (`harness/drawio/drawio.py:225-232`) now writes it and `DrawioFile.save` writes the text; title, dependency and edge cells are also written as raw `mxCell`s (:371-375, :400-405, :530-538). Round 1's draw.io page moved to the framework, but this writer did not move onto it. [2] (still open from round 1)
- drawio_class_model.py:121-132 `_diagram_xml`, `_read_classes` — eliminate-duplication — Parses the XML itself with `ET.fromstring` and its own failure, wraps the element in `DrawioFile` afterwards, and counts `root_el.findall('diagram')` to decide single page or several; `DrawioFile.from_text` (`harness/drawio/drawio.py:197-207`) parses with `UnreadableDrawio` and `pages` lists the pages. `scanners/_drawio_base.py:65` parses a drawio file a third way (`ET.parse`). [2]
- drawio_class_model.py:456-465 `_previous_pages`, :594-599 `_whole_page` — refuse-unreadable-input — Both catch `UnreadableDrawio` and answer an empty result (`{}`, an empty page). A kept drawing that does not parse then reads as one with no positions, so the render lays out every card afresh and writes over the arrangement a person made, with nothing said. [3]
- drawio_class_model.py:550, :555, :562, :585, :594 — prefer-class-operations — Five module functions (`_set_graph_attrs`, `_add_graph_root`, `_class_card_members`, `_card_lines`, `_whole_page`); `_class_card_members` still returns a four-part tuple that `_vertex_diagram_kind` (:197) and `_class_cards` (:278) unpack, so every card is parsed in full twice per read. [3] (still open from round 1)
- drawio_class_model.py:302-303 and :576-577 — eliminate-duplication — "properties are `Property.from_signature(line) or Property(name=...)`, operations are the lines `Operation.from_signature` reads" is written twice in this file (`_folded_classes`, `_class_card_members`) and a third time at `whiteboard_class_model.py:196-197`. [2]
- drawio_class_model.py:307-325 `_ClassDiagramReader._read_arrows` — eliminate-duplication — The same steps as `whiteboard_class_model.py:647-661` `_ClassReader._take_arrows` (inheritance to bases, `«label»` to a dependency, `take_arrow`, then `prop.arrow.derive()` for every property); only `DEPENDENCY_LABEL` was shared since round 1. The modules readers repeat the same way: `_add_module_dependencies` :219-225 and `_ModulesReader._depend` (`whiteboard_class_model.py:608-612`) both add a dependency once and keep its label. [2] (still open from round 1)
- drawio_class_model.py:363-366 subtitle — eliminate-duplication — The sentence under a modules view's title is written here and again as `MODULES_SUBTITLE` (`whiteboard_class_model.py:52-55`); a change to how the view is explained has to be made in both. [2]
- drawio_class_model.py:443-446, :451-454, :480 `ClassDiagramPageWriter.write(graph, positions, previous_edges)` — hold-state-on-the-object-not-in-parameters — The writer reads its own previous page, works out `positions` and `previous_edges` from it (the same two lines twice, in `_write_single_page` and `_write_module_page`), and hands them to the page it just made for that module; the page already holds the writer and could ask it for its previous page. [3]

### cdd_guidance/practices/clean_engineering/model/drawio/page/drawio_page.py

- drawio_page.py:33-35, :109-185 `ClassDiagramPage.cells`, `vertices`, `edges` and nine module functions — put-logic-on-the-owning-resource — The page unwraps the framework's `DrawioCell` back to raw `ET.Element`s (`[cell.element for cell in page.cells]`), so every reader and scanner goes back to `cell.get('source')`, `cell.get('style')`, `cell.find('mxGeometry')`, and re-wraps when it needs a box (`DrawioCell(cell).box` at :40 and `scanners/prefer_short_routes_scanner.py:204`). `edge_kind`, `is_inheritance`, `anchor_fractions`, `share_inheritance_trunk`, `anchor_point`, `segment_hits_box`, `class_title_in`, `class_name_in`, `quoted_title` take an element or a style string; an edge of a class diagram has no object of its own. [3] (still open from round 1)
- drawio_page.py:151-154 `anchor_fractions` and :168-174 `anchor_point` — eliminate-duplication — Both read `exitX`/`exitY` (or `entryX`/`entryY`) from the style, one from an element and one from a style string; `scanners/edges_approach_perpendicular_scanner.py:44` reads them a third time. [2]
- drawio_page.py:109 `class_title_in` and :122 `class_name_in` — eliminate-duplication — Two regexes for a card's `<b>` title: one unescapes twice and matches `<b[^>]*>`, which also matches `<br/>` (the comment at :126 says why the other avoids it), the other unescapes once; `drawio/diagram_node.py:189` is a third. A scanner can see a different title from the one the model reads. [2]
- drawio_page.py:17 `STRAIGHT_TOLERANCE` — use-consistent-naming — "Pixels a segment may lean and still count as horizontal or vertical" is defined three times under three names with two values: `STRAIGHT_TOLERANCE = 1` here (also used by `edges_approach_perpendicular_scanner.py`), `CROSSING_TOLERANCE = 2` (`edges_do_not_cross_other_edges_scanner.py:136`), `ALIGNMENT_TOLERANCE = 2` (`edges_do_not_overlap_edges_scanner.py:14`). A segment leaning 1.5 px is diagonal to one scanner and straight to the next. [2]

### cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py

- _drawio_base.py:25 `DrawioScanner` — keep-classes-single-responsibility — The base of each layout scanner is still also the runner of all of them (`run_report` :103 makes every scanner), the command line (`run_main` :122 with `argparse`, and an `if __name__ == "__main__"` in each of the ten scanner files), the file collector (`collect_drawio_files` :137) and the registry (`every` :81). [3] (still open from round 1)
- _drawio_base.py:97 `importlib.import_module` — one-way-deps — The base imports each scanner file by name at run time while each of those files imports the base, a cycle between the files of one folder. [1] (still open from round 1)
- _drawio_base.py:81 `every` — eliminate-duplication — Layout rules are still a second rule mechanism: found by a glob over `*_scanner.py`, keyed by a `RULE` attribute read with `getattr` (:29, :89), run by their own runner, while the framework holds one registry mechanism (`harness/annotations/class_registry.py:10` `ClassRegistry`) and the practice's other rules are listed in `rules/`. [2] (still open from round 1)
- _drawio_base.py:20, :137-147 `SKIP_DIR_NAMES`, `collect_drawio_files` — eliminate-duplication — Walks the folder with its own list of skipped folders, beside `harness/graph/skipped_folders.py` (`skips_folder` :48, `scanned_files` :55), so a folder the graph skips can still be scanned here and the reverse. `scan` (:51 and :55) also filters skipped paths twice. [2]

### cdd_guidance/practices/clean_engineering/model/drawio/scanners/class_title_no_markdown_bold_scanner.py

- class_title_no_markdown_bold_scanner.py:21-28 `scan_page` — eliminate-duplication — The same body as `stereotype_above_class_name_scanner.py:21-30` (each vertex, `class_title_in`, one test on the title, a message with `quoted_title`); the two differ only in the test and the words. [2]

### cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_do_not_cross_other_edges_scanner.py

- edges_do_not_cross_other_edges_scanner.py:161 `_name` — eliminate-duplication — An edge is named for a message three ways: `ClassDiagramPage.describe` (`drawio_page.py:53`, `Source->Target (kind)`), `_name` here (`Source -> Target`), and `prefer_short_routes_scanner.py:182` (`Source → Target`), so the same edge reads differently in one report. [2]

### cdd_guidance/practices/clean_engineering/model/drawio/scanners/leaf_nodes_not_in_horizontal_row_scanner.py

- leaf_nodes_not_in_horizontal_row_scanner.py:109-118 `_sized_vertex_boxes` — eliminate-duplication — Reads every vertex's box from its `mxGeometry` by hand; `prefer_short_routes_scanner.py:200-207` `_vertex_boxes` does it again through `DrawioCell(cell).box`, and the framework's `DrawioPage.boxes()` (`harness/drawio/drawio.py:156`) already answers every vertex's box by id. [2]

### cdd_guidance/practices/clean_engineering/model/markdown/class_card.py

- class_card.py:66 `ClassCard` — keep-classes-single-responsibility — One object reads a card's lines and writes any class as a card, but writing never reads `_lines`, so every writer makes it with an empty list: `ClassCard([]).lines_of(self)` (`markdown_class_model.py:117`), `_MEMBERS = ClassCard([], writes_constructor=False)` (`ddd/model/markdown/class_cards.py:20`, `ddd/model/sketch/sketch_nodes.py:26`). [3]
- class_card.py:120-146 `_read_properties` and `_read_operations` — eliminate-duplication — The same loop (skip blank and `#`, a note or call goes to the member above, else read a member) written twice, differing in the reader and in `→` being a call only under an operation. [2]
- class_card.py:228-248, :307-308, :367-372 — eliminate-duplication — A `-> call` line is read three ways in this file: under a property it is appended raw (:235), under an operation it goes through `parse_arrow_line` and is not added twice (:245-248), in a sketch fence it is appended raw and may repeat (:308, :370); `sketch_class_model.py:159-163` and `:422-425` are a fourth and fifth. The same line gives different callees depending on which reader meets it. [2]
- class_card.py:265 `FenceRead`, :274 `SketchFence` — keep-classes-single-responsibility — Reads DDD's sketch words (`repo:` repositories, `refs:` identities, `invariant:`, and map lines `pattern:`, `crosses:`, `integrat`, `direction:` at :261) inside Clean Engineering's class-card package, and hands them back as a data bag; its only caller is `ddd/model/sketch/sketch_nodes.py:53`. Clean Engineering's own sketch (`sketch/sketch_class_model.py`) does not use it. [1]
- class_card.py:41-254 — prefer-class-operations — Eleven module functions; `_note_on_property(prop, line)` and `_note_on_operation(operation, line)` take the object they change, and `_property_in` / `_operation_in` make a `Property` / `Operation` from a line beside `Property.from_signature` and `Operation.from_signature`. [3]

### cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py

- markdown_class_model.py:54 `_HEADING`, :478-489 `_headings` — eliminate-duplication — A fence-aware heading scan written by hand, although `harness/markdown/markdown.py:173` `MarkdownText.headings()` does exactly that; the same `^(#{1,6})\s+(.+?)\s*$` pattern is at `reading/card_lines.py:16` and `harness/markdown/markdown.py:168`, and `sketch/sketch_class_model.py:30` with `:357-373` is a fourth fenced scan. [2] (still open from round 1)
- markdown_class_model.py:262-276 `MarkdownModule.render_cards` and :403-416 `CardDocument.render` — eliminate-duplication — The same algorithm (write each kept part in place, a model node by identity, then append each node not yet written) for cards in a module and modules in a document. [2]
- markdown_class_model.py:125-136 and :204-225 — eliminate-duplication — "Write back the text as read while the model has not changed it" is kept twice with two pairs of fields: `MarkdownOoadClass._card` / `_card_model` and `MarkdownModule._read_text` / `_read_as`, each comparing a fresh render with the render at read time. [2]
- markdown_class_model.py:418-427 `CardDocument._module_at` — put-logic-on-the-owning-resource — The document builds `MarkdownModule`s and appends them to `self._model.modules`, while `MarkdownCleanEngineeringModel._read_modules` (:467-476) builds them on the model itself; two owners create the model's modules. [3]

### cdd_guidance/practices/clean_engineering/model/sketch/sketch_class_model.py

- sketch_class_model.py:112-190, :407-431 `SketchOoadClass.read_member`, `read_uml_member`, `_Nest` — eliminate-duplication — Clean Engineering now holds two readers of a sketch's class members: this one and `SketchFence` (`markdown/class_card.py:274-376`), which DDD uses and this format does not; `_Nest.taken` and `SketchFence._calls_below` both collect the `->` lines under a member, `_take_uml_note` and `_note_on_operation` both read a `//` invariant. [2] (still open from round 1)
- sketch_class_model.py:86-89, :33, :284-289 — eliminate-duplication — The heading `Cart <<Aggregate Root>> : Basket, Auditable` is written here and read by its own regex, although `ClassHeading` (`markdown_class_model.py:59-100`) reads and writes exactly that heading (`read`, `text`, `_tail`). [2]
- sketch_class_model.py:112, :142 `read_member(lines, index)`, `read_uml_member(lines, index, owner)` — hold-state-on-the-object-not-in-parameters — The reading position lives in `_SketchCards` and is handed to the class, which answers the next index; the domain class parses a text stream, while the markdown format gives the same job to `ClassCard`. Two shapes for "read a card onto a class". [3]
- sketch_class_model.py:415 `_Nest.taken` — prefer-instance-operations — A `@classmethod` not named as a factory (`from_*`, `create`, …). [3]
- sketch_class_model.py:395, :399, :434 — prefer-class-operations — `_is_rule`, `_uml_member`, `_is_return_type` are module functions; `_uml_member` makes an operation or property from a member line, a factory of `SketchOperation` / `SketchProperty`. [3]

### cdd_guidance/practices/clean_engineering/model/whiteboard/whiteboard_class_model.py

- whiteboard_class_model.py:382 `ClassBoard._arrows_across_pages` — hide-inner-details — Makes a `ClassViewPage` only to call its private `_arrows()` from outside the class. [3]
- whiteboard_class_model.py:493 `_arrow_element` — prefer-class-operations — A module function of five parameters plus `**route` that turns a `DiagramArrow` into a board arrow (kind, label, dash, heads); it is the board's counterpart of draw.io's `EDGE_STYLES` and belongs on the arrow it reads. `_element` (:75) and `_text_box` (:81) are module functions too. [3]
- whiteboard_class_model.py:208-212 `WhiteboardImportedClass.width`, `height` — eliminate-duplication — The same two bodies as `WhiteboardClass.width`, `height` (:183-187), repeated because `ImportedClass.height` comes before `WhiteboardClass.height` in the inheritance order. [2]
- whiteboard_class_model.py:48-51 — limit-comments — The string at :51 ("How far a modules view's title stands above the line under it") describes `SUBTITLE_ROOM` (:48) but sits as a second docstring after `SUBTITLE_WRAP` (:49-50), so `SUBTITLE_ROOM` reads undocumented and `SUBTITLE_WRAP` reads described twice. [4]


### cdd_guidance/practices/clean_engineering/measures/checked_measures.py

- checked_measures.py:96 `CheckedCodeMeasures._measure` — hide-inner-details — A measure is written with `setattr(node, measure.name, value)` when the name is one of `node.graph_facts`, else with `set_fact`; the same branch is written again at `reading/code_read.py:437-440` (`ClassJoins._take_facts`) and `measures/examples/code_measures_examples.py:171-174` (`holding`). Three callers know which facts a node keeps as attributes and which in its fact store, and a name missing from `graph_facts` silently becomes a new attribute. The node should take a fact one way. [3]
- checked_measures.py:62 `_is_function` — eliminate-duplication — Same body as `ReaderTool._is_method` (`measuring_tools.py:250-251`). "A function is an Operation or a Property a getter backs" is tested a third and fourth time, negated, at `code_measures.py:115` and `reading/graph_reading.py:201` (and `rules/operation_checks.py:118`), and the node types are a literal again at :49 beside `code_measures.py:45` `NODE_TYPES` and `graph_reading.py:51` `member_types`. [2]
- checked_measures.py:66 `_files_in` — eliminate-duplication — "Which module holds this path, leaving out modules nested in it" is answered four ways: here (prefix test against every other module), `ReaderTool._classes_of_module` (`measuring_tools.py:273-281`, the same nested-module walk over classes), `ModuleImports._owner` (`reading/folder_facts.py:107-110`, longest prefix), and `CodeFolders._nearest` (`reading/code_read.py:562-572`, walking parents). Each measure and each module fact can put a file in a different module. [2]
- checked_measures.py:119 `_from_root` — eliminate-duplication — "A file's path from the source root" is computed here (empty outside the root), in `MeasuredNode.keep_file` (`measuring_tools.py:97-99`, the bare file name outside the root), and in `ReaderTool._copied_code_blocks` (`measuring_tools.py:286-289`, dropped outside the root): three answers for one question. [2]
- checked_measures.py:23 `_LANGUAGE_OF` — eliminate-duplication — "Which language is this file written in" is asked by suffix in seven places: `_LANGUAGE_OF` here, the suffix set at `measuring_tools.py:297` and again at `reading/operation_facts.py:35`, `_COMMENT_OPENERS` at `copied_blocks.py:18`, `_SCRIPT_SUFFIXES`/`_language_of` at `reading/code_file.py:125,1814`, `.endswith(".py")` at `reading/operation_counts.py:30`, and `reading/second_registries.py:78`; the graph node already answers `file_language` (`harness/graph/graph.py`). [2] (still open from round 1)

### cdd_guidance/practices/clean_engineering/measures/read_facts.py

- read_facts.py:19 `DESCRIBED_FACT` — low-coupling — The fact the reading records (`code_read.py:238`) now lives in the measures package, and DDD imports it from there (`ddd/reading/graph_reading.py:31`) along with seven reading files; "is this class described by a model document" is still a string looked up with `has_fact(DESCRIBED_FACT)`, not a property of the class. [1] (still open from round 1)
- read_facts.py:43 `is_under`, :50 `parameters_of`, :56 `counted_parameters` — prefer-class-operations — Three module functions that take the node or path they are about. They were moved here only so the reading can import downward, so a measures file now holds graph helpers with no measuring in them, and BDD imports `parameters_of` from Clean Engineering's measures (`bdd/model/graph_bdd_model.py:21`). [1] (still open from round 1)
- read_facts.py:43 `is_under` — eliminate-duplication — `code_read.py:272-274` `_under` answers the same question differently at the root: `_under(file, "")` is true, `is_under(file, "")` is false; `statement_links.py:73` writes a third test with `startswith(f"{folder}/")`. [2]

### cdd_guidance/practices/clean_engineering/measures/code_measures.py

- code_measures.py:96 `CodeMeasure.value_on` — use-intention-revealing-names — The measures compare names against `MODULE_FUNCTION_HOLDER` to tell module functions from methods (here, `checked_measures.py:50`), as the reading does at `reading/module_exposure.py:58`, `production_classes.py:230`, `card_drift.py:48`, `statement_links.py:53,55`, `receiver_causes.py:178`, `code_file.py:419,449,480`, `operation_facts.py:29`, `graph_reading.py:68,180`. The class model still has no module functions, so every new reader has to remember the fake class. [4] (still open from round 1)

### cdd_guidance/practices/clean_engineering/measures/measuring_tools.py

- measuring_tools.py:197 `RadonTool._least_maintainability` — errors-out-of-existence — It reads each file with strict UTF-8 (:202) and catches only `SyntaxError`; a file holding a byte that is not UTF-8 raises `UnicodeDecodeError`, which `CheckedCodeMeasures._answer` does not catch (it catches `MeasureNotTaken`, `checked_measures.py:106`), so the whole validate fails on a file the code read keeps as unreadable and reports (`code_read.py:135-136`). `_unshared_method_groups` (:257) has the same strict read. [3]
- measuring_tools.py:304 `ReaderTool._abstractness` — put-logic-on-the-owning-resource — A class counts as abstract when a regex (`_ABSTRACT`, :50) finds `ABC`, `Protocol`, or `@abstractmethod` anywhere in its text, docstrings included, so a class whose docstring names a protocol is "abstract". The graph already keeps each class's `bases`, `CodeIndex.is_protocol` answers it (`graph_reading.py:255`), and a third regex for abstract members is `call_links.py:31` `_ABSTRACT_MARK`. [2]
- measuring_tools.py:212 `ReaderTool` — keep-classes-single-responsibility — One class takes eight measures from three unrelated sources: counts of graph edges (`_classes_depended_on`, `_methods_set_off`), Python syntax trees of the file's text (`_unshared_method_groups`), and clone detection over every production file (`_copied_code_blocks`). Its methods share no field but `_copied`, so by the practice's own `keep-class-methods-sharing-data` it is several classes in one. [3]

### cdd_guidance/practices/clean_engineering/measures/examples/code_measures_examples.py

- code_measures_examples.py:138 `shop_project` — use-explicit-dependencies — The stand-in tools are swapped in by mutating `GraphReading.measuring_tools`, a public dict the reading fills from the global `TOOLS` in its constructor (`reading/graph_reading.py:75`); the tools are never handed in, so a public mutable field is the only seam for replacing them. [3]

### cdd_guidance/practices/clean_engineering/reading/graph_reading.py

- graph_reading.py:44 `GraphReading` — use-consistent-naming — The other practices name theirs `BddGraphReading`, `DddReading`, `StoriesReading`, `UxReading`; Clean Engineering's still carries no practice name. [4] (still open from round 1)
- graph_reading.py:73 `model_documents` — public-seam-only — BDD calls `model_documents.described_member` (`bdd/model/graph_bdd_model.py:78`), yet the reading card's seam terms name no `ModelDocuments`; likewise `NodeEvidence` (imported by `bdd/model/graph_reading.py:21` and `stories/model/story_node_types.py:9`) and `CODE_FIDELITY`, `MODEL_FIDELITY` (imported by `ddd/reading/graph_reading.py:30`) are used across practices and missing from the card. [1] (still open from round 1)
- graph_reading.py:177 `CodeIndex.class_declaring`, :184 `constructors_of` — hold-state-on-the-object-not-in-parameters — A member's class is found by its `owner` name and same file, although the read joined them with an `owns` edge, which `operations_of` (:191) on the same class does use. The owner-name lookup is repeated in `code_file.py:504` (`getter_of`), `:816` (`member_of`), `:906` (`_declaring`), `code_file.py:660`, and `bdd/model/graph_bdd_model.py:119`. [3] (still open from round 1)
- graph_reading.py:257 `CodeIndex.is_protocol` — eliminate-duplication — A base's bare name is parsed in seven shapes: `split("[")[0].rsplit(".")` here, `split("[")[0].split("<")[0]` at `call_links.py:56` and `code_file.py:827`, the `_SPECIALISED` pattern at `code_file.py:1742`, `split("[")[0].split("<")[0].rsplit(".")` at `receiver_causes.py:167`, `rsplit(".")` then `split("[")` at `production_classes.py:102`, and the raw fact at `class_facts.py:117`. `pkg.Base<T>` gets a different name from each. [2] (still open from round 1)
- graph_reading.py:264 `CodeIndex._lineage` — eliminate-duplication — A class's ancestors are worked out four ways: from `baseClass` edges here, from the `bases` fact resolved by the file in `_ClassMembers.lineage_of` (`code_file.py:830-835`), by name over every class of that name in `CopiedModels._beyond_bases` (`class_facts.py:119-132`), and in `ProductionClasses._derives` (`production_classes.py:208-215`). Two classes of one name give different lineages depending on which reader asks. [2]
- graph_reading.py:295 `CodeIndex._is_code` — eliminate-duplication — A member read from a model document is told by its file ending in `.md`, while a class is told by `DESCRIBED_FACT` four lines up (:291); `statement_links.py:109` uses the suffix again. [2]
- graph_reading.py:385 `ModelDocuments._every_folder` — eliminate-duplication — The `os.walk` with `dirnames[:] = [... if not skips_folder(name)]` is written again at `code_read.py:580-581`. [2] (still open from round 1)

### cdd_guidance/practices/clean_engineering/reading/code_read.py

- code_read.py:53 `CodeRead`, :146 `OutsideScope`, :209 `DescribedClasses`, :277 `ClassNodes`, :383 `ClassJoins`, :455 `CodeFolders` — shape-classes-around-resources — Six one-read doers, each unpacking the same `reading` into `_graph`, `_in_graph`, `_test_code`; `ClassNodes.add(relative, folder, cls)`, `add_property(relative, cls, prop)`, `add_operation(relative, cls, operation)`, and `CodeFolders.take(relative, module)` are handed the path, the folder node, and the model on every call. `ClassJoins` is new since round 1 and repeats the shape. [3] (still open from round 1)
- code_read.py:492, :505, :546, :568 parent folder — eliminate-duplication — `str(Path(x).parent).replace("\\", "/")` four times (`"."` at the root), beside `folder_facts.parent_folder` (`folder_facts.py:34`, `""` at the root) and `_described_folder` (:262, `"."` at the root). [2] (still open from round 1)
- code_read.py:295-300, :339, :346, :349, :446 node ids — eliminate-duplication — Each child joins its parent with the same three calls (`in_graph.add`, `edges.link("owns", …)`, `edges.relate("belongsTo", …)`), and the id format `clean_engineering:{Type}:{relative}:{name}` is spelled by hand five times; `_drop_held` (:446) rebuilds a class's id from strings to find it again. [2] (still open from round 1)
- code_read.py:601-605 `module.type = "Module" / "Package"` — use-intention-revealing-names — One `Module` class still stands for two node types, chosen by assigning a string to `type` after construction. [4] (still open from round 1)
- code_read.py:262 `_described_folder`, :267 `_depth`, :272 `_under` — prefer-class-operations — Three module functions used only by `DescribedClasses`; `_under` repeats `read_facts.is_under` with a different answer at the root (see read_facts.py:43). [3]
- code_read.py:528, :536 fact keys — provide-meaningful-context — The folder fact `"imported_classes_by_file"` is a literal here and at `graph_reading.py:233`, `module_exposure.py:122`, `statement_links.py:60`, and a private constant `_FILES_FACT` at `second_registries.py:24`; `"sibling_imports"` is a literal here and at `folder_facts.py:69,71`. A misspelling in any reader reads an empty fact and finds nothing, silently. [2]

### cdd_guidance/practices/clean_engineering/reading/call_links.py

- call_links.py:42 `ClassLinks`, :95 `FieldLinks`, :136 `CallLinks` — shape-classes-around-resources — Each is made from `reading`, copies `reading.graph`, `reading.in_graph`, `reading.code_index`, runs `link()` once, and is thrown away (`graph_reading.py:125-128`); steps of one read acting on graph nodes as data. [3] (still open from round 1)
- call_links.py:187 `CallLinks._is_abstract` with `_NO_BODY` (:35), `_DOCSTRING` (:32), `_python_body` (:201) — eliminate-duplication — "This member has no body" is worked out again from node text although `Operation.has_body` (`model/operation.py:87-93`) defines it for the fidelity rule; the two disagree: `throw new Error('not implemented')` is no body there and a body here. [2]
- call_links.py:34 `_CALL_MARKER` — eliminate-duplication — The same regex is defined again at `code_file.py:42`. [2]
- call_links.py:83 `_class_attributes` — prefer-class-operations — A module function used only by `ClassLinks._realize` (:69), taking the node it reads. [3]

### cdd_guidance/practices/clean_engineering/reading/code_file.py

- code_file.py:1 — limit-module-file-lines — 1,823 lines holding fourteen classes and thirteen module functions: type-hint reading (`_HintTypes`), name resolution (`CodeFile`), inferred answers (`MemberAnswers`), generics (`_TypeArguments`), method resolution order (`_ClassMembers`), locals, expressions, chain heads, and chain walking. Well past the 800-line limit; each is a separate reason to change. [1]
- code_file.py:274 `_HintTypes` — put-logic-on-the-owning-resource — A type hint is still a bare string parsed in many places with different word lists: `_HintTypes` here with `_WRAPPERS` (:109, no `Union`, no `Annotated`), `ReceiverCauses.of_hint` with its own `_WRAPPERS` (`receiver_causes.py:31`, with both), `code_read._names_in`/`_HINT_WORD` (`code_read.py:369,47`), `names_in` (`production_classes.py:238`), and `_key_type` (`class_facts.py:183`). A hint the typer unwraps can be reported as un-typable by the cause reader. [2] (still open from round 1)
- code_file.py:1681 `_top_level_parts` — eliminate-duplication — `split_top_level` (`source_code/bracket_structure.py:73`, used by `call_arguments.py`, `class_facts.py:188`) does the same split. Brackets are matched by three scanners: `function_text.closing_bracket` (`function_text.py:12`, skips strings), `BracketStructure.closing_bracket` (`bracket_structure.py:13`, used at `call_arguments.py:24`, `second_registries.py:86`), and `_opening_at` here (:1782) beside `BracketStructure.opening_bracket`. [2]
- code_file.py:643 `MemberAnswers._returned`, :707 `_declared_function` — eliminate-duplication — The same "every typed `return` agrees" steps (:647-649 and :716-719). [2]
- code_file.py:452 `CodeFile.module_value`, :462 `module_cause` — eliminate-duplication — Two copies of one loop over this file and its imported files, differing only in which `answers` call they make. [2]
- code_file.py:646, :665, :679, :703, :717 `_SpanCalls(...).expressions.typed_at` — hide-inner-details — `MemberAnswers` builds a span reader and reaches into its part; `_SpanCalls` exposes `file`, `index`, `code`, `owner`, `unjoined`, `members`, `locals`, `expressions`, `heads` as public fields that `_Expressions` (:1019-1025), `_Heads` (:1265-1270), and `_ChainWalk` (:1366-1369) copy into their own fields. [3]
- code_file.py:252 `SpanReach` — hide-inner-details — Its `members`, `guessed`, `classes`, and `unresolved_calls` are public containers other classes change directly: `_Heads` appends (:1290, :1344, :1355), `_ChainWalk._walk_guessed` deletes a slice (`del found.classes[classes:]`, :1408), and `UnjoinedCalls.count` is handed the dict to increment (`receiver_causes.py:176-179`, called :1492, :1592). [3]
- code_file.py:194 `CodeSpan.code_of` — prefer-instance-operations — A `@staticmethod` that is not a creation name, called through the class at `graph_reading.py:199`, `code_file.py:662,694,716`, `statement_links.py:79,97`. [3]
- code_file.py:721 `MemberAnswers.text_of` — eliminate-duplication — A file's text is read seven ways with different decoding: here (UTF-8, replacement characters), `CodeRead._text_of` (`code_read.py:130`, `utf-8-sig`), `OutsideScope.class_names` (`code_read.py:178`, `utf-8-sig`), `CopiedBlocks._code_lines` (`copied_blocks.py:95`, replacement), `SecondRegistries._text_of` (`second_registries.py:90-94`, strict), `RadonTool` (`measuring_tools.py:202`, strict), and `ReaderTool._unshared_method_groups` (`measuring_tools.py:257`, strict, and re-read for every class although `node.source.text` holds the class, as `_abstractness` :304 uses). A file with a byte-order mark gives `﻿` as its first character to the UTF-8 readers and not to the code read. [2]
- code_file.py:142 `_LOOKUP_ARGUMENTS` — eliminate-duplication — "This argument names or looks something up" is two patterns: `name|path|key|slug` here (an edge marked `looked up by name`) and `name|slug|key|path|record|data|row|config|payload` at `owned_dependencies.py:32` (`_NAMED_TEXT`), which then judges the same edges; a `config` argument is a lookup for one and not the other. [2]

### cdd_guidance/practices/clean_engineering/reading/function_text.py

- function_text.py:12, :36, :52, :73, :80 — prefer-class-operations — A file of hanging functions over text; `python_function` finds a `def` by regex in text the Python class model already parses, for `MemberAnswers._declared_function` (`code_file.py:710`) alone. [3]

### cdd_guidance/practices/clean_engineering/reading/card_lines.py

- card_lines.py:16, :28-35, :59-72 — eliminate-duplication — Headings and the lines under a heading are still scanned by hand although `harness/markdown/markdown.py` gives `MarkdownText.headings()` (:173) and `section_lines()` (:226); `_HEADING` is the same pattern as `model/markdown/markdown_class_model.py:54`. [2] (still open from round 1)
- card_lines.py:37 `CardLines.place` — put-logic-on-the-owning-resource — Sets another object's state field by field: `oclass.line`, `oclass.end_line`, each member's `line` and `end_line`, and `operation.line_count = 1` (:44-51), instead of asking the class to place itself at a card. [3]

### cdd_guidance/practices/clean_engineering/reading/class_facts.py

- class_facts.py:37 `ComparedFact` and its subclasses `ServicesTakingDataBags`, `CopiedModels`, `PassThroughClasses`, `DomainExtensions`, `BuiltCollaborators` — shape-classes-around-resources — The names now say what each finds, but each is still a measurer with one `record()` that writes a string-keyed fact (`"data_bags_taken"`, `"copied_fields"`, `"forwards_to"`, `"extends_domain"`, `"constructs_collaborator"` as literals) for a rule in `rules/` to read back; `compared_facts.py:48-67` runs them in a tuple whose order is the only contract (`CardDrift` reads what `ModuleImports` writes, `SameBodies` reads what `BodyCopies` writes). [3] (still open from round 1)
- class_facts.py:191 `CopiedModels._class_named`, :195 `_words` — eliminate-duplication — Snake and camel case are split and joined by hand, as `operation_verbs.py:24` `_WORD_START` does again, although `harness/annotations/name.py:11` `Name` is "the one case conversion every published name goes through" and offers `words`. [2]
- class_facts.py:262 `PassThroughClasses._folder_id` — eliminate-duplication — In the same file a class's folder is found by its `belongsTo` edge here and by `parent_folder(each.file)` in `DomainExtensions` (:279); a class held at the practice's root gets a folder from one and not the other. [2]
- class_facts.py:338 `operation.name in CONSTRUCTOR_NAMES` — eliminate-duplication — The constructor test is a name compared with a constant at `class_facts.py:338`, `operation_counts.py:31`, `production_classes.py:118,205`, `passed_state.py:74,120`, `operation_verbs.py:34`, `graph_reading.py:187,201`, `code_read.py:425`, while `Operation.is_constructor` answers it on the model. [2] (still open from round 1)

### cdd_guidance/practices/clean_engineering/reading/compared_facts.py

- compared_facts.py:52 `registered_in_this_process()` — use-explicit-dependencies — The compared facts read three process-global catalogues (`PRACTICE_CATALOGUE`, `ACTION_CATALOGUE`, `REGISTERED_PATTERNS`, `public_routes.py:44-53`) in the middle of a read, so which classes count as public depends on what the process happened to import; the reading cannot be given another set. [3]

### cdd_guidance/practices/clean_engineering/reading/folder_facts.py

- folder_facts.py:20 `record_fact`, :28 `own_fact`, :34 `parent_folder`, :39 `folders_of`, :44 `imported_folders` — prefer-class-operations — Five module functions that take the node or the practice's nodes as their first parameter and reach into them; `record_fact` is imported by twelve files. [3] (still open from round 1)

### cdd_guidance/practices/clean_engineering/reading/imported_classes.py

- imported_classes.py:17 `ImportedClasses` — eliminate-duplication — Two resolvers still answer "which class does this file mean by this name": `ImportedClasses._resolved`/`_re_exported` and `CodeFile._in_reach`/`_passed_on` (`code_file.py:524-544`). Both now follow re-exports, but only `ImportedClasses` also tries each folder above the importer as an import root (:44-49), and only `CodeFile` falls back to a class beside the file (`code_file.py:546-551`), so `deep-module`'s public classes and the `invokes` edges can name different definitions. [2] (still open from round 1)

### cdd_guidance/practices/clean_engineering/reading/module_exposure.py

- module_exposure.py:117 `ClassNamers._references` — eliminate-duplication — Rebuilds each file's `ClassReference` list from the folder facts (:122-125, :132), the same work as `CodeIndex._imports_of` (`graph_reading.py:229-236`); both know how a reference is stored as a list. [2] (still open from round 1)
- module_exposure.py:47, :103 `in_graph.practice.reading.test_code` — use-explicit-dependencies — Reaches back from the node set to the practice to its reading for the test-code rule, as `operation_facts.py:38` and `second_registries.py:48` do; `ComparedFacts` already holds the reading and could hand it in. [3]

### cdd_guidance/practices/clean_engineering/reading/node_evidence.py

- node_evidence.py:23 `NodeEvidence.text` — hide-inner-details — Reads another object's storage, `source.__dict__["text"]`, and the node's `callees`, `collaborators`, `dependencies`, `type_hint` through `getattr` with defaults (:30, :84, :86). [3]
- node_evidence.py:39 `calls`, :80 `CodeNodeTypes.links` — eliminate-duplication — A second rule for `invokes`: any call `name(` in the text links to a target of that name, whatever class it is on. The reading card says an `invokes` edge "means the same member whichever practice draws it" through `CodeFile`, yet BDD (`bdd/model/graph_reading.py:54`) and Stories (`stories/model/story_node_types.py:34`) judge links through this text match. [2]

### cdd_guidance/practices/clean_engineering/reading/operation_counts.py

- operation_counts.py:27 `operation_count` — do-not-invent-parallel-object-models — Counts operations from the `operation_shapes` dicts saved on the class (`shape["name"]`, `shape.get("is_private")`), as `ProductionClass.has_behavior` does (`production_classes.py:118-119`), beside the `Operation` nodes the graph holds for the same operations. [2] (still open from round 1)

### cdd_guidance/practices/clean_engineering/reading/operation_facts.py

- operation_facts.py:25 `qualified_name`, :32 `code_operations`, :42 `file_qualified_name` — prefer-class-operations — Module functions that take an operation node or the practice's nodes; `code_operations` is imported by four recorders and rebuilds the suffix set on every call (:35). [3]

### cdd_guidance/practices/clean_engineering/reading/owned_dependencies.py

- owned_dependencies.py:77 `DependenciesToOwn._operations_of` — eliminate-duplication — Same body as `CodeIndex.operations_of` (`graph_reading.py:191-193`) and the same result as `ProductionClasses.operations_of` (`production_classes.py:179`), which it could ask. [2]

### cdd_guidance/practices/clean_engineering/reading/production_classes.py

- production_classes.py:105 `ProductionClass.operations`, :179 `ProductionClasses.operations_of` — use-intention-revealing-names — Both say "the public operations", but the index (:152-154) holds every owned `Operation`, private ones and constructors included. `PassThroughClasses._forwarding_target` (`class_facts.py:213-225`) relies on "every public operation forwards", so a class with one private helper is never reported as a pass-through; `ParameterEveryOperationTakes` filters `_` names itself (`passed_state.py:120`) and `DependenciesToOwn._operations_of` was written again on the belief that these exclude private ones. [4]
- production_classes.py:110 `ProductionClass.operation_count`, :128 `ProductionClass.is_value` — delete-unused-operations — No reader in the repository, specs included: every `.is_value` call is on `ProductionClasses` (`class_facts.py:323`, `owned_dependencies.py:48`), and no `.operation_count` access exists. [3]

### cdd_guidance/practices/clean_engineering/reading/receiver_causes.py

- receiver_causes.py:128 `UnjoinedCalls.keep_parameter` — delete-unused-operations — No caller in the repository; parameters reach `_Locals.keep` instead (`code_file.py:1550-1551`). [3]
- receiver_causes.py:43-46 `_PYTHON_IMPORT`, `_PYTHON_FROM`, `_SCRIPT_IMPORT` — eliminate-duplication — A file's imports are parsed again with regexes although `ScriptImports` (`source_code`) parses them for every file (`code_read.py:184`, `graph_reading.py:222`); `statement_links.py:34-35` defines two more patterns under the same names for the same lines. [2]
- receiver_causes.py:88 `ReceiverCauses.is_literal` — prefer-instance-operations — A `@staticmethod` that is not a creation name, called through the class (`code_file.py:1083`). [3]

### cdd_guidance/practices/clean_engineering/reading/same_bodies.py

- same_bodies.py:22-24, :68 `SameBodies._code` — eliminate-duplication — `_COMMENT_LINE` and `_DOCSTRING` are copied character for character from `near_copies.py:34-35`, `_TOKEN` nearly (`near_copies.py:33`), and `_code` repeats the first line of `NearCopies._runs_of` (`near_copies.py:78`); the two duplication checks strip comments in two places. [2]

### cdd_guidance/practices/clean_engineering/reading/statement_links.py

- statement_links.py:108 `StatementLinks._is_production` — eliminate-duplication — Production code is "not `.md` and not example code" here, "not test code and not described" in `production_classes.py:227-230`, "not test code" in `checked_measures.py:44` and `operation_facts.py:38`, and "not example code" in `module_exposure.py:53`; a spec file's module statements are linked here as production. [2]
- statement_links.py:112 `_outside`, :129 `_header_end` — prefer-class-operations — Two module functions used only by `StatementLinks` (:78, :85, :96). [3]


### cdd_guidance/practices/clean_engineering/rules/class_rules.py

- class_rules.py:16 `_CLASS_BUDGET` — eliminate-duplication — `rule_numbers.py:1-5` says every number a rule holds is named once there and filled into the rule's text by a marker, so a check never reports a limit its rule does not state. The class budget of 9 is kept here instead. The rule's text (`clean_engineering.md:238`) says only "one reason to change", while the finding at :32 reports "budget ~9", a number no rule states. [2]
- class_rules.py:29, :42 `_public_operations_for_budget(self, shapes: list[dict])` — do-not-invent-parallel-object-models — The rule still reads each operation as a dict (`shape["name"]`, `shape.get("is_private")`, `shape.get("is_property")`) from the class's `operation_shapes` fact, beside the `Operation` nodes the graph already holds. `operation_checks.py:296` reads the same dicts. [2] (still open from round 1)
- class_rules.py:27 `MODULE_FUNCTION_HOLDER` — use-intention-revealing-names — Code still tells a module function from a method by comparing a class's name to `"_module"`. It does so here and five more times in `code_use.py` (:69, :239, :256, :270, :301). The domain has module functions, and the model has none. [4] (still open from round 1)

### cdd_guidance/practices/clean_engineering/rules/code_measure_limits.py

- code_measure_limits.py:40 `_LIMITS_KEPT_BY`, :70-75 `_limit` — put-logic-on-the-owning-resource — The rule finds Clean Engineering by the string `"clean_engineering"` through `context.practice.reading.graph.practices.opened.get(...)` and then asks `reading.chosen_tools.limit(measure)`. `limit_operation_parameters.py:34-39` `most_parameters` repeats the same lookup with its own literal. A renamed practice key would make both answer `None`, and every measured limit would then pass without a word. The guardrails say to hold the reference and never look it up by name. [3]

### cdd_guidance/practices/clean_engineering/rules/limit_operation_parameters.py

- limit_operation_parameters.py:18-21, :61-68 `_parameter_count_exempt` — eliminate-duplication — The factory-name rule is a second copy of `operation_checks.py:53-63` / :334-341 `_allows_static_factory_operation`, and the comment at :18 ("align with prefer-instance-operations") says so. The two copies already disagree. `_LOAD_FACTORY` is `^load(?:[A-Z].*)?$` here and `^load(?:[A-Z_].*)?$` there, so `load_record` is a factory to `prefer-instance-operations` but counted here. `now` and `every` are exempt there and not here. [2]

### cdd_guidance/practices/clean_engineering/rules/depend_toward_stability.py

- depend_toward_stability.py:44 `_importers` — eliminate-duplication — The rule counts the importers of every module again from `IMPORTED_MODULES_FACT`. The reading already records them on each module as `IMPORTING_MODULES_FACT` (`reading/folder_facts.py:104`), and the `limit-modules-importing` measure reads that fact (`measures/measuring_tools.py:271`). [2]

### cdd_guidance/practices/clean_engineering/rules/code_use.py

- code_use.py:56 `CodeUse`, :62 — put-logic-on-the-owning-resource — The docstring (:4) says each rule "makes it once", but each of the six rules builds its own `CodeUse` (`code_use_rules.py:37, :53, :68, :94, :109, :131`). Each `CodeUse` builds a `CodeReach`, which reads the config and scans every code file for registry calls again (`code_reach.py:266-274`). TDD builds a seventh one (`tdd/graph_overlay.py:152`). This use analysis belongs to Clean Engineering's reading, as a part the reading builds once and keeps. [3]
- code_use.py:211 `_subclasses`, :306 `_family`, :236 `_extends_code_outside`, :246 `_outside_bases`, :334 `_owner` — eliminate-duplication — `code_reach.py` walks the same class hierarchy of the same graph a second time: `:229 _owner` (the same "properties" edge index, else the direct parent), `:178 _extending`, `:255 _base_chain`, and `:222 _outside_bases_named` (both trim base names with `rsplit(".", 1)[-1]`). The two walkers have already drifted apart. `code_use.py:31` follows `realizes` (protocols), while `code_reach.py` follows only `baseClass`, so an operation reached through a protocol is a use to one and not to the other. [2]
- code_use.py:349 `_is_production` — eliminate-duplication — "Production code" is decided four ways:
  - here, a file that is not test or example code, unless production imports it;
  - `ProductionCodeRule.check` (`production_code_rule.py:31`) and `CleanEngineering.is_production_code` (`clean_engineering.py:60`), a file that is not test code;
  - `CodeUnderTest._is_production_code` (`tdd/graph_overlay.py:172`), a code file that is not test or example code.

  So a test double such as `mock_repo.py` is production code to the per-node rules and to the session output, but not to the unused-code rules or to TDD. [2]
- code_use.py:44 `_names_examples` — eliminate-duplication — It works out which files are examples again from `TestFileName`'s parts (`words[-1:] == ["examples"]`, `"examples" in roles`), beside `TestFileName.is_example` (`source_code/test_files.py:97`) and `ProjectTestCode.is_example_code`. The `source_code` card makes test-file naming one rule. [2]
- code_use.py:37 `_FOLDER_TYPES`, :39 `_CONSTRUCTOR` — eliminate-duplication — These are private copies of `reading/folder_facts.py:17` `FOLDER_TYPES` (which `coupling_rules.py`, `module_graph_rules.py` and `practice_wide_rules.py` now import) and of `model/source_facts.py:41` `CONSTRUCTOR_NAMES`. `tdd/graph_overlay.py:26` `_SCRIPT_CONSTRUCTOR` is a third copy of the constructor name. [2] (still open from round 1)
- code_use.py:345 `_folder_of` — delete-unused-operations — No caller in the repository: a search for `_folder_of` finds only its definition. [3]
- code_use.py:141-155 `_importers`, :355-365 `_example_files_production_imports` — hide-inner-details — Both walk `imported_classes_by_file` over every Module and Package. They read the saved import one way by position (`reference[1]`, :154) and another way as `ClassReference(*reference)` (:364). `_importers` also reaches `self._context.practice.reading.in_graph.root.get_fact("imported_classes_outside")` (:148). The shape of the reading's fact is spread across the rule. [3]

### cdd_guidance/practices/clean_engineering/rules/coupling_rules.py

- coupling_rules.py:84 `_second_registries` — hide-inner-details — The rule unpacks a seven-field list from a folder fact by position (`file, name, count, other_file, other_name, other_count, shared`). `cross_file_rules.py:47, :81, :89` and `operation_checks.py:311, :403` unpack facts the same way, with sentinel defaults such as `or ["", 0, []]`. The reading and the rules share record shapes that no type names, so a change to one must be made in two files and nothing checks it. [3]

### cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py

- module_graph_rules.py:49 `_python_class_folder` — prefer-class-operations — This is still a module function that takes the node it is about. Three rule classes call it, and it decides the language by `.endswith(".py")`. [3] (still open from round 1)

### cdd_guidance/practices/clean_engineering/rules/operation_checks.py

- operation_checks.py:126 `operation_label` — prefer-class-operations — This is still a free function that takes the node, imported by `limit_operation_parameters.py:13` and `refuse_unreadable_input.py:10`. `OperationMeasureRule` (:110), which all three rules extend, is its owner. [3] (still open from round 1)
- operation_checks.py:25 `VAGUE_NAMES`, :70 `_VAGUE_PARAMETER_NAMES`, :72 `GENERIC_NAMES`, :226 — eliminate-duplication — These are three overlapping word lists: `info`, `thing`, `stuff`, `misc` and `obj` are in two of them, and `options` is in two. `AvoidVagueParameterNames` judges both `Parameter` and `Operation` nodes, with one list for a parameter (:230) and two for an operation (:235). A parameter named `options` is therefore reported twice, once on itself and once on its operation, while `opts` and `config` are reported once. [2]
- operation_checks.py:174-177 `SimplifyControlFlow.measure` — eliminate-duplication — The route-registrar exemption is written twice and matches differently. Here it is `startswith("register") and endswith("Route")` plus `create…Routes`. In `operation_semantics.py:31, :43-45` it is `^register\w+Routes?$` plus `create…Routes`. Neither rule's text states the exemption. [2]

### cdd_guidance/practices/clean_engineering/rules/operation_semantics.py

- operation_semantics.py:17-28 `_LIFECYCLE_WITH_VALIDATION` — put-logic-on-the-owning-resource — A rule the practice ships to every project hard-codes the operation names of one client project (`postOnboarding`, `importStoredPortabilities`, `exportStoredPortabilities`) and quietly exempts them. `operation_checks.py:266-269` does the same for `text`/`rawField` and `asyncRoute`. A project's own choices belong in its `.context/config.json`, where `code_reach` and `test_code` already keep them. [4]

### cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py

- practice_wide_rules.py:18 `_MAX_SIBLING_IMPORTS`, :20 `_MIN_MEASURED_METHODS` — eliminate-duplication — These numbers are kept outside `rule_numbers.py`. The text of `low-coupling` says only "keep sibling imports few" (`clean_engineering.md:151`), so the check holds a limit of 8 that no rule states. `deep-module`'s text types "fewer than 10 methods" by hand (`clean_engineering.md:136`), the very drift `numbers_in_one_place_spec.py` was written to prevent. [2]

### cdd_guidance/practices/clean_engineering/rules/typed_and_comments.py

- typed_and_comments.py:20 `_INVALID_PARAM_NAME` — use-intention-revealing-names — The pattern matches a valid name, and :44 returns early when the name does *not* match it, so the name says the opposite of what the code does. The same regex is written inline at `operation_checks.py:261`. The check at :51 adds only case variants of `_VAGUE_TYPES` (:17) and gives the same message as :49. [4]

### cdd_guidance/practices/clean_engineering/rules/production_code_rule.py

- production_code_rule.py:3, :23 — no-legacy-api-after-refactor — The docstrings still point readers to "the model's `production_code` module" and to `model/compared_facts.py`. Both have moved, to `source_code/test_files.py` (*ProjectTestCode*) and to `reading/compared_facts.py`. Guardrail 3 says the change that moves a name also updates its docs. [1]

### cdd_guidance/practices/clean_engineering/rules/rule_examples.py

- rule_examples.py:60, :79, :90, :111 and code_use_examples.py:182 — eliminate-duplication — Clean Engineering's spec support has five ways of making a pair (`files_rule_pair`, `python_example_pair`, `module_example_pair`, `measured_example_pair`, `example_pair`) and no `EXAMPLE_PAIRS` table. The four other practices and TDD each expose one, and `template_checks.py:132` reads it. So `templates_and_rules_heavy_spec.py:144` runs Clean Engineering only through "templates and rules" and not through "a practice's checked rules". Its checked graph rules are the only ones the shared check ("every checked rule has a failing and a repaired example") skips. [2]

### cdd_guidance/practices/source_code/__init__.py

- __init__.py:21-23 — low-coupling — The package now has a seam, but callers still name internal files. `CodeReach` is used by two other modules (`clean_engineering/rules/code_use.py:18`, `tdd/graph_overlay.py:12`) and appears on neither the seam nor the card. `OWN_RECEIVERS`, `SAFE_NUMBERS`, `STRING_LITERAL`, `WIRED_PEER_FIELDS`, `OWN_CLASS_RECEIVERS` and `is_dunder` are imported from `source_text.py` (`clean_engineering/model/operation_metrics.py:14`). `ClassReference` and `TestFileName` are on the seam, yet `code_use.py:19-20` still imports them from their files. [1] (still open from round 1)

### cdd_guidance/practices/source_code/bracket_structure.py

- bracket_structure.py:13 `closing_bracket` — eliminate-duplication — `clean_engineering/reading/function_text.py:12` `closing_bracket` is a second bracket matcher, and it skips quoted strings where this one does not. `reading/code_file.py` calls that one six times (:332, :1103, :1113, :1161, :1251, :1671). `c_family_parse.py:390`, `call_arguments.py:24`, `code_body.py:275` and `source_text.py:383` call this one. A `}` inside a string therefore closes a block for one reader and not for the other. The card's purpose is "a brace is parsed by one reader". [2]

### cdd_guidance/practices/source_code/call_graph.py

- call_graph.py:35 `CallGraph(list)`, :22 `kind: str  # "call" | "out" | "in"` — hide-inner-details — Subclassing `list` makes the storage the interface: `append` and `insert` bypass `add_line`. The entry kind is a bare string, and the arrows are spelled twice, once as the read patterns (:13-14) and once as the write map (:57). `parse_arrow_line` (:26) is also called outside the graph by `bdd/model/bdd_model.py:214, :226` and `clean_engineering/model/markdown/class_card.py:245`, so arrow lines are read into three shapes. [3]

### cdd_guidance/practices/source_code/code_body.py

- code_body.py:60 `CodeLanguage.suffixes` — eliminate-duplication — The field is described as "the one table every reader of code asks", but the file endings are typed again in:
  - `code_reach.py:21` `_CODE_SUFFIXES` (adds `.mjs`)
  - `script_imports.py:38` `_IMPORTED_FILE_ENDINGS`
  - this file's own `_module_path` regex (:173, with `mjs`)
  - `tdd/tiers.py:25` `TEST_CODE_SUFFIXES`
  - `rules/operation_checks.py:62` `_SCRIPT_SUFFIXES`, and `.endswith(".py")` at :144
  - `rules/module_graph_rules.py:51`
  - `script_imports.py:85`
  - `reading/code_file.py:125`

  `JAVASCRIPT` (:450) has no `.mjs`, which `code_reach` scans and `code_file` reads as script. [2]
- code_body.py:238 `CodeBody.from_written` — delete-unused-operations — The only callers are `clean_engineering/model/code_render_spec.py:248-249`. [3] (still open from round 1)
- code_body.py:295 `WrittenBlock` — hide-inner-details — The block exposes `lead`, `heading`, `inside`, `closing` and `close`, and three callers put it back together from them in the same order (`stories/model/story_writing.py:201, :278`, `bdd/model/code_spec_model.py:123`). The block should write itself. `close` (:306, the closing lines) and `closing` (:325, the lines after the last child) are two near-identical names for neighbouring things. [3]

### cdd_guidance/practices/source_code/code_reach.py

- code_reach.py:80 `CodeReach` — high-cohesion — The module card says "Code here reads text; it knows no practice's nodes and holds no rule". `CodeReach` walks Clean Engineering's class graph instead: `declared.practice.reading.in_graph.edge_index.of("baseClass")` (:183), the `"properties"` edges (:234), `owner.type != "Module"` (:153) and `member.type != "Property"` (:231). It is the other half of `code_use.py`, which is why the two duplicate each other's hierarchy walks. [1]
- code_reach.py:103 `ways` — delete-unused-operations — The only reader is `code_reach_spec.py:205`. [3]

### cdd_guidance/practices/source_code/script_imports.py

- script_imports.py:127 `PythonImports`, :172 `ScriptImportClauses` — eliminate-duplication — The two classes still share no type, and :85 chooses between them by `file.suffix == ".py"`. The same file also reads script imports with a second set of patterns for `targets` (`_SCRIPT_IMPORT` :13 and the type-only handling at :16-17) beside `_JS_FROM`/`_JS_CLAUSE` (:24-25). As a result, a type-only import is dropped from `targets` but kept as a class reference (`_clause` strips `type `, :195). [2] (still open from round 1)
- script_imports.py:41 `imported_files` — eliminate-duplication — `stories/model/story_recording.py:75` defines another `imported_files(file, imported_modules)` that resolves an import to its candidate files by different rules. That makes two functions with one name for one job, and a fix to import resolution has to be made twice. [2]
- script_imports.py:224-230 `_aliases_named_in` — refuse-unreadable-input — A `tsconfig.json` that does not parse (`ValueError`, `UnicodeDecodeError`) answers `()`. Every alias import in that project then reads as an outside package, and its classes as never imported, with no failure that names the file. The `lru_cache(maxsize=None)` on this module function also keeps the first answer for the whole life of the cdd server, so an edited tsconfig is never read again. [3]
- script_imports.py:75 `ScriptImports` — use-consistent-naming — Everywhere else in this file "script" means TypeScript or JavaScript (`_SCRIPT_IMPORT`, `ScriptImportClauses`, `path_aliases` "a script file"), but `ScriptImports` reads Python files too (:85). [4]

### cdd_guidance/practices/source_code/source_text.py

- source_text.py:239 `mixes_io_and_domain`, :246 `mutates_without_record`, :252 `has_prose_comment`, :268 `prototype_swap`, :305 `SpanFailures`, :347 `SpanCollaborators` — high-cohesion — The card's constraint says a measure is written here only when more than one practice reads it, and that Clean Engineering's own measures stay in `model/operation_metrics.py`. These are read only by Clean Engineering (`model/source_facts.py`, `model/operation.py`, `model/code_class_model.py`, `model/operation_metrics.py`). The patterns use only `hits` and `line_of`. [1]

### cdd_guidance/practices/source_code/test_files.py

- test_files.py:135 `is_example_code` — use-intention-revealing-names — It answers "test code *or* example code" under a name that says "example". Callers read `not is_example_code` as "production" (`code_use.py:151, :353, :363`, `tdd/graph_overlay.py:174`, `reading/module_exposure.py:53`). `tdd/graph_overlay.py:151` uses it as "test code", so every operation of a test double such as `mock_repo.py` counts as reached by a test. [4]
- test_files.py:164 `_declares_tests` — prefer-class-operations — A module function with one caller, `ProjectTestCode._holds_tests` (:157), which is its owner. [3]

### cdd_guidance/practices/tdd/tdd.py

- tdd.py:19 `_TIER_RECORD_RULE`, :43 — put-logic-on-the-owning-resource — It finds a rule by matching its slug string among `rules_for(fidelity)`, and `module_tiers.py:116` types the slug again. The guardrails say to hold the reference, not to look it up by name. [3]
- tdd.py:32-33 imports inside `markdown_values` — one-way-deps — `tdd.py` already imports `graph_overlay.py` at the top (:11), and that file imports `Bdd`, `CleanEngineering` and `Stories` at the top too, which are the same modules `rules/__init__.py` imports. Moving the import to the top avoids no cycle, so hiding it inside the function serves no purpose. [1]

### cdd_guidance/practices/tdd/tiers.py

- tiers.py:42-86 `tier_of`, `recorded_tier_of`, `test_tool_of`, `is_code_file`, `real_resources_in`, `stubs_in` — eliminate-duplication — This is a file of free functions about what a test file's name says, the job `TestFileName` already holds (`source_code/test_files.py:51`). The `\.story\.(\w+)\.` pattern is typed twice (:45, :56). The two readers of test-file names already disagree: `TestFileName` calls `cart.test.py` and `checkout.e2e.ts` specs (`_SPEC_ROLES`), but `tier_of` gives them no tier, because `TIER_SUFFIXES` (:8-14) requires `.e2e.spec.ts`. Such files are never recorded and never checked by `unit-tier-fakes-every-boundary`. [2]

### cdd_guidance/practices/tdd/graph_overlay.py

- graph_overlay.py:35 `TEST_FILE_NODES`, rules/__init__.py:24 — eliminate-duplication — The pairs (BDD, `Spec`) and (Stories, `Story`) are still listed twice. [2] (still open from round 1)
- graph_overlay.py:22 `_EMPTY_BODY`, :168 — eliminate-duplication — This is a third definition of "a body nobody has written yet", beside `source_code/code_body.py:24` `_PLACEHOLDERS` with `CodeLanguage.is_unfinished` (:69), and beside the code fidelity that `production_code_rule.py:40` asks for through `node.is_read_at(CODE_FIDELITY)`. Here that fidelity is typed as the string `"code"`. `_EMPTY_BODY` accepts `raise NotImplementedError` but not `throw new Error("not implemented")`, so an unwritten TypeScript operation is asked for a test. [2]
- graph_overlay.py:58-67 `_read_test_code`, :69-74 `_record` — put-logic-on-the-owning-resource — The overlay reads each spec and story test file from disk again, though BDD's and Stories' readings already read it, and it lists every test file again with `graph.scope.source_files`. Guardrail 1 says one owner per file. [3]

### cdd_guidance/practices/tdd/module_tiers.py

- module_tiers.py:15 `_MODULE_CARD`, :83 `_module_of` — eliminate-duplication — It finds a folder's module by walking up the disk for `.context/module-context.md`. That is a further definition of "the module a folder is in", beside Clean Engineering's `model/module_context_files.py:18` `_CARD_NAME` and `reading/folder_facts.py` (*ModuleImports*: "a module is a folder that owns a module card"), and `harness/catalog_generator/catalog_generator.py:450` walks it again. [1]


### cdd_guidance/practices/agent_bdd/agent_bdd_common.py

- agent_bdd_common.py:182 `JudgeResult._embedded_judge_verdicts` — hold-state-on-the-object-not-in-parameters — It sets `self._judge_text` and `self._decoder` (:182-183) to carry one call's text into `_next_verdict_start` and `_decode_embedded_verdict`, but `JudgeResult` is `@dataclass(frozen=True)` (:108), so the first assignment raises `FrozenInstanceError` (checked: a frozen dataclass refuses any attribute set from a method). Every judge answer whose verdict is not alone on a line (`_verdict_from_json_lines` returns `None`, :132-135), such as a verdict wrapped in prose, crashes `AgentBlock._verdict` (`agent_block.py:137`) instead of being parsed or reported as `ERROR`. No spec calls `from_stdout` (grep: only `agent_block.py:137`). The text should be a parameter, or the parser its own object. [3]
- agent_bdd_common.py:123 `JudgeResult.from_stdout` — put-logic-on-the-owning-resource — Still makes a throwaway `cls(verdict="ERROR", reason="")` to call the parsing operations (:131-206) that read none of its fields; the parser is a different thing from the result it produces, and the item above is what that confusion now costs. [3] (still open from round 1)
- agent_bdd_common.py:23 `_YAML = YamlFence()` — use-explicit-dependencies — An object made at import and shared by `RunResponse.from_cli_output` (:260) and `ToolsRunYaml` (:486, :490). [3] (still open from round 1)
- agent_bdd_common.py:297-301 `AgentSession.__post_init__` — use-explicit-dependencies — Still builds two `CursorCli` objects itself, while `from_workspace` (:315) is handed the `cli` the spec chose and uses it only to create the chat (:325); runs then go through the session's own (:335, and `agent_cli_bdd.py:341` `session.streaming_cli`). [3] (still open from round 1)
- agent_bdd_common.py (682 lines, 14 classes) — high-cohesion — Results, the judge's parser, the YAML request reader, the chat session, the toolset request, its run, and the deadline still share one file named "common". [4] (still open from round 1)
- agent_bdd_common.py:375-408 `AgentSession._narrative_from_cli_stdout`, `_assistant_text` — eliminate-duplication — Reads cursor-agent's JSON event stream (`type == "assistant"` text blocks, `type == "result"`) a second time beside `_StreamBuckets.collect_shell_capture`, `_collect_assistant_block`, `_collect_result` (`agent_cli_bdd.py:120-145, 192`); a change to the stream's event shape has to be made in both. [2]
- agent_bdd_common.py:272 `_CHAT_ID_RE` — delete-unused-operations — A compiled pattern nothing reads (repository-wide grep: only its definition). [3]
- agent_bdd_common.py:589-599 `ToolsetInvoke.response` / `invoked_tool`, :623-626 `ActionExpansion.response` / `expanded_action` — use-consistent-naming — Each class names one operation twice: `response()` only returns `invoked_tool()` or `expanded_action()`, and neither second name is called from anywhere else (grep). Two public names for one answer. [2]
- agent_bdd_common.py:451-476 `_toolset_block_from_prompt`, `_sanitize_yaml_body` — eliminate-duplication — Both stop at a line starting `IMPORTANT:` or `Return the complete` (:460, :471-474), each with its own copy of the test. [2]
- agent_bdd_common.py:267 `_ShellCapture` — hide-inner-details — Named private but imported by two other modules (`agent_block.py:30`, `agent_cli_bdd.py:18`) and exposed through `AgentBlock.last_shell_captures` and `session_shell_captures`, which specs read (`_examples/shell-captures.py:53`). It is a public type with a private name. [1]

### cdd_guidance/practices/agent_bdd/agent_block.py

- agent_block.py:50-51 `last_shell_captures`, `session_shell_captures` — put-logic-on-the-owning-resource — Declared on the base *AgentBlock* but filled only by the CLI block (`agent_cli_bdd.py:305-306`); the in-chat block always answers empty lists, so a spec that reads them passes against the chat agent while asserting on nothing. [3]

### cdd_guidance/practices/bdd/model/bdd_model.py

- bdd_model.py:31 `BddModel` — use-consistent-naming — The class is `BddModel`, its node type is `Spec` (:32), its graph node id `bdd:Spec:` (`graph_reading.py:128`); three words for one thing. [4] (still open from round 1)

### cdd_guidance/practices/bdd/model/code_spec_model.py

- code_spec_model.py:42 `KeptLines`, :28 `ChildBlock = Tuple[int, int, Callable…]` — use-intention-revealing-names — `KeptLines` translates a body written in another language to and from comments and reads a realization's call graph; `ChildBlock` is first line, last line, and a reader. Neither name says so. [4] (still open from round 1)
- code_spec_model.py:102 `CodeBddModel.render` sets `self._kept`; :278, :359 `parse_code` sets `self._lines` — hold-state-on-the-object-not-in-parameters — The previous file and the lines being read are written onto the format adapter for one call and read by `_render_body` (:135), `_render_inside` (:181), `_written` (:195), `_read_block` (:172), `_node` (:328) — the "field set on a shared object for one call" the rule names. The adapter is one object per format (`bdd.py:47-56`), so a render started from inside another render on the same adapter reads the wrong previous file. [3]

### cdd_guidance/practices/bdd/model/graph_reading.py

- graph_reading.py:99, :147 `clean: PracticeReading` — low-coupling — Still typed as the framework's base while used as Clean Engineering's reading: `.code_index` (:164, :172) and, in `graph_bdd_model.py:78, :119`, `.model_documents` and `.code_index` exist only on Clean Engineering's reading. [1] (still open from round 1)
- graph_reading.py:112 and :163 — hide-inner-details — A spec's imports are still flattened to lists (`[list(reference) …]`) to be saved and rebuilt as `ClassReference(*pair)`; how a `ClassReference` is stored is known in two practices. [3] (still open from round 1)
- graph_reading.py:21-22 — low-coupling — Imports Clean Engineering's reading internals `reading.node_evidence.NodeEvidence` and `reading.code_file.CodeFile, CodeSpan`; the module card (`bdd/.context/module-context.md`) names only "clean_engineering (class model)" as the dependency, and Clean Engineering's seam terms name neither. [1]
- graph_reading.py:167 `_SpecLinks` — shape-classes-around-resources — Made from `ObservationLinks` by copying its `graph`, `clean.code_index`, `driven`, and `bdd.test_code` into four fields (:171-174), used for one `link()` and thrown away (:164); a step of one read, as round 1 found of Clean Engineering's `ClassLinks` and `CallerBody`. [3]
- graph_reading.py:179-199 `_SpecLinks.link` — keep-operations-single-responsibility — One loop aligns describes, finds enclosing setups, builds the code before each observation, resolves tool operations and calls twice (own body, then nearest setup), merges the two lists, and writes both edges; the nearest-setup rule (:192-196) is calculation inside orchestration. [3]
- graph_reading.py:237 and graph_bdd_model.py:119 `get_fact("owner")` compared with a class name — hold-state-on-the-object-not-in-parameters — A member's class is found by comparing its `owner` fact string (`Name(...).kebab == toolset`, `== owner`) where Clean Engineering's `owns` edge already joins the member to its class node; round 1 counted this comparison in 20 places. [3]
- graph_reading.py:281 `_without_teardown`, :329 `_bracket_balance` — prefer-class-operations — Module functions each used by one class (`_SpecLinks._setup_code` :267; `_Teardown` :308, :323). [3]
- graph_reading.py:37 `_QUOTED` — eliminate-duplication — A second "empty every string literal" pattern in BDD beside `spec_source.py:16` `_STRING_LITERAL`; they disagree on triple-quoted strings (only `_STRING_LITERAL` handles them), so a spec's docstring counts as code in one reading and not the other. [2]

### cdd_guidance/practices/bdd/model/graph_bdd_model.py

- graph_bdd_model.py:31 `Member = tuple[str, str]` — put-logic-on-the-owning-resource — A member is still carried as (owner name, member name) and looked up again by both strings (:115-119) where the graph holds the member's node. [3] (still open from round 1)
- graph_bdd_model.py:21 `parameters_of` — low-coupling — A format adapter imports Clean Engineering's `measures.read_facts`, an internal of the measures package, to read a member's parameters. [1]

### cdd_guidance/practices/bdd/model/nodes.py

- nodes.py:72 `BehaviorNode.children_blocks` — hide-inner-details — The base still reads `contexts` and `observations` with `getattr` because only its subclass `DescribeBlock` declares them (:80-82); `bdd_model.py:92-93` and `:146` do the same. [3] (still open from round 1)
- nodes.py:24 `private_probe_in_text` — shape-classes-around-resources — A module function that answers a `{"line", "kind"}` dict, saved as a fact on two node types (`BehaviorNode.load_span_facts` :60, `BddModel.load_source_facts` `bdd_model.py:83`) and read back by key in `rules/observable_behavior.py:23`; a data bag and a doer. [3] (still open from round 1)

### cdd_guidance/practices/bdd/model/spec_reshape.py

- spec_reshape.py:33 `SpecBlock`, :53 `SpecOutline` — do-not-invent-parallel-object-models — Still a second reading of a spec file into its own block tree beside the model's `Description`, `Context`, `Observation`, which hold `line`, `end_line`, and `written`; `_python_name` (:94-100) repeats `PythonBddModel._block_kind` (`code_spec_model.py:314-322`) and `_script_blocks` walks the same `DescribeCalls` the model reads. [2] (still open from round 1)
- spec_reshape.py:57, :117 `python_kinds`, `script_calls` — hold-state-on-the-object-not-in-parameters — The constructors are still told the language three ways: `language`, a dict of mamba block names, and a callable; which one is `None` picks the parser (:61). The format adapter that makes it (`code_spec_model.py:285`, :368) already is the language. [3] (still open from round 1)
- spec_reshape.py:29 `ScriptCalls = Callable[[str], object]` — use-typed-signatures — Typed as answering `object`, but `_script_blocks` (:102) needs a `DescribeCalls` and reads `.roots`; the alias hides the one type that fits. [4]

### cdd_guidance/practices/bdd/model/spec_source.py

- spec_source.py:19 `has_signature_marker`, :25 `is_developed`, :37 `reads_like_code` — prefer-class-operations — Still a file of functions that answer questions about a spec's text; `BddModel.load_source_facts` (`bdd_model.py:78-79`) copies the answers onto itself, and a rule (`rules/spec_rules.py:10, :33`) imports a model-file function to judge a node's name. [3] (still open from round 1)

### cdd_guidance/practices/bdd/rules/shared_describe_subject.py

- shared_describe_subject.py:19 `_longest_shared_word_prefix`, :41 `branched_top_level_describes` — prefer-class-operations — Two module functions with one caller, `SharedDescribeSubject.check` (:63) (grep: no other caller, specs included). [3]

### cdd_guidance/practices/ddd/ddd.py

- ddd.py:23-37 `_FORMATS` — one-way-deps — Still seven adapters named by module-path and class-name strings, three of them Clean Engineering's code models; a rename breaks it at run time with nothing to find it by. [1] (still open from round 1)
- ddd.py:91-96 `_holds_a_domain`, :21 `_CODE_SUFFIXES` — eliminate-duplication — The docstring says it decides "as DDD's graph reading decides one", but it re-decides by reading every file of the folder with a regex for decorators (`carries_a_stereotype`), while the reading decides from the stereotypes Clean Engineering parsed (`reading/graph_reading.py:242`, :436); and the code suffixes are hard-coded beside `source_code.CODE_LANGUAGES`. The two answers differ for a stereotype written in a docstring or a `<<Mark>>` comment. [2]

### cdd_guidance/practices/ddd/model/building_blocks.py

- building_blocks.py:23 `plain_name`, :29 `member_name` — eliminate-duplication — Each strips `**` and backticks, as `stereotypes.py:55` `plain_class_name` does with more steps; and `clean_engineering/model/diagram/class_view.py:322` defines another `plain_class_name` with a different body. Two functions of one name and two more of the same job: a name read by the markdown reader and by the reading can come out different. [2]
- building_blocks.py:87-100 `DomainClass.named`, `from_heading`, `from_code` — prefer-instance-operations — Three `@staticmethod`s; `named` is not an exempt creation name, and each is called through the class (:98, :104; `markdown/class_cards.py:34, :41`; `sketch/sketch_nodes.py:52, :60`). [3]
- building_blocks.py:63, :79, :196, :238 `**kwargs` — use-typed-signatures — The constructors of `InvariantObject`, `DomainClass`, `Entity`, `DomainEvent` read `type_hint`, `intent`, `description` out of `**kwargs` (`kwargs.get(...)`), so a misspelt keyword is dropped silently and the signature does not say what a block is made with. [4]
- building_blocks.py:46 `called_class` — eliminate-duplication — "The class a call names" is spelled inline again at `nodes.py:363` (`callee.partition(".")[0].strip()`) and `reading/graph_reading.py:776` (`.partition(".")[0].partition("(")[0].strip()`), each with a different rule for a lower-case receiver. [2]

### cdd_guidance/practices/ddd/model/ddd_channel.feature.py

- ddd_channel.feature.py:24 `_events` — eliminate-duplication — Repeats `Aggregate.events` (`nodes.py:264-268`) word for word. The file is a mamba spec that no tier collects (its name matches no `*_spec.py` pattern), whose own run command names a path that does not exist (:6, `practices/ddd/model/...` without `cdd_guidance/`), kept in `model/` among the production files; no script or document runs it (grep `ddd_channel`). [2]

### cdd_guidance/practices/ddd/model/drawio/drawio_bounded_context_map.py, whiteboard/whiteboard_bounded_context_map.py

- drawio_bounded_context_map.py:197 `DrawIOBoundedContextMap`, whiteboard_bounded_context_map.py:70 — use-intention-revealing-names — Each is still a bounded-context map and a Clean Engineering class model at once and calls the second parent through its class (`DrawIOCleanEngineeringModel.render(self, self, written)` :210, `.parse(self, text)` :223; whiteboard :82, :95). The shape leaks: `drawn/drawn_map.py:97` calls `super().modules_title`, which only the Clean Engineering sibling defines, and `ddd_formats.py:29` must ask `not isinstance(target, BoundedContextMap)` to tell a code model from a map. [4] (still open from round 1)
- drawio_bounded_context_map.py:23-33, whiteboard_bounded_context_map.py:16-22 — low-coupling — Imports of Clean Engineering's diagram and format internals, now seven modules for draw.io (`diagram.class_layout`, `diagram.class_view`, `diagram.diagram_node`, `diagram.geometry`, `drawio.diagram_node`, `drawio.drawio_class_model`) and `ClassBoard`, `WhiteboardModule` for the whiteboard. [1] (still open from round 1)
- drawio_bounded_context_map.py:125, :145, :150 `self._writer.classes_by_cell`, `named_modules`, `cell_ids` — hide-inner-details — `AggregateViewPage` reads the private `_writer` field its Clean Engineering base `ClassViewPage` holds, and that writer's storage, from another practice's package. [1]
- drawio_bounded_context_map.py:168 `_bounds`, :176 `_round` — put-logic-on-the-owning-resource — Geometry of `Box` (the smallest box round several, a box grown by an inset) written as module functions; `clean_engineering/model/whiteboard/whiteboard_class_model.py:447, :470` computes the same bounds inline again. [3]
- drawio_bounded_context_map.py:68-165 `_AggregateCards`, `_ContextCards`, `AggregateViewPage` — eliminate-duplication — About 100 lines lay out the aggregate view's nested containers for draw.io, while the whiteboard draws the same view by handing groups to Clean Engineering's `ClassBoard` (`page_groups`, `page_title`, whiteboard :55-67). The grouping of modules by their context labels is written twice (`_modules_by_context` :142 and whiteboard `page_groups` :55). [2]

### cdd_guidance/practices/ddd/model/drawn/drawn_map.py

- drawn_map.py:21 `MapCell` — use-explicit-dependencies — A mixin that reads `self.name`, `seam_terms`, `dependencies`, `dependency_labels`, and `external_deps()` (:43, :63-76), none of which it declares; they exist only when a format joins it with a Clean Engineering module class (`DrawIOContextCell(ContextCell, DrawIOModule)`), and `read_drawing` has to pick cells out with `isinstance(module, MapCell)` (:132). [3]
- drawn_map.py:36, :53 `ContextCell.drawing`, `AggregateCell.drawing` — prefer-instance-operations — `@classmethod`s outside the exempt creation names. [3]

### cdd_guidance/practices/ddd/model/markdown/class_cards.py

- class_cards.py:30 `CardSection.read` — prefer-instance-operations — A `@staticmethod` named `read`, which the rule does not exempt; round 1's five static methods on `ClassCard` are down to this one. [3] (still open from round 1)

### cdd_guidance/practices/ddd/model/markdown/nodes.py

- nodes.py:222 `"## domain driven design:"`, :250 `"# Bounded Context Map\n\n"` — one-way-deps — The markdown format recognises a sketch by the sketch's own section heading, a literal copied from `sketch/sketch_ddd_model.py:22` and the lens titles (:24), and strips its own title by literal; a change to the sketch's heading silently stops markdown from wrapping a sketch's document. [1]

### cdd_guidance/practices/ddd/model/nodes.py

- nodes.py:172 `Aggregate(DomainNode, Module)`, :534 `BoundedContext(DomainNode, Module)`; building_blocks.py:58 `InvariantObject(DomainNode, Property)`, :233 `DomainEvent(DomainNode, Property)` — use-intention-revealing-names — The domain terms are still made by inheriting Clean Engineering's drawing types: an event is appended to its root's `properties` (:219-221, :850) and filtered back out with `isinstance` (:268; `building_blocks.py:134`). [4] (still open from round 1)
- nodes.py:96-139 `Integration.read_arcs`, `targeting`, `kept_by` — prefer-instance-operations — Moved here from `MarkdownIntegration`; still class-level operations outside the exempt creation names (`from_aggregate` is exempt). [3] (still open from round 1)
- nodes.py:645 `BoundedContextMap` — abstraction-focus — The model's root still asks format questions of itself: `holds_document_words` (:676), `holds_classes_only` (:695), `has_class_cards` (:701), so one format can tell which other made the object (`markdown/nodes.py:223`, `drawn/drawn_map.py:103`). [4] (still open from round 1)
- nodes.py:581 `BoundedContext.context_file`, :503 `ContextFile.naming` — no-legacy-api-after-refactor — Still called only from specs (`model/context_file_spec.py`, `context_links_alignment_heavy_spec.py:86`); no production code writes a context's file through them. [3] (still open from round 1)
- nodes.py:172 `Aggregate` — keep-classes-single-responsibility — 29 methods: it reads its root from document lines (`open_root`), from a drawing (`take_drawn_root` :223, `drawn_members` :278, `_drawn_arrows` :196, `read_arrows_across` :351), and from a class model (`take_class`, `take_root_from_classes`); takes words from an earlier document (`take_words_from`); writes itself into a Clean Engineering module, folding repositories for drawings (`write_classes_into(draws_repository_in_root)` :382); and infers relationships. Each format's reading and writing lives on the domain node. [3]
- nodes.py:545-548 `BoundedContext.__init__` — use-typed-signatures — `name: str` may be a `Graph`, detected with `isinstance(name, Graph)`; the same switch is in `clean_engineering/model/base_class_model.py:521` and `ux/model/ux_map.py:90`. The signature lies about its first parameter. [4]
- nodes.py:61 `looks_like_operation`, :68 `_drawn_name` — eliminate-duplication — Module functions used only by `Aggregate` (:214, :287, :338-340); and `drawn_members` repeats `_drawn_name`'s `split(" - ", 1)[0].strip()` inline (:283-284). [2]
- nodes.py:574 `".context" / "bounded-context.md"` — eliminate-duplication — The marker path is written as a literal here while `reading/graph_reading.py:65` defines `BOUNDED_CONTEXT_MARKER` for it (and `clean_engineering/model/module_context_files.py:141` writes a third copy). [2]

### cdd_guidance/practices/ddd/model/stereotypes.py

- stereotypes.py:23 `KIND_OF_STEREOTYPE`, :35 `BUILDING_BLOCK_KINDS` — put-logic-on-the-owning-resource — A building block's kind is still a string (`"EntityRoot"`, `"Repository"`, …) compared throughout the reading and rules, while `Entity`, `ValueObject`, `Repository` classes exist; `building_blocks.py:274` keeps a dict from the kind string to the class. [3] (still open from round 1)
- stereotypes.py:55-102 — prefer-class-operations — Still six module functions (`plain_class_name`, `root_kept_by`, `kind_named_by`, `carries_a_stereotype`, `names_a_building_block`, `marks_another_system`) beside `TacticalClass`, which answers the same kind of question as an object. [3] (still open from round 1)
- stereotypes.py:94 `_named_as_a_building_block` vs :135 `TacticalClass.inferred_kind` — eliminate-duplication — The comment at :43-44 calls `_NAME_ENDINGS` "the one convention", but two readings of it disagree: `_named_as_a_building_block` takes every ending (`Service`, `Entity`, `Root`) plus `Specification` and `Factory`, while `inferred_kind` infers only a repository, a value object, or a root that has a repository. So `Ddd.claims` (`ddd.py:89`) claims a `CartService` file in a domain folder for DDD while the reading makes no building block of it. [2]

### cdd_guidance/practices/ddd/reading/graph_reading.py

- graph_reading.py:25-33 — low-coupling — Still imports Clean Engineering internals: `reading.code_read.CODE_FIDELITY, MODEL_FIDELITY`, `measures.read_facts.DESCRIBED_FACT`, `model.Relationship`, `reading.card_lines.CardLines`. (The `model` ↔ `model/markdown` cycle round 1 reported is gone: the reading now lives in `reading/`.) [1] (still open from round 1)
- graph_reading.py:79 `BuildingBlock` — do-not-invent-parallel-object-models — Still a second node for a class the graph already holds, joined by an `isA` edge (:468), answering `facts`, `has_fact`, and `get_fact` by falling through to the class (:146-158); it wraps a `TacticalClass`, which wraps an `OoadClass`. [2] (still open from round 1)
- graph_reading.py:344 `_WorkingCopyRead`, :642 `_DescribedDomain` — shape-classes-around-resources — Still two doers that read everything; the document, the aggregate, and name pairs are handed down through four- and five-parameter operations (`_link_sides` :530, `_AggregateBlocks.add` :569, `_read_block` :738, `_read_mapping` :803). [3] (still open from round 1)
- graph_reading.py:393, :266, :658 tuple types — use-typed-signatures — `list[tuple[str, BoundedContext, str]]` (:393, :404, :415, :510), `tuple[TacticalClass, str]` (:266, :426, :441, :458), and `tuple[str, str]` keys (:658-661, :738, :803) still stand for a marked context, a classified class, and an aggregate's place with no name. [4] (still open from round 1)
- graph_reading.py:603 `_DomainDocument` — eliminate-duplication — Still one object holding `CardLines` (:609), `MarkdownText` (:612), and its own `## ` scan (:617-618); and `markdown/nodes.py:257, :286` split a `## Name | owner` heading's title a fourth and fifth way. [2] (still open from round 1)
- graph_reading.py:203, :221-222 — hold-state-on-the-object-not-in-parameters — Clean Engineering's reading is still looked up as `practice.working_set.extended` then `graph.practices.loaded(type(extended))`, twice, and held nowhere (`reads_after` is now the class, so one of round 1's three ways is gone; BDD's `graph_reading.py:102` is the third). [3] (still open from round 1)
- graph_reading.py:558 `folder_of` — prefer-class-operations — Still a module function used eleven times in this file on `node.source.file`. [3] (still open from round 1)
- graph_reading.py:397-398, :452-453 `os.walk` with `skips_folder` — eliminate-duplication — The folder walk with `dirnames[:] = [... if not skips_folder(name)]` is still written twice here, beside Clean Engineering's copies; `harness/graph/skipped_folders.py` owns the walk for files only. [2] (still open from round 1)
- graph_reading.py:418-422, :462-464, :576-577, :714-716, :832-834 add, own, belong — eliminate-duplication — Each spells a node id with an f-string, then `in_graph.add`, `edges.link("owns"…)`, `edges.relate("belongsTo"…)`; a change to how a child joins its parent is still made in five places here and more in other practices. [2] (still open from round 1)
- graph_reading.py:262 `("Package", "Module")` folder lookup — eliminate-duplication — The folder-node dictionary from Clean Engineering's Module and Package nodes is rebuilt here with the pair as a literal again. [2] (still open from round 1)
- graph_reading.py:502-506 `_integrations_kept_by` — eliminate-duplication — A building block is a `BuildingBlock` when read now and a plain `Node` when restored from a saved graph, so its dependencies are read two ways: from the class (`block.ooad_class.dependencies`) or by re-parsing its source lines (`Relationship.read_lines`). The two readings can differ for one block depending on how the graph was opened. [2]
- graph_reading.py:236 `_DomainClasses._test_code` — use-explicit-dependencies — Takes the project's test code from Clean Engineering's reading (`classes.practice.reading.test_code`) although `DddReading` is itself `HoldsProjectTestCode` and `Ddd.is_production_code` asks DDD's own (`ddd.py:78`); two holders of one answer, and the DDD read silently has none without Clean Engineering. [3]

### cdd_guidance/practices/ddd/rules/tactical.py

- tactical.py:22 `_TACTICS = "tactics"` — eliminate-duplication — The same fidelity name is `TACTICS_FIDELITY` at `reading/graph_reading.py:46`; the rules and the reading that marks nodes at it hold two copies. [2]
- tactical.py:135 `FlaccidDataObject.check` — simplify-control-flow — Tests `node.type == "ValueObject"` although `node_types` (:132) is `("EntityRoot", "Entity")`; the branch can never be taken and suggests a value-object exemption the rule does not have. [3]

## Design proposals

1. **One class member, one constructor test.** Rename `InvariantHolder` to a member base (`ClassMember`) that declares `owner`, `keep_owner`, `callees`, `description`, `invariants`, `line`, and one `is_constructor` that reads its own owning class (name in `CONSTRUCTOR_NAMES` or equal to the class's); delete `CodeOperation.is_constructor_of`, `answers_to`'s copy, and `OoadClass.member_key`'s test. Ends: property.py:32 use-intention-revealing-names; operation.py:82 eliminate-duplication; source_facts.py:41 eliminate-duplication (with `reshaped_code.py:48` importing the constant); and the `self.parent` hand-back noted under code_class_model.py:251 hold-state-on-the-object-not-in-parameters.

2. **The type hint and the parameter line own their parsing.** A `TypeHint` value in `type_refs.py` (`classes_named`, `is_collection`, `is_optional`, `is_primitive`, `domain_classes`) and `Parameter.from_line(text)` used by `Operation.from_signature`, `take_parameters`, the brace reading and `python_type`. Ends: type_refs.py:37-79 put-logic-on-the-owning-resource; type_refs.py:45 eliminate-duplication; and lets `reading/` drop its four hint parsers.

3. **The JSON format owns its record.** Move every `as_record` onto the `Json*` classes beside `from_record`, write and read the same keys (adding callees, invariants, module path, class dependencies), set `property_type` and `operation_type` instead of overriding the loaders, delete the two unused `render`s. Ends: json_class_model.py:63 put-logic-on-the-owning-resource; :52-60 eliminate-duplication; :74/:99 delete-unused-operations.

4. **A parse is its own object.** Give each code format a parser object made per text (`BraceFileReading`, `PythonFileReading`) that holds the text, the class bodies found once, and the module it builds, and returns the module; the model keeps the returned module. Ends: c_family_parse.py:86 limit-class-methods; c_family_parse.py:86 keep-classes-single-responsibility; c_family_parse.py:512 hold-state-on-the-object-not-in-parameters; and, with the module keeping the file and root it was read from, base_class_model.py:489 hold-state-on-the-object-not-in-parameters.

5. **Body measures taken once, through one shape.** Give `MeasuredBody` the collaborator measures with one signature (the operation hands its own objects and members when it makes the body), take the statement count in `measure_body` as a fact, and export from `source_code` the one comment-and-string blanking the brace reader and the statement count both use. Ends: operation_metrics.py:247 eliminate-duplication; operation_metrics.py:66 put-logic-on-the-owning-resource; operation_metrics.py:14 low-coupling; c_family_parse.py:63-65 eliminate-duplication; and, if `line_count` is defined once there as the span, code_class_model.py:87 use-consistent-naming.

6. **Module facts declared on the module.** `ModuleContext.folder_facts` returns a typed `ModuleCardFacts` record that `Module` holds as one declared field, and `public_source_*` become declared fields. Ends: base_class_model.py:499-509 hide-inner-details; module_context_files.py:133 use-typed-signatures.

7. **Draw and read draw.io only through `harness/drawio`, with a class-diagram edge of its own.** Make `ClassDiagramPage` keep `DrawioCell`s and add a `ClassEdge` (over a `DrawioCell`) holding `kind`, `anchor(end)`, `segments`, `describe`; move the nine module functions of `drawio_page.py` onto it and onto a class card cell; write pages with `DrawioFile.add_page` / `DrawioPage.add`; parse with `DrawioFile.from_text` and let `UnreadableDrawio` reach the caller. Ends: `drawio_page.py:33-35` put-logic-on-the-owning-resource, `drawio_page.py:151-154` and `:109` eliminate-duplication, `drawio/diagram_node.py:44-57` eliminate-duplication and `:182-193` put-logic-on-the-owning-resource, `drawio_class_model.py:342-360` and `:121-132` eliminate-duplication, `:456-465` refuse-unreadable-input, `:550…` prefer-class-operations, `_drawio_base.py:20` eliminate-duplication (parse at :65), `leaf_nodes_not_in_horizontal_row_scanner.py:109` eliminate-duplication, `edges_do_not_cross_other_edges_scanner.py:161` eliminate-duplication.

8. **One drawing-side card text for a class, written and read once.** On `DiagramClass` (and `ImportedClass`): `fill_color`, `owning_module`, `operation_lines()` from `Operation.save`, `imported_property_lines()`, and `take_members(property_lines, operation_lines)`; on `DiagramClass` / the diagram channel, one `take_arrow_from(target, kind, words, unmarked)` that does the bases, dependencies, `take_arrow`, and `derive`, and on `DiagramModule` one `depend_on(name, label)`. Ends: `class_view.py:291-293`, `drawio/diagram_node.py:102-108`, `:134-140`, `drawio_class_model.py:302-303`, `:307-325`, `:363-366` (subtitle onto `ModulesView`), `whiteboard_class_model.py:208-212` — all eliminate-duplication.

9. **One geometry for diagrams.** Put `Point`, `Segment`, the one straightness tolerance, and one right-angle crossing test in `diagram/geometry.py` (or as operations of `harness/whiteboard` `Box` and a segment type), used by the router and every scanner. Ends: `geometry.py:6` and `:10` eliminate-duplication, `drawio_page.py:17` use-consistent-naming, and the `_right_angle_crossing` copy in `edges_do_not_cross_other_edges_scanner.py:184`.

10. **One reader of a class's members in any card or fence, beside one heading.** Split `ClassCard` into a reader made from lines and a writer made for no lines; make `SketchFence` read Clean Engineering's sketch so `SketchOoadClass.read_member`, `read_uml_member` and `_Nest` go, with one `-> call` / `// note` reading on `Operation` and `Property`; move DDD's `repo:`, `refs:` and map-line words into a DDD subclass of the fence; have the sketch read and write its headings with `ClassHeading`; read headings with `MarkdownText.headings()`. Ends: `class_card.py:66` and `:265` keep-classes-single-responsibility, `class_card.py:120-146` and `:228-248` eliminate-duplication, `:41-254` prefer-class-operations, `sketch_class_model.py:112-190` and `:86-89` eliminate-duplication, `:112` hold-state-on-the-object-not-in-parameters, `:415` prefer-instance-operations, `:395` prefer-class-operations, `markdown_class_model.py:54` eliminate-duplication.

11. **Layout scanners as practice rules.** Register each scanner through `ClassRegistry` (or as a `PracticeGraphRule` over drawio files), leave the command line and the file walk to the framework (`harness/graph/skipped_folders.py`), and drop the ten `__main__` blocks. Ends: `_drawio_base.py:25` keep-classes-single-responsibility, `:97` one-way-deps, `:81` and `:20` eliminate-duplication, `class_title_no_markdown_bold_scanner.py:21` eliminate-duplication (one title-check scanner with two tests).

12. **A node answers what kind of member it is and where it lives.** Give the graph node (or a `CodeMember` view like `ProductionClass`) `is_function`, `is_constructor`, `declaring_class` (by its `owns` edge), `language`, and `folder`, and one `keep_measure(name, value)` that decides attribute or fact. Ends: checked_measures.py:62 and :96 (hide-inner-details, eliminate-duplication), checked_measures.py:23 language (eliminate-duplication), graph_reading.py:177 (hold-state-on-the-object-not-in-parameters), class_facts.py:338 (eliminate-duplication), class_facts.py:262 (eliminate-duplication), code_read.py:492-568 parent folder (eliminate-duplication), code_measures.py:96 module-function holder (use-intention-revealing-names), graph_reading.py:295 (eliminate-duplication).

13. **One `ModuleOf` answer for paths.** One object built from the module nodes that answers `module_holding(path)` and `files_of(module)` (nested modules left out), with `is_under` as its method. Ends: checked_measures.py:66, checked_measures.py:119, read_facts.py:43 (both findings), code_read.py:262 (prefer-class-operations), statement_links.py:108, folder_facts.py:20 (prefer-class-operations).

14. **One `ClassLineage` and one base-name parse.** Resolve each class's bases once, after `ClassLinks`, as `baseClass` edges, and have `_ClassMembers`, `CopiedModels`, `ProductionClasses._derives`, `UnjoinedCalls.of_member`, and `is_protocol` read the edges instead of the `bases` strings. Ends: graph_reading.py:257 and :264 (eliminate-duplication), and the raw-bases comparisons in class_facts.py and production_classes.py.

15. **One `SourceFile` per file, read once.** The code read already reads each file; keep its text (decoded one way, `utf-8-sig`) on a `SourceFile` the index holds, with its imports (`ScriptImports`) and its language, and give it to `MemberAnswers`, `ReceiverCauses`, `StatementLinks`, `SecondRegistries`, `CopiedBlocks`, and the measuring tools. Ends: code_file.py:721 (eliminate-duplication), measuring_tools.py:197 (errors-out-of-existence), receiver_causes.py:43-46 (eliminate-duplication), checked_measures.py:23 (language), and the `"imported_classes_by_file"` literal at code_read.py:528 (provide-meaningful-context).

16. **Split `code_file.py` and share the text utilities.** Move `_HintTypes` with one `TypeHint` value (wrappers, collections, unions in one table shared with `ReceiverCauses`), `MemberAnswers`, and the span reader (`_SpanCalls` and its parts, with `SpanReach` adding through operations) into their own files, and use `source_code`'s `BracketStructure` and `split_top_level` instead of `function_text.closing_bracket` and `_top_level_parts`. Ends: code_file.py:1 (limit-module-file-lines), code_file.py:274 (put-logic-on-the-owning-resource), code_file.py:1681 (eliminate-duplication), code_file.py:646 and :252 (hide-inner-details), function_text.py:12 (prefer-class-operations), code_file.py:643 and :452 (eliminate-duplication).

17. **One resolver for names a file writes.** Have `ClassNamers` ask `CodeIndex.file(path).class_named(name)` (with the import-root fallback moved into `CodeFile`) and delete `ImportedClasses`; have `NodeEvidence.calls` ask `CodeFile.members_called_in`. Ends: imported_classes.py:17, module_exposure.py:117 (eliminate-duplication), node_evidence.py:39 (eliminate-duplication).

18. **Comment and body stripping in one place.** One `OperationBody` view of `body_text` (comments and docstrings stripped, tokens, statements, `has_body` from the model) for `NearCopies`, `SameBodies`, `PassThroughClasses._sole_forward`, and `CallLinks._is_abstract`. Ends: same_bodies.py:22 and call_links.py:187 (eliminate-duplication), call_links.py:34 `_CALL_MARKER` (eliminate-duplication).

19. **One answer to "is this file production code".** Give `ProjectTestCode` an `is_production(file)` (with the rule for example files production imports, now in `code_use.py`), rename `is_example_code` to say what it answers, and have every caller ask it. This ends code_use.py:349 and code_use.py:44 (eliminate-duplication), test_files.py:135 (use-intention-revealing-names), and the divergent copies at production_code_rule.py:31, clean_engineering.py:60 and graph_overlay.py:172 named in the first of them.

20. **One table of languages and their file endings.** Make `CodeLanguage.suffixes` complete (`.mjs`, and the module-file endings `script_imports` needs) and have every reader ask `CODE_LANGUAGES`. This ends code_body.py:60 (eliminate-duplication), module_graph_rules.py:49 (its `.py` test), script_imports.py:127 (choosing a reader by language, not by `.py`), tiers.py:42 (`TEST_CODE_SUFFIXES`), and the suffix lists at operation_checks.py:62, :144.

21. **The use analysis becomes a part of Clean Engineering's reading, built once.** Move `CodeReach` beside `CodeUse` in Clean Engineering's reading, leaving `WaysCodeIsReached` (the config section) in `source_code`. The reading holds one `CodeUse`, made from one `CodeReach` with one class-hierarchy walker that follows `realizes`, and TDD's `CodeUnderTest` asks it. This ends code_use.py:56 (put-logic-on-the-owning-resource), code_use.py:211/:306/:334 (eliminate-duplication), code_reach.py:80 (high-cohesion), code_reach.py:103 (delete-unused-operations), and the `CodeReach` part of __init__.py:21-23 (low-coupling).

22. **Rule numbers and project limits in one place, reached by reference.** Move `_CLASS_BUDGET`, `_MAX_SIBLING_IMPORTS` and `_MIN_MEASURED_METHODS` into `rule_numbers.py` with markers in the rule text. Give the rules one accessor for the project's limits on the reading they already hold, instead of a lookup by `"clean_engineering"`. Keep the factory-name rule in one place that both rules use. This ends class_rules.py:16 and practice_wide_rules.py:18 (eliminate-duplication), code_measure_limits.py:40 (put-logic-on-the-owning-resource), and limit_operation_parameters.py:18 (eliminate-duplication).

23. **Test-file naming in one type.** Put the tier a name gives (`tier_of`, `recorded_tier_of`, `is_code_file`) on `TestFileName`, so one reading of a test file's name answers both "is it a spec" and "which tier". Have the rules and the overlay share one list of the practices and node types test files are read into. This ends tiers.py:42 (eliminate-duplication), graph_overlay.py:35 (eliminate-duplication, still open), and test_files.py:164 (prefer-class-operations).

24. **Typed facts between the reading and the rules.** Replace the positional fact lists (`second_registries`, `dependencies_to_own`, `hands_down`, `taken_by_every_operation`, `verbs_for_one_target`, `same_body_elsewhere`, the saved class references) and the `operation_shapes` dicts with named tuples the reading defines and the rules import. This ends coupling_rules.py:84 and code_use.py:141 (hide-inner-details) and class_rules.py:29 (do-not-invent-parallel-object-models, still open).

25. **One parser for the agent's JSON event stream and the judge's verdict.** Move the stream reading into one reader that both `AgentSession.run` and `_StreamBuckets` use, and make the judge's parser its own object that returns a `JudgeResult`. Ends: `agent_bdd_common.py:182` hold-state (the frozen-dataclass crash), `agent_bdd_common.py:123` put-logic-on-the-owning-resource, `agent_bdd_common.py:375-408` eliminate-duplication, and part of `agent_bdd_common.py` high-cohesion.

26. **A building block is one node of one shape, joined to its class by its edges.** Drop `BuildingBlock`'s fall-through and the plain-`Node` restored form; give the block a typed kind (the `Entity`/`Repository` classes) instead of strings; find a member's class by its `owns` edge, not its `owner` string. Ends: `reading/graph_reading.py:79` do-not-invent-parallel-object-models, :502-506 eliminate-duplication, :266/:426 tuple types (part of use-typed-signatures), `stereotypes.py:23` put-logic-on-the-owning-resource, `bdd/model/graph_reading.py:237` and `graph_bdd_model.py:119` hold-state, `graph_bdd_model.py:31` put-logic-on-the-owning-resource.

27. **One naming convention and one name cleaner for DDD.** Make `TacticalClass` the only reader of `_NAME_ENDINGS` and of stereotypes (absorbing the six functions), have `Ddd.claims` ask the reading's answer for a folder, and keep one `plain_name` that strips marks. Ends: `stereotypes.py:94` eliminate-duplication, `stereotypes.py:55-102` prefer-class-operations, `ddd.py:91-96` eliminate-duplication, `building_blocks.py:23, :29` eliminate-duplication, `building_blocks.py:46` eliminate-duplication.

28. **The map and the class model stop being one object.** Give each drawn format a map that holds a Clean Engineering model (composition) instead of inheriting it, and let the map write into and read from that model; the format questions on `BoundedContextMap` and the drawing state on `Aggregate` then move to the format that needs them. Ends: `drawio_bounded_context_map.py:197`/whiteboard :70 use-intention-revealing-names, `drawn_map.py:21` use-explicit-dependencies, `nodes.py:645` abstraction-focus, `nodes.py:172` keep-classes-single-responsibility, and makes `drawio_bounded_context_map.py:125` hide-inner-details avoidable.

29. **BDD reads Clean Engineering through a named seam.** Type `clean_engineering_reading` as Clean Engineering's reading, have it offer the member lookup, parameters, and stored imports BDD needs, and stop flattening `ClassReference`. Ends: `bdd/model/graph_reading.py:99` low-coupling, :21-22 low-coupling, :112/:163 hide-inner-details, `graph_bdd_model.py:21` low-coupling; together with round 1's proposal 7 it would also end `reading/graph_reading.py:25-33` low-coupling.

30. **A spec file is read once, into the model.** Let `SpecReshape` work on the `Description`/`Context`/`Observation` tree the language model already reads (with their `line`, `end_line`, `written`), passed the model rather than kinds and callables, and have the language model keep its per-read lines on a reader object rather than on the adapter. Ends: `spec_reshape.py:33` do-not-invent-parallel-object-models, :57/:117 hold-state, :29 use-typed-signatures, `code_spec_model.py:102` hold-state.

