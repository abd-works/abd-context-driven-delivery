# Rule: Generated code implements story scope only

Generated production code and tests implement exactly the behaviour described in the story's acceptance criteria — no speculative methods, no extra fields, no pre-emptive abstractions.

## DO

- Implement one method per acceptance criterion action; stop when all criteria are covered.

  **Example (pass):** Story has two AC: "spawn character" and "turn character." Generated domain class has `Spawn()` and `TurnTo(float angle)` — nothing else.

- Add a dependency (interface, collaborator) only when the story's behaviour requires crossing a mechanism boundary the spec defines.

  **Example (pass):** `Spawn()` needs `IGameCommandExecutor` (Path 1 — DLL) and `IMemoryInstance` (Path 2 — MemorySharp) per spec; both injected. No third dependency added "for future use."

## DO NOT

- Generate methods, properties, or constructors the story's acceptance criteria do not require.

  **Example (fail):** Story is "spawn character." Generated `Character.cs` also includes `Despawn()`, `SetGangMode()`, and `SavePosition()` — none in the acceptance criteria.

- Add abstraction layers, base classes, or utility helpers not shown in `<spec-root>/template/` and not described in `<context-file>` § Class Specification.

  **Example (fail):** `BaseCharacter` introduced as a parent class when `<spec-root>/template/{Domain}.cs` shows a plain concrete class with constructor injection and no hierarchy, and `<context-file>` § Class Specification names no base class.
