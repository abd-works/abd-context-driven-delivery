# scan.md

Run scanners against an output to check rule compliance.

- [ ] Run the scanner against the generated/target output:

```bash
python -m enforce validate <artifact-file> --rule <rule-name>
```

- [ ] Save the scanner report under `scanner-report/` in the workspace.
- [ ] Fix all violations and re-run until clean, or surface **uncertain** items to the user — do not silently discard them.
- [ ] Emit exactly one verdict line per rule:


```
Rule: <rule-name>  ->  PASS
```
or
```
Rule: <rule-name>  ->  FAIL  <offending line or reason>
```