# tools/prompt_notify
*PromptNotify* shows an IDE toast naming the action, practice, fidelity, or guideline an agent has just invoked, so a person watching the chat sees which guidance is being used. It handles the `preToolUse` hook, writes the notice to `.cursor/prompt-notify-toast.json` in each workspace folder, and installs the IDE toast extension that shows it.

`@Toast` is the mark an author puts on an `@agent_tool` or `@agent_instructions` member so that calling it toasts. `harness/guidance_actions` marks the step every guidance action starts with, so each action toasts without its own mark.

- **Purpose:** Make the guidance an agent is following visible to the person while it runs.
- **Seam (terms):** PromptNotify, ToastFile, `PromptNotify.show_toast`; it reads the mark `@Toast` (harness/marks)
- **Dependencies (one-way):** `harness/agent_tools`, `harness/installation` (`noCatalog`), `harness/installer` (*Installer*, whose toolsets carry the `@Toast` marks), `harness/name` (*Name*), `space/session` (`SessionLog.timestamp`, the time a toast is stamped with), and, read when the catalogue is first built, `harness/guidance` (*PracticeCatalogue*, and *ActionCatalogue*, whose actions are the action names it toasts). `harness/marks` (`@Toast`), and `harness/hooks` (*Hook*, and *HookServer*: this module registers `PromptNotify.show_toast` with `HookServer.show_toasts_with` when it is loaded, so the toast a hook gives in its result is shown here; `TOAST_ARROW` and `rules_toast` for joining the toasts of one burst). Nothing in the framework imports this module.

## Constraint

Mark members with `@Toast`. Practice and fidelity `instructions` toast only when those members are marked, never because the step every action starts with is marked. Toasts that arrive in the same burst join their rule lines under one `rules :` prefix; a later matching guideline never overwrites an earlier one.
