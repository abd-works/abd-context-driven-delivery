# tier-bodies-implemented

**Fidelity:** engineering
**Kind:** quality
**Reads:** `tests`

## Statement

Every step body inside a tier file (`<slug>-<tier>.test.<ext>`, `test_<slug>_<tier>.py`, `<Slug><Tier>Test.java`) must be **implemented**, not stubbed. Engineering fidelity produces working tests — leaving TODO placeholders defeats the purpose of the fidelity gate.

## What counts as "not implemented"

A step body fails this rule if any of the following are true:

- Body is empty (`{}` in TS/JS, `pass` alone in Python, `{}` in Java).
- Body contains a `TODO`, `FIXME`, `XXX`, or `HACK` comment.
- Body contains only a comment plus `raise NotImplementedError`, `throw new Error('not implemented')`, or an equivalent placeholder throw.
- Body is a single-line arrow that returns nothing and does nothing observable.

## What counts as "implemented"

At minimum, a step body must contain **at least one call expression** — a function invocation, an `await`, an assertion (`expect(...)`, `assert `), or a render/mount. The body is allowed to be small, but it must do work that ties back to the step's semantics.

## Rationale

The scaffolder produces TODO stubs when bootstrapping an empty tier file for the first time — that's a bootstrap concern. The engineering-fidelity eval measures whether the AI (or human) turned those stubs into real tests. Passing the scaffolded shape back through the eval is a cop-out, and this rule catches it.

Note that the WRITE-ONCE policy still applies: once a tier file exists with hand-authored bodies, the pipeline never overwrites it. This rule doesn't force regeneration — it only asserts that the tier file, whenever it exists, has actual code inside.

## Examples

**Fail** — empty body:

```ts
when = {
  'the Treasurer submits the Order': async () => {
    // TODO: server-tier action for the Treasurer submits the Order
  },
}
```

**Fail** — placeholder throw:

```py
def _when_the_customer_submits_the_order(self) -> None:
    """server-tier action: the Customer submits the Order"""
    raise NotImplementedError
```

**Pass** — real body:

```ts
when = {
  'the Treasurer submits the Order': async () => {
    this.response = await routeTransfer({ accountId: 'DDA-001', amount: '10000 USD', submittedAt: '14:30 ET' })
  },
}
```
