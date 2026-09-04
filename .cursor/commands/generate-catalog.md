Render the whole catalog into ``self.out_root`` with Foundry chrome.
No output is ever written outside ``out_root``.

Required context params with no value: repo_url, ref, out_root, catalog_context_tool, catalog_action, catalog_utility. AskQuestion to collect each missing value before running.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: catalog_generator.catalog_generator:Catalog
context:
  repo_url: 
  ref: 
  out_root: 
  catalog_context_tool: 
  catalog_action: 
  catalog_utility: 
```
.\tools.ps1 run -
