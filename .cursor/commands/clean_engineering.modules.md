Run the action on clean_engineering at modules fidelity through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  fidelity: modules
action: generate
```
python -m tools run -
