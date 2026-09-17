# Scan

Run the listed context tool's scanner collection against files on disk.

A path without a host is a walk with no rules. Pass the context tool(s) whose
`_scanner_collection` should run.

```yaml
toolset: scan.scan:Scan
tool: scan
arguments:
  tools:
    - <context tool>
  paths:
    - <path>
```

Return the scanner report with registered rules and violations; fix failures before calling work done.
