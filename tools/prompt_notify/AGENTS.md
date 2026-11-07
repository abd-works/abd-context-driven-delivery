# prompt notify

- **A practice toast is the invoked practice or fidelity tool.** A path or command that merely contains `stories`, `ddd`, or `clean-engineering` does not toast. Skill and rule files under `.cursor/skills` and `.cursor/rules` still do. Same-burst `Practice` or `Fidelity` echoes stay separate; only rules lines join under `rules :`.
- **A hook gives its toast back in its `HookResult`; the hook server hands it to the notifier.** `PromptNotify` registers itself with `HookServer.show_toasts_with`. A toast is never sent to the IDE as hook output.
- **The rules toast names what injected the rules, then each rule set** (`rules_toast` in the hook server): `{source} → rules : clean engineering code, ddd tactics`. File saves arrive on `afterFileEdit`; `postToolUse` does not see them.
- **`ToastFile` joins same-burst rules toasts.** Two rules toasts written within a moment become one toast with one `rules :` prefix, and a later matching glob does not overwrite an earlier rule set.
- **The IDE toast watches every workspace folder** for `.cursor/prompt-notify-toast.json`. Write the notice into each `workspace_roots` folder from the hook payload, so it shows whichever folder the file lives in.
