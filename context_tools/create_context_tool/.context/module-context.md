# CreateContextTool

**Purpose:** Meta BaseContextTool domain that scaffolds or patches new context domains under `context_tools/` from `templates/` and the `examples/car_chronicle/` reference extension.

**Primary use case:** Generate a thin domain package (class module, `{domain}.md`, examples, optional formats/scanners) without putting new domains inside `base/` except under this kit.

**Rationale:** Scaffolding lives beside the composer (`base`) so lifecycle prose stays shared while domain creation keeps its own contexts, templates, and worked samples.

## Seam

`CreateContextTool` is the public surface callers construct and run for scaffold/patch. Constraint: do not invent domains inside `base/` outside this kit; subclass `BaseContextTool` in a new underscored folder and leave framework instruction slots alone unless composing another toolset in plain code.

## Public API

- `CreateContextTool(format=None, path=None, session=None, workspace=None)`
- Class attrs: `default_workspace_folder`, `context_index_key`
- Inherited lifecycle: `generate`, `validate`, `satisfy`, `repair`, `partition`, `index`, `segment`, …
- Inherited tools: session tools, `scan`

## Dependencies

`BaseContextTool` (subclass); scaffold assets under `templates/`; worked samples under `examples/`
