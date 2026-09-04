Render the whole catalog into ``self.out_root`` with Foundry chrome.
No output is ever written outside ``out_root``.

through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: catalog_generator.catalog_generator:Catalog
```
python -m tools run -
