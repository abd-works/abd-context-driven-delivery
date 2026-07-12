### Rule: Round-trip structural parity is required for every adapter seam

When a behavior includes parsing and rendering between representations, tests
must assert round-trip structural parity across the canonical model.

At minimum, every adapter test suite includes one fixture that proves:

- `counts(parse(render(canonical))) == counts(canonical)`
- Count dimensions include: Epics, SubEpics, Stories, AcceptanceCriteria.

#### DO

- Add at least one parity fixture with realistic nested structures.
- Include assertions for all four count dimensions.
- Keep the fixture in the adapter's own spec file so regressions fail at the seam.

#### DO NOT

- Treat "conversion succeeded" as sufficient.
- Assert only file-shape/path existence while ignoring semantic counts.
- Skip parity checks for diagram or code backends.

