### Game Bridge tests live in Module.IntegrationTest only — never in CI unit tests

- **Reference:** `architecture-specification.md` §Testing Architecture — Game Bridge tier
- **DO:** Place all tests that use live `MemoryInstance`, `HookCostumeGameCommandExecutor`, `IconInteractionUtility`, DLL injection, or `RunPatch()` in `Module.IntegrationTest/`. Mark them `[TestCategory("GameBridge")]`. Use `CohProcessBootstrap.RequireCohRunning(ctx)` in `[ClassInitialize]` so they skip when COH is not running.
- **DO NOT:** Put a `[TestCategory("GameBridge")]` test inside `Module.UnitTest`. Do not call `CohProcessBootstrap`, `RunPatch()`, or live COH types from any `Module.UnitTest` class. Game Bridge tests are invoked explicitly, never run in CI.

**Example (wrong):**
```csharp
// In Module.UnitTest — wrong project for a bridge test
[TestClass]
[TestCategory("GameBridge")]
public class TestLiveSpawn
{
    [TestMethod]
    public void WhenSpawned_ThenNpcAppearsInGame()
    {
        var character = new Character(new HookCostumeGameCommandExecutor(), new MemoryInstance());
        character.Spawn();  // requires live COH — should never be in Module.UnitTest
        character.IsSpawned.Should().BeTrue();
    }
}
```

**Example (pass):**
```csharp
// In Module.IntegrationTest — correct location for bridge tests
[TestClass]
[TestCategory("GameBridge")]
public class CommandBridgeTest
{
    [ClassInitialize]
    public static void RequireCohRunning(TestContext ctx) =>
        CohProcessBootstrap.RequireCohRunning(ctx);  // skip if COH not running

    [TestMethod]
    public void WhenSpawned_ThenNpcAppearsInGame()
    {
        var character = new Character(new HookCostumeGameCommandExecutor(), new MemoryInstance());
        character.Spawn();
        character.IsSpawned.Should().BeTrue();
    }
}
```

- **Likely source:** `instruction not read`
