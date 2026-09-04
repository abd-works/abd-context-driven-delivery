---
name: ddd-scaffold
description: "Provide guidance for creating bounded contexts, building blocks, and tactics."
disable-model-invocation: true
---

# ddd-scaffold

Use ddd guidance at `scaffold` fidelity only.

Provide guidance for creating bounded contexts, building blocks, and tactics.
When DDD scaffolding is ready, call guidance on the CE companion and pass that companion to this action as a separate tools run for matching OO artifacts.
Scan the production source for every public method and property; flag any with no corresponding test as a coverage gap. Fix every BDD violation and coverage gap — confirm each failing test is RED for the right reason.
If the same test is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (wrong exception, wrong line, shifting failure mode, or a re-read of the code that does not explain the failure).
When this DDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.