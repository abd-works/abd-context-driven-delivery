# Clean Engineering — Procedural Guidance (model fidelity)

## The empty-seam-first approach

At model fidelity, you're defining the shape of the contract, not the implementation. Think of it as writing the table of contents before writing the book:

1. **Stub public properties** — what does this class expose? Each property is a noun phrase: "remaining budget," "active status," "target character." Empty body (`...` / `pass`).
2. **Stub public operations** — what does this class do? Each operation is a verb phrase: "charge card," "reserve seat," "compute total." Empty body.
3. **No private members yet** — those come at code fidelity.
4. **No implementation** — bodies are empty contracts. The shape is what matters.

## Interface decision thinking

By default, there is NO separate `I{Class}` interface. The public seam lives directly on `Class` itself. Only create a separate interface when:

- The user explicitly asks for one
- The module genuinely has multiple layers/implementations behind one seam (e.g. swappable backends, multiple adapters)

A single concrete implementation with no swapping need does not warrant a separate interface. Don't add interfaces "for consistency."

## Relationship thinking

At model fidelity, you add relationship kinds and cardinality. Three kinds, chosen by lifecycle:

1. **Composition** — owner controls the other's lifecycle. Order composes OrderLine — destroying the order destroys the lines.
2. **Aggregation** — collector groups members that can outlive it. Playlist aggregates Song — deleting the playlist doesn't delete the songs.
3. **Association** — both sides are independent; they use each other. Customer associates with SupportAgent.

Value objects that merely describe (Money on a Transaction) are association or property — not composition. Composition is for parts whose lifecycle the owner controls.

## Interaction and invariant thinking (optional at model)

You may name interactions and invariants at model fidelity to capture intent early, but this is optional:

- **Interactions** — one class's operation calling another's. Use `-> {collaborator}.{operation}` notation. Just the receiver and the operation, no parameters.
- **Invariants** — rules that must always hold. State in plain English as `// {rule}`. Not enforcement methods.

Naming these at model captures collaboration intent without committing to implementation.

## Example factory thinking

When a type will be used from Stories, stub the factory in a sibling file:

- `{family}.py` — production type only
- `{type}_example_factory.py` — factory with named methods, empty at model

Fake / Isolated / Production are **modes of how the factory builds**, not subclass types. Never create `FakePayment` / `IsolatedPayment` / `ProductionPayment` classes.
