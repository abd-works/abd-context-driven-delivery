# CarChronicle

**Purpose:** The smallest complete practice — a driving chronicle written in the car's voice — that CreatePracticeGuidance points new practices at, and that the action specs (iterate, partition, sketch) run on.

**Primary use case:** Expand generate, validate, satisfy, and repair against `car_chronicle.md`, its templates, and its repair fixtures; `ChronicleWithOutput` shows a `generate_output` recipe that calls its own `add_epic` tool.

**Rationale:** Keeps a whole small practice (markdown, templates, examples, output) in one folder, so a new practice can copy the layout without a `module_dir` override.

## Seam

`CarChronicle` and `ChronicleWithOutput` are the public surface for this example practice. Constraint: keep the class module beside `car_chronicle.md` in this folder; never override `module_dir` to point elsewhere.

## Public API

- `CarChronicle()`
- `ChronicleWithOutput()`
- `ChronicleWithOutput.toolset_name`
- `ChronicleWithOutput.generate_output()`
- `ChronicleWithOutput.add_epic()`
- Everything *PracticeGuidance* gives a practice

## Dependencies

`harness/guidance` (*PracticeGuidance*), `harness/agent_tools`; the practice markdown and templates in this folder
