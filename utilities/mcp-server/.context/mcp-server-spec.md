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

Do **not** remove or redesign the **`@resource`**, **`@skill`**, or **`@prompt` decorators** as part of this migration — see [Out of scope](#out-of-scope--decorators-unchanged).

**Harness deploy must change:** generated skills, prompts, commands, rules, agents, and related host artifacts that today tell the model to invoke YAML/CLI must instead tell the model to invoke MCP tools. See [Harness deploy changes](#harness-deploy-changes).

---

## Out of scope — decorators unchanged

These **annotation decorators** stay as they are today. Do not rename, merge, or delete them:

- **`@resource`** — observable toolset state (`primitives/tools`); property getters, instruction inlining, and resource registration behavior are unchanged.
- **`@skill`** — harness marker for skill files (`primitives/harness`); still selects which operations deploy as `SKILL.md`.
- **`@prompt`** — harness marker for prompt/command files (`primitives/harness`); still selects which operations deploy as slash commands / prompt files.

What **does** change under `@skill` / `@prompt` is only the **generated file body** where it currently describes YAML/CLI invocation — that content becomes MCP invocation guidance instead.

This migration replaces **AI tool invocation transport** (YAML/CLI → MCP). It does **not** remove harness deploy vehicles or read-only resource authoring.

When deleting YAML/manifest/runner plumbing, do not delete code whose primary job is `@resource`, `@skill`, or `@prompt` discovery/writing unless that code is **only** used by the removed YAML/CLI path and has no remaining role after harness bodies emit MCP references.

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
- discover CDD `@instruction` operations;
- construct the required Python objects;
- register bound `@tool` callables with MCP;
- register `@instruction` content as MCP prompts (or equivalent host-visible prompt entries) plus their referenced tools;
- remain alive across repeated calls;
- invoke `@tool` callables directly when the host calls an MCP tool.

Assume a local single-user process.

Do not add per-user session architecture.

The live MCP process itself may retain:

- loaded modules;
- toolset instances;
- caches;
- workspace state;
- other useful in-memory state.

### Discovery model

On startup (and on reload if supported), the server walks annotated toolset classes and builds two catalogs:

| CDD annotation | MCP exposure | Runtime payload |
|---|---|---|
| `@tool` | MCP **tool** | bound Python callable; schema from signature |
| `@instruction` | MCP **prompt** (or prompt-like catalog entry) | docstring text + declared tool references |

An `@instruction` does **not** execute Python orchestration at runtime. The server **returns** (discovers/exposes):

1. **Prompt** — the instruction method's docstring (after CDD docstring expansion/normalization if any).
2. **Tools** — the MCP tool names resolved from each `tool(self.some_tool)` reference in the instruction body.

The host uses the prompt for guidance and the declared tools for callable operations. CDD does not re-run the instruction body through a generic dispatcher.

Example registration shape (conceptual):

```
bdd.bdd_thinking          → prompt text + [bdd.find_examples, bdd.validate_behavior]
bdd.find_examples         → callable tool
bdd.validate_behavior     → callable tool
```

Use one deterministic naming strategy for both tools and instruction prompts (see [Naming](#naming)).

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

This is a CDD-specific abstraction. The MCP server **discovers** instructions and exposes what they declare: a **prompt** (docstring) and **tools** (`tool(...)` references).

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

Semantics:

- **Docstring** → the instruction prompt text returned to the host via MCP prompt discovery.
- **`tool(...)` lines** → explicit MCP tool references bundled with that instruction (must resolve to registered `@tool` methods on the same toolset instance).

Do not require:

```python
return """..."""
```

Do not execute the instruction body as an orchestration runtime. Statically extract docstring + `tool(...)` references at discovery time.

Do not teach agents a separate YAML/CLI protocol to "fetch" instructions — MCP discovery is the path.

**Naming note:** harness `@prompt` (deployed slash commands / prompt **files**) is unrelated to MCP prompt entries produced from `@instruction`. Both may coexist; this migration adds MCP prompt discovery for `@instruction` without removing harness `@prompt` deploy.

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
- discover `@instruction` methods;
- extract each instruction's docstring and `tool(...)` references;
- resolve whatever constructor context the class requires;
- hand bound `@tool` methods to MCP as tools;
- hand each `@instruction` to MCP as a prompt entry plus its referenced tool names.

Reduce the loader to those responsibilities.

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
→ discover @tool methods → register MCP tools
→ discover @instruction methods → register MCP prompts + tool refs
```

---

## `@resource`, `@skill`, and `@prompt` (decorators unchanged)

The **decorators** are not deprecated or replaced:

- **`@resource`** — still marks observable toolset state. Do not fold it into MCP tools or delete it because MCP has its own resource concept.
- **`@skill`** / **`@prompt`** — still mark which operations deploy as skills and prompts/commands.

Generated **content** under those deploy paths **must** change wherever it currently teaches YAML/CLI invocation.

---

## Harness deploy changes

Harness deploy **is in scope** and **must** be updated as part of this migration.

Any generated host artifact that today tells an agent to call CDD through YAML stdin, `tools.ps1`, or `python -m tools run` must be regenerated to tell the agent to call **MCP tools** instead.

### Artifacts that must change

Review and update generation for every deploy kind, including:

- **`@skill` → `SKILL.md`** — context-tool skills, utility skills, fidelity skills
- **`@prompt` → commands / prompt files** — action commands, utility prompts, harness lifecycle prompts
- **`@instruction` → rules** — generated rule bodies that embed tool invocation
- **Agents** — generated agent definitions that reference YAML/CLI (present or planned under harness)
- **Context-tool bodies** — `ContextToolBody`, `ContextToolFidelityBody`, `ActionBody`
- **Utility / format bodies** — `UtilityBody`, `FormatBody`, `resolve_text` output
- **AGENTS.md** (or equivalent repo guidance) — any global instructions that mention the YAML protocol
- **Redeployed `.cursor/skills/**`, `.cursor/commands/**`, rules, and sibling IDE trees** after harness generation changes land

### Remove from generated output

Delete from all generated artifacts:

- YAML invoke fences (`toolset:`, `context:`, `tool:`, `action:`, `arguments:`)
- “Pipe the block to stdin”
- “Do not write a request file”
- “Do not remanifest”
- “Follow `response.instructions` only” (when that meant YAML/CLI response plumbing)
- “through the tools cli”
- `.\tools.ps1 run -` / `python -m tools run -`

Replace with a single concise MCP line (see [Harness transport rendering](#harness-transport-rendering)).

### Harness code that must change

At minimum, update `primitives/harness/` (and anything that duplicates its invoke rendering):

- **`_invoke_block()`** — remove or replace; must not emit YAML
- **`_CATALOG_LINE`** and **`resolve_text()`** — stop teaching stdin YAML catalog protocol
- **Body classes** (`bodies.py`, skill/prompt/agent writers) — call the centralized MCP renderer instead of YAML blocks
- **`returned_guidance.py`** — stop building YAML input for CLI subprocess invocation
- **Harness tests** (`harness_spec.py`, invoke agent specs) — assert MCP references, not `tools.ps1` / YAML fences

### Redeploy requirement

After harness generation is updated, run **`deploy-harness`** (or equivalent) so checked-in generated skills/commands/rules in the repo match the new MCP invocation text. The migration is not done while deployed artifacts still contain YAML invoke instructions.

### Before / after (skill tail)

Current:

```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: behavior
tool: find_examples
.\tools.ps1 run -
```

Target:

```
Use MCP tool: `bdd.find_examples(concept: str, limit: int = 10)`
```

Same change applies to prompts, commands, rules, and agent files that currently carry the YAML tail or CLI shell step.

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

Give every exposed MCP tool and instruction prompt a stable name derived from its CDD identity.

**Always use dot notation:** `{toolset_slug}.{method_name}`

Examples:

- `bdd.find_examples` — tool
- `bdd.validate_behavior` — tool
- `bdd.bdd_thinking` — instruction prompt
- `plan.create` — tool

Do **not** use alternate separators (no `bdd_find_examples`, no runtime-generated aliases, no host-specific rewrites).

Apply this convention globally for **both** tools and instruction prompts.

Do not create runtime-generated names unless required by future partial-binding work.

Instruction prompts and their referenced tools share the same namespace rules so `tool(self.find_examples)` resolves to the same MCP name the tool was registered under (e.g. `bdd.find_examples`).

Generated harness text, MCP registration, and tests must all use this same dotted form.

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
- `@instruction` discovery
- MCP registration of tools
- MCP registration of instruction prompts with correct docstring text
- MCP instruction entries include correct referenced tool names from `tool(...)` bodies
- Python signature → MCP schema (tools only)
- tool invocation → direct Python callable
- persistent process / retained instance where relevant
- generated skill / prompt / command / rule / agent → correct MCP tool reference (no YAML tail)
- harness `deploy-harness` redeploy removes YAML from `.cursor/skills` and sibling deploy trees
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
├── @resource          (decorator unchanged)
├── @skill / @prompt   (decorators unchanged; generated bodies use MCP invocation)
├── minimal discovery / construction
├── MCP server registration
└── harness generation (deploy output updated — no YAML invoke tails)
```

MCP owns:

- tool schema
- tool discovery
- tool invocation protocol
- instruction prompt discovery (for `@instruction` docstrings)
- transport
- structured arguments
- structured results
- persistent server boundary

CDD owns:

- domain semantics
- `@instruction` composition and `tool(...)` reference semantics
- tool grouping/reference semantics
- generated host guidance (harness deploy)
- object/context construction

There should be no YAML transport architecture underneath this.

There should be no generic CDD RPC protocol underneath MCP.

There should be no duplicate schema system unless a concrete CDD requirement demands one.

---

## Acceptance criteria

The migration is complete when:

1. No generated skill/prompt/rule/command/agent contains YAML invocation instructions.
2. No normal AI execution path uses `tools.ps1` or `python -m tools run`.
3. MCP invokes annotated `@tool` operations directly.
4. MCP discovers annotated `@instruction` operations and exposes each as a prompt (docstring) plus its referenced tools.
5. Tool schemas come from the actual Python callable.
6. `@tool` remains the CDD authoring annotation for AI-callable operations.
7. `@instruction` remains the CDD authoring annotation for docstring-based guidance with explicit `tool(...)` references.
8. `tool(...)` explicitly marks AI tool usage inside instructions and resolves to MCP tool names at discovery time.
9. Generated artifacts reference MCP tools in a concise form such as:  
   `Use MCP tool: bdd.find_examples(concept: str, limit: int = 10)`
10. Old YAML request/response and manifest plumbing is removed when it no longer serves the target architecture.
11. Old CLI dispatcher plumbing is removed when it no longer serves the target architecture.
12. Duplicate signature/schema machinery is removed unless a remaining concrete use justifies it.
13. The resulting implementation is materially smaller than the current one.
14. `@resource`, `@skill`, and `@prompt` **decorators** remain; harness deploy has been updated and redeployed so generated skills/prompts/commands/rules/agents use MCP invocation text instead of YAML/CLI tails.
15. Checked-in deploy trees (e.g. `.cursor/skills/**`, `.cursor/commands/**`) contain no remaining `toolset:` / `tools.ps1 run -` invoke blocks from harness generation.

---

## Core architectural rule

**CDD supplies semantics. MCP supplies the runtime.** Delete everything between those two layers that no longer earns its existence.
