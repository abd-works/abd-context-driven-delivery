# Rule: Prioritize architectural risk validation

**Early** increments should **prove** the scary parts: real **integrations**, **performance** with realistic load, **deployment** and ops, **unfamiliar** frameworks—inside a **short end-to-end** flow. Deferring risk behind mocks or “local only” builds invites late rework.

## DO

- Pull the **riskiest integration** into **Increment 1** with the **simplest** journey that still hits the real system (auth, response shape, limits).
- Deploy **something** real to the target environment early; validate connectivity, config, and observability.
- Size performance or data-volume tests to **match** early concerns (e.g. report with 10k rows if that is the fear).

## DON'T

- Spend increments 1–2 on **perfect UI** while **payment**, **identity**, or **hosting** stays mocked or unspecified.
- Assume **infrastructure** “will be fine”—prove it with a **thin** feature on **real** infra.
- Treat **“we’ll swap the mock later”** as risk reduction without a dated, vertical slice that uses the real dependency.

```text
Good: Increment 1 — place order → **real** gateway (happy path only) → DB row → confirmation page.
Weak: Increment 1 — full cart UX; payment stub; “real payment in increment 4.”
```
