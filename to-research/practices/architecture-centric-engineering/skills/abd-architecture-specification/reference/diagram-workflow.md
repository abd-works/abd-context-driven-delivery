# Diagram workflow

Diagrams live in `architecture-context.md` files, not in the central spec.

## Participant diagrams — Draw.io

Mechanism-tier context files use Draw.io for participant/class diagrams (same format as domain specification). Use `{Parameterized}` names; concrete instances belong in `### Across the Codebase`.

Generate all mechanisms as tabs in one file:

```bash
python <path-to>/drawio-domain-sync/scripts/drawio_domain_cli.py architecture-specification.md \
  --from-arch-spec --output architecture-participants.drawio
```

Or a single mechanism:

```bash
python <path-to>/drawio-domain-sync/scripts/drawio_domain_cli.py architecture-context.md \
  --section "Class Specification" --output architecture-participants.drawio
```

Link to the `.drawio` file — do not embed or inline it.

## When to diagram

**Mechanism** — draw when 3+ classes collaborate in non-obvious ways. Skip for single-class mechanisms or instance-specific flows.

**Package / miscellaneous** — prose first. Add a concrete (non-parameterized) diagram only when structure is genuinely clearer as a visual. If it wants parameterization it's probably a mechanism.
