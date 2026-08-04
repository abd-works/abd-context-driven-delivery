## CatalogFidelity

*CatalogFidelity* is the fidelity page for one stage.

CatalogFidelity(repo_url: str, ref: str, catalog_action: CatalogAction)
------
repo_url: str
ref: str
catalog_action: CatalogAction
----
generate_catalog(fidelity_name, owner): str

- **Interaction:** calls `CatalogAction.generate_catalog(action, owner)` once per lifecycle-action name, in BaseContextTool's declared source order, each name resolved via `owner.actions`
- **Invariant:** never mutates owner — read-only render of a live object
