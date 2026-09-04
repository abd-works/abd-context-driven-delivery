Run the action on cdd at spec fidelity through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: spec
action: generate
```
.\tools.ps1 run -
