# Examples

Worked reference under `wires/` — a feature package (process boot + feature
view) with a nested `recipients/` domain. The rules live in
`mern_domain_driven.md`; this folder is the concrete shape those rules produce.

Prefer generating a fresh feature/domain via `generate` rather than copying
this tree verbatim when the real slice differs.

Acceptance-test shape (`*_spec.{server,client,e2e}`) belongs to `stories` at
`acceptance_tests` fidelity — see that tool's examples.
