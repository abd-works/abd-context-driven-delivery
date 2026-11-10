# CreatePracticeGuidance

**Purpose:** Meta **PracticeGuidance** builder that scaffolds or patches new practice packages under `cdd_guidance/practices/` from `templates/` and the `_examples/car_chronicle/` reference.

**Primary use case:** Generate a thin practice package (class module, `{domain}.md`, templates, examples, optional `model/{format}/` and scanners) without putting new domains inside `harness/`.

**Rationale:** Scaffolding stays in `cdd_guidance/builders/` while runtime guidance types live in `harness/guidance/`.

## Seam

`CreatePracticeGuidance` is the public surface callers construct for scaffold/patch. Constraint: subclass **`PracticeGuidance`** in a new underscored folder under `practices/`; follow **`harness/guidance/AGENTS.md`**; lifecycle work goes through Guidance actions with `guidance=[...]`, not methods on the practice class.

## Public API

- `CreatePracticeGuidance(format=None, path=None, session=None, workspace=None)`
- Class attr: `default_workspace_folder`
- Inherited: `instructions`, `overview`, `guidance`, `rules`, `templates`, `examples`, `fidelities` (when present in md). **generate** / **repair** / **validate** are separate Guidance actions.

## Dependencies

`harness/guidance` (`PracticeGuidance`); scaffold assets under `templates/`; worked sample under `_examples/car_chronicle/`
