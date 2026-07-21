---
name: record-decisions
description: "Offer and write Context Decision Records (CDRs) in .context/cdr/ as decisions crystallise."
disable-model-invocation: true
---

# RecordDecisions

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest record_decisions.record_decisions:RecordDecisions
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
