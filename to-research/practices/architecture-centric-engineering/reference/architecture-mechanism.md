# Architecture Mechanism — Shared Concept

This is the family-level definition of an **architecture mechanism**. The
architecture skills (`abd-architecture-outline`, `abd-architecture-blueprint`,
`abd-architecture-specification`, `abd-architecture-template`,
`abd-architecture-code`) all refer to it; each skill adds its own *level of
fidelity* on top of this single definition rather than re-defining the term.

## What an architecture mechanism is

An **architecture mechanism** is the architecture's fixed answer to a
**cross-cutting concern** — a concern that shows up in many components rather
than belonging to one feature. It is the *verbed* concern: not "errors" but
*how the architecture handles errors*; not "data" but *how it persists*; not
"identity" but *how it authorizes*. A mechanism is a standardized, recurring
technical solution applied consistently across the system so that complexity
stays down, behaviour stays uniform, and proven solutions get reused instead of
reinvented.

The term comes from the Rational Unified Process, where mechanisms evolve
through three stages — analysis (the concern is named), design
(a technology-agnostic approach is chosen), implementation (a concrete
technology realizes it). Modern practice often calls the same idea an
architectural pattern, tactic, or architecturally significant requirement; in
this family we keep the single word **mechanism**. Background notes:
[`data.md`](data.md).

## Canonical mechanism categories

Adapt these to the project; they are the common starting set:

- **Security** — authentication, authorization, secret handling, identity propagation.
- **Error Handling & Resilience** — exception/Result conventions, retry, circuit breaker, fallback, error reporting.
- **Logging & Observability** — logging library, log shape, trace propagation, metric emission.
- **Validation** — input validation, business-rule validation, error reporting back to the caller.
- **Configuration** — config source, environment separation, secret management, feature flags.
- **Caching** — where caches sit, invalidation strategy, consistency model.
- **Communication** — sync vs async patterns, message bus, API versioning, service discovery.
- **Persistence** — repository pattern, transaction boundaries, migration strategy.

Less common but recurring: idempotency, transactions, rate limiting, messaging.

## How each skill uses this concept

- **`abd-architecture-outline`** — *names* every mechanism, records its technology choice + NFR justification, and writes an ADR per mechanism choice. Detail defers downward.
- **`abd-architecture-blueprint`** — describes each mechanism in 1–2 paragraphs as a **code shape** every module must adopt: where the mechanism activates, what every module that participates in it must do, which modules (if any) implement its functional surface. The mechanism-modules section names mechanisms that also have a concrete module surface.
- **`abd-architecture-specification`** — for every mechanism named in the blueprint, produces a **mechanism-tier `architecture-context.md`** in the folder that hosts the templated pattern (File Structure, Participants, Class Specification, Rules, Canonical Patterns, Across the Codebase). The central `architecture-specification.md` lists every mechanism as a one-line entry with a link to its context file and surfaces it in the Where-to-Start table when feature work touches it.
- **`abd-architecture-template`** — turns one mechanism's `architecture-context.md` into a **runnable parameterized reference module** at `docs/architecture/templates/<slug>/` — folder skeleton, real source files using the spec's placeholder vocabulary verbatim, parameterized test scaffolds mirroring the test-helpers context file, plus a concrete `example/` that builds and whose tests pass. In `project` mode (default) one package covers the project's primary mechanism; in `mechanism` mode (opt-in) one package per mechanism is generated.
- **`abd-architecture-code`** — for one story at a time, resolves the right template package (via the central spec's Where-to-Start lookup of the mechanism in scope), reads `<spec-root>/template/`, `<spec-root>/templates/tests/`, `<spec-root>/example/`, `<spec-root>/rules/` from that package, copies and renames the template files with the story's domain terms, and enforces the lifted Rules through tests and production code at the spec's layer order.
