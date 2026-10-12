# prompt echo

- **A practice toast is the invoked practice or fidelity tool.** A path or command that merely contains `stories`, `ddd`, or `clean-engineering` does not toast. Skill and rule files under `.cursor/skills` and `.cursor/rules` still do. Same-burst `Practice` or `Fidelity` echoes stay separate; only inject lines join under `rules :`.
- **The rules toast names the chat, not the file.** The name is Cursor's composer `name` for that `conversation_id`. A file path in the first message is not the title. File saves arrive on `afterFileEdit`; `postToolUse` does not see them.
- **`show_ide_toast` joins same-burst inject lines.** `chat {chat title} edited file → rules : agent bdd` then `chat {chat title} edited file → rules : clean engineering code, ddd tactics` becomes one toast with one `rules :` prefix. The title is that chat's title. A later matching glob must not overwrite an earlier Guidance.
- **The IDE toast watches every workspace folder** for `.cursor/prompt-echo-toast.json`. Write the notice into each `workspace_roots` folder from the hook payload so it shows no matter which folder the file lives in.
