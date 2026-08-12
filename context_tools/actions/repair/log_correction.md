# Log correction

Once a logged mistake is actually fixed, complete it via tool
`log_correction` — never open a new `log_mistake` entry for the same
mistake:

```yaml
tool: log_correction
arguments:
  entry_id: <id returned by log_mistake>
  improved: |
    <corrected output>
  status: fixed
```

## Entry shape (after completion)

Match existing sprint entries. Each block:

| Field | Content |
|-------|---------|
| `id` | Correlates this block back to its `log_mistake` call |
| `when` | ISO date (tool fills today if omitted) |
| `artifact` | Path and/or map node |
| `rule` | Exact failed rule |
| `wrong` | One-liner |
| `original` | Faulty output (YAML `\|` block) |
| `improved` | Corrected output (YAML `\|` block) |
| `status` | Usually `fixed` after the correction |

## Rules

- Fix first, then call `log_correction` — never log a planned fix without
  applying it.
- `entry_id` must match a mistake already logged via `log_mistake`; there is
  no way to create a fresh entry from `log_correction`.
- Call `log_correction` once per completed mistake; use the exact `entry_id`
  `log_mistake` returned so the AI can align multiple mistakes and
  corrections correctly.
