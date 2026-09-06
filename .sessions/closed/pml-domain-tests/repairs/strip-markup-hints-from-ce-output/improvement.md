# output-format

- **tool:** CleanEngineering
- **error:**
  - Added '<!-- Mu -->' annotation comments to every module heading in pml-my-modules.md. These are internal toolset markup hints — they must never appear in the written output file. The document should contain only human-readable content; all annotation-style metadata comments must be stripped before writing.
  - Inserted a blank line between every module heading (# config,
- **rule:** output-format
- **what changed:**
  - **Prose — yes.** Module-rules bullet in `clean_engineering.md`: strip `<!-- Mu -->` / `<!-- Mv -->`; `# name` then `- **Purpose:**` with no blank line.
  - **Scanner — yes.** `output_format_scanner.py` (plus spec).
