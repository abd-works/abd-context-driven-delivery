Mechanical checkers that enforce rules. Each scanner extends `ArtifactScanner` from `scanners.py` and returns violations for artifacts under a workspace.

## Scan artifacts

Run scanners against an artifact to check rule compliance.

read in full → `scan-with-scanners.md`

## Add a new scanner to a rule

Copy the template, move to target rule folder rename, fill in the placeholders.

read in full → `{rule-name}-scanner.py`

## Test scanners

Run scanner tests against pass/fail example fixtures.

```bash
pytest enforce/scanners/validate-artifact-scanner-test.py -v
```
