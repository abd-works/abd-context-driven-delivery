Run the action on stories at acceptance_tests fidelity through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.stories.stories:Stories
context:
  fidelity: acceptance_tests
action: generate
```
.\tools.ps1 run -
