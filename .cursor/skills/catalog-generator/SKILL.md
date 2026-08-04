---
name: catalog-generator
description: "catalog_generator - discover-and-render primitives for the CDD HTML catalog."
disable-model-invocation: true
---

# CatalogGenerator

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest catalog_generator.catalog_generator:CatalogGenerator
```

Follow `response.instructions` before doing anything else. Invoke tools by writing
the request to a YAML file (e.g. `_req.yaml`) and running:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format — `toolset` is the classname from
the manifest step above:

```yaml
toolset: catalog_generator.catalog_generator:CatalogGenerator
context:
  key: value      # constructor params (fidelity, path, session, …)
tool: <tool_name>   # or action: <action_name>
arguments:
  key: value
```

Read `examples/` before guessing any field shape.
