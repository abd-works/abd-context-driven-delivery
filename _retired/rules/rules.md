---
extends: capability
overrides: [validate, create, build-a-rule, fix, test]
---

Generate compliant artifacts, validate artifacts against rules, and build rules with optional mechanical scanners.

## Validate

Validate an artifact against one or all rules.

Each rule folder is checked agentically. If the rule also has a scanner (`{rule-name}-scanner.py`), the scanner runs automatically — rules without a scanner are validated by the agent only.

read in full → `validate-artifacts-with-rules.md`
read in full → `scan-with-scanners.md`

## Create

Produce a new artifact that satisfies all rules.

read in full → `generate-artifact-using-rules.md`

## Build a rule

Create a new rule folder. Every rule needs a definition; a scanner is optional and only added when mechanical checking is practical.

**Required:**

read in full → `{rule-name}/{rule-name}-rule.md`

**Optional — add a scanner when the rule can be checked mechanically:**

read in full → `{rule-name}/{rule-name}-scanner.py`
read in full → `rules.py` §Rule

## Fix

Fix {artifact} to comply with all rules. Requires {artifact} path.

1. Run `## Validate` against {artifact} — read every violation in the report
2. If scanners exist, run them and read the scanner report too
3. Apply all fixes directly to {artifact}
4. Re-run validate (and scanners) until clean

## Test

Run rule agent tests and/or scanner tests against the examples.

```
python rules/__main__.py test [-v]
python rules/__main__.py test --scanner [-v]
```

read in full → `validate-artifact-rules-test.py`
read in full → `validate-artifact-scanner-test.py`
