---
scanner: business_readable_test_names_scanner.py
---

# Rule: Use Domain Language

Apply **Domain Language** (DDD): use the same vocabulary in the domain model, stories, acceptance criteria, scenarios, **and** code. Class names map to domain entities or nouns; method names map to domain responsibilities or verbs; test names read like plain-English stories. This is priority 1 — it overrides generic technical naming at every level.

## DO

- Class names → domain entities/nouns from the model (e.g. `GatherContextAction`, `BotConfig`, `Guardrails`).
- Method names → domain responsibilities/verbs (e.g. `inject_questions_and_evidence`, `load_trigger_words`).
- Test names → plain-English story descriptions readable aloud (`test_agent_loads_configuration_when_file_exists`).

```python
# Domain entity: 'Gather Context Action'
# Domain responsibility: 'Inject questions and evidence'

class GatherContextAction:
    def inject_questions_and_evidence(self) -> Instructions:
        ...

class ValidateRulesAction:
    def inject_behavior_specific_and_bot_rules(self) -> Instructions:
        ...

def test_agent_loads_configuration_when_file_exists(self, workspace_root):
    ...
```

## DON'T

- Use generic technical terms not in the domain model.
- Name classes after infrastructure roles (`Loader`, `Manager`, `Handler`, `Service`, `StdioHandler`).
- Name methods with generic verbs that have no domain meaning (`execute_with_guardrails`, `process`, `handle_request`).
- Write test names that describe implementation rather than behavior.

```python
# WRONG: generic technical names
class Action:           # which action?
class Loader:           # not in domain
class Handler:          # not in domain

def execute_with_guardrails():  # domain says 'inject_questions_and_evidence'
def process():                  # too vague

def test_agt_init_sets_vars():  # abbreviations, implementation focus
```
