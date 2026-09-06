### Tier 1 domain tests are pure — no ViewModel imports, no live COH

- **Reference:** `architecture-specification.md` §Testing Architecture — Tier 1
- **DO:** Construct domain classes directly with `FakeMemoryInstance` and `NoOpGameCommandExecutor`. Assert domain post-state. Keep Tier 1 test classes in `Module.UnitTest/Domain/`. Use one `[TestClass]` per story and one `[TestMethod]` per scenario with Given/When/Then naming.
- **DO NOT:** Import `BindableBase`, `DelegateCommand`, `ObservableCollection` (Prism UI types), any ViewModel class, or any concrete COH class (`MemoryInstance`, `HookCostumeGameCommandExecutor`, `IconInteractionUtility`) in a Tier 1 test.

**Example (wrong):**
```csharp
[TestClass]
public class TestIdentityDomain
{
    [TestMethod]
    public void WhenAddIdentity_ThenViewModelUpdates()
    {
        // Pulls in ViewModel — Tier 1 test should only touch domain
        var vm = new IdentityEditorViewModel(new Character(...));
        vm.AddIdentityCommand.Execute();
        vm.Identities.Should().HaveCount(1);  // asserting VM, not domain
    }
}
```

**Example (pass):**
```csharp
[TestClass]
public class TestIdentityDomain
{
    private Character _character = null!;

    [TestInitialize]
    public void GivenACharacterWithNoIdentities()
    {
        _character = new Character(new NoOpGameCommandExecutor(), new FakeMemoryInstance());
    }

    [TestMethod]
    public void WhenIdentityAdded_ThenIdentitiesContainsIt()
    {
        var id = new Identity("Statesman");
        _character.Identities.Add(id);
        _character.Identities.Should().Contain(id);
    }
}
```

- **Likely source:** `instruction not read`
