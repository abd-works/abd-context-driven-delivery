# log-correction-eval-session-keyerror

- **tool:** Eval
- **error:** log_correction KeyError’d when the entry_id was on disk (mistakes/) but not in session.yaml turns.
- **rule:** (process) log-correction-eval-session-keyerror
- **what changed:**
  - **Prose — no generating-tool rule.** log_correction.md still requires an existing entry_id.
  - **Code — yes.** Session.record_correction was removed. Repair.log_correction looks the mistake up; a folder-only id that is not in yaml turns is a no-op (returns the id) instead of KeyError.
  - **Scanner — no.**
