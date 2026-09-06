# Grill Answers

### Instruction and rule write paths

Write roots follow `utilities/agent_skills`: Cursor `.cursor/`, VS Code `.github/`. Cursor has no instruction files. An instruction is not ignored: on Cursor it deploys as a rule (`.cursor/rules/{name}.mdc`). On VS Code it writes `.github/instructions/{name}.instructions.md`. A rule on VS Code deploys as an instruction.

### Prompt and command

Cursor has no prompt files. A prompt is not ignored: on Cursor it deploys as a command (`.cursor/commands/{name}.md`). On VS Code it writes `.github/prompts/{name}.prompt.md`. A command on VS Code deploys as a prompt. Prompt and command are the same kind.

### Format commands

Format is not a fidelity. Hardcoded list for now, from CleanEngineering `_CHANNELS` and Stories `_CHANNELS`: markdown, json, drawio, miro, python, typescript, java, javascript. Each is a prompt (`@prompt`); on Cursor it deploys as a command. Body: run the context tool / actions using the following format, then name that format. Used mostly with generate and render.

### Generate is the deploy

`Harness.generate` is `@agent_instructions`. If no IDE is given, AskQuestion: Cursor or VS Code. Then construct `Harness(type)` and write skills, commands, formats, and the rest into that IDE's deploy area. One operation — generate is the deploy. `generate(source)` writes one source; no source walks then generates each. No confirm list for the scan.

### Stale files

Same as agent_skills: overwrite generated files; remove stale shortcuts and old slugs (`grill-context`, per-focus×action commands). Cursor multi-folder writes follow agent_skills (`~/.cursor` and workspace-parent `.cursor`).

### Decorators are the classes

Annotations are the VS Code names only: `@skill` from Skill, `@prompt` from Prompt, `@instruction` from Instruction. No `@command` or `@rule` — those are Cursor equivalents written at generate time (`@prompt` → command, `@instruction` → rule). They go on the operation. Unannotated sources still get the default write (context tool → skill, action → prompt). Optional `name` on the decorator; default is the package / module slug.

### generateAgain

Same as agent_skills `save_state` / `deploy_again`. After generate, save the last IDE. `generateAgain` is `@agent_tool`: write with no questions using the saved IDE. No saved state → refuse.

### How generate is run

Same two commands as every other agentic operation (grill, sketch, today’s agent_skills):

```
python -m tools manifest harness.harness:Harness
python -m tools run _req.yaml
```

That is how the agent loads `generate` / `generateAgain`. AgentSkills is not the owner of that run.

### AgentSkills folder

Delete `utilities/agent_skills` this slice. Harness owns generate.

### First generate

First run is the two CLI commands (no committed Harness SKILL.md). Generate also writes Harness itself as a skill and a prompt, even though `primitives/` is not in the walk. Later runs are that skill or `/harness`.

### Batch from agent_skills (2026-08-26)

1. Name filter — AskQuestion all toolsets (recommended) / substring. Still no confirm of the scanned list.
2. `/scaffold` is a separate action prompt (ActionBody), not a fidelity.
3. Tool-specific fidelity prompts from each tool's table: Stories `story_map` / `scenarios` / `acceptance_tests`; DDD `bounded_context` / `building_blocks` / `tactics`; CleanEngineering `modules` / `model` / `specification` / `code`; UX `ia` / `mockup` / `front_end_code`; also BDD `modules` / `behavior` / `development` and CDD `spec` / `engineer`. Plus CDD stages `discovery` / `specification` / `engineering`.
4. `echo` and `handoff` write as prompts (Cursor: commands).
5. Do not set `disable-model-invocation` on generated SKILL.md.
6. Keep clean. `@prompt` on that operation so generate knows the file kind — one deployment per Harness type, not both IDEs.
7. Saved-state file beside the Harness package.
8. ActionBody stays as already sketched. Do not port the agent_skills kit-owned / chain-tools recipe.

