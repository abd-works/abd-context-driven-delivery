---
name: record-decisions-session
description: "Offer and write Context Decision Records (CDRs) sparingly as decisions crystallise during the wrapped action - never batch; never invent decisions."
disable-model-invocation: true
---

Offer and write Context Decision Records (CDRs) sparingly as decisions crystallise during the wrapped action - never batch; never invent decisions.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: record_decisions.record_decisions:RecordDecisions
action: record_decisions_session
```
.\tools.ps1 run -
