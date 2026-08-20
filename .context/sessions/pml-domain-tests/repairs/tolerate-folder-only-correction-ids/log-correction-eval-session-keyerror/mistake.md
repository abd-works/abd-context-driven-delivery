# log-correction-eval-session-keyerror

- **entry_id:** c37f74c9
- **artifact:** (process) log_correction / eval session
- **rule:** (process) log-correction-eval-session-keyerror
- **wrong:** BaseContextTool.log_correction raises KeyError in Session.record_correction when mistake entry_ids are not present in session.yaml turns, even though Repairer already wrote status=fixed to mistakes.log.
- **status:** fixed
