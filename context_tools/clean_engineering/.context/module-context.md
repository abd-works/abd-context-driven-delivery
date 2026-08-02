# CleanEngineering

## Purpose

Multi-fidelity OO design and implementation generator — modules, model, specification, and code — with sideways transform across language and diagram channels.

## Seam

`CleanEngineering` toolset: lifecycle actions (`generate`, `validate`, `satisfy`, …) plus `transform(source_format, target_format, content)` that parses into the canonical class model and renders into another channel at the same fidelity.

## Public API

`CleanEngineering` — fidelity + format constructor; `contexts`; `transform`; inherited BaseContextTool lifecycle and session tools.

## Dependencies

`BaseContextTool`; `class_model` channel adapters (`Markdown`, `Json`, language models, `DrawIO`); `focus`; primitives `Instruction` / tools annotations.
