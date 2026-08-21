 Log mistake

When the user points out a mistake (or says **log mistake**), treat it as
failure: the agent did not do it right. Log it **immediately** — the moment
it is mentioned, before any fix exists — via tool `log_mistake`:

```yaml
tool: log_mistake
arguments:
  artifact: <path of the file that was wrong>
  rule: <exact failed rule — scanner slug or (process) name>
  wrong: <one line — what was done wrong>
  original: |
    <verbatim contents of that file>
```

It returns an `entry_id` — hold onto it. Pass that same id to
`log_correction` once the fix lands, so several mistakes can stay open at
once without being conflated.

## Where

The Mistake records itself onto the EvalSession and the open Turn, and writes
`{session.folder}/mistakes/{mistake-name}/` (named after the mistake). That
folder holds `faultyAsset` (a copy of the artifact file) and `mistake.md`
(rule / wrong / artifact). Do not create an improvement folder until a
correction lands — see `log_correction.md`. Persist the index as
`{session.folder}/session.yaml`. Requires a named sprint (`open` /
constructor `session=`). Do not log into a divergent folder. There is no
`mistakes.log`.

## Rules

- Log the mistake the moment it is pointed out — do not wait for the fix,
  and do not edit the artifact first.
- `wrong` is the one-line diagnosis. `original` is the asset itself — the
  `.drawio` XML, the source file, the sketch. Read the file at `artifact`
  and pass its full contents. Do not paraphrase, summarize, or describe the
  problem in `original`. If the file is already gone, do not invent a
  stand-in; leave `original` empty rather than writing a diagnosis into
  `faultyAsset`.
- Prefer an exact rule id (`branch-on-mechanical-uniqueness`) or a clear
  `(process) …` name when no scanner slug exists.
- Call `log_mistake` once per failure; do not batch unrelated defects.
- Track each returned `entry_id` explicitly when more than one mistake is
  open at once — nothing here assumes only one is in flight.
