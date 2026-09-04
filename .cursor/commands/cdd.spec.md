Run the action on cdd at spec fidelity through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: spec
action: generate
```
python -m tools run -
