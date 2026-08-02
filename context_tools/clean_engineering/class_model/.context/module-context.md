# Class model

## Purpose

Canonical OOAD model (`OoadNode` / `OoadClass` / `Module` / `CleanEngineeringModel`) and channel adapters that parse and render that model across markdown, JSON, languages, and draw.io.

## Seam

Each channel class exposes `parse(text) -> CleanEngineeringModel` and `render(model) -> str`. DrawIO auto-selects modules view vs UML class view from model content.

## Public API

`CleanEngineeringModel`, `Module`, `OoadClass`, `Property`, `Operation`, `Relationship`, `UpdateReport`; channel classes (`MarkdownCleanEngineeringModel`, `PythonCleanEngineeringModel`, `DrawIOCleanEngineeringModel`, …); example-factory helpers on the base model.

## Dependencies

`update_report` (translation / reconcile); stdlib XML/HTML for draw.io; no dependency on scanners.

## Known scan notes

Several channel files still have private module-level helpers that `prefer-class-operations` would fold onto the channel class (`DrawIOCleanEngineeringModel`, language models). Left as known debt — do not extract more free functions when editing.
