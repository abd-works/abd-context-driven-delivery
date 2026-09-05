### Address offsets belong to MemoryInstance — never to domain classes

- **Reference:** `architecture-specification.md` §Mechanism: Direct Memory Manipulation — Principle
- **DO:** Domain classes call `IMemoryInstance` semantic methods (`SetPosition`, `SetFacing`, `ReadXYZ`, `SetFXFlag`). All COH pointer chains and offset constants live only in `MemoryInstance.cs`.
- **DO NOT:** Import `MemorySharp` from a domain class, ViewModel, or test. Do not define memory address constants outside `Library/ProcessCommunicator/`. Do not call `MemorySharp` write/read methods directly from the domain.

**Example (wrong):**
```csharp
// Domain class holding offsets and calling MemorySharp directly
using MemorySharp;

public class Movement
{
    private static readonly int FacingOffset = 0x2A3C44;  // offset in domain — wrong

    public void TurnTo(float angle)
    {
        using var mem = new MemorySharp(Process.GetCurrentProcess());
        mem[FacingOffset].Write(angle);  // MemorySharp in domain — wrong
    }
}
```

**Example (pass):**
```csharp
// Domain describes what to do; IMemoryInstance resolves where in memory
public class Movement
{
    private readonly IMemoryInstance _memory;

    public Movement(IMemoryInstance memory) { _memory = memory; }

    public void TurnTo(float angle)
    {
        var saved = _memory.ReadXYZ();
        _memory.SetFacing(angle);
        _memory.SetPosition(saved.X, saved.Y, saved.Z);
    }
}
```

- **Likely source:** `instruction not read`
