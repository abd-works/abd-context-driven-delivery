# physical-folder

- **tool:** CleanEngineering
- **error:** Wrote module-context.md under the session folder (…/sessions/…/{module}/.context/) instead of beside the module source.
- **rule:** physical-folder
- **what changed:**
  - **Prose — already there, tightened in this loop.** clean_engineering.md physical-folder bullet already says module-context.md never lives under .context/sessions/.
  - **Detector — yes.** physical_folder_scanner.py now fails when module.context_file path contains .context/sessions.
  - **Generator — no path rewrite.** Placement is instructed by the rule; the scanner catches a session-nested write.
