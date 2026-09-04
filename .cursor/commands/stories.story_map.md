Run the action on stories at story_map fidelity through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.stories.stories:Stories
context:
  fidelity: story_map
action: generate
```
python -m tools run -
