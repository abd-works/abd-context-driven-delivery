# Guardrails

Decides when and how to invoke a Generator's actions (`generate`, `satisfy`, `validate`) in response to workspace events — chat ask and direct file edit. Not the Generator (rules, scanners) and not the Agent (session, instruct).

## Language

**Guardrails**:
The enforcement layer that routes workspace events to the right Generator action on the right artifact.
_Avoid_: Hooks (that's a delivery mechanism), generator, agent

**Constraint enforcement**:
Applying a Generator's concepts and scanners to an artifact when a triggering event occurs — without the user manually invoking `python -m tools run`.
_Avoid_: Validation, linting (too generic)

**Trigger**:
A workspace event that may invoke enforcement — chat ask or direct file edit.
_Avoid_: Hook, event, signal

**Compliant content**:
An artifact tagged with one or more Generator slugs in its provenance — enforcement applies only to tagged artifacts, not all files matching a glob.
_Avoid_: Generated content, governed content, all Python files

**Provenance**:
An ordered inline header on the artifact (e.g. `# @governed-by: clean-code, architecture-react`) written by each Generator's template during `generate`. Order in the header is the `satisfy` sequence on edit.
_Avoid_: Metadata, tags, globs, sidecar, registry

**Guardrail rule**:
Orchestration instruction emitted into the edit path — reads artifact provenance and injects each applicable Generator's `satisfy` in sequence. Not one isolated `.mdc` per Generator selected only by globs.
_Avoid_: Skill, AGENTS.md, always-on rule, per-generator glob rule

**Use-when**:
The scoped activation on a guardrail rule — when Cursor loads that rule into context. Not `alwaysApply`.
_Avoid_: alwaysApply, trigger
