# tools

*Tools* are standalone toolsets an agent or an application calls beside the practices: *SubAgent* hands work to a background sub-agent, *Echo* shows an action's instructions inside a do-not-follow fence, *Granola* files meeting notes and writes the ones that matter as `.context` files, *PromptLog* writes what crossed to the model into the open session's logs, and *PromptNotify* shows a toast naming the guidance a tool call used. Each sits in its own package (`tools/sub_agent`, `tools/echo`, `tools/granola`, `tools/prompt_log`, `tools/prompt_notify`) and imports none of the others; they share one card, `tools/.context/module-context.md`. `tools/drawio_viewer` is a small local web server beside them, not a toolset, and imports nothing from the framework. Nothing in the framework imports this module. The whole model of PromptNotify, internals included, is `tools/prompt_notify/.context/prompt-notify-model.md`; that document is canonical for it.

- **Purpose:** Hold the toolsets that are useful on their own, outside any one practice or action: delegating to a sub-agent, reading what an action instructs, filing meeting notes as context, and showing and logging what crosses to the model.
- **Seam (terms):** SubAgent, Echo, Granola, PromptLog, PromptNotify, ToastFile
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/mcp, harness/guidance, space/session

## SubAgent

Launch a non-blocking sub-agent with custom instructions, and continue the current conversation without waiting for it.

------
----
+ sub_agent(instructions: str, summary: str = ''): str
	// never called from inside the sub-agent it launched
---<<opens its instructions with>>--> SUB_AGENT_CALLER_PREAMBLE
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill
---<<annotated with>>--> AgentInstructionsAnnotation

## Echo

Echo wrapped action instructions inside a DO-NOT-FOLLOW fence so the user can inspect them.

------
----
+ fence(body: str): str
+ echo_session(): str
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill
---<<annotated with>>--> NoCatalog

## Granola

Organize Granola notes into folders and capture notes as independent .context files, in the project the call works on.

+ Granola(project: Path | str)
------
+ root: Path
----
+ of_project(project: Path): Granola
+ format_filing_plan(plan: str): str
+ list_note_context(folder: str): str
+ write_note_context(folder: str, note_id: str, title: str, date: str, url: str, content: str): str
+ organize(scope: str = 'unfiled'): str
+ context(notes: str, folder: str): str
---<<creates>>--> Name
---<<writes under>>--> CONTEXT_FOLDER
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill

## PromptLog

Audit what the IDE sends the model — one `@Hook` per event, each writing that event's entry to the log: the file the toolset was made with, else `prompt-log.txt` in the logs folder of the session the event works in.

+ PromptLog(log: Path | None = None)
------
----
+ log_for(payload: HookPayload): HookLog
	-> HookPayload.session
	-> SessionFolder.hook_log
+ before_submit_prompt(payload: HookPayload): dict
+ before_read_file(payload: HookPayload): dict
+ pre_tool_use(payload: HookPayload): dict
+ subagent_start(payload: HookPayload): dict
+ after_agent_response(payload: HookPayload): dict
---<<writes entries as>>--> PromptLogEntry
---<<appends to>>--> HookLog
---<<stamps entries with>>--> LogTimestamp
---<<asks the installed guidance kind of>>--> IdeLayout
---<<reads invoked tool of>>--> HookPayload
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Hooks
---<<annotated with>>--> Hook
---<<annotated with>>--> NoCatalog

## PromptNotify

Echo detected action, practice, fidelity, and rule names on preToolUse.

------
+ catalog: list[tuple[str, str]]
+ echo_toolsets: list
----
+ on_pre_tool_use(payload: HookPayload): dict
+ handle(payload: HookPayload, toolsets: list | None = None): dict
+ detect_echo(payload: HookPayload, toolsets: list | None = None): tuple[str, str] | None
+ detect(payload: HookPayload): tuple[str, str] | None
+ show_toast(toast: str, workspace_roots: list[Path]): list[Path]
	// registered with HOOK_TOASTS.show_with when the module is loaded, so the toast a hook gives in its result is shown here
+ show_ide_toast(echo: str, workspace_roots: list[Path | str]): list[Path]
	-> ToastFile.show
+ install_ide_toast_extension(): Path
---<<lists action names from>>--> ActionCatalogue
---<<lists practices from>>--> PracticeCatalogue
---<<loads the running checkout's toolsets from>>--> RepositoryToolsets
---<<loads>>--> AgentToolSet
---<<asks the installed guidance kind of>>--> IdeLayout
---<<reads workspace roots of>>--> HookPayload
---<<reads invoked tool of>>--> HookPayload
---<<registers its toaster with>>--> HookServer
---<<joins rule toasts with>>--> rules_toast
---<<creates>>--> Name
---<<creates>>--> ToastFile
---<<toasts the calls annotated>>--> Toast
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Hook
---<<annotated with>>--> NoCatalog

## ToastFile

The toast notice of one workspace folder, `.cursor/prompt-notify-toast.json`, which the IDE toast extension shows. A toast written within a moment of the last one joins it, so a burst of tool calls shows as one toast.

+ ToastFile(folder: Path)
------
+ path: Path
----
+ show(message: str, now: datetime): Path
---<<reads and writes>>--> JsonFile
---<<stamps the toast with>>--> LogTimestamp
