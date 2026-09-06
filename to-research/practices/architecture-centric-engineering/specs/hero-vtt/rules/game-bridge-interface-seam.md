### Every COH path crosses an explicit interface — no concrete COH types outside Library/

- **Reference:** `architecture-specification.md` §Mechanism: COH Game Bridge Seam — Principle
- **DO:** Reference `IGameCommandExecutor`, `IMemoryInstance`, and `IIconInteractionUtility` everywhere outside `Library/`. Receive them via constructor injection. Test doubles replace them in all Tier 1–3 tests.
- **DO NOT:** Reference `HookCostumeGameCommandExecutor`, `MemoryInstance`, `MemoryElement`, `IconInteractionUtility`, or `GameCommandExecution.ActiveExecutor` in any domain class, ViewModel, or unit test.

**Example (wrong):**
```csharp
// Domain class directly calls concrete executor — violates the seam
public class Crowd
{
    public void Spawn(Character c)
    {
        var cmd = KeyBindsGenerator.Build(GameEvent.SpawnNpc, c.Surface, c.Name);
        HookCostumeGameCommandExecutor.Instance.ExecuteCmd(cmd);  // concrete type in domain
    }
}
```

**Example (pass):**
```csharp
// Domain class uses injected interface — concrete type unknown to domain
public class Crowd
{
    private readonly IGameCommandExecutor _executor;

    public Crowd(IGameCommandExecutor executor) { _executor = executor; }

    public void Spawn(Character c)
    {
        var cmd = KeyBindsGenerator.Build(GameEvent.SpawnNpc, c.Surface, c.Name);
        _executor.ExecuteCmd(cmd);  // seam — real in prod, NoOp in tests
    }
}
```

- **Likely source:** `instruction not read`
