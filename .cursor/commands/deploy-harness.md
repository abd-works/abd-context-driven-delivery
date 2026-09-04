With no IDE given, AskQuestion: Which IDE? Cursor | VS Code. With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring. With no deploy path given, call suggested_deploy_path, then AskQuestion: deploy to that suggested path (recommended) / enter another path. Set context.type to the chosen IDE before running.

Required context params with no value: type. AskQuestion to collect each missing value before running.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: harness.harness:Harness
context:
  type: 
tool: write_deploy
```
.\tools.ps1 run -
