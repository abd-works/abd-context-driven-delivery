# PromptEcho — class model (model fidelity)

Markdown channel for *Echo* and *PromptEcho*. Same types as `prompt-echo-model.py`.

**Out of scope:** putting `@echo` on every kit method now.

---

## Language

*Echo* is a *Destination* mark. It sets `_echo` on the callable. *AgentOperation* and *AgentInstructions* both accept it — `begin` and `instructions` are *AgentInstructions*.

*PromptEcho* is the `preToolUse` *Hook*. It toasts the invoked member when that callable has `_echo`. If not, and the toolset inherits `begin` with `_echo`, it toasts **Action →** the kit name. *catalog* names action, practice, fidelity, and guideline tokens for path and MCP matching when no Echo mark hits.

### echo

- `@echo` on a member — that invoke toasts.
- `@echo` on `GuidanceAction.begin` — every kit invoke toasts as Action, because every kit runs `begin`.
- **Invariant:** `run` always calls `begin`. *Sketch* and *GrillContext* call `begin` without `run`.

### prompt echo

- `handle` looks at the invoked MCP member first, then inherited `begin`, then *catalog*.
- **Invariant:** practice/fidelity `instructions` toasts only when those members are marked — never because `begin` is marked.
- **Invariant:** `show_ide_toast` must join same-burst inject lines. A later matching glob must never overwrite an earlier Guidance.

---

# installation/hooks/prompt_echo
- **Purpose:** Mark members with *Echo* and toast on `preToolUse`.
- **Seam (terms):** Echo, PromptEcho, catalog, detect, detect_echo, handle, show_ide_toast, inject_rules_toast
- **Dependencies (one-way):** installation (Destination), installation/hooks (HookPayload, HookResult), harness/agent_tools (AgentTool, AgentToolSet)

## Echo : Destination

*Echo* marks an AgentOperation or AgentInstructions so PromptEcho toasts it.

Echo()
------
flag: str
----
annotate(operation): operation
	// must set _echo on the callable
	// must apply to AgentInstructions as well as AgentOperation

## PromptEcho

*PromptEcho* is the preToolUse hook. It toasts when the invoked member, or inherited begin, is marked Echo.

PromptEcho()
------
catalog: list[tuple[str, str]]
	// must be longest-token-first
	// always includes fallback action names
----
on_pre_tool_use(hook_payload: HookPayload): HookResult
	// after handle, always show_ide_toast when user_message is present
	-> PromptEcho.handle
	-> PromptEcho.show_ide_toast
handle(hook_payload: HookPayload, toolsets: list[AgentToolSet] | None): HookResult
	// empty tool_name must allow quietly
	// must try detect_echo before detect
detect_echo(hook_payload: HookPayload, toolsets: list[AgentToolSet] | None): tuple[str, str] | None
	// never treat inherited begin as the echo for instructions
	// never toast open_workspace, end, or begin from inherited begin
	-> PromptEcho.echo_toolsets
detect(hook_payload: HookPayload): tuple[str, str] | None
	// never toast an action from a path haystack
	// always name a guideline when the haystack is a rules path
echo_toolsets(repo: Path | None): list[AgentToolSet]
	-> AgentToolSet.load_toolsets
show_ide_toast(echo: str, repo: Path | None): Path
	// must join same-burst inject lines
	// never overwrite an earlier Guidance in that burst
inject_rules_toast(source: str, labels: list[str]): str
	// always prefix the joined names with rules :
toast_notice(echo: str): dict[str, str]
install_ide_toast_extension(): Path

---

# harness/guidance_actions
- **Purpose:** One *Echo* on `begin` covers every action kit.
- **Seam (terms):** GuidanceAction.begin
- **Dependencies (one-way):** installation/hooks/prompt_echo (Echo, inject_rules_toast, show_ide_toast)

## GuidanceAction

GuidanceAction()
------
----
begin(guidance, action: str): str
	// always the one action Echo mark
run(guidance, operation, action: str): list
	// always calls begin
	-> begin
open_workspace(name: str, path: str): str
	// never the action echo
inject_rules(hook_payload: HookPayload): HookResult
	-> PromptEcho.inject_rules_toast
	-> PromptEcho.show_ide_toast

## Generate : GuidanceAction

Generate()
------
----
generate(guidance): str
	-> run

## Sketch : GuidanceAction

Sketch()
------
----
sketch(guidance): str
	-> begin

---

# harness/guidance
- **Purpose:** Practice and fidelity prompts toast independently of actions.
- **Seam (terms):** PracticeGuidance.instructions, FidelityGuidance.instructions
- **Dependencies (one-way):** installation/hooks/prompt_echo (Echo)

## PracticeGuidance

PracticeGuidance()
------
----
instructions(): str
	// never inherit action echo from begin

## FidelityGuidance

FidelityGuidance()
------
----
instructions(): str
	// never inherit action echo from begin
