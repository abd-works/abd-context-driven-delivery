# PromptNotify — class model (model fidelity)

Markdown channel for *Toast* and *PromptNotify*. The classes other modules own (*GuidanceAction*, *PracticeGuidance*, *Destination*, *Hook*) appear only as names this module uses; their own cards describe them.

---

## Language

*Toast* is a *Destination* mark. Put it on an `@agent_tool` or `@agent_instructions` member, and an agent's call to that member shows an IDE toast naming it. `harness/guidance_actions` marks `GuidanceAction.begin`, the step every guidance action starts with, so each action toasts as **Action →** its name without its own mark.

*PromptNotify* is the `preToolUse` *Hook*. It looks at the invoked member first, then at a toolset's inherited `begin`, then at its *catalog* of action, practice, fidelity, and guideline names, and writes the first match as a toast notice into each workspace folder.

- **Invariant:** practice and fidelity `instructions` toast only when those members carry *Toast* — never because `begin` is marked.
- **Invariant:** toasts in the same burst join their rule lines under one `rules :` prefix; a later matching guideline never overwrites an earlier one.

---

# tools/prompt_notify
- **Purpose:** Make the guidance an agent is following visible to the person while it runs.
- **Seam (terms):** Toast, PromptNotify
- **Dependencies (one-way):** harness/installation (Destination), harness/hooks (Hook), harness/agent_tools (AgentToolSet), harness/guidance (PracticeCatalogue)

## Toast : Destination

*Toast* marks an AgentOperation or AgentInstructions so PromptNotify toasts it when an agent calls it.

Toast()
------
flag: str
----

## PromptNotify

*PromptNotify* is the preToolUse hook. It toasts when the invoked member, or an inherited begin, carries *Toast*.

PromptNotify()
------
catalog: list[tuple[str, str]]
	// longest name first, so a fidelity matches before its practice
----
on_pre_tool_use(hook_payload: dict): dict
	-> PromptNotify.install_ide_toast_extension
	-> PromptNotify.handle
	-> PromptNotify.show_ide_toast
handle(hook_payload: dict, toolsets: list | None): dict
	// an empty tool_name allows quietly
	// tries detect_echo before detect
detect_echo(hook_payload: dict, toolsets: list | None): tuple[str, str] | None
	// never treats an inherited begin as the toast for instructions
	// never toasts open_workspace, end, or begin from an inherited begin
	-> PromptNotify.echo_toolsets
detect(hook_payload: dict): tuple[str, str] | None
	// never toasts an action from a path
	// names a guideline when the path is a rules path
echo_toolsets(repo: Path | None): list
show_ide_toast(echo: str): Path
	// joins same-burst rule lines; never overwrites an earlier guideline in that burst
show_toast(toast: str, workspace_roots: list[Path]): Path
	// prefixes the joined names with rules :
chat_edit_source(hook_payload: dict | None): str
toast_notice(echo: str): dict[str, str]
install_ide_toast_extension(): Path
