# CleanEngineering

## Purpose

Multi-fidelity OO design and implementation generator — modules, model, specification, and code — with sideways transform across language and diagram channels.

## Seam

`CleanEngineering` toolset: `guidance` plus `generate_output` (drawio.render when format is drawio) plus `transform(source_format, target_format, content)` that parses into the canonical class model and renders into another channel at the same fidelity. Lifecycle generate / validate / satisfy live on kits (`Generate().generate(tools=[ce])`).

## Public API

`CleanEngineering` — fidelity + format constructor; `contexts`; `transform`; `render(format, content)` (calls `transform` from the current format); inherited BaseContextTool lifecycle and session tools.

## Dependencies

`BaseContextTool`; `class_model` channel adapters (`Markdown`, `Json`, language models, `DrawIO`); `focus`; primitives `Instruction` / tools annotations.
