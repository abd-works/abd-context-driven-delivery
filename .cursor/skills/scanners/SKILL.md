# scanners

Mechanical checkers that enforce rules. Each scanner extends `ArtifactScanner` from `scanners.py` and returns violations for artifacts under a workspace.

read in full → `.cdd/scanners/scanners.md`

## Scan artifacts
Run scanners against an artifact to check rule compliance.
read `@scanners` §Scan artifacts

## Add a new scanner to a rule
Copy the template, move to target rule folder rename, fill in the placeholders.
read `@scanners` §Add a new scanner to a rule

## Test scanners
Run scanner tests against pass/fail example fixtures.
read `@scanners` §Test scanners

## Deploy
read `@cdd-capability` §Deploy

## Clean
read `@cdd-capability` §Clean
