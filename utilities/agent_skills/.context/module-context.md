# agent_skills — module context

## Purpose
Scans the workspace for Python toolset files and deploys each as a IDE skill shim.
For every discovered toolset under `context_tools/` or `utilities/` it writes a
`SKILL.md` (under `.cursor/skills/` or `.github/skills/` depending on IDE), removes
stale shortcuts, and merges the manifest-gate hook into the IDE hooks config.

Packages under `context_tools/actions/` are **not** deployed as kit-manifest skills
(do not run `sketch.sketch:Sketcher` etc. directly). Instead, deploy writes:

- **Host-action skills + commands** named after the BaseContextTool action
  (`partition`, `grill`, `sketch`, `generate`, `document`, `iterate`, `validate`,
  `satisfy`, `repair`, `improve`). If one or more context tools are already in
  scope — passed in or named in chat (for example `/stories /ddd /iterate`) —
  run **each** tool's matching `action:` in that order, **except** kit-owned actions:
  `/iterate`, `/sketch`, `/grill`, `/partition`, `/generate`, `/validate`,
  `/document`, `/satisfy`, and `/repair` each run their kit once with
  `arguments.tools` listing those context tools. Cursor commands
  (`.cursor/commands/{action}.md`) and VS Code prompts get the same text.
- **CDD stage-fidelity commands** (`discovery`, `specification`, `engineering`) that
  only set `context.fidelity` on the in-scope context tool. Each tool maps the
  stage name to its concrete fidelity via `BaseContextTool.resolve_fidelity` /
  its `fidelities` table.
- **Companion skills + commands** for `echo` / `handoff`, which do run their own
  toolset in the current context-tool session frame.

A saved deploy-state file lets subsequent runs re-deploy without re-asking for
parameters. `deploy_filtered_toolsets` is the one write step the agentic deploy
action should call, so commands are not skipped.

When a nearby multi-folder `.code-workspace` includes this repo, Cursor deploys
also write to `~/.cursor/skills` (user-level, available in every project) and each
matching workspace file's parent `.cursor/skills` (shared sibling layout such as
`paradise-mobile/`). Junction checkouts are handled by walking both absolute and
resolve() path forms.

## Seam
`AgentSkills`

## Dependencies
`primitives.actions`, `tools.tool`, `tools.toolset_header`, `focus._decorator`

## Mechanism
Static-analysis pass over each toolset's source file (`ast.parse`) extracts
`@focus`-decorated action names and their focus-group subdirectories, producing
per-focus shortcut descriptors used only for stale-slug cleanup (legacy
per-focus×action commands are removed, not written). Action-package detection uses
path membership under `context_tools/actions/` (absolute + resolve() forms).
Deploy-root resolution walks ancestors (and sibling dirs) for `*.code-workspace`
files; multi-folder matches expand Cursor write targets beyond the repo root.
