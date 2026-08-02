# agent_skills — module context

## Purpose
Scans the workspace for Python toolset files and deploys each as a IDE skill shim. For every discovered toolset it writes a `SKILL.md` file (under `.cursor/skills/` or `.github/skills/` depending on IDE), removes stale shortcuts, and merges the manifest-gate hook into the IDE hooks config. A saved deploy-state file lets subsequent runs re-deploy without re-asking for parameters.

## Seam
`AgentSkills`

## Dependencies
`primitives.actions`, `tools.tool`, `tools.toolset_header`, `focus._decorator`

## Mechanism
Static-analysis pass over each toolset's source file (`ast.parse`) extracts `@focus`-decorated action names and their focus-group subdirectories, producing per-focus shortcut descriptors that drive shim generation and stale-slug cleanup.
