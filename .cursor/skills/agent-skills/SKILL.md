---
name: agent-skills
description: "Deploy workspace toolsets as IDE shims — one skill per toolset."
disable-model-invocation: true
---

# AgentSkills

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest agent_skills.agent_skills:AgentSkills
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
