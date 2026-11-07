# tools/prompt_notify
*PromptNotify* shows an IDE toast naming the action, practice, fidelity, or guideline an agent has just invoked, so a person watching the chat sees which guidance is being used. It handles the `preToolUse` hook, writes the notice to `.cursor/prompt-notify-toast.json` in each workspace folder, and installs the IDE toast extension that shows it.

`@echo` is the mark an author puts on an `@agent_tool` or `@agent_instructions` member so that calling it toasts. `harness/guidance_actions` marks the step every guidance action starts with, so each action toasts without its own mark.

- **Purpose:** Make the guidance an agent is following visible to the person while it runs.
- **Seam (terms):** PromptNotify, the mark `@echo`
- **Dependencies (one-way):** `harness/agent_tools`, `harness/installation` (*Destination*, *Installer*, *Skill*), `harness/hooks` (*Hook*), and, read when the catalogue is first built, `harness/guidance` (*PracticeCatalogue*), `harness/guidance_actions` (*GuidanceAction*), and the action folders under `cdd_guidance/actions`, whose skill operations are the action names it toasts. `harness/guidance_actions` imports `@echo` and *PromptNotify*, and `harness/guidance` imports *PromptNotify* to toast injected rules, both through `sys.path` as `prompt_notify`; both of those modules are reached again from `harness/agent_tools`, which this module imports, so the framework reaches up into `tools` in a cycle tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Mark members with `@echo`. Practice and fidelity `instructions` toast only when those members are marked, never because the step every action starts with is marked. Toasts that arrive in the same burst join their rule lines under one `rules :` prefix; a later matching guideline never overwrites an earlier one.
