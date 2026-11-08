# Generate compares a fidelity's declared formats through Format

**Status:** decided, round 6 (finding M5); wording brought up to date in round 7 (finding R5).

## Decision

`Generate._earlier_render` reads the format the fidelity works in from the *Format* the fidelity holds (`current.format.name`, since f02b6485), and reads the formats an earlier fidelity declares, and the formats it has files in, through `Format(label).name`, so `md` and `markdown` compare as one format.

## Why

- The declared formats come from their owner: the keys of `FidelityGuidance.outputs` and of `FidelityGuidance.files()` (harness/guidance) are the labels a fidelity's YAML fields give. Generate does not hold those strings or pass them around; it asks the fidelity it works at each time it builds the instructions, once per call.
- Making the fidelity hold *Format* objects for its declared outputs is the change that removes the remaining conversions, and it belongs to `harness/guidance`, whose fidelity every action, the graph, and the Session Board read. Generate converting its own copy into objects would add a second, Generate-only model of a fidelity's formats beside the fidelity's, which is the duplicated shape the guardrails forbid.

## Consequences

The fidelity's own format is already a held *Format*, so that half needs no conversion. When `FidelityGuidance` holds *Format* objects for its declared outputs too, `_earlier_render` compares them directly and this record is superseded.
