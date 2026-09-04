Run the action on ddd at bounded_context fidelity through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.ddd.ddd:Ddd
context:
  fidelity: bounded_context
action: generate
```
python -m tools run -
