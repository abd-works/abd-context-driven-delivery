finish_work_session - agent closes the current work session.

through the tools cli

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: workspace.workspace:WorkSession
tool: finish_work_session
```
python -m tools run -
