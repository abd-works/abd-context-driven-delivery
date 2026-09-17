---
fidelity: [discovery]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — Context-Driven Delivery Framework incremental backlog

## Product / context

**Product:** Context-Driven Delivery — primitives that turn a Python class into an agentic toolset, install it by destination, and let an agent invoke it through MCP, hooks, guidance, and lifecycle actions.

**Slicing intent:** Prove register → install markdown files plus MCP → invoke those writes before extract, hooks, or practice hosts.

**Spine vs optional:** The mandatory spine is **register agent toolset → publish markdown files and MCP → invoke those → use context guidance (install skill/.mdc, collect instructions, generate under rules) → use practice guidance (register guidance and fidelities, invoke both scopes, shared and fidelity rules constrain output) → hook dispatch → extract markdown → lifecycle actions**. Destination-path bookkeeping and extra IDEs ride later.

## Increments

### Increment 1: `Walking skeleton — register, install markdown files and MCP, invoke them`

**Outcome:** An author registers an Agent Toolset. Markdown Installation writes skill, slash command, and rules in one story. Mcp Installation writes `mcp.json`. The agent follows those markdown files and triggers the MCP prompt.

**Slicing notes:** Cursor defaults only. Skill, command, and rules share one mechanic — one story, variations later. Hook dispatch waits.

**Stories in this increment** *(order reflects flow within the slice):*

- *Register Agent Toolsets*
- *Register Agent Instructions*
- *Publish Markdown Files*
- *Publish Mcp Manifest*
- *Follow Skill File*
- *Start Slash Command*
- *Trigger Mcp Prompt*

### Increment 2: `Context guidance — install, invoke instructions, generate under rules`

**Outcome:** Guidance installs as skill and `.mdc` rules. Invoke returns `instructions`. Generate produces content those rules constrain.

**Slicing notes:** One Guidance host. Same Markdown Installation write as agent toolsets. No fidelities yet.

**Stories in this increment:**

- *Register Guidance*
- *Publish Guidance Files*
- *Collect Guidance Instructions*
- *Generate Guided Content*
- *Constrain Valid Output*

### Increment 3: `Practice guidance — register guidance and fidelities, invoke both, rules guide output`

**Outcome:** Practice Guidance registers Guidance and Fidelities. Invoke at practice scope and at fidelity scope. Shared rules and fidelity-specific rules each constrain the matching AI output.

**Slicing notes:** No separate register-practice epic. Practice Guidance *is* Guidance plus fidelities. Hook events wait.

**Stories in this increment:**

- *Register Guidance*
- *Register Fidelities*
- *Collect Guidance Instructions*
- *Collect Fidelity Instructions*
- *Constrain Shared Output*
- *Constrain Fidelity Output*

### Increment 4: `Lifecycle actions — register kits and close the generate loop`

**Outcome:** An author registers action tools and a prompt. Generate, validate, and scan run against context guidance the same way a practice recipe does.

**Slicing notes:** Same marks as practice guidance. Partition, grill, sketch, and iterate wait for increment 5 so the generate loop is proven first.

**Stories in this increment:**

- *Register Action Tools*
- *Register Action Prompt*
- *Generate Context Guidance*
- *Validate Context Guidance*
- *Scan Context Guidance*
- *Start Action Prompt*

### Increment 5: `Shaping kits — partition, grill, sketch, iterate`

**Outcome:** The agent can partition, grill, sketch, and iterate context guidance before or after generate.

**Slicing notes:** Outer slash names from the actions kit table (`/partition`, `/grill`, `/sketch`, `/iterate`). Inner corpus actions stay off the map.

**Stories in this increment:**

- *Partition Context Guidance*
- *Grill Context Guidance*
- *Sketch Context Guidance*
- *Iterate Context Guidance*

### Increment 6: `Produce and check kits — document, render, satisfy, repair`

**Outcome:** Document, render, satisfy, repair, and create-rule run against the same context guidance host.

**Slicing notes:** `/createRule` lives on the validate kit. `/repair` is the improvement kit.

**Stories in this increment:**

- *Document Context Guidance*
- *Render Context Guidance*
- *Satisfy Context Guidance*
- *Repair Context Guidance*
- *Create Context Rule*
