# PromptEcho @echo — class model (model fidelity)

Markdown channel for the *Echo* destination and *PromptEcho* lookup. Target: one `@echo` on `GuidanceAction.begin` covers every action kit; `@echo` on practice/fidelity `instructions` is independent. A later `@echo` on a kit recipe still toasts that invoke.

**Out of scope:** catalog/path matching that PromptEcho uses today; `open_workspace` as the action echo; putting `@echo` on every kit method now.

---

## Language

*Echo* is a *Destination* mark. It sets `_echo` on the callable. *AgentOperation* and *AgentInstructions* both accept it — `begin` and `instructions` are *AgentInstructions*.

*PromptEcho* is the `preToolUse` *Hook*. It toasts the invoked member when that callable has `_echo`. If not, and the toolset inherits `begin` with `_echo`, it toasts **Action →** the kit name.

### echo

- `@echo` on a member — that invoke toasts.
- `@echo` on `GuidanceAction.begin` — every kit invoke toasts as Action, because every kit runs `begin`.
- **Invariant:** `run` always calls `begin`. *Sketch* and *GrillContext* call `begin` without `run`.

### prompt echo

- `handle` looks at the invoked MCP member first, then inherited `begin`.
- **Invariant:** practice/fidelity `instructions` toasts only when those members are marked — not because `begin` is marked.

---

# installation/hooks/prompt_echo

- **Purpose:** Mark members with *Echo* and toast on `preToolUse`.
- **Seam (terms):** Echo, PromptEcho
- **Dependencies (one-way):** installation (Destination), harness/agent_tools (AgentTool), harness/guidance_actions (GuidanceAction.begin), harness/guidance (instructions)

## Echo

Echo()
------
----
apply(operation): operation
	// sets _echo on the callable
	// AgentOperation and AgentInstructions

## PromptEcho

+ on_pre_tool_use(payload: dict): dict
	-> handle
+ handle(payload: dict): dict
	// invoked member _echo → toast that member
	// else toolset begin _echo → Action → kit name
	-> show_ide_toast

---

# harness/guidance_actions

- **Purpose:** One *Echo* on `begin` covers every action kit.
- **Seam (terms):** GuidanceAction.begin
- **Dependencies (one-way):** *(none for this mark)*

## GuidanceAction

+ begin(guidance, action: str): str
	// @echo — the one action mark
+ run(guidance, operation, action: str): list
	-> begin
+ open_workspace(name: str, path: str): str
	// not the action echo

---

# harness/guidance

- **Purpose:** Practice and fidelity prompts toast independently of actions.
- **Seam (terms):** PracticeGuidance.instructions, FidelityGuidance.instructions

## PracticeGuidance

+ instructions(): str
	// @echo independent of begin

## FidelityGuidance

+ instructions(): str
	// @echo independent of begin
