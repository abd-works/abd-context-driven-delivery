# Log mistake

When the user points out a mistake (or says **log mistake**), treat it as
failure: the agent did not do it right. Log it **immediately** — the moment
it is mentioned, before any fix exists — via tool `log_mistake`:

```yaml
tool: log_mistake
arguments:
  artifact: <path or node that was wrong>
  rule: <exact failed rule — scanner slug or (process) name>
  wrong: <one line — what was done wrong>
  original: |
    <faulty output>
```

It returns an `entry_id` — hold onto it. Pass that same id to
`log_correction` once the fix lands, so several mistakes can stay open at
once without being conflated.

## Where

Write under the **current session** folder only:

`{session.folder}/mistakes.log`

(e.g. `{path}/.context/sessions/{name}/mistakes.log`). Requires a named sprint
(`create_session` / constructor `session=`). Do not log into a divergent folder.

## Rules

- Log the mistake the moment it is pointed out — do not wait for the fix.
- `wrong` stays one line; put detail in `original`.
- Prefer an exact rule id (`branch-on-mechanical-uniqueness`) or a clear
  `(process) …` name when no scanner slug exists.
- Call `log_mistake` once per failure; do not batch unrelated defects.
- Track each returned `entry_id` explicitly when more than one mistake is
  open at once — nothing here assumes only one is in flight.
