# CarChronicle

**Purpose:** Minimal BaseContextTool domain example — a driving chronicle written in the car's voice — used as the reference extension for CreateContextTool scaffolds and host-face specs.

**Primary use case:** Expand generate/validate/satisfy/repair against `car_chronicle.md` contexts, templates, and repair fixtures; `ChronicleWithOutput` shows a `generate_output` override that nests `add_epic`.

**Rationale:** Keeps a complete small domain (md + templates + examples + output) in one folder so new domains can copy the layout without a `module_dir` override.

## Seam

`CarChronicle` and `ChronicleWithOutput` are the public surface for this example domain. Constraint: keep the class module beside `car_chronicle.md` in this folder — never override `module_dir` to point elsewhere.

## Public API

- `CarChronicle(path=None, session=None)`
- `ChronicleWithOutput(path=None, session=None)`
- `ChronicleWithOutput.toolset_name`
- `ChronicleWithOutput.generate_output()`
- `ChronicleWithOutput.add_epic()`
- Inherited BaseContextTool lifecycle

## Dependencies

`BaseContextTool`; domain markdown and templates in this folder
