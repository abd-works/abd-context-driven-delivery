# Examples

Worked reference under `wires/` — a feature package (process boot + feature
view) with a nested `recipients/` aggregate. Persistence is
[lowdb](https://github.com/typicode/lowdb): `data/recipients.json` holds only
Recipient aggregate roots (and the value objects nested inside them). The
rules live in `lern_domain_driven.md`; this folder is the concrete shape
those rules produce.

Prefer generating a fresh feature/domain via `generate` rather than copying
this tree verbatim when the real slice differs.

Acceptance-test shape (`*_spec.{server,client,e2e}`) belongs to `stories` at
`acceptance_tests` fidelity — see that tool's examples. When a slice spans
aggregates, AskQuestion for event-based orchestration vs direct repository
calls by the client before writing stories.
