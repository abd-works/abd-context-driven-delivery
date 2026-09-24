*Drawio* is the miniature kit a caller hires to create, scan, and repair a Clean Engineering Draw.io diagram. *Diagram* is the mxfile. *Page* is one tab. *DiagramNode* is the placed-cell contract — geometry, HTML, style, draw, and keep-or-place. It is written like a class without the `+` seam marks: one type, not a second `IDiagramNode`. *DrawIOModule* and *DrawIOClass* are the live `Module` and `OoadClass` filling that contract. *DrawIORelationship* is the live `Relationship` routing itself. *ImportedClass* is a local-page view of a class owned by another module. *Inheritance* is the relationship that must point up at a parent sitting above its children.

- A caller never lays out HTML, waypoints, or mxCell attributes. They ask `Drawio` to create or scan a path.
- *DrawIOModule* always draws from the `Module` it wraps. It never copies purpose or seam terms into a second record.
- *DrawIOClass* always draws from the `OoadClass` it wraps. Properties, operations, and stereotypes come from that class.
- *DrawIORelationship* always draws from the `Relationship` it wraps. Kind chooses the arrowhead; the two classes choose the ends.
- **Invariant:** No second `*Model` / `*Entry` family restates `Module`, `OoadClass`, or `Relationship`.

Build order: `Geometry` → `DiagramNode` → `DrawIOModule` → `DrawIOClass` → `ImportedClass` → `DrawIORelationship` → `Inheritance` → `Page` → `Diagram` → `DrawIOCleanEngineeringModel` → `Drawio`

---

# practices.clean_engineering.model.drawio

- **Purpose:** Turn a Clean Engineering model into a Draw.io mxfile and back, and scan the file against layout rules in `drawio.md`.
- **Seam (terms):** Drawio, Diagram, Page, DiagramNode, DrawIOModule, DrawIOClass, DrawIORelationship
- **Dependencies (one-way):** practices.clean_engineering.model

## Constraint

Callers type `Drawio.create_diagram`, `Drawio.scan`, `Drawio.render`, and the format channel `DrawIOCleanEngineeringModel.parse` / `render` / `sync`. They do not set cell HTML, anchors, or private layout fields. `keep_positioning` on `Drawio` / `Diagram` is the only layout policy they pass.

## Geometry

+ Geometry(x: float, y: float, width: float, height: float)
	// A geometry is a closed axis-aligned box. It never shares its interior with another geometry on the same page except by a named overlap resolver on Page.
------
+ x: float
+ y: float
+ width: float
+ height: float
----
+ overlaps(other: Geometry): bool
+ clear_gap(other: Geometry): float
+ shifted(dx: float, dy: float): Geometry
+ side_anchor(side: str, frac: float): tuple

## DiagramNode

DiagramNode()
	// A diagram node is one placed cell. Every module, class, and import is a diagram node. Edges are not.
	// HTML, height, style, and geometry live here so a subtype never re-implements placing a cell.
------
<< composition >> geometry: Geometry
	// The node occupies this box on its page. Layout never stores a second copy of the box beside the node.
cell_id: str
----
html(): str
	// Label the cell. A subtype fills this from the Module or OoadClass it wraps — never from a parallel record.
height(): int
	// Pixel height of this node's geometry. Derived from html content, not a second layout table.
style(): str
	// mxCell style for this node. Local vs imported vs module chrome are style, not a second type.
draw(page: Page): None
	// Write this cell onto the page from html, style, and geometry. Subtypes may draw children after.
	-> Page.place
keep_or_place(previous: Geometry): None
	// When keep_positioning holds and previous exists, geometry stays. Otherwise the node places itself on the page.
	-> Geometry
parse_html(value: str): None
	// Restore wrapped Module or OoadClass fields from the cell label. Never invent a second card type.
- _write_cell(page: Page): None
	// One mxCell: id, value, style, geometry. Callers never set those attributes.

## DrawIOModule : DiagramNode

+ DrawIOModule(module: Module)
	// DrawIOModule is the Module. It must render that Module's name, purpose, and public seam, never a parallel card.
------
+ << association >> module: Module
+ << composition >> children: list[DrawIOModule]
	// Path children sit inside this module's cell. They never get a fake sibling module for the path parent.
+ << association >> dependencies: list[DrawIOModule]
----
+ html(): str
	-> module.public_terms
+ height(): int
	-> DiagramNode.height
+ draw(page: Page): None
	// After the cell is on the page, children draw inside this geometry.
	-> DiagramNode.draw
	-> DrawIOModule.draw
+ parse_html(value: str): None
	-> module
+ dep_depth(): int
	-> DrawIOModule.dep_depth
- _header_height(): int

## DrawIOClass : DiagramNode

+ DrawIOClass(oclass: OoadClass)
	// DrawIOClass is the OoadClass on a page. HTML, height, and stereotypes come from that class.
------
+ << association >> oclass: OoadClass
+ << association >> owning_module: DrawIOModule
----
+ html(): str
	-> oclass.properties
	-> oclass.operations
+ height(): int
	-> DiagramNode.height
+ parse_html(value: str): None
	-> oclass
- _stereotype_html(): str
- _display_name(): str

## ImportedClass : DrawIOClass

+ ImportedClass(oclass: OoadClass, from_module: DrawIOModule)
	// An imported class is always dashed and labelled «from: Module». It never draws as a solid local card.
------
+ << association >> from_module: DrawIOModule
----
+ html(): str
	// Key properties only — enough to recognise the type, not the full compartment dump.
+ height(): int
+ style(): str
	// Always the dashed imported chrome. Never the solid local class style.
+ draw(page: Page): None
	// Inheritance imports sit above the local subtype. Other imports sit beside the local class they link.
	-> DiagramNode.keep_or_place
	-> DiagramNode.draw

## DrawIORelationship

+ DrawIORelationship(relationship: Relationship, source: DrawIOClass, target: DrawIOClass)
	// A relationship edge relates exactly two class cells. It never crosses a third class's geometry.
------
+ << association >> relationship: Relationship
+ << association >> source: DrawIOClass
+ << association >> target: DrawIOClass
+ waypoints: list[tuple]
+ exit_side: str
+ entry_side: str
+ exit_frac: float
+ entry_frac: float
----
+ kind(): str
	-> relationship
+ style(): str
+ route(page: Page): None
	// First and last segments hit the chosen sides perpendicularly. Parallel runs do not share a column or row.
	-> Geometry.side_anchor
	-> Page.obstacles
+ draw(page: Page): None
	-> DrawIORelationship.route
+ copy_route_from(previous: DrawIORelationship): None
	// When keep_positioning holds, existing routing stays; only a new relationship routes.

## Inheritance : DrawIORelationship

+ Inheritance(relationship: Relationship, source: DrawIOClass, target: DrawIOClass)
	// The parent cell always sits at a smaller y than the child. The arrow is child → parent, block, unfilled.
------
----
+ route(page: Page): None
	// Siblings share a y row under the parent. A grandparent import sits above the parent.
	-> ImportedClass.draw

## Page

+ Page(name: str)
	// A page is one Draw.io tab. Modules view: one containment diagram. Class view: one module's locals plus the imports they need.
------
+ name: str
+ << composition >> modules: list[DrawIOModule]
+ << composition >> classes: list[DrawIOClass]
+ << composition >> relationships: list[DrawIORelationship]
----
+ draw(): None
	// Every diagram node draws itself. The page only orders the asks and then separates overlaps.
	-> DiagramNode.draw
	-> DiagramNode.keep_or_place
	-> DrawIORelationship.draw
	-> Page.separate_overlaps
+ place(node: DiagramNode): None
	-> DiagramNode.geometry
+ obstacles(except_ids: list): list[Geometry]
+ separate_overlaps(): None
	// Prefer moving imports sideways rather than shoving a local pack into a spine.
- _locals(): list[DrawIOClass]
- _imports_needed(): list[ImportedClass]
	// Outbound links and inbound inheritance only. Inbound association sources stay on the other page.

## Diagram

+ Diagram()
	// Diagram is the mxfile. It owns pages. It does not build class HTML or edge styles.
------
+ previous: str
+ keep_positioning: bool
+ << composition >> pages: list[Page]
----
+ parse(text: str): CleanEngineeringModel
	-> DrawIOModule.parse_html
	-> DrawIOClass.parse_html
	-> DrawIORelationship
+ render(canonical: CleanEngineeringModel): str
	// Modules view when the canonical has modules and no class members to show; otherwise class view, one page per module.
	-> Page.draw
+ page_for(module: DrawIOModule): Page

## DrawIOCleanEngineeringModel

+ DrawIOCleanEngineeringModel(name: str, sequential_order: int)
	// Format channel only. Same parse / render / sync seam as MarkdownCleanEngineeringModel. It must not hold layout fields, HTML builders, or edge routers.
------
+ previous: str
+ keep_positioning: bool
+ << composition >> diagram: Diagram
----
+ parse(text: str): DrawIOCleanEngineeringModel
	-> Diagram.parse
+ render(canonical: CleanEngineeringModel): str
	-> Diagram.render
+ sync(text: str, canonical: CleanEngineeringModel): UpdateReport
	-> parse
+ load_module(source: Module): DrawIOModule
+ load_class(source: OoadClass): DrawIOClass

## Drawio

+ Drawio(workspace)
	// The kit a caller types. Create writes a path. Scan judges layout. Repair fixes the generator, not one diagram by hand.
------
+ source_format: str
+ previous: str
+ keep_positioning: bool
+ << association >> scan_root: Path
------
----
+ create_diagram(content: str, path: str): str
	-> DrawIOCleanEngineeringModel.parse
	-> DrawIOCleanEngineeringModel.render
+ scan(paths: list): str
	-> DrawioScanner.run_report
+ render(content: str, path: str): str
	-> Drawio.create_diagram
	-> Drawio.scan
+ validate(): str
	-> Drawio.scan
+ repair(asset: str, violation: str): str
	-> Drawio.scan
+ verify_regression(examples_root: str): str

## DrawioScanner

+ DrawioScanner(rule: str)
	// Layout audit for an existing mxfile. It reads cells; it does not render them.
------
+ rule: str
+ workspace_root: Path
----
+ scan(root: Path, files: list): list
+ run_report(paths: list): str
