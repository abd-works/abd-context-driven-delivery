# Drawio (class_model/drawio)

## Purpose

Miniature kit for Clean Engineering Draw.io class / modules diagrams: create the diagram, scan layout rules from `drawio.md`, and repair the layout generator on definitive failures. Also hosts the `DrawIOCleanEngineeringModel` parse/render channel.

## Seam

`Drawio.render` (create → validate/scan → repair sub-agent); `Drawio.create_diagram(..., keep_positioning=False)`; `Drawio.scan` / `validate` / `repair`; channel `DrawIOCleanEngineeringModel.parse` / `.render(..., keep_positioning=False)`.

## Public API

`Drawio`, `DrawIOCleanEngineeringModel`; `keep_positioning` on render/create_diagram (existing class positions and relationship routing stay put; new classes use the layout algorithm); layout scanners under `scanners/` (`*_scanner.py`); fixtures under `examples/evals/<case>/{faultyAsset,repairedAsset}.drawio`.

## Dependencies

`primitives.actions` (`@action` / `@agentic_toolset`); `utilities.scanners` (`Scan` / `Scanner`); `context_tools.actions.repair` (`Repair`); stdlib XML via `drawio_tools`.

## Known scan notes

Judgment rules in `drawio.md` (e.g. `module-spatial-cohesion`, `ull-bullets-become-rows`, `aggregate-layout-cohesion`) have no scanner — validate covers them as critical-judge prose. `stereotype-above-class-name` is mechanical and has a scanner.
