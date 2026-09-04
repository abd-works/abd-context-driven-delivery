Run the action on bdd at behavior fidelity through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: behavior
action: generate
```
.\tools.ps1 run -
