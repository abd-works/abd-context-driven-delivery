<!--
HOW TO USE THIS TEMPLATE
========================
1. Copy this folder to examples/{domain}/rules/{rule-name}/
2. Rename {rule-name} everywhere (folder, this file, the scanner)
3. Fill in all {placeholders} below
4. Add artifacts to examples/pass/ and examples/fail/
5. Read test.md in full, then run the tests

Structure:
  {rule-name}/
    {rule-name}-rule.md          ← this file
    {rule-name}-scanner.py       ← copy from scanners/{rule-name}-scanner.py
    examples/
      pass/                      ← compliant artifacts
      fail/                      ← violating artifacts
-->
---
rule: {rule-name}
kind: quality          # quality | shape
fidelity: [specification, engineering]
artifact: {artifact-glob}
scanner: {rule-name}-scanner.py
---

# Rule: {Rule Name}

{One sentence: what every artifact MUST declare or satisfy, and why it matters.}

## DO

- {Describe a compliant pattern with a concrete example}
- {Another compliant pattern}

## DON'T

- {Describe a violation pattern}
- {Another violation pattern}
