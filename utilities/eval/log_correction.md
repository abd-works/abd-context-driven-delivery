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

Correction.apply sets `status=fixed` and `fixedIn` to the open Turn, then
each Mistake.correct. The improved text is written as `repairedAsset` beside
that Mistake under `{session.folder}/mistakes/{mistake-name}/`.

## Rules

- Fix first, then call `log_correction` — never log a planned fix without
  applying it.
- `entry_id` must match a mistake already logged via `log_mistake`; there is
  no way to create a fresh entry from `log_correction`.
- Call `log_correction` once per completed mistake; use the exact `entry_id`
  `log_mistake` returned so the AI can align multiple mistakes and
  corrections correctly.
