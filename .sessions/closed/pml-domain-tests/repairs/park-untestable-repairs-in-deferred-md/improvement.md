# defer-improvements-separate-from-mistake-log

- **tool:** Eval
- **error:** No place to park work that cannot be fail-first repaired, so it was at risk of going into the mistake log.
- **rule:** (process) defer-improvements-separate-from-mistake-log
- **what changed:**
  - **Prose — yes.** utilities/eval/repair.md: if a test cannot fail, append to {session.folder}/deferred.md and move on — not the mistake log.
  - **Code — the file is just markdown.** No scanner. The session already has a deferred.md.
