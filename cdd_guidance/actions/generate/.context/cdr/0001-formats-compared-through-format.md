# Generate compares a fidelity's formats through Format

**Status:** decided, round 6 (finding M5).

## Decision

`Generate._earlier_render` keeps reading a fidelity's format and the formats it declares through `Format(label).name`, so `md` and `markdown` compare as one format.

## Why

- The strings come from their owner: `FidelityGuidance.format` and the keys of `FidelityGuidance.outputs` (harness/guidance) are the labels a fidelity's YAML fields and a call's `format=` word give. Generate does not hold those strings or pass them around; it asks the fidelity it works at each time it builds the instructions, once per call.
- Making the fidelity hold *Format* objects is the change that removes the conversions, and it belongs to `harness/guidance`, whose fidelity every action, the graph, and the Session Board read. Generate converting its own copy into objects would add a second, Generate-only model of a fidelity's formats beside the fidelity's, which is the duplicated shape the guardrails forbid.

## Consequences

When `FidelityGuidance` holds *Format* objects for its format and outputs, `_earlier_render` compares them directly and this record is superseded.
