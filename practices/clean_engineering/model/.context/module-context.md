# Class model

## Purpose

Canonical OOAD model (`OoadNode` / `OoadClass` / `Module` / `CleanEngineeringModel`) and channel adapters that parse and render that model across markdown, JSON, languages, and draw.io.

## Seam

Each channel class exposes `parse(text) -> CleanEngineeringModel` and `render(model) -> str`. DrawIO auto-selects modules view vs UML class view from model content.

## Public API

`CleanEngineeringModel`, `Module`, `OoadClass`, `Property`, `Operation`, `Relationship`, `UpdateReport`; channel classes (`MarkdownCleanEngineeringModel`, `PythonCleanEngineeringModel`, `DrawIOCleanEngineeringModel`, …); example-factory helpers on the base model.

Draw.io lives under `class_model/drawio/` and Miro under `class_model/miro/`. Shared positioning, ordering, and layout live in `class_model/diagram/` (`Geometry`, `DiagramNode`, `DiagramClass`, `DiagramModule`, `ContainmentForest`). Each channel only writes its format (mxCell vs Mermaid/SVG).

## Dependencies

`update_report` (translation / reconcile); stdlib XML/HTML for draw.io; Drawio kit depends on Scan + Repair. Layout scanners do not depend on OO code scanners.
