# prompt_echo

## Purpose

Mark AgentOperation and AgentInstructions with Echo, then toast the invoked action, practice, fidelity, or guideline on preToolUse.

## Seam (terms)

Echo, PromptEcho, catalog, detect, detect_echo, handle, show_ide_toast, inject_rules_toast

## Dependencies (one-way)

installation (Destination), installation/hooks (HookPayload, HookResult), harness/agent_tools (AgentTool, AgentToolSet)

## Constraint

Callers mark members with Echo. They must not treat inherited begin as the echo for practice or fidelity instructions. They must not overwrite an earlier Guidance when joining same-burst toasts.

## Primary use case

Cursor fires preToolUse. PromptEcho.handle names the invoked member from Echo, or from catalog when no mark hits, and show_ide_toast writes the notice. GuidanceAction.inject_rules joins rule names onto that toast in the same burst.

## Rationale

Echo lives on the callable so one mark on GuidanceAction.begin covers every kit. Practice and fidelity instructions keep their own marks so an action begin never speaks for them. Toast joining belongs on PromptEcho because that is the notice the IDE shows.

## Public API

- `@echo` / `Echo.annotate` — marks AgentOperation or AgentInstructions so PromptEcho toasts that invoke
- `PromptEcho.on_pre_tool_use(hook_payload)` — hook; handle then show_ide_toast
- `PromptEcho.handle(hook_payload, toolsets=None)` — detect_echo then detect
- `PromptEcho.detect_echo(hook_payload, toolsets=None)` — Echo on the invoked member or inherited begin
- `PromptEcho.detect(hook_payload)` — catalog token in MCP name or path
- `PromptEcho.show_ide_toast(echo, repo=None)` — write `.cursor/prompt-echo-toast.json`; join same-burst inject lines
- `PromptEcho.inject_rules_toast(source, labels)` — `{source} → rules : {labels}`
