# tools

*Tools* are standalone toolsets an agent or an application calls beside the practices: *SubAgent* hands work to a background sub-agent, *Echo* shows an action's instructions inside a do-not-follow fence, *Granola* files meeting notes and writes the ones that matter as `.context` files, *PromptLog* writes what crossed to the model into the open session's logs, and *PromptNotify* shows a toast naming the guidance a tool call used. Each sits in its own package (`tools/sub_agent`, `tools/echo`, `tools/granola`, `tools/prompt_log`, `tools/prompt_notify`) and imports none of the others; they share one card, `tools/.context/module-context.md`. `tools/drawio_viewer` is a small local web server beside them, not a toolset, and imports nothing from the framework. Nothing in the framework imports this module. The whole model of PromptNotify, internals included, is `tools/prompt_notify/.context/prompt-notify-model.md`; that document is canonical for it.

- **Purpose:** Hold the toolsets that are useful on their own, outside any one practice or action: delegating to a sub-agent, reading what an action instructs, filing meeting notes as context, and showing and logging what crosses to the model.
- **Seam (terms):** SubAgent, Echo, Granola, PromptLog, PromptNotify, ToastFile, PromptQueue, ChatIdNotAnId, QueueFileUnreadable, StepStateUnknown
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/mcp, harness/guidance, harness/chat, space/session

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

## PromptQueue

The prompts one chat has queued, in the order they will be done, kept in a file in that chat's own folder. Several processes change one chat's queue, the stable lane's cdd server and the dev lane's among them, so each change holds the queue's file from its read to its write and no caller's change is lost.

+ PromptQueue(chat: str, file: Path, archive: Path | None = None)
------
+ chat: str
+ prompts: list[QueuedPrompt]
+ next: QueuedPrompt | None
	// the first prompt that waits (QueuedPrompt.is_waiting), where the queue's pointer stands; sent by its id
----
+ load(chat: str, call: ToolCall): PromptQueue
+ prompt(prompt: str): QueuedPrompt
	// raises PromptNotQueued for an id the queue does not hold
+ of_chat(chat: str, archive: Path | None = None): PromptQueue
	// a chat id is never a path: an empty one, or one holding a folder separator, a drive or two dots, raises ChatIdNotAnId
+ show(): PromptQueue
+ add(text: str): PromptQueue
+ add_all(texts: list[str]): PromptQueue
+ edit(prompt: str, text: str): PromptQueue
+ move(prompt: str, to: int): PromptQueue
+ remove(prompt: str): PromptQueue
	// the files attached to the prompt are deleted with it (QueuedPrompt.delete_attachments)
+ clear(): PromptQueue
	// takes off the done prompts only; with none done, nothing is taken off
+ done(prompt: str): PromptQueue
+ reopen(prompt: str): PromptQueue
+ assign(prompt: str, robot: str): PromptQueue
	// a robot already on the queue is matched with no regard to case or outer spaces, and keeps the spelling the queue first held
+ set_steps(prompt: str, steps: list[PromptStep]): PromptQueue
	// a step's state is one of STEP_STATES; any other raises StepStateUnknown
+ add_interruption(prompt: str, text: str): PromptQueue
+ step_done(prompt: str, step: int): PromptQueue
+ move_step(prompt: str, step: int, place: int): PromptQueue
+ remove_step(prompt: str, step: int): PromptQueue
+ step_back(prompt: str): PromptQueue
+ step_on(prompt: str): PromptQueue
+ attach(prompt: str, filename: str, media_type: str, data: str): PromptQueue
+ queue_once(source: str, texts: list[str]): int
---<<reads and writes through, holding it for each change>>--> JsonFile
---<<raises>>--> ChatIdNotAnId
---<<raises>>--> QueueFileUnreadable
---<<raises>>--> StepStateUnknown
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> NoCatalog
---<<holds>>--> QueuedPrompt

## QueuedPrompt

One prompt on a chat's queue. It changes itself; `record` is what the queue's file keeps of it, in exactly the keys the stable and dev lanes' servers read (id and text, and steps, attachments, is_done and robot only when it has them).

+ QueuedPrompt(record: dict)
------
+ id: str
+ text: str
+ << composition >> steps: PromptSteps
+ step_pointer: int
+ attachments: list[str]
+ is_done: bool
+ robot: str
+ is_waiting: bool
	// neither done nor asking a decision ([decision required])
+ record: dict
----
+ new(text: str): QueuedPrompt
+ edit(text: str)
+ mark_done()
+ reopen()
+ assign(robot: str)
+ plan(steps: list[PromptStep])
+ interrupt(text: str)
+ attach(file: Path)
+ delete_attachments(folder: Path)
	// as it leaves the queue: deletes its files in the chat's attachments folder, and its record names them as deleted_attachments

## PromptSteps

The steps planned for one queued prompt, numbered from 1, and their pointer, the first step not done.

+ PromptSteps(prompt: str, steps: list[PromptStep])
------
+ listed: list[PromptStep]
+ pointer: int
----
+ done(number: int)
+ move(step: int, place: int)
+ remove(step: int)
+ back()
+ on()
+ restarted()
+ plan(steps: list[PromptStep])
+ add(text: str)
---<<raises>>--> StepNotPlanned
---<<raises>>--> StepStateUnknown

## ChatIdNotAnId : ValueError

A call named a chat by something that is not a chat id: empty, or a path that leads out of the chat's own folder.

+ ChatIdNotAnId(chat: str)
------
+ chat: str
----

## QueueFileUnreadable : JsonFileUnreadable

A chat's queue file does not hold a prompt queue: it is damaged, cut off, empty, or holds something other than cards that each have an id of their own and a text. Nothing is written over it.

------
----
+ message(path: Path, cause: Exception): str

## StepStateUnknown : ValueError

A call gave a step a state that is none of the states a step has.

+ StepStateUnknown(state: str)
------
+ state: str
----
