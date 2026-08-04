## CatalogFidelity

*CatalogFidelity* is the fidelity page for one stage.

CatalogFidelity(repo_url: str, ref: str, catalog_action: CatalogAction)
------
repo_url: str
ref: str
catalog_action: CatalogAction
----
generate_catalog(fidelity_name, owner): str
  -> catalog_action.generate_catalog
  // once per lifecycle-action name, in BaseContextTool's declared source
  //   order (partition, grill, sketch, generate, document, iterate,
  //   validate, satisfy, repair)
  // never mutates owner — read-only render of a live object
