## Overview

One paragraph — what this practice produces and who consumes it.

- **`first-rule-slug`** — Testable requirement as a named rule.

## Guidance

Practice-wide workflow, vocabulary, and quality bar (not per-fidelity detail).

## Shared rules

```yaml
alwaysApply: false
globs: "**/*{domain_slug}*"
```

Whenever you create or change artifacts this practice owns. Follow these rules.

- **`shared-rule-slug`** — Shared rule body.

## Fidelities

### {default_fidelity}

```yaml
default_format: markdown
stage: discovery
```

#### Guidance

Fidelity-specific steps: read overview, apply `templates/`, write outputs, run **validate** through the relevant Guidance action with `guidance: [<this practice>]`.

#### Rules

- **`fidelity-rule-slug`** — Fidelity rule body.
