# CDD MCP Migration Spec

## Goal

Replace the YAML/CLI invocation architecture with a minimal MCP-native runtime.

The target path is:

```
AI host
  ↓
MCP
  ↓
CDD annotated Python
  ↓
actual operation
```

CDD should keep only the abstractions that add useful semantics beyond MCP.

Everything that exists only to support YAML manifests, YAML requests/responses, CLI dispatch, duplicate signature handling, or agent-side transport instructions should be removed.

---

## Target CDD surface

Keep the authoring model small:

```python
@tool
def find_examples(...):
    """Tool description."""
    ...

@instruction
def bdd_thinking(self):
    """
    Think in states, substates, events and transitions.
    """
    tool(self.find_examples)
```

Semantics:

- `@tool` — declares an AI-callable operation; wraps/registers the callable with MCP
- `@instruction` — declares agent guidance/orchestration; docstring is the returned instruction content
- `tool(...)` — explicitly references an AI tool from an instruction

Do not retain parallel CDD abstractions for functionality already supplied by MCP unless they materially improve authoring ergonomics.

If manifest, schema, or runner abstractions become unnecessary, remove them.

Do **not** remove or redesign `@resource`, `@skill`, or `@prompt` as part of this migration — see [Out of scope](#out-of-scope--do-not-change).

---

## Out of scope — do not change

These CDD/harness annotations and their current behavior are **explicitly out of scope** for this refactor. Leave them untouched:

- **`@resource`** — observable toolset state (`primitives/tools`); property getters, instruction inlining, and any manifest/harness usage stay as they are today unless a separate change targets them.
- **`@skill`** — harness skill generation (`primitives/harness`); deployed `SKILL.md` artifacts and `@skill` discovery/writing behavior are unchanged by this migration.
- **`@prompt`** — harness prompt/command generation (`primitives/harness`); deployed prompt/command files and `@prompt(name=…)` behavior are unchanged by this migration.

This migration replaces **AI tool invocation transport** (YAML/CLI → MCP). It does **not** refactor harness deploy vehicles, read-only resources, or slash-command/prompt catalog authoring.

When deleting YAML/manifest/runner plumbing, do not delete or rewrite code whose primary job is implementing `@resource`, `@skill`, or `@prompt` unless that code is **only** used by the removed YAML/CLI path and has no remaining role for those annotations.

---

## MCP replaces the execution architecture

Do not wrap the existing CLI.

Do not translate MCP requests into YAML.

Do not keep `_ToolsetRunner` in the MCP path merely because it already exists.

Do not generate MCP schemas from YAML manifests.

The MCP server should call the underlying Python operation directly.

Target:

```
MCP call
  ↓
bound Python callable
  ↓
result
```

Not:

```
MCP call
  ↓
CDD request document
  ↓
YAML
  ↓
CLI
  ↓
generic dispatcher
  ↓
Python callable
```

---

## MCP server

Add one persistent local MCP server.

It should:

- discover CDD `@tool` operations;
- construct the required Python objects;
- register bound callables with MCP;
- remain alive across repeated calls;
- invoke those callables directly.

Assume a local single-user process.

Do not add per-user session architecture.

The live MCP process itself may retain:

- loaded modules;
- toolset instances;
- caches;
- workspace state;
- other useful in-memory state.

---

## Tool annotation

Keep CDD's `@tool`.

Its purpose should become very small:

1. mark the method as an AI-callable CDD operation;
2. preserve CDD's preferred docstring behavior/metadata;
3. make the callable available for MCP registration.

Do not make `@tool` maintain a second runtime tool protocol.

Where possible, it should simply adapt/register the underlying callable with MCP.

Example:

```python
@tool
def find_examples(
    self,
    concept: str,
    limit: int = 10,
) -> list[Example]:
    """Find behavioral examples relevant to a concept."""
    ...
```

MCP should derive the runtime parameter schema from the actual Python callable.

---

## Instruction annotation

Keep CDD's `@instruction`.

This is a CDD-specific abstraction and should remain independent of MCP.

Example:

```python
@instruction
def bdd_thinking(self):
    """
    Think in states, substates, events and transitions.
    Look for meaningful transitions, invalid transitions,
    ambiguity and concrete examples.
    """
    tool(self.find_examples)
    tool(self.validate_behavior)
```

The instruction docstring is the actual instruction content.

Do not require:

```python
return """..."""
```

Do not convert every instruction into an MCP prompt.

MCP prompts should only be used if there is an actual need for the host's MCP prompt catalog.

---

## Explicit tool references

Change instruction semantics so tool use is explicit.

Preferred:

```python
tool(self.find_examples)
```

Avoid relying on:

```python
self.find_examples()
```

being magically interpreted as an AI tool because the target method happens to carry `@tool`.

The source should visibly distinguish:

- ordinary instruction composition
- vs AI tool boundary

Initial semantics:

```python
tool(self.find_examples)
```

means:

this instruction exposes/requires the `find_examples` AI tool

Future syntax may support binding:

```python
x = some_dynamic_value()
tool(self.operation(x))
```

but partial binding is not part of the initial migration.

Do not complicate the MCP architecture for this future case.

---

## Remove YAML completely

Delete the YAML invocation architecture.

Remove code whose purpose is to:

- build YAML tool requests;
- parse YAML tool requests;
- serialize YAML tool responses;
- emit YAML invocation fences;
- read YAML from stdin for agent invocation;
- convert manifest information into YAML;
- teach the model the YAML protocol.

Generated artifacts must no longer contain:

```yaml
toolset:
context:
tool:
action:
arguments:
```

as an execution protocol.

Remove instructions such as:

- Pipe the block to stdin
- Do not write a request file
- `tools.ps1 run -`
- `python -m tools run -`

from generated skills/prompts/rules.

Do not preserve YAML as a compatibility architecture.

If a test exists solely to test the old YAML protocol, delete or replace the test.

If a helper exists solely because YAML needed it, delete the helper.

---

## Remove CLI execution plumbing

The AI runtime should no longer depend on the CLI.

Delete or isolate CLI code that exists solely to support:

```
agent
→ shell
→ python process
→ parser
→ dispatcher
→ operation
```

If the CLI has no meaningful remaining use after MCP migration, remove it entirely.

Do not keep CLI infrastructure "just in case."

A simple developer utility may be retained only if it has an explicit current use unrelated to the removed runtime architecture.

The burden of proof is on keeping code, not deleting it.

---

## Remove duplicate schema plumbing

MCP can derive tool schemas from Python signatures.

Therefore remove runtime code that exists only to transform:

```
Python signature
→ CDD schema
→ manifest
→ agent invocation contract
```

Specifically review `_SignatureReader`.

If its only remaining responsibilities are covered by MCP, delete it.

If generated skill documentation still needs a readable signature, replace the old schema machinery with the smallest possible Python signature formatter, preferably based on `inspect.signature()`.

Do not retain a large signature/schema subsystem merely to print one documentation line.

---

## Remove manifest plumbing

The old manifest was primarily necessary because the agent had to learn how to call CDD through the CLI.

MCP now provides native discovery.

Delete manifest generation if nothing in the new architecture genuinely requires it.

Do not maintain:

```
CDD manifest
+
MCP tool catalog
```

as duplicate representations of the same thing.

The Python callable is the source of truth.

MCP exposes the runtime contract.

Generated artifacts may contain a human-readable invocation line, but that is documentation rather than a manifest.

---

## Remove generic runner plumbing

Review `_ToolsetRunner` and related request/response document classes.

If their purpose is primarily:

- receive generic request document
- resolve tool/action name
- validate request
- invoke callable
- package response

they should disappear from the MCP runtime architecture.

MCP already provides:

- named tool invocation;
- structured arguments;
- result transport;
- protocol errors.

CDD should not maintain a second generic RPC dispatcher underneath MCP.

The MCP registration should hold or resolve the bound callable and invoke it directly.

---

## Keep only necessary loader functionality

Some existing loader functionality is still useful.

CDD needs a minimal mechanism to:

- find annotated toolset classes;
- construct them;
- discover `@tool` methods;
- resolve whatever constructor context the class requires;
- hand bound methods to MCP.

Reduce the loader to those responsibilities.

Delete functionality related only to:

- manifests;
- YAML;
- CLI request documents;
- generic dispatch;
- response serialization.

Target:

```
discover class
→ instantiate class
→ discover @tool methods
→ register bound methods
```

---

## `@resource`, `@skill`, and `@prompt` (unchanged)

`@resource`, `@skill`, and `@prompt` are **not** deprecated or replaced by this migration.

- **`@resource`** remains the CDD annotation for observable toolset state. Do not fold it into MCP tools or delete it “because MCP has resources.” Native MCP resources are a separate concern for a later change, if ever.
- **`@skill`** and **`@prompt`** remain the harness annotations for generating host skills and prompts/commands. Only the **tool invocation tail** inside generated artifacts changes (YAML block → MCP tool reference). The decorators, deploy paths, and file kinds stay the same.

Do not remove `@resource` registration, `@skill`/`@prompt` harness writers, or their tests as part of YAML/CLI removal unless a line of code is provably dead **and** not used by these annotations.

---

## Generated harness artifacts

Keep the current harness capability to generate:

- skills;
- prompts;
- commands;
- rules;
- AGENTS.md or equivalent guidance;
- host-specific artifacts.

Change only the invocation representation.

Current generated tail:

```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: behavior
tool: find_examples
.\tools.ps1 run -
```

Target generated tail:

```
Use MCP tool: `bdd.find_examples(concept: str, limit: int = 10)`
```

That is enough.

The function signature is included because it is helpful to humans reading the generated skill.

It is not the machine-readable contract.

MCP owns the authoritative runtime schema.

Do not generate extra MCP configuration or schema text into every skill.

---

## Harness transport rendering

Remove `_invoke_block()` or equivalent YAML-specific rendering.

Replace it with one very small MCP invocation renderer.

Example:

```python
def render_mcp_tool_reference(
    tool_name: str,
    callable: Callable[..., Any],
) -> str:
    return f"Use MCP tool: `{tool_name}{inspect.signature(callable)}`"
```

Keep this rendering concern centralized.

Do not spread MCP-specific formatting throughout every harness body class.

---

## Naming

Give every exposed tool a stable MCP name derived from its CDD identity.

Example:

- `bdd.find_examples`
- `bdd.validate_behavior`
- `plan.create`

If host compatibility requires another character convention:

- `bdd_find_examples`
- `bdd_validate_behavior`

use one deterministic naming strategy globally.

Do not create runtime-generated names unless required by future partial-binding work.

---

## Tests

Rewrite tests around the new architecture.

Delete tests whose only purpose is validating:

- YAML serialization;
- YAML parsing;
- CLI stdin invocation;
- manifest formatting;
- `tools.ps1`;
- generic request/response plumbing.

Add tests for:

- `@tool` discovery
- MCP registration
- Python signature → MCP schema
- tool invocation → direct Python callable
- persistent process / retained instance where relevant
- generated skill → correct MCP tool reference
- `@instruction` docstring behavior
- `tool(...)` extraction from instruction bodies

Tests should validate desired behavior, not preserve old implementation structures.

---

## Cleanup rule

After the new MCP path works, perform a deletion pass.

For every old component ask:

> Would this exist if CDD had been designed around MCP from day one?

If the answer is no, delete it.

Do not leave dead compatibility abstractions merely because removing them increases the diff.

The objective is a smaller system, not a parallel MCP implementation beside the old one.

---

## Desired end state

The codebase should conceptually reduce to:

```
CDD
├── @tool
├── @instruction
├── tool(...)
├── @resource          (unchanged)
├── @skill / @prompt   (unchanged — harness deploy only)
├── minimal discovery / construction
├── MCP server registration
└── harness generation
```

MCP owns:

- tool schema
- tool discovery
- tool invocation protocol
- transport
- structured arguments
- structured results
- persistent server boundary

CDD owns:

- domain semantics
- instruction composition
- tool grouping/reference semantics
- generated host guidance
- object/context construction

There should be no YAML transport architecture underneath this.

There should be no generic CDD RPC protocol underneath MCP.

There should be no duplicate schema system unless a concrete CDD requirement demands one.

---

## Acceptance criteria

The migration is complete when:

1. No generated skill/prompt/rule contains YAML invocation instructions.
2. No normal AI execution path uses `tools.ps1` or `python -m tools run`.
3. MCP invokes annotated Python operations directly.
4. Tool schemas come from the actual Python callable.
5. `@tool` remains the CDD authoring annotation for AI-callable operations.
6. `@instruction` remains the CDD authoring annotation for docstring-based guidance.
7. `tool(...)` explicitly marks AI tool usage inside instructions.
8. Generated artifacts reference MCP tools in a concise form such as:  
   `Use MCP tool: bdd.find_examples(concept: str, limit: int = 10)`
9. Old YAML request/response and manifest plumbing is removed when it no longer serves the target architecture.
10. Old CLI dispatcher plumbing is removed when it no longer serves the target architecture.
11. Duplicate signature/schema machinery is removed unless a remaining concrete use justifies it.
12. The resulting implementation is materially smaller than the current one.
13. `@resource`, `@skill`, and `@prompt` behavior and harness/deploy outputs for those annotations remain unchanged except where generated skills/prompts previously embedded YAML tool-invocation tails (those tails become MCP references only).

---

## Core architectural rule

**CDD supplies semantics. MCP supplies the runtime.** Delete everything between those two layers that no longer earns its existence.
