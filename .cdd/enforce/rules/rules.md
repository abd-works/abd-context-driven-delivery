Generate compliant artifacts, validate artifacts against rules, and build/test new rules to improve output quality.

## Validate

Check an artifact against one or all rules.

read in full → `rules/validate-artifacts-with-rules.md`


## Generate

Produce a new artifact that satisfies all rules.

read in full → `rules/generate-artifact-using-rules.md`

## Build a rule

Create a new rule (definition, scanner, examples).

read in full → `rules/{rule-name}/{rule-name}-rule.md`

## Test rules

Run agent eval tests against rule examples. (`eval-rule-agent-test.py`)

Uses `agent_test.AgentTest` (from `agent_test/` at repo root) to invoke `cursor-agent` and assert it emits the correct verdict for each example.

```bash
pytest enforce/rules/validate-artifact-rules-test.py -v -s
```