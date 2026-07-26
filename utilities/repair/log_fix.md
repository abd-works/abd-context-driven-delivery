# Log fix

When the user says **to fix** (or equivalent), treat it as failure: the agent
did not do it right. **Correct immediately**, then append one entry to the
current sprint’s `to-fix.log` via action `log_fix` (calls tool `write_to_fix`):

```yaml
tool: write_to_fix
arguments:
  artifact: <path or node that was wrong>
  rule: <exact failed rule — scanner slug or (process) name>
  wrong: <one line — what was done wrong>
  original: |
    <faulty output>
  improved: |
    <corrected output>
  status: fixed
```

## Where

Write under the **current session** folder only:

`{session.folder}/to-fix.log`

(e.g. `{path}/.context/sessions/{name}/to-fix.log`). Requires a named sprint
(`create_session` / constructor `session=`). Do not log into a divergent folder.

## Entry shape

Match existing sprint entries. Each block:

| Field | Content |
|-------|---------|
| `when` | ISO date (tool fills today if omitted) |
| `artifact` | Path and/or map node |
| `rule` | Exact failed rule |
| `wrong` | One-liner |
| `original` | Faulty output (YAML `\|` block) |
| `improved` | Corrected output (YAML `\|` block) |
| `status` | Usually `fixed` after the correction |

## Rules

- Fix first, then log — never log a planned fix without applying it.
- `wrong` stays one line; put detail in `original` / `improved`.
- Prefer an exact rule id (`branch-on-mechanical-uniqueness`) or a clear
  `(process) …` name when no scanner slug exists.
- Call `write_to_fix` (via action `log_fix`) once per failure; do not batch unrelated defects.
