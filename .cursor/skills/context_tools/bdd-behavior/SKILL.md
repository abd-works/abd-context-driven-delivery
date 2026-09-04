---
name: bdd-behavior
description: "Provide guidance for creating behavior skeletons and development tests."
disable-model-invocation: true
---

# bdd-behavior

Use bdd guidance at `behavior` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@bdd-modules

Provide guidance for creating behavior skeletons and development tests.
At modules fidelity: no BDD spec file is written — bootstrap CE class structure via the companion.
At behavior fidelity: write all BDD test signatures (SIGNATURE markers).
At development fidelity: write full test bodies and production code.
When the target module already exists, scan the production source for every public method and property and verify each has test coverage — add missing signatures for any gap before writing new ones.
BDD tests must conform to CE class structure: describe/it hierarchies must map onto public CE interfaces and operations.
When this BDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.