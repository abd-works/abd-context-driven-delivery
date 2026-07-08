---
rule: prompt-is-a-single-task
kind: quality
fidelity: [engineering]
artifact: test_*.py
---

# Rule: Prompt Is a Single Task

The `prompt` argument to `when_agent_invoked` must be one clear, self-contained instruction. The agent must not need to ask a clarifying question to complete it.

## DO

- Write one specific instruction: `"Validate this artifact against rule X and emit PASS or FAIL."`

## DON'T

- Chain multiple instructions with "and then"
- Write vague prompts like `"Do stuff with the file."`
