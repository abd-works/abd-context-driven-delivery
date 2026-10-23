Remove files from the previous install on this IDE path.

Run from the repository root with the Shell tool:

```text
python -c "from harness.agent_tools.agent_tools import AgentToolSet; print(AgentToolSet.instantiate(\"harness.installation.installer:Installer\").clean())"
```
