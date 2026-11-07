# PromptNotify — class model (model fidelity)

Markdown channel for *PromptNotify*. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *Toast* belongs to `harness/marks`; *Hook*, *HookPayload*, and *HookServer* to `harness/hooks`; *PracticeCatalogue* and *ActionCatalogue* to `harness/guidance`; *GuidanceAction* to `harness/guidance_actions`. They appear here only as names this module uses.

---

## Language

*Toast* is the mark an author puts on an `@agent_tool` or `@agent_instructions` member so that an agent's call to that member shows an IDE toast naming it. `harness/guidance_actions` marks `GuidanceAction.begin`, the step every guidance action starts with, so each action toasts as **Action →** its name without its own mark.

*PromptNotify* is the `preToolUse` *Hook*. It looks at the invoked member first, then at a toolset's inherited `begin`, then at its *catalog* of action, practice, fidelity, and guideline names, and writes the first match as a toast notice into each workspace folder. When the module is loaded it registers `PromptNotify.show_toast` with `HookServer.show_toasts_with`, so the toast any hook gives in its result is shown here.

- **Invariant:** practice and fidelity `instructions` toast only when those members carry *Toast* — never because `begin` is marked.
- **Invariant:** toasts in the same burst join their rule lines under one `rules :` prefix; a later matching guideline never overwrites an earlier one.

---

## PromptNotify

*PromptNotify* is the preToolUse hook. It toasts when the invoked member, or an inherited begin, carries *Toast*.

PromptNotify(toast_roots: list[Path] | None = None)
------
toast_roots: list[Path] | None
	// the workspace folders a toast is written to besides this checkout
catalog: list[tuple[str, str]]
	// every practice, fidelity, practice rule file, and action name with its kind, longest first, so a fidelity matches before its practice; read once per process
	-> PracticeCatalogue.practices
	-> ActionCatalogue.names
----
on_pre_tool_use(payload: HookPayload): dict
	// @Hook("preToolUse")
	-> PromptNotify.install_ide_toast_extension
	-> PromptNotify.handle
	-> PromptNotify.show_toast(user_message, payload.workspace_roots)
handle(payload: HookPayload, toolsets: list | None): dict
	// an empty tool_name allows quietly
	// tries detect_echo before detect; the match becomes user_message "{Kind} → {label}"
detect_echo(payload: HookPayload, toolsets: list | None): tuple[str, str] | None
	// never treats an inherited begin as the toast for instructions
	// never toasts open_workspace, end, or begin from an inherited begin
	-> PromptNotify.echo_toolsets
detect(payload: HookPayload): tuple[str, str] | None
	// never toasts an action from a path
	// names a guideline when the path is a rules path
echo_toolsets(repo: Path | None): list
show_toast(toast: str, workspace_roots: list[Path]): Path
	// class operation the hook server calls for each merged toast
	-> PromptNotify(toast_roots=workspace_roots).show_ide_toast
show_ide_toast(echo: str): Path
	// joins same-burst rule lines under one "rules :" prefix; never overwrites an earlier guideline in that burst
chat_edit_source(payload: HookPayload): str
toast_notice(echo: str): dict[str, str]
install_ide_toast_extension(): Path
	// copies ide_toast into the Cursor extensions folder once per process
