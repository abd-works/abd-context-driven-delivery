Run the action on bdd at development fidelity through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: development
action: generate
```
python -m tools run -
