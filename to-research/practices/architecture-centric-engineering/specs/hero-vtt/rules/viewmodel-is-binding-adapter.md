### ViewModel is a binding adapter — not a controller

- **Reference:** `architecture-specification.md` §Mechanism: Skinny ViewModel — Principle
- **DO:** Every command handler delegates to exactly one domain method. The handler is a one-liner (or a one-liner plus a null guard). Observable properties are direct references to domain properties — no local copies, no manual sync.
- **DO NOT:** Put business logic, ordering logic, collection management, parallel dictionaries, or game internals inside a ViewModel.

**Example (wrong):**
```csharp
// Fat ViewModel — parallel collections kept in sync manually
private Dictionary<string, Identity> _identityMap = new();
private ObservableCollection<Identity> _identities = new();

private void AddIdentityHandler()
{
    var id = new Identity(_nameInput);
    if (!_identityMap.ContainsKey(id.Name))
    {
        _identityMap[id.Name] = id;
        _identities.Add(id);
        _identities.Sort(...);  // ordering logic in ViewModel
    }
}
```

**Example (pass):**
```csharp
// Skinny ViewModel — domain owns the rule; ViewModel is a one-liner
public ObservableCollection<IIdentity> Identities => _character.Identities;  // direct reference

private void AddIdentityHandler() =>
    _character.Identities.Add(new Identity(_nameInput));  // domain enforces uniqueness/ordering
```

- **Likely source:** `instruction not read`
