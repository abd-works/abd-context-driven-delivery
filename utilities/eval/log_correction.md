# Log correction

Once a logged mistake is actually fixed, complete it via tool
`log_correction` — never open a new `log_mistake` entry for the same
mistake:

```yaml
tool: log_correction
arguments:
  entry_id: <id returned by log_mistake>
  improved: |
    <verbatim contents of the repaired artifact file — goes in repairedAsset>
  how: |
    <which context-tool file changed and what the edit was>
  status: fixed
```

Correction.apply sets `status=fixed` and `fixedIn` to the open Turn, then
each Mistake.correct. After root cause, name one folder under `repairs/` as a
concise kebab-case description of **that improvement** (what you changed in
the tool — e.g. `strip-markdown-bold-from-class-titles`). Do not name it after
the mistake rule, a truncated rule slug, or the nested mistake folder. Write
the improvement details there, then drop each Mistake folder into it:

```
{session.folder}/repairs/{theme}/
  improvement.md          ← tool, error, how the tool changed — not the asset
  {mistake-name}/
    faultyAsset
    repairedAsset
    mistake.md
```

Mistakes that share the same root-cause improvement share that folder. If no
improvement was made, leave the Mistake under `mistakes/` — do not create
the theme folder.

## Rules

- Fix first, then call `log_correction` — never log a planned fix without
  applying it.
- `improved` is the repaired artifact (the `.drawio` XML, the source, the
  sketch) — the same kind of file that went in `faultyAsset`. It is not a
  description of the redraw. Read the file at `artifact` after the fix and
  pass its full contents.
- `how` is the tool-file change. Do not put the asset in `how` or a
  diagnosis in `improved`.
- `entry_id` must match a mistake already logged via `log_mistake`; there is
  no way to create a fresh entry from `log_correction`.
- Call `log_correction` once per completed mistake; use the exact `entry_id`
  `log_mistake` returned so the AI can align multiple mistakes and
  corrections correctly.
