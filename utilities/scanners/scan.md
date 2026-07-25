# Scan

Run every registered scanner rule against files on disk.

```yaml
tool: scan
arguments:
  paths:
    - <path>
```

Return the scanner report with registered rules and violations; fix failures before calling work done.
