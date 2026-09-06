# diagram-class-title-no-markdown-bold

- **tool:** CleanEngineering (Drawio)
- **error:** Class titles were written as `**Prospect**` inside an HTML `<b>` tag, so Draw.io showed the asterisks.
- **rule:** class-title-no-markdown-bold
- **what changed:**
  - **Prose — yes.** New rule bullet in `context_tools/clean_engineering/class_model/drawio/drawio.md`: titles inside `<b>` are plain text; do not bake markdown `**` into the label.
  - **Detector — yes.** New scanner `class_title_no_markdown_bold_scanner.py` (plus spec and eval fixtures). Scan fails if a class `<b>` title still contains `**`.
  - **Generator — already done, not this repair.** `_display_class_name` in `drawio_class_model.py` already strips `*` before writing the cell HTML (landed in commit `61349a2` / `pre-repair`). This repair did not edit the emitter.
