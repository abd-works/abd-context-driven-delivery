# Class model

## Purpose

Canonical OOAD model (`OoadNode` / `OoadClass` / `Module` / `CleanEngineeringModel`) and channel adapters that parse and render that model across markdown, JSON, languages, and draw.io.

## Seam

Each channel class exposes `parse(text) -> CleanEngineeringModel` and `render(model) -> str`. DrawIO auto-selects modules view vs UML class view from model content.

The walk is `practices/clean_engineering/.context/ooad-model.md`, written to `practices/stories/model/.context/practice-model.md`. Channel subclasses load and save. The code in this folder still exposes `parse` and `render`.

## Public API

`CleanEngineeringModel`, `Module`, `OoadClass`, `Property`, `Operation`, `Parameter`, `Relationship`, `UpdateReport`; channel classes (`MarkdownCleanEngineeringModel`, `PythonCleanEngineeringModel`, `DrawIOCleanEngineeringModel`, …). Each node clones itself. A channel loads with `load` and writes with `save`.

Draw.io lives under `class_model/drawio/` and Miro under `class_model/miro/`. Shared positioning, ordering, and layout live in `class_model/diagram/` (`Geometry`, `DiagramNode`, `DiagramClass`, `DiagramModule`, `ContainmentForest`). Each channel only writes its format (mxCell vs Mermaid/SVG).

## Dependencies

`update_report` (translation / reconcile); stdlib XML/HTML for draw.io; Drawio kit depends on Scan + Repair. Layout scanners do not depend on OO code scanners.
