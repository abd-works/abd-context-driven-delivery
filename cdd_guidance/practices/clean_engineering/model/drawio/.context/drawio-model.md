*Drawio* is the toolset a caller uses to create, scan, and repair a Clean Engineering Draw.io diagram. *DrawIOCleanEngineeringModel* is the draw.io format of the class model: it parses a diagram into the same modules and classes every other format reads, and renders a model back as a modules view or a class view. *DrawIOModule* and *DrawIOClass* are the live `Module` and `OoadClass` on a page; each writes itself as one Draw.io vertex through *DrawioVertex*. *DrawIOImportedClass* is the dashed Draw.io card for a class owned by another module. *DrawioScanner* reads an existing `.drawio` file page by page and reports one layout rule; each rule is a scanner subclass.

- A caller never lays out HTML, waypoints, or mxCell attributes. They ask `Drawio` to create or scan a path.
- *DrawIOModule* always draws from the `Module` it is. It never copies purpose or seam terms into a second record.
- *DrawIOClass* always draws from the `OoadClass` it is. Properties, operations, and stereotypes come from that class.
- The page layout — *Geometry*, *DiagramNode*, *DiagramClass*, *DiagramModule*, the shared *ImportedClass*, *DiagramArrow*, *CardPlacement*, *ArrowRouter*, and *ContainmentForest* — belongs to the class model and is modelled in [ooad-model.md](../../.context/ooad-model.md). This module uses it; the DDD aggregate view uses it too.
- **Invariant:** No second `*Model` / `*Entry` family restates `Module`, `OoadClass`, or `Relationship`.

---

# cdd_guidance.practices.clean_engineering.model.drawio

- **Purpose:** Turn a Clean Engineering model into a Draw.io mxfile and back, and scan the file against the layout rules in `drawio.md`.
- **Seam (terms):** Drawio, DrawIOCleanEngineeringModel, DrawIOModule, DrawIOClass, DrawioScanner
- **Dependencies (one-way):** cdd_guidance.practices.clean_engineering.model (*CleanEngineeringModel*, *Module*, *OoadClass*, *DiagramCleanEngineeringModel*, *DiagramModule*, *DiagramClass*, *ImportedClass*, *ContainmentForest*, *DiagramArrow*, *CardPlacement*, *ArrowRouter*), harness/graph (*Violation*, *PracticeGraphRule*), harness/agent_tools, harness/markdown

## Constraint

Callers type `Drawio.create_diagram`, `Drawio.scan`, `Drawio.render`, and the format's `DrawIOCleanEngineeringModel.load` / `parse` / `render` and the `sync` every class model inherits. They do not set cell HTML, anchors, or private layout fields. `keep_positioning` on the `DrawIOCleanEngineeringModel` that `Drawio` holds as its `channel` is the only layout policy they pass.

## DrawioVertex

A placed node written as one Draw.io vertex cell: its HTML label, its style, and its box.

------
----
+ append_to(root_el: Element): Element
	// one mxCell: id, value, style, vertex, parent, and geometry. Callers never set those attributes
	-> html
	-> style
	-> DiagramNode.geometry

## DrawIOModule : DiagramModule, DrawioVertex

The rounded modules-view cell.

------
----
+ html(): str
	// the name, the purpose line, then the shown seam terms as bullets
	-> DiagramModule.purpose_line
	-> DiagramModule.shown_seam_terms
+ style(): str
	// a nested module uses the child style
+ from_cell(value: str, sequential_order: int): DrawIOModule | None
	// class operation: the module a cell label names, with its purpose and seam terms; None when it names none
+ load_class(source: OoadClass): DrawIOClass
	-> DrawIOClass.translate_from

## DrawIOClass : DiagramClass, DrawioVertex

The Draw.io UML class cell.

------
+ fill_color: str
	// the colour of the module the class belongs to
+ owning_module: str
	// written into the style, so parse puts the class back in its module
----
+ width(): int
	// wide enough that no member line wraps, because the height counts one printed line per member
+ html(): str
	// the stereotypes as <<Mark>>s in small italics above the name, then properties and operations, with - for a private operation
	// parse reads the marks back into stereotypes, and each inheritance arrow into a base
+ style(): str

## DrawIOImportedClass : ImportedClass, DrawIOClass

The dashed card for a class owned by another module. It extends the class model's shared *ImportedClass* and *DrawIOClass*.

------
----
+ html(): str
	// «from: Module», the name, and the key properties only — enough to recognise the type
	-> ImportedClass.key_properties
+ style(): str
	// always the dashed imported style, never the solid local class style

## DrawIOCleanEngineeringModel : DiagramCleanEngineeringModel

The `drawio` format. A modules view when the model has modules and no class members to show; otherwise a class view, on one page, or one page per module when the model has more than forty classes in two or more modules.

+ DrawIOCleanEngineeringModel(name: str = "", sequential_order: int = 1)
------
+ previous: str | None
	// the diagram as it is now
+ keep_positioning: bool
	// cards and arrows already on previous stay where they are; only new ones are laid out
----
+ parse(text: str): DrawIOCleanEngineeringModel
	// fills this model and returns it: a modules diagram, one page whose cards name their module in their style, or one module per page; dashed import cards are skipped
+ render(canonical: CleanEngineeringModel): str
	// becomes the canonical model once (translate_from), then writes its own Draw.io modules and classes
	-> CardPlacement.place
	-> ArrowRouter.route
+ load(path: str): DrawIOCleanEngineeringModel
	-> parse
+ save(): str
	-> render
+ kept_previous(): str | None
	// previous when this render keeps its positions
+ load_module(source: Module): DrawIOModule
+ load_module_cell(source: Module): DrawIOModule
	// a Draw.io cell for a container module the containment forest made
+ imported_class(source: OoadClass, from_module: str = ""): DrawIOImportedClass

## Drawio

The toolset a caller types. Create writes a path. Scan judges layout. Repair fixes the layout generator, not one diagram by hand.

+ Drawio(practice: CleanEngineering)
------
+ practice: CleanEngineering
	// the practice that makes it; its formats read the content a diagram is drawn from
+ source_format: str
	// the format create_diagram parses its content from: any format the practice reads
+ << composition >> channel: DrawIOCleanEngineeringModel
	// the one Draw.io model it writes; its previous and keep_positioning are the layout policy
+ scan_root: str | None
+ rule: str | None
----
+ create_diagram(content: str, path: str): str
	// with keep_positioning, the diagram already at path is the previous one
	-> CleanEngineering.model_in
	-> DrawIOCleanEngineeringModel.render
+ scan(paths: list[str]): str
	-> DrawioScanner.run_report
+ render(content: str = "", path: str = ""): str
	// create the diagram, validate it, and repair through a sub-agent when definite layout failures remain
	-> create_diagram
	-> validate
	-> repair
+ validate(): str
	-> scan
+ repair(asset: str, violation: str): str
	-> scan
+ verify_regression(examples_root: str = ""): str

## DrawioScanner

Layout audit for an existing mxfile. It reads cells; it does not render them. Each subclass names one `RULE` and checks it in `scan_page`: `base-above-derived`, `class-title-no-markdown-bold`, `distinct-anchor-points`, `edges-approach-perpendicular`, `edges-do-not-cross-classes`, `edges-do-not-cross-other-edges`, `edges-do-not-overlap-edges`, `leaf-nodes-not-in-horizontal-row`, `prefer-short-routes`, and `stereotype-above-class-name`.

+ DrawioScanner(rule: str | None = None, explicit_paths: list[Path] = ())
------
+ rule: str
+ explicit_paths: frozenset[Path]
	// paths the caller named, scanned even inside folders a workspace scan skips
+ workspace_root: Path | str | None
----
+ scan(root: Path, files: list[Path]): list[Violation]
+ scan_file(root: Path, file_path: Path): list[Violation]
	// each diagram page of the file
	-> scan_page
+ scan_page(page: DrawioPage): list[Violation]
	// each subclass checks its one rule here
+ violation(page: DrawioPage, message: str): Violation
+ discover(): dict[str, type[DrawioScanner]]
	// class operation
	// every *_scanner.py beside this file, by its RULE
+ run_report(paths: list[str]): dict
	// every discovered scanner over paths: ok, the rule names, and the violations
+ run_main(argv: list[str] | None = None): int
+ collect_drawio_files(root: Path): list[Path]
+ is_skipped_path(path: Path): bool

## DrawioPage

One page of a draw.io file (`drawio/drawio_page.py`): its cells, the class boxes on it, and the edges between them. It is the one reader of draw.io cells: *DrawIOCleanEngineeringModel* parses a diagram and keeps the positions and routes of the one it replaces through it, and every scanner checks one.

+ DrawioPage(file_path: Path | None, name: str, root: Element)
------
+ cells: list[Element]
+ vertices: list[Element]
+ edges: list[Element]
+ boxes: dict[str, tuple]
+ class_names: dict[str, str]
----
+ pages_in(mxfile: Element, file_path: Path | None = None): list[DrawioPage]
	// class operation: each diagram page that holds a graph model
+ whole(text: str): DrawioPage | None
	// class operation: every cell of a document as one page
+ cell(cell_id: str): Element | None
+ positions(): dict[str, tuple[float, float]]
+ edges_by_ends(): dict[tuple[str, str], Element]
+ kind_of(edge: Element): str
	// inheritance, composition, aggregation, dependency, or association
+ describe(edge: Element): str
	// Source->Target (kind)
+ segments(edge: Element): tuple[list, bool]
	// the polyline an edge draws, and whether Draw.io's router may draw it differently

The graph checks the same rules on diagram files: `drawio/rules/__init__.py` wraps each discovered scanner in a *PracticeGraphRule* whose `check_practice` scans each `.drawio` file the practice read a class, module, or package from once, and reports on the first of those nodes; `CleanEngineering.language_checks("drawio")` returns them.
