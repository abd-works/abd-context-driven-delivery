Run the action on ux at front_end_code fidelity through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.ux.ux:Ux
context:
  fidelity: front_end_code
action: generate
```
python -m tools run -
