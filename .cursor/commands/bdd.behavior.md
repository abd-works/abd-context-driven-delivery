Run the action on bdd at behavior fidelity through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: behavior
action: generate
```
python -m tools run -
